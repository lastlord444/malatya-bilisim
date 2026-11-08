"""Build a compact, repeatable daily creative brief for the Antigravity browser agent.

This module does NOT call video APIs, create a Gemini video or publish to Instagram.
Only Antigravity's authenticated browser execution can attempt those actions.
"""
import argparse
import json
import os
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Istanbul")


def _load_json(path, fallback):
    if not Path(path).exists():
        return fallback
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def build_daily_brief(root_dir=None, day=None):
    root = Path(root_dir) if root_dir else Path(__file__).resolve().parent.parent
    day = day or datetime.now(TZ).date()
    if isinstance(day, str):
        day = date.fromisoformat(day)
    strategy = _load_json(root / "config" / "content_strategy.json", None)
    if not strategy or not strategy.get("pillars"):
        raise ValueError("config/content_strategy.json bulunamadı veya eksik")
    history = _load_json(root / "data" / "reels_history.json", [])
    if not isinstance(history, list):
        raise ValueError("reels_history.json bir liste olmalı")

    ids = {p["id"] for p in strategy["pillars"]}
    # History has legacy Turkish names; support both ID and old pillar name.
    legacy = {
        "Sınav ve Sonuç Otomasyonları": "exam_automation",
        "Modern Web Tasarımı ve Yazılımları": "web_development",
        "Yapay Zekâ Ajanları ve İş Süreçleri": "ai_agents",
        "AI Destekli Sosyal Medya Yönetimi": "social_media_ai",
    }
    recent = []
    for row in history:
        if not isinstance(row, dict):
            continue
        try:
            stamp = date.fromisoformat(str(row.get("tarih", ""))[:10])
        except ValueError:
            continue
        if not day - timedelta(days=27) <= stamp <= day:
            continue
        service = row.get("service_id") or row.get("hizmet")
        pillar_id = service if service in ids else legacy.get(service)
        if pillar_id:
            recent.append((stamp, pillar_id, row))
    counts = Counter(pillar for _, pillar, _ in recent)
    last_pillar = sorted(recent, key=lambda x: (x[0], str(x[2].get("content_id", ""))))[-1][1] if recent else None
    pillars = strategy["pillars"]
    # Fair representation beats a rigid Monday=web schedule; tie breaks rotate by date.
    offset = day.toordinal() % len(pillars)
    indexed = list(enumerate(pillars))
    chosen_index, chosen = min(
        indexed,
        key=lambda item: (
            counts[item[1]["id"]],
            item[1]["id"] == last_pillar,
            (item[0] - offset) % len(pillars),
        ),
    )
    previous = [r for _, _, r in sorted(recent, key=lambda x: x[0], reverse=True)][:30]
    compact_history = [
        {
            "date": row.get("tarih"),
            "service": row.get("service_id") or row.get("hizmet"),
            "topic": row.get("konu"),
            "hook": row.get("hook"),
            "visual": row.get("görsel_yaklaşım"),
            "status": row.get("yayın_durumu"),
        }
        for row in previous
    ]
    prompt = (
        "Sen @malatyabilisim44 için kreatif yönetmen ve günlük üretim sorumlususun. "
        "Bugünkü içerik için sıfırdan ÜÇ ayrı, birbirinin kopyası olmayan fikir üret; "
        "somut iş problemi, alıcı, görsel olay, ilk saniye kancası ve satışa uygunluk açısından puanla. "
        "En güçlüsünü seç; günlük konuya özgü video promptunu, konuşma/ses tasarımını, "
        "gerekirse 2-3 kliplik storyboard'u, kapak başlığını ve doğal Türkçe Instagram açıklamasını üret. "
        "Hazır örnek neon/robot sahnesini tekrar etme. Yalnızca seçilen TEK hizmeti tanıt. "
        "Önceki içeriklerin semantik benzerliğini gözden geçir. Doğrulanmamış başarı iddiası üretme. "
        "Gemini Chrome arayüzünde GERÇEKTEN yeni sohbet aç, Video oluştur aracını seç, dikey 9:16 ayarla, "
        "bugün oluşturduğun YENİ promptu gönder, üretimin başladığını ve bittiğini doğrula. "
        "Eski videoyu indirip yeniymiş gibi gösterme. Gerçek üretim gözlenmezse "
        "GENERATION_NOT_VERIFIED yaz. Oluşursa Gemini bağlantısını sakla, gerçek MP4'ü "
        "resmî düğmeyle indir, SHA-256 ve metadata kontrolü yap. "
        "Kullanıcıya bağlantı ve caption sunup AWAITING_APPROVAL durumunda DUR. "
        "Kullanıcının açık onayı olmadan Upload-Post ile Instagram'a yayın yapma."
    )
    return {
        "content_id": f"MB44-{day:%Y%m%d}-{chosen['id']}",
        "date": day.isoformat(),
        "timezone": "Europe/Istanbul",
        "service_id": chosen["id"],
        "service_name": chosen["title"],
        "audience": chosen["audience"],
        "customer_problems": chosen["problems"],
        "keywords": chosen["keywords"],
        "cta": chosen["cta"],
        "style_options": chosen["styles"],
        "rotation_counts_last_28_days": {p["id"]: counts[p["id"]] for p in pillars},
        "recent_history": compact_history,
        "brand_rules_file": "prompts/creative-director.txt",
        "video_rules_file": "prompts/video-generation.txt",
        "instructions": prompt,
        "state": "BRIEF_READY_NOT_GENERATED",
        "no_automatic_publication": True,
    }


def save_daily_brief(root_dir=None, day=None):
    root = Path(root_dir) if root_dir else Path(__file__).resolve().parent.parent
    brief = build_daily_brief(root, day)
    folder = root / "runtime" / "briefs"
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / (brief["date"] + ".json")
    if destination.exists():
        # Rerunning the schedule must not silently change a day's brief.
        return _load_json(destination, {})
    temporary = folder / (brief["date"] + ".json.tmp")
    temporary.write_text(json.dumps(brief, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, destination)
    return brief


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="YYYY-MM-DD (default Europe/Istanbul today)")
    parser.add_argument("--root", help="Project folder; default repository root")
    args = parser.parse_args()
    result = save_daily_brief(args.root, args.date)
    print(json.dumps(result, ensure_ascii=False, indent=2))

# Malatya Bilişim — AI Reels Factory

Instagram: **@malatyabilisim44** | Kaynak: bu GitHub deposu | İşletim: Windows VDS üzerinde Antigravity'nin Chrome tarayıcı ajanı.

## Hedef

Dört hizmet için **her gün birbirinden farklı kreatif fikir ve video promptunu Antigravity kendi oluşturur**. Mevcut Google AI aboneliğindeki Gemini **Video oluştur** ekranını kullanarak yeni videoyu üretmeyi dener; Gemini'de izlenebilir bağlantıyı ve MP4 dosyasını hazırlar. Kullanıcı açıkça onay vermeden **hiçbir Instagram paylaşımı** yapılmaz.

Hizmetler: **sınav/bursluluk otomasyonu (SINAV), kurumsal web yazılımı (WEB), AI ajanları (AJAN), sosyal medya otomasyonu (SOSYAL).**

Bu depo bir video üretim API'si veya 7/24 çalışan servis değildir. **Günlük planlama script'i çalışır; Gemini UI'yi açıp gerçekten video üretmek Antigravity'nin VDS üzerindeki oturum yetkisine ve Automation'ın çalışmasına bağlıdır.** Bugünkü otomasyon burada etkinleştirilmemiştir. GitHub Actions yalnızca test çalıştırır, Gemini'ye girmez ve Instagram'a göndermez.

## VDS'de bir defalık kurulum

```powershell
cd "C:\Users\musab\.gemini\antigravity\scratch\malatya-bilisim"
git status
git pull --ff-only origin main
python -m pip install -r requirements.txt
python -m unittest discover -s tests -p "test_*.py"
python -m src.daily_brief
```

Günlük brief `runtime/briefs/YYYY-MM-DD.json` içine yazılır. Dosya aynı gün ikinci kez oluşturulmaz; bu, kayıtlarda tekrar oluşma riskini azaltır. Günlük planlayıcı aktif video modelini **çağırmaz**, sadece hizmet seçer, kısa bağlam ve yapılacak iş talimatlarını çıkarır.

**Antigravity → Automations → New Automation** altında günlük görev oluştur:

- Adı: `Malatya Bilişim — Günlük Özgün Reels`
- Proje: `malatya-bilisim`
- Saat: **09:00 Europe/Istanbul**. Yaklaşık tetikleme zamanıdır, tam dakikaya garanti yok.
- Her çalışmada yeni ajan oturumu (mevcut sonsuz sohbeti sürdürme).
- Görev promptu: **[`automations/daily_reels_agent.md`](automations/daily_reels_agent.md)** dosyasının "OTOMASYONUN HER ÇALIŞMASINDA" bölümündeki talimatlar.
- Önce bir defa **Run Now** ile yeni video üretimi, indirme ve oynatıcı linkini doğrula; gerçek yayını tetikleme.

Antigravity'nin resmi Automations özelliğini kullan; yalnızca oturuma bağlı `/schedule` zamanlayıcısını kalıcı günlük görev sanma. VDS açık, Windows oturumu ve Chrome/Gemini yetkisi çalışır olmalı; uzun süreli güvenilirlik kurulum sonrası ölçülmeli.

## İçerik motoru

- [`config/content_strategy.json`](config/content_strategy.json): 4 hizmet, gerçek karar vericiler, farklı problemler, SEO anahtar kelimeleri ve yasak iddialar.
- [`src/daily_brief.py`](src/daily_brief.py): son 28 günün kayıtlarından en az işlenen hizmeti seçer, son 30 kısa içerik kaydını verir.
- [`prompts/creative-director.txt`](prompts/creative-director.txt): hedef, 3 özgün fikirden tek seçim, yeni sahne/prompt üretimi, konuşma/insan/format seçenekleri.
- [`prompts/video-generation.txt`](prompts/video-generation.txt): değişken, sahneye özel Gemini/Flow prompt modeli, ses, hook, Reels SEO, video QC.
- [`src/gemini_downloader.py`](src/gemini_downloader.py): Gemini Chrome UI'sinde zaten indirilen medya için dosya aktarımı; **yeni video üretildiğini kendi başına kanıtlamaz**.
- [`src/video_checker.py`](src/video_checker.py): teknik MP4 metadata kontrolü.
- [`src/approval.py`](src/approval.py): dosya ve caption için onay kaydı.
- [`src/upload_post.py`](src/upload_post.py): Upload-Post üzerinden dosya aktarımı; **sadece explicit onay sonrası**.
- [`src/pipeline.py`](src/pipeline.py): mevcut test ve yayın yönetimi; dry-run gerçek yayımlanma değildir.

Günlük içerikte 8 saniye/insansız/izometrik format artık mecburi değildir. İnsan ve doğal Türkçe konuşma, gerçekçi iş sahnesi, UI animasyonu ve çeşitli klip uzunluğu kullanılabilir. Gerçek model süresi ve abonelik kotası geçerlidir; otomasyon hakları aşarak üretim denemesi yapmamalıdır.

## Statüler ve teslim

`BRIEF_READY_NOT_GENERATED` → `GENERATION_STARTED` → `GENERATION_VERIFIED` → `DOWNLOADED_AND_QC_PASSED` → `AWAITING_APPROVAL` → (açık onayla) `PUBLISHING` → `UPLOAD_ACCEPTED_UNVERIFIED` → (uzak sağlayıcıyla doğrulanırsa) `PUBLISHED`.

Model promptu yazdıysa `GENERATION_VERIFIED` yazılmaz. Eski videoyu indirmek yeni video değildir. Upload-Post 200 döndürdüyse, Instagram'da yayınlandığını doğrulamadan `PUBLISHED` yazılmaz. Ağ belirsizliğinde otomatik yeniden gönderme yapma; mükerrer yayın riski vardır. CLI dry-run asla yayımlanmış olarak işaretlememeli.

## Güvenlik — ÖNEMLİ

Bu GitHub deposu **public**. Daha önce **video dosyaları, kişisel hesap ve Upload-Post ekran görüntüleri, gerçek içerik geçmişi** git'e eklenmiş. Güncellenen `.gitignore` yeni medya ve ekran görüntülerini engeller, fakat **zaten takip edilen dosyaları geri çekmez**; önceki Git commit geçmişinde de kalırlar. Kayıtları ve ekran görüntülerini koruma/temizleme kararı ayrıca verilmeli. API anahtarı veya oturum çerezi açığa çıkmışsa derhal yenilenmeli.

Gelecekte `.env`, `data/*.mp4`, `screenshots/`, `runtime/`, `data/approvals.json` ve özel kullanıcı kayıtlarını public depoya ekleme. Gerçek videolar VDS diskinde/özel depolamada kalsın; Git yalnızca kod ve anonimleştirilmiş konfigürasyonu taşısın.

## Test ve kabul

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python -m src.daily_brief --date 2026-11-10
```

GitHub CI aynı testleri ücretli medya üretimi veya paylaşımı yapmadan çalıştırır. Kod testlerinin geçmesi gerçek Gemini tarayıcı/video üretimi ya da gerçek Instagram yayınının kanıtı değildir.

"""
Malatya Bilişim AI Reels Factory — Central Pipeline Orchestrator
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from .video_checker import VideoChecker
from .upload_post import UploadPostAdapter
from .approval import ApprovalManager
from .gemini_downloader import GeminiDownloadManager


class ReelsPipeline:
    """Orchestrates daily Reels generation, verification, approval, and publication."""

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = Path(root_dir) if root_dir else Path(__file__).resolve().parent.parent
        self.config_dir = self.root_dir / "config"
        self.data_dir = self.root_dir / "data"
        self.prompts_dir = self.root_dir / "prompts"

        # Load configurations
        with open(self.config_dir / "brand.json", "r", encoding="utf-8") as f:
            self.brand = json.load(f)

        with open(self.config_dir / "pipeline.json", "r", encoding="utf-8") as f:
            self.settings = json.load(f)

        self.history_path = self.root_dir / self.settings["storage"]["history_file"]
        self.video_checker = VideoChecker()
        self.downloader = GeminiDownloadManager(target_dir=str(self.data_dir))
        self.approval_mgr = ApprovalManager(str(self.data_dir / "approvals.json"))
        self.uploader = UploadPostAdapter(
            default_user=self.settings["upload_post"]["default_user"],
            default_platform=self.settings["upload_post"]["default_platform"]
        )

    def load_history(self) -> List[Dict[str, Any]]:
        """Load history records, keeping only the most recent N items."""
        if not self.history_path.exists():
            return []
        with open(self.history_path, "r", encoding="utf-8") as f:
            records = json.load(f)
        max_items = self.settings["storage"].get("max_history_items", 30)
        return records[-max_items:]

    def save_history(self, history: List[Dict[str, Any]]) -> None:
        """Save history records safely."""
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    def get_clean_daily_context(self) -> Dict[str, Any]:
        """
        Builds a minimal, clean daily context to prevent context-window bloat.
        Returns only the essential service pillars, rules, and the last 5 covered topics.
        """
        history = self.load_history()
        recent_topics = [
            {
                "tarih": h.get("tarih"),
                "konu": h.get("konu"),
                "hizmet": h.get("hizmet")
            }
            for h in history[-5:]
        ]

        return {
            "bugun": datetime.now().strftime("%Y-%m-%d"),
            "marka": self.brand["brand_name"],
            "instagram": self.brand["instagram_account"],
            "hizmet_alanlari": [p["name"] for p in self.brand["service_pillars"]],
            "yasakli_alanlar": self.brand["strictly_out_of_scope"],
            "son_islenen_konular": recent_topics,
            "baglam_kurali": "Bu görev bağımsız bir oturumdur. Geçmiş sohbet zinciri taşınmamıştır."
        }

    def register_new_reel(
        self,
        content_id: str,
        konu: str,
        hizmet: str,
        görsel_yaklaşım: str,
        kullanılan_model: str,
        video_dosyası: str,
        caption: str
    ) -> Dict[str, Any]:
        """Registers a newly prepared reel candidate into the pipeline history."""
        history = self.load_history()

        # Duplicate check
        for item in history:
            if item.get("content_id") == content_id:
                raise ValueError(f"Content ID '{content_id}' zaten mevcut!")

        entry = {
            "content_id": content_id,
            "tarih": datetime.now().strftime("%Y-%m-%d"),
            "konu": konu,
            "hizmet": hizmet,
            "görsel_yaklaşım": görsel_yaklaşım,
            "kullanılan_model": kullanılan_model,
            "video_dosyası": video_dosyası,
            "caption": caption,
            "üretim_durumu": "BEKLEMEDE",
            "kullanıcı_onayı": False,
            "yayın_durumu": "YAYIMLANMADI",
            "instagram_gönderi_kimliği": None
        }

        history.append(entry)
        self.save_history(history)
        return entry

    def ingest_gemini_video(
        self,
        dest_filename: str = "gemini_reel_latest.mp4",
        source_path: Optional[str] = None,
        not_before: Optional[float] = None
    ) -> Dict[str, Any]:
        """Ingests a NEW Gemini MP4; caller must supply verified generation start."""
        return self.downloader.ingest_downloaded_video(
            dest_filename=dest_filename, source_path=source_path, not_before=not_before
        )

    def _resolve_video_path(self, video_path: str) -> str:
        """Ensures video path is resolved absolutely against project root if relative."""
        p = Path(video_path)
        if not p.is_absolute():
            p = (self.root_dir / p).resolve()
        return str(p)

    def validate_reel_video(self, content_id: str, video_path: str) -> Dict[str, Any]:
        """Runs technical validation on the video file."""
        abs_path = self._resolve_video_path(video_path)
        info = self.video_checker.inspect_file(abs_path)
        history = self.load_history()
        for item in history:
            if item.get("content_id") == content_id:
                item["üretim_durumu"] = "DOĞRULANDI" if info["is_valid"] else "HATALI"
                item["video_teknik_rapor"] = {
                    "is_valid": info["is_valid"],
                    "resolution": f"{info['width']}x{info['height']}",
                    "duration": info["duration_seconds"],
                    "codec": info["video_codec"]
                }
                break
        self.save_history(history)
        return info

    def approve_reel(self, content_id: str, video_path: str, caption: str, approver: str = "kullanici") -> Dict[str, Any]:
        """Grants explicit human approval."""
        abs_path = self._resolve_video_path(video_path)
        record = self.approval_mgr.grant_approval(content_id, abs_path, caption, approved_by=approver)
        history = self.load_history()
        for item in history:
            if item.get("content_id") == content_id:
                item["kullanıcı_onayı"] = True
                item["onay_tarihi"] = record["timestamp"]
                break
        self.save_history(history)
        return record

    def publish_reel(self, content_id: str, video_path: str, caption: str, dry_run: bool = True) -> Dict[str, Any]:
        """
        Publishes the approved reel via Upload-Post.
        Enforces human approval and prevents duplicates.
        """
        abs_path = self._resolve_video_path(video_path)
        if self.approval_mgr.is_already_published(content_id):
            return {
                "success": False,
                "error": f"HATA: Bu içerik ({content_id}) daha önce zaten yayımlanmış. Mükerrer yayın engellendi."
            }

        # Human approval is for a specific video AND an exact caption.
        is_approved = self.approval_mgr.is_approved_and_unaltered(content_id, abs_path, caption=caption)
        if not is_approved:
            return {
                "success": False,
                "error": "GÜVENLİK ENGELİ: Videoya ve açıklamanın bu sürümüne ait açık onay yok."
            }

        history = self.load_history()
        matching = next((item for item in history if item.get("content_id") == content_id), None)
        if matching is None:
            return {"success": False, "error": "GÜVENLİK ENGELİ: Kayıtsız content_id yayımlanamaz."}
        # A timeout after an upload does not prove failure. Never automatically re-post.
        blocking = {"PUBLISHING", "UPLOAD_ACCEPTED_UNVERIFIED", "PUBLISH_UNKNOWN", "YAYIMLANDI"}
        if matching.get("yayın_durumu") in blocking:
            return {"success": False, "error": "Yayın durumu belirsiz veya tamamlanmış; tekrar gönderme engellendi."}

        if not dry_run:
            matching["yayın_durumu"] = "PUBLISHING"
            self.save_history(history)

        result = self.uploader.publish_reel(
            video_path=abs_path,
            caption=caption,
            is_approved=is_approved,
            content_id=content_id,
            dry_run=dry_run
        )

        history = self.load_history()
        for item in history:
            if item.get("content_id") != content_id:
                continue
            if dry_run:
                # Dry-run validates locally; it never creates a published record.
                item["yayın_durumu"] = "DRY_RUN_BAŞARILI" if result.get("success") else "DRY_RUN_FAILED"
            elif result.get("success"):
                # HTTP 200/201 may only acknowledge intake, not Instagram publication.
                item["yayın_durumu"] = "UPLOAD_ACCEPTED_UNVERIFIED"
            else:
                # Preserve the uncertain state until provider-side reconciliation.
                item["yayın_durumu"] = "PUBLISH_UNKNOWN"
            item["yayın_yanıtı"] = result.get("response")
            break
        self.save_history(history)
        return result


if __name__ == "__main__":
    pipeline = ReelsPipeline()
    print("Clean Daily Context Sample:")
    print(json.dumps(pipeline.get_clean_daily_context(), indent=2, ensure_ascii=False))

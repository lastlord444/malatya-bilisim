"""
Malatya Bilişim AI Reels Factory — Gemini Video Download Manager
Handles detection, integrity verification, and relocation of MP4 files downloaded from Gemini.
"""

import os
import time
import shutil
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from .video_checker import VideoChecker


class GeminiDownloadManager:
    """Manages files downloaded via Gemini's official UI download button."""

    def __init__(self, downloads_dir: Optional[str] = None, target_dir: Optional[str] = None):
        user_home = Path.home()
        self.downloads_dir = Path(downloads_dir) if downloads_dir else user_home / "Downloads"
        self.target_dir = Path(target_dir) if target_dir else Path(__file__).resolve().parent.parent / "data"
        self.target_dir.mkdir(parents=True, exist_ok=True)
        self.checker = VideoChecker()

    def find_latest_gemini_video(self, max_age_seconds: int = 3600, not_before: Optional[float] = None) -> Optional[Path]:
        """Return a Gemini-named MP4 downloaded AFTER verified generation started."""
        if not self.downloads_dir.exists():
            return None

        # Never take an arbitrary older MP4 from Downloads as today's new Gemini clip.
        candidates = list(self.downloads_dir.glob("gemini_generated_video_*.mp4"))

        if not candidates:
            return None

        # Sort by modification time descending
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        for candidate in candidates:
            modified = candidate.stat().st_mtime
            if not_before is not None and modified < not_before:
                continue
            if 0 <= time.time() - modified <= max_age_seconds:
                return candidate
        return None

    def wait_for_download_completion(self, file_path: Path, timeout_seconds: int = 30) -> bool:
        """Ensures file is fully downloaded and not being written to."""
        crdownload = file_path.with_suffix(file_path.suffix + ".crdownload")
        start_time = time.time()

        while time.time() - start_time < timeout_seconds:
            if crdownload.exists():
                time.sleep(1)
                continue

            if file_path.exists():
                size1 = file_path.stat().st_size
                time.sleep(1)
                size2 = file_path.stat().st_size
                if size1 == size2 and size1 > 0:
                    return True

            time.sleep(1)

        return False

    def ingest_downloaded_video(
        self,
        dest_filename: str = "gemini_reel_latest.mp4",
        source_path: Optional[str] = None,
        not_before: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Relocates downloaded Gemini video to project data directory and verifies its technical specs.
        """
        if not source_path and not_before is None:
            return {"success": False, "error": "Yeni üretim başlangıç zamanı (not_before) zorunlu; eski video otomatik alınamaz.", "video_path": None}
        source = Path(source_path) if source_path else self.find_latest_gemini_video(not_before=not_before)

        if not source or not source.exists():
            return {
                "success": False,
                "error": f"İndirilen Gemini videosu bulunamadı. Kaynak: {source}",
                "video_path": None
            }

        # Ensure download complete
        if not self.wait_for_download_completion(source):
            return {
                "success": False,
                "error": "Video dosyasının indirilmesi zaman aşımına uğradı veya dosya kilitli.",
                "video_path": None
            }

        # Unique content_id filenames prevent a later run from silently replacing approved media.
        dest = self.target_dir / dest_filename
        if dest.exists():
            return {"success": False, "error": f"Hedef MP4 zaten var (üzerine yazılmadı): {dest}", "video_path": str(dest)}
        shutil.copy2(source, dest)

        # Inspect the copied file
        report = self.checker.inspect_file(str(dest))

        return {
            "success": report["is_valid"],
            "source_path": str(source),
            "dest_path": str(dest),
            "file_name": dest.name,
            "sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
            "file_size_bytes": report["file_size_bytes"],
            "file_size_mb": report["file_size_mb"],
            "technical_report": report,
            "error": report["errors"][0] if report["errors"] else None
        }


if __name__ == "__main__":
    mgr = GeminiDownloadManager()
    latest = mgr.find_latest_gemini_video()
    print("Latest Gemini Video in Downloads:", latest)
    if latest:
        ingest_result = mgr.ingest_downloaded_video(dest_filename="test_ingest.mp4", source_path=str(latest))
        import json
        print(json.dumps(ingest_result, indent=2, ensure_ascii=False))

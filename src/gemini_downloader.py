"""
Malatya Bilişim AI Reels Factory — Gemini Video Download Manager
Handles detection, integrity verification, and relocation of MP4 files downloaded from Gemini.
"""

import os
import time
import shutil
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

    def find_latest_gemini_video(self, max_age_seconds: int = 3600) -> Optional[Path]:
        """Finds the most recently downloaded Gemini MP4 file."""
        if not self.downloads_dir.exists():
            return None

        # Look for gemini_generated_video_*.mp4 or newly downloaded MP4 files
        candidates = list(self.downloads_dir.glob("gemini_generated_video_*.mp4"))
        if not candidates:
            # Fallback to general mp4 files
            candidates = list(self.downloads_dir.glob("*.mp4"))

        if not candidates:
            return None

        # Sort by modification time descending
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        latest = candidates[0]

        # Check age
        file_age = time.time() - latest.stat().st_mtime
        if file_age <= max_age_seconds:
            return latest

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
        source_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Relocates downloaded Gemini video to project data directory and verifies its technical specs.
        """
        source = Path(source_path) if source_path else self.find_latest_gemini_video()

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

        dest = self.target_dir / dest_filename
        shutil.copy2(source, dest)

        # Inspect the copied file
        report = self.checker.inspect_file(str(dest))

        return {
            "success": report["is_valid"],
            "source_path": str(source),
            "dest_path": str(dest),
            "file_name": dest.name,
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

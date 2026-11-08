"""
Unit tests for GeminiDownloadManager
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.gemini_downloader import GeminiDownloadManager


class TestGeminiDownloader(unittest.TestCase):

    def setUp(self):
        self.temp_downloads = tempfile.mkdtemp()
        self.temp_target = tempfile.mkdtemp()
        self.manager = GeminiDownloadManager(
            downloads_dir=self.temp_downloads,
            target_dir=self.temp_target
        )

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_downloads, ignore_errors=True)
        shutil.rmtree(self.temp_target, ignore_errors=True)

    def test_find_latest_gemini_video(self):
        # Create dummy video file
        sample = Path(self.temp_downloads) / "gemini_generated_video_12345678.mp4"
        sample.write_bytes(b"dummy video data")

        latest = self.manager.find_latest_gemini_video()
        self.assertIsNotNone(latest)
        self.assertEqual(latest.name, "gemini_generated_video_12345678.mp4")

    def test_automatic_ingest_requires_verified_start_marker(self):
        sample = Path(self.temp_downloads) / "gemini_generated_video_new.mp4"
        sample.write_bytes(b"dummy video")
        result = self.manager.ingest_downloaded_video(dest_filename="new.mp4")
        self.assertFalse(result["success"])
        self.assertIn("not_before", result["error"])

    def test_does_not_reuse_video_from_before_generation(self):
        import time
        sample = Path(self.temp_downloads) / "gemini_generated_video_old.mp4"
        sample.write_bytes(b"old")
        past = time.time() - 300
        os.utime(sample, (past, past))
        found = self.manager.find_latest_gemini_video(
            max_age_seconds=3600, not_before=time.time() - 30
        )
        self.assertIsNone(found)

    def test_ingest_downloaded_video(self):
        sample = Path(self.temp_downloads) / "gemini_generated_video_abcdef12.mp4"
        sample.write_bytes(b"mp4 content test bytes")

        res = self.manager.ingest_downloaded_video(
            dest_filename="ingested_reel.mp4",
            source_path=str(sample)
        )
        # A dummy byte string is NOT a playable video; do not mark it as PASS.
        self.assertFalse(res["success"])
        self.assertEqual(res["file_name"], "ingested_reel.mp4")
        self.assertTrue(Path(res["dest_path"]).exists())


if __name__ == "__main__":
    unittest.main()

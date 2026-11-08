"""Regression tests for dry-run and caption-bound approval safety."""
import json
import tempfile
import unittest
from pathlib import Path

from src.pipeline import ReelsPipeline


class FakeUploader:
    def __init__(self):
        self.calls = []

    def publish_reel(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "success": True,
            "dry_run": kwargs["dry_run"],
            "response": {"request_id": "test-accepted-not-published"}
        }


class PipelineSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        (root / "config").mkdir()
        (root / "data").mkdir()
        (root / "prompts").mkdir()
        (root / "config" / "brand.json").write_text(json.dumps({
            "brand_name": "Test", "instagram_account": "@malatyabilisim44",
            "service_pillars": [], "strictly_out_of_scope": []
        }), encoding="utf-8")
        (root / "config" / "pipeline.json").write_text(json.dumps({
            "storage": {"history_file": "data/reels_history.json", "max_history_items": 30},
            "upload_post": {"default_user": "default", "default_platform": "instagram"}
        }), encoding="utf-8")
        (root / "data" / "reels_history.json").write_text("[]", encoding="utf-8")
        self.video = root / "data" / "new.mp4"
        self.video.write_bytes(b"test-bytes-that-are-not-published")
        self.pipe = ReelsPipeline(str(root))
        self.pipe.register_new_reel("DAILY-001", "test", "web_development",
                                    "UI", "Gemini", str(self.video), "Approved caption")
        self.fake = FakeUploader()
        self.pipe.uploader = self.fake

    def tearDown(self):
        self.temp.cleanup()

    def test_dry_run_does_not_mark_published(self):
        self.pipe.approve_reel("DAILY-001", str(self.video), "Approved caption")
        first = self.pipe.publish_reel("DAILY-001", str(self.video), "Approved caption", dry_run=True)
        self.assertTrue(first["success"])
        self.assertFalse(self.pipe.approval_mgr.is_already_published("DAILY-001"))
        self.assertEqual(self.pipe.load_history()[0]["yayın_durumu"], "DRY_RUN_BAŞARILI")

    def test_different_caption_is_rejected(self):
        self.pipe.approve_reel("DAILY-001", str(self.video), "Approved caption")
        result = self.pipe.publish_reel("DAILY-001", str(self.video), "Changed caption", dry_run=True)
        self.assertFalse(result["success"])
        self.assertEqual(len(self.fake.calls), 0)

    def test_accepted_upload_is_not_verified_publication(self):
        self.pipe.approve_reel("DAILY-001", str(self.video), "Approved caption")
        first = self.pipe.publish_reel("DAILY-001", str(self.video), "Approved caption", dry_run=False)
        self.assertTrue(first["success"])
        self.assertEqual(self.pipe.load_history()[0]["yayın_durumu"], "UPLOAD_ACCEPTED_UNVERIFIED")
        self.assertFalse(self.pipe.approval_mgr.is_already_published("DAILY-001"))
        blocked = self.pipe.publish_reel("DAILY-001", str(self.video), "Approved caption", dry_run=False)
        self.assertFalse(blocked["success"])
        self.assertEqual(len(self.fake.calls), 1)


if __name__ == "__main__":
    unittest.main()

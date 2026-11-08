"""
Unit tests for UploadPostAdapter
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.upload_post import UploadPostAdapter


class TestUploadPost(unittest.TestCase):

    def setUp(self):
        self.adapter = UploadPostAdapter(api_key="mock_test_key")

    def test_unapproved_rejection(self):
        res = self.adapter.publish_reel(
            video_path="any.mp4",
            caption="Test",
            is_approved=False,
            content_id="TEST-001"
        )
        self.assertFalse(res["success"])
        self.assertIn("GÜVENLİK ENGELİ", res["error"])

    def test_dry_run_success(self):
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            f.write(b"video dummy data")
            temp_path = f.name
        try:
            res = self.adapter.publish_reel(
                video_path=temp_path,
                caption="Malatya Bilişim AI Test #malatya",
                is_approved=True,
                content_id="TEST-002",
                dry_run=True
            )
            self.assertTrue(res["success"])
            self.assertTrue(res["dry_run"])
            self.assertEqual(res["status_code"], 200)
            self.assertEqual(res["response"]["target_account"], "@malatyabilisim44")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_missing_file_with_approval(self):
        res = self.adapter.publish_reel(
            video_path="non_existing_path_123.mp4",
            caption="Test",
            is_approved=True,
            content_id="TEST-003",
            dry_run=False
        )
        self.assertFalse(res["success"])
        self.assertIn("Video dosyası bulunamadı", res["error"])


if __name__ == "__main__":
    unittest.main()

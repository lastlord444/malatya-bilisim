"""
Unit tests for ApprovalManager
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.approval import ApprovalManager


class TestApprovalManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.approvals_file = os.path.join(self.temp_dir.name, "approvals.json")
        self.mgr = ApprovalManager(self.approvals_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_grant_and_verify_approval(self):
        video_path = os.path.join(self.temp_dir.name, "test.mp4")
        with open(video_path, "wb") as f:
            f.write(b"original video content")

        record = self.mgr.grant_approval("REEL-01", video_path, "Caption", approved_by="admin")
        self.assertTrue(record["approved"])
        self.assertTrue(self.mgr.is_approved_and_unaltered("REEL-01", video_path))

    def test_tampered_file_detection(self):
        video_path = os.path.join(self.temp_dir.name, "test_tamper.mp4")
        with open(video_path, "wb") as f:
            f.write(b"original content")

        self.mgr.grant_approval("REEL-02", video_path, "Caption")
        self.assertTrue(self.mgr.is_approved_and_unaltered("REEL-02", video_path))

        # Tamper the file
        with open(video_path, "wb") as f:
            f.write(b"tampered or revised content")

        # Now hash mismatch must trigger rejection
        self.assertFalse(self.mgr.is_approved_and_unaltered("REEL-02", video_path))

    def test_duplicate_prevention(self):
        video_path = os.path.join(self.temp_dir.name, "test_dup.mp4")
        with open(video_path, "wb") as f:
            f.write(b"content")

        self.mgr.grant_approval("REEL-03", video_path, "Caption")
        self.assertFalse(self.mgr.is_already_published("REEL-03"))

        self.mgr.mark_published("REEL-03")
        self.assertTrue(self.mgr.is_already_published("REEL-03"))


if __name__ == "__main__":
    unittest.main()

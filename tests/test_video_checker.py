"""
Unit tests for VideoChecker
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.video_checker import VideoChecker


class TestVideoChecker(unittest.TestCase):

    def setUp(self):
        self.checker = VideoChecker()

    def test_missing_file(self):
        res = self.checker.inspect_file("non_existent_file.mp4")
        self.assertFalse(res["exists"])
        self.assertFalse(res["is_valid"])
        self.assertTrue(len(res["errors"]) > 0)

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            temp_path = f.name
        try:
            res = self.checker.inspect_file(temp_path)
            self.assertTrue(res["exists"])
            self.assertEqual(res["file_size_bytes"], 0)
            self.assertFalse(res["is_valid"])
            self.assertIn("Dosya boyutu 0 bayt (boş dosya).", res["errors"])
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_mock_mp4_header(self):
        # Create a small file with MP4 ftyp box
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            # 4 bytes size, 4 bytes 'ftyp', brand 'isom'
            f.write(b"\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2mp41")
            temp_path = f.name
        try:
            res = self.checker.inspect_file(temp_path)
            self.assertTrue(res["exists"])
            self.assertGreater(res["file_size_bytes"], 0)
            self.assertEqual(res["video_codec"], "mp4_container")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()

"""
Unit tests for GeminiAccountManager
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.account_manager import GeminiAccountManager


class TestAccountManager(unittest.TestCase):

    def test_default_url(self):
        mgr = GeminiAccountManager(target_account_index=0)
        self.assertEqual(mgr.get_gemini_url(), "https://gemini.google.com/app")

    def test_multi_account_url(self):
        mgr = GeminiAccountManager(target_account_index=1)
        self.assertEqual(mgr.get_gemini_url(), "https://gemini.google.com/u/1/app")
        self.assertEqual(mgr.get_gemini_url(2), "https://gemini.google.com/u/2/app")

    def test_parse_account_info(self):
        mgr = GeminiAccountManager(target_email="other@gmail.com")
        label = "Google Hesabı: Ahmet Yılmaz\n(other@gmail.com), Google üyeliği"
        info = mgr.parse_account_info(label)
        self.assertEqual(info["email"], "other@gmail.com")
        self.assertEqual(info["name"], "Ahmet Yılmaz")
        self.assertTrue(info["is_target"])


if __name__ == "__main__":
    unittest.main()

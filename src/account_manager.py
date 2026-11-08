"""
Malatya Bilişim AI Reels Factory — Gemini Multi-Account & Session Manager
Allows seamless switching between different Google / Gemini accounts.
"""

import os
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class GeminiAccountManager:
    """Manages active Google/Gemini session detection and multi-account navigation."""

    def __init__(self, target_account_index: Optional[int] = None, target_email: Optional[str] = None):
        env_index = os.getenv("GEMINI_ACCOUNT_INDEX")
        self.target_account_index = int(env_index) if env_index and env_index.isdigit() else (target_account_index or 0)
        self.target_email = target_email or os.getenv("GEMINI_TARGET_EMAIL", "").strip()

    def get_gemini_url(self, account_index: Optional[int] = None) -> str:
        """Returns the appropriate Gemini URL for the requested account index."""
        idx = account_index if account_index is not None else self.target_account_index
        if idx > 0:
            return f"https://gemini.google.com/u/{idx}/app"
        return "https://gemini.google.com/app"

    def parse_account_info(self, raw_label: str) -> Dict[str, Any]:
        """Parses Google Account aria-label text to extract name and email."""
        info = {
            "name": "Unknown",
            "email": "Unknown",
            "is_target": False,
            "raw": raw_label
        }
        if not raw_label:
            return info

        # Example: "Google Hesabı: Hasan Payer  \n(lastlord444@gmail.com)"
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", raw_label)
        if email_match:
            info["email"] = email_match.group(0)

        # Name extraction
        name_match = re.search(r"(?:Google Hesabı|Google Account):\s*([^\n\(\)]+)", raw_label)
        if name_match:
            info["name"] = name_match.group(1).strip()

        if self.target_email and info["email"].lower() == self.target_email.lower():
            info["is_target"] = True

        return info


if __name__ == "__main__":
    mgr = GeminiAccountManager()
    print("Default URL:", mgr.get_gemini_url())
    print("Account 1 URL:", mgr.get_gemini_url(1))
    sample_label = "Google Hesabı: Test User (test@example.com), Google üyeliği"
    print("Parsed Sample:", mgr.parse_account_info(sample_label))

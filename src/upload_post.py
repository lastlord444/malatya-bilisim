"""
Malatya Bilişim AI Reels Factory — Upload-Post Publication Adapter
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class UploadPostAdapter:
    """Manages secure communication with the Upload-Post REST API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.upload-post.com/api",
        default_user: str = "default",
        default_platform: str = "instagram"
    ):
        self.api_key = api_key or os.getenv("UPLOAD_POST_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.default_user = default_user or os.getenv("UPLOAD_POST_USER", "default")
        self.default_platform = default_platform or os.getenv("UPLOAD_POST_PLATFORM", "instagram")

    def publish_reel(
        self,
        video_path: str,
        caption: str,
        is_approved: bool,
        content_id: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Uploads an approved MP4 video to Instagram via Upload-Post.
        
        Strict Safety Rules:
        - Rejects unapproved videos immediately.
        - Checks for file existence and readability.
        - Supports dry_run mode to test configuration safely without making a real post.
        """
        response_data: Dict[str, Any] = {
            "success": False,
            "content_id": content_id,
            "dry_run": dry_run,
            "status_code": 0,
            "response": {},
            "error": None
        }

        # 1. Verification of human approval
        if not is_approved:
            response_data["error"] = "GÜVENLİK ENGELİ: Kullanıcı açık onayı olmadan Instagram paylaşımı yapılamaz."
            return response_data

        # 2. File verification
        path = Path(video_path).resolve()
        if not path.exists():
            response_data["error"] = f"Video dosyası bulunamadı: {video_path}"
            return response_data

        if path.stat().st_size == 0:
            response_data["error"] = "Video dosyası boş (0 byte)."
            return response_data

        # 3. Dry-Run simulation
        if dry_run:
            response_data["success"] = True
            response_data["status_code"] = 200
            response_data["response"] = {
                "message": "DRY RUN MODE: Video and caption validated successfully. No external API call made.",
                "target_account": "@malatyabilisim44",
                "profile_user": self.default_user,
                "platform": self.default_platform,
                "file_name": path.name,
                "caption_preview": caption[:80] + "..." if len(caption) > 80 else caption
            }
            return response_data

        # 4. API Key verification
        if not self.api_key or "your_upload_post" in self.api_key:
            response_data["error"] = "UPLOAD_POST_API_KEY tanımlanmamış veya geçersiz."
            return response_data

        # 5. Multipart Form-Data Upload
        upload_url = f"{self.base_url}/upload"
        headers = {
            "Authorization": f"Apikey {self.api_key}"
        }

        data = {
            "title": caption,
            "user": self.default_user,
            "platform[]": self.default_platform
        }

        try:
            with open(path, "rb") as video_file:
                files = {
                    "video": (path.name, video_file, "video/mp4")
                }
                res = requests.post(upload_url, headers=headers, data=data, files=files, timeout=120)
                response_data["status_code"] = res.status_code

                try:
                    response_data["response"] = res.json()
                except Exception:
                    response_data["response"] = {"text": res.text}

                if res.status_code in (200, 201):
                    response_data["success"] = True
                else:
                    response_data["error"] = f"Upload-Post API Hatası: HTTP {res.status_code} — {res.text}"

        except requests.exceptions.RequestException as e:
            response_data["error"] = f"Ağ / Bağlantı Hatası: {str(e)}"

        return response_data


if __name__ == "__main__":
    adapter = UploadPostAdapter()
    test_result = adapter.publish_reel(
        video_path="test_sample.mp4",
        caption="Malatya Bilişim Yapay Zekâ Otomasyonları #malatya",
        is_approved=True,
        content_id="TEST-001",
        dry_run=True
    )
    print(json.dumps(test_result, indent=2, ensure_ascii=False))

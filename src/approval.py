"""
Malatya Bilişim AI Reels Factory — Human Approval Manager
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class ApprovalManager:
    """Ensures no content is published without explicit human approval."""

    def __init__(self, approvals_file: str = "data/approvals.json"):
        self.approvals_file = Path(approvals_file).resolve()
        self.approvals_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        if not self.approvals_file.exists():
            with open(self.approvals_file, "w", encoding="utf-8") as f:
                json.dump({"approved_records": {}, "audit_log": []}, f, indent=2)

    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of video file to detect any modifications."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def grant_approval(
        self,
        content_id: str,
        video_path: str,
        caption: str,
        approved_by: str = "user"
    ) -> Dict[str, Any]:
        """Record an explicit human approval."""
        path = Path(video_path).resolve()
        file_hash = self.calculate_file_hash(str(path)) if path.exists() else "no_file"

        with open(self.approvals_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        record = {
            "content_id": content_id,
            "video_path": str(path),
            "video_hash": file_hash,
            "caption": caption,
            "approved": True,
            "approved_by": approved_by,
            "timestamp": datetime.now().isoformat(),
            "published": False
        }

        data["approved_records"][content_id] = record
        data["audit_log"].append({
            "action": "APPROVAL_GRANTED",
            "content_id": content_id,
            "timestamp": datetime.now().isoformat(),
            "by": approved_by
        })

        with open(self.approvals_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return record

    def revoke_approval(self, content_id: str, reason: str = "Düzeltme yapıldı") -> None:
        """Revoke approval for content if modifications occur."""
        with open(self.approvals_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if content_id in data["approved_records"]:
            del data["approved_records"][content_id]
            data["audit_log"].append({
                "action": "APPROVAL_REVOKED",
                "content_id": content_id,
                "timestamp": datetime.now().isoformat(),
                "reason": reason
            })
            with open(self.approvals_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def is_approved_and_unaltered(self, content_id: str, video_path: str) -> bool:
        """Verify that content has approval and the file has not been altered since approval."""
        with open(self.approvals_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        record = data.get("approved_records", {}).get(content_id)
        if not record or not record.get("approved"):
            return False

        path = Path(video_path).resolve()
        if not path.exists():
            return False

        current_hash = self.calculate_file_hash(str(path))
        return current_hash == record.get("video_hash")

    def mark_published(self, content_id: str, publication_meta: Optional[Dict[str, Any]] = None) -> None:
        """Mark content as published to prevent duplicates."""
        with open(self.approvals_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if content_id in data["approved_records"]:
            data["approved_records"][content_id]["published"] = True
            data["approved_records"][content_id]["published_at"] = datetime.now().isoformat()
            if publication_meta:
                data["approved_records"][content_id]["publication_meta"] = publication_meta

        data["audit_log"].append({
            "action": "CONTENT_PUBLISHED",
            "content_id": content_id,
            "timestamp": datetime.now().isoformat()
        })

        with open(self.approvals_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def is_already_published(self, content_id: str) -> bool:
        """Check if content has already been published to Instagram."""
        with open(self.approvals_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        record = data.get("approved_records", {}).get(content_id)
        return bool(record and record.get("published", False))


if __name__ == "__main__":
    mgr = ApprovalManager()
    print("Approval manager initialized successfully.")

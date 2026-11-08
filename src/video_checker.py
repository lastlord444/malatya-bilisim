"""
Malatya Bilişim AI Reels Factory — Video Checker & Technical Validator
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


class VideoChecker:
    """Validates MP4 files for Instagram Reels compliance."""

    def __init__(self, ffprobe_path: str = "ffprobe"):
        self.ffprobe_path = ffprobe_path

    def inspect_file(self, file_path: str) -> Dict[str, Any]:
        """Perform comprehensive technical verification on a local video file."""
        path = Path(file_path).resolve()

        result: Dict[str, Any] = {
            "file_path": str(path),
            "file_name": path.name,
            "exists": path.exists(),
            "file_size_bytes": 0,
            "file_size_mb": 0.0,
            "is_valid": False,
            "duration_seconds": 0.0,
            "width": 0,
            "height": 0,
            "aspect_ratio": "unknown",
            "video_codec": "unknown",
            "has_audio": False,
            "audio_codec": None,
            "is_9_16_vertical": False,
            "errors": [],
            "warnings": []
        }

        if not path.exists():
            result["errors"].append(f"Dosya bulunamadı: {file_path}")
            return result

        result["file_size_bytes"] = path.stat().st_size
        result["file_size_mb"] = round(result["file_size_bytes"] / (1024 * 1024), 2)

        if result["file_size_bytes"] == 0:
            result["errors"].append("Dosya boyutu 0 bayt (boş dosya).")
            return result

        # Run ffprobe extraction
        probe_data = self._run_ffprobe(str(path))
        if probe_data:
            self._parse_probe_data(probe_data, result)
        else:
            # Container signatures are not proof of a playable video.
            self._fallback_mp4_inspect(path, result)
            result["errors"].append("FFprobe ile oynatılabilir medya doğrulanamadı; yayın engellendi.")

        # Evaluate validity criteria for Instagram Reels
        if result["width"] > 0 and result["height"] > 0:
            ratio = result["width"] / result["height"]
            # 9/16 is 0.5625; allow reasonable tolerance [0.50, 0.60]
            if 0.50 <= ratio <= 0.60:
                result["is_9_16_vertical"] = True
                result["aspect_ratio"] = "9:16"
            else:
                result["aspect_ratio"] = f"{result['width']}:{result['height']}"
                result["errors"].append(
                    f"Video 9:16 değil ({result['aspect_ratio']}); Reels için dikey medya gerekli."
                )

        if not result["has_audio"]:
            result["warnings"].append("Video ses akışı içermiyor (sessiz video).")

        if result["duration_seconds"] <= 0:
            result["errors"].append("Video süresi doğrulanamadı.")
        if result["video_codec"] not in ("h264", "avc1"):
            result["errors"].append(f"Desteklenmeyen/doğrulanamayan video codec: {result['video_codec']}")
        if result["width"] < 720 or result["height"] < 1280:
            result["errors"].append("Video en az 720x1280 olmalı.")

        if len(result["errors"]) == 0 and result["file_size_bytes"] > 0 and result["is_9_16_vertical"]:
            result["is_valid"] = True

        return result

    def _run_ffprobe(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Run ffprobe to get structured JSON metadata."""
        cmd = [
            self.ffprobe_path,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            file_path
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
            return json.loads(res.stdout)
        except Exception:
            # Try finding ffprobe in common winget installation paths
            alt_paths = [
                os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffprobe.exe"),
                os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps\ffprobe.exe"),
                r"C:\Program Files\ffmpeg\bin\ffprobe.exe"
            ]
            for alt in alt_paths:
                if os.path.exists(alt):
                    try:
                        cmd[0] = alt
                        res = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
                        return json.loads(res.stdout)
                    except Exception:
                        pass
            return None

    def _parse_probe_data(self, data: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Parse streams and format from ffprobe output."""
        fmt = data.get("format", {})
        if "duration" in fmt:
            try:
                result["duration_seconds"] = round(float(fmt["duration"]), 2)
            except (ValueError, TypeError):
                pass

        for stream in data.get("streams", []):
            codec_type = stream.get("codec_type")
            if codec_type == "video" and result["video_codec"] == "unknown":
                result["video_codec"] = stream.get("codec_name", "unknown")
                result["width"] = int(stream.get("width", 0))
                result["height"] = int(stream.get("height", 0))
                if result["duration_seconds"] == 0.0 and "duration" in stream:
                    try:
                        result["duration_seconds"] = round(float(stream["duration"]), 2)
                    except (ValueError, TypeError):
                        pass
            elif codec_type == "audio":
                result["has_audio"] = True
                result["audio_codec"] = stream.get("codec_name")

    def _fallback_mp4_inspect(self, path: Path, result: Dict[str, Any]) -> None:
        """Fallback check inspecting MP4 header signatures."""
        try:
            with open(path, "rb") as f:
                header = f.read(64)
                if b"ftyp" in header:
                    result["video_codec"] = "mp4_container"
                else:
                    result["warnings"].append("Standart MP4 ftyp başlığı tespit edilemedi.")
        except Exception as e:
            result["errors"].append(f"Dosya okuma hatası: {str(e)}")


if __name__ == "__main__":
    import sys
    test_file = sys.argv[1] if len(sys.argv) > 1 else "test_sample.mp4"
    checker = VideoChecker()
    info = checker.inspect_file(test_file)
    print(json.dumps(info, indent=2, ensure_ascii=False))

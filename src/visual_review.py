"""Extract timestamped frames for mandatory human/agent VISUAL story QA.

This utility does not evaluate creative quality automatically. The inspecting
agent must check every frame and the complete video before marking visual QA PASS.
Requires ffmpeg + ffprobe; writes into ignored runtime/visual_reviews/.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
from pathlib import Path


def sample_times(duration_seconds: float, interval: float = 2.0) -> list[float]:
    """Return review timestamps covering the entire clip, including its ending."""
    if not math.isfinite(duration_seconds) or duration_seconds <= 0:
        raise ValueError("Video duration must be positive and finite")
    if not math.isfinite(interval) or interval <= 0:
        raise ValueError("Review interval must be positive and finite")
    ending = max(0.0, duration_seconds - 0.15)
    stamps = []
    point = min(0.25, ending)
    while point <= ending:
        stamps.append(round(point, 3))
        point += interval
    if stamps and ending - stamps[-1] > min(1.0, interval * 0.5):
        stamps.append(round(ending, 3))
    return stamps


def probe_duration(video: Path) -> float:
    output = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        capture_output=True, text=True, check=True, timeout=25
    )
    return float(output.stdout.strip())


def extract_review_frames(video_path: str, output_dir: str | None = None,
                          interval_seconds: float = 2.0) -> dict:
    video = Path(video_path).resolve()
    if not video.is_file() or video.stat().st_size == 0:
        raise FileNotFoundError(f"Video missing or empty: {video}")
    duration = probe_duration(video)
    root = Path(__file__).resolve().parent.parent
    safe_stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", video.stem)[:70]
    target = Path(output_dir).resolve() if output_dir else (
        root / "runtime" / "visual_reviews" / safe_stem
    )
    target.mkdir(parents=True, exist_ok=True)

    review = {
        "video": str(video),
        "duration_seconds": round(duration, 3),
        "interval_seconds": interval_seconds,
        "visual_qc_status": "REVIEW_REQUIRED",
        "note": "Metadata is not story QA. Inspect all frames plus playback. "
                "Check service consistency, shot continuity, actor eye line, "
                "device orientation, Turkish wording, fake UI, and claims.",
        "frames": []
    }
    for idx, second in enumerate(sample_times(duration, interval_seconds)):
        filename = f"frame_{idx:02d}_{second:.2f}s.jpg"
        path = target / filename
        subprocess.run(
            ["ffmpeg", "-nostdin", "-y", "-hide_banner", "-loglevel", "error",
             "-ss", str(second), "-i", str(video),
             "-frames:v", "1", "-vf", "scale=360:-2",
             "-q:v", "3", str(path)],
            capture_output=True, text=True, check=True, timeout=40
        )
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"FFmpeg did not extract frame at {second}s")
        review["frames"].append({"seconds": second, "file": str(path)})

    (target / "review_manifest.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    return review


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True, help="Existing MP4 video path")
    parser.add_argument("--out", help="Optional local output folder")
    parser.add_argument("--interval", type=float, default=2.0)
    args = parser.parse_args()
    result = extract_review_frames(args.video, args.out, args.interval)
    print(json.dumps(result, ensure_ascii=False, indent=2))

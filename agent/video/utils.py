"""
agent/video/utils.py

Utility helpers for the video generation module:
  - get_audio_duration   : reliable MP3 duration via mutagen
  - build_segment_data   : assemble per-segment {audio_path, image_path} from state fields
  - validate_inputs      : ensure every segment file exists and has valid duration
"""

import logging
from pathlib import Path

from mutagen.mp3 import MP3

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Audio duration
# ---------------------------------------------------------------------------

def get_audio_duration(audio_path: str | Path) -> float:
    """
    Return the duration of an MP3 file in seconds using mutagen.
    Raises FileNotFoundError if the file does not exist.
    Raises ValueError if duration cannot be read.
    """
    p = Path(audio_path)
    if not p.exists():
        raise FileNotFoundError(f"Audio file not found: {p}")

    audio = MP3(str(p))
    duration = audio.info.length
    if duration <= 0:
        raise ValueError(f"Invalid duration {duration} for {p}")
    return duration


# ---------------------------------------------------------------------------
# Segment data builder
# ---------------------------------------------------------------------------

def build_segment_data(
    audio_files: list[str],
    image_results: list[dict],
    project_dir: str | Path,
) -> list[dict]:
    """
    Merge audio file paths and image paths into a unified per-segment list,
    sorted by segment_index.

    audio_files format  : ["projects/slug/0001.mp3", "projects/slug/0002.mp3", ...]
    image_results format: [{segment_index, image_path, status, prompt}, ...]

    Returns list of:
        {segment_index, audio_path: Path, image_path: Path}
    """
    project_dir = Path(project_dir)

    # Build image lookup: segment_index -> image_path
    image_lookup: dict[int, Path] = {}
    for r in image_results:
        if r.get("image_path"):
            image_lookup[r["segment_index"]] = Path(r["image_path"])

    # Build audio lookup from audio_files
    # Supports both list of str/Path and list of dicts {segment_index, file_path}
    if audio_files and isinstance(audio_files[0], dict):
        audio_sorted = sorted(audio_files, key=lambda d: d["segment_index"])
    else:
        audio_sorted = [
            {"segment_index": i, "file_path": p}
            for i, p in enumerate(sorted(audio_files, key=lambda p: Path(p).name), start=1)
        ]

    result = []
    for entry in audio_sorted:
        seg_idx = entry["segment_index"]
        audio_path = Path(entry["file_path"])
        image_path = image_lookup.get(seg_idx)
        if image_path is None:
            raise ValueError(
                f"No image found for segment {seg_idx}. "
                "Image generation must complete before video generation."
            )
        result.append({
            "segment_index": seg_idx,
            "audio_path": audio_path,
            "image_path": image_path,
        })

    result.sort(key=lambda s: s["segment_index"])
    return result


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def validate_inputs(segments_data: list[dict]) -> None:
    """
    Verify that every segment has existing audio and image files.
    Raises FileNotFoundError or ValueError on first problem found.
    """
    for s in segments_data:
        idx = s["segment_index"]

        audio = s["audio_path"]
        if not Path(audio).exists():
            raise FileNotFoundError(f"Segment {idx}: audio not found at {audio}")

        image = s["image_path"]
        if not Path(image).exists():
            raise FileNotFoundError(f"Segment {idx}: image not found at {image}")

        duration = get_audio_duration(audio)
        if duration <= 0:
            raise ValueError(f"Segment {idx}: invalid audio duration {duration}")

    logger.info("[video] Input validation passed — %d segments", len(segments_data))

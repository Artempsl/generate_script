"""
agent/video/generator.py

Orchestrates final video creation from per-segment audio + image files.

Pipeline for each segment:
  ImageClip (1920×1080, duration = audio length)
    → apply_zoom   (continuous ~4 % scale-up over duration)
    → apply_flicker (subtle ±1.5 % brightness variation)
    → apply_fades  (0.5 s fade-in / fade-out)
    → set_audio(AudioFileClip)

All clips are then concatenated into one MP4 at 24 fps:
  output/ final_video.mp4

Public API:
  generate_video(project_dir, audio_files, image_results, audio_base_url)
      → (video_path: str, video_url: str)
"""

import logging
import os
from pathlib import Path

# MoviePy 1.0.3 uses PIL.Image.ANTIALIAS, removed in Pillow 10+
import PIL.Image
if not hasattr(PIL.Image, "ANTIALIAS"):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS  # type: ignore[attr-defined]

from moviepy.editor import (
    AudioFileClip,
    ImageClip,
    concatenate_videoclips,
)

from agent.video.effects import apply_fades, apply_flicker, apply_zoom
from agent.video.utils import build_segment_data, get_audio_duration, validate_inputs

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OUTPUT_FPS    = 24
VIDEO_CODEC   = "libx264"
AUDIO_CODEC   = "aac"
FFMPEG_PRESET = "fast"       # fast encode; use "medium" for smaller file size
VIDEO_BITRATE = "5000k"
OUTPUT_SUBDIR = "output"
OUTPUT_FILENAME = "final_video.mp4"

TARGET_W = 1920
TARGET_H = 1080


# ---------------------------------------------------------------------------
# Single segment clip
# ---------------------------------------------------------------------------

def create_segment_clip(seg: dict) -> "VideoFileClip":
    """
    Build a fully-processed MoviePy video clip for one segment.

    Steps:
      1. Read audio duration from MP3
      2. Create ImageClip with that duration
      3. Apply zoom → flicker → fades
      4. Attach audio

    Args:
        seg: {segment_index, audio_path, image_path}

    Returns:
        A CompositeVideoClip / ImageClip with audio set, ready to concatenate.
    """
    idx        = seg["segment_index"]
    audio_path = seg["audio_path"]
    image_path = seg["image_path"]

    duration = get_audio_duration(audio_path)
    logger.info("[video] Seg %d: duration=%.2fs  image=%s", idx, duration, Path(image_path).name)

    # Base clip — static image displayed for `duration` seconds
    clip = ImageClip(str(image_path)).set_duration(duration)

    # Resize to target resolution if needed (Pollinations always gives 1920×1080,
    # but be safe for future sources)
    if clip.size != (TARGET_W, TARGET_H):
        clip = clip.resize((TARGET_W, TARGET_H))

    # Effects
    clip = apply_zoom(clip, duration)
    clip = apply_flicker(clip, segment_index=idx)
    clip = apply_fades(clip)

    # Attach audio
    audio = AudioFileClip(str(audio_path))
    clip  = clip.set_audio(audio)

    return clip


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def generate_video(
    project_dir: str | Path,
    audio_files: list[str],
    image_results: list[dict],
    audio_base_url: str = "",
) -> tuple[str, str]:
    """
    Generate the final MP4 from all segment audio and image files.

    Args:
        project_dir    : Root project directory path.
        audio_files    : List of local audio file paths (state["audio_files"]).
        image_results  : List of image result dicts (state["image_generation_results"]).
        audio_base_url : Public base URL e.g. "https://tunnel.example.com"
                         Used to build the public video_url.

    Returns:
        (video_path, video_url) — local path string and public URL string.

    Raises:
        FileNotFoundError / ValueError if any required file is missing.
    """
    project_dir = Path(project_dir)
    output_dir  = project_dir / OUTPUT_SUBDIR
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / OUTPUT_FILENAME

    # 1. Assemble and validate segment data
    segments_data = build_segment_data(audio_files, image_results, project_dir)
    validate_inputs(segments_data)

    logger.info("[video] Starting video generation — %d segments", len(segments_data))

    # 2. Build per-segment clips
    clips = []
    for seg in segments_data:
        try:
            clip = create_segment_clip(seg)
            clips.append(clip)
        except Exception as exc:
            logger.error("[video] Seg %d clip creation failed: %s", seg["segment_index"], exc)
            raise

    # 3. Concatenate
    logger.info("[video] Concatenating %d clips...", len(clips))
    final = concatenate_videoclips(clips, method="compose")

    # 4. Render to disk
    logger.info("[video] Rendering → %s", output_path)
    final.write_videofile(
        str(output_path),
        fps=OUTPUT_FPS,
        codec=VIDEO_CODEC,
        audio_codec=AUDIO_CODEC,
        preset=FFMPEG_PRESET,
        bitrate=VIDEO_BITRATE,
        threads=4,
        logger=None,   # suppress moviepy's own progress bar in server logs
    )

    # 5. Clean up clip objects
    for clip in clips:
        try:
            clip.close()
        except Exception:
            pass
    try:
        final.close()
    except Exception:
        pass

    # 6. Build public URL
    project_slug = project_dir.name
    video_url = (
        f"{audio_base_url}/projects/{project_slug}/{OUTPUT_SUBDIR}/{OUTPUT_FILENAME}"
        if audio_base_url
        else ""
    )

    logger.info("[video] Done — %s (%.1f MB)", output_path.name,
                output_path.stat().st_size / 1_048_576)

    return str(output_path), video_url

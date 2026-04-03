"""
agent/video/effects.py

Cinematic effects applied to each ImageClip segment:

  apply_zoom    — continuous slow zoom over full duration (1.00 → 1.04)
  apply_flicker — subtle sinusoidal brightness variation (~±1.5 %)
  apply_fades   — fade-in and fade-out (0.5 s each)

All effects are pure functions: they receive a clip and return a new clip.
Parameters are module-level constants so they can be adjusted in one place.
"""

import logging

import numpy as np
from moviepy.editor import VideoClip

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ZOOM_FACTOR   = 0.10   # total scale increase over segment duration (10 %)
FADE_SECONDS  = 0.5    # duration of fade-in and fade-out

FLICKER_FREQ      = 0.7    # Hz — slow sine cycle
FLICKER_INTENSITY = 0.04   # ±4 % brightness variation
FLICKER_NOISE     = 0.02   # ±2 % random per-frame noise


# ---------------------------------------------------------------------------
# Zoom
# ---------------------------------------------------------------------------

def apply_zoom(clip: VideoClip, duration: float) -> VideoClip:
    """
    Apply a continuous, very subtle Ken-Burns-style zoom that spans the full
    segment duration.

    Strategy:
      1. clip.resize(scale_func) — scale per frame via a linear function t→scale
      2. clip.crop(center, original_size) — always crop back to 1920×1080 from
         the centre so the output resolution stays constant.

    At t=0   → scale = 1.000  (no zoom yet)
    At t=end → scale = 1.040  (4 % larger)
    """
    W, H = clip.size

    def scale_func(t: float) -> float:
        return 1.0 + ZOOM_FACTOR * (t / duration)

    zoomed = clip.resize(scale_func)

    # Crop back to original dimensions from centre
    cropped = zoomed.crop(
        x_center=W / 2,
        y_center=H / 2,
        width=W,
        height=H,
    )
    return cropped


# ---------------------------------------------------------------------------
# Flicker
# ---------------------------------------------------------------------------

def apply_flicker(clip: VideoClip, segment_index: int = 0) -> VideoClip:
    """
    Apply a very subtle cinematic light-flicker effect.

    Implementation:
      - Per-frame brightness multiplier = 1 + sine_component + noise_component
      - sine_component : slow oscillation at FLICKER_FREQ Hz, amplitude ±FLICKER_INTENSITY
      - noise_component: uniform random per frame, amplitude ±FLICKER_NOISE/2
      - Seeded with segment_index for full reproducibility

    The result is invisible as a deliberate effect but gives the image
    a sense of subtle life.
    """
    rng = np.random.default_rng(seed=segment_index * 7 + 42)

    def flicker_frame(get_frame, t: float):
        frame = get_frame(t).astype(np.float32)
        sine_mod   = FLICKER_INTENSITY * np.sin(2.0 * np.pi * FLICKER_FREQ * t)
        noise_mod  = rng.uniform(-FLICKER_NOISE / 2, FLICKER_NOISE / 2)
        brightness = 1.0 + sine_mod + noise_mod
        return np.clip(frame * brightness, 0, 255).astype(np.uint8)

    return clip.fl(flicker_frame, apply_to="video")


# ---------------------------------------------------------------------------
# Fades
# ---------------------------------------------------------------------------

def apply_fades(clip: VideoClip) -> VideoClip:
    """
    Apply fade-in at the start and fade-out at the end of a clip.
    FADE_SECONDS is capped at half the clip duration to avoid overlap.
    """
    fade = min(FADE_SECONDS, clip.duration / 2)
    return clip.fadein(fade).fadeout(fade)

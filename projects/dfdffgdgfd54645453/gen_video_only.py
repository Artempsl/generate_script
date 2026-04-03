"""
Video-only generation for project dfdffgdgfd54645453.
Skips image generation — uses already-generated images.
Run: .venv\Scripts\python.exe projects\dfdffgdgfd54645453\gen_video_only.py
"""
import os, sys, re

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.abspath(ROOT))

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
IMAGES_DIR = os.path.join(PROJECT_DIR, "images")

# ── 1. Read segments to build audio_files list ────────────────────────────────
segmented_path = os.path.join(PROJECT_DIR, "script_segmented.txt")
with open(segmented_path, encoding="utf-8") as f:
    raw = f.read()

segments = []
for m in re.finditer(
    r'\[Segment (\d+)\]\n-+\n(.*?)(?=\n\nAudio URL:|\n\n\[Segment|\n+={10}|$)',
    raw, re.DOTALL
):
    seg_no = int(m.group(1))
    text = m.group(2).strip()
    if text:
        segments.append({"segment_index": seg_no, "text": text})

print(f"[gen_video] {len(segments)} segments")

audio_files = []
for seg in segments:
    fname = f"{seg['segment_index']:04d}.mp3"
    fpath = os.path.join(PROJECT_DIR, fname)
    if not os.path.exists(fpath):
        print(f"[gen_video] WARNING: missing audio {fpath}")
    audio_files.append({"segment_index": seg["segment_index"], "file_path": fpath})

# ── 2. Build image_results from existing PNG files ────────────────────────────
image_results = []
for seg in segments:
    idx = seg["segment_index"]
    img_path = os.path.join(IMAGES_DIR, f"segment_{idx}.png")
    if not os.path.exists(img_path):
        print(f"[gen_video] ERROR: missing image {img_path}")
        sys.exit(1)
    image_results.append({"segment_index": idx, "status": "ok", "image_path": img_path})

print(f"[gen_video] All {len(image_results)} images found")

# ── 3. Generate video ─────────────────────────────────────────────────────────
from agent.video.generator import generate_video

print("[gen_video] Starting video generation ...")
video_path, video_url = generate_video(
    project_dir=PROJECT_DIR,
    audio_files=audio_files,
    image_results=image_results,
    audio_base_url="",
)

size_mb = os.path.getsize(video_path) / 1024 / 1024
print(f"[gen_video] Done → {video_path}")
print(f"[gen_video] Size: {size_mb:.1f} MB")

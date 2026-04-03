"""
Full image + video pipeline test for SpaceAdventure2.
Run from workspace root:
  .venv\\Scripts\\python.exe projects\\SpaceAdventure2\\test_video.py
"""
import os, sys, re

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.abspath(ROOT))

PROJECT_DIR = os.path.dirname(__file__)

# ── 1. Read segments ──────────────────────────────────────────────────────────
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

print(f"[test] {len(segments)} segments loaded")

# ── 2. Build audio_files list ─────────────────────────────────────────────────
audio_files = []
for seg in segments:
    fname = f"{seg['segment_index']:04d}.mp3"
    fpath = os.path.join(PROJECT_DIR, fname)
    if not os.path.exists(fpath):
        print(f"[test] WARNING: missing audio file {fpath}")
    audio_files.append({"segment_index": seg["segment_index"], "file_path": fpath})

# ── 3. Generate images ────────────────────────────────────────────────────────
from agent.image.generator import generate_all_images

print("[test] Starting image generation ...")
image_results = generate_all_images(segments, PROJECT_DIR)
ok = sum(1 for r in image_results if r.get("status") == "ok")
print(f"[test] Image generation done: {ok}/{len(segments)} ok")
for r in image_results:
    print(f"  seg {r['segment_index']:>2}: {r['status']}  -> {r.get('image_path', '')}")

# ── 4. Generate video ─────────────────────────────────────────────────────────
from agent.video.generator import generate_video

print("[test] Starting video generation ...")
video_path, video_url = generate_video(
    project_dir=PROJECT_DIR,
    audio_files=audio_files,
    image_results=image_results,
    audio_base_url="",
)
print(f"[test] Video written to: {video_path}")
size_mb = os.path.getsize(video_path) / 1024 / 1024
print(f"[test] File size: {size_mb:.1f} MB")
print("[test] DONE")

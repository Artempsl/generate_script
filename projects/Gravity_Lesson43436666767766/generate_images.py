"""
generate_images.py — Standalone image generation test utility.

Reads the segmented script, generates a cinematic first-person prompt for each
segment, then requests an image from the Pollinations.ai free API (no key needed).

Usage:
    python generate_images.py

Output:
    images/segment_1.png ... segment_N.png
    image_prompts.json
"""

import json
import logging
import os
import re
import time
import urllib.parse
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_FILE = Path(__file__).parent / "script_segmented.txt"
IMAGES_DIR = Path(__file__).parent / "images"
PROMPTS_JSON = Path(__file__).parent / "image_prompts.json"

# Pollinations.ai authenticated API
# GET https://gen.pollinations.ai/image/{encoded_prompt}?width=W&height=H&model=flux
# API key from env var POLLINATION_API
POLLINATIONS_BASE = "https://gen.pollinations.ai"
POLLINATION_API_KEY = os.environ.get("pollination_api", "")

IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 576        # 16:9 cinematic ratio
IMAGE_MODEL = "flux"      # flux schnell — cheapest per-image

MAX_RETRIES = 3
RETRY_DELAY = 5           # seconds between retries
SEGMENT_DELAY = 3         # seconds between segment requests
RATE_LIMIT_WAIT = 30      # seconds to wait on 429

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# STEP 1 — Load segments
# ---------------------------------------------------------------------------

def load_segments(path: Path) -> list[dict]:
    """
    Parse the segmented script file produced by the backend pipeline.

    Returns a list of dicts:
        [{"index": 1, "text": "..."}, ...]
    """
    content = path.read_text(encoding="utf-8")

    # Match blocks:  [Segment N]\n---...\n<text>\n\nAudio URL:
    pattern = re.compile(
        r"\[Segment (\d+)\]\s*\n-+\n(.*?)\n\nAudio URL:",
        re.DOTALL,
    )
    segments = []
    for match in pattern.finditer(content):
        idx = int(match.group(1))
        text = match.group(2).strip()
        if text:
            segments.append({"index": idx, "text": text})

    segments.sort(key=lambda s: s["index"])
    logger.info(f"Loaded {len(segments)} segment(s) from {path.name}")
    return segments


# ---------------------------------------------------------------------------
# STEP 2 — Generate visual prompt
# ---------------------------------------------------------------------------

def generate_prompt(segment: dict) -> str:
    """
    Build a concise cinematic first-person visual prompt from the segment text.
    Kept short to stay within URL length limits of the Pollinations API.
    """
    text = segment["text"]
    idx  = segment["index"]

    scene = _derive_scene(text)

    # Keep total prompt under ~200 chars to avoid 500 from URL length
    prompt = (
        f"POV cinematic photo, {scene}, "
        f"no people, atmospheric lighting, photorealistic, 8k"
    )

    logger.info(f"[Seg {idx}] Prompt ({len(prompt)} chars): {prompt[:100]}...")
    return prompt


def _derive_scene(text: str) -> str:
    """
    Map segment text to a short concrete scene (kept brief for URL length).
    """
    t = text.lower()

    if any(w in t for w in ["orchard", "apple tree", "tree"]):
        return "English countryside orchard at golden hour, apple tree, warm sunlight"
    if any(w in t for w in ["magic show", "magician", "magic"]):
        return "Victorian theatre stage, red curtains, dramatic spotlight, smoky air"
    if any(w in t for w in ["formula", "equation", "f = g", "mouthful", "r²", "m1", "m2"]):
        return "old wooden desk with handwritten equations on parchment, candlelight"
    if any(w in t for w in ["fall", "falling", "dropped", "drop", "9.8", "m/s"]):
        return "looking up through apple tree canopy, red apple falling toward camera"
    if any(w in t for w in ["recap", "next time", "munch", "bite"]):
        return "close-up red apple on rough wood, dramatic side lighting, deep shadows"
    if any(w in t for w in ["1666", "newton", "pondered"]):
        return "17th-century stone study, moonlit window, candle, open books"
    if any(w in t for w in ["gravity", "force", "pull", "earth"]):
        return "open field, star-filled night sky, Milky Way overhead, long grass"
    if any(w in t for w in ["clue", "secret", "mystery"]):
        return "misty orchard, single sunbeam on a red apple, soft focus shadows"
    return "old science classroom, antique windows, afternoon light, physics instruments"


# ---------------------------------------------------------------------------
# STEP 3 — Generate image via Pollinations.ai
# ---------------------------------------------------------------------------

def generate_image(prompt: str, segment_idx: int) -> bytes | None:
    """
    Request an image from gen.pollinations.ai and return raw JPEG/PNG bytes.
    Authenticates with Bearer token from POLLINATION_API env var.
    Handles 429 rate-limit by waiting RATE_LIMIT_WAIT seconds before retry.
    Returns None after MAX_RETRIES failures.
    """
    if not POLLINATION_API_KEY:
        raise RuntimeError(
            "Environment variable 'pollination_api' is not set. "
            "Set it to your Pollinations API key."
        )

    encoded = urllib.parse.quote(prompt, safe="")
    url = (
        f"{POLLINATIONS_BASE}/image/{encoded}"
        f"?width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}"
        f"&model={IMAGE_MODEL}&seed={segment_idx * 13}"
    )
    headers = {"Authorization": f"Bearer {POLLINATION_API_KEY}"}

    for attempt in range(1, MAX_RETRIES + 2):
        try:
            logger.info(f"[Seg {segment_idx}] Request attempt {attempt}/{MAX_RETRIES + 1}")
            resp = requests.get(url, headers=headers, timeout=120)

            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", RATE_LIMIT_WAIT))
                logger.warning(
                    f"[Seg {segment_idx}] 429 rate limit — waiting {retry_after}s..."
                )
                time.sleep(retry_after)
                continue  # don't count as a retry

            resp.raise_for_status()

            content_type = resp.headers.get("content-type", "")
            if "image" not in content_type:
                raise ValueError(f"Not an image response: {content_type}")

            logger.info(
                f"[Seg {segment_idx}] ✓ Image received "
                f"({len(resp.content) // 1024} KB)"
            )
            return resp.content

        except requests.exceptions.HTTPError as exc:
            logger.error(f"[Seg {segment_idx}] Attempt {attempt} HTTP error: {exc}")
            if attempt <= MAX_RETRIES:
                logger.info(f"[Seg {segment_idx}] Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
        except Exception as exc:
            logger.error(f"[Seg {segment_idx}] Attempt {attempt} failed: {exc}")
            if attempt <= MAX_RETRIES:
                logger.info(f"[Seg {segment_idx}] Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)

    logger.error(f"[Seg {segment_idx}] All attempts exhausted — skipping.")
    return None


# ---------------------------------------------------------------------------
# STEP 4 — Save image
# ---------------------------------------------------------------------------

def save_image(image_bytes: bytes, segment_idx: int) -> Path:
    """Write PNG bytes to images/segment_N.png and return the path."""
    IMAGES_DIR.mkdir(exist_ok=True)
    out_path = IMAGES_DIR / f"segment_{segment_idx}.png"
    out_path.write_bytes(image_bytes)
    logger.info(f"[Seg {segment_idx}] Saved → {out_path.relative_to(Path(__file__).parent)}")
    return out_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    logger.info("=" * 60)
    logger.info("IMAGE GENERATION — START")
    logger.info("=" * 60)

    # 1. Load segments
    segments = load_segments(SCRIPT_FILE)
    if not segments:
        logger.error("No segments found. Exiting.")
        return

    IMAGES_DIR.mkdir(exist_ok=True)

    prompts_data = []
    results = {"generated": [], "failed": []}

    # 2. Process each segment
    for seg in segments:
        idx = seg["index"]
        logger.info(f"\n{'─' * 50}")
        logger.info(f"Processing Segment {idx}/{len(segments)}")
        logger.info(f"Text: {seg['text'][:80]}...")

        # Generate prompt
        prompt = generate_prompt(seg)

        # Generate image
        image_bytes = generate_image(prompt, idx)

        # Save
        if image_bytes:
            save_image(image_bytes, idx)
            results["generated"].append(idx)
            status = "ok"
        else:
            results["failed"].append(idx)
            status = "failed"

        prompts_data.append({
            "segment": idx,
            "text_preview": seg["text"][:120],
            "prompt": prompt,
            "status": status,
            "image_path": f"images/segment_{idx}.png" if status == "ok" else None,
        })

        # Delay between requests to respect rate-limit
        if idx < len(segments):
            logger.info(f"Waiting {SEGMENT_DELAY}s before next segment...")
            time.sleep(SEGMENT_DELAY)

    # 3. Save prompts JSON
    PROMPTS_JSON.write_text(
        json.dumps(prompts_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info(f"\nPrompts saved → {PROMPTS_JSON.name}")

    # 4. Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info(f"  Generated : {len(results['generated'])} image(s) — {results['generated']}")
    if results["failed"]:
        logger.warning(f"  Failed    : {len(results['failed'])} segment(s) — {results['failed']}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

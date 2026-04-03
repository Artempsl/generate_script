"""
agent/image/generator_v2.py

Image Generation Pipeline V2 — Entity-Consistent image-to-image.

How it works:
  1. For every entity in entities.json, generate a reference portrait on a
     white background using Pollinations `flux` model and cache the result.
  2. Generate text prompts for all segments (reuses v1 pipeline).
  3. For each segment that contains entities, build a PIL composite image
     (all entity reference portraits side-by-side on white background),
     upload it to 0x0.st (public temp hosting), and store the URL.
  4. Generate the final segment image using Pollinations `seedream-pro`
      in image-to-image mode: the prompt from step 2 + the
     composite URL as the reference image.
  5. Segments with no entities fall back to z-image-turbo (text-to-image).

All outputs go to {project_dir}/images_v2/
v1 pipeline (agent/image/generator.py) is completely untouched.
"""

import json
import logging
import os
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://gen.pollinations.ai"
# Resolution for final segment images
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080

# Resolution for entity reference images
ENTITY_PORTRAIT_WIDTH = 768
ENTITY_PORTRAIT_HEIGHT = 1024
ENTITY_OBJECT_SIZE = 512

# Model for entity reference images (text-to-image on white background)
ENTITY_REF_MODEL = "seedream-pro"
# Model for segment images (image-to-image)
I2I_MODEL = "seedream-pro"
# Fallback when no entities in segment
FALLBACK_TEXT_MODEL = "z-image-turbo"

RETRY_DELAY = 5          # seconds between retries
SEGMENT_DELAY = 2        # seconds between segments
RATE_LIMIT_WAIT = 30     # seconds on 429
BALANCE_WAIT = 60        # seconds on 402
SEGMENT_MAX_WORKERS = 2  # bounded parallelism to avoid Pollinations bursts

UPLOAD_HOSTS = [
    "https://0x0.st",
    "https://catbox.moe/user/api.php",
    "https://litterbox.catbox.moe/resources/internals/api.php",
]
UPLOAD_TIMEOUT = 30      # seconds


class InsufficientBalanceError(Exception):
    pass


# ---------------------------------------------------------------------------
# Entity reference image prompts
# ---------------------------------------------------------------------------

def build_entity_reference_prompt(entity: dict) -> str:
    """
    Build a white-background reference prompt for an entity.
    Characters/animals → full body portrait.
    Objects → isolated full-size object shot.
    """
    base = entity.get("base_prompt", entity.get("name", "unknown object"))
    entity_type = entity.get("_type", "object")

    if entity_type in ("character", "animal"):
        return (
            f"{base}, "
            "full body from head to toe, entire figure fully visible, no cropped limbs, pure white background, centered in frame, "
            "flat white studio backdrop, soft even lighting, no shadows on background, "
            "no environment, no props, completely isolated figure, "
            "photorealistic, highly detailed, 8k"
        )
    else:
        return (
            f"{base}, "
            "displayed at full size on pure white background, entire object fully visible, nothing cropped, centered in frame, "
            "flat white studio backdrop, even soft lighting, no cast shadow, "
            "completely isolated, no environment, "
            "photorealistic, highly detailed, 8k"
        )


# ---------------------------------------------------------------------------
# Post-process: force white background on saved PNG
# ---------------------------------------------------------------------------

def _force_white_background(png_path: Path) -> None:
    """
    Open the PNG, composite it onto a pure white RGB canvas, and save back.
    Handles RGBA (uses alpha as mask) and RGB images alike.
    Guarantees a #FFFFFF background regardless of model output.
    """
    try:
        from PIL import Image
        img = Image.open(png_path).convert("RGBA")
        canvas = Image.new("RGB", img.size, (255, 255, 255))
        canvas.paste(img, mask=img.split()[3])  # use alpha as mask
        canvas.save(png_path, format="PNG")
        logger.debug("[v2] Forced white background on %s", png_path.name)
    except Exception as exc:
        logger.warning("[v2] Could not force white background on %s: %s", png_path.name, exc)


# ---------------------------------------------------------------------------
# Load entities with type metadata
# ---------------------------------------------------------------------------

def load_entities_typed(project_dir: Path) -> list[dict]:
    """
    Load entities from entities.json and attach _type + _id fields.
    Returns a flat list: characters first, then animals, then objects.
    """
    path = project_dir / "entities.json"
    if not path.exists():
        logger.warning("[v2] entities.json not found at %s", path)
        return []

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("[v2] Failed to load entities.json: %s", exc)
        return []

    result = []
    for char in raw.get("characters", []):
        versions = char.get("versions", [])
        bp = versions[0].get("base_prompt", "") if versions else ""
        if char.get("name") and bp:
            result.append({
                "name": char["name"],
                "base_prompt": bp,
                "_id": char.get("id", f"char_{len(result)}"),
                "_type": "character",
            })

    for animal in raw.get("animals", []):
        versions = animal.get("versions", [])
        bp = versions[0].get("base_prompt", "") if versions else ""
        if animal.get("name") and bp:
            result.append({
                "name": animal["name"],
                "base_prompt": bp,
                "_id": animal.get("id", f"animal_{len(result)}"),
                "_type": "animal",
            })

    for obj in raw.get("objects", []):
        if obj.get("name") and obj.get("base_prompt"):
            result.append({
                "name": obj["name"],
                "base_prompt": obj["base_prompt"],
                "_id": obj.get("id", f"obj_{len(result)}"),
                "_type": "object",
            })

    logger.info("[v2] Loaded %d typed entities", len(result))
    return result


# ---------------------------------------------------------------------------
# Single HTTP image request
# ---------------------------------------------------------------------------

def _get_image(
    prompt: str,
    model: str,
    seed: int,
    api_key: str,
    width: int,
    height: int,
    image_url: str | None = None,
    retries: int = 5,
    retry_forever: bool = False,
) -> bytes | None:
    """
    Call Pollinations image API.
    If image_url is set, passes it as the `image` query param (i2i mode).
    retry_forever=True keeps retrying until success for i2i segments.
    """
    encoded = urllib.parse.quote(prompt, safe="")
    params = f"?width={width}&height={height}&model={model}&seed={seed}&nologo=true"
    if image_url:
        # safe=':/%' — keep : and / for the scheme/host, keep % to avoid double-encoding
        # ?, &, = MUST be encoded so the reference URL's query params don't bleed into outer URL
        params += f"&image={urllib.parse.quote(image_url, safe=':/%')}"
    url = f"{BASE_URL}/image/{encoded}{params}"
    headers = {"Authorization": f"Bearer {api_key}"}

    attempt = 0
    while True:
        attempt += 1
        try:
            logger.debug("[v2] %s attempt %d url=%s", model, attempt, url[:120])
            resp = requests.get(url, headers=headers, timeout=180)

            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", RATE_LIMIT_WAIT))
                logger.warning("[v2] 429 rate-limit — waiting %ds", wait)
                time.sleep(wait)
                continue  # don't count as retry

            if resp.status_code == 402:
                raise InsufficientBalanceError("Insufficient pollen balance")

            resp.raise_for_status()

            ctype = resp.headers.get("content-type", "")
            if "image" not in ctype:
                raise ValueError(f"Non-image content-type: {ctype}")

            logger.info(
                "[v2] ✓ model=%s seed=%d  %d KB",
                model, seed, len(resp.content) // 1024,
            )
            return resp.content

        except InsufficientBalanceError:
            raise

        except Exception as exc:
            logger.warning("[v2] model=%s attempt %d failed: %s", model, attempt, exc)
            if not retry_forever and attempt >= retries:
                return None
            backoff = min(RETRY_DELAY * (2 ** min(attempt - 1, 4)), 120)
            logger.info("[v2] retrying in %ds…", backoff)
            time.sleep(backoff)


# ---------------------------------------------------------------------------
# Phase 1: Entity reference images
# ---------------------------------------------------------------------------

def generate_entity_reference_images(
    entities: list[dict],
    project_dir: Path,
    api_key: str,
) -> dict[str, str]:
    """
    For each entity, generate a reference portrait on a white background.
    Saves to images_v2/entities/{_id}.png and caches the Pollinations URL
    in images_v2/entities/{_id}.url.

    Returns dict: {entity_id -> pollinations_url}
    """
    entities_dir = project_dir / "images_v2" / "entities"
    entities_dir.mkdir(parents=True, exist_ok=True)

    id_to_url: dict[str, str] = {}

    for ent in entities:
        eid = ent["_id"]
        png_path = entities_dir / f"{eid}.png"
        url_path = entities_dir / f"{eid}.url"

        # Load cached URL if image already exists
        if png_path.exists() and url_path.exists():
            url = url_path.read_text(encoding="utf-8").strip()
            id_to_url[eid] = url
            logger.info("[v2] Entity %s cached → %s", eid, url[:60])
            continue

        # PNG exists but no URL — just upload and cache
        if png_path.exists() and not url_path.exists():
            print(f"  [v2] Re-uploading existing PNG for entity: {ent['name']} ({eid})")
            public_url = upload_to_temp_host(png_path)
            if public_url:
                url_path.write_text(public_url, encoding="utf-8")
                id_to_url[eid] = public_url
                logger.info("[v2] Entity %s re-uploaded → %s", eid, public_url)
            else:
                logger.error("[v2] Re-upload failed for entity %s", eid)
            continue

        prompt = build_entity_reference_prompt(ent)
        is_object = ent["_type"] == "object"
        w = ENTITY_OBJECT_SIZE if is_object else ENTITY_PORTRAIT_WIDTH
        h = ENTITY_OBJECT_SIZE if is_object else ENTITY_PORTRAIT_HEIGHT

        # Deterministic seed based on entity id hash
        seed = abs(hash(eid)) % 99991

        print(f"  [v2] Generating reference image for entity: {ent['name']} ({eid})")
        logger.info("[v2] Generating reference for %s  w=%d h=%d", ent["name"], w, h)

        try:
            data = _get_image(
                prompt=prompt,
                model=ENTITY_REF_MODEL,
                seed=seed,
                api_key=api_key,
                width=w,
                height=h,
                retries=5,
            )
        except InsufficientBalanceError:
            raise

        if not data:
            logger.error("[v2] Failed to generate reference for entity %s", eid)
            continue

        png_path.write_bytes(data)
        _force_white_background(png_path)

        # Upload to public temp host so klein can fetch without auth
        print(f"  [v2] Uploading reference image for {ent['name']} to temp host…")
        public_url = upload_to_temp_host(png_path)
        if not public_url:
            logger.error("[v2] Upload failed for entity %s — skipping", eid)
            continue
        url_path.write_text(public_url, encoding="utf-8")
        id_to_url[eid] = public_url

        logger.info("[v2] Entity %s saved → %s", eid, png_path.name)
        time.sleep(SEGMENT_DELAY)

    return id_to_url


# ---------------------------------------------------------------------------
# Phase 3a: PIL composite
# ---------------------------------------------------------------------------

def build_segment_composite(
    segment_entities: list[dict],
    entities_dir: Path,
    output_path: Path,
) -> Path | None:
    """
    Build a side-by-side composite image of all entities in a segment.
    Sorted: characters → animals → objects.
    All images resized to height=768 preserving aspect ratio, then
    concatenated horizontally with 20px gap on white background.

    Returns output_path on success, None if no entity PNGs are available.
    """
    try:
        from PIL import Image
    except ImportError:
        logger.error("[v2] Pillow not installed — cannot build composite")
        return None

    sort_order = {"character": 0, "animal": 1, "object": 2}
    sorted_ents = sorted(segment_entities, key=lambda e: sort_order.get(e.get("_type", "object"), 9))

    TARGET_H = 768
    GAP = 20
    images = []

    for ent in sorted_ents:
        eid = ent["_id"]
        png_path = entities_dir / f"{eid}.png"
        if not png_path.exists():
            logger.warning("[v2] Reference PNG missing for %s, skipping", eid)
            continue
        img = Image.open(png_path).convert("RGBA")
        scale = TARGET_H / img.height
        new_w = max(1, int(img.width * scale))
        img = img.resize((new_w, TARGET_H), Image.LANCZOS)
        images.append(img)

    if not images:
        return None

    if len(images) == 1:
        # No composite needed — reuse single entity PNG directly
        return entities_dir / f"{sorted_ents[0]['_id']}.png"

    total_w = sum(img.width for img in images) + GAP * (len(images) - 1)
    canvas = Image.new("RGBA", (total_w, TARGET_H), (255, 255, 255, 255))
    x = 0
    for img in images:
        canvas.paste(img, (x, 0))
        x += img.width + GAP

    # Convert to RGB (no alpha) before saving as PNG
    rgb = Image.new("RGB", canvas.size, (255, 255, 255))
    rgb.paste(canvas, mask=canvas.split()[3])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rgb.save(output_path, format="PNG")
    logger.info("[v2] Composite saved → %s (%dx%d)", output_path.name, total_w, TARGET_H)
    return output_path


# ---------------------------------------------------------------------------
# Phase 3b: upload composite to public temp host
# ---------------------------------------------------------------------------

def _upload_to_host(image_path: Path, host: str) -> str | None:
    """Try uploading to a single host. Returns URL or None."""
    try:
        with open(image_path, "rb") as f:
            if "catbox.moe" in host or "litterbox" in host:
                data = {"reqtype": "fileupload"}
                if "litterbox" in host:
                    data["time"] = "72h"
                resp = requests.post(
                    host,
                    data=data,
                    files={"fileToUpload": (image_path.name, f, "image/png")},
                    timeout=UPLOAD_TIMEOUT,
                )
            else:
                resp = requests.post(
                    host,
                    files={"file": (image_path.name, f, "image/png")},
                    timeout=UPLOAD_TIMEOUT,
                )
        resp.raise_for_status()
        url = resp.text.strip()
        if url.startswith("http"):
            logger.info("[v2] Uploaded → %s (via %s)", url, host)
            return url
        logger.warning("[v2] Unexpected upload response from %s: %s", host, url[:100])
    except Exception as exc:
        logger.warning("[v2] Upload to %s failed: %s", host, exc)
    return None


def upload_to_temp_host(image_path: Path) -> str | None:
    """
    Upload an image file to a public temp host and return the URL.
    Tries UPLOAD_HOSTS in order, returns first success.
    """
    for host in UPLOAD_HOSTS:
        url = _upload_to_host(image_path, host)
        if url:
            return url
        time.sleep(2)
    logger.error("[v2] All upload hosts failed for %s", image_path.name)
    return None


def ensure_reference_url(reference_path: Path, segment_idx: int | None = None) -> str | None:
    """
    Resolve a stable public URL for a local reference PNG.
    Validates the cached .url sidecar and re-uploads only when needed.
    Runs sequentially before parallel segment generation to avoid duplicate uploads.
    """
    url_cache = reference_path.with_suffix(".url")
    ref_url: str | None = None

    if url_cache.exists():
        candidate = url_cache.read_text(encoding="utf-8").strip()
        try:
            head = requests.head(candidate, timeout=10, allow_redirects=True)
            if head.status_code == 200:
                ref_url = candidate
                if segment_idx is not None:
                    logger.info("[v2] Seg %d ref URL still valid: %s", segment_idx, ref_url[:60])
                else:
                    logger.info("[v2] Ref URL still valid: %s", ref_url[:60])
            else:
                if segment_idx is not None:
                    logger.warning("[v2] Seg %d cached URL expired (%d), re-uploading", segment_idx, head.status_code)
                else:
                    logger.warning("[v2] Cached URL expired (%d), re-uploading", head.status_code)
                url_cache.unlink(missing_ok=True)
        except Exception as exc:
            if segment_idx is not None:
                logger.warning("[v2] Seg %d cached URL check failed (%s), re-uploading", segment_idx, exc)
            else:
                logger.warning("[v2] Cached URL check failed (%s), re-uploading", exc)
            url_cache.unlink(missing_ok=True)

    if ref_url:
        return ref_url

    if segment_idx is not None:
        print(f"  [v2] Seg {segment_idx}: uploading reference {reference_path.name}…")
    else:
        print(f"  [v2] Uploading reference {reference_path.name}…")

    ref_url = upload_to_temp_host(reference_path)
    if ref_url:
        url_cache.write_text(ref_url, encoding="utf-8")
    return ref_url


# ---------------------------------------------------------------------------
# i2i via POST /v1/images/edits (binary multipart — required for p-image-edit)
# ---------------------------------------------------------------------------

def _edit_image_post(
    prompt: str,
    model: str,
    reference_path: Path,
    api_key: str,
    width: int,
    height: int,
    retry_forever: bool = False,
    retries: int = 5,
) -> bytes | None:
    """
    POST to /v1/images/edits with binary reference image read from local disk.
    Returns raw image bytes on success.
    """
    headers = {"Authorization": f"Bearer {api_key}"}
    endpoint = f"{BASE_URL}/v1/images/edits"

    try:
        ref_bytes = reference_path.read_bytes()
    except Exception as exc:
        logger.error("[v2] Failed to read reference image %s: %s", reference_path, exc)
        return None

    attempt = 0
    while True:
        attempt += 1
        try:
            logger.debug("[v2] %s edit attempt %d", model, attempt)
            resp = requests.post(
                endpoint,
                headers=headers,
                data={
                    "model": model,
                    "prompt": prompt,
                    "n": "1",
                    "size": f"{width}x{height}",
                },
                files={"image": ("reference.png", ref_bytes, "image/png")},
                timeout=180,
            )

            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", RATE_LIMIT_WAIT))
                logger.warning("[v2] 429 rate-limit — waiting %ds", wait)
                time.sleep(wait)
                continue

            if resp.status_code == 402:
                raise InsufficientBalanceError("Insufficient pollen balance")

            resp.raise_for_status()

            # Response is JSON with data[0].url or data[0].b64_json
            body = resp.json()
            item = body["data"][0]

            if "b64_json" in item:
                import base64
                img_bytes = base64.b64decode(item["b64_json"])
            elif "url" in item:
                img_resp = requests.get(item["url"], timeout=60)
                img_resp.raise_for_status()
                img_bytes = img_resp.content
            else:
                raise ValueError(f"Unexpected response keys: {list(item.keys())}")

            logger.info("[v2] ✓ edit model=%s  %d KB", model, len(img_bytes) // 1024)
            return img_bytes

        except InsufficientBalanceError:
            raise

        except Exception as exc:
            logger.warning("[v2] edit model=%s attempt %d failed: %s", model, attempt, exc)
            if not retry_forever and attempt >= retries:
                return None
            backoff = min(RETRY_DELAY * (2 ** min(attempt - 1, 4)), 120)
            logger.info("[v2] retrying in %ds…", backoff)
            time.sleep(backoff)


# ---------------------------------------------------------------------------
# Phase 4: segment image generation
# ---------------------------------------------------------------------------

def generate_image_for_segment_v2(
    prompt: str,
    segment_idx: int,
    reference_path: Path | None,
    images_dir: Path,
    api_key: str,
    reference_url: str | None = None,
) -> Path | None:
    """
    Generate a single segment image.
    - reference_path set → I2I_MODEL via POST /v1/images/edits (retries indefinitely)
    - reference_path None → z-image-turbo text-to-image (5 retries)
    """
    images_dir.mkdir(parents=True, exist_ok=True)
    out_path = images_dir / f"segment_{segment_idx}.png"
    seed = segment_idx * 17

    # Skip if already generated
    if out_path.exists():
        print(f"  [v2] Seg {segment_idx}: cached → {out_path.name}")
        logger.info("[v2] Seg %d cached", segment_idx)
        return out_path

    if reference_path:
        ref_url = reference_url or ensure_reference_url(reference_path, segment_idx=segment_idx)
        if ref_url:
            print(f"  [v2] Seg {segment_idx}: {I2I_MODEL} i2i (ref={reference_path.name})…")
            logger.info("[v2] Seg %d i2i via %s", segment_idx, I2I_MODEL)
            data = _get_image(
                prompt=prompt,
                model=I2I_MODEL,
                seed=seed,
                api_key=api_key,
                width=IMAGE_WIDTH,
                height=IMAGE_HEIGHT,
                image_url=ref_url,
                retry_forever=True,
            )
        else:
            print(f"  [v2] Seg {segment_idx}: upload failed, fallback to {FALLBACK_TEXT_MODEL}")
            logger.warning("[v2] Seg %d upload failed, falling back to text-to-image", segment_idx)
            data = _get_image(
                prompt=prompt,
                model=FALLBACK_TEXT_MODEL,
                seed=seed,
                api_key=api_key,
                width=IMAGE_WIDTH,
                height=IMAGE_HEIGHT,
                retries=5,
            )
    else:
        print(f"  [v2] Seg {segment_idx}: {FALLBACK_TEXT_MODEL} text-to-image (no entities)")
        logger.info("[v2] Seg %d fallback text-to-image", segment_idx)
        data = _get_image(
            prompt=prompt,
            model=FALLBACK_TEXT_MODEL,
            seed=seed,
            api_key=api_key,
            width=IMAGE_WIDTH,
            height=IMAGE_HEIGHT,
            retries=5,
        )

    if data:
        out_path.write_bytes(data)
        logger.info("[v2] Seg %d saved → %s", segment_idx, out_path.name)
        return out_path

    logger.error("[v2] Seg %d failed", segment_idx)
    return None


# ---------------------------------------------------------------------------
# Public: full v2 pipeline
# ---------------------------------------------------------------------------

def generate_all_images_v2(
    segments: list[dict],
    project_dir: str | Path,
) -> list[dict]:
    """
    Full v2 pipeline:
      Phase 1 — Text prompts + entity-per-segment analysis (LLM)
      Phase 2 — Entity reference images (only entities that appear in segments)
      Phase 3 — PIL composites + 0x0.st upload per segment
    Phase 4 — seedream-pro i2i segment images

    All outputs in {project_dir}/images_v2/.
    Returns list of result dicts with status 'ok' or 'failed'.
    """
    api_key = os.environ.get("pollination_api", "")
    if not api_key:
        raise RuntimeError("Environment variable 'pollination_api' is not set.")

    project_dir = Path(project_dir)
    images_v2_dir = project_dir / "images_v2"
    images_v2_dir.mkdir(parents=True, exist_ok=True)

    # ── Load typed entities ─────────────────────────────────────────────────
    entities_typed = load_entities_typed(project_dir)

    # For v1 functions that expect flat {name, base_prompt} dicts
    entities_flat = [{"name": e["name"], "base_prompt": e["base_prompt"]} for e in entities_typed]

    # Build name→typed lookup
    name_to_typed: dict[str, dict] = {e["name"]: e for e in entities_typed}

    # ── Phase 1: Text prompts + segment-entity analysis ────────────────────
    print("\n[v2] Phase 1 — Generating text prompts and analysing entities per segment")
    from agent.image.generator import (
        extract_story_context,
        analyze_segment_entities,
        build_prompts_for_segments,
    )

    global_context = ""
    script_path = project_dir / "script.txt"
    script_text = ""
    if script_path.exists():
        script_text = script_path.read_text(encoding="utf-8")
        # Reuse v1 story_context cache
        context_cache = project_dir / "images" / "story_context.txt"
        global_context = extract_story_context(script_text, cache_path=context_cache)

    # Reuse v1 segment_entities cache
    seg_entities_cache = project_dir / "images" / "segment_entities_cache.json"
    segment_entity_map = {}
    if entities_flat and script_text:
        segment_entity_map = analyze_segment_entities(
            segments, entities_flat, script_text, cache_path=seg_entities_cache
        )

    prompts: dict[int, str] = build_prompts_for_segments(
        segments, entities_flat, global_context, script_text=script_text
    )

    # Save prompts
    prompts_file = images_v2_dir / "image_prompts.json"
    with open(prompts_file, "w", encoding="utf-8") as f:
        json.dump(
            [{"segment_index": idx, "prompt": p} for idx, p in sorted(prompts.items())],
            f, ensure_ascii=False, indent=2,
        )
    print(f"  Prompts saved → {prompts_file}")

    # Determine which entity IDs actually appear in at least one segment
    needed_entity_ids: set[str] = set()
    for seg_ents in segment_entity_map.values():
        for ent in seg_ents:
            typed = name_to_typed.get(ent["name"])
            if typed:
                needed_entity_ids.add(typed["_id"])
    needed_entities = [e for e in entities_typed if e["_id"] in needed_entity_ids]
    print(f"  Entities needed for composites: {[e['name'] for e in needed_entities]}")

    # ── Phase 2: Entity reference images (only needed entities) ────────────
    print(f"\n[v2] Phase 2 — Generating entity reference images ({len(needed_entities)} needed)")
    entity_id_to_url: dict[str, str] = {}
    if needed_entities:
        entity_id_to_url = generate_entity_reference_images(needed_entities, project_dir, api_key)

    # ── Phase 3: PIL composites (local paths only, no upload needed) ───────
    print("\n[v2] Phase 3 — Building composites")
    composites_dir = images_v2_dir / "composites"
    composites_dir.mkdir(exist_ok=True)
    entities_dir = project_dir / "images_v2" / "entities"

    segment_reference_path: dict[int, Path | None] = {}

    for seg in segments:
        idx = seg["segment_index"]
        seg_entities_flat = segment_entity_map.get(idx, [])

        if not seg_entities_flat:
            segment_reference_path[idx] = None
            continue

        # Enrich with _id and _type from typed entities
        seg_entities_typed = []
        for ent in seg_entities_flat:
            typed = name_to_typed.get(ent["name"])
            if typed:
                seg_entities_typed.append(typed)

        # Single entity — use its local PNG directly
        if len(seg_entities_typed) == 1:
            eid = seg_entities_typed[0]["_id"]
            png_path = entities_dir / f"{eid}.png"
            if png_path.exists():
                segment_reference_path[idx] = png_path
                logger.info("[v2] Seg %d single entity %s → local PNG", idx, eid)
            else:
                segment_reference_path[idx] = None
                logger.warning("[v2] Seg %d entity PNG missing for %s", idx, eid)
            continue

        # Multiple entities — build PIL composite (save locally)
        composite_out = composites_dir / f"segment_{idx}.png"
        if composite_out.exists():
            segment_reference_path[idx] = composite_out
            logger.info("[v2] Seg %d composite cached locally", idx)
            continue

        composite_path = build_segment_composite(seg_entities_typed, entities_dir, composite_out)
        if composite_path is None:
            logger.warning("[v2] Seg %d composite failed — no reference", idx)
            segment_reference_path[idx] = None
        else:
            segment_reference_path[idx] = composite_path
            logger.info("[v2] Seg %d composite built → %s", idx, composite_path.name)

    # ── Phase 4: Segment image generation ──────────────────────────────────
    print("\n[v2] Phase 4 — Generating segment images")

    # Pre-resolve unique reference URLs sequentially to avoid duplicate uploads
    reference_urls: dict[Path, str | None] = {}
    unique_reference_paths = []
    for ref_path in segment_reference_path.values():
        if ref_path and ref_path not in reference_urls:
            unique_reference_paths.append(ref_path)
            reference_urls[ref_path] = None

    for ref_path in unique_reference_paths:
        reference_urls[ref_path] = ensure_reference_url(ref_path)
        time.sleep(SEGMENT_DELAY)

    results_by_index: dict[int, dict] = {}

    def _run_segment(seg: dict) -> tuple[int, Path | None, Path | None]:
        idx = seg["segment_index"]
        prompt = prompts[idx]
        ref_path = segment_reference_path.get(idx)
        ref_url = reference_urls.get(ref_path) if ref_path else None
        saved = generate_image_for_segment_v2(
            prompt,
            idx,
            ref_path,
            images_v2_dir,
            api_key,
            reference_url=ref_url,
        )
        return idx, saved, ref_path

    with ThreadPoolExecutor(max_workers=SEGMENT_MAX_WORKERS) as executor:
        future_to_idx = {executor.submit(_run_segment, seg): seg["segment_index"] for seg in segments}
        for future in as_completed(future_to_idx):
            idx, saved, ref_path = future.result()
            results_by_index[idx] = {
                "segment_index": idx,
                "prompt": prompts[idx],
                "status": "ok" if saved else "failed",
                "image_path": str(saved) if saved else None,
                "reference_path": str(ref_path) if ref_path else None,
            }

    results = [results_by_index[seg["segment_index"]] for seg in segments]

    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"\n[v2] Done: {ok}/{len(segments)} images generated")
    return results

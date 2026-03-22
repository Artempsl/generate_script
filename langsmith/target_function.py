"""
Target function for LangSmith segmentation evaluation.

Calls OpenAI GPT models with the exact segmentation prompt to split
a storytelling script into visual narrative segments.

Usage:
    target = make_target(model="gpt-4o-mini", temperature=0.0)
    result = target({"script": "...", "metadata": {...}})
    # result = {"segments": [{"index": 1, "text": "..."}, ...]}
"""

import os
import json
import time
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    sys.exit("ERROR: OPENAI_API_KEY environment variable is not set")

# ---------------------------------------------------------------------------
# Exact segmentation prompt (from spec, used unchanged in all experiments)
# ---------------------------------------------------------------------------

SEGMENTATION_SYSTEM_PROMPT = """You are a cinematic story segmentation engine.
Your task is to split a story into short narrative segments optimized for visual scene generation.
Each segment must represent one clear visual moment that can be illustrated with a single static image.
The goal is to prepare the story for AI image generation, storyboards, or image-to-video pipelines.

IMPORTANT RULES

1. One visual moment per segment
Each segment must represent a single scene or action that could realistically be captured in one still image.

2. Avoid multiple events in one segment
If a paragraph contains several actions, split them into separate segments.

3. Prefer visual clarity
Each segment should clearly describe:
\u2022 who is present
\u2022 what they are doing
\u2022 the environment
\u2022 the emotional tone or tension

4. Keep segments short
Ideal length: 1\u20135 sentences.
Maximum: 5 sentences only if they describe the same visual moment.

5. Split when any of the following changes
\u2022 a new action begins
\u2022 a new character appears
\u2022 the emotional tension changes
\u2022 the camera focus would change
\u2022 the scene composition changes

6. Maintain the exact original text
Do NOT rewrite, summarize, or change wording.
Only divide the original text into smaller segments.

7. Preserve story order
Segments must follow the original narrative sequence.

8. Avoid extremely tiny fragments
Do not split into single clauses unless necessary for visual clarity.

9. Avoid abstract or non-visual sentences as standalone segments
If a sentence describes only emotion, atmosphere, or narration, merge it with a nearby visual moment.

10. Avoid segments shorter than 50 characters
Prefer merging very small fragments (less than 50 characters) with the previous visual moment unless absolutely necessary.

BEFORE FINALIZING THE SEGMENTATION, VERIFY:

1. Each segment represents a single visual moment.
2. Each segment could realistically be illustrated as a single static image.
3. No segment contains multiple distinct actions.
4. No segment is purely abstract narration.

Determine the appropriate number of segments based on the structure and length of the script.

CRITICALLY IMPORTANT \u2014 TEXT COPYING RULES:
1. COPY the text CHARACTER BY CHARACTER from the original
2. DO NOT change any words, punctuation, or formatting
3. DO NOT add new sentences
4. DO NOT paraphrase or rewrite anything
5. Simply split the EXISTING text into parts

CORRECT example:
Original: "Hello world! How are you? Great."
Segment 1: "Hello world!" \u2713 (exact copy)
Segment 2: "How are you? Great." \u2713 (exact copy)

INCORRECT:
"Greetings world!" \u2717 (changed wording)
"How are things?" \u2717 (paraphrased)

Return ONLY valid JSON array:
[
  {"index": 1, "text": "..."},
  {"index": 2, "text": "..."}
]"""

SEGMENTATION_USER_TEMPLATE = """\u26a0\ufe0f\u26a0\ufe0f\u26a0\ufe0f TASK: Split this script into visual segments \u26a0\ufe0f\u26a0\ufe0f\u26a0\ufe0f

\u26a0\ufe0f CRITICALLY IMPORTANT: COPY TEXT CHARACTER BY CHARACTER! DO NOT REWRITE!

Original text to segment:

{script}

Reminder: Do not change any words!"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_segments(raw: str) -> list:
    """Parse JSON array from raw LLM response, stripping markdown fences."""
    text = raw.strip()
    for prefix in ("```json", "```"):
        if text.startswith(prefix):
            text = text[len(prefix):]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    data = json.loads(text)

    # Handle object wrapper {"segments": [...]}
    if isinstance(data, dict):
        for key in ("segments", "result", "output", "data"):
            if key in data and isinstance(data[key], list):
                data = data[key]
                break

    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array, got {type(data).__name__}")

    result = []
    for item in data:
        if isinstance(item, dict) and "index" in item and "text" in item:
            result.append({"index": int(item["index"]), "text": str(item["text"]).strip()})

    if not result:
        raise ValueError("No valid segments found in response")

    return result


def _max_tokens_param(model: str, n: int) -> dict:
    """gpt-5.x and o-series models require max_completion_tokens instead of max_tokens."""
    if model.startswith("gpt-5") or model.startswith("o1") or model.startswith("o3") or model.startswith("o4"):
        return {"max_completion_tokens": n}
    return {"max_tokens": n}


def _call_openai(script: str, model: str, temperature: float) -> list:
    """
    Call OpenAI segmentation with retry (2 retries, exponential backoff).

    Args:
        script:      Full script text.
        model:       OpenAI model name.
        temperature: Sampling temperature.

    Returns:
        List of segment dicts: [{"index": int, "text": str}, ...]
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    user_message = SEGMENTATION_USER_TEMPLATE.format(script=script)

    last_error = None
    for attempt in range(3):  # initial attempt + 2 retries
        try:
            t0 = time.time()
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SEGMENTATION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature,
                **_max_tokens_param(model, 2048),
            )
            elapsed = time.time() - t0
            raw = response.choices[0].message.content or ""
            segments = _parse_segments(raw)
            print(
                f"  [{model} t={temperature}] {len(segments)} segments "
                f"in {elapsed:.1f}s (attempt {attempt + 1})"
            )
            return segments

        except (json.JSONDecodeError, ValueError) as e:
            last_error = e
            if attempt < 2:
                wait = 2 ** attempt
                print(f"  Parse error (attempt {attempt + 1}): {e}. Retry in {wait}s...")
                time.sleep(wait)
        except Exception as e:
            last_error = e
            if attempt < 2:
                wait = 2 ** attempt
                print(f"  API error (attempt {attempt + 1}): {e}. Retry in {wait}s...")
                time.sleep(wait)

    raise RuntimeError(f"Segmentation failed after 3 attempts: {last_error}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def make_target(model: str = "gpt-4o-mini", temperature: float = 0.0):
    """
    Factory: returns a LangSmith-compatible target function.

    Args:
        model:       OpenAI model name (e.g. "gpt-4o-mini", "gpt-4o").
        temperature: Sampling temperature (0.0 = deterministic).

    Returns:
        Callable(inputs: dict) -> {"segments": list}
    """
    def _target(inputs: dict) -> dict:
        script = inputs.get("script", "")
        segments = _call_openai(script, model, temperature)
        return {"segments": segments}

    safe_temp = str(temperature).replace(".", "_")
    safe_model = model.replace("-", "_").replace(".", "_")
    _target.__name__ = f"{safe_model}_temp{safe_temp}"
    return _target

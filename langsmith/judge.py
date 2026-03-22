"""
LLM-as-Judge evaluator for segmentation quality.

Uses GPT-4o-mini (temperature=0.0) to evaluate each segmentation output
on four human-aligned criteria, normalized to 0.0-1.0 scores.

Criteria (each rated 1-5 by the judge):
    relevance:       segments copy original text faithfully, no paraphrasing
    coherence:       each segment reads as a self-contained visual unit
    visualizability: each segment maps to exactly one illustratable scene
    completeness:    all story content is captured, no gaps or omissions

LangSmith evaluate() compatible signature:
    llm_judge(outputs, reference_outputs, inputs) -> list[dict]
"""

import os
import json
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

JUDGE_SYSTEM_PROMPT = """You are an expert evaluator of storytelling script segmentation for AI image generation.

You will receive:
1. The original script
2. The AI-produced segmentation
3. The reference (ground truth) segmentation

Evaluate the AI segmentation on four criteria. Output ONLY valid JSON with no text outside the JSON object.

OUTPUT FORMAT:
{
  "relevance": <integer 1-5>,
  "coherence": <integer 1-5>,
  "visualizability": <integer 1-5>,
  "completeness": <integer 1-5>,
  "comments": "<brief justification, max 2 sentences>"
}

SCORING GUIDE:
- relevance (1-5):
    5 = all segments use exact original text, character by character
    3 = minor wording changes in some segments
    1 = text was significantly rewritten or paraphrased

- coherence (1-5):
    5 = every segment is self-contained and clearly readable in isolation
    3 = some segments are ambiguous or weakly connected
    1 = segments are fragmented, incomplete, or confusing

- visualizability (1-5):
    5 = every segment maps to exactly one clear, illustratable static scene
    3 = some segments are abstract or contain multiple scenes
    1 = most segments are unillustrable or cram multiple actions together

- completeness (1-5):
    5 = all story content present, matches reference coverage
    3 = minor content missing (1-2 sentences lost)
    1 = significant story content is missing or gaps exist"""


def _build_judge_prompt(script: str, out_segments: list, ref_segments: list) -> str:
    out_text = "\n".join(
        f"[{s.get('index', i + 1)}] {s.get('text', '')}"
        for i, s in enumerate(out_segments)
    )
    ref_text = "\n".join(
        f"[{s.get('index', i + 1)}] {s.get('text', '')}"
        for i, s in enumerate(ref_segments)
    )
    return (
        f"ORIGINAL SCRIPT:\n{script}\n\n"
        f"---\nAI SEGMENTATION ({len(out_segments)} segments):\n{out_text}\n\n"
        f"---\nREFERENCE SEGMENTATION ({len(ref_segments)} segments):\n{ref_text}"
    )


def llm_judge(outputs: dict, reference_outputs: dict, inputs: dict) -> list:
    """
    LLM-as-judge evaluator. Compatible with LangSmith evaluate() API.

    Args:
        outputs:           Target function output {"segments": [...]}
        reference_outputs: Dataset ground truth {"segments": [...]}
        inputs:            Dataset input {"script": "...", "metadata": {...}}

    Returns:
        List of score dicts (key, score) with scores normalized to 0.0-1.0.
    """
    script = inputs.get("script", "")
    out_segments = outputs.get("segments", [])
    ref_segments = reference_outputs.get("segments", [])

    _zero = [
        {"key": "judge_relevance", "score": 0.0},
        {"key": "judge_coherence", "score": 0.0},
        {"key": "judge_visualizability", "score": 0.0},
        {"key": "judge_completeness", "score": 0.0},
        {"key": "judge_overall", "score": 0.0},
    ]

    if not out_segments:
        return _zero

    client = OpenAI(api_key=OPENAI_API_KEY)
    user_message = _build_judge_prompt(script, out_segments, ref_segments)

    last_error = None
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.0,
                max_tokens=300,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content or "{}"
            scores = json.loads(raw)

            relevance = max(1, min(5, int(scores.get("relevance", 3))))
            coherence = max(1, min(5, int(scores.get("coherence", 3))))
            visualizability = max(1, min(5, int(scores.get("visualizability", 3))))
            completeness = max(1, min(5, int(scores.get("completeness", 3))))
            overall = (relevance + coherence + visualizability + completeness) / 4

            return [
                {"key": "judge_relevance", "score": round(relevance / 5, 2)},
                {"key": "judge_coherence", "score": round(coherence / 5, 2)},
                {"key": "judge_visualizability", "score": round(visualizability / 5, 2)},
                {"key": "judge_completeness", "score": round(completeness / 5, 2)},
                {"key": "judge_overall", "score": round(overall / 5, 2)},
            ]

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            last_error = e
            if attempt < 2:
                time.sleep(2 ** attempt)
        except Exception as e:
            last_error = e
            if attempt < 2:
                time.sleep(2 ** attempt)

    print(f"  [judge] All 3 attempts failed: {last_error}")
    return _zero

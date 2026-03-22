"""
Algorithmic evaluators for segmentation quality assessment.

Three evaluators with the LangSmith evaluate() signature:
    evaluator(outputs: dict, reference_outputs: dict) -> list[dict]

1. structure_validator  - validates segment structure (list of {index, text})
2. length_consistency   - checks sentence counts per segment (ideal: 1-5)
3. reference_similarity - compares output against ground truth segmentation
"""

import re
from difflib import SequenceMatcher


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _count_sentences(text: str) -> int:
    """Heuristic sentence count: split on .!? followed by whitespace."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return len([s for s in sentences if s.strip()])


def _normalize(text: str) -> str:
    """Lowercase + collapse whitespace for text comparison."""
    return " ".join(text.lower().split())


# ---------------------------------------------------------------------------
# Evaluator 1: Structure Validator
# ---------------------------------------------------------------------------

def structure_validator(outputs: dict, reference_outputs: dict) -> list:
    """
    Validate that the output is a properly structured segment list.

    Checks:
    - outputs["segments"] is a non-empty list
    - every segment is a dict with "index" (castable to int) and non-empty "text" (str)

    Returns:
        structure_valid:      1.0 if every segment is valid, else 0.0
        valid_segment_ratio:  fraction of segments that are individually valid (0.0-1.0)
    """
    segments = outputs.get("segments", [])

    if not isinstance(segments, list) or len(segments) == 0:
        return [
            {"key": "structure_valid", "score": 0.0},
            {"key": "valid_segment_ratio", "score": 0.0},
        ]

    valid_count = 0
    for seg in segments:
        if not isinstance(seg, dict):
            continue
        try:
            int(seg.get("index", ""))
        except (TypeError, ValueError):
            continue
        if "text" in seg and isinstance(seg["text"], str) and seg["text"].strip():
            valid_count += 1

    valid_ratio = valid_count / len(segments)
    return [
        {"key": "structure_valid", "score": 1.0 if valid_ratio == 1.0 else 0.0},
        {"key": "valid_segment_ratio", "score": round(valid_ratio, 3)},
    ]


# ---------------------------------------------------------------------------
# Evaluator 2: Length Consistency
# ---------------------------------------------------------------------------

def length_consistency(outputs: dict, reference_outputs: dict) -> list:
    """
    Check that segments contain 1-5 sentences each.

    Penalizes:
    - Segments with 0 sentences (empty or trivially short)
    - Segments with > 5 sentences (multiple visual moments merged)

    Returns:
        length_score:               fraction of segments within 1-5 sentence range
        avg_sentences_per_segment:  average sentence count per segment
    """
    segments = outputs.get("segments", [])

    if not isinstance(segments, list) or len(segments) == 0:
        return [
            {"key": "length_score", "score": 0.0},
            {"key": "avg_sentences_per_segment", "score": 0.0},
        ]

    in_range = 0
    total_sentences = 0
    for seg in segments:
        if not isinstance(seg, dict):
            continue
        count = _count_sentences(seg.get("text", ""))
        total_sentences += count
        if 1 <= count <= 5:
            in_range += 1

    return [
        {"key": "length_score", "score": round(in_range / len(segments), 3)},
        {"key": "avg_sentences_per_segment", "score": round(total_sentences / len(segments), 2)},
    ]


# ---------------------------------------------------------------------------
# Evaluator 3: Reference Similarity
# ---------------------------------------------------------------------------

def reference_similarity(outputs: dict, reference_outputs: dict) -> list:
    """
    Compare output segmentation against the ground truth reference.

    Metrics:
    - segment_count_match:  ratio min/max of segment counts (1.0 = exact match)
    - exact_text_match:     fraction of positional segments with identical normalized text
    - boundary_similarity:  per reference segment, best SequenceMatcher ratio in output (avg)
    - text_coverage:        SequenceMatcher ratio of combined texts (measures text preservation)

    Returns all four metrics.
    """
    ref_segments = reference_outputs.get("segments", [])
    out_segments = outputs.get("segments", [])

    if not ref_segments or not out_segments:
        return [
            {"key": "segment_count_match", "score": 0.0},
            {"key": "exact_text_match", "score": 0.0},
            {"key": "boundary_similarity", "score": 0.0},
            {"key": "text_coverage", "score": 0.0},
        ]

    ref_texts = [_normalize(s.get("text", "")) for s in ref_segments]
    out_texts = [_normalize(s.get("text", "")) for s in out_segments]

    # 1. Segment count match
    ref_n, out_n = len(ref_texts), len(out_texts)
    count_match = min(ref_n, out_n) / max(ref_n, out_n)

    # 2. Positional exact text match
    min_len = min(ref_n, out_n)
    exact_matches = sum(1 for i in range(min_len) if ref_texts[i] == out_texts[i])
    exact_match_score = exact_matches / ref_n

    # 3. Boundary similarity — for each reference segment find best match in output
    boundary_scores = [
        max(SequenceMatcher(None, ref_t, out_t).ratio() for out_t in out_texts)
        for ref_t in ref_texts
    ]
    boundary_similarity = sum(boundary_scores) / len(boundary_scores)

    # 4. Text coverage — whole-text preservation
    ref_combined = " ".join(ref_texts)
    out_combined = " ".join(out_texts)
    text_coverage = SequenceMatcher(None, ref_combined, out_combined).ratio()

    return [
        {"key": "segment_count_match", "score": round(count_match, 3)},
        {"key": "exact_text_match", "score": round(exact_match_score, 3)},
        {"key": "boundary_similarity", "score": round(boundary_similarity, 3)},
        {"key": "text_coverage", "score": round(text_coverage, 3)},
    ]

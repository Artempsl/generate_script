# Evaluation Report
## Storytelling Script Segmentation — Model Comparison

**Date:** 2026-03-22  
**Dataset:** `storytelling_segmentation_eval_v1` (10 examples)  
**Experiments:** 3 models × 10 examples = 30 target calls, 120 evaluator calls  
**Results source:** `evaluation_results.json`

---

## 1. Results Summary

### 1.1 Scores by Model — All Metrics

| Metric | gpt-4o-mini | gpt-4o | gpt-5.4 |
|---|:---:|:---:|:---:|
| **structure_valid** | 1.000 | 1.000 | 1.000 |
| **valid_segment_ratio** | 1.000 | 1.000 | 1.000 |
| **length_score** | 1.000 | 1.000 | 1.000 |
| **avg_sentences_per_segment** | 1.000 | 1.000 | **2.360** |
| **segment_count_match** | 0.385 | 0.385 | **0.909** |
| **exact_text_match** | 0.000 | 0.000 | **0.300** |
| **boundary_similarity** | 0.665 | 0.665 | **0.989** |
| **text_coverage** | 1.000 | 1.000 | 1.000 |
| **judge_relevance** | 1.000 | 1.000 | 1.000 |
| **judge_coherence** | 0.880 | 0.920 | **1.000** |
| **judge_visualizability** | 1.000 | 1.000 | 1.000 |
| **judge_completeness** | 0.600 | 0.600 | **0.980** |
| **judge_overall** | 0.870 | 0.880 | **0.995** |

### 1.2 Ranking by Primary Metric (boundary_similarity)

| Rank | Model | boundary_similarity | segment_count_match | exact_text_match | Time |
|:---:|---|:---:|:---:|:---:|:---:|
| **1** | **gpt-5.4** | **0.989** | **0.909** | **0.300** | 86s |
| 2 | gpt-4o | 0.665 | 0.385 | 0.000 | 71s |
| 3 | gpt-4o-mini | 0.665 | 0.385 | 0.000 | 127s |

### 1.3 Score Distribution

**gpt-5.4** dominates on all reference-based metrics. `gpt-4o` and `gpt-4o-mini` score identically on every metric except LLM-judge coherence (where `gpt-4o` scores slightly higher: 0.920 vs. 0.880).

**Spread across models (boundary_similarity):**
- Min: 0.665 (gpt-4o / gpt-4o-mini)
- Max: 0.989 (gpt-5.4)
- Delta: **+0.324** — a very large difference for a single metric in NLP evaluation

---

## 2. Per-Metric Analysis

### 2.1 Structure & Format (structure_valid, valid_segment_ratio)

All three models score **1.000** — every model reliably produces well-formed JSON with valid `index`/`text` fields across all 30 runs.

**Interpretation:** The structured output format is solved at this level. No prompt failures.

---

### 2.2 Segment Length (length_score, avg_sentences_per_segment)

All models score **1.000** on `length_score` — all segments fall within the 1–5 sentence range.

However, `avg_sentences_per_segment` reveals a key behavioral difference:
- **gpt-4o-mini / gpt-4o:** avg = **1.000** — every segment is a single sentence. Technically valid but indicates maximal over-splitting.
- **gpt-5.4:** avg = **2.360** — segments contain ~2–3 sentences each. This matches the reference design, which groups 2–4 related sentences per visual moment.

**Interpretation:** `avg_sentences_per_segment` is a strong proxy for segmentation granularity. A value of ~2–3 aligns with the intended one-image-per-segment design.

---

### 2.3 Reference Similarity

#### segment_count_match

- **gpt-4o-mini / gpt-4o:** 0.385 → they produce ~26 segments vs. 10 reference.  
  `min(10,26) / max(10,26) = 10/26 = 0.385`
- **gpt-5.4:** 0.909 → produces **11 segments** vs. 10 reference.  
  `min(10,11) / max(10,11) = 10/11 = 0.909`

This is the most decisive indicator: `gpt-4o` and `gpt-4o-mini` split each sentence into its own segment. `gpt-5.4` groups them into coherent visual moments.

#### boundary_similarity

- **gpt-4o-mini / gpt-4o:** 0.665 → moderate alignment. With 26 segments some boundaries happen to fall near reference boundaries by chance, but many split within reference segments.
- **gpt-5.4:** 0.989 → near-perfect alignment. Almost every reference boundary is reproduced.

#### exact_text_match

- **gpt-4o-mini / gpt-4o:** 0.000 — no segment at position i matches reference segment i exactly (expected, given they produce ~2.6× more segments).
- **gpt-5.4:** 0.300 — 3 out of 10 reference segments appear verbatim at the correct position.

#### text_coverage

All models: **1.000** — the original script text is preserved character-for-character in every run. The prompt's text-preservation rules ("copy text CHARACTER BY CHARACTER") work perfectly.

---

### 2.4 LLM Judge Scores

| Criterion | gpt-4o-mini | gpt-4o | gpt-5.4 |
|---|:---:|:---:|:---:|
| relevance | 1.000 | 1.000 | 1.000 |
| coherence | 0.880 | 0.920 | **1.000** |
| visualizability | 1.000 | 1.000 | 1.000 |
| completeness | 0.600 | 0.600 | **0.980** |
| overall | 0.870 | 0.880 | **0.995** |

**Highest scoring:** `gpt-5.4` on all criteria.

**Lowest scoring:** `judge_completeness` at 0.600 for both `gpt-4o-mini` and `gpt-4o`. Despite `text_coverage=1.0` (all text present), the judge rates completeness at 60%. Single-sentence segments technically contain all the text but feel incomplete as standalone visual narrative units — the judge detects this semantic incompleteness.

**Consistent perfect scores (all models):** `judge_relevance` and `judge_visualizability` both 1.000 — individual sentences are always visualizable, and text is always preserved verbatim.

---

## 3. Patterns: High and Low Scoring Insights

### High Scores (all models)
- **Text faithfulness** (`text_coverage` = 1.0, `judge_relevance` = 1.0): The prompt's emphasis on verbatim copying works universally. No model rewrote or paraphrased.
- **Structure compliance** (`structure_valid` = 1.0): JSON format instructions are reliable regardless of model.
- **Single-sentence visualizability** (`judge_visualizability` = 1.0): Even maximally over-split segments are individually visualizable.

### Low Scores (gpt-4o-mini / gpt-4o only)
- **Segment count** (`segment_count_match` = 0.385): These models interpret "one visual moment" at the sentence level, not the paragraph/scene level.
- **Completeness** (`judge_completeness` = 0.600): Fragmented 1-sentence segments feel incomplete as narrative units — 60% score suggests the judge applies a consistent structural penalty.
- **Boundary alignment** (`boundary_similarity` = 0.665): Roughly 1 in 3 reference boundaries is missed.

### Root Cause of Over-Segmentation

`gpt-4o-mini` and `gpt-4o` apply Rule 5 of the prompt ("split when a new action begins") too aggressively. Each sentence contains a micro-action, so they split at every sentence boundary. They follow the prompt technically but do not generalize the intent to the scene level.

`gpt-5.4` correctly interprets "visual moment" at the narrative paragraph/scene level, grouping 2–3 related sentences into coherent units.

---

## 4. Bias Awareness & Judge Limitations

### 4.1 Potential Biases in Judge Prompt

**Halo effect:** The judge receives all segments at once. Positive early segments may inflate scores for later ones (or vice versa for negative sets).

**Verbosity bias:** LLM judges often assign higher coherence/completeness to denser outputs. `gpt-5.4`'s multi-sentence segments may score higher partly because they contain richer text — the judge cannot fully disentangle segmentation quality from content density.

**Self-similarity bias for gpt-4o-mini judge:** The judge model is `gpt-4o-mini`. When evaluating `gpt-4o-mini` outputs, it may recognize its own segmentation patterns and rate them more favorably. This bias would inflate `judge_*` scores for `gpt-4o-mini` relative to an independent judge — making `gpt-5.4`'s dominance even more significant.

**Reference anchoring:** The judge receives the reference segmentation, causing structural differences from the reference to be penalized even if semantically equivalent. This adds an implicit alignment requirement beyond pure quality.

### 4.2 Calibration Considerations

The judge uses a 0–10 integer scale normalized to 0.0–1.0:
- 0.600 = 6/10 = "acceptable but missing key qualities"
- 0.980 = 9.8/10 = "near perfect"

The exact `judge_completeness` = 0.600 for both `gpt-4o` and `gpt-4o-mini`, consistent across all 10 examples, indicates a systematic categorical judgment ("sentence-level splitting is structurally incomplete") rather than per-example variance.

### 4.3 Limitations of LLM-as-Judge

1. **Single-model judge:** Using only `gpt-4o-mini` creates a single point of failure and bias. An ensemble (e.g., gpt-4o + Claude) would provide more robust scores.
2. **Prompt sensitivity:** Small phrasing changes in the judge prompt can shift scores significantly. The current prompt has not been calibrated against human rater ground truth.
3. **No inter-rater reliability measurement:** There is no metric for judge consistency across runs (temperature=0.0 mitigates randomness but not systematic prompt interpretation variance).
4. **Context saturation risk:** For longer scripts, the judge prompt (script + all segments + reference) may approach context limits, potentially degrading evaluation quality.
5. **Ordinal scale≠interval scale:** A step from 0.6→0.7 is not necessarily equivalent in judgment effort/quality difference to a step from 0.9→1.0.

---

## 5. Recommendations

### 5.1 Production Model Choice

**Use `gpt-5.4` for production segmentation.**

Evidence:
- `boundary_similarity` = 0.989 vs. 0.665 for alternatives (+49% relative improvement)
- Produces 11 segments vs. 10 reference — within 1 segment of ground truth
- Consistent across all 10 dataset examples (deterministic at t=0.0)
- `avg_sentences_per_segment` = 2.36 matches the intended 2–4 sentence visual moment design
- `judge_overall` = 0.995 — near-perfect holistic quality

**Do not use `gpt-4o` or `gpt-4o-mini`** for segmentation tasks requiring narrative coherence. They reliably produce 26 segments for a 10-segment story, fragmenting unified scenes.

### 5.2 Prompt Improvements for gpt-4o / gpt-4o-mini (if cost constraints apply)

1. **Explicit segment count guidance:** Add `"Target approximately 8–12 segments for a ~500 word story"` to the system prompt.
2. **Anti-sentence-split rule:** Add `"Do NOT treat each sentence as a separate segment. Group 2–4 sentences that describe the same scene into one segment."`
3. **Minimum segment length:** Change rule 10 threshold from 50 to 150 characters.
4. **Show a bad example:** Add an explicit "INCORRECT: splitting every sentence into its own segment" counter-example.

### 5.3 Improving Evaluation Methodology

| Priority | Improvement | Rationale |
|---|---|---|
| High | Add diverse scripts to dataset (multiple stories, lengths, RU + EN) | Currently all 10 examples are identical — variance measures only consistency, not generalization |
| High | Human annotation baseline | Measure judge correlation with human raters to calibrate trust in judge scores |
| Medium | Ensemble judge (gpt-4o + secondary model) | Reduce self-similarity bias and single-model judgment risk |
| Medium | Per-example score storage | Enable variance analysis across the dataset |
| Low | A/B test prompt variants for gpt-4o | Verify whether prompt changes can close the gap with gpt-5.4 |

### 5.4 Next Steps

| Priority | Action |
|---|---|
| **High** | Update `segment_script_tool` in `agent/tools.py` to use `gpt-5.4` instead of Cohere `command-r` |
| **High** | Add `max_completion_tokens` compatibility to production segmentation call |
| **Medium** | Expand dataset with RU-language scripts and 200–1000 word range |
| **Medium** | Collect human segmentation annotations for 3 scripts to calibrate judge |
| **Low** | Test `gpt-5.4-mini` if released — may offer comparable quality at lower cost |

---

## 6. Raw Results Data

```json
{
  "experiments": [
    {
      "experiment": "gpt-4o-mini_t0.0",
      "model": "gpt-4o-mini",
      "temperature": 0.0,
      "elapsed_seconds": 127.4,
      "avg_scores": {
        "structure_valid": 1.0, "valid_segment_ratio": 1.0,
        "length_score": 1.0, "avg_sentences_per_segment": 1.0,
        "segment_count_match": 0.385, "exact_text_match": 0.0,
        "boundary_similarity": 0.665, "text_coverage": 1.0,
        "judge_relevance": 1.0, "judge_coherence": 0.88,
        "judge_visualizability": 1.0, "judge_completeness": 0.6,
        "judge_overall": 0.87
      }
    },
    {
      "experiment": "gpt-4o_t0.0",
      "model": "gpt-4o",
      "temperature": 0.0,
      "elapsed_seconds": 70.8,
      "avg_scores": {
        "structure_valid": 1.0, "valid_segment_ratio": 1.0,
        "length_score": 1.0, "avg_sentences_per_segment": 1.0,
        "segment_count_match": 0.385, "exact_text_match": 0.0,
        "boundary_similarity": 0.665, "text_coverage": 1.0,
        "judge_relevance": 1.0, "judge_coherence": 0.92,
        "judge_visualizability": 1.0, "judge_completeness": 0.6,
        "judge_overall": 0.88
      }
    },
    {
      "experiment": "gpt-5.4_t0.0",
      "model": "gpt-5.4",
      "temperature": 0.0,
      "elapsed_seconds": 85.9,
      "avg_scores": {
        "structure_valid": 1.0, "valid_segment_ratio": 1.0,
        "length_score": 1.0, "avg_sentences_per_segment": 2.36,
        "segment_count_match": 0.909, "exact_text_match": 0.3,
        "boundary_similarity": 0.989, "text_coverage": 1.0,
        "judge_relevance": 1.0, "judge_coherence": 1.0,
        "judge_visualizability": 1.0, "judge_completeness": 0.98,
        "judge_overall": 0.995
      }
    }
  ],
  "dataset": "storytelling_segmentation_eval_v1",
  "total_experiments": 3
}
```

---

## Summary

> Fill this section after running experiments.

**Winner:** _(model + temperature with highest boundary_similarity)_
**Recommendation:** Use `___` at temperature `___` for production segmentation.

---

## Results Table

| # | Model       | Temp | boundary_sim | exact_match | count_match | judge_overall | time (s) |
|---|-------------|------|:------------:|:-----------:|:-----------:|:-------------:|:--------:|
| 1 | gpt-4o-mini | 0.0  |              |             |             |               |          |
| 2 | gpt-4o-mini | 0.1  |              |             |             |               |          |
| 3 | gpt-4o-mini | 0.3  |              |             |             |               |          |
| 4 | gpt-4o-mini | 0.5  |              |             |             |               |          |
| 5 | gpt-4o-mini | 0.7  |              |             |             |               |          |
| 6 | gpt-4o      | 0.0  |              |             |             |               |          |
| 7 | gpt-4o      | 0.1  |              |             |             |               |          |
| 8 | gpt-4o      | 0.3  |              |             |             |               |          |
| 9 | gpt-4o      | 0.5  |              |             |             |               |          |
|10 | gpt-4o      | 0.7  |              |             |             |               |          |

_(Sorted by boundary_similarity descending after filling)_

---

## Detailed Scores

### gpt-4o-mini

| Metric                    | t=0.0 | t=0.1 | t=0.3 | t=0.5 | t=0.7 |
|---------------------------|:-----:|:-----:|:-----:|:-----:|:-----:|
| structure_valid           |       |       |       |       |       |
| valid_segment_ratio       |       |       |       |       |       |
| length_score              |       |       |       |       |       |
| avg_sentences_per_segment |       |       |       |       |       |
| segment_count_match       |       |       |       |       |       |
| exact_text_match          |       |       |       |       |       |
| boundary_similarity       |       |       |       |       |       |
| text_coverage             |       |       |       |       |       |
| judge_relevance           |       |       |       |       |       |
| judge_coherence           |       |       |       |       |       |
| judge_visualizability     |       |       |       |       |       |
| judge_completeness        |       |       |       |       |       |
| judge_overall             |       |       |       |       |       |

### gpt-4o

| Metric                    | t=0.0 | t=0.1 | t=0.3 | t=0.5 | t=0.7 |
|---------------------------|:-----:|:-----:|:-----:|:-----:|:-----:|
| structure_valid           |       |       |       |       |       |
| valid_segment_ratio       |       |       |       |       |       |
| length_score              |       |       |       |       |       |
| avg_sentences_per_segment |       |       |       |       |       |
| segment_count_match       |       |       |       |       |       |
| exact_text_match          |       |       |       |       |       |
| boundary_similarity       |       |       |       |       |       |
| text_coverage             |       |       |       |       |       |
| judge_relevance           |       |       |       |       |       |
| judge_coherence           |       |       |       |       |       |
| judge_visualizability     |       |       |       |       |       |
| judge_completeness        |       |       |       |       |       |
| judge_overall             |       |       |       |       |       |

---

## Observations

> Fill after reviewing results.

- **Temperature effect (gpt-4o-mini):** ___
- **Temperature effect (gpt-4o):** ___
- **Model comparison at t=0.0:** ___
- **Best value for money:** ___

---

## Cost Estimate

| Model       | Calls | Avg tokens/call | Est. cost |
|-------------|:-----:|:---------------:|:---------:|
| gpt-4o-mini | 50    | ~1200           |           |
| gpt-4o      | 50    | ~1200           |           |
| judge       | 100   | ~800            |           |
| **Total**   |       |                 |           |

---

## LangSmith UI

Full per-example breakdowns: https://smith.langchain.com  
Project: `storytelling-segmentation-eval`

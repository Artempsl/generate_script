# LangSmith Evaluation Documentation
## Storytelling Script Segmentation — Model Comparison

**Project:** `storytelling-segmentation-eval`  
**Dataset:** `storytelling_segmentation_eval_v1`  
**LangSmith UI (EU):** https://eu.smith.langchain.com  
**Dataset URL:** https://eu.smith.langchain.com/o/b9c42180-fcfa-42e9-9776-fad95c258de4/datasets/2a332a51-9bf1-481f-892a-06448fee7f27  
**Experiment URL:** https://eu.smith.langchain.com/o/b9c42180-fcfa-42e9-9776-fad95c258de4/projects/p/storytelling-segmentation-eval

---

## 1. Overview

**Goal:** Determine which OpenAI model produces story segmentation closest to a human-curated 10-segment ground truth, at temperature 0.0 (deterministic).

**Models evaluated:**

| Model | Temperature | Notes |
|---|---|---|
| `gpt-4o-mini` | 0.0 | Lightweight, cost-efficient |
| `gpt-4o` | 0.0 | Standard flagship model |
| `gpt-5.4` | 0.0 | Latest generation model |

**Primary metric:** `boundary_similarity` — measures how closely segment boundaries align with the reference segmentation, robust to segment count differences.

---

## 2. Dataset Creation

### File: `langsmith/dataset_creation.py`

The dataset `storytelling_segmentation_eval_v1` contains **10 identical examples**. All examples share the same input script and reference segmentation. This controlled design allows clean model comparison — variance in scores reflects the model's consistency, not input variability.

### Input Script

A ~550-word English fantasy/literary story about a man named Alex who discovers a mysterious bookstore. The story has clear visual beats: a mundane routine opening, bookstore discovery, interior exploration, an elderly shopkeeper, a magical transition, an otherworldly landscape, and a final decision moment.

The script was chosen because:
- It has natural, unambiguous scene boundaries
- It contains both action paragraphs and atmospheric/reflective passages (tests merging behavior)
- It is long enough to produce ~10 meaningful segments at the correct granularity

### Reference Segmentation (Ground Truth)

10 segments manually curated to represent cinematically coherent visual moments:

| # | Description |
|---|---|
| 1 | Alex's daily routine and comfort in predictability |
| 2 | Discovery of the mysterious bookstore |
| 3 | Entering the shop — air, shelves, atmosphere |
| 4 | The elderly shopkeeper points to a book |
| 5 | Alex touches the cover — reality shifts |
| 6 | Arrival in the otherworldly field |
| 7 | Realization — he is part of this world |
| 8 | A voice explains: every avoided choice led here |
| 9 | Alex weighs his old life vs. the unknown |
| 10 | He smiles and steps forward |

### Dataset Structure

Each example is stored with the following schema:
```json
{
  "inputs": {
    "script": "<full story text>",
    "metadata": {
      "title": "The Bookstore at the Edge of Everything",
      "language": "en",
      "genre": "fantasy",
      "reference_segment_count": 10
    }
  },
  "outputs": {
    "segments": [
      {"index": 1, "text": "Alex had always believed..."},
      ...
    ]
  }
}
```

**Dataset ID:** `2a332a51-9bf1-481f-892a-06448fee7f27`

**Creation command (run once):**
```powershell
$env:LANGCHAIN_API_KEY = [System.Environment]::GetEnvironmentVariable("LANGCHAIN_API_KEY", "User")
python langsmith/dataset_creation.py
```

---

## 3. Target Function

### File: `langsmith/target_function.py`

The target function wraps OpenAI's Chat API with the exact cinematic segmentation prompt used in production (`agent/tools.py`).

**Factory pattern:**
```python
target = make_target(model="gpt-5.4", temperature=0.0)
result = target({"script": "...", "metadata": {...}})
# returns: {"segments": [{"index": 1, "text": "..."}, ...]}
```

**Prompt design:**
- **System prompt:** Cinematic segmentation engine persona with 10 rules covering visual clarity, text preservation, segment length, and splitting criteria. Includes explicit correct/incorrect examples.
- **User prompt:** Task reminder + the script text + repeated text-preservation warnings.
- **Output format:** Raw JSON array `[{"index": int, "text": str}, ...]`

**Retry logic:** 3 attempts with exponential backoff (1s → 2s). On all failures raises `RuntimeError`.

**Model compatibility note:** `gpt-5.x` models require `max_completion_tokens` instead of `max_tokens`. This is handled by the `_max_tokens_param()` helper:
```python
def _max_tokens_param(model: str, n: int) -> dict:
    if model.startswith("gpt-5") or model.startswith("o1") or model.startswith("o3") or model.startswith("o4"):
        return {"max_completion_tokens": n}
    return {"max_tokens": n}
```

---

## 4. Evaluators

### File: `langsmith/evaluators.py`

Four evaluators run on each `(outputs, reference_outputs)` pair. All follow the LangSmith signature and return `list[{"key": str, "score": float}]`.

---

### Evaluator 1: `structure_validator`

**Purpose:** Verify the model returned a well-formed segment list — a prerequisite check before any quality metrics are computed.

| Metric | Type | Description |
|---|---|---|
| `structure_valid` | Binary | 1.0 if all segments have valid `index` (castable to int) and non-empty `text` (str), else 0.0 |
| `valid_segment_ratio` | Continuous | Fraction of individually valid segments (0.0–1.0) |

---

### Evaluator 2: `length_consistency`

**Purpose:** Check that each segment contains 1–5 sentences — enforcing the "one visual moment" rule. Segments with only 1 sentence indicate possible over-splitting; segments with >5 sentences suggest multiple scenes were merged.

| Metric | Type | Description |
|---|---|---|
| `length_score` | Continuous | Fraction of segments with sentence count in [1, 5] |
| `avg_sentences_per_segment` | Continuous | Mean sentence count per segment |

**Sentence detection:** Regex split on `.!?` followed by whitespace.

---

### Evaluator 3: `reference_similarity`

**Purpose:** Compare the model's segmentation against the ground truth on four complementary dimensions.

| Metric | Formula | Interpretation |
|---|---|---|
| `segment_count_match` | `min(n_ref, n_out) / max(n_ref, n_out)` | 1.0 = exact segment count; penalizes over/under segmentation |
| `exact_text_match` | Positional exact match rate | Fraction of segments at the correct position with identical normalized text |
| `boundary_similarity` | For each reference segment, best `SequenceMatcher` ratio in the output; averaged | **Primary metric** — robust to count differences; measures boundary alignment |
| `text_coverage` | `SequenceMatcher` ratio of full combined texts | Measures how well the original text was preserved vs. rewritten/dropped |

`boundary_similarity` is the primary ranking metric because it rewards models that place boundaries in the right narrative locations, regardless of whether they produce exactly 10 segments.

---

### Evaluator 4: `llm_judge`

### File: `langsmith/judge.py`

**Model:** `gpt-4o-mini` at `temperature=0.0`, `response_format={"type": "json_object"}`

The judge receives the input script, the model's output segments, and the reference segments. It rates five criteria on a 0–10 scale (normalized to 0.0–1.0):

| Metric | Criterion |
|---|---|
| `judge_relevance` | Each segment represents a single, visually distinct moment; text is preserved verbatim |
| `judge_coherence` | Segments flow logically; boundaries fall at natural narrative breaks |
| `judge_visualizability` | Each segment can be realistically illustrated as a single static image |
| `judge_completeness` | All story content is covered — nothing is skipped, summarized, or lost |
| `judge_overall` | Holistic quality of the segmentation |

---

## 5. Experiment Configuration

### File: `langsmith/experiment.py`

```python
EXPERIMENT_CONFIGS = [
    {"model": "gpt-4o-mini", "temperature": 0.0},
    {"model": "gpt-4o",      "temperature": 0.0},
    {"model": "gpt-5.4",     "temperature": 0.0},
]
```

**Design decisions:**
- **Temperature fixed at 0.0** — deterministic outputs enable fair comparison without stochastic noise
- **`max_concurrency=1`** — sequential processing to avoid rate-limit errors
- **Skip logic** — already-completed experiments are loaded from `evaluation_results.json` and not re-run
- **LangSmith EU endpoint** — `https://eu.api.smith.langchain.com` (EU account)

**Running the evaluation:**
```powershell
$env:LANGCHAIN_API_KEY = [System.Environment]::GetEnvironmentVariable("LANGCHAIN_API_KEY", "User")
python langsmith/experiment.py
```

**Results saved to:** `langsmith/evaluation_results.json`

**To run a single experiment:**
```powershell
$env:SINGLE = "gpt-5.4:0.0"
python langsmith/experiment.py
```

---

## 6. File Structure

```
langsmith/
├── dataset_creation.py      # Creates LangSmith dataset (run once)
├── target_function.py       # OpenAI call wrapper with retry + model compat
├── evaluators.py            # 3 algorithmic evaluators
├── judge.py                 # LLM-as-judge evaluator (gpt-4o-mini)
├── experiment.py            # Experiment runner + results serializer
├── evaluation_results.json  # Final results (auto-generated)
├── langsmith_evaluation.md  # This documentation
└── evaluation_report.md     # Analysis and recommendations
```

---

## 7. Setup from Scratch

```bash
# 1. Install dependencies
pip install langsmith openai python-dotenv

# 2. Set API keys (Windows)
[System.Environment]::SetEnvironmentVariable("LANGCHAIN_API_KEY", "lsv2_pt_...", "User")
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "User")

# 3. Create dataset (once)
python langsmith/dataset_creation.py

# 4. Run experiments
python langsmith/experiment.py
```

---

## Primary Ranking Metric

**`boundary_similarity`** — measures how well output segment boundaries align
with ground truth. Higher = closer to the ideal 10-segment reference.

Secondary metrics (for tie-breaking):
1. `exact_text_match` — exact positional match
2. `segment_count_match` — correct segment count
3. `judge_overall` — human-aligned quality
4. `elapsed_seconds` — speed

---

## Output Files

| File | Description |
|------|-------------|
| `langsmith/evaluation_results.json` | Machine-readable results after running |
| `langsmith/evaluation_report.md`    | Human-readable summary (fill after run) |

---

## LangSmith UI

View results at: https://smith.langchain.com

Project name: `storytelling-segmentation-eval`

Each experiment appears as a separate run with per-example breakdowns
and aggregated evaluator scores.

---

## File Structure

```
langsmith/
├── dataset_creation.py    # Create LangSmith dataset (run once)
├── target_function.py     # Segmentation target function + make_target() factory
├── evaluators.py          # 3 algorithmic evaluators
├── judge.py               # LLM-as-judge evaluator (GPT-4o-mini)
├── experiment.py          # Main runner — 10 experiments, saves results
├── langsmith_evaluation.md  ← you are here
├── evaluation_report.md   # Results template (fill after running)
└── evaluation_results.json  # Auto-generated by experiment.py
```

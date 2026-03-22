"""
Local Experiment Runner — Storytelling Segmentation Evaluation (no LangSmith required).

Runs 10 experiments (gpt-4o-mini + gpt-4o x 5 temperatures each) and
saves results to evaluation_results.json.

This version does NOT require a LangSmith API key — evaluation runs
entirely locally and results are printed + saved to JSON.

Run:
    python langsmith/run_local.py

Prerequisites:
    pip install openai python-dotenv
    Set OPENAI_API_KEY in your environment.
"""

import os
import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    sys.exit("ERROR: OPENAI_API_KEY environment variable is not set")

_this_dir = str(Path(__file__).parent)
if _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

from target_function import make_target                                    # noqa: E402
from evaluators import structure_validator, length_consistency, reference_similarity  # noqa: E402
from judge import llm_judge                                                # noqa: E402
from dataset_creation import SCRIPT, REFERENCE_SEGMENTATION               # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RESULTS_FILE = Path(__file__).parent / "evaluation_results.json"

EXPERIMENT_CONFIGS = [
    {"model": "gpt-4o-mini", "temperature": 0.0},
    {"model": "gpt-4o-mini", "temperature": 0.1},
    {"model": "gpt-4o-mini", "temperature": 0.3},
    {"model": "gpt-4o-mini", "temperature": 0.5},
    {"model": "gpt-4o-mini", "temperature": 0.7},
    {"model": "gpt-4o",      "temperature": 0.0},
    {"model": "gpt-4o",      "temperature": 0.1},
    {"model": "gpt-4o",      "temperature": 0.3},
    {"model": "gpt-4o",      "temperature": 0.5},
    {"model": "gpt-4o",      "temperature": 0.7},
]

# 10 identical inputs (same as the LangSmith dataset)
INPUTS = [
    {"script": SCRIPT, "metadata": {"genre": "fantasy", "duration": 4}}
    for _ in range(10)
]
REFERENCE_OUTPUTS = {"segments": REFERENCE_SEGMENTATION}

EVALUATORS = [
    structure_validator,
    length_consistency,
    reference_similarity,
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def _avg_scores(all_scores: list[list[dict]]) -> dict:
    """Average per-metric scores across examples."""
    totals: dict[str, list] = {}
    for scores in all_scores:
        for s in scores:
            totals.setdefault(s["key"], []).append(s["score"])
    return {k: round(sum(v) / len(v), 4) for k, v in totals.items()}


def run_experiment(config: dict) -> dict:
    model = config["model"]
    temperature = config["temperature"]
    name = f"{model}_t{temperature}"

    print(f"\n{'=' * 60}")
    print(f"Experiment: {name}")
    print(f"{'=' * 60}")

    target = make_target(model=model, temperature=temperature)
    example_outputs = []
    judge_scores_all = []
    start_time = time.time()

    for i, inp in enumerate(INPUTS):
        try:
            out = target(inp)
        except Exception as exc:
            print(f"  [example {i+1}] target error: {exc}")
            out = {"segments": []}
        example_outputs.append(out)

    elapsed = time.time() - start_time

    # Algorithmic evaluators
    algo_scores_all = []
    for out in example_outputs:
        combined = []
        for ev in EVALUATORS:
            combined.extend(ev(out, REFERENCE_OUTPUTS))
        algo_scores_all.append(combined)

    # LLM judge (one call per example)
    print(f"  Running LLM judge on {len(example_outputs)} examples...")
    for i, (inp, out) in enumerate(zip(INPUTS, example_outputs)):
        try:
            j = llm_judge(out, REFERENCE_OUTPUTS, inp)
        except Exception as exc:
            print(f"  [judge {i+1}] error: {exc}")
            j = []
        judge_scores_all.append(j)

    avg_algo = _avg_scores(algo_scores_all)
    avg_judge = _avg_scores(judge_scores_all)
    avg_scores = {**avg_algo, **avg_judge}

    print(f"\nResults for {name} ({elapsed:.0f}s):")
    for key, score in sorted(avg_scores.items()):
        print(f"  {key:<35} {score:.4f}")

    # Sample output for inspection
    if example_outputs[0].get("segments"):
        count = len(example_outputs[0]["segments"])
        print(f"  segment_count (example 1): {count}")

    return {
        "experiment": name,
        "model": model,
        "temperature": temperature,
        "elapsed_seconds": round(elapsed, 1),
        "avg_scores": avg_scores,
        "sample_segment_count": len(example_outputs[0].get("segments", [])),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Local Segmentation Evaluation (no LangSmith required)")
    print(f"Script: {len(SCRIPT)} chars")
    print(f"Reference segments: {len(REFERENCE_SEGMENTATION)}")
    print(f"Experiments: {len(EXPERIMENT_CONFIGS)}")
    print(f"Examples per experiment: {len(INPUTS)}")

    all_results = []

    for i, config in enumerate(EXPERIMENT_CONFIGS, 1):
        print(f"\n[{i}/{len(EXPERIMENT_CONFIGS)}] Starting...")
        try:
            summary = run_experiment(config)
            all_results.append(summary)
        except Exception as exc:
            print(f"  ERROR: {exc}")
            all_results.append({
                "experiment": f"{config['model']}_t{config['temperature']}",
                "model": config["model"],
                "temperature": config["temperature"],
                "error": str(exc),
            })

        if i < len(EXPERIMENT_CONFIGS):
            time.sleep(1)

    # Save results
    output = {
        "experiments": all_results,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset": "local_evaluation",
        "total_experiments": len(all_results),
        "reference_segment_count": len(REFERENCE_SEGMENTATION),
    }
    RESULTS_FILE.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"\nResults saved to: {RESULTS_FILE}")

    # Final ranking
    ranked = [r for r in all_results if "avg_scores" in r]
    ranked.sort(
        key=lambda r: r["avg_scores"].get("boundary_similarity", 0.0),
        reverse=True,
    )

    print(f"\n{'=' * 75}")
    print("RANKING by boundary_similarity (higher = closer to ground truth)")
    print(f"{'=' * 75}")
    print(f"{'#':<3} {'Experiment':<35} {'boundary':>8} {'exact':>7} {'count':>7} {'segs':>5} {'time':>6}")
    print("-" * 75)
    for rank, r in enumerate(ranked, 1):
        s = r["avg_scores"]
        boundary = s.get("boundary_similarity", 0.0)
        exact = s.get("exact_text_match", 0.0)
        count = s.get("segment_count_match", 0.0)
        segs = r.get("sample_segment_count", "?")
        elapsed = r.get("elapsed_seconds", "?")
        print(f"{rank:<3} {r['experiment']:<35} {boundary:>8.4f} {exact:>7.4f} {count:>7.4f} {segs:>5} {elapsed:>5}s")

    if ranked:
        winner = ranked[0]
        print(f"\nWINNER: {winner['experiment']}")
        print(f"  boundary_similarity: {winner['avg_scores'].get('boundary_similarity', 0):.4f}")
        print(f"  judge_overall:       {winner['avg_scores'].get('judge_overall', 'N/A')}")
        print(f"  elapsed:             {winner['elapsed_seconds']}s")


if __name__ == "__main__":
    main()

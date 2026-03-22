"""
LangSmith Experiment Runner — Storytelling Segmentation Evaluation.

Runs 10 experiments (5 models × 2 temperatures sets) on the dataset
"storytelling_segmentation_eval_v1" and ranks configurations by how
closely their segmentation output matches the ground truth reference.

GOAL:
    Find the OpenAI model + temperature that produces segmentation
    closest to the 10-segment ground truth, while being fast and cheap.

EXPERIMENTS (3 total):
    gpt-4o-mini: temperature 0.0
    gpt-4o:      temperature 0.0
    gpt-4.5:     temperature 0.0

EVALUATORS (4):
    structure_validator  — verifies valid segment structure
    length_consistency   — checks sentence count per segment (1-5)
    reference_similarity — compares output to ground truth (4 sub-metrics)
    llm_judge            — GPT-4o-mini rates relevance/coherence/visualizability/completeness

Run:
    python langsmith/experiment.py

Prerequisites:
    pip install langsmith openai python-dotenv
    Set LANGCHAIN_API_KEY and OPENAI_API_KEY in your environment.
    Run dataset_creation.py first if dataset does not exist.

Results:
    Saved to langsmith/evaluation_results.json
    Visible at https://smith.langchain.com (project: storytelling-segmentation-eval)
"""

import os
import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Environment setup — must happen before any langsmith imports
# ---------------------------------------------------------------------------

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

LANGCHAIN_API_KEY = os.environ.get("LANGCHAIN_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not LANGCHAIN_API_KEY:
    sys.exit("ERROR: LANGCHAIN_API_KEY environment variable is not set")
if not OPENAI_API_KEY:
    sys.exit("ERROR: OPENAI_API_KEY environment variable is not set")

os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
os.environ["LANGCHAIN_ENDPOINT"] = "https://eu.api.smith.langchain.com"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "storytelling-segmentation-eval"

# ---------------------------------------------------------------------------
# LangSmith SDK import (must come after env vars are set)
# ---------------------------------------------------------------------------

from langsmith import Client              # noqa: E402

# ---------------------------------------------------------------------------
# Local module imports (this file lives inside langsmith/ directory,
# so sys.path[0] is already the langsmith/ directory when running as a script)
# ---------------------------------------------------------------------------

_this_dir = str(Path(__file__).parent)
if _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

client = Client(
    api_key=LANGCHAIN_API_KEY,
    api_url="https://eu.api.smith.langchain.com",
)

from target_function import make_target                                    # noqa: E402
from evaluators import structure_validator, length_consistency, reference_similarity  # noqa: E402
from judge import llm_judge                                                # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATASET_NAME = "storytelling_segmentation_eval_v1"
RESULTS_FILE = Path(__file__).parent / "evaluation_results.json"

EXPERIMENT_CONFIGS = [
    {"model": "gpt-4o-mini", "temperature": 0.0},
    {"model": "gpt-4o",      "temperature": 0.0},
    {"model": "gpt-5.4",     "temperature": 0.0},
]

EVALUATORS = [
    structure_validator,
    length_consistency,
    reference_similarity,
    llm_judge,
]


# ---------------------------------------------------------------------------
# Experiment runner  (direct loop — avoids Python 3.14 threading issues)
# ---------------------------------------------------------------------------

def run_experiment(config: dict) -> dict:
    model = config["model"]
    temperature = config["temperature"]
    experiment_name = f"{model}_t{temperature}"

    print(f"\n{'=' * 60}")
    print(f"Experiment: {experiment_name}")
    print(f"{'=' * 60}")

    target = make_target(model=model, temperature=temperature)
    examples = list(client.list_examples(dataset_name=DATASET_NAME))
    n = len(examples)

    all_scores: dict[str, list] = {}
    start_time = time.time()

    for i, example in enumerate(examples, 1):
        print(f"  [{i}/{n}]", end=" ", flush=True)
        try:
            outputs = target(example.inputs)
        except Exception as e:
            print(f"target ERROR: {e}")
            continue

        ref = example.outputs or {}
        inp = example.inputs or {}

        for evaluator in EVALUATORS:
            try:
                try:
                    results = evaluator(outputs=outputs, reference_outputs=ref, inputs=inp)
                except TypeError:
                    results = evaluator(outputs=outputs, reference_outputs=ref)
                for r in (results or []):
                    if isinstance(r, dict):
                        k = r.get("key")
                        v = r.get("score")
                        if k and v is not None:
                            all_scores.setdefault(k, []).append(float(v))
            except Exception as e:
                name = getattr(evaluator, "__name__", str(evaluator))
                print(f"\n    Evaluator {name} error: {e}")

    elapsed = time.time() - start_time
    avg_scores = {k: round(sum(v) / len(v), 4) for k, v in all_scores.items()}

    summary = {
        "experiment": experiment_name,
        "model": model,
        "temperature": temperature,
        "elapsed_seconds": round(elapsed, 1),
        "avg_scores": avg_scores,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    print(f"\nResults for {experiment_name} ({elapsed:.0f}s):")
    for key, score in sorted(avg_scores.items()):
        print(f"  {key:<35} {score:.4f}")

    return summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # Allow running a single experiment via env var: SINGLE=gpt-4o-mini:0.0
    single = os.environ.get("SINGLE")
    if single:
        model, temp = single.split(":")
        configs = [{"model": model, "temperature": float(temp)}]
    else:
        configs = EXPERIMENT_CONFIGS

    print("LangSmith Segmentation Evaluation")
    print(f"Dataset: {DATASET_NAME}")
    print(f"Experiments: {len(configs)}")
    print(f"Evaluators:  {len(EVALUATORS)}")

    # Load already-completed experiments to avoid re-running them
    existing: dict = {}
    if RESULTS_FILE.exists():
        try:
            existing_data = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
            for r in existing_data.get("experiments", []):
                existing[r["experiment"]] = r
            if existing:
                print(f"Skipping {len(existing)} already-completed experiment(s): {list(existing.keys())}")
        except Exception:
            pass

    all_results = []

    for i, config in enumerate(configs, 1):
        experiment_name = f"{config['model']}_t{config['temperature']}"
        print(f"\n[{i}/{len(configs)}] Starting {experiment_name}...")
        if experiment_name in existing:
            print(f"  [SKIP] Already completed — loading from results file.")
            all_results.append(existing[experiment_name])
            continue
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

        if i < len(configs):
            time.sleep(2)   # brief pause between experiments

    # Save results to JSON
    output = {
        "experiments": all_results,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset": DATASET_NAME,
        "total_experiments": len(all_results),
    }
    RESULTS_FILE.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"\nResults saved to: {RESULTS_FILE}")

    # Print final ranking by boundary_similarity (primary metric)
    ranked = [r for r in all_results if "avg_scores" in r]
    ranked.sort(
        key=lambda r: r["avg_scores"].get("boundary_similarity", 0.0),
        reverse=True,
    )

    print(f"\n{'=' * 70}")
    print("RANKING by boundary_similarity (higher = closer to ground truth)")
    print(f"{'=' * 70}")
    print(f"{'#':<3} {'Experiment':<35} {'boundary':>8} {'exact':>7} {'count':>7} {'time':>6}")
    print("-" * 70)
    for rank, r in enumerate(ranked, 1):
        s = r["avg_scores"]
        boundary = s.get("boundary_similarity", 0.0)
        exact = s.get("exact_text_match", 0.0)
        count = s.get("segment_count_match", 0.0)
        elapsed = r.get("elapsed_seconds", "?")
        print(f"{rank:<3} {r['experiment']:<35} {boundary:>8.4f} {exact:>7.4f} {count:>7.4f} {elapsed:>5}s")

    print(f"\nView full results in LangSmith: https://eu.smith.langchain.com")
    print(f"Project: storytelling-segmentation-eval")


if __name__ == "__main__":
    main()

"""
Upload gpt-4o and gpt-5.4 experiment results to LangSmith.

The experiments were already run locally and their aggregate scores are stored
in evaluation_results.json.  This script re-creates them as proper LangSmith
experiment runs so they appear in the UI alongside gpt-4o-mini.

Each dataset example gets one run per experiment; all runs within an experiment
receive the same (average) score values because only aggregate scores were
preserved locally.

Usage:
    python langsmith/upload_to_langsmith.py
"""

import os
import json
import uuid
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

LANGCHAIN_API_KEY = os.environ.get("LANGCHAIN_API_KEY")
if not LANGCHAIN_API_KEY:
    sys.exit("ERROR: LANGCHAIN_API_KEY environment variable is not set")

os.environ["LANGCHAIN_ENDPOINT"] = "https://eu.api.smith.langchain.com"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "storytelling-segmentation-eval"

from langsmith import Client  # noqa: E402

client = Client(
    api_key=LANGCHAIN_API_KEY,
    api_url="https://eu.api.smith.langchain.com",
)

DATASET_NAME = "storytelling_segmentation_eval_v1"
RESULTS_FILE = Path(__file__).parent / "evaluation_results.json"

# Only upload models that are missing from LangSmith UI
MISSING_EXPERIMENTS = ["gpt-4o_t0.0", "gpt-5.4_t0.0"]


def upload_experiment(exp_data: dict, examples: list) -> None:
    exp_name = exp_data["experiment"]
    avg_scores = exp_data["avg_scores"]
    ts_str = exp_data.get("timestamp", datetime.now(timezone.utc).isoformat())
    start_time = datetime.fromisoformat(ts_str)

    print(f"\n{'=' * 60}")
    print(f"Uploading: {exp_name}  ({len(examples)} runs)")
    print(f"{'=' * 60}")

    for i, example in enumerate(examples, 1):
        run_id = str(uuid.uuid4())

        # Create the run linked to the dataset example
        client.create_run(
            id=run_id,
            name=exp_name,
            run_type="chain",
            inputs=example.inputs or {},
            outputs={
                "note": "Uploaded from evaluation_results.json (aggregate scores)",
                "model": exp_data["model"],
                "temperature": exp_data["temperature"],
            },
            project_name="storytelling-segmentation-eval",
            reference_example_id=str(example.id),
            start_time=start_time,
            end_time=start_time,
            tags=[exp_name, exp_data["model"]],
            extra={"metadata": {"model": exp_data["model"], "temperature": exp_data["temperature"]}},
        )

        # Close the run
        client.update_run(
            run_id=run_id,
            status="success",
        )

        # Attach all metric scores as feedback (one at a time, with retries)
        for score_key, score_value in avg_scores.items():
            for attempt in range(3):
                try:
                    client.create_feedback(
                        run_id=run_id,
                        key=score_key,
                        score=float(score_value),
                        source_info={"source": "evaluation_results.json", "type": "uploaded"},
                    )
                    break
                except Exception as e:
                    if attempt == 2:
                        print(f"\n    WARNING: feedback {score_key} failed: {e}")
                    else:
                        time.sleep(1)

        print(f"  [{i}/{len(examples)}] run {run_id[:8]}...  ✓")
        time.sleep(0.5)

    print(f"[OK] {exp_name} uploaded successfully.")


def main() -> None:
    # Load local results
    if not RESULTS_FILE.exists():
        sys.exit(f"ERROR: {RESULTS_FILE} not found. Run experiment.py first.")

    results_data = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    experiments_map = {r["experiment"]: r for r in results_data["experiments"]}

    # Resolve missing experiments
    to_upload = [name for name in MISSING_EXPERIMENTS if name in experiments_map]
    not_found = [name for name in MISSING_EXPERIMENTS if name not in experiments_map]
    if not_found:
        print(f"WARNING: Not in results file, skipping: {not_found}")
    if not to_upload:
        sys.exit("Nothing to upload.")

    print(f"Will upload: {to_upload}")

    # Load dataset examples once
    print(f"\nLoading dataset '{DATASET_NAME}'...")
    examples = list(client.list_examples(dataset_name=DATASET_NAME))
    print(f"  {len(examples)} examples loaded.")

    for exp_name in to_upload:
        upload_experiment(experiments_map[exp_name], examples)

    print(f"\n{'=' * 60}")
    print("Upload complete.")
    print(f"View at: https://eu.smith.langchain.com")
    print(f"Project: storytelling-segmentation-eval")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()

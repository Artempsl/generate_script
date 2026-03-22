"""
LangSmith Dataset Creation for Storytelling Segmentation Evaluation.

Creates dataset: "storytelling_segmentation_eval_v1"
- 10 identical examples (same script, same reference segmentation)
- Controlled comparison across model/temperature configurations

Run ONCE before experiments:
    python langsmith/dataset_creation.py
"""

import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

LANGCHAIN_API_KEY = os.environ.get("LANGCHAIN_API_KEY")
if not LANGCHAIN_API_KEY:
    sys.exit("ERROR: LANGCHAIN_API_KEY environment variable is not set")

LANGCHAIN_ENDPOINT = "https://eu.api.smith.langchain.com"

os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
os.environ["LANGCHAIN_ENDPOINT"] = LANGCHAIN_ENDPOINT

from langsmith import Client  # noqa: E402 — must be after env setup

DATASET_NAME = "storytelling_segmentation_eval_v1"
DATASET_DESCRIPTION = (
    "Evaluation dataset for storytelling script segmentation. "
    "10 identical examples to enable controlled comparison across "
    "model/temperature configurations."
)

SCRIPT = (
    "Alex had always believed that his life would follow a predictable path. "
    "Every morning he woke up at the same time, took the same route to work, "
    "and greeted the same people with the same polite smile. "
    "There was comfort in this routine, a quiet reassurance that nothing "
    "unexpected would disrupt his carefully constructed world.\n\n"
    "One evening, as he was walking home, something unusual caught his attention. "
    "A small, dimly lit bookstore stood between two modern buildings, a place he "
    "was certain had never been there before. The sign above the door flickered "
    "slightly, as if inviting him inside.\n\n"
    "Curiosity overcame him, and Alex stepped into the shop. The air inside felt "
    "heavy with the scent of old paper. Shelves stretched from floor to ceiling, "
    "filled with books that looked ancient and untouched.\n\n"
    "Behind the counter stood an elderly man, watching Alex with a calm expression. "
    "Without saying a word, the man pointed to a single book on the table. "
    "Alex hesitated before picking it up.\n\n"
    "As soon as his fingers touched the cover, everything changed. The noise of "
    "the street disappeared, and he found himself somewhere else.\n\n"
    "He stood in a vast open field under a sky filled with impossible colors. "
    "In the distance, strange structures shimmered. "
    "A feeling of fear and excitement filled him.\n\n"
    "Then he realized something unsettling. "
    "He was not just observing this world \u2014 he was part of it.\n\n"
    "A voice echoed around him, telling him that every choice he had avoided had "
    "led him here. Now, he had a chance to choose differently.\n\n"
    "Alex stood still. His old life was still within reach. But this new world "
    "offered something else \u2014 uncertainty and possibility.\n\n"
    "For the first time in years, he smiled. "
    "Then he stepped forward into the unknown."
)

REFERENCE_SEGMENTATION = [
    {
        "index": 1,
        "text": (
            "Alex had always believed that his life would follow a predictable path. "
            "Every morning he woke up at the same time, took the same route to work, "
            "and greeted the same people with the same polite smile. "
            "There was comfort in this routine, a quiet reassurance that nothing "
            "unexpected would disrupt his carefully constructed world."
        ),
    },
    {
        "index": 2,
        "text": (
            "One evening, as he was walking home, something unusual caught his attention. "
            "A small, dimly lit bookstore stood between two modern buildings, a place he "
            "was certain had never been there before. The sign above the door flickered "
            "slightly, as if inviting him inside."
        ),
    },
    {
        "index": 3,
        "text": (
            "Curiosity overcame him, and Alex stepped into the shop. "
            "The air inside felt heavy with the scent of old paper. "
            "Shelves stretched from floor to ceiling, filled with books that looked "
            "ancient and untouched."
        ),
    },
    {
        "index": 4,
        "text": (
            "Behind the counter stood an elderly man, watching Alex with a calm expression. "
            "Without saying a word, the man pointed to a single book on the table. "
            "Alex hesitated before picking it up."
        ),
    },
    {
        "index": 5,
        "text": (
            "As soon as his fingers touched the cover, everything changed. "
            "The noise of the street disappeared, and he found himself somewhere else."
        ),
    },
    {
        "index": 6,
        "text": (
            "He stood in a vast open field under a sky filled with impossible colors. "
            "In the distance, strange structures shimmered. "
            "A feeling of fear and excitement filled him."
        ),
    },
    {
        "index": 7,
        "text": (
            "Then he realized something unsettling. "
            "He was not just observing this world \u2014 he was part of it."
        ),
    },
    {
        "index": 8,
        "text": (
            "A voice echoed around him, telling him that every choice he had avoided "
            "had led him here. Now, he had a chance to choose differently."
        ),
    },
    {
        "index": 9,
        "text": (
            "Alex stood still. His old life was still within reach. "
            "But this new world offered something else \u2014 uncertainty and possibility."
        ),
    },
    {
        "index": 10,
        "text": (
            "For the first time in years, he smiled. "
            "Then he stepped forward into the unknown."
        ),
    },
]


def create_dataset() -> None:
    client = Client(api_key=LANGCHAIN_API_KEY, api_url=LANGCHAIN_ENDPOINT)

    # Check if dataset already exists
    existing = list(client.list_datasets(dataset_name=DATASET_NAME))
    if existing:
        ds = existing[0]
        print(f"Dataset '{DATASET_NAME}' already exists (ID: {ds.id}).")
        print("Delete it manually in LangSmith UI if you want to recreate it.")
        return

    # Create dataset
    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description=DATASET_DESCRIPTION,
    )
    print(f"Created dataset: '{DATASET_NAME}' (ID: {dataset.id})")

    # Add 10 identical examples
    inputs = [
        {"script": SCRIPT, "metadata": {"genre": "fantasy", "duration": 4}}
        for _ in range(10)
    ]
    outputs = [
        {"segments": REFERENCE_SEGMENTATION}
        for _ in range(10)
    ]

    client.create_examples(
        inputs=inputs,
        outputs=outputs,
        dataset_id=dataset.id,
    )
    print(f"Added 10 examples to dataset '{DATASET_NAME}'.")
    print(f"View at: https://eu.smith.langchain.com/datasets/{dataset.id}")


if __name__ == "__main__":
    create_dataset()

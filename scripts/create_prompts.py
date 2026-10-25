import json
from pathlib import Path


output = Path("data/prompts.jsonl")

topics = [
    "machine learning",
    "python",
    "data science",
    "deep learning",
    "neural networks",
    "NLP",
    "cloud computing",
    "databases",
    "Linux",
    "MLOps",
]


with output.open("w", encoding="utf-8") as f:

    for i in range(10_000):

        topic = topics[i % len(topics)]

        prompt = {
            "id": i,
            "prompt": (
                f"Explain {topic} in simple terms. "
                f"Give one practical example."
            ),
        }

        f.write(
            json.dumps(prompt)
            + "\n"
        )


print(f"Created {output}")
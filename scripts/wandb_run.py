import os
import time
import wandb
from dotenv import load_dotenv

load_dotenv()

run = wandb.init(
    project=os.getenv("WANDB_PROJECT", "nemotron-small-practice"),
    entity=os.getenv("WANDB_ENTITY") or None,
    mode=os.getenv("WANDB_MODE", "offline"),
    config={
        "model": os.getenv("MODEL_NAME", "distilgpt2"),
        "profile": "local-small",
        "container": os.getenv("NGC_IMAGE") or "local-python",
        "device": os.getenv("MODEL_DEVICE", "cpu"),
    },
)

for step in range(5):
    wandb.log({
        "step": step,
        "demo_loss": 1.0 / (step + 1),
        "tokens_per_second": 10 + step,
    })
    time.sleep(0.1)

run.finish()
print("W&B run complete.")

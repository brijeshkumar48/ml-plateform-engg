import random
import wandb


run = wandb.init(
    entity="surendradalsingaryadav-practice",
    project="nemotron-small-practice",
    config={
        "model": "distilgpt2",
        "parameters": "~82M",
        "architecture": "small-language-model",
        "dataset": "practice",
        "epochs": 5,
        "profile": "local-small",
        "container": "local-python",
    },
)


for epoch in range(1, 6):

    accuracy = (
        0.70
        + epoch * 0.04
        + random.random() * 0.01
    )

    loss = (
        1.0 / epoch
        + random.random() * 0.02
    )

    run.log(
        {
            "epoch": epoch,
            "accuracy": accuracy,
            "loss": loss,
        }
    )


run.finish()

print("W&B test completed successfully.")


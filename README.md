# Nemotron / NVIDIA Small-Model Practice Project

Laptop-friendly practice project that mirrors the architecture of the larger
Nemotron 3 Nano MVP without requiring a billion-parameter model or H200 cluster.

Default model: `distilgpt2` (~82M parameters).

## Setup

If starting from scratch:

```bash
- uv init
- uv python install 3.12
- uv python pin 3.12
- uv venv
- source .venv/bin/activate
- uv add fastapi uvicorn httpx transformers torch pydantic python-dotenv wandb
- uv sync
```

Copy environment settings:

```bash
cp .env.example .env
```

Validate all profiles:

```bash
uv run python scripts/test_env_profiles.py
```

Run the small model locally:

```bash
uv run python scripts/run_model.py
```

Start API:

```bash
uv run uvicorn serving.server:app --host 127.0.0.1 --port 8014
```

In another terminal:

```bash
uv run python scripts/test_api.py
uv run python scripts/benchmark.py --n 10
```

W&B practice:

```bash
uv run python scripts/wandb_run.py
```

For offline W&B, keep `WANDB_MODE=offline`.

## NGC

Set the exact NVIDIA image/tag approved by your architect:

```bash
export NGC_IMAGE="nvcr.io/<namespace>/<image>:<tag>"
```

Authenticate using your NGC account and approved credential method, then:

```bash
bash scripts/pull_ngc_image.sh
```

Do not put an NGC API key in source code or `.env` committed to Git.

## Architecture

```text
NGC
  |
  v
NVIDIA container
  |
  v
Small model (~82M)
  |
  +--> local API
  +--> benchmark
  +--> W&B
  |
  v
env.toml
  +--> local-small
  +--> sft-small
  +--> rl-small
  +--> eval-small
```

The container is the software environment; model weights are separate.

The local profiles demonstrate configuration. They do not pretend to provide
real Slurm nodes.

## Production mapping

```text
local-small -> dev-2n
sft-small   -> sft-16n
rl-small    -> rl-20n
eval-small  -> eval-2n

local API       -> Run:ai serving
local filesystem-> Lustre
local process   -> Slurm
local W&B       -> production W&B lineage
```

Real H200 training, multi-node Slurm, Lustre, and Run:ai still require the
actual cluster.

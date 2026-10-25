# Practice project task map

| Real MVP responsibility | Practice project |
|---|---|
| Pull/squash NVIDIA containers | `scripts/pull_ngc_image.sh` |
| env.toml profiles | `config/env.toml` |
| Profile validation | `scripts/test_env_profiles.py` |
| Model execution | `scripts/run_model.py` |
| Model serving | `serving/server.py` |
| Throughput benchmark | `scripts/benchmark.py` |
| W&B lineage | `scripts/wandb_run.py` |
| Checkpoint policy | `scripts/checkpoint_policy.py` |
| Disk alarm | `scripts/disk_check.py` |

Local proof:
Python inference, API serving, benchmark, W&B metadata, profile validation,
and NGC container pull if Docker/NGC access are available.

Cluster-only proof:
Slurm allocation, multi-node execution, Lustre, Run:ai, H200-scale training,
and production checkpoint storage.

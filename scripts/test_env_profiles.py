from pathlib import Path
import tomllib

CONFIG = Path(__file__).resolve().parents[1] / "config" / "env.toml"
REQUIRED = {
    "executor", "nodes", "gpus_per_node", "container",
    "mounts", "account", "partition", "time"
}

with CONFIG.open("rb") as f:
    data = tomllib.load(f)

profiles = ["local-small", "sft-small", "rl-small", "eval-small"]

for name in profiles:
    if name not in data:
        raise SystemExit(f"Missing profile: {name}")
    missing = REQUIRED - set(data[name])
    if missing:
        raise SystemExit(f"{name}: missing {sorted(missing)}")
    print(f"\n=== {name} ===")
    for key in REQUIRED:
        print(f"{key}: {data[name][key]}")
    print("STATUS: VALID")

print("\nAll four local profiles are structurally valid.")

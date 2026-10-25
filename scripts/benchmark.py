import json
import os
import time
from pathlib import Path

import requests
import wandb

BASE_DIR = Path(__file__).resolve().parents[1]
PROMPTS_FILE = BASE_DIR / "data" / "prompts.jsonl"

API_URL = os.getenv(
    "MODEL_API_URL",
    "http://127.0.0.1:8014/v1/chat/completions",
)
MODEL_NAME = os.getenv("MODEL_NAME", "distilgpt2")
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "32"))
LOG_EVERY = max(1, int(os.getenv("LOG_EVERY", "100")))

# Set BENCHMARK_LIMIT=100 for a quick test.
# Leave unset or set to 0 to process the complete dataset.
BENCHMARK_LIMIT = int(os.getenv("BENCHMARK_LIMIT", "0"))

CONNECT_TIMEOUT = float(os.getenv("BENCHMARK_CONNECT_TIMEOUT", "5"))
READ_TIMEOUT = float(os.getenv("BENCHMARK_READ_TIMEOUT", "45"))


def load_prompts():
    prompts = []

    with PROMPTS_FILE.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                print(f"Skipping invalid JSON on line {line_number}: {exc}")
                continue

            if isinstance(item, str):
                prompt = item
            elif isinstance(item, dict):
                prompt = (
                    item.get("prompt")
                    or item.get("text")
                    or item.get("content")
                )
            else:
                prompt = None

            if isinstance(prompt, str) and prompt.strip():
                prompts.append(prompt.strip())

    if not prompts:
        raise ValueError(f"No valid prompts found in {PROMPTS_FILE}")

    if BENCHMARK_LIMIT > 0:
        prompts = prompts[:BENCHMARK_LIMIT]

    return prompts


def main():
    prompts = load_prompts()

    run = wandb.init(
        project=os.getenv(
            "WANDB_PROJECT", "nemotron-small-practice"
        ),
        entity=os.getenv(
            "WANDB_ENTITY", "surendradalsingaryadav-practice"
        ),
        job_type="inference-benchmark",
        config={
            "model": MODEL_NAME,
            "api_url": API_URL,
            "dataset": str(PROMPTS_FILE.name),
            "prompt_count": len(prompts),
            "max_new_tokens": MAX_NEW_TOKENS,
            "profile": "local-small",
            "device": "cpu",
            "connect_timeout_seconds": CONNECT_TIMEOUT,
            "read_timeout_seconds": READ_TIMEOUT,
            "benchmark_limit": BENCHMARK_LIMIT,
        },
    )

    completed = 0
    failed = 0
    blank_responses = 0
    total_output_tokens = 0
    total_latency = 0.0
    successful_latencies = []
    start_time = time.perf_counter()

    try:
        with requests.Session() as session:
            for index, prompt in enumerate(prompts, start=1):
                request_start = time.perf_counter()
                request_ok = False

                try:
                    response = session.post(
                        API_URL,
                        json={
                            "model": MODEL_NAME,
                            "messages": [
                                {"role": "user", "content": prompt}
                            ],
                            "max_tokens": MAX_NEW_TOKENS,
                        },
                        timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
                    )
                    response.raise_for_status()
                    result = response.json()

                    content = result["choices"][0]["message"]["content"]

                    if not isinstance(content, str) or not content.strip():
                        failed += 1
                        blank_responses += 1
                        print(f"Request {index}: blank response")
                    else:
                        completed += 1
                        request_ok = True

                    usage = result.get("usage", {})
                    total_output_tokens += int(
                        usage.get("completion_tokens", 0) or 0
                    )

                except (
                    requests.RequestException,
                    ValueError,
                    KeyError,
                    IndexError,
                    TypeError,
                ) as exc:
                    failed += 1
                    print(
                        f"Request {index} failed: "
                        f"{type(exc).__name__}: {exc}"
                    )

                finally:
                    latency = time.perf_counter() - request_start
                    total_latency += latency

                    if request_ok:
                        successful_latencies.append(latency)

                if index % LOG_EVERY == 0 or index == len(prompts):
                    elapsed = time.perf_counter() - start_time

                    run.log(
                        {
                            "benchmark/requests_processed": index,
                            "benchmark/requests_completed": completed,
                            "benchmark/requests_failed": failed,
                            "benchmark/blank_responses": blank_responses,
                            "benchmark/average_latency_seconds": (
                                total_latency / index
                            ),
                            "benchmark/average_success_latency_seconds": (
                                sum(successful_latencies)
                                / len(successful_latencies)
                                if successful_latencies else 0
                            ),
                            "benchmark/elapsed_seconds": elapsed,
                            "benchmark/requests_per_second": (
                                index / elapsed if elapsed else 0
                            ),
                            "benchmark/output_tokens": total_output_tokens,
                            "benchmark/output_tokens_per_second": (
                                total_output_tokens / elapsed
                                if elapsed else 0
                            ),
                            "benchmark/success_rate_percent": (
                                completed / index * 100 if index else 0
                            ),
                        },
                        step=index,
                    )

                    print(
                        f"{index}/{len(prompts)} processed | "
                        f"completed={completed} | failed={failed} | "
                        f"elapsed={elapsed:.1f}s"
                    )

        elapsed = time.perf_counter() - start_time

        run.summary["benchmark/final_requests_processed"] = len(prompts)
        run.summary["benchmark/final_requests_completed"] = completed
        run.summary["benchmark/final_requests_failed"] = failed
        run.summary["benchmark/final_blank_responses"] = blank_responses
        run.summary["benchmark/final_elapsed_seconds"] = elapsed
        run.summary["benchmark/final_success_rate_percent"] = (
            completed / len(prompts) * 100 if prompts else 0
        )
        run.summary["benchmark/final_output_tokens"] = total_output_tokens
        run.summary["benchmark/final_output_tokens_per_second"] = (
            total_output_tokens / elapsed if elapsed else 0
        )

        print("\n=== Benchmark summary ===")
        print(f"Prompts processed: {len(prompts)}")
        print(f"Completed: {completed}")
        print(f"Failed: {failed}")
        print(f"Blank responses: {blank_responses}")
        print(f"Elapsed seconds: {elapsed:.2f}")
        print(f"Output tokens: {total_output_tokens}")
        print(
            "Output tokens/sec: "
            f"{total_output_tokens / elapsed if elapsed else 0:.2f}"
        )
        print(f"W&B run: {run.url}")

    except KeyboardInterrupt:
        elapsed = time.perf_counter() - start_time
        print("\nBenchmark interrupted by user.")

        run.summary["benchmark/interrupted"] = True
        run.summary["benchmark/requests_processed_at_interrupt"] = (
            completed + failed
        )
        run.summary["benchmark/requests_completed_at_interrupt"] = completed
        run.summary["benchmark/requests_failed_at_interrupt"] = failed
        run.summary["benchmark/elapsed_seconds_at_interrupt"] = elapsed

    finally:
        run.finish()


if __name__ == "__main__":
    main()

# Nemotron Small Practice: Local Testing vs Production

**Purpose:** Compare the current Windows practice project with the
production ODC/Slurm target, and provide a file-by-file run flow.

> **Important:** The local project uses `distilgpt2` on a Windows CPU
> and includes mock services. It is a practice implementation, not a
> production Nemotron 3 Nano deployment.

## 1. Current setup vs production

  -----------------------------------------------------------------------
  Area                    Local testing           Production target
  ----------------------- ----------------------- -----------------------
  Machine                 Windows, PowerShell,    Approved ODC Linux
                          CPU                     environment with H200
                                                  GPUs

  Model                   `distilgpt2` (\~82M     Approved Nemotron
                          parameters)             model/checkpoint

  Container               Local Docker smoke test Approved NeMo/NeMo-RL
                          with Ubuntu             image, staged as
                                                  `.sqsh` on Lustre if
                                                  required

  Scheduler               Manual local commands   NeMo-Run submitting
                                                  jobs to Slurm

  Storage                 Local project folders   Lustre for containers,
                                                  datasets, checkpoints,
                                                  logs and artifacts

  Profiles                Script checks config    Profiles actually
                          structure               submit jobs with the
                                                  requested resources

  Serving                 Local FastAPI           Approved model-serving
                                                  platform, such as
                                                  Run:ai where required

  W&B                     Practice metrics and    Traceable production
                          config                  runs: model, dataset,
                                                  image, config, code
                                                  revision, artifacts and
                                                  metrics

  Operations              Local checkpoint/disk   Retention enforced on
                          scripts                 real checkpoints and
                                                  alerts connected to
                                                  production storage

  Judge/reward            Heuristic/mock APIs     Actual approved models
                                                  and tested endpoints

  Sandbox                 Syntax validation only  Isolated code execution
                                                  with security/resource
                                                  controls and
                                                  concurrency tests
  -----------------------------------------------------------------------

### What the local project proves

-   `uv` environment and dependency setup.
-   Loading a small Hugging Face model and generating text.
-   Running a FastAPI endpoint.
-   Sending prompts and measuring local request behavior.
-   Logging metrics/configuration to W&B.
-   Basic Docker pull/start behavior and profile-file validation.

### What it does not prove

-   Nemotron runs inside the production container.
-   A `.sqsh` image works on Lustre and exposes GPUs on a compute node.
-   NeMo-Run successfully submits jobs to Slurm.
-   Production W&B lineage is complete.
-   Real teacher/judge/reward services are deployed.
-   Checkpoint retention and Lustre alerts are enforced.
-   The sandbox safely executes untrusted code or supports 50 concurrent
    executions.

## 2. File groups and what must change

### Task 1 --- Infrastructure and containers

  -----------------------------------------------------------------------------
  File                          Current role            Production change
  ----------------------------- ----------------------- -----------------------
  `scripts/pull_ngc_image.sh`   Pulls a Docker image    Use approved NGC image
                                and optionally attempts and credentials;
                                Enroot `.sqsh`          validate conversion,
                                conversion              Lustre staging,
                                                        permissions, image
                                                        identity and GPU
                                                        visibility on ODC

  `config/env.toml`             Contains                Confirm container
                                local/cluster-style     paths, Lustre mounts,
                                execution profiles      account, partition,
                                                        nodes, GPUs and time
                                                        limits with the cluster
                                                        owner
  -----------------------------------------------------------------------------

**Production gate:** approved container starts on a compute node and GPU
visibility is verified.

### Task 2 --- Tooling, profiles and W&B lineage

  --------------------------------------------------------------------------------
  File                             Current role            Production change
  -------------------------------- ----------------------- -----------------------
  `config/env.toml`                Defines profiles such   Validate against the
                                   as `dev-2n`, `sft-16n`, actual NeMo-Run
                                   `rl-20n`, `eval-2n`     executor and cluster
                                                           conventions

  `configs/model.yaml`             Local model settings    Use approved
                                                           model/checkpoint
                                                           references and
                                                           production parameters

  `scripts/test_env_profiles.py`   Checks profile          Add a real
                                   structure               NeMo-Run/Slurm smoke
                                                           submission; parsing
                                                           alone is not enough

  `scripts/test_wandb.py`          Tests W&B logging       Log actual model,
                                                           dataset version,
                                                           profile, image, code
                                                           revision, metrics and
                                                           artifacts
  --------------------------------------------------------------------------------

**Production gate:** a real profile submits a job and its W&B run can be
traced to the exact inputs and outputs.

### Task 3 --- Serving and performance benchmark

  --------------------------------------------------------------------------------
  File                          Current role            Production change
  ----------------------------- ----------------------- --------------------------
  `scripts/run_model.py`        Loads `distilgpt2` and  Use the approved Nemotron
                                generates text          checkpoint and launch
                                                        method

  `serving/server.py`           Local FastAPI           Add production model
                                chat-completion         loading, readiness/health,
                                endpoint                validation, timeouts,
                                                        concurrency controls,
                                                        access control and
                                                        structured logs

  `scripts/test_api.py`         Tests a local API       Test status, response
                                request                 content, errors, timeouts
                                                        and load

  `scripts/create_prompts.py`   Generates the           Use approved
                                10,000-prompt workload  representative/versioned
                                                        prompts and follow
                                                        data-handling rules

  `data/prompts.jsonl`          Local benchmark input   Stage approved workload
                                                        data in the designated
                                                        location

  `scripts/benchmark.py`        Sends requests and logs Benchmark the real
                                results to W&B          endpoint; record latency
                                                        percentiles, request/token
                                                        throughput, failures,
                                                        blank responses,
                                                        concurrency, model and
                                                        hardware details
  --------------------------------------------------------------------------------

**Production gate:** repeatable results exist for the actual deployed
model and target hardware.

### Task 4 --- Checkpoint retention and storage

  --------------------------------------------------------------------------------
  File                             Current role            Production change
  -------------------------------- ----------------------- -----------------------
  `scripts/checkpoint_policy.py`   Tests intended policy,  Integrate with the real
                                   including               checkpoint save
                                   `keep_top_k=10` and     lifecycle; test
                                   `save_period`           retention and recovery

  `scripts/disk_check.py`          Checks local disk usage Monitor the correct
                                   and warning threshold   Lustre filesystem and
                                                           connect the 80%
                                                           threshold to an
                                                           approved alerting
                                                           channel
  --------------------------------------------------------------------------------

**Production gate:** retention actually applies to training checkpoints
and the storage alert is tested end-to-end.

### Task 5 --- Judge, reward, embedding and sandbox

  ------------------------------------------------------------------------
  File                     Current role            Production change
  ------------------------ ----------------------- -----------------------
  `serving/judge.py`       Heuristic judge API     Replace heuristic with
                                                   approved judge model

  `serving/reward.py`      Heuristic reward API    Replace heuristic with
                                                   approved reward model

  `serving/embedding.py`   Sentence Transformers   Pin the approved model;
                           embedding API           validate vector
                                                   dimensions, quality and
                                                   serving performance

  `serving/sandbox.py`     Validates code syntax;  Use a security-reviewed
                           does not execute it     isolated execution
                                                   service with strict
                                                   CPU, memory, time and
                                                   concurrency limits
  ------------------------------------------------------------------------

**Production gate:** approved models are deployed and the sandbox
isolation/concurrency requirements are demonstrated.

### Supporting files

  -----------------------------------------------------------------------
  File/path                           Purpose
  ----------------------------------- -----------------------------------
  `pyproject.toml`                    Project metadata and dependencies

  `uv.lock`                           Locked dependency resolution

  `.env`                              Local variables/secrets; never
                                      commit

  `.env.example`                      Safe list of required variable
                                      names

  `.gitignore`                        Excludes local secrets,
                                      environments and generated files

  `README.md`                         Setup/runbook

  `wandb/`                            Local W&B run files

  `reports/`                          Intended benchmark report output

  `checkpoints/`                      Intended local checkpoint output

  `artifacts/containers/`             Intended container artifact
                                      location; Docker pull alone may not
                                      populate it
  -----------------------------------------------------------------------

## 3. Local execution flow (PowerShell)

Run from the project root:

`C:\Users\yadav\Documents\projects\backend\nemotron-small-practice`

### Step 0 --- Synchronize dependencies

``` powershell
uv sync
```

### Step 1 --- Check profiles

``` powershell
uv run python scripts/test_env_profiles.py
```

This checks local profile structure; it does not submit Slurm jobs.

### Step 2 --- Test local model generation

``` powershell
uv run python scripts/run_model.py
```

This uses `distilgpt2`, not Nemotron.

### Step 3 --- Start FastAPI (Terminal 1)

``` powershell
uv run uvicorn serving.server:app --host 127.0.0.1 --port 8014
```

### Step 4 --- Check health and API (Terminal 2)

``` powershell
Invoke-RestMethod http://127.0.0.1:8014/health
uv run python scripts/test_api.py
```

### Step 5 --- Create prompt data

``` powershell
uv run python scripts/create_prompts.py
```

Check that `data/prompts.jsonl` exists and has the expected
format/count.

### Step 6 --- Run a small benchmark first

``` powershell
$env:BENCHMARK_LIMIT = "100"
uv run python scripts/benchmark.py
```

Inspect W&B for success/failure counts, blank outputs, latency and
throughput. Confirm the benchmark points at the intended local endpoint.

### Step 7 --- Run the full benchmark only when the small run is stable

``` powershell
$env:BENCHMARK_LIMIT = "0"
uv run python scripts/benchmark.py
```

In this project, `0` means no limit if that behavior remains in the
script. A 10,000-request CPU test can take hours.

### Step 8 --- Check checkpoint and disk helper scripts

``` powershell
uv run python scripts/checkpoint_policy.py
uv run python scripts/disk_check.py
```

These are local checks until integrated with real training and Lustre.

### Step 9 --- Compile supporting service files

``` powershell
uv run python -m py_compile serving\server.py serving\judge.py serving\reward.py serving\embedding.py serving\sandbox.py
```

Configured local ports: - Main API: `8014` - Judge: `8015` - Reward:
`8016` - Embedding: `8017` - Sandbox: `8018`

Start/test each service separately. The sandbox only validates syntax;
it is not safe execution of untrusted code.

### Step 10 --- Inspect W&B

Open the project:

https://wandb.ai/surendradalsingaryadav-practice/nemotron-small-practice

Check run config, metrics, exit status and summary. Demo/simulated
metrics must not be represented as real training results. Keep W&B keys
in environment variables or the approved secret store.

## 4. Production execution flow

Exact commands depend on approved ODC paths, cluster account/partition,
container runtime and NeMo-Run version. Confirm these with the
platform/cluster owner.

### Phase A --- Infrastructure

1.  Confirm NGC/JFrog access and approved image references.
2.  Confirm ODC access, account, partition and network requirements.
3.  Confirm Lustre paths for containers, datasets, checkpoints, logs and
    artifacts.
4.  Use the approved Docker-to-`.sqsh`/Enroot process if required.
5.  Start a small compute-node smoke job and verify the approved
    container sees GPUs.

**Gate:** container and GPU checks pass on the target compute node.

### Phase B --- Real profiles and scheduling

1.  Update `config/env.toml` with reviewed `dev-2n`, `sft-16n`, `rl-20n`
    and `eval-2n` settings.
2.  Validate node/GPU counts, account, partition, wall time, mounts and
    container paths.
3.  Submit a real smoke job through NeMo-Run to Slurm.
4.  Verify job state, logs, outputs and W&B association.

**Gate:** the intended profile completes a real scheduled job.

### Phase C --- Training/evaluation and lineage

1.  Run the approved data-curation stage and version the dataset.
2.  Submit the team-owned pretraining/SFT/RL/evaluation jobs.
3.  Record model, dataset, image, profile, code revision, config,
    metrics and artifacts in W&B.
4.  Save checkpoints and artifacts to approved storage.
5.  Confirm another engineer can reproduce the run inputs and identify
    its outputs.

**Gate:** a completed run has traceable, real lineage.

### Phase D --- Production serving and benchmark

1.  Deploy the actual teacher model through the approved serving
    platform.
2.  Verify readiness, health and inference correctness.
3.  Run a small representative batch, then the approved 10,000-prompt
    workload.
4.  Capture latency percentiles, request/token throughput, errors, blank
    outputs, concurrency, model version, hardware and serving config.
5.  Use measured throughput to estimate the prompt/data-generation
    timeline.

**Gate:** repeatable benchmark results exist for the actual model and
hardware.

### Phase E --- Operations and supporting services

1.  Integrate `keep_top_k=10` and `save_period` into the real checkpoint
    writer and test recovery.
2.  Connect the 80% storage threshold to the correct Lustre filesystem
    and approved alert channel.
3.  Deploy approved judge/reward/embedding models with health checks and
    monitoring.
4.  Replace the syntax-only sandbox with isolated execution.
5.  Test the required concurrency target, including at least 50
    concurrent sandbox executions if that remains the requirement.

**Gate:** retention, alerting, service behavior, sandbox isolation and
concurrency are verified in production.

## 5. Production-readiness checklist

-   [ ] Approved image and image identifier/digest recorded
-   [ ] Container staged on Lustre and accessible from compute nodes
-   [ ] GPU visibility validated inside the approved container
-   [ ] NeMo-Run profile submits a real Slurm job
-   [ ] Dataset, model, config, image and code revision recorded in W&B
-   [ ] Actual serving endpoint passes health and inference tests
-   [ ] 10K-prompt benchmark completed with interpretable metrics
-   [ ] Checkpoint retention and recovery tested
-   [ ] Lustre 80% alert tested end-to-end
-   [ ] Judge/reward/embedding use approved models and are monitored
-   [ ] Sandbox isolation and required concurrency validated
-   [ ] Secrets, access, logs and rollback follow platform policy

## 6. Mental model: file run flow

``` text
LOCAL PRACTICE
uv sync
  -> test_env_profiles.py
  -> run_model.py
  -> serving/server.py
  -> test_api.py
  -> create_prompts.py
  -> benchmark.py
  -> W&B charts
  -> checkpoint_policy.py / disk_check.py
  -> test supporting services

PRODUCTION
Approved access + image + Lustre paths
  -> stage/validate container on compute node
  -> env.toml + NeMo-Run profile
  -> real Slurm smoke job
  -> data/config/model pipeline
  -> training/evaluation + checkpoints + W&B lineage
  -> deploy actual teacher/judge/reward/embedding services
  -> benchmark actual endpoint and hardware
  -> retention + storage alerts + sandbox security/concurrency tests
```

## Final takeaway

Use the Windows project to develop scripts and interfaces quickly. Treat
production container validation, real NeMo-Run/Slurm jobs, approved
model deployment, Lustre operations, and production W&B lineage as
separate integration milestones. Do not mark a production task complete
based only on a local mock or configuration check.

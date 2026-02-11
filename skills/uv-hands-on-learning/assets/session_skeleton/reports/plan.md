# Experiment plan

Link to repo analysis: `../../repo_analysis.md`.

## Goal (one sentence)

{goal}

## Hypotheses

- {hypothesis_1}
- {hypothesis_2}

## Workload matrix

| Workload | Batch | Seq len | Dtype | Notes |
| --- | --- | --- | --- | --- |
| prefill | 1 | 1024 in / 1 out | fp16 | cold vs warm |
| decode | 16 | 128 in / 32 out | fp16 | kv_len sweep |
| kv-append | 32 | N/A | fp16 | page size sweep |

## Metrics

- TTFT / prefill latency
- ITL (inter-token latency)
- throughput (tokens/s)
- VRAM footprint

## Baselines

- Baseline A: repo-provided example (known-good)
- Baseline B: smallest ungated model or minimal microbench (for fast iteration)

## Execution policy

- Every run must save raw output under `results/`.
- Every run must be listed in `report.md` with:
  - the exact command,
  - a short summary,
  - and evidence paths.


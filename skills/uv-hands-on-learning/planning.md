# Planning

## Non-negotiables

- Plan must be testable: hypotheses are falsifiable.
- Plan must be runnable: commands exist, inputs are specified, outputs are captured.
- Plan must include a baseline (even if it’s “this repo’s built-in example”).
- Plan must specify what to do when blocked (errors + unblock steps).

## Convert vague goals into tracking requirements

User says: “Understand FlashInfer performance”.

Translate into:

- scope: prefill vs decode vs KV-cache ops
- workloads: batch size, sequence lengths, dtype
- evidence: which trace/log/metric confirms the claim

## Workload matrix template

Use a small matrix first (3–6 runs), then expand.

```markdown
## Workload matrix

| Workload | Batch | Seq len | Dtype | Notes |
| --- | --- | --- | --- | --- |
| prefill | 1 | 1024 in / 1 out | fp16 | cold vs warm |
| decode | 16 | 128 in / 32 out | fp16 | kv_len sweep |
| kv-append | 32 | N/A | fp16 | page_size sweep |
```

## Metrics (pick only what you can actually measure)

- TTFT / prefill latency
- ITL (inter-token latency) for decode
- tokens/s (steady-state)
- VRAM and KV-cache footprint
- kernel-level time for hot ops (optional, requires `ncu`)

## Evidence capture rules

For every run, record:

- exact command line
- exact model/input config
- start/end timestamps
- where raw logs live (path under `results/`)

Then summarize in the report:

- what happened,
- what you expected,
- what surprised you,
- what to do next.

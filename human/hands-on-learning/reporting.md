# Reporting

The report is the product. Raw logs/traces are supporting evidence.

## What “good” looks like

Bad:

- “Throughput is 1000 tokens/s.”

Good:

- “First decode step is 20x slower due to cold module load; steady-state ITL stabilizes after 5 steps.”
- “KV length increases cause linear growth in decode kernel time; memory bandwidth dominates.”

## Report structure (`reports/report.md`)

Use this as a minimum:

1) **What I ran**: a table of runs with command + result + evidence paths  
2) **Observations**: concrete events tied to evidence (log lines, trace screenshots, metrics)  
3) **Root cause hypotheses**: what explains the events (and what would disprove it)  
4) **Next steps**: 3–5 actions, ordered, each with a command or file pointer

## Evidence policy

- Tracked report should include small excerpts (a few lines) plus links to raw logs under `results/`.
- If the run fails, record:
  - the exact error text,
  - the exact command,
  - and the unblock plan.

## Common failure modes in reports

- Missing command lines.
- Missing environment details (GPU/driver/CUDA/tooling).
- No evidence paths (can’t verify claims).
- No baselines (can’t interpret “fast/slow”).

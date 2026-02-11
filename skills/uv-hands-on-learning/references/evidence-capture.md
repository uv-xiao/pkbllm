# Evidence capture patterns

## Rule

If a run happened, there must be a file on disk that proves it happened.

## Recommended layout

Keep raw outputs under `results/` (gitignored) and keep summaries under `reports/` (tracked).

Examples of “raw outputs”:

- stdout/stderr logs
- JSON requests/responses
- `nsys` traces (`.nsys-rep`)
- `ncu` reports
- screenshots (if needed)

## Minimal pattern (stdout/stderr)

```bash
mkdir -p results/logs
python your_script.py {args...} |& tee results/logs/run_$(date -u +%Y%m%dT%H%M%SZ).log
```

In `reports/report.md`, include:

- the exact command line,
- a short excerpt from the log,
- and the path to the saved log.

## “Run table” pattern

Your report should include a table like:

```markdown
| Date | Command | Result summary | Evidence |
| --- | --- | --- | --- |
| 2026-02-11 | python bench.py --bs 16 | ITL ~ 8.7ms | `results/logs/run_20260211T014417Z.log` |
```


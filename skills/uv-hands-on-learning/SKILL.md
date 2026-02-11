---
name: uv-hands-on-learning
description: Run a structured hands-on exploration session for an ML/LLM repository (setup, environment detection, experiment plan, execution, profiling, and reporting). Use when you want to validate performance claims, identify bottlenecks, reproduce benchmarks, or turn repo analysis into concrete experiments stored alongside the repo analysis report.
---

# Hands-on learning (session-based)

Create a session under the same research folder as `uv-repo-analysis`, with scripts, results (gitignored), and reports.

This skill is intentionally process-heavy: the outcome should include **real running evidence** and be reviewable by another
engineer later.

## Non-negotiables (requirements)

- **Analyze first**: link to a filled `repo_analysis.md` (file:line pointers, not hand-waving).
- **Evidence-first**: every claim in `reports/report.md` must point to evidence (log snippet + `results/...` path).
- **No “trust me”**: if you didn’t run it, say you didn’t run it. If it failed, capture the real error and unblock plan.
- **Reproducibility**: record commit/versions, commands, and key configs.
- **No placeholder stubs**: don’t leave template markers like `<...>` in tracked reports.

## Output locations (pkbllm convention)

- **Tracked outputs**: `$HUMAN_MATERIAL_PATH/research/<repo_slug>/hands_on/<session>/reports/`
- **Scripts**: `$HUMAN_MATERIAL_PATH/research/<repo_slug>/hands_on/<session>/scripts/`
- **Local results** (gitignored by materials repo): `$HUMAN_MATERIAL_PATH/research/<repo_slug>/hands_on/<session>/results/`

Use `$HUMAN_MATERIAL_PATH/.references/repos/` for clones (configurable).

## Directory structure (required)

Your session directory must look like:

```
hands_on/<session>/
├── .gitignore                   # ignores results/
├── scripts/                     # runnable scripts and helpers
├── results/                     # raw logs/traces (gitignored)
└── reports/                     # tracked markdown reports
    ├── INDEX.md                 # navigation / “what to read first”
    ├── environment.md           # environment capture + raw evidence links
    ├── plan.md                  # hypotheses + workload matrix
    └── report.md                # what actually happened
```

## Quick start

Create a session (also clones if needed):

```bash
# Run from this skill directory (the folder containing this SKILL.md):
python scripts/init_hands_on_session.py https://github.com/vllm-project/vllm
```

This copies a session skeleton from `assets/session_skeleton/` into the new session directory **without overwriting existing files**.

## Session workflow (default)

1. **Analyze first**: run `uv-repo-analysis` and link your session to `repo_analysis.md`.
2. **Detect environment**: capture GPU/CPU/tooling availability into `reports/environment.md`.
   - Recommended: `bash scripts/capture_environment.sh` (writes raw evidence into `results/`).
3. **Write an experiment plan** in `reports/plan.md`:
   - hypotheses (what you expect to be slow/fast)
   - workload matrix (batch, seq len, model size, dtype, kv-cache mode)
   - metrics (latency, throughput, memory, stalls)
   - baselines
4. **Execute** with incremental scope:
   - minimal “hello world” run
   - one controlled workload
   - expand matrix
5. **Report** in `reports/report.md`:
   - what happened (not just final numbers)
    - event-level observations (kernel/operator level if possible)
    - actionable next steps

## Profiling guidance (optional)

Use whatever exists on the machine:

- If `nsys` exists: system-level traces (CUDA + CPU)
- If `ncu` exists: kernel-level metrics
- Otherwise: `torch.profiler`, `py-spy`, and log instrumentation

Record commands + summaries in the session report.

Convenience wrappers copied into each new session:

- `bash scripts/profile_nsys.sh python your_script.py {args...}`
- `bash scripts/profile_ncu.sh python your_microbench.py {args...}`

## Review policy (must follow)

Before saying a session is “done”, perform a self-review pass:

- `reports/environment.md` includes toolchain + package versions and links to raw evidence in `results/`.
- `reports/plan.md` has falsifiable hypotheses and a small runnable workload matrix (not a wish list).
- `reports/report.md` has a “What I ran” table with exact commands and evidence paths.
- If any run failed, the report includes the **full error** plus unblock steps.

Use the `uv-verification-before-completion` mindset: evidence before claims.

## Common pitfalls (avoid)

- Mixing “local clone” vs “installed wheel” without recording which one you used.
- Not saving raw outputs (can’t verify later).
- Benchmarking before you can run a minimal smoke.
- Profiling a full server first (too much noise); start with microbenches.

## Modules (read when needed)

- Environment checklist: `environment.md`
- Analysis-first checklist: `analysis-first.md`
- Planning guidance: `planning.md`
- Profiling guidance: `profiling.md`
- Reporting requirements: `reporting.md`
- Evidence capture patterns: `references/evidence-capture.md`
- Workload matrix examples: `references/workload-matrix-examples.md`

## Integration

Prerequisites / follow-ups:
- Use `uv-repo-analysis` first to know *what* to profile and *where* the hot paths are.
- Use `uv-tutorial-generator` after the session to convert findings into teachable material under `$HUMAN_MATERIAL_PATH/exercises/`.
- If you add/change these workflows, run `uv-bootstrap-skill-linking`.

---
name: uv-hands-on-learning
description: Run a structured hands-on exploration session for an ML/LLM repository (setup, environment detection, experiment plan, execution, profiling, and reporting). Use when you want to validate performance claims, identify bottlenecks, reproduce benchmarks, or turn repo analysis into concrete experiments stored alongside the repo analysis report.
---

# Hands-on learning (session-based)

Create a hands-on session under the same research folder as `uv-repo-analysis`, with scripts, results (gitignored), and reports.

## Output locations (pkbllm convention)

- **Tracked outputs**: `$HUMAN_MATERIAL_PATH/research/<repo_slug>/hands_on/<session>/reports/`
- **Scripts**: `$HUMAN_MATERIAL_PATH/research/<repo_slug>/hands_on/<session>/scripts/`
- **Local results** (gitignored by materials repo): `$HUMAN_MATERIAL_PATH/research/<repo_slug>/hands_on/<session>/results/`

Use `$HUMAN_MATERIAL_PATH/.references/repos/` for clones (configurable).

## Quick start

Create a session (also clones if needed):

```bash
python human/hands-on-learning/scripts/init_hands_on_session.py https://github.com/vllm-project/vllm
```

## Session workflow (default)

1. **Analyze first**: run `uv-repo-analysis` and link your session to `repo_analysis.md`.
2. **Detect environment**: capture GPU/CPU/tooling availability into `reports/environment.md`.
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

## Integration

Prerequisites / follow-ups:
- Use `uv-repo-analysis` first to know *what* to profile and *where* the hot paths are.
- Use `uv-tutorial-generator` after the session to convert findings into teachable material under `$HUMAN_MATERIAL_PATH/exercises/`.
- If you add/change these workflows, run `uv-bootstrap-skill-linking`.


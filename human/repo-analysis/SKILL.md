---
name: uv-repo-analysis
description: Analyze a code repository to understand architecture, key components, data flow, and extension points. Use when onboarding to an unfamiliar repo, preparing a hands-on profiling session, or extracting LLM-specific implementation details (attention/KV cache/scheduler/decoding) after determining the repo is LLM-related.
---

# Repo analysis (LLM-aware)

Produce a high-signal repository analysis that a human can read quickly and use to drive implementation, debugging, and profiling.

## Non-negotiables (requirements)

- The report must be actionable: it includes real paths and **file:line pointers** (not vague descriptions).
- If LLM-related, the report must separate **prefill vs decode**, and include KV cache + scheduler + sampling surfaces.
- No placeholder markers like `<...>` may remain in tracked output.

## Output locations (pkbllm convention)

- **Tracked output**: `$HUMAN_MATERIAL_PATH/research/<repo_slug>/repo_analysis.md`
- **Local clone** (gitignored, configurable): `$HUMAN_MATERIAL_PATH/.references/repos/<repo_slug>/`

Config precedence (repo overrides user):
1. `$HUMAN_MATERIAL_PATH/.agents/config.toml`
2. `~/.agents/config.toml`

## Quick start

Initialize workspace + clone (if needed):

```bash
# Run from this skill directory (the folder containing this SKILL.md):
python scripts/init_repo_analysis.py https://github.com/vllm-project/vllm
```

This prints:
- local clone path
- report path

## What to produce (`repo_analysis.md`)

Use the template at `assets/repo_analysis_template.md` and fill:

1. **TL;DR**: what the repo is, who it’s for, why it’s interesting.
2. **Architecture map**: a single diagram + a module table.
3. **Primary workflows**:
   - installation/build
   - primary entrypoints (CLI/server/train)
   - configuration surface
4. **Key components** (with file paths + line numbers):
   - runtime loop(s)
   - state/data structures
   - error handling + logging
5. **Extension points**: where you would add a feature safely.
6. **Risks / pitfalls**: things that will waste time.

## LLM-specific deep dive (only if LLM-related)

First decide whether the repo is LLM-related using signals like:
- mentions of: prefill/decode, KV cache, paged attention, continuous batching, speculative decoding
- model families: llama/gpt/transformer
- serving surfaces: OpenAI-compatible server, tokenizer, sampling params

If it’s LLM-related, add these sections (template includes stubs):

- **Prefill vs decode loop** (pseudocode with the real loop nesting)
- **KV cache**: layout, paging, updates, eviction, memory accounting
- **Scheduler/batching**: queue, priorities, chunking, preemption
- **Sampling/decoding**: logits processing, temperature/top-p/top-k, repetition penalties
- **Parallelism**: tensor/pipeline/sequence parallel, comms hotspots
- **Kernel hotspots**: attention, GEMMs, layernorm, quantization paths

## Recommended repo-reading commands

Use these patterns to locate the “real” implementation:

```bash
rg -n \"main\\(|if __name__ == '__main__'|typer\\.run|argparse\" .
rg -n \"prefill|decode|kv cache|scheduler|continuous batching|paged\" -S .
rg -n \"sample\\(|logits|temperature|top_p|top_k\" -S .
rg -n \"flash(attn|infer)|attention kernel|triton|cuda\" -S .
```

More query snippets:

- `references/rg-queries.md`

## Integration

Prerequisites / follow-ups:
- If you will run experiments or profiling, use `uv-hands-on-learning` after this analysis.
- If you want to teach the repo’s internals, use `uv-tutorial-generator` and base it on the analysis + hands-on results.
- If you add/change these workflows, run `uv-bootstrap-skill-linking` to keep relationships consistent.

## Review policy

Before calling a repo analysis “done”, use:

- Review checklist: `review.md`
- Pitfalls list: `pitfalls.md`

### Subagent review gates (recommended)

If you have subagent tooling available, add two explicit review gates before calling it “done”:

1) **Gate 1 — Spec compliance**: verify the analysis meets the “Non-negotiables” and matches the template expectations (no placeholders, real file:line pointers, LLM sections present when applicable).
2) **Gate 2 — Quality**: verify the document is readable, actionable, and would let a second engineer run and extend the repo without guesswork.

Prompt templates:
- Gate 1: `reviewer-prompts/spec-compliance-reviewer.md`
- Gate 2: `reviewer-prompts/quality-reviewer.md`

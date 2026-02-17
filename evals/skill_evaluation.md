# Skill evaluation (pkbllm)

This repo treats skills as **testable interfaces**: each skill should reliably trigger when appropriate, avoid triggering when inappropriate, and produce outputs that match repo conventions.

This folder defines a systematic evaluation mechanism based on the pattern described in OpenAI’s “Testing Agent Skills Systematically with Evals” (Jan 22, 2026):

> prompt(s) → captured run (trace + artifacts) → deterministic checks → rubric grading → comparable score over time

Generated outputs always go to `artifacts/skill-evals/` (gitignored).

---

## Goals (what we measure)

Keep checks small and must-pass. Split requirements into:

- **Outcome goals**: did the task complete (or correctly *not* run for negative controls)?
- **Process goals**: did the agent behave as if it followed the skill’s intended workflow (verification-first, required steps, etc.)?
- **Style goals**: does the output match conventions (paths, structure, naming)?
- **Efficiency goals**: did it avoid thrashing (excessive commands/loops)?

---

## Artifacts and evidence

Each eval case produces a directory:

`artifacts/skill-evals/<run-id>/work/<skill-slug>/<case-id>/`

Common files:

- `trace.jsonl`: JSONL event stream from `codex exec --json` (tool calls, command executions, etc.)
- `final.txt`: last assistant message (optionally schema-constrained JSON)
- `stderr.txt`: codex stderr (helps debug failures)
- `grade.json`: deterministic grading results
- `judge.json`: optional rubric grading output (schema-constrained)
- `meta.json`: case metadata (prompt, should_trigger, etc.)

Why JSONL matters: deterministic graders should rely on **what actually happened**, not vibes.

---

## Eval case format (per-skill)

Curated cases live under:

`evals/skills/<skill-slug>/prompts.csv`

Minimum columns:

- `id`: stable case id
- `should_trigger`: `true` or `false`
- `prompt`: the prompt to run

Optional columns supported by the runner:

- `sandbox`: `read-only` or `workspace-write`
- `timeout_s`: per-case timeout
- `max_commands`: fail if more than this many commands executed
- `max_input_tokens`: fail if trace usage exceeds this (best-effort)
- `max_output_tokens`: fail if trace usage exceeds this (best-effort)
- `max_total_tokens`: fail if trace usage exceeds this (best-effort; input+output)
- `output_schema`: path to a JSON Schema (runner passes `--output-schema`)
- `judge`: `true/false` for whether to run the rubric judge for this case
- `require_files`: `;`-separated list of required relative paths
- `must_include`: `|`-separated regex patterns that must match `final.txt`
- `must_not_include`: `|`-separated regex patterns that must not match `final.txt`
- `fixture`: relative path under `evals/skills/<skill-slug>/` copied into the case directory before execution

Recommended baseline coverage per skill:

- **Explicit invocation**: prompt names `$uv-skill-name`
- **Implicit invocation**: prompt describes the situation without naming the skill
- **Negative control**: adjacent/unrelated prompt that should not match

Add new cases whenever you hit a real failure or regression.

---

## Deterministic vs rubric grading

### Deterministic grading (default)

Fast, explainable, and debuggable:

- exit code
- command count / max commands (the harness reports both `command_count_total` and `command_count_effective`; the effective count ignores read-only commands that simply open injected `SKILL.md` from the skills snapshot)
- token usage (best-effort extraction from `turn.completed` usage records in the JSONL trace)
- required files exist
- required/forbidden patterns in the final response
- structured-output sanity (when an output schema is used): `invoked_skills` must include (or exclude) the skill under test based on `should_trigger`

These checks are sufficient for many regression signals and are ideal for CI-safe linting and quick local iterations.

### Rubric grading (optional judge pass)

Some requirements are qualitative (trigger correctness, workflow discipline, style). For those, add a **second, read-only grading run**:

- the harness runs a judge prompt in the same case directory
- output is constrained by `evals/schemas/style_rubric.schema.json`
- the judge should reference trace evidence and on-disk artifacts

Rubric grading is slower/costlier but provides higher confidence where deterministic checks can’t express intent.

---

## How to run

Static linting (CI-safe, no LLM calls):

```bash
python bootstrap/scripts/lint_skills.py --check-evals
```

Recommended CI policy:

- Run `lint_skills.py --check-evals` (fast, deterministic).
- Do **not** run `run_skill_evals.py` in CI by default (it requires an agent runtime + credentials and will be slow/costly).
- Maintain a separate “eval runner” machine/job that has `codex` configured and runs LLM-backed evals on demand (or nightly).

LLM-backed evals (developer machine with `codex` configured). By default, curated cases set `judge=true` so rubric grading runs unless you disable it:

```bash
python bootstrap/scripts/run_skill_evals.py --suite explicit --max-cases 1 --write-progress
```

With rubric judge:

```bash
python bootstrap/scripts/run_skill_evals.py --suite explicit --max-cases 1 --judge --write-progress
```

Fast runs (skip rubric judge):

```bash
python bootstrap/scripts/run_skill_evals.py --suite smoke --no-judge --write-progress
```

Background run (detached; writes progress files under `artifacts/skill-evals/<run-id>/`):

```bash
python bootstrap/scripts/run_skill_evals.py --suite smoke --background
```

Check status:

```bash
python bootstrap/scripts/run_skill_evals.py --status --run-id <run-id>
```

---

## Guidance for skill authors (make skills testable)

- Include a **definition of done** in the skill body when the skill expects file outputs or commands.
- Prefer small, bounded workflows; avoid “do everything” instructions.
- Put heavy downloads/clones under `$HUMAN_MATERIAL_PATH/.references/` and keep them optional.
- For evalability, provide at least one “dry-run” mode where the skill can respond with steps + verifications without executing anything.
- Add negative controls: if your skill overlaps with adjacent requests, explicitly say when *not* to use it.

---

## References

- OpenAI dev blog: “Testing Agent Skills Systematically with Evals” (Jan 22, 2026): https://developers.openai.com/blog/eval-skills/
- OpenAI: “Introducing Structured Outputs” (JSON Schema constrained responses): https://openai.com/index/introducing-structured-outputs-in-the-api/
- Promptfoo: evaluate coding agents (trace + rubric patterns): https://www.promptfoo.dev/docs/guides/evaluate-coding-agents/
- Microsoft Research: Agent-Pex (agent testing + evaluation): https://www.microsoft.com/en-us/research/project/agent-pex-automated-evaluation-and-testing-of-ai-agents/
- LangSmith: multi-turn / online evaluations: https://docs.langchain.com/langsmith/online-evaluations-multi-turn

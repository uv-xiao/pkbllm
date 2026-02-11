# Review policy

## What counts as “done”

A repo analysis is “done” when another engineer can:

1) identify the primary entrypoints and run the system,  
2) locate the real hot paths (with file:line pointers), and  
3) design a hands-on session (workload matrix + hypotheses) without guesswork.

## Evidence requirements

- Code claims must include **file:line pointers**.
- If you cite behavior (“does X during decode”), include either:
  - code pointers showing the behavior, or
  - hands-on evidence (link to a session report and a `results/...` log/trace).

## Self-review checklist

- No placeholder markers like `<...>` remain.
- TL;DR is specific (names loops, components, and why it matters).
- “Key components” table has at least 6–10 rows with `{path:line}` pointers.
- If LLM-related: prefill/decode + KV cache + scheduler + sampling are present and grounded in code.

## Quick placeholder scan (recommended)

Run this against the tracked report before review:

```bash
rg -n \"\\{[a-zA-Z0-9_]+\\}|<\\.\\.\\.>\" \"$HUMAN_MATERIAL_PATH/research/<repo_slug>/repo_analysis.md\" -S
```

## Subagent review gates (recommended)

If you have subagent tooling available, use two review passes:

1) **Spec compliance** using `reviewer-prompts/spec-compliance-reviewer.md`
2) **Quality/actionability** using `reviewer-prompts/quality-reviewer.md`

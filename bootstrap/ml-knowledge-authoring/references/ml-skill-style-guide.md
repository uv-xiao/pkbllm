# ML knowledge skill style guide (pkbllm)

This file is intentionally short and copy-ready.

## Naming

- Skill frontmatter `name:` must start with `uv-`.
- Skill folder name should be short and stable (no versions).

## Frontmatter template

```yaml
---
name: uv-<skill-slug>
description: "<what it is>. Use when <trigger phrases and contexts>."
license: MIT
tags: [Tag, Tag]
dependencies: [optional, list]
---
```

## Body template

```markdown
# <Skill title>

## Quick start

## When to use

## Core concepts

## Workflows

## Pitfalls

## References
```

## “When to use” patterns

Good triggers (copy the shape):
- “Use when deploying `<framework>` in production and tuning throughput/latency.”
- “Use when debugging multi-GPU hangs, OOMs, or divergence in `<stack>`.”
- “Use when implementing `<algorithm>` from paper `<X>` and validating assumptions.”

Avoid:
- “Use when you want to learn about X” (too broad)

## What to include (high-signal checklist)

- At least one runnable minimal snippet (CLI or code).
- 1–2 checklists for common workflows.
- 5+ concrete pitfalls with diagnostics and fixes.
- Primary references (official docs, paper, canonical repo).

## What to avoid

- Copying full upstream docs into the skill.
- Huge link lists with no guidance.
- Multiple overlapping skills for the same tool (prefer improving existing).


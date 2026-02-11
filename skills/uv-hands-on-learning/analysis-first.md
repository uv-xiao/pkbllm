# Analysis-first strategy

Running benchmarks without knowing the code is expensive noise. This module is a checklist for “understand before running”.

## Goal

Turn “I want to understand performance” into:

- which loops to profile,
- which configs matter,
- what you expect to see (hypotheses),
- and what evidence will confirm/deny it.

## 15-minute quick scan (before any run)

```bash
# Surface area
ls -la
rg -n "if __name__ == .__main__.|main\\(|argparse|typer|click" -S .

# LLM signals
rg -n "prefill|decode|kv cache|paged|scheduler|batching|continuous batching" -S .
rg -n "sampling|logits|temperature|top_p|top_k|repetition" -S .
rg -n "triton|cuda|cudnn|flashinfer|flashattn|cutlass" -S .
```

Write down:

- 2–3 primary entrypoints (CLI/server/scripts),
- the “real” runtime loop file(s),
- and where config is parsed (args/env/config files).

## Map features → evidence you need

For each suspected performance driver, write:

- feature: {what it is}
- where in code: `{path:line}`
- evidence: {what output/trace/log would prove it matters}

Example:

```text
feature: paged KV cache append cost
where: src/cache/paged.py:123
evidence: ncu kernel time dominates in decode loop when kv_len grows
```

## Deliverable

Your hands-on `reports/plan.md` should explicitly reference the analysis (file:line pointers) and turn them into measurable runs.

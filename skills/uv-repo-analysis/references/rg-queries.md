# Repo-reading query snippets

These are starting points for finding “the real loop” quickly.

## Entrypoints

```bash
rg -n "if __name__ == .__main__.|main\\(|typer\\.run|argparse|click\\.command" -S .
```

## LLM signals

```bash
rg -n "prefill|decode|kv cache|paged|scheduler|continuous batching" -S .
rg -n "sampling|logits|temperature|top_p|top_k|repetition" -S .
```

## Kernel backends

```bash
rg -n "triton|cuda|cudnn|flashinfer|flash(attn|attention)|cutlass" -S .
```


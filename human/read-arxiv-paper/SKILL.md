---
name: uv-read-arxiv-paper
description: "Download and deeply read an arXiv paper (given an arXiv URL or id), then write a clear human-facing report with strong storytelling and logical reasoning. Use when asked to summarize/review an arXiv paper, extract key ideas, connect them to practice, and produce a report under $HUMAN_MATERIAL_PATH/research/<paper_slug>/report.md. Stores downloads under $HUMAN_MATERIAL_PATH/.references/ (configurable via $HUMAN_MATERIAL_PATH/.agents/config.toml or ~/.agents/config.toml)."
---

# Read an arXiv paper (deep report)

## Output locations (pkbllm convention)

- **Tracked output** (write here): `$HUMAN_MATERIAL_PATH/research/<paper_slug>/`
  - `report.md` (main deliverable)
  - `figures/` (optional images/diagrams)
- **Local downloads** (gitignored, configurable): `$HUMAN_MATERIAL_PATH/.references/`
  - PDFs default: `.references/pdfs/`
  - Sources default: `.references/arxiv/`
  - Cloned repos default: `.references/repos/`

Config precedence (repo overrides user):
1. `$HUMAN_MATERIAL_PATH/.agents/config.toml`
2. `~/.agents/config.toml`

## Quick start

1) Download paper assets:

```bash
python skills/uv-read-arxiv-paper/scripts/download_arxiv.py https://arxiv.org/abs/2601.07372
```

2) Extract the TeX source:

```bash
python skills/uv-read-arxiv-paper/scripts/extract_arxiv_source.py 2601.07372
```

3) Write the report:

- Create `$HUMAN_MATERIAL_PATH/research/<paper_slug>/`
- Start from `skills/uv-read-arxiv-paper/assets/report_template.md`
- Fill it with a coherent story:
  - What problem is being solved and why now?
  - What is the key trick (the one idea that makes it work)?
  - What are the assumptions and failure modes?
  - What to implement first if we were to reproduce it?

## Workflow (recommended)

1. **Normalize the paper id** from the URL (keep the version if present; it’s fine).
2. **Download PDF + source** into `.references/` using the provided scripts.
3. **Unpack sources** into `.references/arxiv/<arxiv_id>/` and locate the LaTeX entrypoint (`main.tex`, etc.).
4. **Read in passes**:
   - Pass 1: abstract + intro + figures (build the mental model)
   - Pass 2: method (write down the algorithm precisely)
   - Pass 3: experiments (what matters, what doesn’t)
   - Pass 4: limitations + related work (what breaks, what’s missing)
5. **Produce a report** under `$HUMAN_MATERIAL_PATH/research/<paper_slug>/report.md`:
   - Use the template (copy it and fill it)
   - Prefer concrete examples, small equations, and “why this design” explanations
   - Include at least one visual explanation if it helps (optionally generate via `uv-scientific-schematics`)


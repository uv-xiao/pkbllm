# Human

Skills for creating and managing human-facing materials (slides, manuscripts, exercises).

## Structure

| Path | What it contains |
| --- | --- |
| `human/slider/` | Imported skills from uv-xiao/slider |

## <TABLE>
<!-- PKBLLM_TABLE_START -->
| Path | Type | Description |
| --- | --- | --- |
| `exercises/` | group | (2 skill(s)) |
| `hands-on-learning/` | skill | Run a structured hands-on exploration session for an ML/LLM repository (setup, environment detection, experiment plan, execution, profiling, and reporting). Use when you want to validate performance claims, identify bottlenecks, reproduce benchmarks, or turn repo analysis into concrete experiments stored alongside the repo analysis report. |
| `init-human-material-repo/` | skill | Initialize a dedicated HUMAN_MATERIAL_PATH git repository for generated human-facing materials. Use when a user asks to set up a new materials repo/folder for slides/manuscripts/exercises, create the expected file structure under $HUMAN_MATERIAL_PATH, and create a local-only .OPENROUTER_API_KEY file for slider rendering. |
| `read-arxiv-paper/` | skill | Download and deeply read an arXiv paper (given an arXiv URL or id), then write a clear human-facing report with strong storytelling and logical reasoning. Use when asked to summarize/review an arXiv paper, extract key ideas, connect them to practice, and produce a report under $HUMAN_MATERIAL_PATH/research/<paper_slug>/report.md. Stores downloads under $HUMAN_MATERIAL_PATH/.references/ (configurable via $HUMAN_MATERIAL_PATH/.agents/config.toml or ~/.agents/config.toml). |
| `repo-analysis/` | skill | Analyze a code repository to understand architecture, key components, data flow, and extension points. Use when onboarding to an unfamiliar repo, preparing a hands-on profiling session, or extracting LLM-specific implementation details (attention/KV cache/scheduler/decoding) after determining the repo is LLM-related. |
| `scientific/` | group | (3 skill(s)) |
| `slider/` | group | (4 skill(s)) |
<!-- PKBLLM_TABLE_END -->

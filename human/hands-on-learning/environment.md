# Environment detection and setup

Hands-on learning is only credible if the environment is explicitly captured. Most “it’s slow” / “it broke” outcomes are
environment issues (driver/toolkit mismatch, wrong GPU, missing optional deps, wrong clone vs wheel, etc.).

## Non-negotiables

- Capture **commands and outputs**, not just “I have an A100”.
- Capture **GPU topology** for multi-GPU work.
- Capture **Python + packages** (at least the ML stack and the project package itself).
- Capture **CUDA toolchain** (`nvcc`, driver version) when relevant.
- If something is missing, record the **exact error** and an **unblock plan**.

## Minimum environment report (`reports/environment.md`)

Copy this template into your session’s `reports/environment.md` and fill it:

```markdown
# Environment

**Captured:** {YYYY-MM-DD HH:MM TZ}
**Repo:** {repo_url_or_path}
**Repo commit:** {git_sha_or_tag}

## System

- OS: {uname -a}
- CPU: {lscpu summary}
- RAM: {free -h summary}

## GPU

- `nvidia-smi` summary: {gpu model list + memory}
- Compute capability: {major.minor if known}
- Topology: {nvlink pairs / numa}

## Toolchain

- Driver: {nvidia-smi driver version}
- CUDA runtime: {torch.version.cuda or runtime}
- CUDA toolkit: {nvcc --version or not available}
- cuDNN: {if relevant}

## Python

- Python: {python --version}
- pip: {pip --version}
- Torch: {torch.__version__}, CUDA available: {True/False}

## Key packages (versions)

- {project package}: {version or “local clone”}
- {kernel libs}: {flashinfer, triton, xformers, sgl-kernel, etc.}
- transformers: {version}
- accelerate: {version}
- jsonschema: {version if relevant}

## Notes / anomalies

- {e.g. “multiple matplotlib installs warning (non-fatal)”}
- {e.g. “flashinfer-jit-cache missing; using cubin package”}
```

## Recommended commands

Run from the session directory (and save raw outputs under `results/`).

### GPU inventory and topology

```bash
nvidia-smi
nvidia-smi topo -m
nvidia-smi --query-gpu=name,memory.total,driver_version,compute_cap --format=csv
```

### CUDA toolkit / compiler

```bash
which nvcc && nvcc --version
```

### Python + package snapshot

```bash
python --version
python -m pip --version
python -m pip freeze | sort | tee results/pip_freeze.txt
python -c "import torch; print('torch', torch.__version__, 'cuda', torch.version.cuda, 'available', torch.cuda.is_available())"
```

### Project version (wheel vs clone)

If using a local clone:

```bash
git -C {clone_path} rev-parse --short HEAD
```

If using an installed wheel:

```bash
python -c "import importlib.metadata as m; print(m.version('{package_name}'))"
```

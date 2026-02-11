# Environment

**Captured:** {YYYY-MM-DD HH:MM TZ}
**Repo:** {repo_url_or_path}
**Repo commit:** {git_sha_or_tag}

## System

- OS: {uname -a}
- CPU: {lscpu summary}
- RAM: {free -h summary}

## GPU

- Models: {gpu models}
- Driver: {driver version}
- CUDA runtime: {torch.version.cuda}
- Topology: {nvlink pairs / numa}

## Python

- Python: {python --version}
- pip: {pip --version}
- Torch: {torch.__version__}, CUDA available: {True/False}

## Packages (selected)

- {project package}: {version or local clone}
- {kernel libs}: {flashinfer, triton, sgl-kernel, etc.}

## Raw evidence

- `results/env_uname.txt`
- `results/env_nvidia_smi.txt`
- `results/env_pip_freeze.txt`


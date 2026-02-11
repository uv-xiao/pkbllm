#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS="${ROOT}/results"
mkdir -p "${RESULTS}"

uname -a | tee "${RESULTS}/env_uname.txt"

if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi | tee "${RESULTS}/env_nvidia_smi.txt"
  nvidia-smi topo -m | tee "${RESULTS}/env_nvidia_smi_topo.txt" || true
else
  echo "nvidia-smi: unavailable" | tee "${RESULTS}/env_nvidia_smi.txt"
fi

python --version | tee "${RESULTS}/env_python_version.txt"
python -m pip --version | tee "${RESULTS}/env_pip_version.txt"
python -m pip freeze | sort | tee "${RESULTS}/env_pip_freeze.txt" >/dev/null

python - <<'PY' | tee "${RESULTS}/env_torch.txt"
import sys
try:
    import torch
    print("python", sys.version.replace("\n", " "))
    print("torch", torch.__version__)
    print("torch.version.cuda", torch.version.cuda)
    print("torch.cuda.is_available", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("cuda.device_count", torch.cuda.device_count())
        for i in range(torch.cuda.device_count()):
            print("cuda.device", i, torch.cuda.get_device_name(i))
except Exception as e:
    print("torch: unavailable:", repr(e))
PY

echo "ok"

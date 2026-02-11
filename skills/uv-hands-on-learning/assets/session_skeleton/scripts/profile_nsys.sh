#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS="${ROOT}/results/nsys"
mkdir -p "${RESULTS}"

if ! command -v nsys >/dev/null 2>&1; then
  echo "nsys: unavailable"
  exit 2
fi

OUT="${RESULTS}/run"
echo "Writing trace prefix: ${OUT}"

nsys profile -o "${OUT}" \
  --trace=cuda,nvtx,osrt \
  --cuda-memory-usage=true \
  --force-overwrite=true \
  "$@" |& tee "${RESULTS}/stdout_stderr.log"


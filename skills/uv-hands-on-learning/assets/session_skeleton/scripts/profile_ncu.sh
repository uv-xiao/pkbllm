#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS="${ROOT}/results/ncu"
mkdir -p "${RESULTS}"

if ! command -v ncu >/dev/null 2>&1; then
  echo "ncu: unavailable"
  exit 2
fi

OUT="${RESULTS}/run"
echo "Writing report prefix: ${OUT}"

ncu --set full --target-processes all -o "${OUT}" \
  "$@" |& tee "${RESULTS}/stdout_stderr.log"


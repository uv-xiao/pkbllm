#!/usr/bin/env bash
set -euo pipefail

# pkb_task_start.sh
#
# Interactive task bootstrap:
# - clones pkbllm into a temporary directory
# - asks a few lightweight "brainstorm" questions about the task
# - recommends and lets you pick pkbllm skills
# - installs the picked skills into the target project (copy mode by default)
# - assembles full SKILL.md bodies into the target project's AGENTS.md
#
# Intended to be run via: curl/wget ... | bash

PKB_REPO_URL_DEFAULT="https://github.com/uv-xiao/pkbllm.git"
PKB_REF_DEFAULT="main"

usage() {
  cat <<'EOF'
Usage:
  pkb_task_start.sh [--target <dir>] [--agent <agent>] [--ref <git-ref>] [--repo <git-url>]
                   [--install-mode <copy|skills-cli|none>] [--keep]

Notes:
  - Default install mode is "copy" (no npx required).
  - "skills-cli" uses `npx skills add ...` for installation.
  - AGENTS.md is updated in-place using stable markers.
EOF
}

TARGET_DIR=""
AGENT="codex"
PKB_REPO_URL="$PKB_REPO_URL_DEFAULT"
PKB_REF="$PKB_REF_DEFAULT"
INSTALL_MODE="copy"
KEEP="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET_DIR="${2:-}"; shift 2;;
    --agent) AGENT="${2:-}"; shift 2;;
    --repo) PKB_REPO_URL="${2:-}"; shift 2;;
    --ref) PKB_REF="${2:-}"; shift 2;;
    --install-mode) INSTALL_MODE="${2:-}"; shift 2;;
    --keep) KEEP="1"; shift 1;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2;;
  esac
done

if [[ -z "${TARGET_DIR}" ]]; then
  TARGET_DIR="$(pwd)"
fi
TARGET_DIR="$(cd "${TARGET_DIR}" && pwd)"

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: missing required command: $1" >&2
    exit 1
  fi
}

need_cmd git
need_cmd python3

if [[ "${INSTALL_MODE}" == "skills-cli" ]]; then
  if ! command -v npx >/dev/null 2>&1; then
    echo "ERROR: install-mode=skills-cli requires npx" >&2
    exit 1
  fi
fi

PROMPT_TTY="/dev/tty"
if [[ ! -r "${PROMPT_TTY}" ]]; then
  # If no tty (rare), fall back to stdin.
  PROMPT_TTY="/dev/stdin"
fi

prompt() {
  local label="$1"
  local default="${2:-}"
  local ans=""
  if [[ -n "${default}" ]]; then
    read -r -p "${label} [${default}]: " ans <"${PROMPT_TTY}" || true
    if [[ -z "${ans}" ]]; then
      ans="${default}"
    fi
  else
    read -r -p "${label}: " ans <"${PROMPT_TTY}" || true
  fi
  printf '%s' "${ans}"
}

prompt_multiline() {
  local label="$1"
  echo "${label} (end with an empty line):" >&2
  local lines=()
  while true; do
    local line=""
    read -r line <"${PROMPT_TTY}" || true
    [[ -z "${line}" ]] && break
    lines+=("${line}")
  done
  printf '%s\n' "${lines[@]}"
}

echo "== pkbllm task bootstrap ==" >&2
echo "Target project: ${TARGET_DIR}" >&2
echo "Agent: ${AGENT}" >&2
echo "pkbllm repo: ${PKB_REPO_URL} (${PKB_REF})" >&2
echo "Install mode: ${INSTALL_MODE}" >&2

TASK="$(prompt "One-sentence task description" "")"
DONE="$(prompt "Definition of done (1 sentence)" "")"
CONSTRAINTS="$(prompt_multiline "Constraints / preferences (deps, network, style, repo rules)")"

QUERY=$(
  cat <<EOF
Task: ${TASK}
Done: ${DONE}
Constraints:
${CONSTRAINTS}
EOF
)

TMP_ROOT="$(mktemp -d)"
PKB_DIR="${TMP_ROOT}/pkbllm"
cleanup() {
  if [[ "${KEEP}" == "1" ]]; then
    echo "Keeping temp pkbllm clone at: ${PKB_DIR}" >&2
    return
  fi
  rm -rf "${TMP_ROOT}" || true
}
trap cleanup EXIT

echo "Cloning pkbllm into temp dir..." >&2
git clone --depth 1 --filter=blob:none --branch "${PKB_REF}" "${PKB_REPO_URL}" "${PKB_DIR}" >/dev/null 2>&1 || {
  echo "ERROR: failed to clone ${PKB_REPO_URL} (${PKB_REF})" >&2
  exit 1
}

RECOMMEND_OUT="$(
  python3 "${PKB_DIR}/bootstrap/scripts/pkb_agents_md.py" --source mirror recommend --query "${QUERY}" --top 12
)"

echo "" >&2
echo "Top recommendations:" >&2
echo "${RECOMMEND_OUT}" >&2

mapfile -t REC_SKILLS < <(printf '%s\n' "${RECOMMEND_OUT}" | sed -n 's/^[[:space:]]*[0-9]\+\.[[:space:]]\+\(uv-[^[:space:]]\+\).*/\1/p')
if [[ "${#REC_SKILLS[@]}" -eq 0 ]]; then
  echo "ERROR: no recommended skills found (empty query?)" >&2
  exit 1
fi

echo "" >&2
echo "Pick skills to embed into ${TARGET_DIR}/AGENTS.md:" >&2
for i in "${!REC_SKILLS[@]}"; do
  printf "  %2d) %s\n" "$((i+1))" "${REC_SKILLS[$i]}" >&2
done
SEL="$(prompt "Enter numbers (e.g. 1 2 5), or 'a' for all, default '1 2 3'" "1 2 3")"

CHOSEN=()
if [[ "${SEL}" == "a" || "${SEL}" == "A" ]]; then
  CHOSEN=("${REC_SKILLS[@]}")
else
  for tok in ${SEL}; do
    if [[ "${tok}" =~ ^[0-9]+$ ]]; then
      idx=$((tok-1))
      if [[ "${idx}" -ge 0 && "${idx}" -lt "${#REC_SKILLS[@]}" ]]; then
        CHOSEN+=("${REC_SKILLS[$idx]}")
      fi
    fi
  done
fi

if [[ "${#CHOSEN[@]}" -eq 0 ]]; then
  echo "ERROR: no skills selected." >&2
  exit 1
fi

# De-dup preserve order
DEDUP=()
SEEN=""
for s in "${CHOSEN[@]}"; do
  if [[ " ${SEEN} " == *" ${s} "* ]]; then
    continue
  fi
  SEEN="${SEEN} ${s}"
  DEDUP+=("${s}")
done
CHOSEN=("${DEDUP[@]}")

echo "" >&2
echo "Selected skills:" >&2
for s in "${CHOSEN[@]}"; do
  echo "  - ${s}" >&2
done

echo "" >&2
echo "Assembling AGENTS.md (full SKILL.md embeds)..." >&2
ASM_ARGS=(python3 "${PKB_DIR}/bootstrap/scripts/pkb_agents_md.py" --source mirror assemble --query "${QUERY}" --agents-md "${TARGET_DIR}/AGENTS.md" --init)
for s in "${CHOSEN[@]}"; do
  ASM_ARGS+=(--skill "${s}")
done
"${ASM_ARGS[@]}" >/dev/null
echo "Updated: ${TARGET_DIR}/AGENTS.md" >&2

if [[ "${INSTALL_MODE}" == "none" ]]; then
  echo "Skipping skill installation (install-mode=none)." >&2
  exit 0
fi

if [[ "${INSTALL_MODE}" == "copy" ]]; then
  echo "" >&2
  echo "Installing skills by copying into ${TARGET_DIR}/.codex/skills/ ..." >&2
  mkdir -p "${TARGET_DIR}/.codex/skills"
  for s in "${CHOSEN[@]}"; do
    src="${PKB_DIR}/skills/${s}"
    dst="${TARGET_DIR}/.codex/skills/${s}"
    if [[ ! -d "${src}" ]]; then
      echo "WARN: missing in mirror: ${src} (skipping install for ${s})" >&2
      continue
    fi
    rm -rf "${dst}" || true
    python3 - <<PY
import shutil, os
from pathlib import Path
src=Path(${src@Q})
dst=Path(${dst@Q})
dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(src, dst, copy_function=shutil.copy2)
PY
    echo "  installed: ${s} -> .codex/skills/${s}" >&2
  done
  echo "Done." >&2
  exit 0
fi

if [[ "${INSTALL_MODE}" == "skills-cli" ]]; then
  echo "" >&2
  echo "Installing skills via Skills CLI into the target project..." >&2
  for s in "${CHOSEN[@]}"; do
    (cd "${TARGET_DIR}" && npx -y skills add "${PKB_DIR}" -a "${AGENT}" --skill "${s}" -y) >/dev/null
    echo "  installed: ${s} (agent=${AGENT})" >&2
  done
  echo "Done." >&2
  exit 0
fi

echo "ERROR: unknown install mode: ${INSTALL_MODE}" >&2
exit 2


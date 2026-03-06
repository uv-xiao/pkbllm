#!/usr/bin/env bash
set -euo pipefail

# Agent-assisted task bootstrap (one-liner friendly):
# - clones pkbllm to a temp directory
# - runs pkb_task_start_agent.py which invokes a codex-backed agent with structured outputs
# - updates target repo: installs selected skills + assembles AGENTS.md

PKB_REPO_URL_DEFAULT="https://github.com/uv-xiao/pkbllm.git"
PKB_REF_DEFAULT="main"

usage() {
  cat <<'EOF'
Usage:
  pkb_task_start_agent.sh [--target <dir>] [--agent <agent>] [--ref <git-ref>] [--repo <git-url>]
                         [--install-mode <copy|skills-cli|none>] [--keep] [--no-interactive]
                         [--task <text>] [--done <text>] [--constraints <text>]

Notes:
  - Requires `git`, `python3`, and `codex` (Codex CLI) for the agent step.
  - Default install mode is "copy" (no npx required).
  - Writes debug logs under the cloned pkbllm `artifacts/task-start/<ts>/`.
EOF
}

TARGET_DIR="."
AGENT="codex"
PKB_REPO_URL="$PKB_REPO_URL_DEFAULT"
PKB_REF="$PKB_REF_DEFAULT"
INSTALL_MODE="copy"
KEEP="0"
NO_INTERACTIVE="0"
TASK=""
DONE=""
CONSTRAINTS=""
PROMPT_TTY_FD_OPEN="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET_DIR="${2:-}"; shift 2;;
    --agent) AGENT="${2:-}"; shift 2;;
    --repo) PKB_REPO_URL="${2:-}"; shift 2;;
    --ref) PKB_REF="${2:-}"; shift 2;;
    --install-mode) INSTALL_MODE="${2:-}"; shift 2;;
    --keep) KEEP="1"; shift 1;;
    --no-interactive) NO_INTERACTIVE="1"; shift 1;;
    --task) TASK="${2:-}"; shift 2;;
    --done) DONE="${2:-}"; shift 2;;
    --constraints) CONSTRAINTS="${2:-}"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2;;
  esac
done

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: missing required command: $1" >&2
    exit 1
  fi
}

need_cmd git
need_cmd python3
need_cmd codex

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

if [[ "${NO_INTERACTIVE}" != "1" && ! -t 0 ]]; then
  if exec 3</dev/tty; then
    PROMPT_TTY_FD_OPEN="1"
  else
    cat >&2 <<'EOF'
ERROR: stdin is not interactive, so prompt mode cannot run here.

If you launched this with `curl ... | bash`, rerun it in one of these forms:
  curl -fsSL https://raw.githubusercontent.com/uv-xiao/pkbllm/main/bootstrap/scripts/pkb_task_start_agent.sh | bash -s -- --no-interactive --task "..." --done "..."
  curl -fsSL https://raw.githubusercontent.com/uv-xiao/pkbllm/main/bootstrap/scripts/pkb_task_start_agent.sh | bash -s -- --target /path/to/repo

The first form is for CI/non-TTY usage. The second form works from a real terminal because bash can still prompt via /dev/tty.
EOF
    exit 2
  fi
fi

ARGS=(--target "${TARGET_DIR}" --agent "${AGENT}" --install-mode "${INSTALL_MODE}")
if [[ "${NO_INTERACTIVE}" == "1" ]]; then
  ARGS+=(--no-interactive)
fi
if [[ -n "${TASK}" ]]; then ARGS+=(--task "${TASK}"); fi
if [[ -n "${DONE}" ]]; then ARGS+=(--done "${DONE}"); fi
if [[ -n "${CONSTRAINTS}" ]]; then ARGS+=(--constraints "${CONSTRAINTS}"); fi

if [[ "${PROMPT_TTY_FD_OPEN}" == "1" ]]; then
  python3 "${PKB_DIR}/bootstrap/scripts/pkb_task_start_agent.py" "${ARGS[@]}" <&3
  exec 3<&-
else
  python3 "${PKB_DIR}/bootstrap/scripts/pkb_task_start_agent.py" "${ARGS[@]}"
fi

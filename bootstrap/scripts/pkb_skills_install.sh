#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
pkb_skills_install.sh

Download/clone pkbllm, remove any existing pkb (`uv-*`) skill installs, and install repo-locally to <pkb_dir>/.agent/skills.

Usage:
  pkb_skills_install.sh [--repo-dir DIR] [--repo-url URL] [--ref REF] [--dev]
                       [--copy] [--no-skills-cli] [--clean-only] [--dry-run]
                       [--verbose] [--quiet] [--keep-logs] [--no-dev-update]

Defaults:
  --repo-url   https://github.com/uv-xiao/pkbllm.git
  --repo-dir   $XDG_DATA_HOME/pkbllm/pkbllm  (or ~/.local/share/pkbllm/pkbllm)

Examples:
  pkb_skills_install.sh
  pkb_skills_install.sh --repo-dir ~/src/pkbllm --ref main
  pkb_skills_install.sh --dev --repo-dir ~/src/pkbllm
  pkb_skills_install.sh --dev --repo-dir ~/src/pkbllm --no-dev-update
  pkb_skills_install.sh --dry-run
  pkb_skills_install.sh --copy
  pkb_skills_install.sh --verbose
  pkb_skills_install.sh --keep-logs
EOF
}

repo_url="https://github.com/uv-xiao/pkbllm.git"
repo_dir=""
ref=""
dev="0"
copy="0"
no_skills_cli="0"
clean_only="0"
dry_run="0"
verbose="0"
quiet="0"
keep_logs="0"
no_dev_update="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-url) repo_url="$2"; shift 2 ;;
    --repo-dir) repo_dir="$2"; shift 2 ;;
    --ref) ref="$2"; shift 2 ;;
    --dev) dev="1"; shift ;;
    --copy) copy="1"; shift ;;
    --no-skills-cli) no_skills_cli="1"; shift ;;
    --clean-only) clean_only="1"; shift ;;
    --dry-run) dry_run="1"; shift ;;
    --verbose) verbose="1"; shift ;;
    --quiet) quiet="1"; shift ;;
    --keep-logs) keep_logs="1"; shift ;;
    --no-dev-update) no_dev_update="1"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ -z "${repo_dir}" ]]; then
  data_home="${XDG_DATA_HOME:-"$HOME/.local/share"}"
  repo_dir="${data_home}/pkbllm/pkbllm"
fi

need() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: missing required command: $1" >&2
    exit 1
  fi
}

need git
need bash

is_pkb_repo() {
  [[ -f "${repo_dir}/bootstrap/scripts/pkb_skills_reset.py" ]] && \
    ( [[ -f "${repo_dir}/skills/manifest.json" ]] || [[ -d "${repo_dir}/bootstrap" ]] || [[ -d "${repo_dir}/knowledge" ]] )
}

log() {
  if [[ "${quiet}" == "1" ]]; then
    return 0
  fi
  echo "[pkb-install] $*"
}

run() {
  if [[ "${dry_run}" == "1" ]]; then
    echo "[dry-run] $*"
    return 0
  fi
  "$@"
}

workdir="$(mktemp -d)"
log_file="${workdir}/pkb_install.log"

finish() {
  if [[ "${keep_logs}" == "1" ]]; then
    log "logs kept at: ${log_file}"
    return 0
  fi
  rm -rf "${workdir}" >/dev/null 2>&1 || true
}

on_err() {
  echo "ERROR: installation failed." >&2
  echo "Log file: ${log_file}" >&2
  if [[ -f "${log_file}" ]]; then
    echo "---- last 200 log lines ----" >&2
    tail -n 200 "${log_file}" >&2 || true
  fi
  finish
}

trap on_err ERR

if [[ "${dev}" == "1" ]]; then
  if ! is_pkb_repo; then
    echo "ERROR: --dev requires an existing pkbllm checkout at --repo-dir: ${repo_dir}" >&2
    echo "Expected files:" >&2
    echo "  ${repo_dir}/bootstrap/scripts/pkb_skills_reset.py" >&2
    echo "  ${repo_dir}/bootstrap/  (or common/ knowledge/ productivity/ human/)" >&2
    exit 1
  fi
  if command -v git >/dev/null 2>&1 && [[ -d "${repo_dir}/.git" ]]; then
    head_ref="$(git -C "${repo_dir}" rev-parse --short HEAD 2>/dev/null || true)"
    dirty="$(git -C "${repo_dir}" status --porcelain 2>/dev/null | wc -l | tr -d ' ' || true)"
    log "dev mode: using existing repo: ${repo_dir} (HEAD=${head_ref:-unknown}, dirty_files=${dirty:-unknown})"
    if [[ "${no_dev_update}" == "1" ]]; then
      log "dev mode: auto-update disabled (--no-dev-update)"
    elif [[ "${dirty}" == "0" ]]; then
      log "dev mode: updating repo (git pull --ff-only)…"
      if [[ "${verbose}" == "1" ]]; then
        git -C "${repo_dir}" pull --ff-only || true
      else
        git -C "${repo_dir}" pull --ff-only >>"${log_file}" 2>&1 || true
      fi
      head_ref2="$(git -C "${repo_dir}" rev-parse --short HEAD 2>/dev/null || true)"
      if [[ -n "${head_ref2}" ]] && [[ "${head_ref2}" != "${head_ref}" ]]; then
        log "dev mode: updated HEAD=${head_ref2}"
      fi
    else
      log "dev mode: repo has local changes; skipping auto-update"
    fi
  else
    log "dev mode: using existing repo: ${repo_dir}"
  fi
else
  log "repo url: ${repo_url}"
  log "repo dir: ${repo_dir}"
  if [[ -d "${repo_dir}/.git" ]]; then
    if [[ "${verbose}" == "1" ]]; then
      run git -C "${repo_dir}" fetch --all --tags --prune
    else
      run git -C "${repo_dir}" fetch --all --tags --prune >>"${log_file}" 2>&1
    fi
  else
    run mkdir -p "$(dirname "${repo_dir}")"
    if [[ "${verbose}" == "1" ]]; then
      run git clone "${repo_url}" "${repo_dir}"
    else
      run git clone "${repo_url}" "${repo_dir}" >>"${log_file}" 2>&1
    fi
  fi

  if [[ -n "${ref}" ]]; then
    if [[ "${verbose}" == "1" ]]; then
      run git -C "${repo_dir}" checkout "${ref}"
    else
      run git -C "${repo_dir}" checkout "${ref}" >>"${log_file}" 2>&1
    fi
  else
    # Best-effort update on the default branch.
    if [[ "${verbose}" == "1" ]]; then
      run git -C "${repo_dir}" checkout main || true
      run git -C "${repo_dir}" pull --ff-only || true
    else
      (run git -C "${repo_dir}" checkout main || true) >>"${log_file}" 2>&1
      (run git -C "${repo_dir}" pull --ff-only || true) >>"${log_file}" 2>&1
    fi
  fi
fi

if [[ "${dry_run}" == "1" ]]; then
  echo "[dry-run] would run: python3 ${repo_dir}/bootstrap/scripts/pkb_skills_reset.py --install-root ${repo_dir}/.agent/skills --force ..."
  echo "pkbllm repo: ${repo_dir}"
  echo "repo-local skills: ${repo_dir}/.agent/skills"
  cat <<EOF

Next steps (after running without --dry-run):
  export PKB_PATH="${repo_dir}"
  export HUMAN_MATERIAL_PATH="\${XDG_DATA_HOME:-\$HOME/.local/share}/pkbllm/human-materials"

Optional verification:
  npx -y skills add "${repo_dir}" --list
EOF
  exit 0
fi

py="python3"
if ! command -v "${py}" >/dev/null 2>&1; then
  py="python"
fi
if ! command -v "${py}" >/dev/null 2>&1; then
  echo "ERROR: need python3 (or python) to run pkb installer." >&2
  exit 1
fi

py_exec=("${py}" "-u")

reset_py="${repo_dir}/bootstrap/scripts/pkb_skills_reset.py"
if [[ ! -f "${reset_py}" ]]; then
  echo "ERROR: expected ${reset_py} to exist after clone." >&2
  exit 1
fi

args=()
args+=(--install-root "${repo_dir}/.agent/skills" --force)
if [[ "${copy}" == "1" ]]; then args+=(--copy); fi
if [[ "${no_skills_cli}" == "1" ]]; then args+=(--no-skills-cli); fi
if [[ "${clean_only}" == "1" ]]; then args+=(--clean-only); fi
if [[ "${dry_run}" == "1" ]]; then args+=(--dry-run); fi

log "cleaning existing installs and installing repo-local skills…"
if [[ "${verbose}" == "1" ]]; then
  "${py_exec[@]}" "${reset_py}" "${args[@]}" --verbose
else
  "${py_exec[@]}" "${reset_py}" "${args[@]}" >>"${log_file}" 2>&1
fi

materials_dir="${XDG_DATA_HOME:-"$HOME/.local/share"}/pkbllm/human-materials"
mkdir -p "${materials_dir}"/{slides,research,manuscripts,exercises} 2>/dev/null || true

cat <<EOF
Done.

Installed repo-local skills:
  ${repo_dir}/.agent/skills

Recommended environment variables (add to ~/.zshrc or ~/.bashrc):
  export PKB_PATH="${repo_dir}"
  export HUMAN_MATERIAL_PATH="${materials_dir}"

Optional verification:
  npx -y skills add "${repo_dir}" --list

Optional (Skills CLI linking to Codex agent, project-scope):
  cd "${repo_dir}" && npx -y skills add . -a codex --skill '*' -y
EOF

finish

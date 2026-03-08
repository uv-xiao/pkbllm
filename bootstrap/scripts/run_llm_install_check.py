#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from pkb_install_lib import copy_install_root


REPO_ROOT = Path(__file__).resolve().parents[2]


def _require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def _configure_kimi_for_claude() -> None:
    kimi_key = os.environ.get("KIMI_API_KEY", "").strip()
    if kimi_key and not os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        os.environ["ANTHROPIC_AUTH_TOKEN"] = kimi_key
    os.environ.setdefault("ANTHROPIC_BASE_URL", "https://api.kimi.com/coding/")
    os.environ.setdefault("ANTHROPIC_MODEL", "kimi-for-coding")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run the LLM-selected install/bootstrap flow against a temp target repo.")
    ap.add_argument("--selector", default="claude", help="LLM runner CLI to use (default: claude).")
    ap.add_argument("--agent", default="kimi", help="Install target agent to validate (default: kimi).")
    ap.add_argument("--install-mode", default="copy", choices=["copy", "skills-cli", "none"])
    ap.add_argument("--task", default="Bootstrap pkbllm skills for a coding repo that needs planning and debugging workflows.")
    ap.add_argument("--done", default="Relevant skills are installed and AGENTS.md contains embedded guidance.")
    ap.add_argument("--constraints", default="Prefer minimal high-impact skills. Avoid unrelated ML or human-material skills.")
    args = ap.parse_args(argv)

    if shutil.which(args.selector) is None:
        raise SystemExit(f"Missing required CLI on PATH: {args.selector}")

    if args.selector == "claude":
        _configure_kimi_for_claude()
        _require_env("ANTHROPIC_BASE_URL")
        _require_env("ANTHROPIC_AUTH_TOKEN")

    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "target-repo"
        target.mkdir(parents=True)

        cmd = [
            "bash",
            str(REPO_ROOT / "bootstrap" / "scripts" / "pkb_task_start_agent.sh"),
            "--target",
            str(target),
            "--selector",
            args.selector,
            "--agent",
            args.agent,
            "--install-mode",
            args.install_mode,
            "--no-interactive",
            "--task",
            args.task,
            "--done",
            args.done,
            "--constraints",
            args.constraints,
        ]
        subprocess.run(cmd, cwd=str(REPO_ROOT), check=True)

        agents_md = target / "AGENTS.md"
        if not agents_md.exists():
            raise SystemExit("LLM install check failed: AGENTS.md was not created.")

        install_root = copy_install_root(target, args.agent)
        installed_skill_dirs = sorted(p.parent.name for p in install_root.glob("uv-*/SKILL.md"))
        if not installed_skill_dirs:
            raise SystemExit(f"LLM install check failed: no installed skills found under {install_root}.")

        print(f"AGENTS.md: {agents_md}")
        print(f"Install root: {install_root}")
        print(f"Installed skills: {len(installed_skill_dirs)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

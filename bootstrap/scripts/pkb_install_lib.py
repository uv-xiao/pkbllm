#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


WhichFn = Callable[[str], str | None]


@dataclass(frozen=True)
class AgentSpec:
    name: str
    cli_commands: tuple[str, ...]
    copy_dirs: tuple[str, ...]
    prompt_label: str


AGENT_SPECS: dict[str, AgentSpec] = {
    "codex": AgentSpec(
        name="codex",
        cli_commands=("codex",),
        copy_dirs=(".codex/skills",),
        prompt_label="Codex",
    ),
    "claude": AgentSpec(
        name="claude",
        cli_commands=("claude",),
        copy_dirs=(".claude/skills",),
        prompt_label="Claude Code",
    ),
    "kimi": AgentSpec(
        name="kimi",
        cli_commands=("kimi", "kimi-cli"),
        copy_dirs=(".agents/skills", ".kimi/skills", ".claude/skills", ".codex/skills"),
        prompt_label="Kimi CLI",
    ),
    "agents": AgentSpec(
        name="agents",
        cli_commands=(),
        copy_dirs=(".agents/skills",),
        prompt_label="Generic .agents",
    ),
    "agent": AgentSpec(
        name="agent",
        cli_commands=(),
        copy_dirs=(".agent/skills",),
        prompt_label="Generic .agent",
    ),
}

PROJECT_DIR_AGENT_ORDER: tuple[tuple[str, str], ...] = (
    (".claude/skills", "claude"),
    (".codex/skills", "codex"),
    (".kimi/skills", "kimi"),
    (".agents/skills", "agents"),
    (".agent/skills", "agent"),
)

DETECTION_ORDER = ("claude", "codex", "kimi")
PROMPT_ORDER = ("auto", "claude", "codex", "kimi", "agents", "agent")
DEFAULT_AGENT = "codex"


def supported_agents() -> tuple[str, ...]:
    return tuple(name for name in PROMPT_ORDER if name != "auto")


def normalize_agent(value: str | None) -> str:
    raw = (value or "").strip().lower()
    if not raw:
        return DEFAULT_AGENT
    if raw == "auto":
        return "auto"
    if raw not in AGENT_SPECS:
        raise ValueError(f"Unsupported agent: {value!r}")
    return raw


def prompt_choices_text() -> str:
    return "/".join(PROMPT_ORDER)


def _existing_project_agents(target: Path | None) -> list[str]:
    if target is None:
        return []
    out: list[str] = []
    for rel_dir, agent in PROJECT_DIR_AGENT_ORDER:
        if (target / rel_dir).exists():
            out.append(agent)
    return out


def detect_installed_agents(target: Path | None = None, which: WhichFn = shutil.which) -> list[str]:
    found: list[str] = []
    for agent in _existing_project_agents(target):
        if agent not in found:
            found.append(agent)
    for agent in DETECTION_ORDER:
        spec = AGENT_SPECS[agent]
        if any(which(cmd) for cmd in spec.cli_commands):
            if agent not in found:
                found.append(agent)
    return found


def resolve_agent(requested: str | None, target: Path | None = None, which: WhichFn = shutil.which) -> dict[str, object]:
    requested_norm = normalize_agent(requested)
    detected = detect_installed_agents(target=target, which=which)
    if requested_norm != "auto":
        selected = requested_norm
        reason = "explicit"
    elif detected:
        selected = detected[0]
        reason = "detected"
    else:
        selected = DEFAULT_AGENT
        reason = "default"
    return {
        "requested_agent": requested_norm,
        "selected_agent": selected,
        "detected_agents": detected,
        "reason": reason,
        "copy_install_dir": str(copy_install_root(target or Path("."), selected)),
    }


def copy_install_root(target: Path, agent: str) -> Path:
    selected = normalize_agent(agent)
    if selected == "auto":
        selected = resolve_agent("auto", target=target)["selected_agent"]  # pragma: no cover - defensive
    spec = AGENT_SPECS[selected]
    if selected == "kimi":
        for rel_dir in spec.copy_dirs[1:]:
            candidate = target / rel_dir
            if candidate.exists():
                return candidate
    return target / spec.copy_dirs[0]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Shared pkb install/bootstrap agent helpers.")
    ap.add_argument("--target", default=".", help="Project root used for existing-dir detection.")
    ap.add_argument("--requested-agent", default="auto", help="Explicit agent choice or auto.")
    args = ap.parse_args(argv)

    payload = resolve_agent(args.requested_agent, target=Path(args.target).expanduser().resolve())
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

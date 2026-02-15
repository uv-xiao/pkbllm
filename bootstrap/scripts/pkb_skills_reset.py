#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    # bootstrap/scripts/<this_file>
    return Path(__file__).resolve().parents[2]

@dataclass(frozen=True)
class SkillSpec:
    name: str
    slug: str
    canonical_path: str | None = None


def _parse_skill_name(skill_md: Path) -> str | None:
    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError:
        return None

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    for line in lines[1:]:
        if line.strip() == "---":
            break
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith("name:"):
            continue
        value = line.split(":", 1)[1].strip()
        if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
            value = value[1:-1]
        return value.strip() or None

    return None


def _discover_uv_skills_from_canonical(repo_root: Path) -> list[SkillSpec]:
    roots = ["common", "knowledge", "productivity", "human", "bootstrap"]
    specs: dict[str, SkillSpec] = {}

    for root in roots:
        root_path = repo_root / root
        if not root_path.is_dir():
            continue
        for skill_md in root_path.rglob("SKILL.md"):
            name = _parse_skill_name(skill_md)
            if not name or not name.startswith("uv-"):
                continue
            canonical_path = str(skill_md.parent.relative_to(repo_root))
            specs[name] = SkillSpec(name=name, slug=name, canonical_path=canonical_path)

    return [specs[k] for k in sorted(specs)]


def _load_pkb_skills(repo_root: Path) -> list[SkillSpec]:
    manifest_path = repo_root / "skills" / "manifest.json"
    if not manifest_path.exists():
        # Don't assume a generated mirror exists in the checkout.
        specs = _discover_uv_skills_from_canonical(repo_root)
        if not specs:
            raise FileNotFoundError(
                f"Missing `{manifest_path}` and no `uv-*` skills found under canonical folders."
            )
        return specs

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Unexpected manifest format in `{manifest_path}` (expected JSON list).")

    specs: list[SkillSpec] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        slug = item.get("slug")
        canonical_path = item.get("canonical_path")
        if not isinstance(name, str):
            continue
        if not name.startswith("uv-"):
            continue
        if not isinstance(slug, str) or not slug:
            slug = name
        if not isinstance(canonical_path, str) or not canonical_path:
            canonical_path = None
        specs.append(SkillSpec(name=name, slug=slug, canonical_path=canonical_path))

    unique: dict[str, SkillSpec] = {}
    for spec in specs:
        unique[spec.name] = spec

    specs = [unique[k] for k in sorted(unique)]
    if not specs:
        raise ValueError(f"No `uv-` skills found in `{manifest_path}`.")
    return specs


def _agent_dot_dirs_from_gitignore(repo_root: Path) -> list[str]:
    gitignore_path = repo_root / ".gitignore"
    if not gitignore_path.exists():
        return []

    lines = gitignore_path.read_text(encoding="utf-8").splitlines()
    try:
        start_idx = lines.index("# Local agent skill installs / tool state (untracked; never commit)") + 1
    except ValueError:
        return []

    dot_dirs: list[str] = []
    for line in lines[start_idx:]:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if not line.startswith(".") or not line.endswith("/"):
            continue
        if any(ch in line for ch in "*?[]!"):
            continue
        dot_dir = line[:-1]
        if "/" in dot_dir:
            continue
        dot_dirs.append(dot_dir)

    return sorted(set(dot_dirs))


def _home_skill_roots() -> list[Path]:
    home = Path.home()
    roots: list[Path] = []
    try:
        entries = list(home.iterdir())
    except OSError:
        return []

    for entry in entries:
        name = entry.name
        if not name.startswith(".") or name in {".", ".."}:
            continue
        # Only consider top-level dot dirs with a `skills/` child.
        skills_dir = home / name / "skills"
        if skills_dir.is_dir():
            roots.append(skills_dir)

    return sorted(set(roots))


def _default_cleanup_roots(repo_root: Path) -> list[Path]:
    home = Path.home()
    roots: list[Path] = []
    # Home scope: keep conservative. Broader home cleanup is handled via `npx skills remove -g -a '*'`.
    roots.extend(
        [
            home / ".codex" / "skills",
            home / ".agents" / "skills",
            home / ".agent" / "skills",
        ]
    )
    # Also sweep any `~/.*/skills` roots to catch agent-specific installs (e.g. `~/.cursor/skills`, `~/.claude/skills`, ...).
    roots.extend(_home_skill_roots())

    # Repo scope: include common + tool-specific project dirs (mirrors `.gitignore` list).
    repo_dot_dirs = set(_agent_dot_dirs_from_gitignore(repo_root))
    repo_dot_dirs.update({".codex", ".agents", ".agent"})
    for dot_dir in sorted(repo_dot_dirs):
        roots.append(repo_root / dot_dir / "skills")

    return [p for i, p in enumerate(roots) if p not in roots[:i]]


def _which(cmd: str) -> str | None:
    return shutil.which(cmd)


def _chunk(items: list[str], size: int) -> list[list[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def _skills_cli_remove(*, repo_root: Path, skill_names: list[str], global_scope: bool, dry_run: bool) -> None:
    if _which("npx") is None:
        print("NOTE: `npx` not found; skipping Skills CLI cleanup.")
        return

    # NOTE: The Skills CLI help claims `--agent '*'` is supported, but some versions reject it
    # (e.g., "Invalid agents: *"). We intentionally omit `--agent` and rely on the CLI's default
    # behavior plus a filesystem sweep for agent-specific `~/.*/skills` link dirs.
    base_cmd = ["npx", "-y", "skills", "remove", "-y"]
    if global_scope:
        base_cmd.insert(4, "-g")

    for names_chunk in _chunk(skill_names, 20):
        cmd = [*base_cmd, "--skill", *names_chunk]
        if dry_run:
            scope = "global" if global_scope else "project"
            print(f"[dry-run] run ({scope}): {' '.join(cmd)}")
            continue

        result = subprocess.run(
            cmd,
            cwd=str(repo_root),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        output = (result.stdout or "").strip()
        if output:
            print(output)
        if result.returncode != 0:
            scope = "global" if global_scope else "project"
            print(
                f"WARNING: Skills CLI cleanup failed (scope={scope}, exit={result.returncode}).",
                file=sys.stderr,
            )


def _rm_path(path: Path, *, dry_run: bool) -> bool:
    if not path.exists() and not path.is_symlink():
        return False
    if dry_run:
        print(f"[dry-run] remove {path}")
        return True
    if path.is_symlink() or path.is_file():
        path.unlink()
        return True
    if path.is_dir():
        shutil.rmtree(path)
        return True
    # Fallback for odd filesystem entries
    path.unlink(missing_ok=True)
    return True


def _ensure_dir(path: Path, *, dry_run: bool) -> None:
    if path.exists():
        return
    if dry_run:
        print(f"[dry-run] mkdir -p {path}")
        return
    path.mkdir(parents=True, exist_ok=True)


def _symlink(src: Path, dest: Path, *, dry_run: bool) -> None:
    rel_src = os.path.relpath(src, start=dest.parent)
    if dry_run:
        print(f"[dry-run] ln -s {rel_src} {dest}")
        return
    dest.symlink_to(rel_src)

def _skill_dirnames(spec: SkillSpec) -> set[str]:
    names = {spec.slug, spec.name}
    return {n for n in names if n}


def _resolve_skill_source(repo_root: Path, spec: SkillSpec) -> Path | None:
    if spec.canonical_path:
        canonical = repo_root / spec.canonical_path
        if canonical.exists():
            return canonical
    mirror = repo_root / "skills" / spec.slug
    if mirror.exists():
        return mirror
    return None


def main(argv: list[str]) -> int:
    repo_root = _repo_root()

    parser = argparse.ArgumentParser(
        description="Remove existing pkbllm (`uv-*`) skills from common machine locations and install to this repo.",
    )
    parser.add_argument(
        "--install-root",
        default=str(repo_root / ".agent" / "skills"),
        help="Destination directory for repo-local install (default: <repo>/.agent/skills).",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy skill folders instead of symlinking (default: symlink).",
    )
    parser.add_argument(
        "--skip-clean",
        action="store_true",
        help="Skip cleanup; only install to --install-root.",
    )
    parser.add_argument(
        "--no-skills-cli",
        action="store_true",
        help="Disable using `npx skills remove` for cleanup (filesystem-only cleanup).",
    )
    parser.add_argument(
        "--clean-only",
        action="store_true",
        help="Only remove existing installs; do not install.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing skills under --install-root.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without changing anything.",
    )
    args = parser.parse_args(argv)

    specs = _load_pkb_skills(repo_root)
    skill_names = [s.name for s in specs]
    cleanup_roots = _default_cleanup_roots(repo_root)
    install_root = Path(args.install_root).expanduser().resolve()

    removed = 0
    if not args.skip_clean:
        if not args.no_skills_cli:
            _skills_cli_remove(repo_root=repo_root, skill_names=skill_names, global_scope=True, dry_run=args.dry_run)
            _skills_cli_remove(repo_root=repo_root, skill_names=skill_names, global_scope=False, dry_run=args.dry_run)

        for root in cleanup_roots:
            for spec in specs:
                for dirname in _skill_dirnames(spec):
                    removed += int(_rm_path(root / dirname, dry_run=args.dry_run))

    if args.clean_only:
        print(f"Done. Removed {removed} existing installs.")
        return 0

    _ensure_dir(install_root, dry_run=args.dry_run)

    installed = 0
    for spec in specs:
        src = _resolve_skill_source(repo_root, spec)
        if src is None:
            mirror = repo_root / "skills" / spec.slug
            canonical = repo_root / spec.canonical_path if spec.canonical_path else None
            parts = [f"ERROR: cannot find source for `{spec.name}`."]
            parts.append(f"- expected canonical: `{canonical}`" if canonical else "- canonical: (unknown)")
            parts.append(f"- expected mirror: `{mirror}`")
            parts.append("If you are on a partial checkout, pull full repo contents. If needed, regenerate mirror:")
            parts.append("  python bootstrap/scripts/update_skills_mirror.py all")
            print("\n".join(parts), file=sys.stderr)
            return 2

        dest = install_root / spec.slug
        if dest.exists() or dest.is_symlink():
            if not args.force:
                print(f"skip (exists): {dest}")
                continue
            _rm_path(dest, dry_run=args.dry_run)

        if args.copy:
            if args.dry_run:
                print(f"[dry-run] copytree {src} -> {dest}")
            else:
                shutil.copytree(src, dest, symlinks=True)
        else:
            _symlink(src, dest, dry_run=args.dry_run)

        installed += 1

    print(f"Done. Removed {removed} existing installs. Installed {installed} skills to `{install_root}`.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except BrokenPipeError:
        raise SystemExit(0)

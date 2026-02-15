#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    # bootstrap/scripts/<this_file>
    return Path(__file__).resolve().parents[2]

_SLUG_BAD = re.compile(r"[^a-z0-9._-]+")


def _skill_slug(name: str) -> str:
    slug = name.strip().lower()
    slug = re.sub(r"\s+", "-", slug)
    slug = slug.replace("/", "").replace("\\", "").replace(":", "")
    slug = _SLUG_BAD.sub("-", slug)
    slug = slug.strip("-")
    if not slug:
        raise ValueError(f"Could not slugify skill name: {name!r}")
    return slug


def _parse_frontmatter_name(skill_md: Path) -> str | None:
    try:
        lines = skill_md.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:120]:
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return None


def _iter_canonical_skill_dirs(repo_root: Path) -> list[Path]:
    canonical_roots = [
        repo_root / "common",
        repo_root / "knowledge",
        repo_root / "productivity",
        repo_root / "human",
        repo_root / "bootstrap",
    ]
    dirs: set[Path] = set()
    for root in canonical_roots:
        if not root.is_dir():
            continue
        for skill_md in root.rglob("SKILL.md"):
            if skill_md.name != "SKILL.md":
                continue
            parent = skill_md.parent
            if parent.name.startswith("."):
                continue
            dirs.add(parent)
    return sorted(dirs)


def _scan_canonical_pkb_skill_names(repo_root: Path) -> list[str]:
    names: set[str] = set()
    for skill_dir in _iter_canonical_skill_dirs(repo_root):
        name = _parse_frontmatter_name(skill_dir / "SKILL.md")
        if not name or not name.startswith("uv-"):
            continue
        names.add(name)
    return sorted(names)


def _load_pkb_skill_slugs_from_manifest(repo_root: Path) -> list[str]:
    manifest_path = repo_root / "skills" / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Missing `{manifest_path}`. Run `python bootstrap/scripts/update_skills_mirror.py build-mirror` first."
        )

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Unexpected manifest format in `{manifest_path}` (expected JSON list).")

    slugs: list[str] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        slug = item.get("slug")
        if not isinstance(name, str) or not name.startswith("uv-"):
            continue
        if not isinstance(slug, str) or not slug:
            slug = _skill_slug(name)
        slugs.append(slug)

    slugs = sorted(set(slugs))
    if not slugs:
        raise ValueError(f"No `uv-` skills found in `{manifest_path}`.")
    return slugs


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


def _skills_cli_remove(
    *, repo_root: Path, skill_names: list[str], global_scope: bool, dry_run: bool, verbose: bool
) -> None:
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
        if output and (verbose or result.returncode != 0):
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

def _run_update_skills_mirror(repo_root: Path, *, dry_run: bool) -> None:
    script = repo_root / "bootstrap" / "scripts" / "update_skills_mirror.py"
    if not script.exists():
        raise FileNotFoundError(f"Missing `{script}`.")
    # Installation should only require generating `skills/` (not mutating README tables).
    cmd = [sys.executable, str(script), "build-mirror"]
    if dry_run:
        print(f"[dry-run] run: {' '.join(cmd)}")
        return
    subprocess.run(cmd, cwd=str(repo_root), check=True)

def _skills_mirror_dir_count(repo_root: Path) -> int:
    skills_root = repo_root / "skills"
    if not skills_root.is_dir():
        return 0
    keep = {"README.md", "manifest.json"}
    count = 0
    for entry in skills_root.iterdir():
        if entry.name in keep:
            continue
        if entry.is_dir():
            count += 1
    return count


def _missing_skill_sources(repo_root: Path, slugs: list[str]) -> list[str]:
    missing: list[str] = []
    for slug in slugs:
        if not (repo_root / "skills" / slug).exists():
            missing.append(slug)
    return missing


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
        "--skip-mirror-update",
        action="store_true",
        help="Skip `python bootstrap/scripts/update_skills_mirror.py build-mirror` before installation.",
    )
    parser.add_argument(
        "--no-skills-cli",
        action="store_true",
        help="Disable using `npx skills remove` for cleanup (filesystem-only cleanup).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose logs (includes Skills CLI output).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress non-error output (implies --no-skills-cli output suppression).",
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

    def log(msg: str) -> None:
        if args.quiet:
            return
        print(msg, flush=True)

    skill_names = _scan_canonical_pkb_skill_names(repo_root)
    slugs_for_cleanup = sorted({_skill_slug(n) for n in skill_names})
    cleanup_roots = _default_cleanup_roots(repo_root)
    install_root = Path(args.install_root).expanduser().resolve()

    removed = 0
    if not args.skip_clean:
        if not args.no_skills_cli:
            if not args.quiet and args.verbose:
                log("[pkb-reset] removing installed pkb skills via Skills CLI (global)")
                log("[pkb-reset] NOTE: project-scope `skills remove` is disabled to avoid deleting this repo's `skills/<slug>/` mirror.")
            _skills_cli_remove(
                repo_root=repo_root,
                skill_names=skill_names,
                global_scope=True,
                dry_run=args.dry_run,
                verbose=(args.verbose and not args.quiet),
            )

        for root in cleanup_roots:
            for slug in slugs_for_cleanup:
                removed += int(_rm_path(root / slug, dry_run=args.dry_run))
            for name in skill_names:
                removed += int(_rm_path(root / name, dry_run=args.dry_run))

    if args.clean_only:
        log(f"Done. Removed {removed} existing installs.")
        return 0

    if not args.skip_mirror_update:
        log(f"[pkb-reset] building skills mirror via `update_skills_mirror.py build-mirror` (python={sys.executable})")
        _run_update_skills_mirror(repo_root, dry_run=args.dry_run)

    slugs = _load_pkb_skill_slugs_from_manifest(repo_root)
    mirror_dirs = _skills_mirror_dir_count(repo_root)
    log(f"[pkb-reset] skills mirror dirs: {mirror_dirs} (expected {len(slugs)})")
    missing = _missing_skill_sources(repo_root, slugs)
    if missing and not args.dry_run:
        print("[pkb-reset] ERROR: skills mirror is incomplete after build-mirror.", file=sys.stderr)
        print(f"[pkb-reset] missing sources (first 10): {', '.join(missing[:10])}", file=sys.stderr)
        print("[pkb-reset] hint: your repo may be incomplete (sparse/partial checkout), or mirror was deleted mid-run.", file=sys.stderr)
        return 2

    _ensure_dir(install_root, dry_run=args.dry_run)

    installed = 0
    for slug in slugs:
        src = repo_root / "skills" / slug
        if not src.exists():
            if args.dry_run:
                print(f"[dry-run] missing source {src} (would be created by `update_skills_mirror.py build-mirror`)")
                continue
            print(
                f"ERROR: missing source `{src}`. Run `python bootstrap/scripts/update_skills_mirror.py build-mirror`.",
                file=sys.stderr,
            )
            return 2

        dest = install_root / slug
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

    log(f"Done. Removed {removed} existing installs. Installed {installed} skills to `{install_root}`.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except BrokenPipeError:
        raise SystemExit(0)

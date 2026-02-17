#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANONICAL_ROOTS = [
    ROOT / "bootstrap",
    ROOT / "common",
    ROOT / "human",
    ROOT / "knowledge",
    ROOT / "productivity",
]


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    skill_md: Path

    @property
    def canonical_dir(self) -> Path:
        return self.skill_md.parent


_SLUG_BAD = re.compile(r"[^a-z0-9._-]+")


def _skill_slug(name: str) -> str:
    slug = name.strip().lower()
    slug = re.sub(r"\s+", "-", slug)
    slug = slug.replace("/", "").replace("\\", "").replace(":", "")
    slug = _SLUG_BAD.sub("-", slug).strip("-")
    if not slug:
        raise ValueError(f"Could not slugify skill name: {name!r}")
    return slug


def _read_frontmatter(skill_md: Path) -> dict[str, str]:
    lines = skill_md.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md missing frontmatter (expected leading '---').")
    out: dict[str, str] = {}
    for line in lines[1:250]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and value and key not in out:
            out[key] = value
    return out


def _iter_skill_mds() -> list[Path]:
    out: list[Path] = []
    for root in CANONICAL_ROOTS:
        if not root.exists():
            continue
        out.extend(p for p in root.rglob("SKILL.md") if p.name == "SKILL.md")
    return sorted(set(out))


def _load_skills() -> list[Skill]:
    skills: list[Skill] = []
    for skill_md in _iter_skill_mds():
        fm = _read_frontmatter(skill_md)
        name = fm.get("name", "").strip()
        description = fm.get("description", "").strip()
        skills.append(Skill(name=name, description=description, skill_md=skill_md))
    return skills


def _lint_prompts_csv(prompts_csv: Path) -> list[str]:
    errors: list[str] = []
    try:
        with prompts_csv.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            expected_cols = {"id", "should_trigger", "prompt"}
            missing = expected_cols - set(reader.fieldnames or [])
            if missing:
                errors.append(f"missing columns: {sorted(missing)}")
            rows = list(reader)
    except Exception as e:
        return [f"failed to read CSV: {e}"]

    if not rows:
        errors.append("no rows")
        return errors

    seen_ids: set[str] = set()
    saw_true = False
    saw_false = False
    for i, row in enumerate(rows, start=2):
        rid = (row.get("id") or "").strip()
        st = (row.get("should_trigger") or "").strip().lower()
        prompt = (row.get("prompt") or "").strip()
        if not rid:
            errors.append(f"row {i}: missing id")
        elif rid in seen_ids:
            errors.append(f"row {i}: duplicate id {rid!r}")
        else:
            seen_ids.add(rid)
        if st not in {"true", "false"}:
            errors.append(f"row {i}: should_trigger must be true/false (got {st!r})")
        if not prompt:
            errors.append(f"row {i}: missing prompt")
        saw_true = saw_true or (st == "true")
        saw_false = saw_false or (st == "false")

        # Optional columns (best-effort validation)
        sandbox = (row.get("sandbox") or "").strip()
        if sandbox and sandbox not in {"read-only", "workspace-write"}:
            errors.append(f"row {i}: sandbox must be read-only/workspace-write (got {sandbox!r})")

        timeout_s = (row.get("timeout_s") or "").strip()
        if timeout_s and not timeout_s.isdigit():
            errors.append(f"row {i}: timeout_s must be integer seconds (got {timeout_s!r})")

        max_commands = (row.get("max_commands") or "").strip()
        if max_commands and not max_commands.isdigit():
            errors.append(f"row {i}: max_commands must be integer (got {max_commands!r})")

        for col in ["max_input_tokens", "max_output_tokens", "max_total_tokens"]:
            raw = (row.get(col) or "").strip()
            if raw and not raw.isdigit():
                errors.append(f"row {i}: {col} must be integer (got {raw!r})")

        output_schema = (row.get("output_schema") or "").strip()
        if output_schema:
            schema_path = (ROOT / output_schema).resolve()
            if not schema_path.exists():
                errors.append(f"row {i}: output_schema missing: {output_schema!r}")

        fixture = (row.get("fixture") or "").strip()
        if fixture:
            fixture_path = (prompts_csv.parent / fixture).resolve()
            if not fixture_path.exists():
                errors.append(f"row {i}: fixture missing: {fixture!r}")

        # Regex fields should compile (if present)
        import re

        for col in ["must_include", "must_not_include"]:
            raw = (row.get(col) or "").strip()
            if not raw:
                continue
            parts = [p.strip() for p in raw.split("|") if p.strip()]
            for pat in parts:
                try:
                    re.compile(pat)
                except re.error as e:
                    errors.append(f"row {i}: invalid regex in {col}: {pat!r} ({e})")

    if not saw_true:
        errors.append("no should_trigger=true rows (need at least one positive case)")
    if not saw_false:
        errors.append("no should_trigger=false rows (need at least one negative control)")
    return errors


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Lint canonical skills and eval case metadata.")
    ap.add_argument("--strict", action="store_true", help="Fail if curated eval cases are missing.")
    ap.add_argument(
        "--check-evals",
        action="store_true",
        help="Validate any committed prompts.csv under evals/skills/**/prompts.csv.",
    )
    args = ap.parse_args(argv)

    skills = _load_skills()
    errors: list[str] = []
    warnings: list[str] = []

    if not skills:
        errors.append("No canonical skills found.")
    else:
        for s in skills:
            if not s.name:
                errors.append(f"{s.skill_md}: missing frontmatter name:")
            elif not s.name.startswith("uv-"):
                errors.append(f"{s.skill_md}: name must start with 'uv-': {s.name!r}")
            if not s.description:
                errors.append(f"{s.skill_md}: missing frontmatter description:")

    # Collisions
    names: dict[str, Path] = {}
    slugs: dict[str, Path] = {}
    for s in skills:
        if s.name:
            if s.name in names:
                errors.append(f"duplicate skill name {s.name!r}: {s.skill_md} and {names[s.name]}")
            else:
                names[s.name] = s.skill_md
            try:
                slug = _skill_slug(s.name)
            except Exception as e:
                errors.append(f"{s.skill_md}: slugify failed: {e}")
                continue
            if slug in slugs:
                errors.append(f"slug collision {slug!r}: {s.skill_md} and {slugs[slug]}")
            else:
                slugs[slug] = s.skill_md

    # Curated eval coverage (recommended, not required unless --strict)
    evals_root = ROOT / "evals" / "skills"
    missing_cases: list[str] = []
    for s in skills:
        if not s.name:
            continue
        slug = _skill_slug(s.name)
        prompts_csv = evals_root / slug / "prompts.csv"
        if not prompts_csv.exists():
            missing_cases.append(f"{s.name} -> {prompts_csv.relative_to(ROOT)}")

    if missing_cases:
        msg = f"{len(missing_cases)}/{len(skills)} skills missing curated eval cases (prompts.csv)."
        if args.strict:
            errors.append(msg)
        else:
            warnings.append(msg)

    if args.check_evals and evals_root.exists():
        for prompts_csv in sorted(evals_root.rglob("prompts.csv")):
            errs = _lint_prompts_csv(prompts_csv)
            if errs:
                errors.append(f"{prompts_csv.relative_to(ROOT)}: " + "; ".join(errs))

    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)

    print(f"Skills: {len(skills)}", file=sys.stderr)
    print(f"Warnings: {len(warnings)}", file=sys.stderr)
    print(f"Errors: {len(errors)}", file=sys.stderr)

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

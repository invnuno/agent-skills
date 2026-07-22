#!/usr/bin/env python3
"""Validate local Agent Skills package structure."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


NAME_RE = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?")


def validate_skill(path: Path) -> list[str]:
    errors: list[str] = []
    skill_file = path / "SKILL.md"
    if not skill_file.exists():
        return [f"{path}: missing SKILL.md"]

    text = skill_file.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return [f"{skill_file}: missing YAML frontmatter"]

    try:
        frontmatter = text.split("---\n", 2)[1]
        metadata = yaml.safe_load(frontmatter)
    except Exception as exc:
        return [f"{skill_file}: invalid frontmatter: {exc}"]

    name = metadata.get("name") if isinstance(metadata, dict) else None
    description = metadata.get("description") if isinstance(metadata, dict) else None

    if name != path.name:
        errors.append(f"{skill_file}: name must match directory ({path.name})")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        errors.append(f"{skill_file}: invalid name")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{skill_file}: missing description")
    elif len(description) > 1024:
        errors.append(f"{skill_file}: description exceeds 1024 characters")

    return errors


def main() -> int:
    root = Path("skills")
    if not root.exists():
        print("missing skills/ directory", file=sys.stderr)
        return 1

    errors: list[str] = []
    for skill_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        errors.extend(validate_skill(skill_dir))

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print("Agent Skills validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

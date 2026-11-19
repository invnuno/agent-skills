#!/usr/bin/env python3
"""Validate Agent Skills structure and audit publishable repository content."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import ipaddress
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable

import yaml


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LOCAL_RESOURCE_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])((?:references|scripts|agents)/[A-Za-z0-9._/-]+)"
)
IPV4_RE = re.compile(r"(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])")
EMAIL_RE = re.compile(
    r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,}|[A-Za-z0-9.-]+\.example)\b"
)
PERSONAL_PATH_PATTERNS = (
    re.compile(r"/home/[A-Za-z0-9._-]+/"),
    re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    re.compile(r"[A-Za-z]:\\Users\\[A-Za-z0-9._-]+\\", re.IGNORECASE),
)
SECRET_PATTERNS = (
    ("secret.private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("secret.github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("secret.aws-access-key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("secret.slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("secret.bearer-token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~-]{20,}")),
    ("secret.jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
)
CREDENTIAL_ASSIGNMENT_RE = re.compile(
    r"(?im)^[ \t]*(?:export[ \t]+)?"
    r"(?=[A-Za-z0-9_-]*(?:token|secret|password|api[_-]?key))"
    r"[A-Za-z_][A-Za-z0-9_-]*"
    r"[ \t]*[:=][ \t]*[\"']?([^\s\"']+)"
)
DEVICE_SERIAL_RE = re.compile(r"\bR[0-9]{11,15}\b")
PRIVATE_CHECKSUM_RE = re.compile(r"\b[0-9a-fA-F]{64}\b")
ALLOWED_FRONTMATTER = {"name", "description", "license", "metadata", "allowed-tools"}
RISKY_FILENAMES = {".env", "KoboRoot.tgz", "Kobo.tgz"}
RISKY_SUFFIXES = {
    ".db",
    ".img",
    ".iso",
    ".log",
    ".sqlite",
    ".sqlite3",
    ".tgz",
    ".zip",
}
WALK_EXCLUDES = {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


@dataclass(frozen=True, order=True)
class Issue:
    rule: str
    path: str
    line: int
    message: str


def issue(rule: str, path: Path, message: str, line: int = 0) -> Issue:
    return Issue(rule=rule, path=path.as_posix(), line=line, message=message)


def parse_skill(skill_file: Path) -> tuple[dict[str, object] | None, str, list[Issue]]:
    errors: list[Issue] = []
    try:
        text = skill_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None, "", [issue("skill.unreadable", skill_file, "SKILL.md must be readable UTF-8")]

    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return None, "", [issue("skill.frontmatter", skill_file, "missing opening YAML frontmatter delimiter", 1)]
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return None, "", [issue("skill.frontmatter", skill_file, "missing closing YAML frontmatter delimiter", 1)]

    try:
        parsed = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError:
        return None, "", [issue("skill.frontmatter", skill_file, "invalid YAML frontmatter", 1)]
    if not isinstance(parsed, dict):
        errors.append(issue("skill.frontmatter", skill_file, "frontmatter must be a mapping", 1))
        return None, "\n".join(lines[end + 1 :]), errors
    return parsed, "\n".join(lines[end + 1 :]), errors


def validate_openai_yaml(path: Path, skill_name: str) -> list[Issue]:
    errors: list[Issue] = []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError):
        return [issue("openai.invalid", path, "agents/openai.yaml must be readable YAML")]
    if not isinstance(data, dict) or not isinstance(data.get("interface"), dict):
        return [issue("openai.interface", path, "interface mapping is required")]

    interface = data["interface"]
    for key in ("display_name", "short_description", "default_prompt"):
        if not isinstance(interface.get(key), str) or not interface[key].strip():
            errors.append(issue("openai.interface", path, f"interface.{key} must be a non-empty string"))
    short_description = interface.get("short_description")
    if isinstance(short_description, str) and not 25 <= len(short_description) <= 64:
        errors.append(issue("openai.description", path, "short_description must contain 25-64 characters"))
    default_prompt = interface.get("default_prompt")
    if isinstance(default_prompt, str) and f"${skill_name}" not in default_prompt:
        errors.append(issue("openai.prompt", path, "default_prompt must explicitly name the skill"))
    return errors


def validate_skill(path: Path, root: Path) -> list[Issue]:
    errors: list[Issue] = []
    skill_file = path / "SKILL.md"
    if not skill_file.is_file():
        return [issue("skill.missing", skill_file.relative_to(root), "missing SKILL.md")]

    relative_skill = skill_file.relative_to(root)
    metadata, body, parse_errors = parse_skill(skill_file)
    errors.extend(
        Issue(item.rule, relative_skill.as_posix(), item.line, item.message)
        for item in parse_errors
    )
    if metadata is None:
        return errors

    unknown = sorted(set(metadata) - ALLOWED_FRONTMATTER)
    if unknown:
        errors.append(
            issue(
                "skill.frontmatter-keys",
                relative_skill,
                f"unsupported frontmatter keys: {', '.join(unknown)}",
            )
        )

    name = metadata.get("name")
    description = metadata.get("description")
    if name != path.name:
        errors.append(issue("skill.name-match", relative_skill, "name must match the parent directory"))
    if not isinstance(name, str) or len(name) > 64 or not NAME_RE.fullmatch(name):
        errors.append(issue("skill.name", relative_skill, "name must be lowercase kebab case and at most 64 characters"))
    if not isinstance(description, str) or not description.strip():
        errors.append(issue("skill.description", relative_skill, "description is required"))
    elif len(description) > 1024:
        errors.append(issue("skill.description", relative_skill, "description exceeds 1024 characters"))
    if not body.strip():
        errors.append(issue("skill.body", relative_skill, "instruction body is empty"))
    if len(skill_file.read_text(encoding="utf-8").splitlines()) >= 500:
        errors.append(issue("skill.length", relative_skill, "SKILL.md must stay below 500 lines"))

    nested_manifests = [candidate for candidate in path.rglob("SKILL.md") if candidate != skill_file]
    for nested in nested_manifests:
        errors.append(issue("skill.nested", nested.relative_to(root), "nested SKILL.md is not allowed"))
    if (path / "README.md").exists():
        errors.append(issue("skill.readme", (path / "README.md").relative_to(root), "per-skill README files are not allowed"))

    for match in LOCAL_RESOURCE_RE.finditer(skill_file.read_text(encoding="utf-8")):
        resource = match.group(1).rstrip(".,;:)")
        candidate = (path / resource).resolve()
        try:
            candidate.relative_to(path.resolve())
        except ValueError:
            errors.append(issue("skill.resource", relative_skill, "resource path escapes the skill directory"))
            continue
        if not candidate.exists():
            line = skill_file.read_text(encoding="utf-8")[: match.start()].count("\n") + 1
            errors.append(issue("skill.resource", relative_skill, f"referenced resource does not exist: {resource}", line))

    openai_yaml = path / "agents" / "openai.yaml"
    if openai_yaml.exists() and isinstance(name, str):
        for item in validate_openai_yaml(openai_yaml, name):
            errors.append(Issue(item.rule, openai_yaml.relative_to(root).as_posix(), item.line, item.message))

    scripts_dir = path / "scripts"
    if scripts_dir.is_dir():
        for script in scripts_dir.iterdir():
            if script.is_file() and script.suffix in {".py", ".sh"} and not os.access(script, os.X_OK):
                errors.append(issue("script.executable", script.relative_to(root), "helper script must be executable"))
    return errors


def line_number(text: str, offset: int) -> int:
    return text[:offset].count("\n") + 1


def is_placeholder(value: str) -> bool:
    lowered = value.lower()
    if "(" in value or value.startswith("$"):
        return True
    return any(marker in lowered for marker in ("replace", "example", "placeholder", "<", "xxxxx"))


def is_rfc1918(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if not isinstance(address, ipaddress.IPv4Address):
        return False
    value = int(address)
    return any(
        lower <= value <= upper
        for lower, upper in (
            (0x0A000000, 0x0AFFFFFF),
            (0xAC100000, 0xAC1FFFFF),
            (0xC0A80000, 0xC0A8FFFF),
        )
    )


def audit_text(path: Path, display_path: Path) -> list[Issue]:
    errors: list[Issue] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeError:
        if "assets" not in path.parts:
            errors.append(issue("privacy.binary", display_path, "binary content is only allowed under a skill assets directory"))
        return errors
    except OSError:
        return [issue("privacy.unreadable", display_path, "file could not be read for privacy review")]

    for pattern in PERSONAL_PATH_PATTERNS:
        for match in pattern.finditer(text):
            errors.append(issue("privacy.personal-path", display_path, "personal home-directory path is not allowed", line_number(text, match.start())))
    for match in IPV4_RE.finditer(text):
        try:
            address = ipaddress.ip_address(match.group(0))
        except ValueError:
            continue
        if is_rfc1918(address):
            errors.append(issue("privacy.private-ip", display_path, "RFC1918 address literal is not allowed", line_number(text, match.start())))
    for match in EMAIL_RE.finditer(text):
        domain = match.group(1).lower()
        if not domain.endswith((".example", ".example.com", ".example.org", ".example.net")):
            errors.append(issue("privacy.email", display_path, "real email address is not allowed", line_number(text, match.start())))
    for rule, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            errors.append(issue(rule, display_path, "possible secret is not allowed", line_number(text, match.start())))
    for match in CREDENTIAL_ASSIGNMENT_RE.finditer(text):
        if not is_placeholder(match.group(1)):
            errors.append(issue("secret.assignment", display_path, "credential assignment must use a placeholder", line_number(text, match.start())))
    for match in DEVICE_SERIAL_RE.finditer(text):
        errors.append(issue("privacy.device-serial", display_path, "device serial-like value is not allowed", line_number(text, match.start())))
    for match in PRIVATE_CHECKSUM_RE.finditer(text):
        errors.append(issue("privacy.private-checksum", display_path, "embedded 64-character checksum requires removal or explicit policy", line_number(text, match.start())))
    return errors


def candidate_files(root: Path) -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=root,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return sorted(
            path
            for path in root.rglob("*")
            if path.is_file()
            and not any(part in WALK_EXCLUDES for part in path.relative_to(root).parts)
            and path.name != ".env"
        )
    return sorted(
        root / item.decode("utf-8")
        for item in result.stdout.split(b"\0")
        if item
    )


def audit_repository_files(root: Path) -> list[Issue]:
    errors: list[Issue] = []
    for path in candidate_files(root):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if path.name in RISKY_FILENAMES and path.name != ".env.example":
            errors.append(issue("privacy.risky-file", relative, "sensitive runtime artifact must not be published"))
            continue
        if path.suffix.lower() in RISKY_SUFFIXES:
            errors.append(issue("privacy.risky-file", relative, "binary/runtime artifact must not be published"))
            continue
        size = path.stat().st_size
        if size > 10 * 1024 * 1024:
            errors.append(issue("privacy.file-size", relative, "file exceeds the 10 MiB repository limit"))
        elif size > 1024 * 1024 and "assets" not in relative.parts:
            errors.append(issue("privacy.file-size", relative, "non-asset file exceeds 1 MiB"))
        errors.extend(audit_text(path, relative))
    return errors


def validate_repository(root: Path) -> list[Issue]:
    root = root.resolve()
    skills_root = root / "skills"
    errors: list[Issue] = []
    if not skills_root.is_dir():
        errors.append(issue("repository.skills", Path("skills"), "missing skills directory"))
    else:
        skill_dirs = sorted(path for path in skills_root.iterdir() if path.is_dir() and not path.name.startswith("."))
        if not skill_dirs:
            errors.append(issue("repository.skills", Path("skills"), "no skill directories found"))
        for skill_dir in skill_dirs:
            errors.extend(validate_skill(skill_dir, root))
    errors.extend(audit_repository_files(root))
    return sorted(set(errors))


def render_text(errors: Iterable[Issue]) -> None:
    for item in errors:
        location = f":{item.line}" if item.line else ""
        print(f"{item.rule}: {item.path}{location}: {item.message}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root (default: current directory)")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Diagnostic output format")
    args = parser.parse_args()

    errors = validate_repository(args.root)
    if args.format == "json":
        print(json.dumps([asdict(item) for item in errors], indent=2))
    elif errors:
        render_text(errors)
    if errors:
        return 1
    if args.format == "text":
        print("Agent Skills validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Small Home Assistant REST helper for Agent Skills workflows."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
MAX_ERROR_CHARS = 1_000


def default_env_file() -> Path:
    override = os.environ.get("AGENT_SKILLS_ENV_FILE")
    return Path(override).expanduser() if override else REPOSITORY_ROOT / ".env"


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    if not path.is_file():
        raise SystemExit("Environment-file path is not a regular file")

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value.rstrip("/") if name == "HA_URL" else value


def redact_error(text: str, secrets: tuple[str, ...]) -> str:
    redacted = text[:MAX_ERROR_CHARS]
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "<redacted>")
    return re.sub(
        r"(?i)bearer\s+[a-z0-9._~-]+",
        "Bearer <redacted>",
        redacted,
    )


def request(
    method: str,
    path: str,
    *,
    timeout: float,
    payload: object | None = None,
) -> object:
    base = required_env("HA_URL")
    token = required_env("HA_TOKEN")
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        base + path,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        safe_body = redact_error(body, (token,))
        raise SystemExit(
            f"HTTP {exc.code} {exc.reason}: {safe_body}"
        ) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Connection failed: {exc.reason}") from exc


def print_json(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--env-file",
        type=Path,
        default=default_env_file(),
        help=(
            "Environment file containing HA_URL and HA_TOKEN "
            "(default: AGENT_SKILLS_ENV_FILE or repository .env)"
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="HTTP timeout in seconds (default: 60)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("states", help="List all HA states")
    state_parser = subparsers.add_parser("state", help="Read one entity state")
    state_parser.add_argument("entity_id")
    subparsers.add_parser("services", help="List HA services")
    subparsers.add_parser("check-config", help="Run homeassistant.check_config")
    subparsers.add_parser("reload-automations", help="Reload automations")
    subparsers.add_parser("reload-scripts", help="Reload scripts")
    prompt_parser = subparsers.add_parser(
        "conversation", help="Run conversation.process"
    )
    prompt_parser.add_argument("text")
    prompt_parser.add_argument("--agent-id", default=None)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.timeout <= 0:
        raise SystemExit("--timeout must be greater than zero")
    load_dotenv(args.env_file.expanduser())

    request_args = {"timeout": args.timeout}
    if args.command == "states":
        result = request("GET", "/api/states", **request_args)
    elif args.command == "state":
        result = request("GET", f"/api/states/{args.entity_id}", **request_args)
    elif args.command == "services":
        result = request("GET", "/api/services", **request_args)
    elif args.command == "check-config":
        result = request(
            "POST",
            "/api/services/homeassistant/check_config",
            payload={},
            **request_args,
        )
    elif args.command == "reload-automations":
        result = request(
            "POST",
            "/api/services/automation/reload",
            payload={},
            **request_args,
        )
    elif args.command == "reload-scripts":
        result = request(
            "POST",
            "/api/services/script/reload",
            payload={},
            **request_args,
        )
    else:
        payload = {"text": args.text}
        if args.agent_id:
            payload["agent_id"] = args.agent_id
        result = request(
            "POST",
            "/api/services/conversation/process?return_response",
            payload=payload,
            **request_args,
        )

    print_json(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Small Home Assistant REST helper for Agent Skills workflows."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request


def load_dotenv() -> None:
    path = Path(".env")
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def env(name: str) -> str:
    load_dotenv()
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value.rstrip("/") if name == "HA_URL" else value


def request(method: str, path: str, payload: object | None = None) -> object:
    base = env("HA_URL")
    token = env("HA_TOKEN")
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
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code} {exc.reason}: {body}") from exc


def print_json(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("states", help="List all HA states")
    state_parser = sub.add_parser("state", help="Read one entity state")
    state_parser.add_argument("entity_id")
    sub.add_parser("services", help="List HA services")
    sub.add_parser("check-config", help="Run homeassistant.check_config")
    sub.add_parser("reload-automations", help="Reload automations")
    sub.add_parser("reload-scripts", help="Reload scripts")
    prompt_parser = sub.add_parser("conversation", help="Run conversation.process")
    prompt_parser.add_argument("text")
    prompt_parser.add_argument("--agent-id", default=None)

    args = parser.parse_args()

    if args.command == "states":
        print_json(request("GET", "/api/states"))
    elif args.command == "state":
        print_json(request("GET", f"/api/states/{args.entity_id}"))
    elif args.command == "services":
        print_json(request("GET", "/api/services"))
    elif args.command == "check-config":
        print_json(request("POST", "/api/services/homeassistant/check_config", {}))
    elif args.command == "reload-automations":
        print_json(request("POST", "/api/services/automation/reload", {}))
    elif args.command == "reload-scripts":
        print_json(request("POST", "/api/services/script/reload", {}))
    elif args.command == "conversation":
        payload = {"text": args.text}
        if args.agent_id:
            payload["agent_id"] = args.agent_id
        print_json(
            request(
                "POST",
                "/api/services/conversation/process?return_response",
                payload,
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())

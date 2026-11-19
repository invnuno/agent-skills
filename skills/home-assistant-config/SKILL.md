---
name: home-assistant-config
description: Work safely on Home Assistant YAML repositories and live HA instances. Use for Home Assistant configuration, automations, scripts, scenes, Lovelace dashboards, themes, Assist sentence triggers, Ollama/LLM setup, REST validation, SSH deployment, and reload/restart decisions.
metadata:
  version: "1.0.0"
---

# Home Assistant Config

Use this skill when asked to review, modify, validate, deploy, or troubleshoot Home Assistant YAML configuration, Lovelace dashboards, automations, Assist, or local AI integrations.

## Environment

Local review requires a Home Assistant YAML repository. Live operations use
`HA_URL` and `HA_TOKEN` or equivalent authorized access; remote deployment may
also require SSH/SCP. If live access is unavailable, continue with local
validation and state the limitation.

## Core workflow

1. Inspect local repository state before editing.
2. Prefer live Home Assistant state over stale snapshots when API access is available.
3. Make the smallest YAML change that solves the request.
4. Validate local YAML syntax before deployment.
5. Back up remote files before overwriting `/config`.
6. Deploy through `/tmp` first when `/config` requires elevated permissions.
7. Run `homeassistant.check_config` before reloads or restarts.
8. Reload only the affected domain when possible.
9. Restart Home Assistant Core only when explicitly requested or technically required.
10. Summarize changed files, deployment target, validation result, and residual risks.

## Scope

Allowed by default:

- `configuration.yaml`, `automations.yaml`, `scripts.yaml`, `scenes.yaml`
- `packages/`, `blueprints/`, helper YAML, theme YAML
- YAML Lovelace dashboards and Lovelace resource definitions
- static dashboard assets under `www/` when referenced by Lovelace or themes
- local documentation that records Home Assistant operating decisions

Do not modify unless explicitly instructed:

- secrets, tokens, `.env`, `secrets.yaml` values
- sync, backup, deployment, CI, hooks, or non-Home-Assistant tooling
- UI-managed `.storage` files when a supported YAML/API/UI path exists

## Branching

For multi-file work, feature work, risky changes, or live-deployed improvements, create a dedicated branch first. Use direct edits on the current branch only for small, low-risk fixes or when explicitly requested.

## Live review

If `HA_URL` and `HA_TOKEN` are available, use the REST API for read-only inspection before editing. Refresh local snapshots only when they materially help the task. Treat live state as authoritative over `entities.txt`, `ha_states.json`, and other snapshots.

Use `scripts/ha_api.py` for common REST calls when available:

```bash
python skills/home-assistant-config/scripts/ha_api.py states
python skills/home-assistant-config/scripts/ha_api.py services
python skills/home-assistant-config/scripts/ha_api.py check-config
```

Read `references/rest-api-recipes.md` when a task needs live state, service calls, Assist pipeline tests, or Ollama config-entry inspection.

## Deployment

Home Assistant config normally lives under `/config` on the HA host. If `/config` is root-owned, upload to `/tmp` and install with `sudo install`. Use `scp -O` when the remote SSH server does not support SFTP.

Read `references/deployment.md` before remote deployment, reloads, restarts, or file backup/restore.

## Assist and AI

Prefer deterministic sentence-trigger automations for common daily commands. Use LLM fallback only for summaries, explanations, and safe control over intentionally exposed entities.

For local LLMs on constrained hardware, benchmark with real Assist prompts before keeping a model. Record rejected models and rollback decisions.

Read `references/assist-ai.md` for deterministic sentence trigger patterns, exposed-entity rules, Ollama model trials, and dashboard-context controls.

## Validation

Validation is mandatory before finalizing changes:

- YAML parses locally.
- Entity IDs are valid against live state or inventory snapshots.
- Dashboard references resolve.
- `homeassistant.check_config` passes when live access exists.
- Reload/restart is only as broad as needed.
- Control tests restore state when they change devices.

Read `references/validation.md` for command examples and acceptance checks.

## Gotchas

- Home Assistant sentence triggers do not consistently normalize typed apostrophes. Include non-contracted variants such as `whats`, `hows`, or full phrases.
- Dashboard-only YAML changes usually do not require a Core restart.
- Lovelace resource or frontend JavaScript asset changes may require a resource reload or Core restart.
- The built-in Home Assistant conversation agent cannot answer many inventory questions; prefer deterministic sentence triggers or an LLM pipeline with local intents preferred.
- Keep smart plugs, update entities, backups, add-ons, network controls, and configuration entities out of broad AI exposure unless explicitly requested.
- Never print long-lived access tokens, secrets, or secret-bearing config entries.

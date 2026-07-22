# Home Assistant Config Skill

Portable Agent Skill for safe Home Assistant YAML, Lovelace, Assist, local AI, validation, deployment, and reload/restart decisions.

This skill is repo-first: it helps an agent work from a Home Assistant configuration repository, inspect live state when available, make small changes, validate them, deploy with backups, and reload only what changed.

## When To Use

Use this skill for:

- Reviewing or editing `configuration.yaml`, `automations.yaml`, `scripts.yaml`, `scenes.yaml`, `packages/`, `blueprints/`, themes, and YAML Lovelace dashboards.
- Checking live entity IDs, services, Assist behavior, and config validation through the Home Assistant REST API.
- Deploying YAML or dashboard assets to `/config` through SSH/SCP with a backup-first workflow.
- Designing deterministic Assist sentence triggers and constrained local LLM fallback behavior.

Do not use it to modify secrets, `.env`, `secrets.yaml`, UI-managed `.storage`, or unrelated sync/deployment tooling unless explicitly requested.

## Setup

Live Home Assistant access is optional. For local file review only, no token is required.

For live REST checks, create a root `.env` from the repository example:

```bash
cp .env.example .env
```

Then set:

```dotenv
HA_URL=http://homeassistant.local:8123
HA_TOKEN=replace-with-your-long-lived-access-token
```

Create `HA_TOKEN` in Home Assistant from your user profile under **Long-lived access tokens**. Copy it once, store it only in local `.env`, and never print or commit the real value.

## Walkthrough

1. Inspect git status and the Home Assistant config layout before editing.
2. Load the relevant reference below before touching files.
3. If `HA_URL` and `HA_TOKEN` are available, inspect live state and services before relying on snapshots.
4. Edit the smallest config surface that solves the request.
5. Validate YAML locally, including Home Assistant tags such as `!include`.
6. If deploying, back up remote files, upload through `/tmp`, and install into `/config`.
7. Run `homeassistant.check_config` before reloads or restarts.
8. Reload the narrowest affected domain; restart Core only when explicitly requested or technically required.
9. Summarize changed files, validation results, deployment target, reload/restart action, and residual risk.

## Reference Map

- `references/rest-api-recipes.md` - use for live states, services, config checks, reloads, conversation tests, Assist pipeline checks, and config-entry reloads.
- `references/deployment.md` - use before SSH/SCP deployment, backup/restore, remote installs, reloads, or restart decisions.
- `references/validation.md` - use before finalizing YAML, dashboard, Assist, or deployment work.
- `references/assist-ai.md` - use for sentence triggers, dashboard context, Ollama/local LLM trials, MCP decisions, and AI entity exposure.

## Helper Script

The REST helper reads `HA_URL` and `HA_TOKEN` from root `.env` or the process environment.

```bash
python skills/home-assistant-config/scripts/ha_api.py states
python skills/home-assistant-config/scripts/ha_api.py services
python skills/home-assistant-config/scripts/ha_api.py check-config
python skills/home-assistant-config/scripts/ha_api.py reload-automations
python skills/home-assistant-config/scripts/ha_api.py reload-scripts
python skills/home-assistant-config/scripts/ha_api.py conversation "summarize the home status"
```

## Comparison With HA Vibecode Agent

[HA Vibecode Agent](https://github.com/Coolver/home-assistant-vibecode-agent) is a running Home Assistant add-on or Docker service plus MCP server. It exposes structured APIs for file operations, entities, helpers, automations, scripts, dashboards, themes, logs, backups, HACS, add-ons, and system operations.

| Area | This skill | HA Vibecode Agent |
| --- | --- | --- |
| Runtime | Markdown instructions plus optional Python helper | Installed add-on/Docker agent plus MCP server |
| Default workflow | Local repo edits, explicit validation, optional SSH/SCP deploy | IDE talks MCP to an HA-side agent with direct API/file access |
| Best fit | Auditable, portable, conservative YAML workflow | Full AI operations layer with broad HA runtime tooling |
| Safety model | Human-readable rules: smallest change, backups, check config, narrow reloads | Path validation, authentication, Git-backed rollback, audit-oriented API |
| Dependency cost | Low; works with any agent that can read skills and run shell commands | Higher; requires installing and operating the agent/MCP components |

Use this skill when you want a lightweight workflow guide that stays close to your repo. Use HA Vibecode Agent when you want an installed MCP-backed operations layer that can manage Home Assistant directly from an IDE.

Further reading: [Coolver project site](https://coolver.github.io/home-assistant-vibecode-agent/), [development/API docs](https://github.com/Coolver/home-assistant-vibecode-agent/blob/main/DEVELOPMENT.md), and [add-on config](https://github.com/Coolver/home-assistant-vibecode-agent/blob/main/config.yaml).

## Safety Notes

- Never commit tokens, secrets, private hostnames, private IPs, or machine-specific deployment details.
- Prefer deterministic scripts/scenes over broad AI control surfaces.
- Keep LLM-exposed entities small and intentional.
- Avoid editing UI-managed `.storage` files when YAML, API, or UI-supported paths exist.
- Always report whether validation passed and what was reloaded or restarted.

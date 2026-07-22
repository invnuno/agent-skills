# Agent Skills

Portable Agent Skills for coding agents that support the `SKILL.md` open format.

## Purpose

This repository is a personal collection of reusable Agent Skills. It is meant to be cloned, linked, or copied into coding agents that understand the `SKILL.md` format.

Skill-specific usage belongs inside each skill directory. The repository root only documents repository layout, validation, and how to make the skills discoverable by common agents.

## Structure

```text
skills/
└── <skill-name>/
    ├── SKILL.md
    ├── references/
    └── scripts/
```

Each skill follows the Agent Skills format:

- `SKILL.md` with YAML frontmatter.
- `name` matches the parent directory.
- `description` explains when the skill should activate.
- `references/` contains optional on-demand documentation.
- `scripts/` contains optional reusable tooling.

Keep detailed instructions, examples, and domain-specific references in the relevant skill directory, not in this root README.

## Validate

```bash
python3 scripts/validate_skills.py
```

## Environment Configuration

A local `.env` file is optional. It is only needed for live Home Assistant REST helper workflows, such as running `skills/home-assistant-config/scripts/ha_api.py`.

Create it from the committed example:

```bash
cp .env.example .env
```

Then edit `.env` with your Home Assistant URL and token:

```dotenv
HA_URL=http://homeassistant.local:8123
HA_TOKEN=replace-with-your-long-lived-access-token
```

To create `HA_TOKEN` in Home Assistant:

1. Open Home Assistant.
2. Click your user profile or avatar.
3. Scroll to **Long-lived access tokens**.
4. Click **Create Token**.
5. Use a descriptive name, such as `agent-skills-local`.
6. Copy the token immediately and paste it into `.env`.

The token is secret and is shown only once. Do not commit, print, or share the real value. `.env` is ignored by git; `.env.example` is safe to commit because it contains placeholders only.

## Install Or Link Skills

The most portable source of truth is each `skills/<skill-name>/SKILL.md` directory. Different agents discover that directory from different locations.

### Codex

Codex supports skills as part of its customization system. For local development, keep this repository as the source of truth and point Codex at the desired `SKILL.md` path through the active Codex skills configuration for your environment.

Example per-skill config entry:

```toml
[[skills.config]]
path = "/absolute/path/to/agent-skills/skills/<skill-name>/SKILL.md"
enabled = true
```

Use an absolute path and replace `<skill-name>` with the skill directory you want to expose.

### Gemini CLI

Gemini CLI discovers skills from user and workspace skill directories. You can install from a repository or link a local skill while developing.

Install from GitHub:

```bash
gemini skills install https://github.com/<user>/<repo>.git
```

Link a local skill:

```bash
gemini skills link /absolute/path/to/agent-skills/skills/<skill-name>
```

During a Gemini CLI session:

```text
/skills list
/skills reload
```

Gemini also supports `.agents/skills/` as a workspace-compatible location.

### Claude Code

Claude Code skills are filesystem artifacts under `.claude/skills/`.

Project-local install:

```bash
mkdir -p .claude/skills
cp -R /absolute/path/to/agent-skills/skills/<skill-name> .claude/skills/
```

Global install:

```bash
mkdir -p ~/.claude/skills
cp -R /absolute/path/to/agent-skills/skills/<skill-name> ~/.claude/skills/
```

Restart or refresh Claude Code after adding or updating skills if it does not detect changes automatically.

### OpenCode

OpenCode searches several locations, including native OpenCode paths and compatible `.agents` / `.claude` paths.

Project-local install:

```bash
mkdir -p .opencode/skills
cp -R /absolute/path/to/agent-skills/skills/<skill-name> .opencode/skills/
```

Global install:

```bash
mkdir -p ~/.config/opencode/skills
cp -R /absolute/path/to/agent-skills/skills/<skill-name> ~/.config/opencode/skills/
```

Portable workspace install:

```bash
mkdir -p .agents/skills
cp -R /absolute/path/to/agent-skills/skills/<skill-name> .agents/skills/
```

## Development Rules

- Keep each skill self-contained under `skills/<skill-name>/`.
- Keep root documentation generic and agent-focused.
- Do not put secrets, real `.env` values, tokens, hostnames, private IPs, or machine-specific config in committed files.
- Keep `.env.example` limited to non-secret placeholders.
- Prefer references over a large `SKILL.md` when details are only needed sometimes.
- Run validation before committing.

## Sources

- https://agentskills.io/specification
- https://agentskills.io/skill-creation/best-practices
- https://agentskills.io/clients
- https://geminicli.com/docs/cli/using-agent-skills/
- https://code.claude.com/docs/en/agent-sdk/skills
- https://opencode.ai/docs/skills

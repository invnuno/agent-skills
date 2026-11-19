# Agent Skills

Portable, version-controlled skills for coding agents that support the open
[`SKILL.md` format](https://agentskills.io/specification).

## Available skills

| Skill | Use it for |
| --- | --- |
| `home-assistant-config` | Reviewing, validating, and safely deploying Home Assistant YAML, Lovelace, Assist, and related configuration. |
| `kobo-ereader-maintenance` | Diagnosing Kobo devices, backing up or restoring internal cards, recovering a Kobo Nia, and configuring NickelMenu or a Home Assistant dashboard. |

Each skill is self-contained under `skills/<skill-name>/`. Install only the
skills relevant to the agent and project.

## Repository structure

```text
skills/
├── home-assistant-config/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/
│   └── scripts/
└── kobo-ereader-maintenance/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── references/
    └── scripts/
```

`SKILL.md` contains discovery metadata and the core workflow. Detailed or
conditional guidance belongs in `references/`; deterministic helpers belong in
`scripts/`. Optional client metadata belongs in `agents/` and does not change
the portable skill instructions.

## Install or link skills

Clone this repository, then set a local variable rather than embedding the
clone location in configuration or documentation:

```bash
AGENT_SKILLS_ROOT=$(pwd)
```

### Codex and portable workspace discovery

Codex discovers project skills from `.agents/skills/` and user skills from
`~/.agents/skills/`. Link a skill while developing:

```bash
mkdir -p .agents/skills
ln -s "$AGENT_SKILLS_ROOT/skills/kobo-ereader-maintenance" \
  .agents/skills/kobo-ereader-maintenance
```

For user-wide discovery, use `~/.agents/skills/` as the destination. Restart or
begin a new agent session after installing or updating a skill.

### Other coding agents

Agents may use different discovery directories. Copy or link the complete
skill directory—never only `SKILL.md`—into the directory documented by the
client. Common project-local locations include:

- Claude Code: `.claude/skills/`
- Gemini CLI and OpenCode portable discovery: `.agents/skills/`
- OpenCode native discovery: `.opencode/skills/`

The core skill packages do not depend on a specific coding-agent runtime.

## Optional local environment

The Home Assistant helper can read credentials from process environment
variables or an explicitly selected environment file. For local development:

```bash
cp .env.example .env
```

`.env` is ignored and must never be committed, printed, or shared. The Kobo
skill does not require repository-level credentials.

## Validate

Install the development dependency in an isolated environment, then run all
checks:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests
python3 scripts/validate_skills.py
```

The validator checks skill structure, references, optional Codex metadata,
script permissions, and tracked content for common secrets, personal paths,
private addresses, and unsafe artifacts. It reports rule identifiers and
locations without echoing suspected secret values.

## Development rules

- Follow progressive disclosure and keep each skill self-contained.
- Use placeholders or environment variables instead of personal paths,
  addresses, hostnames, device identifiers, or credentials.
- Platform-defined paths may be used when they are intrinsic to the workflow
  and are clearly documented.
- Do not commit `.env`, setup state, logs, raw disk images, update archives,
  databases, or downloaded application binaries.
- Run validation before every commit. See [CONTRIBUTING.md](CONTRIBUTING.md)
  and [SECURITY.md](SECURITY.md).

## Sources

- [Agent Skills specification](https://agentskills.io/specification)
- [Agent Skills authoring practices](https://agentskills.io/skill-creation/best-practices)
- [OpenAI skill installation guidance](https://developers.openai.com/api/reference/cli)

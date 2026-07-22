# Agent Skills

Portable Agent Skills for coding agents that support the `SKILL.md` open format.

## Skills

- `home-assistant-config-agent`: safely review, modify, validate, deploy, and troubleshoot Home Assistant YAML configuration, Lovelace dashboards, Assist sentence triggers, and local AI/Ollama workflows.

## Structure

```text
skills/
└── home-assistant-config-agent/
    ├── SKILL.md
    ├── references/
    └── scripts/
```

Each skill follows the Agent Skills format:

- `SKILL.md` with YAML frontmatter.
- `name` matches the parent directory.
- optional `references/` for progressive disclosure.
- optional `scripts/` for reusable deterministic tooling.

## Validate

```bash
python3 scripts/validate_skills.py
```

## Sources

- https://agentskills.io/specification
- https://agentskills.io/skill-creation/best-practices

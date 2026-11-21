# Repository Guidelines

## Structure

This repository contains portable Agent Skills. Every immediate child of
`skills/` is one independently installable skill and must contain exactly one
`SKILL.md` with matching lowercase kebab-case `name` frontmatter.

- Put activation metadata and the core workflow in `SKILL.md`.
- Put conditional detail in one-level `references/` files and route to each
  reference from `SKILL.md`.
- Put deterministic reusable helpers in `scripts/` and keep executable files
  executable.
- Put optional client metadata in `agents/`; keep core instructions
  client-neutral.
- Keep installation and contributor documentation at the repository root. A
  concise per-skill README is allowed for package onboarding or architecture
  when useful; keep detailed operational instructions in references.

## Commands

- `python3 scripts/validate_skills.py` validates every skill and audits tracked
  content for privacy/security violations.
- `python3 -m unittest discover -s tests` runs validator tests.
- `python3 -m py_compile scripts/validate_skills.py` checks Python syntax.
- `bash -n skills/*/scripts/*.sh` checks shell syntax when shell helpers exist.
- `rg --files skills` inventories skill package contents.

There is no application build step.

## Style

Write concise, task-oriented Markdown. Descriptions must explain both capability
and activation boundary. Add only instructions that change agent decisions.
Prefer focused references over a large entrypoint.

Python uses four-space indentation, type hints, `pathlib.Path`, small functions,
and explicit errors. Shell uses Bash strict mode, quoted variables, `--help`,
non-interactive interfaces, dry runs for stateful operations, and actionable
exit statuses.

## Safety and privacy

Never commit secrets, real `.env` values, personal paths, private hostnames or
addresses, email addresses, device serials, private image checksums, setup
state, logs, raw images, downloaded binaries, or machine-specific config.
Standard platform paths are allowed when technically required. Validators must
never print a suspected secret value.

Inspect exact targets before destructive operations, preserve authorization
boundaries, and test stateful helpers through dry runs or disposable fixtures.

## Commits and pull requests

Use short imperative commit subjects and keep commits focused. Pull requests
must identify changed skills/tooling, validation commands, dependencies,
security-sensitive behavior, and unresolved assumptions.

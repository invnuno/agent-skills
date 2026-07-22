# Repository Guidelines

## Project Structure & Module Organization

This repository stores portable Agent Skills. Each skill lives under `skills/<skill-name>/` and must include a `SKILL.md` file with YAML frontmatter. Optional deep reference material belongs in `skills/<skill-name>/references/`; reusable helper commands belong in `skills/<skill-name>/scripts/`. Keep human installation guidance in `README.md`, agent contributor rules in `AGENTS.md`, and skill-specific operating instructions inside the relevant skill directory.

Current layout:

- `skills/home-assistant-config/` - Home Assistant skill package.
- `scripts/validate_skills.py` - repository validator for skill metadata.
- `README.md` - installation, linking, and development overview.

## Build, Test, and Development Commands

- `python3 scripts/validate_skills.py` - validates that every directory in `skills/` has a valid `SKILL.md`, matching `name`, and non-empty `description`.
- `python3 -m py_compile scripts/validate_skills.py` - checks the validator for Python syntax errors after edits.
- `rg --files skills` - quickly inspect skill package contents before changing structure.

There is no build step; this repository is documentation and lightweight Python tooling.

## Coding Style & Naming Conventions

Use Markdown for skill instructions and keep sections task-oriented. Skill directory names and `name` frontmatter must match and use lowercase kebab case, for example `home-assistant-config`. Keep `description` concise and activation-focused. For Python, follow the existing style: 4-space indentation, type hints where useful, `pathlib.Path` for filesystem paths, and small validation functions with explicit error messages.

Follow Agent Skills progressive disclosure: keep `SKILL.md` focused on activation and core workflow, move conditional or detailed procedures into one-level `references/`, and avoid auxiliary files such as per-skill `README.md` unless explicitly required by the skill format.

## Testing Guidelines

Run `python3 scripts/validate_skills.py` before committing any skill changes. When editing Python scripts, also run `python3 -m py_compile` on the changed file. For new skills, confirm the validator accepts the frontmatter and manually review that optional `references/` and `scripts/` files are reachable from `SKILL.md` only when needed.

## Commit & Pull Request Guidelines

Recent commits use short, imperative messages such as `Rename Home Assistant skill` and `Document agent skill setup`. Follow that style: one focused change per commit, with a clear verb and object. Pull requests should describe the changed skill or tooling, list validation commands run, and call out any new assumptions, external dependencies, or security-sensitive behavior.

## Security & Configuration Tips

Do not commit secrets, tokens, `.env` values, private hostnames, private IPs, or machine-specific config. Keep live credentials and deployment details out of skills unless they are generic placeholders or documented as environment variables.

# Contributing

## Add or update a skill

1. Create or edit `skills/<skill-name>/SKILL.md` using lowercase kebab case.
2. Keep the entrypoint concise; move task-specific detail into directly linked
   references.
3. Add scripts only when deterministic execution materially improves safety or
   reliability.
4. Use placeholders and environment variables for user-specific input.
5. Run the full validation suite before committing.

Do not add per-skill READMEs, copied vendor manuals, downloaded binaries, live
configuration, or credentials. Keep automatic skill selection enabled unless a
skill explicitly requires opt-in invocation.

## Validate

```bash
python3 -m unittest discover -s tests
python3 scripts/validate_skills.py
python3 -m py_compile scripts/validate_skills.py
```

Also run `bash -n` and `--help` smoke tests for changed shell helpers. Test
destructive workflows only with dry runs, disposable fixtures, or explicit
authorized media.

## Review checklist

- The skill name matches its directory and the description routes accurately.
- Every referenced local file exists and no reference chain is unnecessarily
  deep.
- Scripts have documented dependencies, safe defaults, and helpful failures.
- No tracked file contains confidential, personal, or machine-specific data.
- The change is covered by focused tests or an explained manual verification.

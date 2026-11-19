# Security policy

## Sensitive information

Do not open a public issue containing a credential, private host, device image,
serial number, personal path, log with private state, or other confidential
data. Use the repository's private security-reporting feature when available.

If sensitive data is committed, revoke or rotate the exposed credential first.
Removing it in a later commit does not remove it from Git history. Coordinate a
history rewrite only after the secret is invalidated and affected collaborators
have been notified.

## Skill safety

Treat skill scripts as executable code. Review target selection, network use,
credential handling, destructive operations, and bundled artifacts before
installing a skill. Raw-device helpers must require an exact target and an
explicit confirmation immediately before writing.

Repository validation detects common problems but cannot prove that content is
non-sensitive. Authors remain responsible for reviewing diffs and generated
artifacts before publication.

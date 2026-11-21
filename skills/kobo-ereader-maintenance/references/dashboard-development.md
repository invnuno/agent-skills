# Dashboard source development

Use this workflow for repeated changes to Kobo HA Dashboard source, layout configuration, device deployment, or runtime diagnosis. It complements the release setup workflow; it does not replace USB installation or recovery.

## Prefer the project workflow

From the authoritative dashboard source repository, check for an executable `tools/kobo-dashboard`. When present:

1. Read the repository's `AGENTS.md` and the tool's `--help`.
2. Run `tools/kobo-dashboard doctor` to validate local tooling and read-only device access.
3. Run `tools/kobo-dashboard plan --scope auto` to classify the change.
4. Use the smallest matching operation below.

Do not copy the source into a temporary directory or reconstruct Podman, cross-compilation, SSH, SCP, checksum, restart, or rollback commands. A project workflow captures version-specific behavior that this portable skill should not duplicate.

## Change scopes

- Configuration or layout only: preview, then deploy `config` without rebuilding Rust.
- Rust, embedded assets, or translations: run checks, build the ARM artifact, then deploy `binary`.
- Launcher, Wi-Fi, or NickelMenu entry: deploy `support` files only.
- Mixed or uncertain changes: use `auto`; let artifact hashes select the required work.
- Home Assistant diagnosis: use only the project's read-only entity and service inspection. Creating helpers, integrations, or automations is a distinct Home Assistant change and requires explicit authorization.

Use the setup UI preview for layout approval before a live deployment. Do not control real household devices merely to verify rendering or request construction unless the user explicitly authorizes that test.

## Mutation boundaries

Treat `plan`, `doctor`, `verify`, status, and ordinary log inspection as read-only. Preview startup may create local build/cache artifacts. Device deployment, restart, rollback, USB installation, and Home Assistant changes are mutations and require matching user intent.

Prefer tools whose deployment and rollback modes are dry-run by default. Before applying a live change, confirm the target device resolved through the configured SSH alias or mounted Kobo and review the exact artifact scope. Never print connection secrets or the contents of dashboard configuration.

## Completion

For a live SSH deployment, require all of the following:

- The remote artifact checksum matches the intended local artifact.
- A timestamped rollback copy exists for every replaced file.
- The dashboard process runs the expected executable.
- The recent log confirms a Home Assistant WebSocket subscription.
- The recent log contains no startup or service-call errors.

When the repository has no project workflow, fall back to [dashboard-podman.md](dashboard-podman.md) for setup/preview and the version-matched upstream build and install scripts. Keep the same authorization, privacy, backup, and verification boundaries.

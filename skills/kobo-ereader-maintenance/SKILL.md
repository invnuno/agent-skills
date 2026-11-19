---
name: kobo-ereader-maintenance
description: Diagnose and maintain Kobo e-readers at the system level, including USB detection, raw microSD backup or restore, Kobo Nia N306 recovery, NickelMenu configuration, and Kobo Home Assistant dashboard installation or layout changes. Use for recovery and customization tasks, not ordinary ebook transfers or library management.
license: MIT
metadata:
  version: "1.0.0"
---

# Kobo E-Reader Maintenance

Use the smallest workflow that matches the request. Inspect first and keep read-only diagnosis separate from authorized mutations.

## Environment

The knowledge is client-neutral. Bundled helpers target Linux and require Bash, coreutils, and util-linux; Nia recovery also requires e2fsprogs, while dashboard setup requires Podman and network access. Raw block-device operations require root. If those tools are unavailable, use the references to guide an equivalent workflow without weakening the safety checks.

## Route the task

- For USB detection, mount discovery, firmware identification, or storage inspection, read [references/device-identification.md](references/device-identification.md).
- For raw microSD backup or ordinary image restore, read [references/backup-restore.md](references/backup-restore.md) before running `scripts/kobo-card-image.sh`.
- For a Kobo Nia N306 that flashes, boot-loops, or needs a factory-recovery card, also read [references/nia-recovery.md](references/nia-recovery.md). Do not apply that workflow to another model.
- For the Home Assistant dashboard setup tool in Podman, read [references/dashboard-podman.md](references/dashboard-podman.md).
- For adding or changing NickelMenu entries, read [references/nickelmenu.md](references/nickelmenu.md).
- For dashboard pages, cards, display, sleep, battery, or Home Assistant settings, read [references/dashboard-layout.md](references/dashboard-layout.md).
- For failures after installation or firmware updates, read [references/troubleshooting.md](references/troubleshooting.md).

## Safety invariants

- Resolve the exact whole-disk target with read-only inspection. Never infer a target from `/dev/sdX` examples, ordering, or capacity alone.
- Immediately before a raw-device write, show the resolved device identity, partitions, size, transport, and mounts, then obtain explicit authorization for that exact device. Prior approval for diagnosis or backup is not approval to overwrite media.
- Preserve the original Kobo card and its verified image whenever possible. Prefer restoring to a separate card.
- Require a trusted SHA-256 value for every restore. Verify the completed write byte-for-byte.
- Never download, share, or embed a Kobo disk image unless the user has the right to use it. Full images can contain device identity, calibration, account, Wi-Fi, and library data.
- Never display Home Assistant tokens or the contents of `.kobo-ha/config.yaml`. Report only presence, size, mode, or a redacted summary.
- Do not edit `.adds/nm/doc`; NickelMenu replaces it during updates. Put personal entries in a uniquely named file such as `.adds/nm/local-custom`.
- Safely unmount/eject before disconnecting. If the environment cannot access the desktop storage service, say so and give the user the manual eject step.

## Helpers

- `scripts/kobo-device-info.sh [--mount PATH] [--json]` performs read-only mounted-device discovery.
- `scripts/kobo-card-image.sh inspect|backup|restore|prepare-nia-recovery ...` handles guarded raw-card operations. Read its `--help` and use `--dry-run` before a mutating mode.
- `scripts/run-dashboard-setup-podman.sh --app-dir DIR [--kobo-mount PATH]` runs a downloaded dashboard setup binary in a compatible Fedora container.
- `scripts/verify-dashboard-install.sh --mount PATH [--json]` verifies installation without exposing configuration contents.

Use paths relative to this skill directory when invoking bundled scripts. Do not substitute repository-local legacy scripts unless the user explicitly asks to use them.

## Completion checks

- For backups: report image path, byte size, SHA-256 path/value, metadata paths, and byte-verification success.
- For restores: report source checksum verification, exact target, bytes written, byte-verification success, and whether Nia recovery was armed.
- For dashboard installs: verify files, eject, allow any pending NickelMenu update to finish, then confirm that the menu entry opens the dashboard and live Home Assistant data loads.
- When troubleshooting: preserve `dashboard.log` and `dashboard.log.old`, but inspect them for secrets before quoting or sharing.

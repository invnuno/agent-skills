# Dashboard layout and operation

Prefer the setup tool for normal changes. Direct YAML editing is useful for review, automation, or options not exposed by the UI, but the setup tool provides a pixel-accurate preview and catches cards that do not fit.

## Setup-tool workflow

1. Start the Podman setup workflow from `references/dashboard-podman.md`.
2. On **Connect**, test Home Assistant connectivity and select the Kobo model, portrait/landscape orientation, language, theme, clock, refresh, frontlight, sleep, and battery settings.
3. On **Design**, import a Lovelace dashboard or generate pages from Home Assistant areas.
4. Treat import as a starting point. Unsupported Lovelace/custom cards are skipped rather than emulated.
5. Keep page labels short, move overflow cards to another page, and verify every page in the exact Kobo preview.
6. Save before **Install** or **Update**.

For a Kobo Nia's monochrome 6-inch screen, start with portrait, high-contrast black and white, short page names, and only the most frequently used controls. Split dense pages rather than shrinking controls.

## Configuration file

The installed configuration is `.kobo-ha/config.yaml`. The release's `config.example.yaml` is the version-matched schema and card reference. Read that file before hand editing; do not assume keys from another release.

Major sections are:

- `device`: model preview, orientation, full-refresh cadence, framebuffer/touch overrides, frontlight timeout, sleep, and critical-battery behavior.
- `home_assistant`: reachable URL, token, refresh/timeout, optional battery reporting, and demo fallback.
- `theme`: e-ink theme, accent, language, clock, and timezone behavior.
- `pages`: ordered tabs containing native dashboard cards.

Common native cards include weather, lights, switches, fans, climate controls, sensors, sensor grids, media players, scene/script rows, headings, statistics, and image entities. Confirm the exact release's support in its example configuration.

## Home Assistant and secrets

- Use an address the Kobo can reach directly; prefer a DHCP-reserved IP over `.local`.
- Use HTTPS when the local deployment supports it correctly.
- Use a dedicated token with the least privilege available. Battery reporting needs elevated rights in current dashboard releases; disable it if that tradeoff is not acceptable.
- Never quote, log, commit, or paste the token into issue reports.
- Before sharing `config.yaml`, replace the token and private hostnames/IPs with placeholders.

## E-ink and power defaults

- A 60-second periodic refresh is a reasonable starting point because Home Assistant changes also arrive over WebSocket.
- Enable periodic full refreshes to control ghosting rather than forcing a full flash on every update.
- Use a short frontlight timeout for a desk or wall panel.
- Sleep mode significantly improves battery life, but the dashboard deliberately avoids suspend in conditions known to be unsafe, such as charging on some models or incompatible Wi-Fi/Bluetooth states.
- Keep the critical-battery protection enabled unless the installation has a separate reliable charging strategy.

## Timezone

Prefer the setup tool's POSIX `TZ` rule in the launcher so daylight-saving changes remain correct without a timezone database on the Kobo. Avoid a fixed `theme.utc_offset` unless the user explicitly wants a fixed offset; it can become wrong after a seasonal clock change.

## Manual edit procedure

1. Back up `config.yaml` without displaying its token.
2. Edit a computer-side copy with restrictive permissions.
3. Validate YAML syntax and compare keys with the matching release's `config.example.yaml`.
4. Re-run the setup tool and use **Load its config** when possible to preview the result.
5. Install/update, verify with `scripts/verify-dashboard-install.sh`, and eject safely.

## Source

- [Kobo HA Dashboard configuration and usage](https://github.com/armamut/kobo-ha-dashboard)


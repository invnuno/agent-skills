# Troubleshooting

Start with read-only evidence. Do not combine diagnosis with a raw restore unless the user explicitly asks to perform the repair.

## Dashboard does not appear in the menu

1. Connect by USB and run `scripts/verify-dashboard-install.sh --mount PATH`.
2. If the dashboard files and menu entry exist but `.adds/nm/doc` does not, a firmware update probably removed NickelMenu. Re-run the setup tool and reinstall NickelMenu.
3. If `KoboRoot.tgz` or `Kobo.tgz` is pending, eject and let the Kobo finish the update/restart; do not copy another update package over it.
4. If the menu file is missing, use **Update** in the setup tool rather than reconstructing its generated command from memory.

## Dashboard opens but says Offline

- Confirm the Kobo is connected to a saved Wi-Fi network.
- Test the configured Home Assistant address from another device on the same network.
- Replace `.local` with a stable LAN address or resolvable DNS name.
- Confirm the token still exists and has access, without printing it.
- Check reverse-proxy scheme/port and certificate validity.
- Inspect `.kobo-ha/dashboard.log` for connection errors after redacting URLs or tokens.

## Rotation or touch mismatch

The dashboard log records detected framebuffer/input devices and tap coordinates. Compare the screen orientation with the logged tap positions, then adjust only the relevant version-supported settings:

- `device.fb_rotation`
- `device.swap_touch_xy`
- `device.invert_touch_x`
- `device.invert_touch_y`

Change one axis/rotation assumption at a time and verify in the setup preview or on-device log.

## Battery drains or sleep does not start

- Confirm sleep is enabled and read the log's explicit reason when unavailable.
- The dashboard may intentionally avoid sleep while charging, with Bluetooth enabled, or on unsupported Wi-Fi hardware.
- Reduce frontlight duration and page activity before reducing safety settings.
- Keep critical-battery protection enabled.
- If suspend causes hangs, hold power for about 15 seconds to restart, disable sleep, and preserve `dashboard.log.old` for diagnosis.

## Read-only Kobo volume

A FAT volume can remount read-only after filesystem errors or unsafe removal. Stop installation writes, eject, and repair the filesystem only after backing up accessible data. Reconnect and confirm `rw` mount options before running the setup tool. Do not force writes through a read-only mount.

## Setup tool cannot detect the Kobo

- Confirm the Kobo is in USB storage mode and `.kobo/version` is visible.
- Run `scripts/kobo-device-info.sh`.
- In Podman, ensure the selected mount, resolved block device, and `/run/udev` are exposed and the container runs as the host user.
- If the app configuration was created in an ephemeral container home, move it into the persistent `setup-home` only while protecting its token.
- Desktop eject APIs such as UDisks can be inaccessible inside a sandbox or container. Use the host file manager when automatic eject fails.

## Boot loop or flashing LED/screen

Try only model-appropriate reset/charging guidance first. If the Kobo never reaches Linux and the issue persists, preserve the internal card and follow `references/device-identification.md`. For a confirmed Nia N306 with the correct evidence, use `references/nia-recovery.md`.

Do not assume every flashing LED is firmware corruption; battery, power delivery, card seating, display, and motherboard faults remain possible.

## Logs and issue reports

The current run is normally `.kobo-ha/dashboard.log`; the previous run is `.kobo-ha/dashboard.log.old`. Before sharing:

1. Copy the files read-only.
2. Search for tokens, URLs, IPs, Wi-Fi names, paths, serials, and entity names the user considers private.
3. Redact secrets while retaining timestamps, error messages, detected hardware, and state transitions.
4. State the Kobo model, firmware, dashboard release, and whether the problem followed a firmware/dashboard update.

## Sources

- [Kobo HA Dashboard troubleshooting](https://github.com/armamut/kobo-ha-dashboard#troubleshooting)
- [NickelMenu official documentation](https://github.com/pgaskin/NickelMenu/blob/master/res/doc)


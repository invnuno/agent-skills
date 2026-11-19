# Kobo HA Dashboard setup with Podman

The dashboard project publishes a Linux setup binary, not a dedicated dashboard container image. Podman runs that downloaded binary inside a compatible Fedora userspace while exposing the mounted Kobo and its USB block device.

## Obtain the application

1. Use the [official Kobo HA Dashboard releases](https://github.com/armamut/kobo-ha-dashboard/releases).
2. Select the Linux x64 package appropriate for the host.
3. Record the chosen version and verify any checksum published by the project or release channel.
4. Extract it into a user-controlled directory. Do not bundle the binary in this skill.

Do not hard-code the release described as “latest”; discover the current upstream release at execution time. Keep an already tested release when recovery stability is more important than new features.

## Start the setup tool

Connect the running Kobo by USB, tap **Connect**, and confirm that the volume is mounted read-write. Then run:

```bash
APP_DIR=${APP_DIR:?Set APP_DIR to the extracted release directory}

scripts/run-dashboard-setup-podman.sh \
  --app-dir "$APP_DIR" \
  --dry-run
```

Review the resolved mount, block device, persistent configuration directory, container image, and complete Podman command. Repeat without `--dry-run`, keep the terminal open, and visit `http://127.0.0.1:3000`.

The proven default is `docker.io/library/fedora:44`. Override `--image` only when the downloaded binary requires a different glibc/userspace and after verifying the image source.

## Container behavior

The helper:

- Uses host networking so the local UI and Home Assistant LAN address are reachable.
- Runs as the invoking UID/GID with a persistent `setup-home` under the application directory.
- Exposes only the selected Kobo mount, its resolved block device, the application directory, and `/run/udev` when present.
- Disables SELinux relabeling for these explicit bind mounts.
- Does not print the saved Home Assistant token.

The setup state under `setup-home/.config/kobo-ha-dashboard/` is sensitive because it can contain a long-lived token. Keep permissions restrictive and do not commit or share it.

## Configure and install

1. Enter a Home Assistant URL reachable from the Kobo. Prefer a reserved LAN IP; Kobo does not reliably resolve `.local` mDNS names.
2. Use a dedicated long-lived token with the least privilege compatible with the selected features. Battery reporting currently needs an administrator token; leave it disabled to avoid that privilege.
3. Select the correct model, orientation, theme, timezone behavior, refresh, light, and sleep settings.
4. Build or import a dashboard, resolve preview overflow warnings, and save.
5. On **Install**, select the detected Kobo and install or update. Let the tool stage NickelMenu when missing.
6. Run `scripts/verify-dashboard-install.sh --mount PATH` before ejecting.
7. Eject safely. A newly staged NickelMenu update installs during the next restart.

## Updating later

Reconnect the Kobo, run the same setup release or a deliberately chosen newer release, use **Load its config**, edit and save, then click **Update**. Re-run verification and eject. A Kobo firmware update can remove NickelMenu even when `.kobo-ha` remains; reinstall NickelMenu through the tool.

## Sources

- [Kobo HA Dashboard README](https://github.com/armamut/kobo-ha-dashboard)
- [Kobo HA Dashboard releases](https://github.com/armamut/kobo-ha-dashboard/releases)


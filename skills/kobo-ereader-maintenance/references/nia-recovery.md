# Kobo Nia N306 factory recovery

Use this only for a confirmed Kobo Nia N306 with a removable internal microSD and a trusted full-device image containing an intact Nia recovery filesystem. Other Kobo models can use different storage, partitioning, SoCs, and boot environments.

## When this workflow applies

Typical evidence includes repeated LED/screen flashes, failure to reach the Kobo UI, early USB download-gadget enumeration, and an externally inspected card whose main root filesystem is corrupt while the recovery filesystem remains readable.

An ordinary clone of a corrupt image reproduces the corruption. The Nia recovery workflow instead clones the full image and writes the recovery U-Boot environment already stored inside its recovery partition, causing a one-time factory restore on the next boot.

## Validated Nia image invariants

The bundled helper requires all of these before it writes a target:

- DOS/MBR-style image with the recovery partition beginning at sector `573441`.
- Recovery partition length `524289` sectors.
- An ext filesystem containing `/etc/u-boot/mx6ull-ntx/u-boot.recovery`.
- Recovery environment size exactly `131072` bytes.
- The environment is written at `128 KiB × 6` and verified by read-back.

These values are intentionally model-specific. Do not weaken the checks to make an unrelated image pass.

## Prepare a replacement recovery card

Use a replacement card at least as large in bytes as the image and keep the original untouched:

```bash
DEVICE=${DEVICE:?Set DEVICE to the whole replacement disk}
IMAGE=${IMAGE:?Set IMAGE to the trusted Kobo Nia image}

sudo scripts/kobo-card-image.sh prepare-nia-recovery \
  --device "$DEVICE" \
  --image "$IMAGE" \
  --sha256-file "$IMAGE.sha256" \
  --confirm "ERASE-$DEVICE" \
  --dry-run
```

Review the source validation and target identity. After the user explicitly authorizes that exact target, repeat without `--dry-run`.

## First recovery boot

1. Power off and disconnect the Kobo battery.
2. Install the verified replacement card.
3. Reconnect the battery and close or safely support the back cover.
4. Connect a wall charger and press the power button once.
5. Do not interrupt screen flashes, restarts, or the factory restore.
6. Complete normal Kobo setup after the reader reaches the UI.

If it still loops, stop repeated power cycling. Recheck the written card in the external reader, preserve logs/observations, and reconsider battery, card-reader reliability, card seating, or hardware failure.

## Firmware updates

A successful recovery can later accept a normal Kobo update. Firmware updates may remove NickelMenu, so reinstall NickelMenu through the dashboard setup tool afterward. Do not downgrade merely because NickelMenu disappeared.

## Image provenance

Prefer the user's own verified image. Do not bundle, publish, or silently fetch Nia images. A third-party image can contain another device's identifiers or calibration and may not be lawful or safe to redistribute.

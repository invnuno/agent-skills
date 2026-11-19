# Raw-card backup and restore

Use this workflow for a removable internal Kobo microSD connected to a Linux computer through a card reader. Read `references/device-identification.md` first.

## Data handling

A raw image can contain the Kobo serial, display calibration, account state, Wi-Fi information, sideloaded books, annotations, and other personal data. Store it as sensitive data. Do not upload or redistribute it as a generic firmware image.

Prefer this order:

1. Preserve and label the original card.
2. Back it up while unmounted.
3. Record a cryptographic checksum and device/partition metadata.
4. Verify the image byte-for-byte against the source.
5. Restore to a separate card of at least the same byte size.

## Backup

Review the exact device first:

```bash
DEVICE=${DEVICE:?Set DEVICE to the whole removable disk}
BACKUP=${BACKUP:?Set BACKUP to the destination image path}

sudo scripts/kobo-card-image.sh inspect --device "$DEVICE"
sudo scripts/kobo-card-image.sh backup \
  --device "$DEVICE" \
  --output "$BACKUP" \
  --confirm "READ-$DEVICE" \
  --dry-run
```

When the dry run is correct, repeat without `--dry-run`. The helper creates and verifies:

- `kobo-backup.img`
- `kobo-backup.img.sha256`
- `kobo-backup.img.sfdisk`
- `kobo-backup.img.lsblk.txt`

Do not treat an image as good merely because `dd` exited successfully. Require the byte comparison and checksum file.

## Ordinary restore

Use a checksum recorded when the trusted image was created, not a checksum computed from an untrusted download immediately before writing it.

```bash
DEVICE=${DEVICE:?Set DEVICE to the whole replacement disk}
IMAGE=${IMAGE:?Set IMAGE to the trusted backup image}

sudo scripts/kobo-card-image.sh restore \
  --device "$DEVICE" \
  --image "$IMAGE" \
  --sha256-file "$IMAGE.sha256" \
  --confirm "ERASE-$DEVICE" \
  --dry-run
```

After explicit authorization for the exact target, repeat without `--dry-run`. The helper validates the checksum and capacity, performs a one-sector persistence test, writes the image, flushes the reader, and byte-compares the written range.

Writing a smaller image to a larger card leaves the additional space unused. Expanding the final user-data partition is optional and should happen only after the restored card boots successfully and another verified image remains available.

## Failure handling

- If even the first sector does not read back, stop and change the card or reader.
- If the final comparison fails, do not install the card in the Kobo as a known-good restore.
- If the image is from a failing card, a successful byte backup preserves the failure state; it does not repair corrupted filesystems.
- Do not run filesystem repair against the only original copy. Clone first, then repair a copy if appropriate.
- A factory reset is different from a raw restore: it erases user state but cannot repair an unreadable or corrupt root filesystem.

## Physical handling

Power the Kobo off, disconnect the battery before removing or inserting its internal card, avoid bending the display substrate, and reconnect the battery only after the card is seated. Opening procedures vary by model.

For a visual Nia card-replacement example, see [Kobo Nia – MicroSD Card Upgrade](https://www.youtube.com/watch?v=_ZyEXQcfPZg). Treat third-party videos as physical guidance, not as a source for firmware images or device selection.

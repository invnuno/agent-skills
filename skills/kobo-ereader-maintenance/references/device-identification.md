# Device identification

Read this before selecting a Kobo USB volume or raw microSD card.

## Mounted Kobo over USB

1. Ask the user to connect the running Kobo, tap **Connect**, and wait for the `KOBOeReader` volume.
2. Run `scripts/kobo-device-info.sh` without arguments, or pass `--mount PATH` when more than one candidate exists.
3. Corroborate the result with `findmnt`, `lsblk`, and, when available, `lsusb`. A mounted Kobo normally exposes a FAT filesystem containing `.kobo/version`.
4. Treat the filesystem source (often a partition or USB gadget device) separately from an internal microSD connected through a card reader. Never assume that yesterday's `/dev/sdb` is today's target.

The helper intentionally extracts firmware without printing the full `.kobo/version` line because that line can include the device serial.

## Raw internal microSD

With the Kobo powered off and battery disconnected before card removal:

```bash
lsblk -p -o NAME,SIZE,MODEL,SERIAL,TRAN,RM,RO,TYPE,FSTYPE,LABEL,MOUNTPOINTS
sudo scripts/kobo-card-image.sh inspect --device /dev/DEVICE
```

Identify the card using multiple facts: reader model/serial, capacity, transport, removable flag, partition count, filesystems, and what appeared after insertion. Unmount every partition before backup or restore. Do not run a raw-card command against a partition such as `/dev/sdb1`; use the whole disk such as `/dev/sdb`.

## Early boot USB mode

An NXP/Freescale USB download gadget can indicate that the device reached the SoC's early recovery/download mode but did not boot Linux. It does not prove which component failed. Preserve the card, inspect it externally, and prefer a verified backup before repair attempts.

## Stop conditions

Stop and ask for clarification when:

- More than one device could be the Kobo or card reader.
- The candidate backs `/`, `/home`, the workspace, swap, or another live system filesystem.
- The target is mounted, read-only, or unexpectedly reports a different capacity or partition table.
- The model is not confirmed before a model-specific recovery procedure.

## Sources

- [Kobo Nia user guide](https://cdn.kobo.com/downloads/magento/userguides/KoboNia/Kobo_Nia_User_Guides_%28all_languages%29_June_16_2020_Final/Kobo-Nia-User-Guide-EN-%28English%29.pdf)
- [Kobo HA Dashboard device support](https://github.com/armamut/kobo-ha-dashboard#supported-devices)


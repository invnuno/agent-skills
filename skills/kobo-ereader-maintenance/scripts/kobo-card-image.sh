#!/usr/bin/env bash
set -euo pipefail

readonly NIA_RECOVERY_START=573441
readonly NIA_RECOVERY_SECTORS=524289
readonly NIA_RECOVERY_ENV_BYTES=131072

usage() {
  cat <<'EOF'
Usage:
  kobo-card-image.sh inspect (--device /dev/DEVICE | --image FILE)
  sudo kobo-card-image.sh backup --device /dev/DEVICE --output FILE \
    --confirm READ-/dev/DEVICE [--overwrite-output] [--dry-run]
  sudo kobo-card-image.sh restore --device /dev/DEVICE --image FILE \
    (--sha256 HASH | --sha256-file FILE) --confirm ERASE-/dev/DEVICE [--dry-run]
  sudo kobo-card-image.sh prepare-nia-recovery --device /dev/DEVICE --image FILE \
    (--sha256 HASH | --sha256-file FILE) --confirm ERASE-/dev/DEVICE [--dry-run]

Commands:
  inspect               Read-only identity and partition-table inspection.
  backup                Create and byte-verify a full raw image plus metadata.
  restore               Checksum, write, and byte-verify a full raw image.
  prepare-nia-recovery  Restore a Kobo Nia N306 image, then arm its one-time
                        factory-recovery U-Boot environment.

Safety:
  Mutating target operations only accept an unmounted, writable whole disk
  reported as removable or USB. System disks are refused. --dry-run performs
  validation but does not read the full target or write anything.

Backup output files:
  FILE, FILE.sha256, FILE.sfdisk, FILE.lsblk.txt

Exit codes:
  2 invalid arguments; 3 missing dependency/input; 4 unsafe target;
  5 checksum/layout validation failure; 6 copy/verification failure.
EOF
}

die() {
  local code=$1
  shift
  printf 'Error: %s\n' "$*" >&2
  exit "$code"
}

need() {
  command -v "$1" >/dev/null 2>&1 || die 3 "required command not found: $1"
}

[[ $# -ge 1 ]] || { usage >&2; exit 2; }
command_name=$1
shift
case $command_name in
  inspect|backup|restore|prepare-nia-recovery) ;;
  -h|--help) usage; exit 0 ;;
  *) die 2 "unknown command: $command_name" ;;
esac

device=
image=
output=
expected_sha=
sha_file=
confirmation=
overwrite_output=false
dry_run=false

while (($#)); do
  case $1 in
    --device) [[ $# -ge 2 ]] || die 2 "--device needs a value"; device=$2; shift 2 ;;
    --image) [[ $# -ge 2 ]] || die 2 "--image needs a value"; image=$2; shift 2 ;;
    --output) [[ $# -ge 2 ]] || die 2 "--output needs a value"; output=$2; shift 2 ;;
    --sha256) [[ $# -ge 2 ]] || die 2 "--sha256 needs a value"; expected_sha=$2; shift 2 ;;
    --sha256-file) [[ $# -ge 2 ]] || die 2 "--sha256-file needs a value"; sha_file=$2; shift 2 ;;
    --confirm) [[ $# -ge 2 ]] || die 2 "--confirm needs a value"; confirmation=$2; shift 2 ;;
    --overwrite-output) overwrite_output=true; shift ;;
    --dry-run) dry_run=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die 2 "unknown argument: $1" ;;
  esac
done

for cmd in lsblk findmnt sfdisk stat realpath; do need "$cmd"; done

resolve_device() {
  [[ -n $device ]] || die 2 "--device is required"
  [[ $device == /dev/* ]] || die 2 "device must be an explicit /dev path"
  device=$(realpath -e -- "$device")
  [[ -b $device ]] || die 3 "$device is not a block device"
}

show_device() {
  lsblk -p -o NAME,SIZE,MODEL,SERIAL,TRAN,RM,RO,TYPE,FSTYPE,LABEL,MOUNTPOINTS "$device"
}

refuse_system_disk() {
  local path source
  for path in / /home "$PWD"; do
    [[ -e $path ]] || continue
    source=$(findmnt -nro SOURCE --target "$path" 2>/dev/null || true)
    source=${source%%\[*}
    [[ $source == /dev/* && -b $source ]] || continue
    if lsblk -s -nrpo NAME "$source" 2>/dev/null | grep -Fxq "$device"; then
      die 4 "$device backs $path and is a system/workspace disk"
    fi
  done
}

validate_target_disk() {
  local type readonly removable transport mounted
  type=$(lsblk -dno TYPE "$device" | tr -d '[:space:]')
  readonly=$(lsblk -dno RO "$device" | tr -d '[:space:]')
  removable=$(lsblk -dno RM "$device" | tr -d '[:space:]')
  transport=$(lsblk -dno TRAN "$device" | tr -d '[:space:]')
  [[ $type == disk ]] || die 4 "$device is not a whole disk"
  [[ $readonly == 0 ]] || die 4 "$device is read-only"
  [[ $removable == 1 || $transport == usb ]] || \
    die 4 "$device is neither removable nor transported over USB"
  refuse_system_disk
  mounted=$(lsblk -nrpo MOUNTPOINT "$device" | awk 'NF {print; exit}')
  [[ -z $mounted ]] || die 4 "$device or one of its partitions is mounted at $mounted"
}

resolve_image() {
  [[ -n $image ]] || die 2 "--image is required"
  image=$(realpath -e -- "$image")
  [[ -f $image ]] || die 3 "$image is not a regular file"
}

load_expected_sha() {
  if [[ -n $expected_sha && -n $sha_file ]]; then
    die 2 "use only one of --sha256 or --sha256-file"
  fi
  if [[ -n $sha_file ]]; then
    sha_file=$(realpath -e -- "$sha_file")
    read -r expected_sha _ < "$sha_file" || die 5 "could not read $sha_file"
  fi
  [[ $expected_sha =~ ^[0-9a-fA-F]{64}$ ]] || \
    die 2 "a 64-character trusted checksum is required with --sha256 or --sha256-file"
  expected_sha=${expected_sha,,}
}

verify_source_image() {
  local actual
  need sha256sum
  printf 'Verifying source image checksum...\n' >&2
  actual=$(sha256sum "$image" | awk '{print $1}')
  [[ $actual == "$expected_sha" ]] || \
    die 5 "checksum mismatch: expected $expected_sha, got $actual"
  printf 'Source checksum verified: %s\n' "$actual" >&2
}

validate_capacity() {
  local image_size device_size
  image_size=$(stat -c %s "$image")
  device_size=$(lsblk -dnbo SIZE "$device")
  ((device_size >= image_size)) || \
    die 4 "target is too small: $device_size bytes; image is $image_size bytes"
}

require_root() {
  [[ $(id -u) -eq 0 ]] || die 4 "this command must run as root (usually with sudo)"
}

confirm_exact() {
  local expected=$1
  [[ $confirmation == "$expected" ]] || \
    die 4 "confirmation mismatch; pass --confirm '$expected' after reviewing the device"
}

write_and_verify_image() {
  local image_size
  image_size=$(stat -c %s "$image")
  need dd
  need cmp
  need blockdev

  printf 'Testing one direct sector write after authorization...\n' >&2
  dd if="$image" of="$device" bs=512 count=1 oflag=direct conv=fsync status=none
  blockdev --flushbufs "$device"
  cmp -n 512 "$image" "$device" || \
    die 6 "target did not preserve the first-sector test write; use another card or reader"

  printf 'Writing %s bytes to %s...\n' "$image_size" "$device" >&2
  dd if="$image" of="$device" bs=4M iflag=fullblock oflag=direct conv=fsync status=progress
  blockdev --flushbufs "$device"
  printf 'Byte-verifying the completed image...\n' >&2
  cmp -n "$image_size" "$image" "$device" || die 6 "target differs from the source image"
}

inspect_path() {
  local target=$1
  printf 'Target: %s\n' "$target"
  if [[ -b $target ]]; then
    lsblk -dnbo SIZE "$target" | sed 's/^/Bytes: /'
  else
    stat -c 'Bytes: %s' "$target"
  fi
  printf 'Partition table:\n'
  sfdisk --dump "$target" 2>&1 || true
  if [[ -b $target ]]; then
    printf 'Device tree:\n'
    lsblk -p -o NAME,SIZE,MODEL,SERIAL,TRAN,RM,RO,TYPE,FSTYPE,LABEL,MOUNTPOINTS "$target"
  fi
}

prepare_nia_environment() {
  local dump recovery_image recovery_env env_size
  need dd
  need debugfs
  dump=$(sfdisk --dump "$image")
  grep -Eq 'start=[[:space:]]*573441,[[:space:]]*size=[[:space:]]*524289' <<<"$dump" || \
    die 5 "image does not contain the expected Kobo Nia N306 recovery partition"

  work_dir=$(mktemp -d "${TMPDIR:-/tmp}/kobo-nia-recovery.XXXXXX")
  recovery_image=$work_dir/recoveryfs.img
  recovery_env=$work_dir/u-boot.recovery
  dd if="$image" of="$recovery_image" bs=512 skip=$NIA_RECOVERY_START \
    count=$NIA_RECOVERY_SECTORS iflag=fullblock status=none
  debugfs -R "dump /etc/u-boot/mx6ull-ntx/u-boot.recovery $recovery_env" \
    "$recovery_image" >/dev/null 2>&1 || \
    die 5 "Nia recovery environment is missing from the recovery filesystem"
  env_size=$(stat -c %s "$recovery_env")
  [[ $env_size -eq $NIA_RECOVERY_ENV_BYTES ]] || \
    die 5 "unexpected Nia recovery environment size: $env_size bytes"
  nia_recovery_env=$recovery_env
  printf 'Validated Kobo Nia recovery environment: %s bytes.\n' "$env_size" >&2
}

work_dir=
nia_recovery_env=
cleanup() {
  [[ -z ${work_dir:-} ]] || rm -rf -- "$work_dir"
}
trap cleanup EXIT

case $command_name in
  inspect)
    if [[ -n $device && -n $image ]]; then die 2 "choose either --device or --image"; fi
    if [[ -n $device ]]; then resolve_device; inspect_path "$device"
    elif [[ -n $image ]]; then resolve_image; inspect_path "$image"
    else die 2 "inspect requires --device or --image"
    fi
    ;;

  backup)
    resolve_device
    [[ -n $output ]] || die 2 "--output is required"
    output=$(realpath -m -- "$output")
    [[ -d $(dirname -- "$output") ]] || die 3 "output directory does not exist"
    [[ ! -e $output || $overwrite_output == true ]] || \
      die 4 "$output already exists; use --overwrite-output to replace it"
    require_root
    validate_target_disk
    confirm_exact "READ-$device"
    show_device
    device_size=$(lsblk -dnbo SIZE "$device")
    available=$(df -PB1 --output=avail "$(dirname -- "$output")" | tail -n1 | tr -d '[:space:]')
    ((available > device_size)) || die 4 "not enough free space for a $device_size-byte image"
    if $dry_run; then
      printf 'Dry run: would back up %s to %s and byte-verify it.\n' "$device" "$output"
      exit 0
    fi
    need dd; need cmp; need sha256sum; need blockdev
    partial=$output.partial
    [[ ! -e $partial || $overwrite_output == true ]] || die 4 "$partial already exists"
    printf 'Reading %s into %s...\n' "$device" "$partial" >&2
    dd if="$device" of="$partial" bs=4M iflag=fullblock conv=fsync status=progress
    blockdev --flushbufs "$device"
    [[ $(stat -c %s "$partial") -eq $device_size ]] || die 6 "backup size does not match the source device"
    printf 'Byte-verifying backup against the source device...\n' >&2
    cmp -n "$device_size" "$partial" "$device" || die 6 "backup differs from the source device"
    mv -f -- "$partial" "$output"
    sha256sum "$output" > "$output.sha256"
    sfdisk --dump "$device" > "$output.sfdisk"
    lsblk -p -o NAME,SIZE,MODEL,SERIAL,TRAN,RM,RO,TYPE,FSTYPE,LABEL,MOUNTPOINTS "$device" > "$output.lsblk.txt"
    printf 'Backup complete and verified.\nImage: %s\nChecksum: %s.sha256\n' "$output" "$output"
    ;;

  restore|prepare-nia-recovery)
    resolve_device
    resolve_image
    load_expected_sha
    require_root
    validate_target_disk
    validate_capacity
    verify_source_image
    if [[ $command_name == prepare-nia-recovery ]]; then prepare_nia_environment; fi
    confirm_exact "ERASE-$device"
    show_device
    if $dry_run; then
      printf 'Dry run: validated source and target; would overwrite %s with %s.\n' "$device" "$image"
      [[ $command_name == prepare-nia-recovery ]] && \
        printf 'Dry run: would also arm the Kobo Nia one-time factory-recovery environment.\n'
      exit 0
    fi
    write_and_verify_image
    if [[ $command_name == prepare-nia-recovery ]]; then
      need dd; need cmp
      printf 'Arming the Kobo Nia one-time factory-recovery environment...\n' >&2
      dd if="$nia_recovery_env" of="$device" bs=128K seek=6 count=1 conv=notrunc,fsync status=progress
      dd if="$device" of="$work_dir/u-boot.readback" bs=128K skip=6 count=1 \
        iflag=fullblock status=none
      cmp "$nia_recovery_env" "$work_dir/u-boot.readback" || \
        die 6 "Nia recovery environment read-back differs"
      printf 'Nia recovery card prepared and verified.\n'
    else
      printf 'Restore complete and byte-verified.\n'
    fi
    ;;
esac

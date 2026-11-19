#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: kobo-device-info.sh [--mount PATH] [--json]

Discover a mounted Kobo USB storage volume and report non-secret device details.
If --mount is omitted, common removable-media directories are searched.

Options:
  --mount PATH  Inspect this KOBOeReader mount.
  --json        Emit one JSON object.
  -h, --help    Show this help.
EOF
}

mount_path=
json=false
while (($#)); do
  case $1 in
    --mount) [[ $# -ge 2 ]] || { echo "Error: --mount needs a path." >&2; exit 2; }; mount_path=$2; shift 2 ;;
    --json) json=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Error: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z $mount_path ]]; then
  candidates=()
  while IFS= read -r path; do
    candidates+=("${path%/.kobo/version}")
  done < <(find /run/media /media /mnt -maxdepth 5 -type f -path '*/.kobo/version' -print 2>/dev/null | sort -u)
  case ${#candidates[@]} in
    0)
      echo "Error: no mounted Kobo found. Connect it by USB and tap Connect on its screen." >&2
      command -v lsusb >/dev/null && lsusb | grep -Ei 'kobo|2237:' >&2 || true
      exit 3
      ;;
    1) mount_path=${candidates[0]} ;;
    *)
      echo "Error: multiple Kobo mounts found; choose one with --mount:" >&2
      printf '  %s\n' "${candidates[@]}" >&2
      exit 4
      ;;
  esac
fi

mount_path=$(realpath -e -- "$mount_path")
version_file=$mount_path/.kobo/version
[[ -f $version_file ]] || {
  echo "Error: $mount_path does not contain .kobo/version." >&2
  exit 3
}

source_device=$(findmnt -nro SOURCE --target "$mount_path" 2>/dev/null || true)
fstype=$(findmnt -nro FSTYPE --target "$mount_path" 2>/dev/null || true)
options=$(findmnt -nro OPTIONS --target "$mount_path" 2>/dev/null || true)
firmware=$(grep -Eo '[0-9]+\.[0-9]+\.[0-9]+' "$version_file" | tail -n1 || true)
[[ -n $firmware ]] || firmware=unknown

device_name=unknown
device_size=unknown
device_model=unknown
device_transport=unknown
device_readonly=unknown
if [[ $source_device == /dev/* ]]; then
  device_name=$(lsblk -ndo NAME "$source_device" 2>/dev/null || basename "$source_device")
  device_size=$(lsblk -dnbo SIZE "$source_device" 2>/dev/null || echo unknown)
  device_model=$(lsblk -dno MODEL "$source_device" 2>/dev/null | sed 's/[[:space:]]*$//' || true)
  device_transport=$(lsblk -dno TRAN "$source_device" 2>/dev/null | tr -d '[:space:]' || true)
  device_readonly=$(lsblk -dno RO "$source_device" 2>/dev/null | tr -d '[:space:]' || true)
  [[ -n $device_model ]] || device_model=unknown
  [[ -n $device_transport ]] || device_transport=unknown
  [[ -n $device_readonly ]] || device_readonly=unknown
fi

json_escape() {
  local value=$1
  value=${value//\\/\\\\}
  value=${value//\"/\\\"}
  value=${value//$'\n'/\\n}
  printf '%s' "$value"
}

if $json; then
  printf '{"mount":"%s","source":"%s","filesystem":"%s","options":"%s","firmware":"%s","device_name":"%s","device_size_bytes":"%s","model":"%s","transport":"%s","readonly":"%s"}\n' \
    "$(json_escape "$mount_path")" "$(json_escape "$source_device")" \
    "$(json_escape "$fstype")" "$(json_escape "$options")" \
    "$(json_escape "$firmware")" "$(json_escape "$device_name")" \
    "$(json_escape "$device_size")" "$(json_escape "$device_model")" \
    "$(json_escape "$device_transport")" "$(json_escape "$device_readonly")"
else
  printf 'Kobo mount: %s\n' "$mount_path"
  printf 'Source device: %s\n' "${source_device:-unknown}"
  printf 'Filesystem: %s\n' "${fstype:-unknown}"
  printf 'Mount options: %s\n' "${options:-unknown}"
  printf 'Firmware: %s\n' "$firmware"
  printf 'Block device: %s\n' "$device_name"
  printf 'Size (bytes): %s\n' "$device_size"
  printf 'Model: %s\n' "$device_model"
  printf 'Transport: %s\n' "$device_transport"
  printf 'Read-only flag: %s\n' "$device_readonly"
fi

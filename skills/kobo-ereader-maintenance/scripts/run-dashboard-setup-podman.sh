#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: run-dashboard-setup-podman.sh --app-dir DIR [OPTIONS]

Run a downloaded Kobo HA Dashboard Linux setup binary in a Fedora container.
The setup UI is served locally at http://127.0.0.1:3000.

Options:
  --app-dir DIR       Extracted release directory containing kobo-ha-dashboard.
  --kobo-mount PATH   Mounted KOBOeReader volume. Auto-detected when omitted.
  --image IMAGE       Container image (default: docker.io/library/fedora:44).
  --dry-run           Validate inputs and print the Podman command only.
  -h, --help          Show this help.

The persistent setup configuration is stored in DIR/setup-home. This can
contain a Home Assistant token; protect it and never print its contents.
EOF
}

die() {
  printf 'Error: %s\n' "$*" >&2
  exit 2
}

app_dir=
kobo_mount=
container_image=docker.io/library/fedora:44
dry_run=false
while (($#)); do
  case $1 in
    --app-dir) [[ $# -ge 2 ]] || die "--app-dir needs a path"; app_dir=$2; shift 2 ;;
    --kobo-mount) [[ $# -ge 2 ]] || die "--kobo-mount needs a path"; kobo_mount=$2; shift 2 ;;
    --image) [[ $# -ge 2 ]] || die "--image needs a value"; container_image=$2; shift 2 ;;
    --dry-run) dry_run=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[[ -n $app_dir ]] || die "--app-dir is required"
command -v podman >/dev/null 2>&1 || die "Podman is required"
command -v findmnt >/dev/null 2>&1 || die "findmnt is required"
app_dir=$(realpath -e -- "$app_dir")
binary=$app_dir/kobo-ha-dashboard
[[ -x $binary ]] || die "$binary is missing or not executable"

if [[ -z $kobo_mount ]]; then
  candidates=()
  while IFS= read -r path; do candidates+=("${path%/.kobo/version}"); done < <(
    find /run/media /media /mnt -maxdepth 5 -type f -path '*/.kobo/version' -print 2>/dev/null | sort -u
  )
  case ${#candidates[@]} in
    0) die "no mounted Kobo found; connect it by USB and tap Connect" ;;
    1) kobo_mount=${candidates[0]} ;;
    *) printf 'Multiple Kobo mounts found:\n' >&2; printf '  %s\n' "${candidates[@]}" >&2; die "choose one with --kobo-mount" ;;
  esac
fi

kobo_mount=$(realpath -e -- "$kobo_mount")
[[ -f $kobo_mount/.kobo/version ]] || die "$kobo_mount is not a Kobo storage mount"
kobo_device=$(findmnt -nro SOURCE --target "$kobo_mount" 2>/dev/null || true)
[[ $kobo_device == /dev/* && -b $kobo_device ]] || die "could not resolve the Kobo block device"
mount_options=$(findmnt -nro OPTIONS --target "$kobo_mount")
case ,$mount_options, in
  *,rw,*) ;;
  *) die "the Kobo mount is not writable: $mount_options" ;;
esac

setup_home=$app_dir/setup-home
podman_args=(
  run --rm -it
  --network host
  --security-opt label=disable
  --userns=keep-id
  --user "$(id -u):$(id -g)"
  --env HOME=/app/setup-home
  --env "USER=$(id -un)"
  --device "$kobo_device:$kobo_device:rwm"
  --volume "$app_dir:/app:rw"
  --volume "$kobo_mount:$kobo_mount:rw"
  --workdir /app
)
[[ ! -d /run/udev ]] || podman_args+=(--volume /run/udev:/run/udev:ro)
podman_args+=("$container_image" ./kobo-ha-dashboard)

if $dry_run; then
  printf 'Validated application: %s\n' "$binary"
  printf 'Validated Kobo mount: %s (%s)\n' "$kobo_mount" "$kobo_device"
  printf 'Persistent configuration: %s\n' "$setup_home"
  printf 'Command:'
  printf ' %q' podman "${podman_args[@]}"
  printf '\n'
  exit 0
fi

mkdir -p "$setup_home/.config/kobo-ha-dashboard"
chmod 0700 "$setup_home" "$setup_home/.config" "$setup_home/.config/kobo-ha-dashboard"

printf 'Starting Kobo HA Dashboard setup at http://127.0.0.1:3000\n'
printf 'Keep this terminal open until setup is finished.\n'
exec podman "${podman_args[@]}"

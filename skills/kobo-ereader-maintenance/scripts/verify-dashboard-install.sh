#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: verify-dashboard-install.sh --mount PATH [--json]

Verify a Kobo HA Dashboard installation without printing config.yaml or tokens.
The Kobo volume must be mounted.
EOF
}

mount_path=
json=false
while (($#)); do
  case $1 in
    --mount) [[ $# -ge 2 ]] || { echo "Error: --mount needs a path." >&2; exit 2; }; mount_path=$2; shift 2 ;;
    --json) json=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Error: unknown argument: $1" >&2; exit 2 ;;
  esac
done

[[ -n $mount_path ]] || { echo "Error: --mount is required." >&2; exit 2; }
mount_path=$(realpath -e -- "$mount_path")
[[ -f $mount_path/.kobo/version ]] || { echo "Error: not a Kobo mount: $mount_path" >&2; exit 3; }

dashboard=$mount_path/.kobo-ha/kobo-ha-dashboard
launcher=$mount_path/.kobo-ha/launch.sh
config=$mount_path/.kobo-ha/config.yaml
pending=none
[[ ! -f $mount_path/.kobo/KoboRoot.tgz ]] || pending=KoboRoot.tgz
[[ ! -f $mount_path/.kobo/Kobo.tgz ]] || pending=Kobo.tgz

nickel_state=missing
[[ ! -f $mount_path/.adds/nm/doc ]] || nickel_state=installed
menu_entry=
if [[ -d $mount_path/.adds/nm ]]; then
  menu_entry=$(grep -rlF '/mnt/onboard/.kobo-ha/launch.sh' "$mount_path/.adds/nm" 2>/dev/null | head -n1 || true)
fi
if [[ $pending != none ]]; then nickel_state=pending-restart; fi

dashboard_ok=false; launcher_ok=false; config_ok=false; menu_ok=false
# VFAT desktop mounts can hide execute bits even though the Kobo can launch the file.
[[ -s $dashboard ]] && dashboard_ok=true
[[ -s $launcher ]] && launcher_ok=true
[[ -s $config ]] && config_ok=true
[[ -n $menu_entry ]] && menu_ok=true

size_or_zero() {
  [[ -f $1 ]] && stat -c %s "$1" || printf '0'
}

json_escape() {
  local value=$1
  value=${value//\\/\\\\}
  value=${value//\"/\\\"}
  value=${value//$'\n'/\\n}
  printf '%s' "$value"
}

if $json; then
  printf '{"mount":"%s","dashboard":%s,"dashboard_bytes":%s,"launcher":%s,"config_present":%s,"config_bytes":%s,"menu_entry":%s,"nickelmenu":"%s","pending_update":"%s"}\n' \
    "$(json_escape "$mount_path")" "$dashboard_ok" "$(size_or_zero "$dashboard")" "$launcher_ok" \
    "$config_ok" "$(size_or_zero "$config")" "$menu_ok" "$nickel_state" "$pending"
else
  printf 'Kobo mount: %s\n' "$mount_path"
  printf 'Dashboard executable: %s (%s bytes)\n' "$dashboard_ok" "$(size_or_zero "$dashboard")"
  printf 'Launcher present: %s\n' "$launcher_ok"
  printf 'Configuration present: %s (%s bytes; contents not displayed)\n' "$config_ok" "$(size_or_zero "$config")"
  printf 'NickelMenu dashboard entry: %s\n' "$menu_ok"
  printf 'NickelMenu state: %s\n' "$nickel_state"
  printf 'Pending Kobo update: %s\n' "$pending"
fi

if ! $dashboard_ok || ! $launcher_ok || ! $config_ok || ! $menu_ok; then
  exit 5
fi

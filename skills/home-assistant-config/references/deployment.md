# Remote Deployment

Load this reference before deploying YAML, dashboard assets, Lovelace resources, or theme files to a Home Assistant host.

## Rules

- Back up every remote file before overwriting it.
- Upload to a configured staging directory first (commonly `/tmp`).
- Install into the configured Home Assistant directory (commonly `/config`)
  with permissions appropriate for the environment.
- Use `scp -O` if SFTP is unavailable.
- Validate config before reload or restart.
- Reload the smallest possible domain.
- Do not restart Core unless explicitly requested or required.

## Example deployment

Set explicit inputs in the environment rather than embedding a local account,
host, key, or directory in the command:

```bash
: "${HA_SSH_TARGET:?Set the SSH account and host}"
: "${HA_SSH_KEY:?Set the SSH private-key path}"
: "${HA_CONFIG_DIR:=/config}"
: "${HA_STAGING_DIR:=/tmp}"
LOCAL_FILE=${LOCAL_FILE:?Set the local file to deploy}
REMOTE_NAME=${REMOTE_NAME:?Set the destination filename}
```

Upload:

```bash
scp -O -i "$HA_SSH_KEY" "$LOCAL_FILE" \
  "$HA_SSH_TARGET:$HA_STAGING_DIR/$REMOTE_NAME.agent"
```

Install with backup:

```bash
BACKUP_SUFFIX=$(date -u +%Y%m%dT%H%M%SZ)
ssh -i "$HA_SSH_KEY" "$HA_SSH_TARGET" \
  "sudo cp '$HA_CONFIG_DIR/$REMOTE_NAME' '$HA_CONFIG_DIR/$REMOTE_NAME.backup-$BACKUP_SUFFIX' && sudo install -m 0644 -o root -g root '$HA_STAGING_DIR/$REMOTE_NAME.agent' '$HA_CONFIG_DIR/$REMOTE_NAME'"
```

Validate:

```bash
curl -fsS -X POST -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/services/homeassistant/check_config" --data-binary "{}"
```

Reload:

```bash
curl -fsS -X POST -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/services/automation/reload" --data-binary "{}"
```

## Restart decision

Usually no restart:

- automation YAML changes
- script YAML changes
- scene YAML changes
- YAML dashboard content changes

Possible restart or frontend reload:

- Lovelace resource changes
- frontend JavaScript asset replacement
- integration option changes that report `require_restart: true`

Always state whether a restart was performed. If not performed, state what was reloaded.

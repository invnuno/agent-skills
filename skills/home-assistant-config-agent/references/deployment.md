# Remote Deployment

Load this reference before deploying YAML, dashboard assets, Lovelace resources, or theme files to a Home Assistant host.

## Rules

- Back up every remote file before overwriting it.
- Upload to `/tmp` first.
- Install into `/config` with permissions appropriate for the HA environment.
- Use `scp -O` if SFTP is unavailable.
- Validate config before reload or restart.
- Reload the smallest possible domain.
- Do not restart Core unless explicitly requested or required.

## Example deployment

Upload:

```bash
scp -O -i ~/.ssh/homeassistant homeassistant-config/automations.yaml user@host:/tmp/automations.yaml.agent
```

Install with backup:

```bash
ssh -i ~/.ssh/homeassistant user@host \
  "sudo cp /config/automations.yaml /config/automations.yaml.backup-YYYYMMDD-topic && sudo install -m 0644 -o root -g root /tmp/automations.yaml.agent /config/automations.yaml"
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

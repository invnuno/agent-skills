# REST API Recipes

Load this reference when live Home Assistant inspection, service calls, Assist tests, or config-entry checks are needed.

## Environment

Expected environment variables:

- `HA_URL`, for example `http://homeassistant.local:8123`
- `HA_TOKEN`, a Home Assistant long-lived access token

Do not print token values.

## Read live state

```bash
curl -fsS \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  "$HA_URL/api/states"
```

Filter likely daily-use entities:

```bash
curl -fsS -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/states" \
  | jq -r '.[] | select(.entity_id|test("^(weather|climate|light|scene|media_player|sensor|switch)[.]")) | [.entity_id,.state,(.attributes.friendly_name // "")] | @tsv'
```

## List services

```bash
curl -fsS -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/services"
```

Useful domains:

- `homeassistant.check_config`
- `automation.reload`
- `script.reload`
- `scene.reload`
- `weather.get_forecasts`
- `conversation.process`
- `climate.set_temperature`

## Check config

```bash
curl -fsS -X POST \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  "$HA_URL/api/services/homeassistant/check_config" \
  --data-binary "{}"
```

Expected successful response is usually `[]`.

## Reload domains

```bash
curl -fsS -X POST -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/services/automation/reload" --data-binary "{}"
curl -fsS -X POST -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/services/script/reload" --data-binary "{}"
curl -fsS -X POST -H "Authorization: Bearer $HA_TOKEN" "$HA_URL/api/services/scene/reload" --data-binary "{}"
```

## Test Assist pipeline

Use WebSocket `assist_pipeline/run` when validating the same path used by Assist UI/apps. Record:

- `engine`
- `processed_locally`
- final speech text
- elapsed seconds for LLM fallback

Prefer deterministic commands to return `processed_locally: true`.

## Test direct conversation agent

```bash
curl -fsS -X POST \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  "$HA_URL/api/services/conversation/process?return_response" \
  --data-binary '{"agent_id":"conversation.ollama_conversation","text":"summarize the home status"}'
```

Use this for agent-specific diagnosis, not as a substitute for pipeline validation.

## Exposed Assist entities

Use Home Assistant WebSocket command `homeassistant/expose_entity/list`. Keep exposure small and intentional. Treat exposed entities as the LLM control surface.

## Config entry reload

Reload one config entry instead of restarting Core when changing integration options:

```bash
curl -fsS -X POST \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  "$HA_URL/api/config/config_entries/entry/$ENTRY_ID/reload" \
  --data-binary "{}"
```

If response says `{"require_restart":false}`, do not restart Core.

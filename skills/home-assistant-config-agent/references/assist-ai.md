# Assist and Local AI

Load this reference for Home Assistant Assist, deterministic sentence triggers, Ollama, local LLM model trials, MCP, or dashboard-context controls.

## Architecture

Use two layers:

1. Deterministic sentence-trigger automations for common daily commands.
2. LLM fallback for summaries, explanations, and safe control over intentionally exposed entities.

Set the preferred Assist pipeline to use the LLM conversation engine with local intents preferred when an LLM is configured.

## Deterministic sentence triggers

Use `trigger: conversation` and `set_conversation_response` for exact daily prompts.

Pattern:

```yaml
- id: "assist_example"
  alias: "Assist: Example"
  triggers:
    - trigger: conversation
      id: status
      command:
        - example status
  conditions: []
  actions:
    - set_conversation_response: "Example is {{ states('sensor.example') }}."
  mode: single
```

Good deterministic targets:

- weather and time
- common light controls
- AC status and temperature step changes
- safe scenes
- TV status/control
- energy readings for known sensors

Avoid ambiguous plain-text commands like `this device` unless the dashboard or script passes an explicit entity.

## Dashboard context

For "this device" style interactions, use dashboard buttons that call scripts with explicit fields:

- `target_entity`
- `sensor_entity`
- `label`
- signed temperature step

Do not assume Assist text has Lovelace card context.

## Local LLM rules

- Keep exposed entities under a small, intentional limit.
- Prefer scripts and scenes as the AI control surface.
- Do not expose backup, update, add-on, network, security, or broad configuration entities unless explicitly requested.
- Benchmark candidate models with real Assist prompts before keeping them.
- Record latency, correctness, hallucinated tool syntax, and rollback decisions.

## Model trial checklist

1. Confirm current active model and installed models.
2. Pull candidate model.
3. Reconfigure the Ollama conversation subentry.
4. Reload only the Ollama config entry.
5. Test deterministic prompts; they should stay `processed_locally: true`.
6. Test fallback prompts; record response quality and latency.
7. Keep only if latency and correctness are acceptable.
8. Roll back active model if the trial fails.
9. Delete unused models after cleanup if requested.

## Known gotchas

- Small local models may hallucinate Home Assistant tool calls.
- Larger models may be too slow on Raspberry Pi-class hardware.
- Typed apostrophes may fail deterministic sentence matching; include non-contracted alternatives and full phrases.
- The built-in `conversation.home_assistant` agent may return `no_intent_match` for inventory questions.

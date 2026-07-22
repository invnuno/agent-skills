# Validation

Load this reference before finalizing Home Assistant YAML, dashboard, Assist, or deployment work.

## Local validation

Use a YAML parser that tolerates Home Assistant tags such as `!include`.

```python
from pathlib import Path
import yaml

class Loader(yaml.SafeLoader):
    pass

def construct_unknown(loader, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)

Loader.add_multi_constructor("!", lambda loader, suffix, node: construct_unknown(loader, node))

for path in [Path("homeassistant-config/automations.yaml")]:
    yaml.load(path.read_text(), Loader=Loader)
```

## Entity validation

Check all new or changed entity IDs against live state when available. If live access is unavailable, use `entities.txt` or snapshot files and state that validation was limited.

## Home Assistant config validation

Run `homeassistant.check_config` through REST after deploying YAML and before reload/restart.

Successful response is commonly `[]`.

## Reload validation

After deployment:

- reload `automation` for automation changes
- reload `script` for script changes
- reload `scene` for scene changes
- reload dashboard resources only when relevant

## Assist validation

For deterministic sentence triggers, run prompts through the preferred Assist pipeline and verify:

- `processed_locally` is `true`
- response text is correct
- no unnecessary LLM latency

For LLM fallback, verify:

- `processed_locally` is `false`
- response is correct enough for the use case
- latency is acceptable
- no hallucinated tool JSON is shown to the user

## Control test safety

For commands that change device state:

1. Capture original state or target value.
2. Run the command.
3. Verify the expected change.
4. Restore the original state when the test is only for validation.
5. Report what changed and whether it was restored.

## Final response checklist

Include only high-signal facts:

- files changed
- remote target and backup names if deployed
- validation commands and results
- reload/restart performed
- residual warnings or limitations

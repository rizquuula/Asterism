# Configuration API

Asterism exposes runtime config endpoints under the `/asterism` prefix.

## Endpoints

- `GET /asterism/config` — read active config (provider API keys are redacted)
- `PUT /asterism/config` — update value (`set`, `append`, `remove`)
- `GET /asterism/config/schema` — get generated JSON schema

## Update Request

```json
{
  "key": "models.fallback",
  "value": "openrouter/qwen/qwen3-coder-next",
  "action": "append"
}
```

## Supported Actions

- `set`: replace any value
- `append`: append unique item to list
- `remove`: remove item from list

All successful updates are persisted back to `workspace/config.yaml`.

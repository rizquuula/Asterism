# Configuration File (config.yaml)

Asterism is configured via a `config.yaml` file located in your workspace directory. This guide explains all available options.

## File Location

The configuration file is located at:

```
workspace/config.yaml
```

The workspace directory is determined by:
1. `WORKSPACE_DIR` environment variable
2. Current working directory (`.`) if not set

## Complete Configuration Example

```yaml
# Agent metadata
agent:
  name: Asteri
  version: 1.0.0
  description: A part of Asterism AI Agents

# API server settings
api:
  host: 0.0.0.0
  port: 20820
  debug: false
  cors_origins:
    - "*"
  api_keys: env.API_KEYS
  db_path: sessions/data.db

# LLM provider configuration
models:
  provider:
    - type: openai-compatible
      name: openrouter
      base_url: https://openrouter.ai/api/v1
      api_key: env.OPENROUTER_API_KEY
    - type: openai-compatible
      name: llmgateway
      base_url: https://llm-gateway.psn.co.id
      api_key: env.LLMGATEWAY_API_KEY
  default: llmgateway/psn/Nusa-Max
  fallback:
    - openrouter/stepfun/step-3.5-flash:free
    - openrouter/qwen/qwen3-coder-next

# MCP server configuration
mcp:
  servers_file: mcp_servers/mcp_servers.json
  timeout: 30
```

## Configuration Sections

### agent

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Agent's display name |
| `version` | string | Yes | Semantic version string |
| `description` | string | Yes | Brief description of the agent |

Example:
```yaml
agent:
  name: Asteri
  version: 1.0.0
  description: An intelligent AI assistant
```

### api

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `host` | string | Yes | - | Host address to bind to |
| `port` | integer | Yes | - | Port number to listen on |
| `debug` | boolean | Yes | - | Enable debug mode |
| `cors_origins` | list[string] | No | `["*"]` | Allowed CORS origins |
| `api_keys` | string | No | None | Comma-separated API keys for auth |
| `db_path` | string | No | `sessions/data.db` | SQLite checkpoint database path |

Example:
```yaml
api:
  host: 0.0.0.0
  port: 20820
  debug: false
  cors_origins:
    - "https://example.com"
    - "https://app.example.com"
  api_keys: env.API_KEYS
  db_path: sessions/data.db
```

### models

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provider` | list[Provider] | Yes | List of LLM providers |
| `default` | string | Yes | Default model (format: `provider_name/model`) |
| `fallback` | list[string] | No | Fallback models if default fails |

#### Provider Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Provider type (currently only `openai-compatible`) |
| `name` | string | Yes | Unique provider identifier |
| `base_url` | string | No | API base URL |
| `api_key` | string | No | API key (supports `env.` prefix) |

Example:
```yaml
models:
  provider:
    - type: openai-compatible
      name: openrouter
      base_url: https://openrouter.ai/api/v1
      api_key: env.OPENROUTER_API_KEY
    - type: openai-compatible
      name: local
      base_url: http://localhost:11434/v1
      api_key: not-needed
  default: openrouter/openai/gpt-4o-mini
  fallback:
    - openrouter/openai/gpt-4o
```

### mcp

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `servers_file` | string | No | `mcp_servers/mcp_servers.json` | Path to MCP servers config |
| `timeout` | integer | No | `30` | MCP server timeout in seconds |

Example:
```yaml
mcp:
  servers_file: mcp_servers/mcp_servers.json
  timeout: 60
```

## Environment Variable Substitution

Asterism supports loading values from environment variables using the `env.` prefix:

```yaml
api:
  api_keys: env.API_KEYS

models:
  provider:
    - type: openai-compatible
      name: openrouter
      api_key: env.OPENROUTER_API_KEY
```

When the config is loaded, `env.API_KEYS` is replaced with the value of the `API_KEYS` environment variable.

## Dynamic Configuration Updates

Asterism provides API endpoints to update configuration at runtime:

### Get current config

```bash
curl http://localhost:20820/v1/config
```

### Update a value

```bash
curl -X PUT http://localhost:20820/v1/config \
  -H "Content-Type: application/json" \
  -d '{
    "key": "api.port",
    "value": 8080,
    "action": "set"
  }'
```

### Add to a list

```bash
curl -X PUT http://localhost:20820/v1/config \
  -H "Content-Type: application/json" \
  -d '{
    "key": "models.fallback",
    "value": "openrouter/anthropic/claude-3-opus",
    "action": "append"
  }'
```

### Get config schema

```bash
curl http://localhost:20820/v1/config/schema
```

## Next Steps

- [Environment Variables](environment.md) — Complete list of environment variables
- [LLM Providers](providers.md) — Configuring different LLM backends
- [MCP Configuration](../mcp/configuration.md) — Setting up MCP servers

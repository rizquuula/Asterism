# Environment Variables

Asterism uses environment variables for configuration that shouldn't be committed to version control, such as API keys.

## Complete Variable Reference

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `WORKSPACE_DIR` | No | Path to workspace directory | `./workspace` |
| `LOG_FILENAME` | No | Path to log file | `./logs/app.log` |
| `LOG_LEVEL` | No | Log level (debug, info, warning, error) | `info` |
| `OPENROUTER_API_KEY` | No* | OpenRouter API key | - |
| `LLMGATEWAY_API_KEY` | No* | LLM Gateway API key | - |
| `API_KEYS` | No | Comma-separated API keys for client auth | - |

*At least one LLM provider API key is required.

## Setting Environment Variables

### Option 1: .env File (Recommended)

Create a `.env` file in the project root:

```bash
# Required: At least one LLM provider key
OPENROUTER_API_KEY=YOUR_API_KEY_HERE
LLMGATEWAY_API_KEY=your_llmgateway_key

# Optional: Client authentication
API_KEYS=key1,key2,key3

# Optional: Logging
LOG_LEVEL=debug
LOG_FILENAME=./logs/app.log

# Optional: Workspace location
WORKSPACE_DIR=./workspace
```

The `.env` file is automatically loaded by `uv` when running commands.

### Option 2: System Environment

=== "Linux/macOS"

    ```bash
    export OPENROUTER_API_KEY=YOUR_API_KEY_HERE
    uv run uvicorn asterism.api.main:create_api_app --factory
    ```

=== "Windows (PowerShell)"

    ```powershell
    $env:OPENROUTER_API_KEY = "YOUR_API_KEY_HERE"
    uv run uvicorn asterism.api.main:create_api_app --factory
    ```

### Option 3: Docker

Pass environment variables to Docker:

```bash
docker run -d \
  -e OPENROUTER_API_KEY=YOUR_API_KEY_HERE \
  -e LLMGATEWAY_API_KEY=your_key \
  -p 20820:20820 \
  asterism:latest
```

Or use a `.env` file with Docker Compose:

```yaml
# docker-compose.yml
services:
  asterism:
    build: .
    env_file:
      - .env
```

## Variable Details

### `WORKSPACE_DIR`

Path to the workspace directory containing:
- `config.yaml` - Main configuration
- `SOUL.md` - Agent philosophy
- `AGENT.md` - Agent capabilities
- `PERSONALITY.md` - Agent personality
- `mcp_servers/` - MCP server configurations

```bash
WORKSPACE_DIR=/path/to/custom/workspace
```

### `LOG_FILENAME`

Path to the application log file. Logs are rotated daily and kept for 30 days.

```bash
LOG_FILENAME=./logs/app.log
```

### `LOG_LEVEL`

Controls verbosity of logging. Options (in increasing verbosity):
- `error` - Only errors
- `warning` - Warnings and errors
- `info` - Information, warnings, and errors (default)
- `debug` - All messages including detailed debug info

```bash
LOG_LEVEL=debug
```

### `OPENROUTER_API_KEY`

Your OpenRouter API key. Get one free at [openrouter.ai](https://openrouter.ai/).

```bash
OPENROUTER_API_KEY=YOUR_API_KEY_HERE
```

### `LLMGATEWAY_API_KEY`

Your LLM Gateway API key. Contact your administrator for access.

```bash
LLMGATEWAY_API_KEY=your_key_here
```

### `API_KEYS`

Comma-separated list of API keys that clients can use for authentication. If set, clients must include their key in the `Authorization` header:

```bash
API_KEYS=key1,key2,key3
```

Client request:
```bash
curl -H "Authorization: Bearer key1" http://localhost:20820/v1/health
```

## Security Best Practices

!!! warning "Never commit secrets"

    Never commit API keys or secrets to version control.

1. **Use `.env` files** — Add `.env` to `.gitignore`
2. **Use secrets management** — In production, use Docker secrets or a secrets manager
3. **Rotate keys regularly** — Update API keys periodically
4. **Use least privilege** — Only grant necessary permissions to API keys

## Verifying Configuration

Check that environment variables are set correctly:

```bash
# Check if a variable is set
echo $OPENROUTER_API_KEY

# List all Asterism-related variables
env | grep -E "^(OPENROUTER|LLMGATEWAY|API_KEYS|LOG_|WORKSPACE)"
```

## Troubleshooting

### "API key not found"

Ensure your `.env` file exists and contains the required keys:

```bash
cat .env | grep API_KEY
```

### "Invalid API key"

Check that the key is correct and has sufficient credits/quota.

### "Environment variable not resolved"

Make sure the `env.` prefix is used in `config.yaml`:

```yaml
# Correct
api_key: env.OPENROUTER_API_KEY

# Wrong - will use literal string
api_key: $OPENROUTER_API_KEY
```

## Next Steps

- [Configuration File](config-yaml.md) — Complete config reference
- [LLM Providers](providers.md) — Configuring different providers
- [Quick Start](../getting-started/quick-start.md) — Running the server

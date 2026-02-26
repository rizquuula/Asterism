# LLM Provider Configuration

Asterism supports multiple LLM providers through a flexible provider abstraction. This guide explains how to configure different providers.

## Supported Providers

Asterism is designed to work with any OpenAI-compatible API. Here are the commonly used providers:

| Provider | Base URL | Notes |
|----------|----------|-------|
| OpenRouter | `https://openrouter.ai/api/v1` | Many models, free tier available |
| LLM Gateway | `https://llm-gateway.psn.co.id` | Custom deployment |
| Ollama | `http://localhost:11434/v1` | Local models |
| OpenAI | `https://api.openai.com/v1` | Official OpenAI API |
| Azure OpenAI | `https://{resource}.openai.azure.com/` | Azure deployment |

## Provider Configuration

Providers are configured in `workspace/config.yaml`:

```yaml
models:
  provider:
    - type: openai-compatible
      name: provider_name
      base_url: https://api.example.com/v1
      api_key: env.PROVIDER_API_KEY
```

### Configuration Fields

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | Must be `openai-compatible` |
| `name` | Yes | Unique identifier for the provider |
| `base_url` | Yes | API endpoint URL |
| `api_key` | No | Authentication key |

## Examples

### OpenRouter (Recommended for Development)

[OpenRouter](https://openrouter.ai/) provides access to many models through a single API:

```yaml
models:
  provider:
    - type: openai-compatible
      name: openrouter
      base_url: https://openrouter.ai/api/v1
      api_key: env.OPENROUTER_API_KEY
  default: openrouter/openai/gpt-4o-mini
  fallback:
    - openrouter/google/gemma-2-9b-it:free
    - openrouter/meta-llama/llama-3.1-8b-instruct
```

Get a free key at [openrouter.ai](https://openrouter.ai/).

### Ollama (Local)

Run models locally with [Ollama](https://ollama.ai/):

```yaml
models:
  provider:
    - type: openai-compatible
      name: ollama
      base_url: http://localhost:11434/v1
      api_key: not-needed
  default: ollama/llama3.1
```

Make sure Ollama is running:
```bash
ollama serve
```

### Azure OpenAI

```yaml
models:
  provider:
    - type: openai-compatible
      name: azure
      base_url: https://your-resource.openai.azure.com/
      api_key: env.AZURE_OPENAI_API_KEY
  default: azure/gpt-4o
```

### Multiple Providers

Configure multiple providers for redundancy:

```yaml
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
    - openrouter/openai/gpt-4o-mini
```

## Model Selection

### Format

Model names use the format: `provider_name/model_id`

Examples:
- `llmgateway/psn/Nusa-Max`
- `openrouter/openai/gpt-4o-mini`
- `ollama/llama3.1`

### Default Model

Set the default model that will be used if none is specified:

```yaml
models:
  default: llmgateway/psn/Nusa-Max
```

### Fallback Models

If the default model fails, Asterism will try fallback models in order:

```yaml
models:
  default: llmgateway/psn/Nusa-Max
  fallback:
    - openrouter/stepfun/step-3.5-flash:free
    - openrouter/qwen/qwen3-coder-next
```

## Request-Specific Model

You can override the default model in each API request:

```bash
curl -X POST http://localhost:20820/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openrouter/anthropic/claude-3-haiku",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Finding Model IDs

### OpenRouter Models

Visit [openrouter.ai/models](https://openrouter.ai/models) for a complete list. Model IDs follow this pattern:
- `openrouter/openai/gpt-4o`
- `openrouter/google/gemma-2-9b-it:free`
- `openrouter/meta-llama/llama-3.1-70b-instruct`

### Ollama Models

```bash
ollama list
```

Common models:
- `ollama/llama3.1`
- `ollama/mistral`
- `ollama/codellama`

## Provider Health Check

Check which providers are available:

```bash
curl http://localhost:20820/v1/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "providers": {
    "openrouter": "available",
    "llmgateway": "available"
  }
}
```

## Troubleshooting

### "Model not found"

- Check that the model ID is correct
- Verify the provider is configured in `config.yaml`

### "API key invalid"

- Verify your API key is set in environment variables
- Check that the key has sufficient credits/quota

### "Connection timeout"

- Check network connectivity
- Verify the provider's base URL is correct
- Try increasing the timeout in config:

    ```yaml
    mcp:
      timeout: 60
    ```

### "Rate limited"

- Add fallback models to your config
- Consider using a different provider

## Next Steps

- [Configuration File](config-yaml.md) — Complete config reference
- [Environment Variables](environment.md) — Setting API keys
- [API Reference](../api-reference/overview.md) — Making API calls

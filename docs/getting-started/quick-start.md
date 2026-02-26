# Quick Start

This guide will get you from zero to making your first API call in under 5 minutes.

## Start the API Server

There are two ways to run the Asterism API server:

=== "Using Make"

    ```bash
    make dev
    ```

=== "Using uv directly"

    ```bash
    uv run uvicorn asterism.api.main:create_api_app --factory --host 0.0.0.0 --port 20820
    ```

!!! tip "Default Port"

    The server runs on **port 20820** by default (configurable in `workspace/config.yaml`).

## Verify the Server is Running

Open a new terminal and check the health endpoint:

```bash
curl http://localhost:20820/v1/health
```

You should see a response like:

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

## Make Your First Request

### Non-Streaming Request

Send a simple chat request:

```bash
curl -X POST http://localhost:20820/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llmgateway/psn/Nusa-Max",
    "messages": [
      {"role": "user", "content": "Hello! What can you help me with?"}
    ]
  }'
```

=== "Expected Response"

    ```json
    {
      "id": "chatcmpl-abc123def456",
      "object": "chat.completion",
      "created": 1706745600,
      "model": "llmgateway/psn/Nusa-Max",
      "choices": [
        {
          "index": 0,
          "message": {
            "role": "assistant",
            "content": "Hello! I'm Asteri, an AI agent built with Asterism. I can help you with a wide range of tasks including..."
          },
          "finish_reason": "stop"
        }
      ],
      "usage": {
        "prompt_tokens": 150,
        "completion_tokens": 85,
        "total_tokens": 235
      }
    }
    ```

### Streaming Request

For real-time responses, use streaming:

```bash
curl -X POST http://localhost:20820/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llmgateway/psn/Nusa-Max",
    "messages": [
      {"role": "user", "content": "Tell me a short story about a brave knight."}
    ],
    "stream": true
  }'
```

This will return Server-Sent Events (SSE) with chunks of the response as they're generated.

## Using API Keys (Optional)

If you've configured API keys in your environment, include them in requests:

```bash
curl -X POST http://localhost:20820/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "llmgateway/psn/Nusa-Max",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Using with Python

You can also use the OpenAI Python SDK by changing the base URL:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:20820/v1",
    api_key="YOUR_API_KEY"  # Optional if not configured
)

response = client.chat.completions.create(
    model="llmgateway/psn/Nusa-Max",
    messages=[
        {"role": "user", "content": "Hello! What can you help me with?"}
    ]
)

print(response.choices[0].message.content)
```

## What's Next?

Now that you have the basics working, explore:

| Topic | Description |
|-------|-------------|
| [Configuration](../configuration/config-yaml.md) | Customize port, models, MCP servers |
| [API Reference](../api-reference/overview.md) | Full API documentation |
| [MCP Integration](../mcp/overview.md) | Add custom tools to your agent |
| [Architecture](../architecture/overview.md) | Understand how Asterism works |

## Common Issues

### "Connection refused"

The server might not be running. Check:
- Is the server started? (`make dev`)
- Is the port correct? (default: 20820)

### "Model not found"

Check your configured models in `workspace/config.yaml`. The default model is `llmgateway/psn/Nusa-Max`.

### "API key invalid"

Ensure your API key is set in the `.env` file and matches the provider configuration.

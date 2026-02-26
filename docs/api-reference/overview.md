# API Reference Overview

Asterism provides an OpenAI-compatible REST API for interacting with the agent. All endpoints are prefixed with `/v1`.

## Base URL

```
http://localhost:20820/v1
```

## Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat/completions` | POST | Send a chat message and get a response |
| `/models` | GET | List available models |
| `/health` | GET | Check API health status |
| `/config` | GET | Get current configuration |
| `/config` | PUT | Update configuration |
| `/config/schema` | GET | Get configuration schema |

## Authentication

If API keys are configured, include them in requests:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:20820/v1/health
```

## Request/Response Format

All endpoints accept and return JSON.

### Chat Completions

**Request:**
```json
{
  "model": "llmgateway/psn/Nusa-Max",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "stream": false,
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Response:**
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1706745600,
  "model": "llmgateway/psn/Nusa-Max",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! I'm Asteri..."
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

## Error Responses

Errors return standard HTTP status codes with JSON details:

```json
{
  "error": {
    "message": "Invalid model name",
    "type": "invalid_request_error",
    "code": "model_not_found"
  }
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad request (invalid parameters) |
| 401 | Unauthorized (invalid API key) |
| 404 | Endpoint not found |
| 500 | Internal server error |
| 503 | Service unavailable |

## Rate Limiting

Rate limiting is not currently enforced but may be added in future versions.

## SDK Usage

You can use the OpenAI Python SDK with Asterism:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:20820/v1",
    api_key="YOUR_API_KEY"  # Optional
)

response = client.chat.completions.create(
    model="llmgateway/psn/Nusa-Max",
    messages=[
        {"role": "user", "content": "What is Asterism?"}
    ]
)

print(response.choices[0].message.content)
```

## OpenAPI Specification

For developers who need the complete specification, Asterism exposes an OpenAPI schema:

- **Swagger UI**: `http://localhost:20820/docs`
- **ReDoc**: `http://localhost:20820/redoc`
- **Raw JSON**: `http://localhost:20820/openapi.json`

## Next Steps

- [Chat Completions](chat-completions.md) — Detailed chat endpoint docs
- [Models](models.md) — List available models
- [Health](health.md) — Health check endpoint
- [Config](config.md) — Configuration management
- [OpenAPI](openapi.md) — Auto-generated API docs

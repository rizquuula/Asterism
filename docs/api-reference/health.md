# Health

`GET /v1/health`

Checks API service status and configured provider availability.

## Response

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

If any configured provider cannot be initialized, status becomes `unhealthy`.

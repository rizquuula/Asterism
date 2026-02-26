# Models

`GET /v1/models`

Returns model metadata in OpenAI-compatible format.

## Response

```json
{
  "object": "list",
  "data": [
    {
      "id": "asterism/Asteri",
      "object": "model",
      "created": 1700000000,
      "owned_by": "asterism",
      "root": "asterism/Asteri"
    }
  ]
}
```

## Notes

This endpoint currently exposes the framework-level model identity (agent name), not a full upstream provider catalog.

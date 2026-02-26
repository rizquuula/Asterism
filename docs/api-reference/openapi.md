# OpenAPI

When `api.debug: true` in `workspace/config.yaml`, API docs are exposed:

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- Raw schema: `/openapi.json`

## Enable

```yaml
api:
  debug: true
```

Then restart the server and open `http://localhost:20820/docs`.

# Docker Deployment

This guide shows how to run Asterism using Docker for easy deployment and isolation.

## Prerequisites

- [Docker](https://www.docker.com/get-started) installed
- [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

## Quick Start with Docker

### 1. Build and Run

```bash
make deploy
```

This command runs `docker compose up --build -d`, which:
1. Builds the Docker image
2. Starts the API server on port 20820
3. Creates necessary directories

### 2. Verify It's Running

```bash
make healthcheck
```

Expected output:
```
{"status":"healthy","version":"1.0.0","providers":{"openrouter":"available","llmgateway":"available"}}
```

### 3. Stop the Server

```bash
make deploy-down
```

## Manual Docker Commands

If you prefer manual control:

### Build the Image

```bash
docker build -t asterism:latest .
```

### Run the Container

```bash
docker run -d \
  --name asterism \
  -p 20820:20820 \
  -v ./workspace:/app/workspace \
  -v ./logs:/app/logs \
  -e OPENROUTER_API_KEY=your_key_here \
  -e LLMGATEWAY_API_KEY=your_key_here \
  asterism:latest
```

### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  asterism:
    build: .
    ports:
      - "20820:20820"
    volumes:
      - ./workspace:/app/workspace
      - ./logs:/app/logs
      - ./sessions:/app/sessions
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - LLMGATEWAY_API_KEY=${LLMGATEWAY_API_KEY}
      - API_KEYS=${API_KEYS}
      - LOG_LEVEL=info
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:20820/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Then run:

```bash
# Start
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

## Volume Mounts

| Volume | Description |
|--------|-------------|
| `./workspace` | Agent configuration, persona files |
| `./logs` | Application logs |
| `./sessions` | SQLite database for session persistence |

## Environment Variables in Docker

Pass environment variables to the container:

=== "docker run"

    ```bash
    -e OPENROUTER_API_KEY=sk-xxx
    -e LLMGATEWAY_API_KEY=xxx
    ```

=== "docker-compose.yml"

    ```yaml
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    ```

=== ".env file"

    Create a `.env` file in your project root:

    ```
    OPENROUTER_API_KEY=sk-your-key-here
    LLMGATEWAY_API_KEY=your-key-here
    ```

    Then reference it in docker-compose:

    ```yaml
    env_file:
      - .env
    ```

## Custom Workspace

To use a custom workspace directory:

```bash
docker run -d \
  --name asterism \
  -p 20820:20820 \
  -v /path/to/your/workspace:/app/workspace \
  -e WORKSPACE_DIR=/app/workspace \
  asterism:latest
```

## Production Considerations

### Security

1. **Don't hardcode secrets** — Use environment variables or Docker secrets
2. **Restrict ports** — Only expose port 20820 if needed
3. **Use a reverse proxy** — Consider nginx or Traefik for SSL termination

### Performance

1. **Resource limits** — Set appropriate CPU/memory limits:

    ```yaml
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
    ```

2. **Logging** — Configure log rotation:

    ```yaml
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    ```

### Health Checks

The included healthcheck verifies the API is responding:

```bash
curl http://localhost:20820/v1/health
```

## Troubleshooting

### Container won't start

Check logs:
```bash
docker compose logs
```

### Port already in use

Change the port in `docker-compose.yml` or stop the conflicting service.

### Permission errors

Ensure the directories exist and have correct permissions:

```bash
mkdir -p logs sessions
chmod 755 logs sessions
```

## Next Steps

- [Configuration Guide](../configuration/config-yaml.md) — Customize your deployment
- [MCP Integration](../mcp/overview.md) — Add tools to your Docker container
- [API Reference](../api-reference/overview.md) — Full API documentation

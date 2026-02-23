# Agent Coding Guidelines for Asterism

This file provides guidelines for agentic coding agents working in this repository.

## Overview

Asterism is an AI agent framework built with FastAPI, LangGraph, and LangChain. It provides an OpenAI-compatible API for agentic task execution.

---

## Build, Lint, and Test Commands

This project uses **uv** for all Python package management and execution. Always use `uv` commands instead of pip/poetry.

### Installation
```bash
make install          # Install dependencies with uv sync
```

### Adding Dependencies
```bash
uv add <package>      # Add new dependency
uv add -d <package>   # Add as dev dependency
```

### Development Server
```bash
make dev              # Run API server (uv run asterism/api_server.py)
```

### Formatting and Linting
```bash
./auto_format_ruff.sh # Runs: uvx ruff check --fix && uvx ruff format
```

Or individually:
```bash
uvx ruff check --fix  # Check and auto-fix issues
uvx ruff format       # Format code
```

### Docker
```bash
make deploy           # docker compose up --build -d
make deploy-down      # docker compose down
make healthcheck      # curl http://localhost:20820/v1/health
```

---

## Code Style Guidelines

### General Principles

- **Python 3.13+** - Use modern Python syntax and features
- **Ruff** - Primary linter/formatter (line-length: 120)
- **Type hints** - Always use type hints for function signatures and variables
- **Pydantic v2** - Use for all data models and validation

### Import Conventions

```python
# Standard library first, then third-party, then local
import os
import time
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from asterism.config import Config
from asterism.llm import LLMProviderRouter

# Use relative imports within the same package
from ..dependencies import get_config
from ..models import ChatCompletionRequest
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Modules | snake_case | `chat.py`, `agent_service.py` |
| Classes | PascalCase | `Config`, `AgentService` |
| Functions | snake_case | `get_config()`, `run_completion()` |
| Constants | UPPER_SNAKE | `LOG_FILENAME` |

### Docstrings

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> dict[str, Any]:
    """Short one-line description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value
    """
```

### Error Handling

1. **Custom exceptions** - Inherit from `APIError`
2. **Use HTTPException** - For request-level errors (400, 401, 404, etc.)
3. **Global handlers** - Register in `main.py`

```python
class ValidationError(APIError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400, code="invalid_request")

raise HTTPException(status_code=400, detail="Invalid key path")
```

### Pydantic Models

```python
class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    stream: bool = False
    temperature: float | None = None
    max_tokens: int | None = None

    model_config = ConfigDict(populate_by_name=True)
```

### FastAPI Patterns

```python
from typing import Annotated
from fastapi import APIRouter, Depends

router = APIRouter()

@router.post("/endpoint", response_model=ResponseModel)
async def handler(
    request: RequestModel,
    service: Annotated[Service, Depends(get_service)],
) -> ResponseModel:
    return await service.handle(request)
```

---

## Common Patterns

### New API Endpoint
1. Add route in `asterism/api/routes/<name>.py`
2. Export router in `asterism/api/routes/__init__.py`
3. Register in `asterism/api/main.py`: `app.include_router(router, prefix="/prefix")`

### New Config Option
1. Add field to `Config` model in `asterism/config/config.py`
2. Add key to `workspace/config.yaml` with default value
3. Access via `config.data.section.field`

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `WORKSPACE_DIR` | Path to workspace (default: `./workspace`) |
| `LOG_FILENAME` | Path to log file (default: `./logs/app.log`) |
| `LOG_LEVEL` | Log level (debug, info, warning, error) |
| `OPENROUTER_API_KEY` | OpenRouter API key |
| `LLMGATEWAY_API_KEY` | LLM Gateway API key |
| `API_KEYS` | Comma-separated API keys |

---

## File Locations

- **Config**: `workspace/config.yaml`
- **MCP Servers**: `workspace/mcp_servers/mcp_servers.json`
- **Agent State DB**: `sessions/data.db` (SQLite)
- **Logs**: `logs/app.log`

---

## Pre-commit Checklist

- [ ] Run `./auto_format_ruff.sh`
- [ ] Verify code compiles: `python3 -m py_compile <file>`

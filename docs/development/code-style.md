# Code Style

Asterism follows Python-first, Ruff-enforced style.

## Standards

- Type hints on function signatures
- Pydantic models for request/response schemas
- Clear module boundaries (`api`, `agent`, `mcp`, `config`)

## Commands

```bash
./auto_format_ruff.sh
# or
uvx ruff check --fix
uvx ruff format
```

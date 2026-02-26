# Testing

## Run test suite

```bash
uv run pytest
```

## Targeted tests

```bash
uv run pytest tests/unit -q
uv run pytest tests/integration_tests -q
```

## Recommended validation before merge

1. `./auto_format_ruff.sh`
2. `uv run pytest`

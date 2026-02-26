# Contributing

## Local setup

```bash
git clone https://github.com/rizquuula/Asterism.git
cd Asterism
make install
```

## Workflow

1. Create a branch
2. Make focused changes
3. Run formatting and tests
4. Open PR with clear scope and rationale

## Minimum checks

```bash
./auto_format_ruff.sh
uv run pytest
```

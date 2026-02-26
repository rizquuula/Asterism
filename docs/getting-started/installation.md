# Installation

This guide will help you get Asterism up and running on your machine. Whether you're a developer or just curious, we'll walk through the setup step by step.

## Prerequisites

Before installing Asterism, make sure you have the following:

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.13+ | Required. Check with `python --version` |
| uv | Latest | Fast Python package manager |
| Git | Any recent version | For cloning the repository |

!!! tip "What is uv?"

    [uv](https://github.com/astral-sh/uv) is an extremely fast Python package manager written in Rust. It replaces pip, poetry, and conda with a single, blazingly fast tool.

## Step 1: Clone the Repository

```bash
git clone https://github.com/rizquuula/Asterism.git
cd Asterism
```

## Step 2: Install Dependencies

We use `uv` for all package management. This will install all required dependencies:

```bash
make install
```

Or if you prefer running uv directly:

```bash
uv sync
```

## Step 3: Configure Environment Variables

Asterism requires an API key for the LLM provider. Copy the example environment file:

```bash
cp .env.example .env
```

Now open `.env` and add your API key. The file looks like this:

```bash
# Required: LLM Provider API Keys (at least one)
OPENROUTER_API_KEY=your_openrouter_key_here
LLMGATEWAY_API_KEY=your_llmgateway_key_here

# Optional: Custom API Keys for your users
API_KEYS=key1,key2,key3

# Optional: Logging
LOG_LEVEL=info
LOG_FILENAME=./logs/app.log

# Optional: Workspace directory
WORKSPACE_DIR=./workspace
```

!!! warning "Get Your API Key"

    - **OpenRouter**: Get a free key at [openrouter.ai](https://openrouter.ai/)
    - **LLMGateway**: Contact your administrator for access

## Step 4: Verify Installation

Run the tests to make sure everything is working:

```bash
uv run pytest
```

You should see output similar to:

```
========================= test session starts =========================
collected 93 items

tests/unit/agent/test_agent.py .................                 [ 50%]
tests/unit/config/test_config.py .........                       [100%]

========================= 93 passed in 2.5s =========================
```

## Step 5: Configure Your Agent (Optional)

Asterism loads agent personality from the `workspace/` directory. You can customize:

- **[SOUL.md](../workspace/soul.md)** — Agent's philosophy and beliefs
- **[AGENT.md](../workspace/agent.md)** — Agent's capabilities and workflows
- **[PERSONALITY.md](../workspace/personality.md)** — Agent's character and communication style

The default configuration is ready to use, but you can customize these files to change how your agent behaves.

## Troubleshooting

### "Python version not found"

Make sure you have Python 3.13+ installed:

```bash
python --version
# Should output: Python 3.13.x
```

### "uv: command not found"

Install uv:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

### "No API key found"

Ensure your `.env` file exists and contains at least one valid API key:

```bash
cat .env | grep API_KEY
```

### "Module not found" errors

Reinstall dependencies:

```bash
uv sync --force-reinstall
```

## Next Steps

Now that you have Asterism installed, continue to:

- [Quick Start Guide](quick-start.md) — Start the API server and make your first request
- [Configuration Guide](../configuration/config-yaml.md) — Customize your setup
- [API Reference](../api-reference/overview.md) — Understand the endpoints

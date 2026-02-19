# Asterism

A high-performance AI agent framework built with **LangGraph** for workflow orchestration and **MCP** for tool execution. Features runtime persona configuration through SOUL.md, AGENT.md, and PERSONALITY.md.

## Core Features

- **Plan-Execute-Evaluate Cycle**: Hierarchical agent workflow with automatic retry logic
- **Dynamic LLM Abstraction**: Plug-and-play provider architecture (OpenAI implementation included)
- **Multi-Transport MCP**: stdio, http_stream, and SSE transport support
- **Runtime Persona Loading**: SOUL.md (philosophy), AGENT.md (capabilities), PERSONALITY.md (character)
- **Robust JSON Parsing**: Automatic retry with markdown extraction fallback
- **Comprehensive Logging**: Full debugging visibility across all nodes

## Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/rizquuula/Asterism.git
cd Asterism

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Add OPENAI_API_KEY to .env

# Run tests
uv run pytest
```

## Project Structure

```
Asterism/
├── asterism/              # Core framework
│   ├── agent/             # Agent implementation
│   │   ├── agent.py       # LangGraph workflow orchestration
│   │   ├── nodes/         # Workflow nodes
│   │   │   ├── planner/   # Plan creation with validation
│   │   │   ├── executor/  # Task execution with logging
│   │   │   ├── evaluator/ # Decision making & retry logic
│   │   │   └── finalizer/ # Response synthesis
│   │   ├── state/         # AgentState TypedDict
│   │   └── models/        # Pydantic schemas
│   ├── core/              # Utilities
│   │   └── prompt_loader.py  # SOUL.md/AGENT.md loader
│   ├── llm/               # LLM providers
│   │   ├── base.py        # Abstract provider interface
│   │   └── openai_provider.py
│   └── mcp/               # MCP integration
│       ├── executor.py    # Dynamic tool execution
│       └── transport_executor/  # stdio, http_stream, sse
├── workspace/             # Persona configuration
│   ├── SOUL.md           # Philosophy & core beliefs
│   ├── AGENT.md          # Agent capabilities & workflow
│   └── PERSONALITY.md    # Character & communication style
├── tests/                # Unit & integration tests
│   ├── unit/             # 93 tests, ~100% coverage
│   └── integration_tests/
└── workspace/mcp_servers/ # MCP server configurations
```

## Architecture

### Agent Workflow

```
START → Planner → Executor → Evaluator → (loop) Finalizer → END
              ↑              ↓              ↓
              └──────────────┴──────────────┘
```

### System Prompt Assembly

Every LLM call receives:

```
[SystemMessage: SOUL.md + AGENT.md]
[SystemMessage: Node-specific instructions]
[HumanMessage: User request]
```

### Persona Configuration

| File | Purpose |
|------|---------|
| `SOUL.md` | Philosophy, beliefs, and sacred commitments |
| `AGENT.md` | Operational capabilities and workflows |
| `PERSONALITY.md` | Tone, character, and communication style |

## Key Patterns

1. **Dependency Injection** - Nodes receive LLM/MCP via closures
2. **State Immutability** - Nodes return new state: `state.copy()`
3. **Configuration-Driven MCP** - Servers defined in JSON
4. **Singleton Executor** - Global `get_mcp_executor()` access
5. **Error Context Propagation** - Rich error details for replanning

## Configuration

**Required:** `OPENAI_API_KEY`

**Optional:** `LOG_LEVEL`, `DEBUG`

**MCP Servers:** `workspace/mcp_servers/mcp_servers.json`

## Commands

```bash
uv sync              # Install dependencies
uv run pytest        # Run tests
./auto_format_ruff.sh # Format code
```

## API Usage

The API is OpenAI-compatible and runs on port 8080 by default.

### Start the Server

```bash
uv run uvicorn asterism.api.main:create_api_app --factory --host 0.0.0.0 --port 8080
```

### Chat Completions

**Non-streaming:**

```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llmgateway/psn/Nusa-Max",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

**Streaming:**

```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llmgateway/psn/Nusa-Max",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'
```

## Testing

- 93 unit tests with ~100% coverage on core modules
- Functional Python style (`def test_...()`), no classes
- Integration tests for LLM providers and transport executors

## Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) for workflow orchestration
- [Model Context Protocol](https://modelcontextprotocol.io/) for tool standardization
- [uv](https://github.com/astral-sh/uv) for fast Python packaging

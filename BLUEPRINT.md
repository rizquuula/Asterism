# Asterism Agent - Project Blueprint

## 1. Overview

High-performance AI agent framework built with **LangGraph** for workflow orchestration and **MCP** for tool execution.

**Core Features:**
- Plan-Execute-Evaluate cycle with automatic retry logic
- Dynamic LLM provider abstraction (OpenAI)
- Multi-transport MCP tool execution (stdio, http_stream, SSE)
- State persistence via SQLite checkpointing
- Runtime system prompt loading (SOUL.md + AGENT.md)

## 2. Directory Structure

```
asterism/
├── agent/           # Core agent implementation
│   ├── agent.py    # LangGraph workflow orchestration
│   ├── nodes/      # Planner, Executor, Evaluator, Finalizer
│   ├── state/      # AgentState TypedDict
│   └── models/     # Pydantic schemas (Task, Plan, TaskResult)
├── core/           # Core utilities
│   └── prompt_loader.py  # SOUL.md/AGENT.md loader
├── llm/            # LLM providers
│   ├── base.py     # BaseLLMProvider abstract interface
│   └── openai_provider.py  # OpenAI implementation
└── mcp/            # MCP integration
    ├── config.py    # MCP server configuration
    ├── executor.py  # Dynamic tool executor
    └── transport_executor/  # stdio, http_stream, sse

tests/
├── unit/           # Unit tests (93 tests, ~100% coverage)
└── integration_tests/  # Integration tests

workspace/
├── AGENT.md        # Agent identity & capabilities (mandatory)
└── SOUL.md         # Core values & philosophy (mandatory)
```

## 3. Architecture

### Agent Workflow (LangGraph State Machine)

```
START → Planner → Executor → Evaluator → (loop or) Finalizer → END
              ↑              ↓              ↓
              └──────────────┴──────────────┘
```

### System Prompt Loading

Every LLM call receives:
```
[SystemMessage(content=SOUL.md + AGENT.md)]
[SystemMessage(content=node-specific instructions)]
[HumanMessage(content=user request)]
```

**Flow:**
1. `SystemPromptLoader.load()` reads `workspace/SOUL.md` and `workspace/AGENT.md` fresh
2. Content is combined and passed to LLM provider
3. `FileNotFoundError` raised if either file is missing (mandatory)

### LLM Provider Interface

```python
class BaseLLMProvider(ABC):
    def __init__(self, prompt_loader: SystemPromptLoader | None = None)
    def invoke(prompt: str | list[BaseMessage], **kwargs) -> str
    def invoke_structured(prompt: str | list[BaseMessage], schema: type, **kwargs) -> Any
```

**Message Types:** Uses LangChain's `SystemMessage`, `HumanMessage`, `AIMessage`, `ToolMessage`

## 4. Data Models

| Model | Purpose |
|-------|---------|
| `Task` | Atomic action with tool_call, tool_input, depends_on |
| `Plan` | Ordered list of Tasks with reasoning |
| `TaskResult` | Execution result (success/error/result) |
| `AgentResponse` | Final user-facing response with execution trace |

## 5. Key Patterns

1. **Dependency Injection** - Agent injects LLM/MCP into nodes via closures
2. **State Immutability** - Nodes return new state: `state.copy()`
3. **Configuration-Driven** - MCP servers defined in JSON, no code changes needed
4. **Singleton Access** - Global `get_mcp_executor()` for convenience

## 6. Configuration

**Environment:** `OPENAI_API_KEY` (required), `LOG_LEVEL`, `DEBUG`

**MCP Servers:** `config/mcp_servers.json`
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "python",
      "args": ["-m", "server"],
      "transport": "stdio",
      "enabled": true
    }
  }
}
```

## 7. Error Handling

- All nodes catch exceptions → set `state["error"]`
- Errors trigger replanning (route to Planner)
- Final state always has `final_response` or `error`
- Missing SOUL.md/AGENT.md → `FileNotFoundError` (agent cannot run)

## 8. Testing

- **Unit Tests:** 93 tests covering all components
- **Style:** Functional Python (`def test_...()`), no classes
- **Coverage:** ~100% for core modules
- **Execution:** `uv run pytest tests/unit/`

## 9. Commands

```bash
uv sync          # Install dependencies
uv run pytest    # Run tests
./auto_format_ruff.sh  # Format code
```

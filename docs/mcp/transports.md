# MCP Transports

## stdio

Spawns local processes and communicates via JSON-RPC over stdin/stdout.

## http_stream

Uses HTTP streaming (`/mcp`) with session header (`mcp-session-id`) and SSE-formatted responses.

## sse

Connects to `/sse`, receives message endpoint, then exchanges JSON-RPC via HTTP POST.

All transports expose:

- `start()` / `stop()`
- `list_tools()`
- `get_tool_schemas()`
- `execute_tool()`

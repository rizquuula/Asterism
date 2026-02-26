# MCP Integration Overview

Asterism uses MCP (Model Context Protocol) to execute external tools through configurable servers.

Key files:

- `workspace/mcp_servers/mcp_servers.json` — server definitions
- `asterism/mcp/executor.py` — dynamic tool execution
- `asterism/mcp/transport_executor/*` — transport implementations

## Built-in transport support

- `stdio`
- `http_stream`
- `sse`

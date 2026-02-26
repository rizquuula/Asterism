# MCP Configuration

MCP servers are defined in `workspace/mcp_servers/mcp_servers.json`.

## Example

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
      "transport": "stdio",
      "cwd": "."
    }
  }
}
```

## Fields

- `command`: executable to start server
- `args`: command args
- `transport`: `stdio`, `http_stream`, or `sse`
- `cwd`: working directory for server process
- `enabled`: optional (default true)

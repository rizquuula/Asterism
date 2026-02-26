# Custom MCP Servers

## Add a new server

1. Add it to `workspace/mcp_servers/mcp_servers.json`
2. Choose the correct `transport`
3. Restart the API server

## Validation Checklist

- Server command runs locally
- Transport endpoint/path is reachable (for HTTP/SSE)
- Server exposes `tools/list` and `tools/call`

## Debug Tips

- Check `logs/app.log`
- Temporarily run the MCP server command directly in terminal
- Use `/v1/health` and a test chat request to confirm execution path

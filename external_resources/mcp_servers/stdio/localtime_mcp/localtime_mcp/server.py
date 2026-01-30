"""Simple MCP server that returns current local time using FastMCP."""

from datetime import UTC, datetime

from mcp.server.fastmcp import FastMCP

# Create the FastMCP instance
mcp = FastMCP("localtime-mcp")


@mcp.tool()
def get_current_time() -> dict:
    """Get the current local time with timezone information.

    Returns:
        Dictionary containing ISO datetime string, UNIX timestamp, and timezone.
    """
    now = datetime.now(UTC).astimezone()
    return {
        "iso_datetime": now.isoformat(),
        "unix_timestamp": int(now.timestamp()),
        "timezone": str(now.tzinfo),
    }


def main():
    """Run the MCP server using FastMCP stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

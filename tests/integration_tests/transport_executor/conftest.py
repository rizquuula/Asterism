"""Shared fixtures for integration tests."""

import os

import pytest


@pytest.fixture
def localtime_mcp_path():
    """Return the path to the localtime MCP server."""
    data = os.getenv("TEST_LOCALTIME_MCP_PATH")
    if data is None:
        pytest.skip("TEST_LOCALTIME_MCP_PATH not set in environment variables")
    return data


@pytest.fixture(scope="module")
def sse_server_url():
    """Return the URL for the SSE MCP server."""
    data = os.getenv("TEST_SSE_MCP_URL")
    if data is None:
        pytest.skip("TEST_LOCALTIME_MCP_PATH not set in environment variables")
    return data


@pytest.fixture(scope="module")
def http_stream_server_url():
    """Return the URL for the HTTP Stream MCP server."""
    data = os.getenv("TEST_HTTP_STREAM_MCP_URL")
    if data is None:
        pytest.skip("TEST_LOCALTIME_MCP_PATH not set in environment variables")
    return data

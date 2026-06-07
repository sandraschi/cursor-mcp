"""FastMCP server registration."""

from fastmcp import FastMCP

from .tools.cloud import cursor_cloud
from .tools.docs import cursor_docs, cursor_help
from .tools.inbox import cursor_inbox
from .tools.sdk import cursor_sdk
from .tools.usage import cursor_usage

mcp = FastMCP("cursor-mcp")

mcp.tool()(cursor_usage)
mcp.tool()(cursor_cloud)
mcp.tool()(cursor_docs)
mcp.tool()(cursor_sdk)
mcp.tool()(cursor_inbox)
mcp.tool()(cursor_help)

"""HTTP surface for fleet_bridge (Fritz)."""

from fastapi import FastAPI

from .server import mcp

_mcp_http = mcp.http_app(path="/")
app = FastAPI(title="cursor-mcp", version="0.2.0", lifespan=_mcp_http.lifespan)
app.mount("/mcp", _mcp_http)

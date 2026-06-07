"""HTTP surface for fleet_bridge (Fritz)."""

from fastapi import FastAPI

from .server import mcp

app = FastAPI(title="cursor-mcp", version="0.2.0")
app.mount("/mcp", mcp.http_app())

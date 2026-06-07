"""stdio (Cursor IDE) or HTTP (Fritz fleet_bridge)."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys

import uvicorn

from .config import load_settings
from .server import mcp


def main() -> None:
    parser = argparse.ArgumentParser(description="cursor-mcp")
    parser.add_argument("--serve", action="store_true", help="HTTP on CURSOR_MCP_HOST:PORT with /mcp")
    parser.add_argument("--stdio", action="store_true", help="MCP stdio (default)")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO, stream=sys.stderr, format="%(message)s")

    transport = os.environ.get("MCP_TRANSPORT", "").lower()
    use_http = args.serve or transport in {"http", "streamable"}

    if use_http and args.stdio:
        parser.error("Choose --serve or --stdio, not both")

    settings = load_settings()

    if use_http:
        uvicorn.run("cursor_mcp.app:app", host=settings.host, port=settings.port, log_level="info")
        return

    asyncio.run(mcp.run_stdio_async(show_banner=False))


if __name__ == "__main__":
    main()

set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

# cursor-mcp — just recipes
import 'scripts/just/fleet.just'
# cursor-mcp — just recipes

# Lint
lint:
    uv run ruff check .

# Tests
test:
    uv run pytest tests/ -v

# HTTP server (Fritz :11000)
serve:
    .\start.ps1 -Serve

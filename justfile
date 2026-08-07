set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

# --- cursor-mcp  just recipes ---
import 'scripts/just/fleet.just'
# --- cursor-mcp  just recipes ---

# Lint
lint:
    uv run ruff check .

# Tests
test:
    uv run pytest tests/ -v

# HTTP server (Fritz :11000)
serve:
    .\start.ps1 -Serve

# Bootstrap: install dev deps + pre-commit hook
bootstrap:
    uv sync --group dev
    uv run pre-commit install
    Write-Host "Pre-commit hooks installed." -ForegroundColor Green
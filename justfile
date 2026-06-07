# cursor-mcp — just recipes

# Build .mcpb Claude Desktop bundle
mcpb-pack:
    pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\mcpb\pack.ps1

# Lint
lint:
    uv run ruff check .

# Tests
test:
    uv run pytest tests/ -v

# HTTP server (Fritz :11000)
serve:
    .\start.ps1 -Serve

param(
    [switch]$Serve,
    [switch]$Stdio
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSCommandPath
Set-Location $RepoRoot

if (-not (Test-Path ".venv")) {
    Write-Host "Creating venv (uv)..." -ForegroundColor Cyan
    uv venv
    uv pip install -e .
}

if ($Serve) {
    Write-Host "cursor-mcp HTTP :11000/mcp" -ForegroundColor Green
    uv run python -m cursor_mcp --serve
}
elseif ($Stdio) {
    uv run python -m cursor_mcp --stdio
}
else {
    Write-Host "Usage: .\start.ps1 -Serve   # Fritz fleet_bridge" -ForegroundColor Yellow
    Write-Host "       .\start.ps1 -Stdio   # Cursor mcp.json" -ForegroundColor Yellow
}

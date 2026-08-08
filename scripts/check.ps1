$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
uv sync --dev
uv run pytest
uv run cad-agent-tools --version
uv build --no-sources
Write-Host "Checks and build completed." -ForegroundColor Green

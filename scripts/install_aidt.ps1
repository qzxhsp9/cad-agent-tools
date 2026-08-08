param(
    [string]$Repository = "qzxhsp9/cad-agent-tools",
    [string]$Ref = "v0.5.1"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is not available on PATH. Install uv first, then reopen PowerShell."
}

$source = "git+https://github.com/$Repository.git@$Ref"
Write-Host "Installing cad-agent-tools from $source ..." -ForegroundColor Cyan
uv tool install --force --from $source cad-agent-tools
if ($LASTEXITCODE -ne 0) { throw "uv tool install failed." }

$binDir = (uv tool dir --bin).Trim()
if (-not $binDir) { throw "uv tool dir --bin returned an empty path." }

$tool = Join-Path $binDir "cad-agent-tools.exe"
if (-not (Test-Path $tool)) {
    $tool = Join-Path $binDir "cad-agent-tools"
}
if (-not (Test-Path $tool)) {
    throw "cad-agent-tools command was not found in uv tool bin directory: $binDir"
}

Write-Host "Installed command: $tool" -ForegroundColor Green
& $tool --version
if ($LASTEXITCODE -ne 0) { throw "Version check failed." }
& $tool doctor --compact
if ($LASTEXITCODE -ne 0) { throw "Doctor check failed." }

uv tool update-shell | Out-Host

Write-Host "" 
Write-Host "Installation complete." -ForegroundColor Green
Write-Host "Close and reopen the AIDT local runner / terminal so it inherits the updated PATH." -ForegroundColor Yellow
Write-Host "Use this AIDT MCP configuration:" -ForegroundColor Cyan
@'
{
  "mcpServers": {
    "cad-agent-tools": {
      "command": "cad-agent-tools",
      "args": []
    }
  }
}
'@ | Write-Host

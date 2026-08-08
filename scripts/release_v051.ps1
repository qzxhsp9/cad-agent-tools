param(
    [string]$Repository = "qzxhsp9/cad-agent-tools",
    [switch]$SkipChecks
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git is not available on PATH."
}
if (-not (Test-Path ".git")) {
    throw "Run this script inside the existing cad-agent-tools Git repository."
}
if (-not (Select-String -Path ".\pyproject.toml" -Pattern 'version = "0.5.1"' -Quiet)) {
    throw "pyproject.toml is not version 0.5.1. Apply the v0.5.1 upgrade first."
}

if (-not $SkipChecks) {
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        throw "uv is required for checks and build. Use -SkipChecks only if already verified."
    }
    uv sync --dev
    if ($LASTEXITCODE -ne 0) { throw "uv sync failed." }
    uv run pytest
    if ($LASTEXITCODE -ne 0) { throw "pytest failed." }
    uv build --no-sources
    if ($LASTEXITCODE -ne 0) { throw "build failed." }
}

git add -A
$pending = git status --porcelain
if ($pending) {
    git commit -m "Release cad-agent-tools v0.5.1"
    if ($LASTEXITCODE -ne 0) { throw "git commit failed." }
} else {
    Write-Host "No uncommitted changes; continuing with push/tag." -ForegroundColor Yellow
}

$remoteNames = @(git remote)
if ($remoteNames -notcontains "origin") {
    git remote add origin "https://github.com/$Repository.git"
    if ($LASTEXITCODE -ne 0) { throw "git remote add origin failed." }
}

git push origin main
if ($LASTEXITCODE -ne 0) { throw "git push origin main failed." }

$tagExists = git tag --list v0.5.1
if (-not $tagExists) {
    git tag -a v0.5.1 -m "Release cad-agent-tools v0.5.1"
}
git push origin v0.5.1
if ($LASTEXITCODE -ne 0) { throw "git push origin v0.5.1 failed." }

Write-Host "Published https://github.com/$Repository tag v0.5.1" -ForegroundColor Green
Write-Host "Next: powershell -ExecutionPolicy Bypass -File .\scripts\install_aidt.ps1" -ForegroundColor Cyan

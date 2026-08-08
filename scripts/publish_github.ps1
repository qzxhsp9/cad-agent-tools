param(
    [string]$Repository = "qzxhsp9/cad-agent-tools"
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git is not available on PATH."
}
if (-not (Test-Path ".git")) {
    throw "This script updates an existing Git repository. Initialize/clone the repository first."
}

$remoteNames = @(git remote)
if ($remoteNames -notcontains "origin") {
    git remote add origin "https://github.com/$Repository.git"
    if ($LASTEXITCODE -ne 0) { throw "git remote add origin failed." }
}

git add -A
$pending = git status --porcelain
if ($pending) {
    git commit -m "Update cad-agent-tools"
}
git push -u origin main
if ($LASTEXITCODE -ne 0) { throw "git push failed." }
Write-Host "Published source to https://github.com/$Repository" -ForegroundColor Green

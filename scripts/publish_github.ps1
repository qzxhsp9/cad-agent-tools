param(
    [string]$Repository = "qzxhsp9/cad-agent-tools",
    [ValidateSet("public", "private")]
    [string]$Visibility = "public"
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git is not available on PATH."
}
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI (gh) is not available on PATH."
}

if (-not (Test-Path ".git")) {
    git init -b main
}

git add .
$pending = git status --porcelain
if ($pending) {
    git commit -m "Initial cad-agent-tools 0.5.0 package"
}

$repoExists = $true
try {
    gh repo view $Repository --json name | Out-Null
} catch {
    $repoExists = $false
}

if (-not $repoExists) {
    gh repo create $Repository --$Visibility --source . --remote origin
} elseif (-not (git remote get-url origin 2>$null)) {
    git remote add origin "https://github.com/$Repository.git"
}

git push -u origin main
Write-Host "Published source to https://github.com/$Repository" -ForegroundColor Green
Write-Host "AIDT can now use examples/aidt.github.json." -ForegroundColor Green

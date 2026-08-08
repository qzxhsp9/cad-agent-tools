param(
    [switch]$TestPyPI
)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
if (-not $env:UV_PUBLISH_TOKEN) {
    throw "Set UV_PUBLISH_TOKEN in the current process or use a Trusted Publisher workflow."
}
uv build --no-sources
if ($TestPyPI) {
    uv publish --publish-url https://test.pypi.org/legacy/
} else {
    uv publish
}

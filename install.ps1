# Thin wrapper around the cross-platform installer.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$py = "python"
if (-not (Get-Command $py -ErrorAction SilentlyContinue)) { $py = "python3" }
& $py install.py @args
exit $LASTEXITCODE

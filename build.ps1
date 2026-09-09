# Resolve the active JetBrains keymap, then generate keybindings + report.
# Extra args pass through to resolve_keymap.py (--product / --keymap / --app / --config-dir).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$py = "python"
if (-not (Get-Command $py -ErrorAction SilentlyContinue)) { $py = "python3" }
& $py resolve_keymap.py @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host ""
& $py generate.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host ""
Write-Host "next: python install.py"

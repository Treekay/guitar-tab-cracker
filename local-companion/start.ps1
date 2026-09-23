param([string]$CodexPath = '')
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $repo
$python = if (Test-Path -LiteralPath 'F:/anaconda/python.exe') { 'F:/anaconda/python.exe' } else { 'python' }
if ($CodexPath) {
    & $python -m local_companion --codex-path $CodexPath
} else {
    & $python -m local_companion
}

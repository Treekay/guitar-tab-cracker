$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $repo
$python = if (Test-Path -LiteralPath 'F:/anaconda/python.exe') { 'F:/anaconda/python.exe' } else { 'python' }
& $python -m local_companion

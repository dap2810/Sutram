# Optional developer-only test. Python and Pillow are test tools, not product dependencies.
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
& python -X utf8 (Join-Path $root 'tools\test_windows_gui.py')
if ($LASTEXITCODE -ne 0) { throw 'Native GUI smoke test failed.' }

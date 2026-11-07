$ErrorActionPreference='Stop'
$before=Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'environment-before.json') | ConvertFrom-Json
$observed=Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'environment-after-uninstaller.json') | ConvertFrom-Json
$current=[Environment]::GetEnvironmentVariable('Path','User')
if ($current -cne $observed.user_path) { throw 'User PATH changed since audit; refusing replacement' }
$old='C:\Users\dmech\AppData\Local\Sutram\bin'
$expected=(@($before.user_path -split ';' | Where-Object { $_.TrimEnd('\') -ine $old }) -join ';')
$restore='C:\Users\dmech\AppData\Local\Programs\OpenAI\Codex\bin'
if ($expected -cne ($restore+';'+$current)) { throw 'Unexpected difference beyond the missing unrelated first entry' }
[Environment]::SetEnvironmentVariable('Path',$expected,'User')
$r=[ordered]@{status='PASS';restored_entry=$restore;position='original first position';reason='Before/after audit detected this unrelated entry missing following old uninstaller cleanup';old_sutram_entry_restored=$false;machine_path_changed=$false}
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'path-restoration.json'),($r | ConvertTo-Json),[Text.UTF8Encoding]::new($false))
$r | ConvertTo-Json

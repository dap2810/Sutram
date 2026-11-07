$ErrorActionPreference='Stop'
$target='C:\Users\dmech\AppData\Local\Sutram'
$resolved=(Resolve-Path -LiteralPath $target).ProviderPath.TrimEnd('\')
if ($resolved -cne $target) { throw 'Unexpected resolved deletion target' }
$entries=@(Get-ChildItem -LiteralPath $target -Force)
if ($entries.Count -ne 1 -or $entries[0].Name -ne 'uninstall.exe' -or $entries[0].PSIsContainer) { throw 'Unexpected remaining files; refusing cleanup' }
if ((Get-FileHash -LiteralPath $entries[0].FullName).Hash -ne 'B2B1C0800848EBA1F99A807D3868B7C48845B875FE1A29CA15E157B80F158084') { throw 'Remaining uninstaller hash changed' }
Remove-Item -LiteralPath 'C:\Users\dmech\AppData\Local\Sutram\uninstall.exe'
Remove-Item -LiteralPath 'C:\Users\dmech\AppData\Local\Sutram'
$raw=[Environment]::GetEnvironmentVariable('Path','User')
$entries=@($raw -split ';')
$kept=@($entries | Where-Object { [Environment]::ExpandEnvironmentVariables($_.Trim().Trim('"')).TrimEnd('\') -ine 'C:\Users\dmech\AppData\Local\Sutram\bin' })
$pathChanged=$kept.Count -ne $entries.Count
if ($pathChanged) { [Environment]::SetEnvironmentVariable('Path',($kept -join ';'),'User') }
$r=[ordered]@{status='PASS';resolved_target=$resolved;removed=@('C:\Users\dmech\AppData\Local\Sutram\uninstall.exe','C:\Users\dmech\AppData\Local\Sutram');recursive_delete=$false;stale_user_path_removed=$pathChanged;old_folder_exists=(Test-Path -LiteralPath $target);canonical_sha256=(Get-FileHash -LiteralPath 'C:\Users\dmech\AppData\Local\Programs\Sutram\bin\sutram.exe').Hash;canonical_uninstall_key_exists=(Test-Path -LiteralPath 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram')}
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'cleanup-finish.json'),($r | ConvertTo-Json -Depth 5),[Text.UTF8Encoding]::new($false))
$r | ConvertTo-Json -Depth 5

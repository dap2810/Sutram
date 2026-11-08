$ErrorActionPreference='Stop';$out=$PSScriptRoot
if(Test-Path -LiteralPath (Join-Path $out 'uninstall-observer.json')){throw 'Observer already started'}
$p=Start-Process -FilePath "$PSHOME\powershell.exe" -ArgumentList @('-NoProfile','-File',('"'+(Join-Path $out 'watch-uninstall.ps1')+'"')) -WindowStyle Hidden -RedirectStandardOutput (Join-Path $out 'observer-stdout.txt') -RedirectStandardError (Join-Path $out 'observer-stderr.txt') -PassThru
@{pid=$p.Id;started=$p.StartTime.ToString('o')}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $out 'observer-process.json') -Encoding UTF8
Write-Host "Hidden observer PID $($p.Id)"

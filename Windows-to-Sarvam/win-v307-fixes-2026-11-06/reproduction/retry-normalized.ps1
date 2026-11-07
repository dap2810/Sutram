$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$out=Join-Path $root 'Windows-to-Sarvam\win-v307-fixes-2026-11-06'
$archive=Join-Path $out 'attempt1'
if(Test-Path -LiteralPath $archive){throw 'Already archived'}
[void](New-Item -ItemType Directory -Path $archive)
foreach($f in Get-ChildItem -LiteralPath $out -File){if($f.Name -ne 'before.json'){Copy-Item -LiteralPath $f.FullName -Destination $archive}}
$before=Get-Content -LiteralPath (Join-Path $out 'before.json') -Raw|ConvertFrom-Json
foreach($f in $before.files){if((Get-FileHash -LiteralPath (Join-Path $before.installed $f.relative)).Hash -ne $f.sha256){throw 'Working baseline changed'}}
$source=[IO.File]::ReadAllText((Join-Path $root 'Windows-to-Sarvam\win-v307-2026-11-06\install.ps1'))
$pin=(Get-FileHash (Join-Path $root 'Sutram-Setup.exe')).Hash
$source=$source.Replace('CBBFD0A66C0A9728C3FD88096631462430C0185CD8C6738964D5B885253E7481',$pin)
[IO.File]::WriteAllText((Join-Path $out 'install.ps1'),$source,[Text.UTF8Encoding]::new($false))
& (Join-Path $out 'install.ps1') -Phase upgrade

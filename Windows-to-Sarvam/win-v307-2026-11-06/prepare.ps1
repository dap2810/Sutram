param([ValidateSet('clean','upgrade','interrupt')][string]$Phase)
$ErrorActionPreference='Stop'
$parent=[IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs')).TrimEnd('\')
$src=Join-Path $parent 'Sutram'
$names=@{clean='Sutram-before-v307-20261106';upgrade='Sutram-v307-before-upgrade-20261106';interrupt='Sutram-v307-before-interruption-20261106'}
$dst=[IO.Path]::GetFullPath((Join-Path $parent $names[$Phase]))
if([IO.Path]::GetDirectoryName($dst) -ne $parent -or (Test-Path -LiteralPath $dst)){throw 'Unsafe or existing preservation destination'}
$expected=if($Phase -eq 'clean'){'D3F3DC157BADDEC973947A4D5F5B1760203542B6576B11C15AAB6A757F48DF77'}else{'0444B43552F6140147EE4701AEAC857D585086681BBE4E5BD71D8F90BEDD3F7B'}
if((Get-FileHash -LiteralPath (Join-Path $src 'bin\sutram.exe')).Hash -ne $expected){throw 'Unexpected installed compiler'}
if(Test-Path -LiteralPath (Join-Path $src 'payload.pending.sha256')){throw 'Existing installation is pending'}
$walk=$src
while($walk){if((Get-Item -LiteralPath $walk -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse ancestor'};$walk=[IO.Path]::GetDirectoryName($walk)}
if(Get-ChildItem -LiteralPath $src -Recurse -Force|Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}|Select-Object -First 1){throw 'Reparse content'}
$r=[ordered]@{phase=$Phase;at=[DateTime]::Now.ToString('o');source=$src;backup=$dst;files=@();machine_path=[Environment]::GetEnvironmentVariable('Path','Machine')}
foreach($file in (Get-ChildItem -LiteralPath $src -Recurse -Force -File)){$r.files+=@{relative=$file.FullName.Substring($src.Length+1);bytes=$file.Length;sha256=(Get-FileHash -LiteralPath $file.FullName).Hash}}
$r.file_count=$r.files.Count
if($Phase -eq 'upgrade'){Copy-Item -LiteralPath $src -Destination $dst -Recurse;$r.method='copy'}else{Move-Item -LiteralPath $src -Destination $dst;$r.method='move'}
foreach($file in $r.files){if((Get-FileHash -LiteralPath (Join-Path $dst $file.relative)).Hash -ne $file.sha256){throw 'Preserved-file mismatch'}}
$key=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Environment',($Phase -eq 'clean'))
try{
    $raw=[string]$key.GetValue('Path','',[Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames)
    $r.user_path_before=$raw;$r.user_path_after=$raw;$r.removed=@()
    if($Phase -eq 'clean'){
        $target=(Join-Path $src 'bin').TrimEnd('\');$kept=@()
        foreach($entry in ($raw -split ';')){$norm=[Environment]::ExpandEnvironmentVariables($entry.Trim().Trim('"')).TrimEnd('\');if([string]::Equals($norm,$target,[StringComparison]::OrdinalIgnoreCase)){$r.removed+=$entry}else{$kept+=,$entry}}
        $r.user_path_after=$kept -join ';';$r.path_kind=$key.GetValueKind('Path').ToString()
        $key.SetValue('Path',$r.user_path_after,$key.GetValueKind('Path'))
    }
}finally{$key.Dispose()}
$r.verified=$true
$r|ConvertTo-Json -Depth 6|Set-Content (Join-Path $PSScriptRoot ('prepare-'+$Phase+'.json')) -Encoding UTF8
Write-Host "$Phase preparation: $($r.file_count) files preserved and verified."

$ErrorActionPreference='Stop'
$parent=[IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs')).TrimEnd('\')
$src=[IO.Path]::GetFullPath((Join-Path $parent 'Sutram'))
$dst=[IO.Path]::GetFullPath((Join-Path $parent 'Sutram-A3-before-clean-v306'))
if([IO.Path]::GetDirectoryName($src) -ne $parent -or [IO.Path]::GetDirectoryName($dst) -ne $parent -or (Test-Path -LiteralPath $dst)) { throw 'Unsafe move scope' }
if(-not(Test-Path -LiteralPath (Join-Path $parent 'Sutram-before-v306\payload.manifest.sha256'))) { throw 'Original v305 backup missing' }
$walk=$src
while($walk) { if((Get-Item -LiteralPath $walk -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse ancestor' }; $walk=[IO.Path]::GetDirectoryName($walk) }
if(Get-ChildItem -LiteralPath $src -Recurse -Force | Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}|Select-Object -First 1) { throw 'Reparse content' }
$owned=Get-Content (Join-Path $PSScriptRoot 'a3.json') -Raw|ConvertFrom-Json
if(Get-Process -Id $owned.pid -ErrorAction SilentlyContinue) { throw 'A3 wizard still running' }
Move-Item -LiteralPath $src -Destination $dst
$key=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Environment',$true)
try {
    $raw=[string]$key.GetValue('Path','',[Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames)
    $kind=$key.GetValueKind('Path')
    $target=(Join-Path $src 'bin').TrimEnd('\')
    $kept=[Collections.Generic.List[string]]::new(); $removed=@()
    foreach($entry in ($raw -split ';')) {
        $normalized=[Environment]::ExpandEnvironmentVariables($entry.Trim().Trim('"')).TrimEnd('\')
        if([string]::Equals($normalized,$target,[StringComparison]::OrdinalIgnoreCase)) { $removed+=$entry } else { $kept.Add($entry) }
    }
    $after=$kept -join ';'
    $key.SetValue('Path',$after,$kind)
} finally { $key.Dispose() }
@{source=$src;preserved_after_a3=$dst;user_path_before=$raw;user_path_after=$after;removed=$removed;kind=$kind.ToString();machine_path=[Environment]::GetEnvironmentVariable('Path','Machine')}|ConvertTo-Json -Depth 5|Set-Content (Join-Path $PSScriptRoot 'path-removal.json') -Encoding UTF8
Write-Host "Preserved A3 tree; removed $($removed.Count) canonical user PATH entry."

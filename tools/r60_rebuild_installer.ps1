#requires -version 5.1
# Genuine source rebuild of the PURE NASM Windows setup EXE on GitHub Windows.
# The payload is made from the already-tested portable ZIP tree; SHA-256
# verification manifest is generated fresh, never bypassed.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$PortableDir,
      [Parameter(Mandatory=$true)][string]$OutputDir)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$portable=(Resolve-Path $PortableDir).Path
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$work=(Resolve-Path $OutputDir).Path
$manifest=Join-Path $portable 'payload.manifest.sha256'
$lines=New-Object System.Collections.Generic.List[string]
$files=@(Get-ChildItem -LiteralPath $portable -Recurse -File |
         Where-Object { $_.FullName -ne $manifest } | Sort-Object FullName)
foreach($file in $files) {
    $rel=$file.FullName.Substring($portable.Length).TrimStart('\')
    $hash=(Get-FileHash -Algorithm SHA256 -LiteralPath $file.FullName).Hash.ToLowerInvariant()
    $lines.Add($hash+' *'+$rel)
}
[IO.File]::WriteAllLines($manifest,$lines.ToArray(),([Text.UTF8Encoding]::new($false)))
Write-Host ("R60_PAYLOAD_MANIFEST source_files="+$files.Count+" path="+$manifest)
$zip=Join-Path $work 'payload.zip'
Compress-Archive -LiteralPath (Join-Path $portable '*') -DestinationPath $zip -CompressionLevel Optimal -Force
Copy-Item -LiteralPath (Join-Path $root 'windows\native-installer\install-core.ps1') -Destination (Join-Path $work 'install-core.ps1') -Force
Copy-Item -LiteralPath (Join-Path $root 'windows\native-installer\uninstall-core.ps1') -Destination (Join-Path $work 'uninstall-core.ps1') -Force
Copy-Item -LiteralPath (Join-Path $root 'icons\sutram.ico') -Destination (Join-Path $work 'sutram.ico') -Force
$nasm=(Get-Command nasm.exe -ErrorAction Stop).Source
$ld=(Get-Command ld.exe -ErrorAction Stop).Source
Push-Location $work
try{
    & $nasm -f win64 (Join-Path $root 'windows\native-installer\sutram_setup.asm') -o (Join-Path $work 'sutram_setup.obj')
    if($LASTEXITCODE -ne 0){throw 'Sutram setup NASM compilation failed'}
    & $ld -mi386pep --subsystem windows --entry=_start -o (Join-Path $work 'Sutram-Setup-R60-Fixed.exe') (Join-Path $work 'sutram_setup.obj')
    if($LASTEXITCODE -ne 0){throw 'Sutram setup PE link failed'}
}finally{Pop-Location}
$setup=Join-Path $work 'Sutram-Setup-R60-Fixed.exe'
if(-not(Test-Path $setup -PathType Leaf)){throw "Missing linked $setup"}
Write-Host ("R60_INSTALLER_SOURCE_BUILD_PASS bytes="+(Get-Item $setup).Length+" sha256="+(Get-FileHash -Algorithm SHA256 $setup).Hash.ToLowerInvariant())

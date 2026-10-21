. (Join-Path $PSScriptRoot '..\build-common.ps1')
$ProjectRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$nasm=Get-BuildTool 'nasm.exe'; $linker=Get-BuildTool 'ld.exe'
$work=Join-Path $ProjectRoot ('build\windows\setup-'+[guid]::NewGuid().ToString('N'))
$stage=Join-Path $work 'payload'
[void](New-Item -ItemType Directory -Force -Path $stage,(Join-Path $stage 'bin'),(Join-Path $stage 'win'),(Join-Path $stage 'assets'))
foreach ($pair in @(
    @('win\sutram.exe','bin\sutram.exe'),@('win\sutram.exe','win\sutram.exe'),
    @('sutram-ide-gui.exe','sutram-ide-gui.exe'),@('icons\sutram.ico','assets\sutram.ico'),
    @('LICENSE.txt','LICENSE.txt'),@('README.md','README.md'))) {
    $source=Join-Path $ProjectRoot $pair[0]
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Missing payload input: $source" }
    if ([IO.Path]::GetExtension($source) -eq '.exe') { Assert-Pe64 $source }
    Copy-Item -LiteralPath $source -Destination (Join-Path $stage $pair[1])
}
foreach ($folder in @('lang','lib','examples','docs')) {
    Copy-Item -LiteralPath (Join-Path $ProjectRoot $folder) -Destination (Join-Path $stage $folder) -Recurse
}
foreach ($destination in @('bin','win')) {
    foreach ($folder in @('lib','lang')) {
        Copy-Item -LiteralPath (Join-Path $ProjectRoot $folder) -Destination (Join-Path $stage $destination) -Recurse -Force
    }
}
# R77: require the compiler embedded by this installer to match the CURRENT
# accepted NASM source, not an older copy left in win/ by another build.
# The full build-windows-setup.ps1 wrapper regenerates win/sutram.exe first.
$compilerAsm=[IO.File]::ReadAllText((Join-Path $ProjectRoot 'src\sutram_compiler.asm'))
$sourceVersion=[regex]::Match($compilerAsm,'msg_version\s+db\s+"Sutram 1\.0 \((v[0-9]+)\)')
if (-not $sourceVersion.Success) { throw 'Cannot determine accepted compiler version from current source; refusing an unverified payload.' }
$expectedVersion=$sourceVersion.Groups[1].Value
$compilerExe=Join-Path $ProjectRoot 'win\sutram.exe'
$compilerCheck=Invoke-BoundedProcess $compilerExe @('--version') $work
if ($compilerCheck.Stdout -notmatch ('Sutram 1\.0 \(' + [regex]::Escape($expectedVersion) + '\)')) {
    throw ("STALE INSTALLER PAYLOAD: win/sutram.exe reports another version, expected " + $expectedVersion +
           ". Run windows/build-windows-setup.ps1 to rebuild the compiler and installer together.")
}
foreach ($payloadCompiler in @('bin\sutram.exe','win\sutram.exe')) {
    $embedded=Join-Path $stage $payloadCompiler
    if ((Get-FileHash -LiteralPath $embedded -Algorithm SHA256).Hash -ne
        (Get-FileHash -LiteralPath $compilerExe -Algorithm SHA256).Hash) {
        throw ("Installer payload compiler differs from verified source binary: " + $payloadCompiler)
    }
}
Write-Host ("Installer compiler payload version verified: " + $expectedVersion)
$rows=foreach ($file in Get-ChildItem -LiteralPath $stage -File -Recurse | Sort-Object FullName) {
    (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()+' *'+$file.FullName.Substring($stage.Length+1)
}
[IO.File]::WriteAllLines((Join-Path $stage 'payload.manifest.sha256'),[string[]]$rows,([Text.UTF8Encoding]::new($false)))
$zip=Join-Path $work 'payload.zip'
Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $zip -CompressionLevel Optimal
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'install-core.ps1'),(Join-Path $PSScriptRoot 'uninstall-core.ps1') -Destination $work
Copy-Item -LiteralPath (Join-Path $ProjectRoot 'LICENSE.txt') -Destination $work
$hashLines=New-Object Collections.Generic.List[string]
$hashLines.Add('section .data')
foreach ($pair in @(@('payload.zip','payload'),@('install-core.ps1','install'),@('uninstall-core.ps1','uninst'),@('LICENSE.txt','license'))) {
    $hash=(Get-FileHash -LiteralPath (Join-Path $work $pair[0]) -Algorithm SHA256).Hash
    $bytes=for ($i=0;$i -lt 64;$i+=2) { '0x'+$hash.Substring($i,2) }
    $hashLines.Add(('hash_'+$pair[1]+': db '+($bytes -join ',')))
}
$hashLines.Add('embedded_hash_table:')
foreach ($name in @('payload','install','uninst','license')) {
    $hashLines.Add(('dq blob_'+$name+',blob_'+$name+'_end-blob_'+$name+',hash_'+$name))
}
$hashLines.Add('dq 0,0,0')
[IO.File]::WriteAllLines((Join-Path $work 'embedded_hashes.inc'),$hashLines,([Text.UTF8Encoding]::new($false)))
$obj=Join-Path $work 'wizard.obj'
# R73: the wizard carries the canonical icon as a PE resource (title bar, taskbar, Explorer).
Write-IconResourceInclude (Join-Path $ProjectRoot 'icons\sutram.ico') (Join-Path $work 'r73_icon.inc') 'icons/sutram.ico'
[void](Invoke-BoundedProcess $nasm @('-f','win64','-dR73_ICON',('-I'+$work.Replace('\','/')+'/'),('-I'+$ProjectRoot.Replace('\','/')+'/'),(Join-Path $PSScriptRoot 'sutram_wizard.asm'),'-o',$obj) $work)
$out=Join-Path $ProjectRoot 'Sutram-Setup.exe'
[void](Invoke-BoundedProcess $linker @('-mi386pep','--subsystem','windows','--entry=_start','-o',$out,$obj,'-lkernel32','-lbcrypt') $work)
Assert-Pe64 $out
Write-Host ('Installer icon: ' + (Assert-PeResourceDirectory $out))
[void](Invoke-BoundedProcess $out @('--self-test') $work)
(Get-FileHash -LiteralPath $out -Algorithm SHA256).Hash.ToLowerInvariant()+' *Sutram-Setup.exe' |
    Set-Content -Encoding ASCII (Join-Path $ProjectRoot 'Sutram-Setup.sha256')
Write-Host "SETUP PASS: embedded SHA-256 self-test. Built $out"
Write-Host "Payload staging/evidence retained at $work"

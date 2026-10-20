. (Join-Path $PSScriptRoot '..\build-common.ps1')
$ProjectRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$nasm=Get-BuildTool 'nasm.exe'; $linker=Get-BuildTool 'ld.exe'
$python=Get-BuildTool 'python.exe' # Developer-only; never included in user payload.
$principal=New-Object Security.Principal.WindowsPrincipal ([Security.Principal.WindowsIdentity]::GetCurrent())
if ($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Build Sutram from a standard-user, non-elevated PowerShell session.'
}
$work=Join-Path $ProjectRoot ('build\windows\setup-'+[guid]::NewGuid().ToString('N'))
$stage=Join-Path $work 'payload'
[void](New-Item -ItemType Directory -Force -Path $stage,(Join-Path $stage 'bin'),(Join-Path $stage 'win'),(Join-Path $stage 'assets'))
# R80: always compile the canonical, source-locked compiler into a fresh work path.
# A version string is NOT build provenance, and committed win/sutram.exe may be stale.
$compiler=Join-Path $work 'compiler.exe'
$compilerReport=Join-Path $work 'compiler-build.json'
$buildTool=Join-Path $ProjectRoot 'tools\r69_build.py'
$verifyTool=Join-Path $ProjectRoot 'tools\r80_payload_verify.py'
# R81: refuse to package a correctly source-pinned compiler with a stale
# user-visible banner (current CHANGELOG version versus NASM msg_version).
# This is a source-only preflight; no production binary is published on failure.
$versionGate=Join-Path $ProjectRoot 'tools\r81_version_gate.py'
[void](Invoke-BoundedProcess $python @($versionGate,'--repo',$ProjectRoot) $ProjectRoot 30000)
[void](Invoke-BoundedProcess $python @($buildTool,'--target','windows','--output',$compiler,
    '--report',$compilerReport,'--nasm',$nasm,'--linker',$linker) $ProjectRoot 300000)
Assert-Pe64 $compiler
$versionCheck=Invoke-BoundedProcess $compiler @('--version') $ProjectRoot
if ([string]::IsNullOrWhiteSpace($versionCheck.Stdout)) { throw 'Compiler returned an empty version response.' }
# Match a known program result, never localized diagnostic prose.
$hello=Join-Path $work 'hello.exe'
[void](Invoke-BoundedProcess $compiler @((Join-Path $ProjectRoot 'examples\01_hello.sm'),$hello) $ProjectRoot)
Assert-Pe64 $hello
$helloCheck=Invoke-BoundedProcess $hello @() $ProjectRoot
if ($helloCheck.Stdout.Replace([string][char]13,'') -ne ('Namaste, Sutram!'+[char]10)) {
    throw 'Fresh compiler generated-hello output mismatch.'
}
foreach ($destination in @('bin\sutram.exe','win\sutram.exe')) {
    Copy-Item -LiteralPath $compiler -Destination (Join-Path $stage $destination)
}
foreach ($pair in @(
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
$rows=foreach ($file in Get-ChildItem -LiteralPath $stage -File -Recurse | Sort-Object FullName) {
    (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()+' *'+$file.FullName.Substring($stage.Length+1)
}
[IO.File]::WriteAllLines((Join-Path $stage 'payload.manifest.sha256'),[string[]]$rows,([Text.UTF8Encoding]::new($false)))
$zip=Join-Path $work 'payload.zip'
Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $zip -CompressionLevel Optimal
$verifyArgs=@($verifyTool,'--repo',$ProjectRoot,'--compiler',$compiler,
    '--build-report',$compilerReport,'--payload',$zip)
[void](Invoke-BoundedProcess $python ($verifyArgs+@('--report',(Join-Path $work 'payload-verified.json'))) $ProjectRoot 300000)
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
# Do not replace the published setup until candidate checks succeed.
$candidate=Join-Path $work 'Sutram-Setup.candidate.exe'
[void](Invoke-BoundedProcess $linker @('-mi386pep','--subsystem','windows','--entry=_start','-o',$candidate,$obj,'-lkernel32','-lbcrypt') $work)
Assert-Pe64 $candidate
Write-Host ('Installer icon: ' + (Assert-PeResourceDirectory $candidate))
$selfTest=Invoke-BoundedProcess $candidate @('--self-test') $work
$evidencePath=Join-Path $work 'setup-verified.json'
[void](Invoke-BoundedProcess $python ($verifyArgs+@('--setup',$candidate,'--report',$evidencePath)) $ProjectRoot 300000)
$evidence=[IO.File]::ReadAllText($evidencePath,[Text.Encoding]::UTF8) | ConvertFrom-Json
$evidence | Add-Member -NotePropertyName runtime_smoke_checks -NotePropertyValue @{
    compiler_version=$versionCheck; generated_hello=$helloCheck; setup_self_test=$selfTest
}
# These smoke checks are NOT owner acceptance of install/upgrade/uninstall.
$evidence | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $evidencePath -Encoding UTF8
$out=Join-Path $ProjectRoot 'Sutram-Setup.exe'
$existing=Get-Item -LiteralPath $out -Force -ErrorAction SilentlyContinue
if ($existing -and ($existing.PSIsContainer -or ($existing.Attributes -band [IO.FileAttributes]::ReparsePoint))) {
    throw 'Published setup path is nonregular/reparse; refusing replacement.'
}
if ($existing) {
    [IO.File]::Replace($candidate,$out,(Join-Path $work 'previous-setup.exe'))
} else {
    [IO.File]::Move($candidate,$out)
}
$publishedHash=(Get-FileHash -LiteralPath $out -Algorithm SHA256).Hash.ToLowerInvariant()
if ($publishedHash -ne $evidence.installer_sha256) { throw 'Published setup SHA-256 mismatch.' }
$publishedHash+' *Sutram-Setup.exe' | Set-Content -Encoding ASCII (Join-Path $ProjectRoot 'Sutram-Setup.sha256')
Copy-Item -LiteralPath $evidencePath -Destination (Join-Path $ProjectRoot 'Sutram-Setup.evidence.json') -Force
Write-Host ('PAYLOAD SHA-256: '+$evidence.payload_sha256)
Write-Host ('COMPILER SHA-256: '+$evidence.compiler_sha256)
Write-Host ('SETUP SHA-256: '+$publishedHash)
Write-Host ('SOURCE PINS CHECKED: '+@($evidence.source_inputs.PSObject.Properties).Count)
Write-Host "SETUP BUILD VERIFIED: $out. Owner install/upgrade/uninstall acceptance remains separate."
Write-Host "Payload and raw build evidence retained at $work"

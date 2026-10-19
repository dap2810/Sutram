. (Join-Path $PSScriptRoot 'build-common.ps1')
$nasm=Get-BuildTool 'nasm.exe'; $linker=Get-BuildTool 'ld.exe'
$build=Join-Path $ProjectRoot 'build\windows'
[void](New-Item -ItemType Directory -Force -Path $build,(Join-Path $ProjectRoot 'win'))
$obj=Join-Path $build 'sutram.obj'
$exe=Join-Path $ProjectRoot 'win\sutram.exe'
$inc=($ProjectRoot.Replace('\','/')+'/')
[void](Invoke-BoundedProcess $nasm @('-f','win64','-dWINDOWS',('-I'+$inc),'src/r68_compiler_entry.asm','-o',$obj) $ProjectRoot)
[void](Invoke-BoundedProcess $linker @('-mi386pep','--entry=_start','-o',$exe,$obj) $ProjectRoot)
Assert-Pe64 $exe
[void](Invoke-BoundedProcess $exe @('--version') $ProjectRoot)
$out=Join-Path $build 'hello.exe'
[void](Invoke-BoundedProcess $exe @('examples/01_hello.sm',$out) $ProjectRoot)
Assert-Pe64 $out
$run=Invoke-BoundedProcess $out @() $ProjectRoot
if ($run.Stdout.Replace([string][char]13,'') -ne ('Namaste, Sutram!'+[char]10)) { throw 'Compiled hello output mismatch.' }
foreach ($folder in @('lib','lang')) {
    Copy-Item -LiteralPath (Join-Path $ProjectRoot $folder) -Destination (Join-Path $ProjectRoot 'win') -Recurse -Force
}
Write-Host 'COMPILER PASS: native host and generated hello executed on Windows.'

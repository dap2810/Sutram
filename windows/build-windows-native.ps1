# R69: modern pure-NASM entry, replacing the obsolete generated compiler + host path.
[CmdletBinding()]
param([string]$NasmPath = 'nasm.exe', [string]$LinkerPath = 'ld.exe',
      [string]$OutputPath = '', [switch]$ReplaceOutput)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
. (Join-Path $PSScriptRoot 'r69-build-common.ps1')
Assert-R69StandardUser
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Assert-R69SourcePins $Root
if (-not $OutputPath) { $OutputPath = Join-Path $Root 'win\sutram.exe' }
$OutputPath = [IO.Path]::GetFullPath($OutputPath)
$nasm = (Get-Command $NasmPath -ErrorAction Stop).Source
$linker = (Get-Command $LinkerPath -ErrorAction Stop).Source
$work = Join-Path $env:TEMP ('sutram-r69-native-' + [guid]::NewGuid().ToString('N'))
[void](New-Item -ItemType Directory -Path $work)
try {
    $obj = Join-Path $work 'compiler.obj'
    $candidate = Join-Path $work 'sutram.exe'
    $entry = Join-Path $Root 'src\r68_compiler_entry.asm'
    $include = $Root + [IO.Path]::DirectorySeparatorChar
    [void](Invoke-R69Process $nasm @('-f','win64','-DWINDOWS=1','-I',$include,$entry,'-o',$obj) $Root)
    [void](Invoke-R69Process $linker @('-mi386pep','--subsystem','console','--entry=_start','-o',$candidate,$obj) $Root)
    Assert-R69Pe64 $candidate
    $version = Invoke-R69Process $candidate @('--version') $Root 20
    if ($version.Stdout -notmatch 'Sutram') { throw 'Version smoke check failed.' }
    $source = Join-Path $work 'hello.sm'
    $program = Join-Path $work 'hello.exe'
    [IO.File]::WriteAllText($source, "mukhya() {`n    likha(7)`n}`n", (New-Object Text.UTF8Encoding($false)))
    [void](Invoke-R69Process $candidate @($source,$program) $Root 20)
    Assert-R69Pe64 $program
    $hello = Invoke-R69Process $program @() $Root 20
    if ($hello.Stdout -ne "7`n" -or $hello.Stderr) { throw 'Native generated-program stdout differs from 7 + LF.' }
    $bad = Join-Path $work 'invalid.sm'
    $badOutput = Join-Path $work 'invalid.exe'
    [byte[]]$prefix = [Text.Encoding]::ASCII.GetBytes("mukhya() {`n    vitti x = ")
    [byte[]]$invalid = $prefix + [byte[]]@(0xe0,0xa5,0xff,0x0a,0x7d,0x0a)
    [IO.File]::WriteAllBytes($bad,$invalid)
    $rejected = Invoke-R69Process $candidate @($bad,$badOutput) $Root 20 1
    $wanted = "Sutram Error [E_UTF8]: ${bad}:2: invalid or truncated UTF-8 in source code`n"
    if (-not $rejected.Stdout.EndsWith($wanted) -or (Get-Item -LiteralPath $badOutput -Force -ErrorAction SilentlyContinue)) {
        throw 'R68 malformed-UTF8 diagnostic smoke gate failed or left an executable.'
    }
    Assert-R69SourcePins $Root
    Publish-R69Artifact $candidate $OutputPath ([bool]$ReplaceOutput)
    Write-Host "Built and smoke-tested canonical Windows compiler: $OutputPath"
    Write-Host ('SHA256: ' + (Get-FileHash -LiteralPath $OutputPath -Algorithm SHA256).Hash)
    Write-Host 'These smoke checks are not GUI, installer, full regression or release acceptance.'
} finally {
    if (Test-Path -LiteralPath $work) { Remove-Item -LiteralPath $work -Recurse -Force }
}

# R72 Windows Unicode execution probe. Run only on real non-elevated Windows.
param([string]$Compiler="", [string]$Evidence="")
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest
. (Join-Path $PSScriptRoot 'build-common.ps1')
$identity=[Security.Principal.WindowsIdentity]::GetCurrent()
$principal=New-Object Security.Principal.WindowsPrincipal($identity)
if ($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw "R72 requires a non-elevated standard-user process"
}
if (-not $Compiler) { $Compiler=Join-Path $ProjectRoot 'win\sutram.exe' }
$Compiler=[IO.Path]::GetFullPath($Compiler)
if (-not (Test-Path -LiteralPath $Compiler -PathType Leaf)) { throw "Compiler missing" }
Assert-Pe64 $Compiler
$fixture=Join-Path $ProjectRoot 'examples\218_sanskrit_devanagari.sm'
$expectedFile=Join-Path $ProjectRoot 'tests\expect\218_sanskrit_devanagari.out'
if (-not (Test-Path -LiteralPath $fixture -PathType Leaf)) { throw "Sanskrit source missing" }
if (-not (Test-Path -LiteralPath $expectedFile -PathType Leaf)) { throw "Accepted output missing" }
$nl=[string][char]10
$crlf=([string][char]13)+([string][char]10)
$expected=[IO.File]::ReadAllText($expectedFile,[Text.Encoding]::UTF8).Replace($crlf,$nl)
$work=Join-Path ([IO.Path]::GetTempPath()) ('sutram-r72-'+[guid]::NewGuid().ToString('N'))
[void](New-Item -Path $work -ItemType Directory -ErrorAction Stop)
try {
    $version=Invoke-BoundedProcess $Compiler @('--version') $ProjectRoot
    $output=Join-Path $work 'sanskrit.exe'
    $compile=Invoke-BoundedProcess $Compiler @('--lang','sanskrit',$fixture,$output) $ProjectRoot
    Assert-Pe64 $output
    $run=Invoke-BoundedProcess $output @() $ProjectRoot
    $actual=$run.Stdout.Replace($crlf,$nl)
    if ($actual -cne $expected) { throw 'Unicode stdout mismatch' }
    $result=[ordered]@{
        scope='real Windows CLI and generated executable only'
        target='Windows AMD64 PE32+'
        standard_user=$true
        compiler_sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $Compiler).Hash.ToLowerInvariant()
        generated_pe_sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $output).Hash.ToLowerInvariant()
        version_stdout=$version.Stdout
        source='examples/218_sanskrit_devanagari.sm'
        native_stdout=$actual
        native_exit=$run.Code
        result='PASS'
        gui_open_edit_run_close='NOT_RUN'
        installer='NOT_RUN'
        terminal_glyph_visual='NOT_RUN'
    }
    if ($Evidence) {
        if (Test-Path -LiteralPath $Evidence) { throw 'Evidence path must be fresh' }
        $json=$result|ConvertTo-Json -Depth 4
        [IO.File]::WriteAllText([IO.Path]::GetFullPath($Evidence),$json,[Text.UTF8Encoding]::new($false))
    }
    $result|ConvertTo-Json -Depth 4
} finally {
    if (Test-Path -LiteralPath $work) { Remove-Item -LiteralPath $work -Recurse -Force }
}

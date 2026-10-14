#requires -version 5.1
# R61: staged native compiler fault localisation, run deliberately on real Windows.
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File tools/r61_windows_compiler_diagnostics.ps1
# Never elevate, disable UAC, or modify user security settings.
[CmdletBinding()]
param(
    [string]$ResultsDir = "",
    [int]$TimeoutMs = 8000,
    [string]$NasmPath = "",
    [string]$LinkerPath = "",
    [string]$LegacyCompiler = ""
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (-not $ResultsDir) { $ResultsDir = Join-Path $env:TEMP ('Sutram-R61-' + [guid]::NewGuid().ToString('N')) }
New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null
$ResultsDir = (Resolve-Path -LiteralPath $ResultsDir).Path
if ($TimeoutMs -lt 1000 -or $TimeoutMs -gt 60000) { throw 'TimeoutMs must be 1000..60000.' }
if (-not $NasmPath) {
    $n = Get-Command nasm.exe -ErrorAction SilentlyContinue
    if (-not $n) { $n = Get-Command nasm -ErrorAction SilentlyContinue }
    if (-not $n) { throw 'A Windows NASM is required (nasm.exe in PATH or -NasmPath).' }
    $NasmPath = $n.Source
}
if (-not $LinkerPath) {
    $ld = Get-Command ld.exe -ErrorAction SilentlyContinue
    if (-not $ld) { throw 'A MinGW PE64 linker is required (ld.exe in PATH or -LinkerPath).' }
    $LinkerPath = $ld.Source
}
$srcAsm = Join-Path $root 'src\sutram_compiler.asm'
$fixture = Join-Path $ResultsDir 'win_native_test.sm'
[IO.File]::WriteAllText($fixture, ("mukhya() {" + [Environment]::NewLine + '    likha("WIN_NATIVE_TEST_OK")' + [Environment]::NewLine + "}" + [Environment]::NewLine), ([Text.UTF8Encoding]::new($false)))
function Invoke-Bounded([string]$Path, [string]$Arguments, [string]$Tag, [string]$WatchOutput = "") {
    $out = Join-Path $ResultsDir ($Tag + '.stdout.txt')
    $err = Join-Path $ResultsDir ($Tag + '.stderr.txt')
    $sw = [Diagnostics.Stopwatch]::StartNew()
    $startup = @{ FilePath=$Path; WorkingDirectory=$root; PassThru=$true; NoNewWindow=$true; RedirectStandardOutput=$out; RedirectStandardError=$err }
    if ($Arguments) { $startup.ArgumentList = $Arguments }
    $proc = Start-Process @startup
    $timedOut = $false
    $oversize = $false
    try {
        # Enforce size and wall-clock limits; the R60 native failure wrote
        # more than 500 MB of zero padding in less than 12 seconds.
        while (-not $proc.HasExited -and $sw.ElapsedMilliseconds -lt $TimeoutMs) {
            if ($WatchOutput -and (Test-Path -LiteralPath $WatchOutput -PathType Leaf) -and
                (Get-Item -LiteralPath $WatchOutput).Length -gt 65536) {
                $oversize = $true
                break
            }
            Start-Sleep -Milliseconds 80
            $proc.Refresh()
        }
        if (-not $proc.HasExited) {
            $timedOut = -not $oversize
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            [void]$proc.WaitForExit(3000)
        }
        $code = if ($oversize) { -9998 } elseif ($timedOut) { -9999 } else { $proc.ExitCode }
    } finally { $sw.Stop(); $proc.Dispose() }
    $stdout = if(Test-Path $out) {[IO.File]::ReadAllText($out)} else {''}
    $stderr = if(Test-Path $err) {[IO.File]::ReadAllText($err)} else {''}
    Write-Host ("R61_STAGE tag={0} timeout={1} oversize={2} exit={3} ms={4} stdout={5} stderr={6}" -f $Tag,$timedOut,$oversize,$code,$sw.ElapsedMilliseconds,($stdout -replace "[\r\n]+"," | "),($stderr -replace "[\r\n]+"," | "))
    if ($oversize) { Write-Host ("R61_PE_SIZE_REGRESSION bytes=" + (Get-Item -LiteralPath $WatchOutput).Length) }
    return [pscustomobject]@{ Tag=$Tag; TimedOut=$timedOut; Oversize=$oversize; Exit=$code; Ms=$sw.ElapsedMilliseconds; Stdout=$stdout; Stderr=$stderr }
}
function Compile-Native([string]$Tag, [string]$ExtraDefine = '') {
    $obj = Join-Path $ResultsDir ($Tag + '.obj')
    $exe = Join-Path $ResultsDir ($Tag + '.exe')
    $params = @('-f','win64','-dWINDOWS')
    if ($ExtraDefine) { $params += $ExtraDefine }
    $params += @('-I.',$srcAsm,'-o',$obj)
    Push-Location $root
    try {
        & $NasmPath @params
        if ($LASTEXITCODE -ne 0) { throw "NASM failed for $Tag (exit $LASTEXITCODE)." }
        & $LinkerPath -mi386pep --entry=_start -o $exe $obj
        if ($LASTEXITCODE -ne 0) { throw "PE linker failed for $Tag (exit $LASTEXITCODE)." }
    } finally { Pop-Location }
    $header=[IO.File]::ReadAllBytes($exe)
    if ($header.Length -lt 512 -or $header[0] -ne 77 -or $header[1] -ne 90) { throw "Not a PE file: $exe" }
    Write-Host ("R61_BUILT tag={0} bytes={1} sha256={2}" -f $Tag, $header.Length, (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant())
    return $exe
}
Write-Host ("R61_ENVIRONMENT user={0} os={1} nasm={2} linker={3} workdir={4}" -f $env:USERNAME,[Environment]::OSVersion,$NasmPath,$LinkerPath,$ResultsDir)
Write-Host ("R61_SOURCE_SHA256 compiler={0}" -f (Get-FileHash -LiteralPath $srcAsm -Algorithm SHA256).Hash.ToLowerInvariant())
$reference = Compile-Native 'sutram-r61-fresh'
if ($LegacyCompiler) {
    if (-not (Test-Path -LiteralPath $LegacyCompiler -PathType Leaf)) { throw 'Specified LegacyCompiler not found.' }
    Write-Host ("R61_LEGACY_SHA256 "+(Get-FileHash -LiteralPath $LegacyCompiler -Algorithm SHA256).Hash.ToLowerInvariant())
    [void](Invoke-Bounded $LegacyCompiler '--version' 'legacy-version')
    $oldOut = Join-Path $ResultsDir 'legacy_program.exe'
    [void](Invoke-Bounded $LegacyCompiler ('"' + $fixture + '" "' + $oldOut + '"') 'legacy-compile' $oldOut)
}
# Probe instructions are already defined at compiler entry. No instrumentation
# inside production code or mutation of any accepted codegen baseline.
for ($i=0; $i -le 7; $i++) {
    $probe = Compile-Native ("probe-" + $i) ("-DR49_WIN_DIAG_" + $i)
    $out = Join-Path $ResultsDir ("probe-" + $i + '-program.exe')
    [void](Invoke-Bounded $probe ('"' + $fixture + '" "' + $out + '"') ("probe-" + $i))
}
$ver = Invoke-Bounded $reference '--version' 'fresh-version'
$help = Invoke-Bounded $reference '--help' 'fresh-help'
$check = Invoke-Bounded $reference ('--check "' + $fixture + '"') 'fresh-check'
$exe = Join-Path $ResultsDir 'fresh-program.exe'
$compiled = Invoke-Bounded $reference ('"' + $fixture + '" "' + $exe + '"') 'fresh-compile' $exe
if (!$compiled.TimedOut -and $compiled.Exit -eq 0 -and (Test-Path -LiteralPath $exe -PathType Leaf)) {
    Write-Host ("R61_PE_NORMAL_SIZE bytes=" + (Get-Item -LiteralPath $exe).Length)
    if ((Get-Item -LiteralPath $exe).Length -gt 65536) { throw "R61 PE output unexpectedly exceeds 64 KiB" }
    $prog = Invoke-Bounded $exe '' 'fresh-program'
    if (!$prog.TimedOut -and $prog.Exit -eq 0 -and $prog.Stdout.Contains('WIN_NATIVE_TEST_OK')) {
        Write-Host 'R61_WINDOWS_COMPILE_EXECUTE_PASS'
    } else {
        Write-Host 'R61_WINDOWS_COMPILE_EXECUTE_FAIL: generated PE runtime failed'
    }
} else {
    Write-Host 'R61_WINDOWS_COMPILE_EXECUTE_FAIL: compiler did not produce a program'
}
Write-Host "R61_DIAGNOSTICS_COMPLETE $ResultsDir"
Write-Host 'Interpretation: probe 0/1/2 isolate bootstrap, probe 3 file read (exit=source byte length), probe 4 graph, 5 import expansion, 6 lexer, 7 parser. A completing probe does NOT prove downstream phases.'

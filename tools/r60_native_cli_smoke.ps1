#requires -version 5.1
# Real Windows command-line Sutram compiler acceptance, isolated from GUI.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$PortableDir)
$ErrorActionPreference='Stop'
$dir=(Resolve-Path -LiteralPath $PortableDir).Path
$compiler=Join-Path $dir 'win\sutram.exe'
if(-not (Test-Path -LiteralPath $compiler)){throw "Missing native compiler $compiler"}
$src=Join-Path $dir 'r60_cli_test.sm'
$exe=Join-Path $dir 'r60_cli_test.exe'
$program='mukhya() {' + "`r`n" + '    likha("WIN_NATIVE_TEST_OK")' + "`r`n" + '}'
[IO.File]::WriteAllText($src,$program,([Text.UTF8Encoding]::new($false)))
Write-Host "R60_CLI_SOURCE $src"
Write-Host "R60_CLI_COMPILER sha256=$((Get-FileHash -Algorithm SHA256 -LiteralPath $compiler).Hash.ToLowerInvariant())"
$timer=[Diagnostics.Stopwatch]::StartNew()
$stdout=Join-Path $dir 'r60_cli_stdout.txt'
$stderr=Join-Path $dir 'r60_cli_stderr.txt'
$process=Start-Process -FilePath $compiler -ArgumentList ('"' + $src + '" "' + $exe + '"') -NoNewWindow -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
try {
    if(-not $process.WaitForExit(12000)) {
        Write-Host "R60_CLI_COMPILER_TIMEOUT 12000ms: native compiler is hanging independently of the GUI"
        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        throw 'Native Sutram compiler failed to exit in 12 seconds'
    }
    $compileExit=$process.ExitCode
} finally { $timer.Stop() }
Write-Host "R60_CLI_COMPILE exit=$compileExit elapsed_ms=$($timer.ElapsedMilliseconds) output_exists=$(Test-Path -LiteralPath $exe)"
Write-Host ("R60_CLI_STDOUT "+([IO.File]::ReadAllText($stdout)))
Write-Host ("R60_CLI_STDERR "+([IO.File]::ReadAllText($stderr)))
if($compileExit -ne 0 -or -not(Test-Path $exe)){throw 'Native Sutram compiler failed independent CLI test'}
$timer.Restart()
& $exe
$programExit=$LASTEXITCODE
$timer.Stop()
Write-Host "R60_CLI_EXECUTE exit=$programExit elapsed_ms=$($timer.ElapsedMilliseconds)"
if($programExit -ne 0){throw "Native Sutram executable returned $programExit"}
Write-Host "R60_CLI_COMPILE_EXEC_PASS; inspect stdout for WIN_NATIVE_TEST_OK"

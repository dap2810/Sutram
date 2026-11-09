# R162 (ChatGPT R223 A): what is already at <InstallDir>.sutram-lock, run against the installer's own Open-SutramLock
# (taken from install-core.ps1 by its syntax tree, as the other fixtures here do). Everything is under build\.
#   1  nothing there: the lock is made, holds the marker, and is gone when it closes
#   2  a user's file with content there: the run stops with the "not a Sutram lock" message, and the file is unchanged
#   3  an empty file (a lock left by v315 or earlier after the machine stopped): it is taken, and gone when it closes
#   4  a stale marked lock: the same
#   5  a lock another process holds: "Another Sutram installer or uninstaller is working", and the holder keeps it
# Written in the Linux container, where PowerShell could not be run: NOT RUN by its author.
#   powershell -NoProfile -ExecutionPolicy Bypass -File tests\windows\test_installer_lock_file.ps1
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$t = $null; $e = $null
$ast = [Management.Automation.Language.Parser]::ParseFile((Join-Path $root 'windows\native-installer\install-core.ps1'), [ref]$t, [ref]$e)
if ($e.Count) { throw ($e | Out-String) }
$f = $ast.Find({ param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq 'Open-SutramLock' }, $true)
if (-not $f) { throw 'Missing Open-SutramLock' }
. ([ScriptBlock]::Create($f.Extent.Text))
$work = Join-Path $root ('build\lock-file-fixture-' + [guid]::NewGuid().ToString('N'))
[void][IO.Directory]::CreateDirectory($work)
$checks = [ordered]@{}
$mark = [Text.Encoding]::ASCII.GetBytes("Sutram installer lock`r`n")
function Same([string]$Path, [byte[]]$Bytes) { [IO.File]::Exists($Path) -and [Convert]::ToBase64String([IO.File]::ReadAllBytes($Path)) -eq [Convert]::ToBase64String($Bytes) }
# 1
$p = Join-Path $work 'one.sutram-lock'
$l = Open-SutramLock $p
$l.Position = 0; $buf = New-Object byte[] 64; $n = $l.Read($buf, 0, 64)
$checks.c1_made_and_marked = ($n -eq $mark.Length)
$l.Dispose()
$checks.c1_gone_when_closed = (-not [IO.File]::Exists($p))
# 2
$p = Join-Path $work 'two.sutram-lock'
$user = [Text.Encoding]::UTF8.GetBytes("my notes`r`n")
[IO.File]::WriteAllBytes($p, $user)
$msg = ''
try { $l = Open-SutramLock $p; $l.Dispose() } catch { $msg = $_.Exception.Message }
$checks.c2_refused = ($msg -like 'A file that is not a Sutram lock*')
$checks.c2_user_file_unchanged = (Same $p $user)
# 3
$p = Join-Path $work 'three.sutram-lock'
[IO.File]::WriteAllBytes($p, [byte[]]@())
$l = Open-SutramLock $p; $l.Dispose()
$checks.c3_empty_stale_taken_and_gone = (-not [IO.File]::Exists($p))
# 4
$p = Join-Path $work 'four.sutram-lock'
[IO.File]::WriteAllBytes($p, $mark)
$l = Open-SutramLock $p; $l.Dispose()
$checks.c4_marked_stale_taken_and_gone = (-not [IO.File]::Exists($p))
# 5
$p = Join-Path $work 'five.sutram-lock'
$holder = Open-SutramLock $p
$msg = ''
try { $l = Open-SutramLock $p; $l.Dispose() } catch { $msg = $_.Exception.Message }
$checks.c5_held_refused = ($msg -like 'Another Sutram installer or uninstaller is working*')
$checks.c5_holder_keeps_it = [IO.File]::Exists($p)
$holder.Dispose()
foreach ($key in $checks.Keys) { Write-Output ((@('FAIL', 'PASS')[[int][bool]$checks[$key]]) + ' ' + $key) }
Write-Output ('Evidence: ' + $work)
if ($checks.Values -contains $false) { exit 1 }

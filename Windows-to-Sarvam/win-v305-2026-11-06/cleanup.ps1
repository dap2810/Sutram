$ErrorActionPreference='Stop'
$OutDir=$PSScriptRoot
. (Join-Path $PSScriptRoot 'ui-helper.ps1')
Add-Type -TypeDefinition @'
using System; using System.Collections.Generic; using System.Runtime.InteropServices; using System.Text;
public static class CleanupUI {
 public delegate bool Callback(IntPtr h,IntPtr l);
 [DllImport("user32.dll")] static extern bool EnumChildWindows(IntPtr h,Callback cb,IntPtr l);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] static extern int GetWindowTextW(IntPtr h,StringBuilder b,int n);
 public static string Children(IntPtr h) { var lines=new List<string>(); EnumChildWindows(h,delegate(IntPtr c,IntPtr l) { var b=new StringBuilder(4096); GetWindowTextW(c,b,b.Capacity); lines.Add(b.ToString()); return true; },IntPtr.Zero); return string.Join("\n",lines); }
}
'@
$target='C:\Users\dmech\AppData\Local\Sutram'
$resolved=(Resolve-Path -LiteralPath $target).ProviderPath.TrimEnd('\')
if ($resolved -cne $target) { throw 'Resolved target is not the explicitly requested old installation' }
if ((Get-Item -LiteralPath $target).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Old install root is a reparse point' }
$reparse=@(Get-ChildItem -LiteralPath $target -Force -Recurse | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint })
if ($reparse.Count) { throw 'Old install contains reparse points; refusing recursive cleanup' }
$beforeHash=(Get-FileHash -LiteralPath "$target\bin\sutram.exe").Hash
if ($beforeHash -ne '441DB69C3BCC04576BEBFC4D87B1D43A53D3B1E7497CCAEB7A00BFAC6E78C2A8') { throw 'Old binary identity changed' }
$canonical=Join-Path $env:LOCALAPPDATA 'Programs\Sutram\bin\sutram.exe'
$canonicalHash=(Get-FileHash -LiteralPath $canonical).Hash
$r=[ordered]@{target=$target;resolved=$resolved;old_sha256=$beforeHash;canonical_sha256_before=$canonicalHash;started=[DateTime]::Now.ToString('o');dialogs=@();actions=@()}
$p=$null
try {
    $uninstaller=Join-Path $target 'uninstall.exe'
    $r.uninstaller_sha256=(Get-FileHash -LiteralPath $uninstaller).Hash
    $p=Start-Process -FilePath $uninstaller -ArgumentList '/uninstall' -WorkingDirectory $target -WindowStyle Hidden -PassThru
    $r.command='"'+$uninstaller+'" /uninstall'
    $watch=[Diagnostics.Stopwatch]::StartNew()
    while (-not $p.HasExited -and $watch.Elapsed.TotalSeconds -lt 30) {
        foreach ($h in [SutramIde]::WindowsOf([uint32]$p.Id,'#32770')) {
            $words=[CleanupUI]::Children($h)
            if ($words -match 'Remove Sutram 1\.4\.0') {
                $r.dialogs += $words
                $yes=[SutramIde]::GetDlgItem($h,6)
                [void][SutramIde]::PostMessageW($yes,0xF5,[IntPtr]::Zero,[IntPtr]::Zero)
            } elseif ($words -match 'has been uninstalled') {
                $r.dialogs += $words
                $ok=[SutramIde]::GetDlgItem($h,1)
                [void][SutramIde]::PostMessageW($ok,0xF5,[IntPtr]::Zero,[IntPtr]::Zero)
            }
        }
        Start-Sleep -Milliseconds 200
    }
    if (-not $p.HasExited) { $p.Kill(); [void]$p.WaitForExit(3000); throw 'Old uninstaller timed out after 30 seconds' }
    $r.uninstaller_exit=$p.ExitCode
    $r.actions += 'Ran the old installation own uninstaller and confirmed its removal dialog.'
    [void](Wait-Until { -not (Test-Path -LiteralPath $target) } 10000)
    $r.old_folder_remains=Test-Path -LiteralPath $target
    if ($r.old_folder_remains) { throw 'Old folder remains after uninstaller; inspect before further action' }
    # Remove only an exact stale old-install entry if the uninstaller left it.
    $raw=[Environment]::GetEnvironmentVariable('Path','User')
    $oldBin=Join-Path $target 'bin'
    $entries=@($raw -split ';')
    $kept=@($entries | Where-Object { [Environment]::ExpandEnvironmentVariables($_.Trim().Trim('"')).TrimEnd('\') -ine $oldBin })
    if ($kept.Count -ne $entries.Count) {
        [Environment]::SetEnvironmentVariable('Path',($kept -join ';'),'User')
        $r.actions += 'Removed exact old-install bin entry from user PATH.'
    }
    $r.canonical_sha256_after=(Get-FileHash -LiteralPath $canonical).Hash
    if ($r.canonical_sha256_after -ne $canonicalHash) { throw 'Canonical compiler changed unexpectedly' }
    $r.status='PASS'
} catch { $r.status='FAIL'; $r.error=$_.Exception.Message; throw }
finally { [IO.File]::WriteAllText((Join-Path $OutDir 'cleanup.json'),($r | ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false)) }
$r | ConvertTo-Json -Depth 8

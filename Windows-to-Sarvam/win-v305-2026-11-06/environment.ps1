param([ValidateSet('Before','After')][string]$Phase='Before')
$ErrorActionPreference='Stop'
$out=$PSScriptRoot
$record=[ordered]@{phase=$Phase;time=[DateTime]::Now.ToString('o');machine_path=[Environment]::GetEnvironmentVariable('Path','Machine');user_path=[Environment]::GetEnvironmentVariable('Path','User');inherited_process_path=$env:PATH}
$env:PATH=[Environment]::ExpandEnvironmentVariables($record.machine_path+';'+$record.user_path)
$record.fresh_process_path=$env:PATH
function Invoke-Captured([string]$File,[string]$Arguments) {
    $p=New-Object Diagnostics.Process
    $p.StartInfo.FileName=$File; $p.StartInfo.Arguments=$Arguments
    $p.StartInfo.WorkingDirectory=$out
    $p.StartInfo.UseShellExecute=$false; $p.StartInfo.CreateNoWindow=$true
    $p.StartInfo.RedirectStandardOutput=$true; $p.StartInfo.RedirectStandardError=$true
    [void]$p.Start()
    $o=$p.StandardOutput.ReadToEndAsync(); $e=$p.StandardError.ReadToEndAsync()
    $timedOut=-not $p.WaitForExit(30000)
    if ($timedOut) { $p.Kill(); [void]$p.WaitForExit(3000) }
    $r=[ordered]@{file=$File;arguments=$Arguments;stdout=$o.Result;stderr=$e.Result;exit=$p.ExitCode;timed_out=$timedOut}
    $p.Dispose(); return $r
}
$record.where=Invoke-Captured $env:ComSpec '/d /c where sutram'
$record.version=Invoke-Captured $env:ComSpec '/d /c sutram --version'
$record.echo_path=Invoke-Captured $env:ComSpec '/d /c echo %PATH%'
$record.reg_machine=Invoke-Captured 'reg.exe' 'query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path'
$record.reg_user=Invoke-Captured 'reg.exe' 'query "HKCU\Environment" /v Path'
$record.executables=@()
foreach ($line in ($record.where.stdout -split '\r?\n')) {
    $path=$line.Trim()
    if ($path -and (Test-Path -LiteralPath $path -PathType Leaf)) {
        $record.executables += [ordered]@{path=$path;sha256=(Get-FileHash -LiteralPath $path).Hash;version=(Invoke-Captured $path '--version')}
    }
}
$record.old_folder_exists=Test-Path -LiteralPath 'C:\Users\dmech\AppData\Local\Sutram'
[IO.File]::WriteAllText((Join-Path $out ('environment-'+$Phase.ToLower()+'.json')),($record | ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))
$record.executables | ConvertTo-Json -Depth 5
if ($Phase -eq 'After' -and ($record.executables.Count -ne 1 -or $record.old_folder_exists)) { throw 'Cleanup gate failed: expected one executable and no old install folder' }

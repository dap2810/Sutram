# R161 (Sarvam R161 WS4): run this BEFORE and AFTER each installer case on Tuesday. It changes nothing: it reads.
#   1  both engine scripts parse with zero errors (the installer's PowerShell has not run since R154; a syntax error
#      would stop the install at its first line, and this finds it without installing anything)
#   2  it writes what the registry and PATH hold now, so a case's before and after can be compared byte for byte:
#      HKCU\Software\Classes\.sm (its default: absent, empty or a value; every value and subkey under it),
#      HKCU\Software\Classes\Sutram.Source (the same), HKCU\Environment Path (exact text and kind, REG_SZ or
#      REG_EXPAND_SZ, or absent), the Uninstall\Sutram entry, and the shortcuts in the Start-menu Sutram folder and
#      on the desktop with their SHA-256
# Written in the Linux container, where PowerShell could not be run: NOT RUN by its author.
#   powershell -NoProfile -ExecutionPolicy Bypass -File tests\windows\preflight_installer_state.ps1 -Label before-case1
param([string]$Label = 'snapshot')
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$out = [ordered]@{ label = $Label; time = (Get-Date).ToString('o') }
$parse = [ordered]@{}
foreach ($f in @('install-core.ps1', 'uninstall-core.ps1')) {
    $t = $null; $e = $null
    [void][Management.Automation.Language.Parser]::ParseFile((Join-Path $root ('windows\native-installer\' + $f)), [ref]$t, [ref]$e)
    $parse[$f] = @($e | ForEach-Object { $_.Extent.StartLineNumber.ToString() + ': ' + $_.Message })
}
$out.parse_errors = $parse
function Read-Tree([string]$Sub) {
    $k = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey($Sub, $false)
    if (-not $k) { return $null }
    try {
        $vals = [ordered]@{}
        foreach ($n in $k.GetValueNames()) {
            $name = $n; if ($n -eq '') { $name = '(default)' }
            $vals[$name] = [ordered]@{ kind = $k.GetValueKind($n).ToString(); text = [string]$k.GetValue($n, $null, [Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames) }
        }
        $subs = [ordered]@{}
        foreach ($s in $k.GetSubKeyNames()) { $subs[$s] = Read-Tree ($Sub + '\' + $s) }
        return [ordered]@{ values = $vals; subkeys = $subs }
    } finally { $k.Dispose() }
}
$out.sm = Read-Tree 'Software\Classes\.sm'
$out.sutram_source = Read-Tree 'Software\Classes\Sutram.Source'
$out.uninstall_entry = Read-Tree 'Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram'
$envKey = Read-Tree 'Environment'
$out.path = $null
if ($envKey -and $envKey.values.Contains('Path')) { $out.path = $envKey.values['Path'] }
$links = [ordered]@{}
$dirs = @([Environment]::GetFolderPath('Desktop'), (Join-Path ([Environment]::GetFolderPath('Programs')) 'Sutram'))
foreach ($d in $dirs) {
    if (Test-Path -LiteralPath $d -PathType Container) {
        foreach ($l in Get-ChildItem -LiteralPath $d -Filter '*.lnk' -Force) { $links[$l.FullName] = (Get-FileHash -LiteralPath $l.FullName -Algorithm SHA256).Hash }
    }
}
$out.shortcuts = $links
$dir = Join-Path $root 'build\installer-preflight'
[void][IO.Directory]::CreateDirectory($dir)
$file = Join-Path $dir ($Label + '.json')
[IO.File]::WriteAllText($file, ($out | ConvertTo-Json -Depth 12), [Text.UTF8Encoding]::new($false))
$bad = @($parse.Values | Where-Object { $_.Count -gt 0 })
if ($bad.Count) { Write-Output ('FAIL  the engine does not parse: ' + (($parse.GetEnumerator() | ForEach-Object { $_.Key + ' ' + ($_.Value -join '; ') }) -join ' | ')) }
else { Write-Output 'PASS  install-core.ps1 and uninstall-core.ps1 parse with no errors' }
Write-Output ('Written: ' + $file)
if ($bad.Count) { exit 1 }

. (Join-Path $PSScriptRoot 'build-common.ps1')
if (-not [Environment]::Is64BitProcess) { throw 'Use 64-bit Windows PowerShell.' }
$manifest = Join-Path $PSScriptRoot 'windows-build-integrity.sha256'
$seen = @{}
foreach ($line in [IO.File]::ReadAllLines($manifest)) {
    if ($line -notmatch '^([0-9a-f]{64}) \*(.+)$') { throw "Malformed source manifest: $line" }
    $hash=$Matches[1]; $rel=$Matches[2]
    if ([IO.Path]::IsPathRooted($rel) -or ($rel -split '[\\/]') -contains '..') { throw "Unsafe source path: $rel" }
    $full=[IO.Path]::GetFullPath((Join-Path $ProjectRoot $rel))
    if (-not $full.StartsWith($ProjectRoot+'\',[StringComparison]::OrdinalIgnoreCase)) { throw "Source path escapes project: $rel" }
    if ($seen.ContainsKey($rel)) { throw "Duplicate source path: $rel" }
    $seen[$rel]=$true
    if (-not (Test-Path -LiteralPath $full -PathType Leaf)) { throw "Missing source: $rel" }
    if ((Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash.ToLowerInvariant() -ne $hash) { throw "Source integrity mismatch: $rel" }
}
# Every file used from recursive payload/source trees must be covered.
foreach ($directory in @('src','lib','lang','examples','docs','icons','windows')) {
    foreach ($file in Get-ChildItem -LiteralPath (Join-Path $ProjectRoot $directory) -File -Recurse) {
        if ($file.FullName -eq $manifest -or $file.FullName -match '[\\/]__pycache__[\\/]') { continue }
        $rel=$file.FullName.Substring($ProjectRoot.Length+1).Replace('\','/')
        if (-not $seen.ContainsKey($rel)) { throw "Unmanifested build/payload input: $rel" }
    }
}
foreach ($rel in @('src/sutram_compiler.asm','src/r68_compiler_entry.asm','win/winrt.inc','win/rtblob.inc',
    'win/winrt_blob.asm','win/pe_layout.inc','win/pe_imports.inc','windows/build-common.ps1',
    'windows/preflight-windows.ps1','windows/build-windows-setup.ps1','windows/build-windows-native.ps1',
    'windows/gui/build-gui.ps1','windows/gui/sutram_gui.asm','windows/gui/r67_gui_entry.asm',
    'windows/gui/r66_indic_clusters.asm','windows/gui/r67_cluster_count.asm',
    'windows/native-installer/sutram_wizard.asm','windows/native-installer/build-installer.ps1',
    'windows/native-installer/install-core.ps1','windows/native-installer/uninstall-core.ps1','icons/sutram.ico')) {
    if (-not $seen.ContainsKey($rel)) { throw "Required input absent from source manifest: $rel" }
}
foreach ($rel in @('windows/build-windows-setup.ps1','windows/build-windows-native.ps1',
    'windows/native-installer/build-installer.ps1','windows/native-installer/sutram_wizard.asm',
    'windows/native-installer/install-core.ps1','windows/native-installer/uninstall-core.ps1')) {
    $text = [IO.File]::ReadAllText((Join-Path $ProjectRoot $rel))
    foreach ($bad in @('ExecutionPolicy Bypass','HKLM:', '::LocalMachine','MachinePathEntry','-Verb RunAs','RelaunchElevated')) {
        if ($text.IndexOf($bad,[StringComparison]::OrdinalIgnoreCase) -ge 0) { throw "Forbidden active build/install behavior in ${rel}: $bad" }
    }
}
[void](Get-BuildTool 'nasm.exe')
[void](Get-BuildTool 'ld.exe')
Write-Host ("PREFLIGHT PASS: {0} source hashes; native NASM toolchain; per-user install sources." -f $seen.Count)

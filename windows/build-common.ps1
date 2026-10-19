[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
function Invoke-BoundedProcess([string]$Exe,[string[]]$Arguments,[string]$WorkingDir,[int]$Timeout=20000) {
    $p = New-Object Diagnostics.Process
    $p.StartInfo.FileName = $Exe
    $quoted = foreach ($arg in $Arguments) {
        if ($arg.Contains('"')) { throw 'Embedded quotes are not valid build arguments.' }
        '"' + $arg + '"'
    }
    $p.StartInfo.Arguments = $quoted -join ' '
    $p.StartInfo.WorkingDirectory = $WorkingDir
    $p.StartInfo.UseShellExecute = $false
    $p.StartInfo.CreateNoWindow = $true
    $p.StartInfo.RedirectStandardOutput = $true
    $p.StartInfo.RedirectStandardError = $true
    $p.StartInfo.StandardOutputEncoding = [Text.Encoding]::UTF8
    $p.StartInfo.StandardErrorEncoding = [Text.Encoding]::UTF8
    try {
        if (-not $p.Start()) { throw "Could not start $Exe" }
        $stdout = $p.StandardOutput.ReadToEndAsync()
        $stderr = $p.StandardError.ReadToEndAsync()
        if (-not $p.WaitForExit($Timeout)) { $p.Kill(); $p.WaitForExit(); throw "Timed out: $Exe" }
        $result = [pscustomobject]@{ Code=$p.ExitCode; Stdout=$stdout.Result; Stderr=$stderr.Result }
        Write-Host ($Exe + ' ' + ($Arguments -join ' '))
        if ($result.Stdout) { Write-Host $result.Stdout.TrimEnd() }
        if ($result.Stderr) { Write-Host $result.Stderr.TrimEnd() }
        if ($result.Code -ne 0) { throw "$Exe failed: exit $($result.Code)" }
        return $result
    } finally { $p.Dispose() }
}
function Assert-Pe64([string]$Path) {
    $b = [IO.File]::ReadAllBytes($Path)
    if ($b.Length -lt 512 -or $b[0] -ne 77 -or $b[1] -ne 90) { throw "Not an MZ executable: $Path" }
    $pe = [BitConverter]::ToInt32($b,60)
    if ($pe -lt 64 -or $pe + 264 -gt $b.Length -or [BitConverter]::ToUInt32($b,$pe) -ne 17744 -or
        [BitConverter]::ToUInt16($b,$pe+4) -ne 34404 -or [BitConverter]::ToUInt16($b,$pe+24) -ne 523) {
        throw "Not a PE32+ AMD64 executable: $Path"
    }
    $sections = [BitConverter]::ToUInt16($b,$pe+6)
    $table = $pe+24+[BitConverter]::ToUInt16($b,$pe+20)
    for ($i=0; $i -lt $sections; $i++) {
        $off = $table+40*$i
        if ($off+40 -gt $b.Length) { throw 'Truncated section table.' }
        $flags = [BitConverter]::ToUInt32($b,$off+36)
        if (($flags -band 0x20000000) -and ($flags -band 2147483648)) { throw 'Writable executable section rejected.' }
    }
}
function Get-BuildTool([string]$Name) {
    $tool = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $tool) { throw "Missing developer build tool: $Name. No tools are installed automatically." }
    return $tool.Source
}
# R73: emit a NASM .rsrc directory (RT_GROUP_ICON 1 + RT_ICON 1..N) from an .ico file.
# Each image is an incbin slice of the icon, so the executable shows the canonical icon
# in Explorer, the taskbar and its title bar without a resource compiler or C.
function Write-IconResourceInclude([string]$IcoPath,[string]$OutPath,[string]$IncbinPath) {
    $ico=[IO.File]::ReadAllBytes($IcoPath)
    if ($ico.Length -lt 6 -or [BitConverter]::ToUInt16($ico,0) -ne 0 -or [BitConverter]::ToUInt16($ico,2) -ne 1) { throw "Not an ICO file: $IcoPath" }
    $count=[BitConverter]::ToUInt16($ico,4)
    if ($count -lt 1 -or $count -gt 32) { throw "Unexpected icon image count: $count" }
    $inc=New-Object Collections.Generic.List[string]
    $inc.Add("; generated from $IncbinPath by windows/build-common.ps1; do not edit")
    $inc.Add('section .rsrc rdata align=8')
    $inc.Add('rsrc_root:')
    $inc.Add('    dd 0,0')
    $inc.Add('    dw 0,0,0,2')
    $inc.Add('    dd 3,(rsrc_icons-rsrc_root)|0x80000000')
    $inc.Add('    dd 14,(rsrc_group-rsrc_root)|0x80000000')
    $inc.Add('rsrc_icons:')
    $inc.Add('    dd 0,0')
    $inc.Add("    dw 0,0,0,$count")
    for ($i=1;$i -le $count;$i++) { $inc.Add("    dd $i,(rsrc_icon_lang_$i-rsrc_root)|0x80000000") }
    for ($i=1;$i -le $count;$i++) {
        $inc.Add("rsrc_icon_lang_${i}:")
        $inc.Add('    dd 0,0')
        $inc.Add('    dw 0,0,0,1')
        $inc.Add("    dd 0x0409,(rsrc_icon_data_$i-rsrc_root)")
    }
    $inc.Add('rsrc_group:')
    $inc.Add('    dd 0,0')
    $inc.Add('    dw 0,0,0,1')
    $inc.Add('    dd 1,(rsrc_group_lang-rsrc_root)|0x80000000')
    $inc.Add('rsrc_group_lang:')
    $inc.Add('    dd 0,0')
    $inc.Add('    dw 0,0,0,1')
    $inc.Add('    dd 0x0409,(rsrc_group_data-rsrc_root)')
    for ($i=1;$i -le $count;$i++) {
        $e=6+16*($i-1)
        $size=[BitConverter]::ToUInt32($ico,$e+8)
        $inc.Add("rsrc_icon_data_${i}:")
        $inc.Add("    dd rsrc_icon_bytes_$i wrt ..imagebase,$size,0,0")
    }
    $inc.Add('rsrc_group_data:')
    $inc.Add('    dd rsrc_group_bytes wrt ..imagebase,rsrc_group_end-rsrc_group_bytes,0,0')
    $inc.Add('rsrc_group_bytes:')
    $inc.Add("    dw 0,1,$count")
    for ($i=1;$i -le $count;$i++) {
        $e=6+16*($i-1)
        $w=$ico[$e]; $h=$ico[$e+1]; $colors=$ico[$e+2]
        $planes=[BitConverter]::ToUInt16($ico,$e+4); $bpp=[BitConverter]::ToUInt16($ico,$e+6)
        $size=[BitConverter]::ToUInt32($ico,$e+8)
        $inc.Add("    db $w,$h,$colors,0")
        $inc.Add("    dw $planes,$bpp")
        $inc.Add("    dd $size")
        $inc.Add("    dw $i")
    }
    $inc.Add('rsrc_group_end:')
    for ($i=1;$i -le $count;$i++) {
        $e=6+16*($i-1)
        $size=[BitConverter]::ToUInt32($ico,$e+8); $off=[BitConverter]::ToUInt32($ico,$e+12)
        if ([uint64]$off+[uint64]$size -gt [uint64]$ico.Length) { throw "Icon entry $i exceeds the file" }
        $inc.Add('    align 8')
        $inc.Add("rsrc_icon_bytes_${i}:")
        $inc.Add("    incbin `"$IncbinPath`",$off,$size")
    }
    [IO.File]::WriteAllLines($OutPath,[string[]]$inc,([Text.UTF8Encoding]::new($false)))
}
function Assert-PeResourceDirectory([string]$Path) {
    $b=[IO.File]::ReadAllBytes($Path); $pe=[BitConverter]::ToInt32($b,60)
    $rva=[BitConverter]::ToUInt32($b,$pe+24+112+16); $size=[BitConverter]::ToUInt32($b,$pe+24+112+20)
    if ($rva -eq 0 -or $size -lt 64) { throw "No resource directory in $Path; the icon resource was not linked." }
    return "resource directory RVA $rva, $size bytes"
}

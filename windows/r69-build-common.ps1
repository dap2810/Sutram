# R69 developer build helpers. No elevation, tool installation, registry or policy changes.
Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

function Assert-R69StandardUser {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    if ($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw 'Run the Sutram build in a standard-user, non-elevated PowerShell session.'
    }
}

function Assert-R69RegularPath([string]$Root, [string]$Relative) {
    if ($Relative -notmatch '^[A-Za-z0-9_./-]+$' -or $Relative.StartsWith('/') -or
        ($Relative.Split('/') | Where-Object { $_ -eq '..' -or $_ -eq '.' -or $_ -eq '' })) {
        throw "Unsafe locked path: $Relative"
    }
    $current = $Root
    foreach ($part in $Relative.Split('/')) {
        $current = Join-Path $current $part
        $item = Get-Item -LiteralPath $current -Force
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "Reparse-point input refused: $Relative"
        }
    }
    if (-not (Test-Path -LiteralPath $current -PathType Leaf)) { throw "Missing input: $Relative" }
    return $current
}

function Get-R69GitBlob([string]$Path) {
    $data = [IO.File]::ReadAllBytes($Path)
    $header = [Text.Encoding]::ASCII.GetBytes('blob ' + $data.Length + [char]0)
    $joined = New-Object byte[] ($header.Length + $data.Length)
    [Buffer]::BlockCopy($header, 0, $joined, 0, $header.Length)
    [Buffer]::BlockCopy($data, 0, $joined, $header.Length, $data.Length)
    $hash = [Security.Cryptography.SHA1]::Create()
    try { return [BitConverter]::ToString($hash.ComputeHash($joined)).Replace('-', '').ToLowerInvariant() }
    finally { $hash.Dispose() }
}

function Assert-R69SourcePins([string]$Root) {
    $lockPath = Assert-R69RegularPath $Root 'tools/r69_build.lock.json'
    $lock = [IO.File]::ReadAllText($lockPath, [Text.Encoding]::UTF8) | ConvertFrom-Json
    if ($lock.schema -ne 1 -or $lock.entry -ne 'src/r68_compiler_entry.asm' -or
        $lock.pins.'src/sutram_compiler.asm' -ne '64ea028a5ccf56117c132a7efd0673cbe2df3fc6' -or
        $lock.pins.'src/r68_compiler_entry.asm' -ne '42389aaf73179726d91e23359aee2199734036e1') {
        throw 'Unknown compiler/entry contract. Review source drift; do not bypass the lock.'
    }
    foreach ($pin in $lock.pins.PSObject.Properties) {
        if ($pin.Value -notmatch '^[0-9a-f]{40}$') { throw "Invalid pin: $($pin.Name)" }
        $path = Assert-R69RegularPath $Root $pin.Name
        $actual = Get-R69GitBlob $path
        if ($actual -ne $pin.Value) { throw "Source drift: $($pin.Name): expected $($pin.Value), got $actual" }
        $text = [IO.File]::ReadAllText($path, [Text.Encoding]::UTF8)
        foreach ($include in [regex]::Matches($text, '(?m)^\s*%(?:include|incbin)\s+"([^"]+)"')) {
            if (-not $lock.pins.PSObject.Properties[$include.Groups[1].Value]) {
                throw "Unpinned include in $($pin.Name): $($include.Groups[1].Value)"
            }
        }
    }
}

function ConvertTo-R69Argument([string]$Value) {
    # Windows command-line quoting, including trailing backslashes and embedded quotes.
    $builder = New-Object Text.StringBuilder
    [void]$builder.Append('"')
    $slashes = 0
    foreach ($character in $Value.ToCharArray()) {
        if ($character -eq [char]92) { $slashes++; continue }
        if ($character -eq [char]34) {
            [void]$builder.Append([char]92, 2 * $slashes + 1)
            [void]$builder.Append([char]34)
        } else {
            if ($slashes) { [void]$builder.Append([char]92, $slashes) }
            [void]$builder.Append($character)
        }
        $slashes = 0
    }
    if ($slashes) { [void]$builder.Append([char]92, 2 * $slashes) }
    [void]$builder.Append('"')
    return $builder.ToString()
}

function Invoke-R69Process {
    param([string]$FilePath, [string[]]$Arguments, [string]$WorkingDirectory,
          [int]$TimeoutSeconds = 120, [int]$ExpectedExit = 0)
    if ($TimeoutSeconds -lt 1 -or $TimeoutSeconds -gt 1800) { throw 'Invalid timeout.' }
    $info = New-Object Diagnostics.ProcessStartInfo
    $info.FileName = $FilePath
    $info.Arguments = (($Arguments | ForEach-Object { ConvertTo-R69Argument $_ }) -join ' ')
    $info.WorkingDirectory = $WorkingDirectory
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $info.RedirectStandardInput = $true
    $info.StandardOutputEncoding = New-Object Text.UTF8Encoding($false)
    $info.StandardErrorEncoding = New-Object Text.UTF8Encoding($false)
    foreach ($key in @($info.EnvironmentVariables.Keys)) {
        if ($key -like 'SUTRAM_*') { $info.EnvironmentVariables.Remove($key) }
    }
    $process = New-Object Diagnostics.Process
    $process.StartInfo = $info
    try {
        if (-not $process.Start()) { throw "Could not start $FilePath" }
        $process.StandardInput.Close()
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
            try { $process.Kill(); [void]$process.WaitForExit(5000) } catch { }
            throw "Timed out: $FilePath. Inspect descendant processes before retrying; none are assumed cleaned up."
        }
        if (-not $stdout.Wait(5000) -or -not $stderr.Wait(5000)) {
            throw 'A child still holds the output stream; inspect descendants before retrying.'
        }
        $result = [pscustomobject]@{ ExitCode = $process.ExitCode;
            Stdout = $stdout.GetAwaiter().GetResult(); Stderr = $stderr.GetAwaiter().GetResult() }
        if ($result.ExitCode -ne $ExpectedExit) {
            throw "Unexpected exit $($result.ExitCode), expected $ExpectedExit from $FilePath`n$($result.Stdout)`n$($result.Stderr)"
        }
        return $result
    } finally { $process.Dispose() }
}

function Assert-R69Pe64([string]$Path) {
    $data = [IO.File]::ReadAllBytes($Path)
    if ($data.Length -lt 64 -or $data[0] -ne 0x4d -or $data[1] -ne 0x5a) { throw "Missing MZ: $Path" }
    $pe = [BitConverter]::ToUInt32($data, 0x3c)
    if ($pe -lt 64 -or [uint64]$pe + 26 -gt [uint64]$data.Length -or
        $data[$pe] -ne 0x50 -or $data[$pe+1] -ne 0x45 -or
        $data[$pe+2] -ne 0 -or $data[$pe+3] -ne 0 -or
        [BitConverter]::ToUInt16($data, $pe+4) -ne 0x8664 -or
        [BitConverter]::ToUInt16($data, $pe+24) -ne 0x20b) { throw "Invalid PE32+ AMD64: $Path" }
}

function Publish-R69Artifact([string]$Candidate, [string]$Destination, [bool]$Replace) {
    $parent = Split-Path -Parent $Destination
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) { throw "Missing output parent: $parent" }
    # Get-Item also catches dangling reparse points rather than treating them as fresh outputs.
    $old = Get-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue
    if ($old -and ((($old.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) -or $old.PSIsContainer -or -not $Replace)) {
        throw "Existing/nonregular output refused: $Destination. Use -ReplaceOutput only for known build artifacts."
    }
    $staged = Join-Path $parent ('.r69-' + [guid]::NewGuid().ToString('N') + '.tmp')
    try {
        [IO.File]::Copy($Candidate, $staged, $false)
        if (Test-Path -LiteralPath $Destination -PathType Leaf) {
            if (-not $Replace) { throw 'Output appeared during publication.' }
            [IO.File]::Replace($staged, $Destination, $null)
        } else { [IO.File]::Move($staged, $Destination) }
        if ((Get-FileHash -LiteralPath $Candidate -Algorithm SHA256).Hash -ne
            (Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash) { throw 'Published hash mismatch.' }
    } finally { if (Test-Path -LiteralPath $staged) { Remove-Item -LiteralPath $staged -Force } }
}

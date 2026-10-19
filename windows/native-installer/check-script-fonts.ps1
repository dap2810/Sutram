<#
  R9 (WS7): does this Windows have a font for each script of Sutram's eleven
  language packs (nine scripts: Devanagari serves sanskrit, hindi and marathi)?

  The installer does not install fonts: Windows 10 and 11 ship Nirmala UI, which
  covers all of them. This only CHECKS, so a user is told before they see empty
  boxes where the letters should be. It never fails an install.

  Written by Claude for ChatGPT's installer (the installer is ChatGPT's code, so
  this is a separate file to call, not an edit of install-core.ps1). Suggested use
  in install-core.ps1, after the payload is verified:

      . (Join-Path $PSScriptRoot 'check-script-fonts.ps1')
      $fonts = Test-SutramScriptFonts
      Log ('Script fonts: ' + $fonts.Summary)
      # and show $fonts.Message on the wizard's last page when $fonts.AllCovered is false

  Run it alone:  powershell -NoProfile -File check-script-fonts.ps1
  It prints one line per script and exits 0 (all covered) or 3 (something missing).
#>
Set-StrictMode -Version 2.0

function Get-SutramInstalledFontNames {
    # Font names Windows has registered, machine-wide and (Windows 10 1809+) per user.
    $names = New-Object System.Collections.Generic.List[string]
    foreach ($key in @('HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts',
                       'HKCU:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts')) {
        if (Test-Path -LiteralPath $key) {
            $item = Get-ItemProperty -LiteralPath $key
            foreach ($p in $item.PSObject.Properties) {
                if ($p.Name -notlike 'PS*') { $names.Add([string]$p.Name) }
            }
        }
    }
    return $names
}

function Test-SutramScriptFonts {
    # For each script: the Nirmala UI face covers it; older Windows had one font per script.
    $scripts = @(
        @{ Script = 'Devanagari (sanskrit, hindi, marathi)'; Fonts = @('Nirmala UI', 'Mangal', 'Aparajita', 'Kokila', 'Utsaah') },
        @{ Script = 'Bengali';   Fonts = @('Nirmala UI', 'Vrinda', 'Shonar Bangla') },
        @{ Script = 'Gujarati';  Fonts = @('Nirmala UI', 'Shruti') },
        @{ Script = 'Gurmukhi (punjabi)'; Fonts = @('Nirmala UI', 'Raavi') },
        @{ Script = 'Odia';      Fonts = @('Nirmala UI', 'Kalinga') },
        @{ Script = 'Tamil';     Fonts = @('Nirmala UI', 'Latha', 'Vijaya') },
        @{ Script = 'Telugu';    Fonts = @('Nirmala UI', 'Gautami', 'Vani') },
        @{ Script = 'Kannada';   Fonts = @('Nirmala UI', 'Tunga') },
        @{ Script = 'Malayalam'; Fonts = @('Nirmala UI', 'Kartika') }
    )
    $installed = Get-SutramInstalledFontNames
    $rows = @()
    foreach ($s in $scripts) {
        $found = $null
        foreach ($f in $s.Fonts) {
            # registry names look like "Nirmala UI (TrueType)" or "Nirmala UI & Nirmala UI Semilight (TrueType)"
            if (@($installed | Where-Object { $_ -match ('(^|& )' + [regex]::Escape($f) + '( |$)') }).Count -gt 0) { $found = $f; break }
        }
        $rows += [pscustomobject]@{ Script = $s.Script; Font = $found; Covered = ($null -ne $found) }
    }
    $missing = @($rows | Where-Object { -not $_.Covered })
    $nirmala = @($rows | Where-Object { $_.Font -eq 'Nirmala UI' }).Count -eq $rows.Count
    $summary = ($rows | ForEach-Object { $_.Script + '=' + $(if ($_.Covered) { $_.Font } else { 'MISSING' }) }) -join '; '
    if ($missing.Count -eq 0) {
        $msg = if ($nirmala) { 'All nine scripts of Sutram''s eleven language packs are covered by Nirmala UI.' } else { 'All nine scripts of Sutram''s eleven language packs have a font.' }
    } else {
        $msg = 'No font was found for: ' + (($missing | ForEach-Object { $_.Script }) -join ', ') +
               '. Programs in those scripts will show empty boxes. Windows 10 and 11 include Nirmala UI; on other systems add a font for these scripts (Settings > Personalization > Fonts, or an optional language feature).'
    }
    return [pscustomobject]@{ AllCovered = ($missing.Count -eq 0); NirmalaUI = $nirmala; Rows = $rows; Summary = $summary; Message = $msg }
}

if ($MyInvocation.InvocationName -ne '.') {
    $r = Test-SutramScriptFonts
    foreach ($row in $r.Rows) {
        '{0,-40} {1}' -f $row.Script, $(if ($row.Covered) { $row.Font } else { 'MISSING' })
    }
    $r.Message
    if ($r.AllCovered) { exit 0 } else { exit 3 }
}

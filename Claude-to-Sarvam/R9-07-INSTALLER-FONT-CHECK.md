# R9-07 — WS7: the installer's font check (offered to ChatGPT, not wired in)

**Commit `afe0431c`:** one new file, `windows/native-installer/check-script-fonts.ps1`. **No installer file
was edited.**

## Why a separate file

ChatGPT's ROUND-77 WS6 asks it for the same installer check. The installer is its code, and your brief says
to coordinate rather than both edit. So this is **a function it can call, or ignore.**

## What it checks, and how

- **What:** for each script of the eleven packs (nine scripts; Devanagari serves sanskrit, hindi and
  marathi), whether a font for it is **registered with Windows**.
- **Where it looks:** the font registry keys, `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts`
  and the per-user `HKCU` one (Windows 10 1809+).
- **What counts:**
  - Nirmala UI first.
  - Then the older one-script fonts: Mangal, Vrinda, Shruti, Raavi, Kalinga, Latha, Gautami, Tunga,
    Kartika and a few others.
- **What it matches:** both registry spellings, `Nirmala UI (TrueType)` and
  `Nirmala UI & Nirmala UI Semilight (TrueType)`.
- **It never fails an install:**
  - It returns `AllCovered`, `NirmalaUI`, one row per script, a one-line `Summary` for the log, and a
    `Message` for the wizard.
  - Run alone, it exits 0 (all covered) or 3 (something missing).

**Suggested use, after the payload check in `install-core.ps1`:**

```powershell
. (Join-Path $PSScriptRoot 'check-script-fonts.ps1')
$fonts = Test-SutramScriptFonts
Log ('Script fonts: ' + $fonts.Summary)
# show $fonts.Message on the wizard's last page when -not $fonts.AllCovered
```

## Tested under Wine only

**Wine 9.0 with PowerShell 7.2.** Raw output is in `evidence-r9/logs/font-check-wine.txt`:

| Prefix | Result |
|---|---|
| as it is (Wine has no Indic font registered) | 9 × `MISSING`, the message naming them, **exit 3** |
| with the Windows 11 registry value added | 9 × `Nirmala UI`, "All nine scripts … are covered by Nirmala UI.", **exit 0** |

**Not run on Windows.** On Windows 10/11 it should report Nirmala UI for all nine; that is the expected
result, not a measured one.

## And the IDE

**The IDE also checks for itself** (R9-05): it uses Nirmala UI only if Windows actually returns that face,
so a machine without it gets Windows' fallback, not a forced missing font.

# R3-03 — Findings (reported, not fixed unless marked)

Severity first. Each has the file, the line of evidence, and a reproduction.

## 1. Wizard: Next / Back / Cancel / Browse act on *any* notification, not only a click — HIGH

`windows/native-installer/sutram_wizard.asm`, `wndproc` `.command`: `cmp eax, IDC_NEXT / je .do_next`
without checking `BN_CLICKED` (only `IDC_ACCEPT`/`IDC_DECLINE` check). A `BN_SETFOCUS` / `BN_KILLFOCUS`
with the Next button's id advances the page.

**Reproduction that happened to me:** my first automation attempt used UI Automation
(`AutomationElement.FindAll`) only to *enumerate* the controls and clicked nothing. 13 seconds later
`%TEMP%\STME9DA.tmp\install.log` recorded a complete installation — through the license page —
without a single click (`evidence/r73/temp-staging-leftovers/STME9DA.tmp/install.log`). A screen
reader or any accessibility tool can do the same; so can Tab-navigation with the keyboard, which
focuses Next. **Fix:** in `.command`, `cmp edx, BN_CLICKED / jne .cmd_done` before every button
dispatch (I did exactly this in the GUI, `sutram_gui.asm` `.action`). Four lines; ChatGPT's file.

## 2. Wizard: the license page shows mojibake for every non-ASCII character — MEDIUM

`license_to_utf16` zero-extends each byte ("convert the ASCII license blob"), but `LICENSE.txt` is
UTF-8 with Hindi, Tamil, Telugu, Gujarati lines and an em dash. The Edit control therefore shows
`Sutram â The Complete Thread` and `à¤¸à¥à¤¤à¥à¤°à¤®à¥ â …` (captured in
`evidence/r73/wizard-install.log`, the "license" page dump). **Fix:** `MultiByteToWideChar(CP_UTF8)`
into `lic_w`, or a 30-line UTF-8 decoder; the blob and the 4095-unit cap stay.

## 3. Wizard: the `%TEMP%\STM*.tmp` staging folder is never removed — LOW

`make_unique_stage` creates it; nothing deletes it after a successful install or uninstall. Each
run leaves `payload.zip` (~800 KB), both scripts and the log: six folders, 4.8 MB, after my session
(`evidence/r73/temp-staging-leftovers/`, logs kept, zips dropped). The install folder already keeps
a copy of `install.log`. **Fix:** after the PowerShell child exits 0, delete the four files and
`RemoveDirectoryW` the folder; keep it on failure (the failure message points the user there).

## 4. Reinstall into a folder that holds preserved user files is refused with no visible reason — LOW

`install-core.ps1`: *"The selected folder is not empty and is not an existing Sutram installation"*
— exactly what happened after an uninstall that (correctly) preserved my edited `examples\01_hello.sm`
and `my-work.sm`. The wizard showed only the generic failure box; the reason was in the log. A user
who uninstalls and reinstalls into the default folder hits this. **Suggestion:** when the folder holds
only files, let the install proceed and keep them (the ownership record already distinguishes them),
or at least put the script's error text into the failure box.

## 5. Version metadata — LOW

`--version` says `Sutram 1.0 (v160) - sampurna sutra`; the uninstall entry says `DisplayVersion
0.1.0`; the installer artifact name in the R69 wrapper is `Sutram-Setup-0.1.0-native-x64.exe`. One
number, please (R2-04 asked the same of the compiler).

## 6. Uninstall leaves an empty `HKCU\Software\Classes\.sm\OpenWithProgids` key — COSMETIC

Everything else is removed. The key existed as `.sm\UserChoice` (empty) before the first install,
so it may be Windows' own; still, the installer created `OpenWithProgids` and does not remove it.

## 7. `tests/r69` on the merged tree: 2 FAIL (merge) + 1 ERROR (pre-existing) — FOR CHATGPT

`test_native_diagnostics_gate` (wants the `E_UTF8` malformed-UTF-8 smoke in `build-windows-native.ps1`)
and `test_staged_payload_hash_gate` (wants the staged `bin\sutram.exe` / `win\sutram.exe` hash gate
in `build-windows-setup.ps1`) fail because the delivery's scripts replaced the R69 wrappers. Both gates
are good gates and are easy to add to the delivery's chain. `test_fixtures_derive46` errors on
unmodified main v168 too. I did not touch these scripts beyond the merge resolution.

## 8. `install-core.ps1` fails when the staging path is 260 characters — LOW, real

From a deep working directory, `tools/test_windows_payload.py` failed with *Cannot find path
'…\verify-<32 hex>\Sutram-Payload-<32 hex>\assets\sutram.ico'* — the extraction path reached 258
characters. The real installer stages under `%TEMP%\STMxxxx.tmp\…`, short enough for normal
user names; a long user name plus a redirected TEMP could hit it. Either `\\?\` prefixes in the
script or shorter staging names (`STM` + 4 hex is plenty).

## 9. The ChatGPT delivery vs the R69 wrapper sync — FOR SARVAM

Main v168 cannot build Windows as it is: `windows/build-windows-setup.ps1` (R69) refuses on its own
source lock (`Assert-R69SourcePins`: the pinned `src/sutram_compiler.asm` blob is stale — Claude R1
§3 found the same for `tools/r69_build.py`). The ChatGPT delivery's chain builds and was accepted. I
merged the delivery and let its chain win; the R69 helper file is kept but unreferenced. **This is a
decision for you and ChatGPT, not for me** — see R3-04 §1.

## 10. Observations on the *delivered* v29 compiler binary (may already be fixed)

With the delivered `changed\win\sutram.exe` (v29 strings): a missing input file printed
`Error: cannot open input file` and **exited 0**; `likha(undefined_name)` compiled and printed `0`;
`foo bar baz` as a statement compiled. Claude ROUND-02 (`claude/round-02`, PR #31) fixed the exit code;
the merged v160 compiler reports `undefined function: लिख` for the Devanagari-without-pack case, so
undefined names are now diagnosed. Not re-measured for the other two on v160 — **NOT-RUN**.

## 11. Things that are fine and worth saying

The console code page handling works: an em dash and Devanagari survive a 437 console and the code
page is restored. The generated-program crash (0xC0000005) the delivery fixed stays fixed across all
186 native cases. Install is per-user, no UAC, no HKLM, and the uninstaller preserves user files.

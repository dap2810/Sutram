# Temporary-directory finding — preflight inventory

**No new install or uninstall was performed in this round.** The available package is v312; the v313 package needed to verify successful cleanup is absent. The working v312 installation and all residue were left untouched.

## B1: identified directory and every file

The read-only inspection at `2026-11-08T12:18:48.397333-05:00` confirms the previously observed directory still exists:

`%USERPROFILE%\AppData\Local\Temp\STM7C1C.tmp`

- `%USERPROFILE%\AppData\Local\Temp\STM7C1C.tmp\uninstall-core.ps1` — 14901 bytes; SHA-256 `eb53ebd2f9eb817314237bf941bd09e02feee81233b5269d61eaf70b44fc0479`.
- `%USERPROFILE%\AppData\Local\Temp\STM7C1C.tmp\uninstall.log` — 289 bytes; SHA-256 `f766a8cd0f17eebb123301ed6608145f52943f10400e0d9ec0008933d5f87b6a`.

These are the v312 uninstaller's script and successful-uninstall log, not unrelated files. Their hashes match the prior round's post-uninstall evidence exactly. The prior log reports removal of the empty Classes keys and then successful completion. This identifies the outstanding residue; it is not a new uninstall pass. [Current inventory](temp-inspection.json), [prior full uninstall evidence](../win-v312-2026-11-08/UNINSTALL.md).

`%TEMP%` and `%LOCALAPPDATA%\Temp` resolve to the **same directory** for this account. The inspection records the 15 newest entries in each location plus every file in each STM directory. It uses direct filesystem enumeration with modification times, equivalent to the relevant listing purpose of `dir /od`; no new post-uninstall command run is claimed.

An older `STM1E91.tmp` also remains, with `uninstall-core.ps1` (13,794 bytes) and `uninstall.log` (117 bytes). It predates the v312 run; it is not evidence of a repeated v313 uninstall.

## B2: directory naming and repeat run

Observed names: `STM1E91.tmp` and `STM7C1C.tmp`. The source calls **GetTempFileNameW with prefix `STM` and uniqueness input zero**, then replaces that temporary file with a directory. The observed pattern is **`STM<hexadecimal unique component>.tmp`**, not a timestamp chosen by Sutram. Do not infer randomness from the names. [Exact source excerpt](temp-name-source.txt).

**New install/uninstall repetition: NOT RUN**, because installing another v312 package would not satisfy the brief's v313 identity requirement. Historical names plus source establish the naming mechanism; they do not establish v313 cleanup repeatability.

## B3: after-fix removal and other new artifacts

**NOT RUN — v313 unavailable.** Once supplied, snapshot both temp locations, run two installation/uninstallation cycles, track each exact staging path, and compare the before/after listings. Verify the script, log and directory disappear after successful uninstall and identify any other new entries. No files were deleted to make this condition appear satisfied.

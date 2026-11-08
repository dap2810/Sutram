# R153-00 — WS1: ChatGPT's trace is right, and it was data loss. Now one function decides whether a shortcut may be written and records it, and ownership is the link's own bytes, not a flag or a target. WS2: the installer's decide-and-record pairs, every one named; no third one disagrees, and two weaker records are named. WS3: no. No build path that can produce a shipped binary defines a mutant flag or a lowered budget. They appear in two test files and the source, and a gate now proves the committed compilers are the plain builds.

## Release line

```
gates: 78 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v314) - sampurna sutra      (compiler unchanged since 52d78435)
```

- **Commit:** the one carrying this file (SHA in my chat report). Base: `4e2e0fa` (v314 + ROUND-153).
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **The guard: NOT re-run,** because no compiler, runtime, library or language-pack byte changed. `src/`, `win/`, `lib/`, `lang/` and the binaries are as at `52d78435`. The v313 → v314 guard (R152-00) stands.
- **The installer is rebuilt** - the engine and the uninstaller changed: `Sutram-Setup.sha256` = `573e5feb236313576f0081eb750e1684a5ea101d14cc611df69bdabd068a9959`, `PASS payload v314 = compiler v314`, self-test exit 0 under Wine, gate `R140 package` 7/0. **This is a new package. The v314 candidate is now this one.**

**Not done:**
- **No PowerShell here,** so the new shortcut fixture is **NOT RUN**. It is written for Tuesday's Windows run, as R142's boundary fixture was.
- **No native run.**

## WS1 - the shortcut ownership defect

**ChatGPT's five steps are right, and I reproduce them by reading v314's engine:**
1. `New-Shortcut` (the helper) saw an existing `Sutram IDE.lnk` not in the old state's `OwnedShortcuts`, logged "Preserved", returned - and did not record it.
2. The desktop block had picked that name because `$isOurs` - a matching TargetPath - said it was the installer's.
3. The caller then set `$desktopOwned = $true` regardless, so the state said `DesktopOwned=1`, `DesktopLink=Sutram IDE.lnk`.
4. The uninstaller removed the desktop link on `DesktopOwned` plus a matching target.

**So a user's own link to the IDE was deleted.**
- **And ChatGPT's second case is right too:** a link the installer had written, retargeted by the user, was overwritten on reinstall. History in `OwnedShortcuts` was taken as permission.
- **The Start-menu removal had the same weakness:** membership plus a target under the installation folder.

**The fix: one place decides and records** (`install-core.ps1`, `Set-OwnedShortcut`). It is the only place in the engine that saves a link. It has five callers: four Start-menu links and the desktop. It returns what it did:
- **`created`** - the name was free;
- **`updated`** - it is this installer's own link, unchanged since it wrote it. That means its bytes have the SHA-256 recorded when it was written. Or, for a record from before this change, which has no hash, it says exactly what this installer writes: target, arguments, working folder, icon;
- **`preserved`** - anything else: a user's own link, or the installer's changed by the user. It is left as it is, and **not recorded**.

**How the record works:**
- **Only `created` and `updated` are recorded,** in the same function, as `OwnedShortcuts` entries of `<base64 path>|<SHA-256 of the .lnk as written>`.
- **A matching target is no longer evidence of anything.**
- **`$isOurs` is gone.**

**The desktop:**
- It tries the previous name it made, then `Sutram IDE.lnk`, `Sutram IDE (Sutram).lnk`, `Sutram IDE (Sutram 2).lnk` … `(Sutram 9)`, and takes the first one `Set-OwnedShortcut` does not preserve.
- `DesktopOwned` and `DesktopLink` are written from that result, and nothing deletes on their word.
- **If all ten names are taken,** no desktop link is made, and the log says the IDE is in the Start menu.
- **Not done: the Finish page does not say so.** The engine cannot reach the wizard's page today. Nine fallback names make that case very unlikely; I name it rather than claim the icon always exists.

**Unchecked on a reinstall:** only an unchanged own link is removed (`Remove-OwnedShortcut`, the same test). A changed one stays.

**The uninstaller:**
- It removes a shortcut only when all of these hold:
  - the state records it **with a hash**;
  - it is in the Start-menu `Sutram` folder or directly on the desktop;
  - it ends `.lnk`;
  - **its bytes still have that hash.**
- `DesktopOwned` and the target are no longer read at all.
- **A link recorded without a hash is kept.** That case does not arise: the uninstaller reads only a state its own installer wrote (each installer copies itself as its uninstaller), and that installer records hashes. An upgrade from v314, whose records have none, re-records each link it keeps as its own.

**Checked, and a fixture for Windows:**
- **gate `R143 installer first contact`** (16 checks) now requires all of this:
  - the order inside `Set-OwnedShortcut`: the test, then the save, then the record with the hash;
  - "preserved" returns before the save;
  - it is the only `.Save()` in the engine, with five callers;
  - DesktopOwned derives from the result;
  - uninstall checks the hash, the folder and the record, and never a target or a flag.
- **The new R153 checks fail on v314's engine** (`evidence-r153/first-contact-on-v314-engine.txt`).
- **`tests/windows/test_installer_shortcuts.ps1`, NOT RUN:** the installer's own functions, desktop statement and uninstall statement, run against real `.lnk` files under `build\`. It has six cases, and they include all four of ChatGPT's:
  1. a user's same-target link with their own arguments - kept byte for byte through install and uninstall;
  2. the retargeted own link and a reinstall - kept byte for byte, fresh name;
  3. both names taken - both kept, the third name used;
  4. an empty desktop, and the v312 Notepad collision - only the installer's made and removed;
  5. a pre-v315 record without a hash - adopted only when it says exactly what the installer writes;
  6. unchecked on reinstall - the unchanged own link goes, a changed one stays.

**One limit, named:** if Windows itself rewrites a `.lnk` the installer made (link tracking can), its hash no longer matches. Uninstall then leaves it. **That direction is a leftover shortcut, not a deleted file.**

## WS2 - the class: who decides, who records

**Every place the installer or uninstaller acts on its own earlier decision:**

| # | what | decided where | recorded where | acted on (uninstall or reinstall) by | agree? |
|---|---|---|---|---|---|
| 1 | **shortcuts** (Start menu, desktop) | `Set-OwnedShortcut` | **the same function**, with the link's hash | the hash | **yes, from R153** (it was two places) |
| 2 | **the desktop flag** (`DesktopOwned`, `DesktopLink`) | the result of 1 | the state | **nothing deletes on it any more** | yes |
| 3 | **installed files** | the manifest and journal hashes | the manifest (`payload.manifest.sha256`) | the hash of each file | yes |
| 4 | **the superseded copy** | the full hash compared (R142) | the `_superseded` name | the comparison, then the delete | yes - **the race between them remains** |
| 5 | **PATH** | `Set-UserPathEntry` says whether it added the entry **now** | `PathOwned` = owned before, or added now - **the same statement** | `PathOwned` and the entry's value | yes; **see the weaker record below** |
| 6 | **the `.sm` association** | the extension's default was empty, so it was set | `AssociationOwned`, the same block | `AssociationOwned` **and** the default still being `Sutram.Source` | yes |
| 7 | **the `Sutram.Source` class** | always written; a conflicting one refuses | its command value | the command value still being this installation's | yes |
| 8 | **the uninstaller itself** | copied by the installer | `UninstallerSHA256` | the hash; a changed one is kept | yes |
| 9 | **the staging folder** (`%TEMP%\STM*.tmp`) | the wizard creates it | its name and contents | TEMP, the name, exactly two entries | yes |
| 10 | **the empty `.sm` keys** | nothing records them | - | removed only when empty | yes - by state, not record |
| 11 | **the installer's own record files** (manifest, pending, state, marker, journal log) | the installer writes them | **their names only** | **the name** | **weaker: by name, not content** |
| 12 | **the uninstall registry key** (`HKCU\...\Uninstall\Sutram`) | the installer writes it | its name | the name; a second Sutram is refused before install | the name, which is Sutram's own |

**No third place disagrees the way the shortcut did.** Two are weaker than content, and I name them:
- **PATH (5):** an entry is a string. If the user later adds the same entry by hand after the installer did, uninstall removes the one entry - the two are the same string. Nothing records who typed it second. **That loses a PATH entry identical to the installer's, not a file.**
- **The five record files (11):** removed by name in the installation folder the marker identifies. **R142-00 named them; not changed.** A file a user put there under one of those names would go.

## WS3 - the mutant flags: no

**Is there any build path that defines either mutant flag, or a lowered budget, and produces a binary that could be shipped? No.**

**Every place they are defined** (the whole tree searched, `.git` excluded):
- **`src/sutram_compiler.asm`** - the `%ifndef R142_MUTANT_NO_STMT_CHECK` / `NO_GLOBAL_CHECK` guards, and `%ifndef R143_WALK_BUDGET` with its default. **Not defined there, only tested for.**
- **`tests/r137/test_slice_number.py`** - passes `-DR142_MUTANT_NO_STMT_CHECK` and `-DR142_MUTANT_NO_GLOBAL_CHECK` to `nasm`. The output goes to a fresh `tempfile.mkdtemp()` folder, never the tree.
- **`tests/r143/test_walk_budget.py`** - passes `-DR143_WALK_BUDGET=64`, also into a fresh temporary folder.
- Everything else that mentions them is a hand-back, a brief, a review or evidence text.

**Every build path, read for `-D`:**
- `tools/build_installer_linux.py` and `windows/native-installer/build-installer.ps1` package the **committed** `win/sutram.exe`. They build only the wizard (`-dR73_ICON`).
- `windows/gui/build-gui.ps1` builds the IDE (`-dR73_ICON`).
- `tools/r62_windows_acceptance.ps1` builds `win\sutram.exe` with `-dWINDOWS` only.
- `tools/proof_lib.py` builds into its own build folder with no `-D`.
- `tools/guard_page.py` (`-dGUARD_PAGES`), `tools/r65_native_acceptance.py` (`SUTRAM_R65_*`) and `tools/build_xmm_variants.sh` (`SUTRAM_EXPERIMENTAL_XMM_CACHE`) build other test variants into scratch folders.
- The CI workflows (`.github/workflows/*.yml`, `workflow_dispatch` only) build with `-dWINDOWS` and `R49_WIN_DIAG_*` probes into `/tmp`. None uses a mutant or budget flag.

**And it is checked, not just searched** (from R152, gate `R137`): the gate builds the compiler from `src/` with no `-D`. It requires the committed `sutram_compiler`, `sutram.exe` and `win/sutram.exe` to equal those builds byte for byte. A binary built with either mutant or a lowered budget differs, and the gate fails.

**The chain to the user's machine:** gate `R140 package` requires every payload entry to equal the tree file it came from. **So the `sutram.exe` in `Sutram-Setup.exe` is the plain build.**

## For Tuesday

1. `tests/windows/test_installer_shortcuts.ps1` - the six shortcut cases, no installation.
2. The installer with a user's own `Sutram IDE.lnk` on the desktop (same target, custom arguments): install, uninstall, compare its bytes.
3. The rest of the v314 list (R152-00).

Evidence: `Claude-to-Sarvam/evidence-r153/`.

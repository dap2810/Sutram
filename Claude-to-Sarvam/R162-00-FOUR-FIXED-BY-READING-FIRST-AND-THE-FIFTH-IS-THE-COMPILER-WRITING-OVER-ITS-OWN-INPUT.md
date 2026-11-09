# R162-00 — WS1: all four fixed; D was already in R161 (`3677663f`), after the commit ChatGPT reviewed. WS2: yes, there is a fifth, and it is outside the installer. The compiler, in both modes, and the linker overwrite their own input when the output names the same file: `sutram hello.sm hello.sm` replaces the program with a binary. Reported, with a fix, not fixed - it would make the compiler v316 two days before the native run. WS3: the package is `84e36b5915172c2c2eba3b0a4379672148ea431bff43f99ffdd81eee8954cb01`; what could blur Tuesday's reading is named below. WS4: my channel has no more safe copies by the R161 rule.

## Release line

```
gates: 79 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v315) - sampurna sutra      (compiler unchanged since 308c2161)
installer 84e36b5915172c2c2eba3b0a4379672148ea431bff43f99ffdd81eee8954cb01
```

- **Commit:** the one carrying this file (SHA in my chat report). Base: `1c5150ad`.
- **The guard: NOT re-run** - no compiler, runtime, library or pack byte changed.
- **The installer is rebuilt:** the engine and the uninstaller changed. Gate `R140 package` 7/0. **`67e07959…` is superseded.**

## WS1 - the four, and the rule

**The rule, as ChatGPT put it, applied to each:** capture what decides the change and what would reverse it, and keep it until the step that can fail is done.

**A. The lock deleted whatever was at its path.**
- Both engines opened `<InstallDir>.sutram-lock` with `OpenOrCreate` and `DeleteOnClose`. A file already there was opened, never read, and deleted when the lock closed - even by a run that then refused.
- **Now both engines share one function, `Open-SutramLock`:**
  - it makes the lock with **`CreateNew`** (the file must not exist yet), still `DeleteOnClose`, and writes a marker into it: `Sutram installer lock`;
  - **a file already there is read before anything is decided:**
    - held by another process: another installer or uninstaller is working - the old message;
    - empty (what R161 and earlier left, only if the machine stopped), or the marker: a stale lock. It is removed **after it was read**, and the lock is made again;
    - **anything else: the run stops, names the file, and leaves it unchanged.**
- **ChatGPT's warning is kept:** an occupied lock is never deleted. One that another process holds cannot even be opened, and the run stops.

**B. `-VerifyOnly` changed things.**
- It returned only after taking the lock (a file made and deleted beside the target) and after removing a committed transaction folder.
- **Now it returns before both, and before any installation state is read.** It extracts the embedded payload into a private folder under TEMP, verifies its hashes, runs the compiler's `--version` and `--help`, and removes that folder.
- **What it still writes:** the log it is given, and that TEMP folder.
- Its only caller is `tools/test_windows_payload.py`. The normal wizard path does not use it.

**C. Finishing an interrupted run skipped the uninstaller's hash check.**
- The check ran only when no run was pending. The copy at FINALIZE overwrote whatever `Sutram-Uninstall.exe` was there.
- **Now, when a run is pending, an existing uninstaller is replaced only if its bytes are ones an installer wrote:**
  - the previous installation's (`UninstallerSHA256` in its state);
  - the one the interrupted run wrote - **the uninstaller's hash is now journaled (`UNINSTALLER`) before it is copied**, and `Read-Journal` reads it back;
  - or this setup's own bytes. Overwriting identical bytes loses nothing.
- **Anything else: the run stops** and says to move the file.
- **The one case this makes stricter:** a run interrupted by a v315-or-older setup, after it copied its uninstaller, then finished by a *different* setup. Nothing recorded those bytes, so the run refuses, and the message says what to do. With the same setup, which is how the interrupt-and-retry test runs, the hash matches.

**D. State and marker deleted before the self-delete:** done in R161 (`3677663f`). ChatGPT's R223 reviewed `1c6dfc5d`, the commit before it. The Settings entry, the manifest, the state and the marker now go only after the uninstaller has deleted itself.

**Gates:**
- `R143 installer first contact` has **28 checks**:
  - A: `CreateNew`, the marker, the read before the delete, one shared function, no `OpenOrCreate` left;
  - B: `-VerifyOnly` returns before the lock, the cleanup and every state read;
  - C: the pending check and the journal order;
  - D: from R161.
- **All four new ones fail on the engine of `3677663f`** (`evidence-r162/first-contact-on-3677663f-engine.txt`).
- `R134 install transaction` follows the lock's new form.
- The PR #68 lock fixture (`tests/windows/test_installer_lock.ps1`) now extracts `Open-SutramLock`.

**New Windows fixture, NOT RUN:** `tests/windows/test_installer_lock_file.ps1` runs the real `Open-SutramLock` under `build\` with:
1. nothing at the path;
2. a user's file with content: refused, bytes unchanged;
3. an empty stale file;
4. a marked stale file;
5. a lock another process holds: refused, and the holder keeps it.

## WS2 - is there a fifth? Yes: the toolchain

ChatGPT scoped its audit to the two engines and the wizard's staging. **The other programs that write to a user's disk are the compiler, the linker and the IDE.** I tested the first two (Linux, v315):

| command | what happened |
|---|---|
| `sutram_compiler same.sm same.sm` | **`Siddh`, exit 0 - `same.sm` is now an ELF binary. The program is gone.** |
| `sutram_compiler --object b.sm b.sm` | exit 0 - `b.sm` is now a `SUTRAMO1` object |
| `sutram-link a.smo a.smo` | exit 0 - the object is now an ELF binary |
| a program that fails to compile, with an existing `out.bin` | **not this defect:** the refusal leaves `out.bin` unchanged |

**It is the same class:** the compiler reads the source into memory, then writes the output by name, and never asks whether that name is the file it read. A student who types the source name twice loses the program without a word.

**The IDE does not have it:** it compiles into a fresh `GetTempFileName` path under TEMP and runs from there. Its Save writes the file being edited, which is what Save is for.

**The fix I propose, not done:** refuse when the output is the same *file* as an input - not the same string, since `./a.sm` and `a.sm` are one file.
- **On Linux:** compare `st_dev` and `st_ino` from `fstat` of the open source with `stat` of the output path, if it exists.
- **On Windows:** compare `GetFileInformationByHandle`'s volume serial and file index.
- **Also in the linker,** against each object.
- **It belongs in the compiler and linker, so it is v316:** the guard over 783 programs, the Windows compiler under Wine, and a new installer.
- **It cannot change any program's bytes,** but it changes the compiler two days before the only native run. **I would do it after Tuesday. Say if you want it now.**

## WS3 - the package, and what could make Tuesday harder to read

**Tuesday's package: `84e36b5915172c2c2eba3b0a4379672148ea431bff43f99ffdd81eee8954cb01`** (this commit). It has every fix since R153:
- shortcuts by hash;
- the `.sm` key opened, not remade;
- PATH as text;
- the PATH re-append;
- the uninstall retry;
- these three.

**What could blur the run, honestly:**
1. **The lock now runs on every install and uninstall, first.**
   - A mistake in `Open-SutramLock` would stop every run at its first step, with one of its own messages. That is easy to read, but it would block everything after it.
   - **So run the two lock fixtures before any installer case:** `test_installer_lock.ps1`, then `test_installer_lock_file.ps1`. Each takes seconds and installs nothing.
2. **The engine's PowerShell has changed in five rounds and has never run.** `tests/windows/preflight_installer_state.ps1` (R161) parses both engine files first. **Run it before anything else.**
3. **C changes one recovery path.** The interrupt-then-retry case should behave as on v309, because the same setup is used. If it refuses with *"not one an installer wrote"*, that is C, and the log names the file.
4. **The lock file has 23 bytes in it now,** where it was empty. Nothing reads it but the engines.

**Nothing in the four changes an ordinary install's result** - the files, the registry, PATH or the shortcuts. **The order I gave in R161-00 stands,** with the lock fixtures added as step 2.

## WS4 - my footprint

**`Claude-to-Sarvam/`: 2,059 files, 15.26 MB** (decimal; measured at this commit before this report; `evidence-r162/footprint.txt`):

| | files | bytes |
|---|---:|---:|
| hand-backs (`R*.md` and the other reports at the top level) | 254 | 1,930,225 |
| evidence | 1,805 | 13,331,047 |
| - cited by path, or by name in a report that names its folder | 975 | 6,742,307 |
| - in a folder a report names as a whole | 829 | 6,584,722 |
| - neither | 1 | 4,018 |

**Copies:**
- **283 evidence files share their bytes with another file in my channel**, 2.88 MB in the extra copies. They are mostly the same guard, Wine or gate log saved under a second name in a later round, as R120-00 found.
- **30 share their bytes with a file outside it**, 134 KB.
- **Every one of these is cited**, by path or as part of a cited folder.

**Under the rule you set in R161, none can go.** That rule lets a byte-identical copy go when the file that stays covers it. Here each copy is the record of a different round, and that round's report names it by its own path. ChatGPT's condition - consolidate only when every dependent link, command and manifest is accounted for - is not met by removing one.

**The 11 removed in R159 were the only ones that were both uncited and copies. There are no more.** I removed nothing this round.

## Not done, and why

- **The compiler and linker self-overwrite: not fixed** (WS2) - your call on timing.
- **No PowerShell or Windows here:** every installer change is gated by reading, not run. Both new fixtures are NOT RUN.

**Also corrected while in there:** five more reference sentences from ChatGPT's R223 list (its items 13-17). The R158 gate now holds them:
- `bindu_gunan` stops on unequal lengths, it does not read the shorter one;
- the Windows compiler always makes a Windows program, whatever the output name;
- 349,521 is an upper bound, not a statement anyone has built;
- the `kosh` count limit is gone, but memory still bounds it;
- the descriptor has been stable since v302.

Evidence: `Claude-to-Sarvam/evidence-r162/`.

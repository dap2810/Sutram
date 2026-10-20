# R14-01 — WS1: the installer is rebuilt

**Branch `claude/round-14`, commit `b059afc1`, draft PR #49.** Base: main `a82968d1` (v212).

## The deliverable

**`Sutram-Setup.exe` now installs the current compiler.**

| | main (before) | the branch |
|---|---|---|
| `Sutram-Setup.exe` | `73fabd71…` | **`7c4158e12d539c26f179f3c7baa3128bd6b73d8306dff161bde9b3b2535d97cb`** |
| **the payload (`payload.zip`, inside the setup)** | 458 entries, no `.sandesh` | **`d267a876aed52682c41534fd0bd9ced9e90087468520c9775c5c6f8f6ffb7df5`**, 1,272,374 bytes, 494 entries, 33 `.sandesh` |
| payload `bin/sutram.exe` | `b6e2bb34…`, prints **v160** | **`798534ba…`**, prints **v208**: the same file as the repo's `win/sutram.exe` |
| payload `sutram-ide-gui.exe` | `528a4ee0…` | **`6574b21b…`**: the same file as the repo's |

`Sutram-Setup.sha256` is updated to match. The full hashes are in `evidence-r14/hashes.txt`.

## A correction to the brief

**The brief says I have a Windows 11 machine. This session does not.** The ROUND-03 acceptance ran on a
Windows 11 machine that was linked to that session. **No Windows machine is linked to this one.**

**The rebuild did not need one.** `tools/cross_build_windows.py` builds the setup on Linux. It follows
`windows/native-installer/build-installer.ps1` step by step, and its output is reproducible.

**What did need Windows, and so was not done:**

- `build-installer.ps1`'s own Windows-only steps (`Assert-PeResourceDirectory`, and the self-test as part of
  the build). **The self-test was run, under Wine.**
- **The acceptance on Windows.** It is NOT-RUN.

## Checks

| Check | Environment | Result |
|---|---|---|
| `cross_build_windows.py --check` (rebuild, compare all four files) | Linux | **REPRODUCED**, 4/4 MATCH |
| `Sutram-Setup.exe --self-test` | Wine 9.0 | exit 0 |
| the same, with one payload byte flipped | Wine 9.0 | exit 1 |
| `tools/accept-windows.ps1`, **this setup** | Wine 9.0 | **FAIL at `install-wizard`**: the files are copied, then the shortcut step fails with `HRESULT E_FAIL` from a COM component. **This is Wine's `WScript.Shell`, the R6 finding**, not this build. |
| `tools/accept-windows.ps1`, **the R6 harness build of the same tree** (two Wine-only lines, `evidence-r6/C-harness-build/HARNESS-ONLY.diff`; not a deliverable) | Wine 9.0 | **PARTIAL: 11 PASS / 0 FAIL required.** The advisory `temp-staging-cleaned` FAILs, as known (R4-03). |
| **the installed copy's `bin\sutram.exe --version`** (harness build) | Wine 9.0 | **`Sutram 1.0 (v208) - sampurna sutra`** |
| `gates.sh` | Linux | 12 PASS / 1 FAIL / 1 NOT-RUN (below) |
| **Windows: build, install, acceptance** | — | **NOT-RUN** |

**Who can run the Windows check:** the owner, on his Windows machine:

```
powershell -ExecutionPolicy Bypass -File tools\accept-windows.ps1
```

It reports the setup's and the installed files' hashes. **The installed `bin\sutram.exe` should be
`798534ba…`, and `sutram --version` should print v208.** (The script does not check the version itself.) Or
I can run it in a session that is linked to his Windows machine.

## Three things found on the way

1. **The binaries' mode was lost again.** On main, `sutram_compiler`, `sutram-ide` and `sutram-gui` are
   100644 again. The R13 merge uploaded them one at a time ("merge Claude ROUND-13: sutram_compiler").
   - **The "committed modes" gate FAILs on main**, as R13-05 predicted.
   - **The X11 gate fails 18 of 18 with main's mode**, because `sutram-gui` cannot run.
   - **The branch sets all three to 100755 again.**
   - **Please merge PR #49 with `git merge` or a cherry-pick, not by uploading the files,** or this
     happens again.
2. **The setup goes stale whenever `docs/` changes.** The payload carries all of `docs/`, so the v212
   CHANGELOG entry alone made my first build (`070089e8…`, on v211) differ. I rebuilt on v212.
   - **After any later commit to `docs/`, `--check` will say DIFFERS again**, while the compiler in the
     payload stays current.
   - **Two ways out, your choice:** rebuild the setup only at release time, and treat DIFFERS between
     releases as expected; or leave `CHANGELOG.md` (or all of `docs/`) out of the payload. The second is a
     change to `build-installer.ps1` as well as the cross-build.
3. **One X11 test fails, and it is not new.** `tools/test_x11_edscroll.py` times out in `sendall` while
   typing 30 lines. It fails the same with main's pre-R13 GUI (`465c202f`). The test does not read the
   GUI's replies while it types, so the socket fills up and both sides wait. **The other 17 pass.** I did
   not change the test.

## Evidence (`evidence-r14/`)

| File | What |
|---|---|
| `hashes.txt` | the setup, the payload, its three binaries, old and new; the installed copy's `--version` |
| `cross-build.json` | the build report |
| `wine-accept-real-setup.txt` / `.json`, `wine-real-setup-install.log`, `wizard-failure-box.png` | the real setup under Wine |
| `wine-accept-harness-setup.txt` / `.json`, `wizard-done.png` | the harness build under Wine |

**Every Wine result is Wine 9.0 only. None of it is Windows acceptance.**

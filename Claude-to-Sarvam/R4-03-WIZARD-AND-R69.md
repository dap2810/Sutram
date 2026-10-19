# R4-03 — WS3: the r69 tests and the wizard defects

For each item: reproduced or not, whose it is, and what I did. All reproductions ran under **Wine 9.0 on
Linux**, not on Windows.

**How I decided whose each item is.** Git authorship cannot answer it: every main commit is `dap2810`
(the merge-by-file commits). I used R3-00, which lists exactly what Claude's R3 changed in the wizard: 28
lines, the class icon. I also checked `git blame` and the R3 patch.
- Everything in the wizard outside those icon lines is **ChatGPT's delivery**.
- The GUI and the icon are **mine**.

## Summary

| # | Item | Reproduced | Owner | Action |
|---|---|---|---|---|
| 1 | Wizard acts on any `WM_COMMAND` notification, not only a click | **YES**, and it is worse than R3 said | ChatGPT | reported, **not fixed** |
| 2 | Licence page mojibake | **YES** | ChatGPT | reported, **not fixed** |
| 3 | `%TEMP%\STM*.tmp` left after install | **YES** (on the path the wizard treats as success) | ChatGPT | reported, **not fixed** |
| 4 | `tests/r69` 2 FAIL | **YES** (2 FAIL; the old ERROR is gone) | ChatGPT (scripts) | reported, **not fixed** |
| 5 | `tests/r67` 2 FAIL (GUI build/link source tests) | **YES** | **mine** (R73) | **fixed**: 17/17 |
| 6 | IDE names the wrong failing stage | YES (found this round) | **mine** | **fixed** (R4-02 §1) |
| 7 | Wizard footer cut at 12 characters | YES (found this round) | text length of ChatGPT's string | fixed as part of WS2's text change (R4-02 §2) |

## 1. Next / Back / Cancel / Browse act on any notification — HIGH, ChatGPT's

**The code.** In `windows/native-installer/sutram_wizard.asm`, the `wndproc` `.command` handler (line
2536) reads the notification code into `edx`. It then compares only the control id for `IDC_BACK`,
`IDC_NEXT`, `IDC_CANCEL` and `IDC_BROWSE`. `BN_CLICKED` is checked only for `IDC_ACCEPT` / `IDC_DECLINE`.

**The reproduction.** I wrote a 25-line program, `evidence-r4/repro/sendfocus.asm`. It finds the wizard
window and sends it one `WM_COMMAND` with `LOWORD = IDC_NEXT (2002)` and `HIWORD = BN_SETFOCUS (6)`. That is
a focus notification, not a click. It sends nothing else, and no mouse or keyboard input is involved.

```
DISPLAY=:99 wine64 wizard.exe &          # welcome page
wine64 sendfocus.exe   → exit 0           # page: licence
wine64 sendfocus.exe   → exit 0           # page: install location
```

`evidence-r4/screens/bn-repro.png` shows the three states. **The second message went past the licence page
while `asvikar` (decline) was selected and the Next button was disabled.** The handler never looks at the
button's state, so the licence is not enforced against this path.

Five such messages and no click took the wizard through every page, including Install, to
`Sutram sthapana purna` ("installed successfully") (`wizard-done-after-focus-only.png`).

**What this does and does not prove.**

- Under Wine, `powershell.exe` is a stub that exits 0. So nothing was actually installed:
  `AppData\Local\Programs\Sutram` does not exist.
- That exposes a second, smaller point. **The wizard shows success on the script's exit code alone.** It
  never checks that the install folder exists afterwards.
- On Windows, R3 saw a real install happen this way under passive UI Automation (R3-03 §1).

**Fix, for ChatGPT:** add `cmp edx, BN_CLICKED` / `jne .cmd_done` before each of the four dispatches. That
is four pairs of lines, and the same check the IDE has. Optionally, have `.do_next` refuse while
`hw_next` is disabled (`IsWindowEnabled`), so the licence cannot be skipped by any message.

**I did not change it.** The brief says "do not fix ChatGPT's wizard behaviour".

## 2. Licence page mojibake — MEDIUM, ChatGPT's

**The code.** `license_to_utf16` (line 956) does `movzx eax, byte [rsi]` / `mov [rdi], ax` on each byte of
the UTF-8 `LICENSE.txt`. `wizard-license-after.png` shows the first line as **`Sutram âThe Complete Thread`**:
the em dash (`E2 80 94`) becomes `â` plus two invisible C1 controls. The Hindi, Tamil, Telugu and Gujarati
lines further down are garbled in the same way. The capture is under Wine, but the code path is
platform-independent.

**Fix, for ChatGPT:** `MultiByteToWideChar(CP_UTF8, 0, blob, len, lic_w, 4095)`. The import is one line.

**Not changed.**

## 3. `%TEMP%\STM*.tmp` is never removed — LOW, ChatGPT's

**The code.**

- `make_unique_stage` (line 2810) creates the folder with `GetTempFileNameW` + `DeleteFileW` +
  `CreateDirectoryW`.
- `RemoveDirectoryW` is not imported anywhere: `grep -c RemoveDirectoryW sutram_wizard.asm` → `0`.
- Nothing deletes `payload.zip`, the two scripts or the log.

**The reproduction.** After the run in §1, which ended on the success page,
`…/users/root/Temp/STM821d.tmp/` still held `install-core.ps1` (25157 B), `uninstall-core.ps1` (11729 B)
and `payload.zip`. On Windows, R3 measured six such folders, 4.8 MB.

**Fix, for ChatGPT:** as R3-03 §3 says, delete the files and remove the folder only after the child exits 0.

**Not changed.**

## 4. `tests/r69` — ChatGPT's scripts

```
$ python3 -m unittest discover -s tests/r69
FAIL: test_native_diagnostics_gate   'E_UTF8' not found in windows/build-windows-native.ps1
FAIL: test_staged_payload_hash_gate  'bin\sutram.exe' not found in windows/build-windows-setup.ps1
Ran 39 tests — FAILED (failures=2)
```

These are the same two gates as R3-03 §7. The scripts are ChatGPT's (v171 accepted its chain). Both gates
are good ones:

- a malformed-UTF-8 smoke test of the native compiler
- a check that the staged `bin\sutram.exe` and `win\sutram.exe` are the built ones

**The fix belongs in those scripts, not the test**, so I report it to ChatGPT. **Not changed.**

**Answered by itself:** the third item, the ERROR in `test_fixtures_derive46`, **no longer occurs.** 39 ran,
0 errors. I did not investigate which commit fixed it.

## 5. `tests/r67` — mine, fixed (commit `2ee5c5ac`)

`tests/r67` had 2 FAIL on main. Both are source-shape tests that my own R73 GUI work (R3) made stale:

| Test | Why it failed | What I changed |
|---|---|---|
| `test_gui_build_links_objects` | R73 listed the sources as `r67_gui_entry`, without `.asm` | **The program:** `build-gui.ps1` now lists the files by their full names and derives the `.obj` name. |
| same test, `'@objects'` | R73 routes the linker through `Invoke-BoundedProcess` with an argument array (`+$objects+`), so there is no splat any more | **The test:** it now checks that `$objects` reaches the linker call. The reason is in a comment. |
| `test_gui_calls_real_counter_without_caret_override`, `'API SetWindowTextA'` | R73 deliberately moved the cluster count from the window title (which the editor now owns: file name, `*` marker) to the status line | **The test:** it now checks for `call update_status` and that `SetWindowTextA` is absent. Reason in a comment. |

**Two of these three are test edits, so I am saying so plainly.** In both, the program's behaviour changed
on purpose in R73, which was accepted at v171. The test's intent is unchanged: all three objects are linked,
and the count is shown. Making the program call `SetWindowTextA` again would undo an accepted change.

```
$ python3 -m unittest discover -s tests/r67    → Ran 17 tests — OK      (was 15/17)
```

**The icon:** no defect found. It is the R73 PE resource and the drawn sidebar, unchanged this round.

## All gates on the branch (`claude/round-04`)

| Gate | Result |
|---|---|
| `tests/run_tests.py` (branch compiler) | **PASS 191 / NO-EXPECTATION 4** |
| `sh tools/gates.sh` | **PASS 8 · FAIL 1 · NOT-RUN 1** (log: `evidence-r4/logs/gates-branch.txt`). Codegen, packs, proof_lib 191/191, proof_props 86/86, layers, stdlib and module graph all PASS. |
| — the gates FAIL | **X11 GUI protocol 17/18.** `test_x11_edscroll.py` times out (`TimeoutError` in `conn.sendall`). **Pre-existing:** the X11 GUI built from unmodified main is byte-identical to the branch's and fails 3/3 the same way. Same as R3 reported. Not investigated. It ran this time only because my Xvfb made `/tmp/.X11-unix` exist. |
| — the gates NOT-RUN | Windows execution. Note that its text, "never executed by anyone", is now **stale** after v171. I left it, because `gates.sh` is yours. |
| `tests/r66` / `r67` / `r68` / `module_graph` / `gui` / `ci` | 22 / **17** / 19 / 18 / 28 / 9 — all OK |
| `tests/r69` | 39 ran, **2 FAIL** (§4) |
| `tools/check_workflow_triggers.py` | `CI_NOTIFICATION_POLICY_ACCEPTED: no automatic workflow events`. No workflow was changed. |
| `r69_build --check-only` / R70 corpus | `SOURCE_PINS_CHECKED` / 6 of 6, `native_status` PASS |
| Windows cross-build (compiler, GUI, wizard) | assembles and links |
| `tools/test_windows_gui.py`, the other `tools/test_windows_*.py` | **NOT-RUN.** Windows-only. |

Raw outputs are in `evidence-r4/logs/other-gates.txt`.

## Not verified

- **None of the wizard reproductions ran on Windows.**
  - §1's message path is identical on both platforms, but I did not see a real install happen.
  - §3 is shown on the path the wizard treats as success, not after a real successful install.
- **Not reproduced:** R3-03 §4, §5, §6 and §8. They are ChatGPT's and were not in this brief's list. They
  stand as R3 reported them.

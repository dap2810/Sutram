# R3-01 — ChatGPT's Windows delivery, accepted for real, then merged onto main v168

**Machine:** Windows 11 10.0.26300, standard (non-administrator) account, no UAC prompt at any step,
PowerShell 5.1 with `CurrentUser RemoteSigned`, NASM 3.01, GNU ld 2.47, Python 3.13. Console code page
65001 at start; a child console at code page 437 was also used. `evidence/environment.txt`.

The delivery under test is the `ChatGPT-to-Sarvam-Windows` package (REPORT base `a09ce309`), the one
whose START-HERE says *"No installation or uninstallation was performed."* This is that step.

## 1. The package as shipped — PASS

| Step | Command / action | Observed |
|---|---|---|
| Integrity | every row of `SHA256.txt` recomputed | 121 rows, 0 mismatches |
| Compiler | `changed\win\sutram.exe --version` | `Sutram 1.0 (v29) — the complete thread` — the em dash renders; no mojibake |
| | same, inside `cmd /c "chcp 437 & ... & chcp"` | bytes `E2 80 94` written, console restored to 437 afterwards |
| | `examples\01_hello.sm` → run | `Namaste, Sutram!` exit 0 |
| | `examples\79_ayojan_cwd.sm` (import) → run | `81` |
| | `--lang sanskrit examples\218_sanskrit_devanagari.sm` → run | `योगः = 15` |
| | output path with a space | compiles and runs |
| Installer self-test | `Sutram-Setup.exe --self-test` | exit 0, nothing extracted, nothing installed |
| Developer gates | `windows/build-windows-setup.ps1` on the patched source | PREFLIGHT 403 hashes, COMPILER, GUI, SETUP all PASS; rebuilt `sutram.exe` differs from the delivered one in 6 bytes (PE timestamp + checksum) — reproducible |
| | `tools/test_windows_native.py` | 186 PASS / 3 NO_EXPECTATION / 2 SKIP |
| | portable, setup (7 checks), preflight, install-contract, `tests/gui` 28, `tests/ci`, workflow check | PASS |
| | `tools/test_windows_payload.py` | FAIL from my scratch path, PASS from a short path — see R3-03 §8 (MAX_PATH) |

## 2. Install and uninstall of the shipped `Sutram-Setup.exe` — PASS, with findings

The wizard was driven by Win32 messages (`evidence/drive-wizard.ps1`: `BM_CLICK` on the real buttons,
`BM_SETCHECK` on the real check boxes), logged page by page in `evidence/r73/wizard-install.log`-style
files. Welcome → License (Next disabled until "I accept") → Location (`%LOCALAPPDATA%\Programs\Sutram`)
→ Components (PATH on by default, desktop shortcut off) → Ready → Install → Finish in 9 seconds.
**No elevation prompt.**

After install: `bin/ win/ assets/ lang/ lib/ examples/ docs/`, `sutram-ide-gui.exe`,
`Sutram-Uninstall.exe`, `payload.manifest.sha256`, `install-state.ini`; user PATH gained
`...\Sutram\bin`; `HKCU\...\Uninstall\Sutram` (DisplayVersion **0.1.0**); `.sm` → `Sutram.Source` →
the IDE; four Start-Menu shortcuts and the desktop shortcut, all pointing at files that exist.
From a **fresh shell** (registry PATH only), from `%USERPROFILE%`: `sutram --version`, hello, import
and the Devanagari example all ran correctly.

The shipped IDE launched from the Start-Menu shortcut, showed a window, and closed on WM_CLOSE.

Uninstall (`Sutram-Uninstall.exe --uninstall`): PATH entry removed, uninstall key, `Sutram.Source`,
shortcuts and desktop link removed; my `my-work.sm` and my edited `01_hello.sm` were **preserved**
(logged as such); an unrelated PATH entry I had added survived. Leftovers: an empty
`HKCU\Software\Classes\.sm\OpenWithProgids` key, and the `%TEMP%\STM*.tmp` staging folders with
`payload.zip` (~800 KB each) — see R3-03.

## 3. Merge onto main v168

Main had moved from the delivery's base (`a09ce309`, 2026-10-16) to `e0e5031` (v168). The delivery's
`SOURCE-CHANGES.patch` does not apply to v168 (`git apply --check` fails on four files), so I
committed the 44 delivered files on their own base and did a real `git merge`:

| File | Conflict | Resolution |
|---|---|---|
| `windows/build-windows-setup.ps1` | R69 wrapper (pins, `r69-build-common.ps1`) vs delivery chain (preflight + manifest) | delivery version — it is what was built and executed |
| `windows/build-windows-native.ps1` | same | delivery version |
| `windows/BUILD-WINDOWS-SETUP.cmd` | same | delivery version |
| `docs/INSTALLATION-ROUTES.md` | prose about the old wrapper | delivery text; CRLF that crept in was normalized back to LF |

`src/sutram_compiler.asm` merged automatically (the delivery's Windows adapter edits on top of v160's
strings). Line endings were audited: no file differs from main by CR only. `windows/windows-build-
integrity.sha256` was regenerated for the merged tree (440 inputs) in its own commit.

## 4. Gates on the merged tree (before my GUI work) — the baseline

| Gate | Result |
|---|---|
| `windows/build-windows-setup.ps1` | PREFLIGHT 440 / COMPILER / GUI / SETUP PASS; `--version` = `Sutram 1.0 (v160) - sampurna sutra` |
| `tools/test_windows_native.py` | **186 PASS** / 3 NO_EXPECTATION / 2 SKIP |
| `tools/test_windows_gui.py` | 16 / 16 |
| portable · setup · payload · preflight · install-contract | PASS |
| `tests/gui` | 28 OK |
| `tests/ci` · `check_workflow_triggers.py` | OK |
| **`tests/r69`** | **FAILED: 2 failures + 1 error** (39 ran). The error `test_fixtures_derive46` **already fails on unmodified main v168**. The two failures are the merge: `test_native_diagnostics_gate` wants `E_UTF8` in `build-windows-native.ps1`, `test_staged_payload_hash_gate` wants the `bin\sutram.exe` / `win\sutram.exe` / "Installer staged a different" gate in `build-windows-setup.ps1`; the delivery's scripts do not have them. ChatGPT's call — R3-04. |
| Linux (WSL Ubuntu, ELF assembled with NASM on the Windows side, linked with WSL `ld`) | `tests/run_tests.py` **187 PASS / 4 NO-EXPECTATION** · codegen **12/12** · packs **33/33** · layers 14/9/1 · `tests/module_graph` **18/18** |
| `tools/proof_lib.py`, `tools/proof_props.py` | **NOT-RUN** — they build with a NASM inside WSL, which is not installed |

Raw outputs: `evidence/baseline-merged-tree/`.

## 5. Gates after the GUI round (final state of the branch)

Same as §4 except `tools/test_windows_gui.py` = **30 / 30** (`evidence/r73/gui-smoke.json`), and a full
install → run-from-Start-Menu → uninstall cycle of the **rebuilt** installer, twice
(`evidence/r73/wizard-install.log`, `wizard-install-final.log`, `uninstall.log`): no elevation,
installed IDE hash equals the built one, `nava patra - Sutram sampadak` title on a fresh start,
Devanagari example → `योगः = 15`, status `bhasha: swayam (sanskrit)`, uninstall leaves no install
folder, PATH entry, key, shortcut or desktop link.

Between the two cycles the reinstall was **refused**: *"The selected folder is not empty and is not
an existing Sutram installation"* — because the first uninstall had preserved my two test files in
`examples\`. Correct behaviour, bad experience; R3-03 §4.

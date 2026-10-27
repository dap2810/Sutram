# R42 on real Windows - GitHub Actions `windows-2025`, run 40515082104

**Where:** a GitHub-hosted Windows Server 2025 runner, administrator, started by hand
(`.github/workflows/r42-windows.yml`, `workflow_dispatch` only), on main at `ee2cf6f0` (the workflow commit after the R42
hand-back). **Driver:** `tools/r42_windows_run.py`. **Transcripts:** `run-40515082104-transcripts.txt` (read back
through the check-run annotations; the artifact host is not reachable from the delivering workspace).

| Check | Result |
|---|---|
| versions | committed `win/sutram.exe` **v249** (sha256 `ba6e7f60…`), previous **v248** (`416c2dbc…`) |
| **alias tests 251-255, run natively** | **PASS 5 / 5** - 251-253 print `mala ank seema atikram`, exit 1; 254 `30 7 3`; 255 `2 4` |
| **the guard, Windows compiler v248 -> v249** | **573 programs: 475 byte-identical, 93 refused identically, 5 DIFFER - exactly the 5 new alias tests; 0 elsewhere** |
| **`tests/r35/test_ffi_windows.py`** | **PASS - 21 checks, 0 failed** (all parts: build, builder, 6 sidecar refusals, the reader's refusals) |
| **`tests/r34/test_link_windows.py`** | **PASS - 1044 checks, 0 failed** |
| `tests/r34/test_windows_fixes.py` | **PASS - 4 checks, 0 failed** |
| **the Microsoft x64 call vs a C compiler ON Windows** | **PASS** - `winffi.c` compiled on the runner by **GCC 15.2.0 (MinGW-Builds)**, a different build from the committed object's GCC 16.2.0 (the object differs: 1200 vs 1136 bytes of code), read by `sutram-coff2smo`, linked: **prints `winffi.expect` exactly, 27 lines** - including the mixed `i64`/`f64` by-position cases |
| the same with MSVC `cl.exe` | **NOT-RUN** - `winffi.c` has three GCC `naked` inline-assembly functions and MSVC x64 has no inline assembly (`C2143` at lines 43, 48, 53). The run reported it as FAIL; the driver now says NOT-RUN with this reason. Not an ABI result. |

**PASS 7 · FAIL 0 · NOT-RUN 1** (the run itself printed FAIL 1 for MSVC, before the reclassification above).

**What this is NOT:** the Windows 11 standard-user acceptance (16 checks, machine clean after). This runner is
Windows Server, as an administrator, fresh each run. The installer and the IDE (`Sutram-Setup.exe`,
`sutram-ide-gui.exe`) were not rebuilt or run; they still carry v246.

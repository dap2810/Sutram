# Evidence, R130 + R131 (v306), Linux container with Wine and Xvfb

- `gates.txt` - `sh tools/gates.sh` under `xvfb-run`, first and only run: 69 PASS / 0 FAIL / 1 NOT-RUN (Windows execution).
- `suite.txt` - `tests/run_tests.py`: NO-EXPECTATION=4 PASS=327 (331 run).
- `guard-elf.txt`, `guard-pe.txt` - v305 (`30be5ac`) vs v306, 737 programs, compiled the ordinary way, bytes compared.
- `pe-differ-run.txt` - the 584 PE programs that differ, run old and new under Wine: same output and exit.
- `wine-compiler.txt` - the v306 Windows compiler under Wine against the Linux PE output, all 737.
- `installer-build.txt`, `installer-version.txt` - `tools/build_installer_linux.py`, `tools/check_installer_version.py`.
- `r130-gate-on-v305.txt`, `r130-gate-on-v306.txt` - the new installer gate on v305's wizard/engine/setup (12 of 16 fail) and on v306 (0 fail).
- `harness-79-under-wine.txt` - `79_ayojan_cwd` from a folder outside the tree: `win\sutram.exe` vs the root `sutram.exe`.
- `old-*.png` (v305's committed IDE) and `new-*.png` (v306's IDE), under Wine and Xvfb: 1 a program loaded, 2 after Run, 3 after Load example on the 70 KiB `105_block_nesting_capacity.sm`.

NOT RUN here: any PowerShell, any native Windows run (installer, OOM probe under a Job commit limit, native suite, IDE on Windows).

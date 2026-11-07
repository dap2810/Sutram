# Evidence, R133 (v307), Linux container with Wine and Xvfb

- `gates.txt` - `sh tools/gates.sh` under `xvfb-run`, first and only run: 72 PASS / 0 FAIL / 1 NOT-RUN (Windows execution).
- `suite.txt` - NO-EXPECTATION=4 PASS=327 (331 run).
- `guard-elf.txt`, `guard-pe.txt` - v306 (`5bd58ae`) vs v307, 747 programs (10 new: tests/r133/indirect).
- `pe-differ-run.txt` - the 584 PE programs that differ (the runtime), run old and new under Wine.
- `wine-compiler.txt` - the v307 Windows compiler under Wine against the Linux PE output, all 747.
- `indirect-on-v306.txt`, `indirect-on-v307.txt`, `probes-v306-vs-dev.txt` - ChatGPT's S3 and variants.
- `veh-registration-wine.txt`, `veh-registration-gate.txt` - W1: the handler registration forced to fail.
- `installer-recovery-gate-on-v306.txt`, `installer-recovery-gate-on-v307.txt` - the interrupted-install gate.
- `installer-build.txt`, `installer-version.txt` - the rebuilt Sutram-Setup.exe.

NOT RUN here: PowerShell; any native Windows run (installer, the stopped-and-finished install, OOM, suite, IDE).

# Evidence, R136 (compiler v308 unchanged; installer rebuilt), Linux container with Wine and Xvfb

- `muse-probes.txt` - Muse's thirteen R136 programs compiled and run with v306, v307 and v308.
- `one-pred-on-c306.txt`, `one-pred-on-c307.txt`, `one-pred-on-v308.txt` - gate `R134 one predicate` (21 programs).
- `gates.txt` - `sh tools/gates.sh` under `xvfb-run`: 73 PASS / 0 FAIL / 1 NOT-RUN.
- `txn-gate.txt` - gate `R134 install transaction` with the logging check.
- `installer-build.txt`, `installer-version.txt` - the rebuilt Sutram-Setup.exe.

NOT RUN here: tests/windows/test_oom_headroom.py (WS2), any native Windows run, PowerShell.

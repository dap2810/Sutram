# Evidence, R141 (v310), Linux container with Wine and Xvfb

- `gates.txt` - `sh tools/gates.sh` under `xvfb-run`: 75 PASS / 0 FAIL / 1 NOT-RUN.
- `guard-elf.txt`, `guard-pe.txt` - v309 (`040a31f`) vs v310, 768 programs: 0 DIFFER; `refusal-messages.txt` - the 181 refusals unchanged.
- `wine-compiler.txt` - the v310 Windows compiler under Wine against the Linux PE output, all 768.
- `probes-v309.txt`, `probes-v310.txt` - module-level initializers and the other non-statement forms.
- `slice-number-on-v309.txt`, `slice-number-on-v310.txt` - gate `R137 slice is not a number` (65 checks).
- `txn-gate-on-v309-engine.txt`, `txn-gate-on-v310.txt` - gate `R134 install transaction`: the lock before every state read.
- `package-gate.txt`, `installer-build.txt`, `installer-version.txt` - the rebuilt Sutram-Setup.exe.

NOT RUN here: PowerShell; any native Windows run of v310.

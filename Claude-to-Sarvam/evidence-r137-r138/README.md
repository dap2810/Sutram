# Evidence, R137 + R138 (v309), Linux container with Wine and Xvfb

- `gates.txt` - `sh tools/gates.sh` under `xvfb-run`, second run: 74 PASS / 0 FAIL / 1 NOT-RUN. `gates-run1-summary.txt` - the first run (71/3/1) and why.
- `guard-elf.txt`, `guard-pe.txt` - v308 (`11c6071`) vs v309, 768 programs: 0 DIFFER on both.
- `refusal-messages.txt` - the 181 refused programs: v308 and v309 print the same message (paths normalised).
- `wine-compiler.txt` - the v309 Windows compiler under Wine against the Linux PE output.
- `probes-v308.txt`, `probes-v309.txt`, `probes2-v308.txt`, `probes2-v309.txt` - the expression probes (ChatGPT's S4 and variants).
- `slice-number-on-v308.txt`, `slice-number-on-v309.txt` - gate `R137 slice is not a number`.
- `txn-gate.txt`, `veh-gate.txt` - the installer transaction gate (24) and the handler gate (5).
- `installer-build.txt`, `installer-version.txt` - the rebuilt Sutram-Setup.exe.

NOT RUN here: PowerShell; any native Windows run.

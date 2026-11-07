# Evidence, R134 + R135 (v308), Linux container with Wine and Xvfb

- `gates.txt` - `sh tools/gates.sh` under `xvfb-run`, first and only run: 73 PASS / 0 FAIL / 1 NOT-RUN (Windows execution).
- `guard-elf.txt`, `guard-pe.txt` - v307 (`60ce554`) vs v308, 755 programs (8 new: tests/r134/escape).
- `pe-differ-run.txt` - the PE programs that differ (the runtime), run old and new under Wine.
- `wine-compiler.txt` - the v308 Windows compiler under Wine against the Linux PE output, all 755.
- `escape-probes-v307-vs-dev.txt`, `one-pred-on-v307.txt`, `one-pred-on-v308.txt` - R134 WS1.
- `txn-gate-on-v307.txt`, `txn-gate-on-v308.txt` - R134 WS2 (static).
- `veh-and-commit-gate.txt` - the handler registration and the forced commit failure (R135 WS1), under Wine.
- `installer-build.txt`, `installer-version.txt`, `r93-after-rebuild.txt` - the installer, rebuilt after the gate run.

NOT RUN here: PowerShell; native Windows (the 512 MiB / mandapa stack-overflow cases, the transaction e2e, the wizard).

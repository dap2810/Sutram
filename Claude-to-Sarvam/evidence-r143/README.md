# Evidence, R143 (v312), Linux container with Wine and Xvfb

- `gates.txt` - `sh tools/gates.sh` under `xvfb-run`: 77 PASS / 0 FAIL / 1 NOT-RUN (two new gates: R143 walk budget, R143 installer first contact).
- `guard-elf.txt`, `guard-pe.txt` - v311 (`f924ac3`) vs v312, 768 programs: 0 DIFFER; `refusal-messages.txt` - the 181 refusals unchanged.
- `corpus-walks.txt` - steps per expression walk (a tracing build): the largest in the 768 programs is 52; the widest statement the heap holds is 87,316; shapes at 1,000 terms.
- `walk-budget-on-v312.txt`, `walk-budget-on-v311-tree.txt` - gate R143 walk budget on v312 (6/0) and in the v311 tree (4 fail).
- `first-contact-on-v312.txt`, `first-contact-on-v311.txt` - gate R143 installer first contact on v312 (10/0) and on v311's wizard and uninstaller (7 fail; the "first line" check reads the reference and passes on both).
- `package-gate.txt`, `installer-build.txt`, `installer-version.txt` - the rebuilt Sutram-Setup.exe.
- `wine-compiler.txt` - the v312 Windows compiler under Wine against the Linux PE output.

NOT RUN: anything on native Windows - the licence page drawn, the uninstall window, the registry after uninstall, the budget natively.

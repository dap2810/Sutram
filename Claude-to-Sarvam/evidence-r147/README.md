# Evidence, R147 (v313), Linux container with Wine and Xvfb

- `fourteen-shapes.txt` - the fourteen probes (tests/r147/slices) compiled and run with v313 and v307.
- `slice-gate-on-v313.txt` (89/0), `slice-gate-on-v307.txt` - gate R137 with the fourteen, on v313 and on v307 (12 of the 14 new cases fail there).
- `walk-budget-gate.txt` - gate R143 walk budget: the budget equals 8 x (AST_HEAP_CAP / AST_NODE_SIZE) + 1, the widest statement (21,829 terms) compiles, the budget-64 build refuses with the new message, the margin.
- `first-contact-gate.txt` - gate R143 installer first contact (12): licence conversion, label height, uninstall window, keys, staging folder.
- `wine-licence-label-default-font.png`, `wine-licence-label-serif-font.png` - the v313 Sutram-Setup.exe under Wine on Xvfb, licence page, with two fonts: the instruction shows both lines in each. Not Windows.
- `guard-elf.txt`, `guard-pe.txt`, `refusal-messages.txt` - v312 vs v313, 782 programs (14 new, refused by both): 0 DIFFER; refusal messages unchanged.
- `gates.txt` - 77 PASS / 0 FAIL / 1 NOT-RUN; `package-gate.txt`, `installer-build.txt`, `installer-version.txt` - the setup.
- `wine-compiler.txt`, `fourteen-shapes-windows-compiler.txt` - the v313 Windows compiler under Wine.

NOT RUN: anything on native Windows.

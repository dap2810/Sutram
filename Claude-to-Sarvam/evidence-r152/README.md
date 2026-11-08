# Evidence, R152 (v314), Linux container with Wine and Xvfb

- `ffi-shape.txt` - the FFI probes: v313 compiles a kosh slice to a foreign ptr argument (prints the descriptor's words as a number) and to an i64 count (segfault); v314 refuses both, Linux and the Windows compiler under Wine (msabi sidecar).
- `slice-gate-on-v314.txt` (91/0), `slice-gate-on-v313.txt` - gate R137 with the fifteen shapes, the mutants and the plain-build check; shape 15 fails on v313.
- `analysis-steps-gate.txt` - gate R152 analysis steps, 40 checks: every accepted and rejected case of the contract.
- `walk-budget-gate.txt` - gate R143 walk budget, 7 checks: default 200000, the exact boundary 87315/87316, the budget-64 build and the flag overriding it, the margin.
- `first-contact-gate.txt` - gate R143 installer first contact, 15 checks, including the desktop collision and the checkbox.
- `guard-elf.txt`, `guard-pe.txt`, `refusal-messages.txt` - v313 vs v314, 783 programs: 0 DIFFER; the 195 refusal messages unchanged.
- `gates.txt` - 78 PASS / 0 FAIL / 1 NOT-RUN; `package-gate.txt`, `installer-build.txt`, `installer-version.txt` - the setup.
- `wine-compiler.txt` - the v314 Windows compiler under Wine against the Linux PE (added when the run finished).

NOT RUN: anything on native Windows.

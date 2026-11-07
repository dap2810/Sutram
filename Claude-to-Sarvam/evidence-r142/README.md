# Evidence, R142 (v311), Linux container with Wine and Xvfb

- `gates.txt` - `sh tools/gates.sh` under `xvfb-run`: 75 PASS / 0 FAIL / 1 NOT-RUN.
- `guard-elf.txt`, `guard-pe.txt` - v310 (`e7eb31d`) vs v311, 768 programs: 0 DIFFER; `refusal-messages.txt` - the 181 refusals unchanged.
- `slice-number-on-v311.txt` - gate `R137 slice is not a number`, 74 checks, with the two mutant compilers.
- `slice-number-on-v310.txt` - the same gate with the v310 compiler (`--compiler`): the three walk-stack negatives compile.
- `slice-number-on-v310-tree.txt` - the same gate run in the v310 tree: the source checks fail, and the "mutants" (v310 ignores the defines) leak.
- `forgotten-entry.txt` - C1 with the initializer's walk removed: v310's design compiles it, v311's refuses it.
- `walk-stack-probes.txt` - the three probes and their output on v310 and v311.
- `unchecked-entries-trace.txt` - every gen_expr entry outside a checked statement, over the 768 programs (a tracing build of the R142 source before the version bump): two compiler-made diagnostic calls.
- `txn-gate-on-v310-engine.txt`, `txn-gate-on-v311.txt` - gate `R134 install transaction` (27 checks).
- `package-gate.txt`, `installer-build.txt`, `installer-version.txt` - the rebuilt Sutram-Setup.exe.
- `wine-compiler.txt` - the v311 Windows compiler under Wine against the Linux PE output.

NOT RUN here: PowerShell (a downloaded PowerShell binary was not permitted to run); the three tests/windows/*.ps1 fixtures; any native Windows run of v310 or v311.

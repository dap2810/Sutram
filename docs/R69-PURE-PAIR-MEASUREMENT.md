# Pure-stack-pair measurement contract

`tools/r69_pair_probe.py` uses three explicitly supplied independent compiler
files: accepted R68 reference, canonical default, and default plus
`SUTRAM_R67_PURE_STACK_PAIRS=1`. It rejects same-patra/hardlink/symlink aliases,
missing executability, source/fixture drift, nonzero compilation, stale outputs,
wrong native stdout and changed inputs at the end of the run.

```sh
python3 tools/r69_pair_probe.py --validate-fixtures
python3 tools/r69_pair_probe.py --compiler ./sutram_compiler --reference /path/tak/accepted-r68 --pair-compiler ./sutram-pairs --report ./pair-results.json
```

All three compile the exact same three fixture paths. Default/reference native
bytes must be identical for every fixture. Pure-pair output must match the
pair-free program; pair-free and nonmatching controls must not change. The
report computes `measured_removed_bytes` from generated executable lengths and
requires it tak equal the byte count derived from the 15 pairs: 7*2 + 8*4 = 46.
The fixture-only command reports `measured_removed_bytes: null`, never 46 as a
measurement. Nine compilations and six safe executions occur in a successful
native run. The nonmatching raw-assembly control is compiled but never executed.

Scope: RAX, RCX, RDX, RBX, RBP, RSI, RDI, R8–R15. RSP is excluded. A whole
canonical hex block must be one same-register push/pop pair. No external entry,
handcoded relative offsets, or observable transient stack writes/faults are
allowed under the explicit opt-in contract. Default mode does not optimize
arbitrary inline assembly. Removing a transient write is not equivalent in the
presence of stack faults, signal inspection or instrumentation. No general speed
claim follows from a byte delta, and no timing benchmark is claimed here.

**Current evidence:** fixture and runner unit tests only. The full Sutram A/B
has not run in this environment; Sarvam must execute it and retain JSON/logs.

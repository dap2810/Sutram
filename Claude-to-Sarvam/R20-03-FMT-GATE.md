# R20-03 — WS3: `sutram-fmt --check` is in `gates.sh`

**It is in, since ROUND-19** (merged as v241). Confirmed on main `1b15330b`:

- `tools/gates.sh` line: `run_gate "formatted tree" sh -c 'python3 tools/sutram_fmt.py --check --exclude-from
  tools/fmt-exclude.txt examples/*.sm examples/*/*.sm examples/lib/*.smlib lib/*.smlib tests/stdlib/*.sm
  tests/r*/*.sm tests/r*/*/*.sm tests/r*/lib/*.smlib tests/sandesh/cases/*.sm && echo FORMATTED'`
- its verdict line: `"formatted tree") … FORMATTED → PASS`, otherwise FAIL with the count and the first file
  that would change.
- **On main today: `formatted tree PASS`.** On this branch too.

R19-02 said so under "The gate"; it was in the same merged commit as the reformat. **What it covers:** every
program and module in `examples/`, `lib/`, `tests/stdlib/` and the `tests/r*/` fixtures, minus the 13 in
`tools/fmt-exclude.txt`; **not** the two negative corpora (`tests/negative/`), whose inputs are malformed on
purpose.

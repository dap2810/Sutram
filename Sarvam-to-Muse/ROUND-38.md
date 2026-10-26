# Sutram — ROUND-38: Sarvam → Muse

**Base:** main at **v340** · **Deliver into:** `Muse-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`.

## Part 1 — THREE APPROVED CHANGES, and they are yours because you have the toolchain

**The owner has approved all three. Do them in this order, and report each separately.**

### WS1 — WIRE THE FIVE DOC CHECKS INTO `gates.sh`
**`check_version`, `doc_counts_gate`, `doc_stale_claims`, `check_alloc_bounds`, `check_doc_signatures` all exist and
NOTHING RUNS THEM.** **Add them as gates.**
- `doc_counts_gate.py` and `doc_stale_claims.py` need a `--gates <transcript>` argument or they recurse - see
  `doc_counts_gate.py`'s own docstring for why
- **the gate count will rise from 34 - state the new number**
- **a documentation regression must now FAIL the build**, which is the point

### WS2 — TURN ON THE PEEPHOLE OPTIMISER, AND MEASURE IT
**`SUTRAM_R65_PEEPHOLES` is written and default-OFF.** **Build with it ON and run the guard.**
- **the guard is absolute: 476 byte-identical, 0 differ**
- **if it moves a single byte, say so and revert - that is a finding, not a failure**
- **if it is off for a correctness reason, say what the reason is and do NOT turn it on**
- **and report the benchmark difference** (`tools/bench_gate.py`) so the owner sees what the switch is worth

### WS3 — UNIVERSAL BOUNDS GUARD ON `mala` AND `kosh`
**The runtime already has it** - `mala ank seema atikram` fired in R37. **Extend it to `mala` and `kosh` indexing
generally.**
- **this changes behaviour for programs that currently overrun silently** - so **the suite may reveal tests that were
  relying on the overrun.** **Report every one; do not silently update a golden**
- **the guard still applies:** no compiled byte changes for programs that stay in bounds

## Part 2 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately. **Do not touch `backups/` or a frozen pack.**
**If any of the three cannot be done safely, STOP and say which and why - an approved change that breaks the guard is
still wrong.**

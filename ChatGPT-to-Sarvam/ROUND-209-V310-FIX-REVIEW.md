# R209 follow-up — v310 source fixes credited; final acceptance still pending

Reviewed main: `1cfab0518285e43009cafbdcd3dc761fe186c5ee`. Latest ChatGPT brief remains R209. Read-side review only: compiler/build/suite/Wine/native Windows/installer execution **NOT RUN — no toolchain used**.

## Progress credited

The source diff supports three fixes:
- `r56_gen_global_initializers` now validates the declaration before generation and applies `r134_holds_kosh` to its value. This covers both arithmetic C1 and the direct kosh-valued initializer.
- Exhausting the expression-walk budget now refuses with E_VAKYA_SEEMA instead of returning success.
- The installer lock now precedes registration, other-installation checks, oldState, pending and journal reads.

Claude R141 reports the new global cases refused, valid scalar global output 7, 65 expression checks, 75 PASS / 0 FAIL / 1 NOT-RUN, and 0 DIFFER in its ELF/PE guard. These are contributor results, not my executions. Setup is reported as `bb134603d70d49c4abd08112b77a5309ff447280f8754cb4e6e24cb4626bba47`. R141 explicitly says native v310 and PowerShell execution were not performed.

## Two statements need correction

**1. The gate does not detect an added unchecked entry.** R141 says a new expression entry fails the gate until it gets the walk. The actual check in `tests/r137/test_slice_number.py` verifies calls in two named bodies and exactly two total calls to r137_check_stmt. Adding a third entry that calls gen_expr but never calls the checker leaves both predicates unchanged and passes this structural assertion. Adding a *checked* third entry fails the count until the gate is updated. Credit protection of the two known entry checks, not discovery of a new unchecked entry.

This is a source-level counterexample to the gate claim, **not a reproduced new current-language escape**. A caller/entry inventory with explicit classifications or validation required by the expression-generation interface would strengthen it. The known-case fixes need not await a full compiler redesign.

**2. R209 I2c is not fully addressed by moving to _superseded.** The current installer still does:
```powershell
$sup = Join-Path (Join-Path $txnBackup '_superseded') ($rel + '.' + $have.Substring(0,12))
Journal ("SUPERSEDED\t" + $rel + "\t" + $have)
if (Test-Path -LiteralPath $sup -PathType Leaf) { [IO.File]::Delete($target) } else { Move-Into $target $sup }
```
(The displayed journal separators are explanatory escapes; actual source uses PowerShell tab escapes.)

Existence at a name containing a 12-hex prefix is not proof of identical bytes. Before describing this as retaining an identical copy, compare the superseded file's full hash; on mismatch preserve both or refuse. Proposed check, **NOT RUN**: create an interrupted-retry fixture with an existing backup and alter the expected superseded file; ensure retry never discards the current target on the strength of that filename. This does not assert that ordinary retry currently loses user data: target ownership is separately checked. It identifies the remaining deletion-equality condition explicitly requested in R209.

## Remaining acceptance

- Execute the final-candidate native compiler checks, including the global/local pair and positive controls.
- Close the named R209 ownership checks: suffix preservation, concurrency/fresh state, edit during publication, superseded equality, and interruption boundaries.
- Verify late recovery on this engine. The source now skips restaging matching installed files, but the earlier native run tested the old engine.
- Pin final package integrity and complete the required native installation/IDE/uninstall acceptance for that artifact.

The finite R209 checklist remains the acceptance contract. C1, fail-closed exhaustion and the stale pre-lock snapshot should now be recorded as **source fixed, with reported compiler regression evidence where applicable**, not left as unchanged defects. Native evidence from older setups is not v310 acceptance.

**Verdict: not yet YES for v310.** No new assignment or Round 210 was present. This documentation follow-up changes no source, tests, binaries or Windows evidence and launches no CI.

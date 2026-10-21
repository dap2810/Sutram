# Sutram ROUND-89 WS1 — Independent review of Claude's fuzzer evidence

**Assignment:** `Sarvam-to-ChatGPT/ROUND-89.md`. **Method:** read Claude's committed Round-15, Round-17 and Round-18 logs and current `tools/fuzz_valid.py` / `tools/fuzz_robust.py`; parse the aggregate numerical data independently. **Sutram compiler execution: NOT_RUN**, as directed. Complete machine-readable source/blob identities, histogram bins, recalculations and source-control checks: [ROUND-89-WS1-FUZZER-EVIDENCE.json](ROUND-89-WS1-FUZZER-EVIDENCE.json).

## What the raw files actually contain

| Committed evidence file | Seed / range | Claimed successes | Printed comparison count | Failures | Git blob |
|---|---|---:|---:|---:|---|
| `evidence-r15/valid/run-seed15-20000.txt` | 15, 0–19999 | 20,000 | 387,913 | 0 | `9acf12b12886` |
| `evidence-r17/fuzz-valid-seed15-20000-final.txt` | 15, 0–19999 | 20,000 | 388,616 | 0 | `30ee67abffdc` |
| `evidence-r18/fuzz-valid-seed15-20000.txt` | 15, 0–19999 | 20,000 | 388,616 | 0 | `30ee67abffdc` |

**Verdict:** The Round-17 and Round-18 claim of **20,000 / 20,000 with 388,616 reported print values** matches the committed summary headers exactly. Round-15's older number is 387,913, **703 fewer**; the generator changed in Round-17 when D1–D4 workarounds were removed. They are different run recipes, not contradictory counts.

**Important evidence limit:** The Round-17 final log, Round-17 no-workarounds log, and Round-18 log are **byte-identical Git blobs** (`30ee67abffdc1d83f47e1517a64fb18b84eb357c`). Repeated deterministic runs can legitimately produce identical output, but the identical summary cannot independently prove that all claimed separate executions actually took place. The three-line aggregate does not contain every program's stdout. **The 388,616 cannot be reconstructed independently from committed per-program stdout traces**, only matched against these summary artifacts.

## Independently summed F1 variable-count histogram

The generator deliberately draws requested local counts near 19–21, 26–28, 31–34 and 37–39. Its Round-17/18 logged histogram can be independently summed:

| Counted shape | R15 histogram | R17/18 histogram |
|---|---:|---:|
| All counted function definitions | 54,763 | **55,186** |
| 20+ counted variables | 51,088 | **51,450** |
| 27–40 counted variables | 20,358 | **20,398** |
| 34+ counted variables | 38,536 | **38,946** |

**Sample exact Round-18 bins:** 26→798, 27→800, 31→1,310, 32→1,338, 34→1,497, 37→1,789, 38→1,750, 39→1,783, 40→1,903. Thus the **F1-sensitive 27–40 region is heavily represented in the generated program definitions**; the counts are not merely random noise around the boundary.

**But the histogram's label is too strong.** In `tools/fuzz_valid.py` (near lines 605–619), `shape(prog)` iterates **all defined functions in `prog[0]`**, counting parameters and local declarations including nested scopes. In `main` (around 645–648), it increments each bin **before the binary executes**. It never observes which functions are called at runtime. **20,398 is the number of generated function definitions in that count interval, not a verified count of runtime call frames crossing F1.** Moreover, counting all lexical local declarations does not establish the maximum number simultaneously live in each frame. This is a coverage-label/measurement issue, not evidence that the underlying F1 fix failed.

## Independent robustness-log arithmetic

Round-18 `fuzz-robust-seed18-50000.txt` contains:

```text
fixed     ACCEPTED 56  ERROR 115
mutation  ACCEPTED 6880  ERROR 43120
CRASH or HANG: 0
```

Independent totals: fixed **171**, mutations **50,000**, together **50,171**. Reported accepted **6,936** plus reported errors **43,235** equals **50,171**. The claimed **zero CRASH/HANG** is present in the committed summary. **PASS: aggregate arithmetic; NOT_RUN: independent compiler/hostile-input execution.** "Hostile" does not necessarily mean every mutated input is invalid—accepted inputs are explicitly counted.

## Three source-level limitations worth fixing before a stronger claim

**F89-01 — 'output lines' are whitespace tokens, not checked line boundaries.** The harness uses `got = rr.stdout.decode('utf-8', 'replace').split()` and `lines += len(exp)`. This compares sequences of whitespace-separated numeric tokens; it would not distinguish a correct numeric sequence printed with spaces from one printed on separate lines. So the wording **'388,616 output lines compared' overstates formatting verification**. Rename the metric to *expected printed values/token comparisons*, or use `splitlines()` plus line-boundary tests. The reference's print values are counted even on a failing case; the zero-failure run avoids ambiguity for this particular sample.

**F89-02 — histogram tallies definitions, not runtime-called functions.** Rename the histogram to *generated function definitions by syntactic variable count*. If actual F1 dynamic coverage is needed, add a separate instrumentation/coverage measure that proves the relevant call sites execute and the live stack frame reaches the tested offsets.

**F89-03 — positive nonzero generated-program exits can be marked successful.** After running a binary, the harness checks `rr.returncode < 0` for signals, then checks printed tokens; it does **not** reject `rr.returncode > 0` when output matches. An exit-status failure could therefore be missed. Add `rr.returncode != 0` validation before comparing output. No proof from the logs that such a case actually occurred.

## Verdict to Sarvam

**AGREE (bounded):** committed run summaries report 20,000/20,000 successful integer-program comparisons and 50,171 hostile inputs with 0 crashes or hangs; the arithmetic is internally consistent. The generated-function histogram densely covers numeric counts around the historical F1 boundary.

**QUALIFY:** neither the 388,616 count nor the 20,398 histogram subset proves per-program stdout line exactness or actual invocation of every counted function. Logs are aggregate summaries, not independent raw output. An exit-code hole exists in the validation logic.

**NOT_RUN:** no native compiler, generated binary, Windows acceptance, or independent 20,000-case re-execution. The generator excludes floats, strings, function-side-effect evaluation order, division by zero, out-of-bounds indexes, source language packs, and Windows. These runs do **not** prove universal compiler correctness.

**Change control:** no source/lock/golden/compiler/fuzzer files changed. These are review observations and proposed future harness improvements; Claude owns the fuzzer changes, and Sarvam owns acceptance.

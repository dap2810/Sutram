# Sutram R87 WS2 — all 107 original crashes versus 21 regression cases

**Original reference:** `Claude-to-Sarvam/evidence-r15/robust/run-seed15-50000-summary.txt` and `mutation-crashes-reduced.txt` at the v238 source pin `64ea953a909eb77ebe5f278691407848014b9b6f`. **Result:** six crash *categories* are regression-covered, but **104 original crash inputs are not represented by exact-source entries in the current R17 corpus**.

## Counts grounded in original R15 evidence

| Origin | Original crashes | Distribution / preservation |
|---|---:|---|
| R1, mutation crashes (trailing `yoj`) | 27 | Canonical R1 fixture represents the root cause; none of the 27 original mutation streams is an independently named R17 case |
| R2, malformed parameter list mutations | 40 | Three small R2 fixtures; no individual original mutation streams committed |
| R3, truncated `rachana` mutations | 9 | Two R3 fixtures; no individual original mutation streams committed |
| R4, second `anya yadi` mutations | 5 | One R4 fixture; no individual original mutation streams committed |
| R5, invalid assignment-LHS mutations | 21 | Two R5 fixtures; no individual original mutation streams committed |
| R6, fixed hostile nesting cases | 5 | Three source-template equivalents in R17 generated tests; two originals not generated |

**Original: 27 + 40 + 9 + 5 + 21 + 5 = 107; R15 logs: 102 mutation crashes + 5 fixed-input crashes.** The full 102 historical mutation IDs each has a corresponding minimized witness text line in `mutation-crashes-reduced.txt` (102/102 matched). These witness lines are **not the original full mutated source bytes**. The Git tree has no individually named `mutation-15-*.sm` file.

## Which exact fixed inputs are absent?

- **`parens-unclosed-100000`: MISSING as an R17 crash-corpus generator pattern.** R17 generates deeply nested *balanced* parentheses, not the original unclosed expression. R15's fuzzer retains a generator recipe, but R17's runner does not cover that exact shape.
- **`braces-100000`: MISSING as the original raw nested-braces pattern.** The R15 fuzzer builds a `mukhya()` followed by 100,000 bare nested braces. The R17 runner's `braces` function instead builds 100,000 nested `yadi (1)` blocks. Both test depth, but they are different inputs.
- **`parens-100000`, `unary-minus-100000`, and `call-depth-100000`: SOURCE-TEMPLATE EQUIVALENTS PRESENT** in R17's generated depth cases. This is a source comparison, not a fresh native compiler run.

**Thus 102 non-individually-pinned original mutations + 2 absent fixed-source patterns = 104 original inputs without exact per-input regression coverage.** That statement does not mean those 104 causes are unprotected; all six failure kinds have at least one regression representative.

## Reproducible exact identifier inventory

[ROUND-87-WS2-ORIGINAL-CRASH-GAPS.json](ROUND-87-WS2-ORIGINAL-CRASH-GAPS.json) enumerates **all 107** old crashing input IDs, the five fixed-input template decisions, the 102 reduced-witness log line numbers and display strings, R15 report Git blob identities, and the input-coverage limitations. It is machine-readable and can guide Sarvam in adding cases without guessing what was originally found.

The log's reduced text must not be treated as byte-identical source without reconstruction and compilation, particularly for any flattened separator characters. The original full mutated byte streams were not committed individually. A new fuzzer run with modified `examples` or `fuzz_valid` may not reconstruct exact R15 streams even with the same seed.

## Next action for Sarvam (without overlapping Claude)

1. Add the **two original R6 shapes** as review-only generated negative regressions, matching R15's fixed-case recipes; test them on the current native compiler under time/memory limits and verify exit 1, diagnostic, no output binary.
2. Retain the current nine committed R1–R5 fixtures and twelve R6 generated tests (21 cases), which prior maintainer evidence reports passing on Linux. Do not claim an independent rerun here.
3. Decide whether to curate the 102 reduced mutation witnesses into stable, SHA-pinned additional cases. For each, independently reconstruct exact source, test the expected diagnostic/rejection, and include it only after validation. Avoid flooding the accepted suite with many semantically duplicate reductions.
4. Do not edit the strict R70 manifest just to merge categories; its validator intentionally requires the prior six R70 groups.

**Executed here:** GitHub source inspection, exact crash-ID count and red-log ID cross-match. **NOT_RUN:** native Sutram compiler, regenerated 100,000-depth programs, Linux/Windows acceptance. **No compiler, existing negative-test runner, golden, or language pack changed.**

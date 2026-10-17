# Round 71 — specification evidence and pending characterization

This adds an evidence ledger; it does not silently turn new expected-output
files into accepted language guarantees. `SPECIFICATION.md` gains only two narrow, existing-test-backed clauses.
No historical golden was rewritten.

## Existing test-backed clauses carried forward

The accepted `89_b9_short_circuit.sm` and its existing output pin the conditional
right-hand-side effects of `&&` and `||`, including normalized 0/1 results in
those examples. They do not prove ordinary argument evaluation order.
The accepted `65_char_code_index.sm` and its `90` output pin
`aksharank("AZ", 1)` selecting the second ASCII byte. They do not specify
Unicode grapheme indexing or normalization. These are inherited test-backed
clauses, **not new executions performed during R71**.

## Newly documented existing-test-backed cases

The specification now pins the particular effectful index read from example 140:
its mutation is observed by the indexed load (10.500000, then 9.000000 and
7.500000). It does not prove universal expression order or exactly-once effects.
Example 112 pins integer-kosh conversion of 2.9 tak 2 and 4.8 tak 4; it does not
prove every scalar, negative or out-of-range conversion rule. Their exact
source and golden captures match the GitHub blob IDs in
`tests/r71/existing_semantics.json`. These are inherited expectation contracts,
not compiler executions performed in R71.

## New probes, not yet promoted tak normative rules

| Probe | Candidate phal being tested | Current status |
|---|---|---|
| `associativity.sm` | `20-5-3` = 12; `100/10/2` = 5; `29%8%3` = 2; `1 << 2+1` = 8 | Full compiler run pending |
| `evaluation_order.sm` | side-effect stamps expose left-tak-right ordinary expression and three-argument evaluation | Full compiler run pending |
| `conversion.sm` | 2.75 tak integer = 2; -2.75 = -2; mixed phal = 2.500000 | Full compiler run pending |
| isolated pack-resolution cases | local `lang/` beats HOME fallback; HOME works after local removal; explicit CLI pack beats `SUTRAM_LANG` | Full compiler run pending |

The resolution runner creates its own temporary CWD/HOME and two deliberately
contrasting pack mappings. It never modifies user-installed packs. The inspected
`try_load_lang` source checks the local path before HOME, but this source
observation alone is not reported as new executable proof.

Run `tools/r71_native_acceptance.py` against an explicit compiler. Its negative
profile checks require successful positive controls first. Unexpected failures,
wrong output, crashes and an executable left by rejected input fail the run;
rejected programs are never executed. `--validate-only` reports NOT_RUN.

Only after the actual report passes should a reviewer promote the **specific
covered cases** into the specification. Do not infer all associativity levels,
all conversions, all pack conflicts, or every evaluation context from this
small sangrah. NaN/infinity/subnormal behavior, out-of-range conversions, normalization,
confusable identifiers and wider ordering cases remain unspecified by this work.

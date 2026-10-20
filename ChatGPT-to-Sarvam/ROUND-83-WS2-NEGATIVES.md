# Sutram Round 83 — WS2: diagnostic-to-negative-test traceability

## Real source inventory, exact 128-key scope

Read current `tools/sandesh.py` compiler `KEYS` and IDE `IDE_KEYS` from pinned Git commit `9bff1dd63877ac2c15ccd76a25153fe3c01ef015`: **105 compiler messages + 23 IDE messages = 128 keys**. Extracted default message fragments from `lang/sanskrit.sandesh` comments (128 found) and read all nine already checked-in `tests/sandesh/expect/default/*.out` fixtures: `arity, duplicate, kosh_empty, missing_module, ok, oob, parse, undefined_name, unknown_field`.

Published full per-key 128-row inventory [ROUND-83-WS2-COVERAGE-OBSERVED.json](ROUND-83-WS2-COVERAGE-OBSERVED.json) with the following status categories, deliberately conservative:

| Classification | Count | Precise meaning |
|---|---:|---|
| `CHECKED_IN_EXPECTATION_CANDIDATE` | 20 | Default message fragment found in an existing expected-output file; not newly executed and some fragments are generic |
| `PROBE_AVAILABLE_NOT_VERIFIED` | 9 | Existing test source or new draft fixture could trigger the label, native exit/output still unverified |
| `NON_SOURCE_CLI_OR_SHELL` | 8 | Command invocation, input opening, pack loader or interactive shell; not a diagnostic triggered solely by a `.sm` program |
| `NON_SOURCE_IDE_MESSAGE` | 23 | IDE status/output, not from a `.sm` source program |
| `UNMAPPED_NEEDS_REPRO` | 68 | No adequately proven source trigger found in this inventory; **not** a claim of dead/unreachable compiler code |

The 20 hits across nine goldens are *candidate matches* based on literal text; for example short generic `Sanket: '` fragments can match more than one output. Do not present 20 label triggers as 20 independently proven native cases.

## New concrete proposed programs

Review [draft PR #50](https://github.com/dap2810/Sutram/pull/50), isolated from accepted goldens:
- `tests/r83/cases/empty_kosh_peek.sm`, expected message label `msg_kosh_peek_empty`
- `tests/r83/cases/empty_kosh_dequeue.sm`, expected message label `msg_kosh_dequeue_empty`
- `tests/r83/cases/setchar_bad_arity.sm`, expected label `r50_msg_setchar_arity`

Also identified existing programs `tests/r52_check/char_at_bad_arity.sm`, `char_code_bad_arity.sm`, `dvaram_bad_arity.sm`, `tests/r55_check/prototype_duplicate.sm`, `tests/r56_check/duplicate_global.sm` and `examples/69_undefined_function.sm`, without inventing new goldens.

Delivered `tools/r83_diagnostic_coverage.py` and `tests/r83/test_diagnostic_coverage.py`. It regenerates all 128 inventory rows from a full checkout, fails on missing candidate paths, and refuses to treat an unmapped label as unreachable. **Python fixture tests and native compiler execution NOT_RUN** here.

## What remains

Sarvam should execute:
```sh
python3 -m unittest discover -s tests/r83 -p 'test_*.py' -v
python3 tools/r83_diagnostic_coverage.py --repo . --report /tmp/r83-coverage.json
./sutram_compiler tests/r83/cases/empty_kosh_peek.sm /tmp/r83-peek.elf
./sutram_compiler tests/r83/cases/empty_kosh_dequeue.sm /tmp/r83-dequeue.elf
./sutram_compiler tests/r83/cases/setchar_bad_arity.sm /tmp/r83-arity.elf
```
A generated runtime binary must then be executed with an appropriate bounded timeout and exit/stderr captured. Parse errors can occur at compilation; do not assume all three behave the same way. Only add accepted goldens after a real independent check. Reconcile all 68 unmapped compiler labels with exact emitting callsites and negative examples; label true environment/CLI-only/unreachable messages with line-number evidence. Full one-trigger-or-proven-not-source coverage is **INCOMPLETE**, not represented as achieved.

**No tests were auto-merged into `main` and no accepted golden modified.**

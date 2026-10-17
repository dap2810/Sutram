# Sutram Round 64 — kosh-empty diagnostic names (source review)

This is a source-level patch. The assistant could not run the whole NASM
compiler or genuine Windows desktop/GUI acceptance; independent native
tests are mandatory before merge.

## Change

All three operations continue tak use the original shared runtime
empty-length guard. The compiler selects an AST error varna before
emission based on builtin ID in r12:

| Operation | Diagnostic |
| --- | --- |
| kosh_pop | Sutram Error: kosh pop from empty mala (UNCHANGED) |
| kosh_peek | Sutram Error: kosh peek from empty mala |
| kosh_dequeue | Sutram Error: kosh dequeue from empty mala |

The runtime trap, nonzero exit, FIFO shift, binary64 preservation, and
peek non-mutating behavior are unchanged. No extra runtime branch is
introduced. No accepted tests/expect goldens were modified.

The R63 native harness's two diagnostic substring expectations are
updated tak match the explicit R64 semantic change. A new R64 native
harness also asserts the unchanged legacy kosh_pop diagnostic, correct
nonzero exit, and positive-case exact stdout.

## Independent Linux reproduction

    nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/sutram-r64.o
    ld -o /tmp/sutram-r64 /tmp/sutram-r64.o
    python3 tools/r64_source_gate.py
    python3 tools/r64_kosh_diagnostic_acceptance.py --compiler /tmp/sutram-r64
    python3 tools/r63_kosh_acceptance.py --compiler /tmp/sutram-r64
    python3 tests/run_tests.py
    python3 tools/codegen_gate.py
    python3 tools/test_lang_packs.py
    python3 -m unittest discover -s tests/module_graph -p 'test_*.py' -v
    python3 tools/proof_lib.py --compiler /tmp/sutram-r64
    python3 tools/proof_props.py --compiler /tmp/sutram-r64
    python3 tools/r58_codegen_baseline.py
    python3 tools/r59_codegen_baseline.py
    python3 tools/check_workflow_triggers.py
    python3 -m unittest discover -s tests/ci -p 'test_*.py' -v

Build the accepted main parent as /tmp/sutram-before, then run:

    python3 tools/r64_kosh_diagnostic_acceptance.py --compiler /tmp/sutram-r64 --before /tmp/sutram-before

The default_compat.sm native binary must be byte-for-byte identical
before/after. This is not yet an observed phal.

## Remaining Round 64 workstreams

WS1 genuine standard-user Windows compiler, installer and screenshot:
NOT RUN. Execute R62 staged acceptance and visually inspect screenshot.

WS2 both deferred peepholes: NOT IMPLEMENTED, no instruction-count
improvement claimed.

WS3 opt-in overflow/zero-divisor trapping: NOT IMPLEMENTED; preserving
intentional wrapping and checked/saturating arithmetic takes priority.

No workflow changes, library modifications, accepted golden rewrites,
new network access, admin rights, or GUI colour changes.

# Sutram Round 63 — native typed `kosh` compiler builtins (source-level partial)

## Scope and evidence discipline

This review branch implements **five of five** container builtins requested by Sarvam/Muse. They are *pure NASM compiler changes*, no runtime dependency and no library edits. **Not yet compiled or executed on Windows or Linux in this ChatGPT session**; no claim of native correctness, timing improvement, release readiness, full regression gates or compiler acceptance. Preserve every existing frozen codegen baseline until verified against a built compiler; if the source legitimately changes any image, propose the new hashes separately, never overwrite accepted baselines.

| Operation | Input | Result | Implementation |
|---|---|---|---|
| `kosh_clear(k)` | typed integer or float `kosh` variable | `0` | Set header qword at `ptr-16` (length) to zero, do not change `ptr-8` capacity or allocate/free |
| `kosh_empty(k)` | typed integer or float `kosh` variable | `1` if length zero, else `0` | Load header len, `test`, `sete`, `movzx` |
| `kosh_peek(k)` | typed integer or float `kosh` variable | Last element by value, without removing | Reuse `kosh_pop` type/bounds path but omit `[r8-16]` length store; preserve binary64 typing |
| `kosh_enqueue(k,value)` | typed integer or float `kosh` variable | New length | Builtin-token alias of existing `kosh_push`; append/grow logic and parameter growth restrictions unchanged |
| `kosh_dequeue(k)` | typed integer or float `kosh` variable | First (oldest) element by value | Reuse empty bounds-check; return head from `[r8]`, decrement hidden length, shift `len-1` elements one qword toward front with `cld; rep movsq`; O(n), FIFO. Binary64 return typed |

`kosh_clear` intentionally resets the **logical length only**, not the historical qword storage: normal kosh indexing is bounds-checked against length, and the hidden allocation/header remain retained for reuse. Caller must not assume cryptographic erasure of previous values; storage zeroing would be a separate feature. `kosh_peek` on empty arrays shares the preexisting `kosh_pop` diagnostic (currently says "kosh pop from empty array") and terminates with nonzero exit. Source detects non-kosh arguments and wrong builtin arity at compilation. Float `kosh_peek` is passed through `expr_is_float` so `dasham` result representation is preserved.

All changes are at **compiler time prior to emitting the instruction bytes**, and existing `kosh_pop` runtime instructions are not changed: the compiler dispatches to the old pop path or new peek path before writing the length store. No post-emission modification of branch or RIP offsets. The `kosh_enqueue` alias uses the original growable append implementation. `kosh_dequeue` is NOT a `kosh_pop` alias: it preserves FIFO order by shifting the remaining qwords left. The generated copy instructions were independently encoded and disassembled using GNU `as --64` and `objdump` on Linux (`49 8B 00; 49 FF C9; 4D 89 48 F0; 4C 89 C7; 49 8D 70 08; 4C 89 C9; FC; F3 48 A5`). This proves the instruction bytes, NOT full native compiler or test execution.

**Danda regression:** The source compiler's existing Devanagari `।` and `॥` lexer code remains unchanged. New `tests/r63_check/indic_danda_regression.sm` deliberately puts both danda kinds immediately after identifiers/expressions to catch the earlier `0xE0` collection bug.

## Reproduce on a Linux x86-64 build host (after source review)

```bash
nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/sutram-r63.o
ld -o sutram_compiler /tmp/sutram-r63.o
python3 tools/r63_kosh_acceptance.py --compiler ./sutram_compiler

# Optional A/B: a pinned *pre-R63* native compiler, where the new
# builtin names should fail at compile time.
python3 tools/r63_kosh_acceptance.py --compiler ./sutram_compiler --before ./pre_r63_compiler

# Mandatory original gates, record actual stdout and any legitimate hash changes:
python3 tests/run_tests.py
python3 tools/codegen_gate.py
python3 tools/test_lang_packs.py
python3 -m unittest discover -s tests/module_graph -p 'test_*.py' -v
python3 tools/proof_lib.py --compiler ./sutram_compiler
python3 tools/proof_props.py --compiler ./sutram_compiler
python3 tools/r59_codegen_baseline.py
python3 tools/r58_codegen_baseline.py
# R57 codegen hash must be tested against the PRE-R58 compiler,
# not blindly against a newer optimizing compiler:
# SUTRAM_COMPILER=<pinned_R57_compiler> python3 tools/r57_codegen_baseline.py
python3 tools/check_workflow_triggers.py
python3 -m unittest discover -s tests/ci -p 'test_*.py' -v
```

Run the corresponding R55/R56/R57/R58/R59 native acceptance gates and compare emitted instructions/hashes before acceptance. The new `tools/r63_kosh_acceptance.py` runs five exact-output positive programs, two expected compile errors, two expected runtime empty traps (peek and dequeue), and optional pre-R63 compiler name-rejection A/B. Tests are **provided but not executed** in this environment.

## Workstreams 1–3 not completed

Round 63 Windows compiler/installer/GUI acceptance remains **NOT RUN**: no genuine standard-user Windows desktop or inspected screenshot is available here. This branch does **not** mark `R61_PE_NORMAL_SIZE`, `R61_WINDOWS_COMPILE_EXECUTE_PASS`, wizard success, per-user HKCU/shortcut icon, shell `>>>` or GUI token colours accepted.

Remaining R59 peepholes **NOT IMPLEMENTED**: no proof yet for runtime push/pop pair cancellation or adjacent slot store+reload beyond the accepted self-assignment path. No x86-64 instruction-count A/B or timing claimed.

The automatic compiler arithmetic overflow/zero-divisor traps **NOT IMPLEMENTED**: accepted R18 library `ganita_checked_* / ganita_sat_*` add/sub/mul implementations can themselves perform an overflow *before checking it*, and the accepted `tests/stdlib/ganita_checked.sm` intentionally wraps `max + 1`. A blanket default trap would break both correctness and frozen tests. Safer path: opt-in checked compilation with explicit runtime diagnostic and new tests, plus independently reviewed library prechecks by Muse; do not silently change default semantics. Absolutely no `lib/*.smlib` changed here.

## Safety

No elevation, admin, HKLM, credentials, OS security changes, or new network access. No workflow added; no CI triggered. Existing GUI colour values, compiler backend golden files, and Devanagari lexer kept unchanged. Source is a **draft PR only** pending Sarvam review and native A/B execution. Handoff to `ChatGPT-to-Sarvam/` is **docs-only on main**.

**Still unverified:** Complete NASM compiler assembly and native stdout must be run before Sarvam accepts the five builtins. A disassembled isolated `rep movsq` instruction sequence is not a complete acceptance run. `kosh_dequeue` leaves physical storage in the now-out-of-bounds trailing slot untouched, consistent with logical `kosh_clear` semantics.

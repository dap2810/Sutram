# ROUND-41 — bounds guard installed, whole files only

**Base:** `origin/main` at `be5b856f` (R116; round written against v350).
**Environment:** Linux x86-64 (this VM), nasm 2.16.03, Python 3.12.
PASS / FAIL / NOT-RUN separately throughout.

## WS1 — install the bounds guard, whole files only

Everything below is in `Muse-to-Sarvam/round41-whole-files/`. No diff is
needed; copy each file to its target, in order.

### The compiler — complete new `src/sutram_compiler.asm`, in 7 parts

The file is 601,909 bytes, which exceeds the single-upload limit of the
tool I use to deliver files, so it ships as 7 parts that concatenate
byte-identically. Concatenate in order, then verify:

```
cat sutram_compiler.asm.part1 sutram_compiler.asm.part2 \
    sutram_compiler.asm.part3 sutram_compiler.asm.part4 \
    sutram_compiler.asm.part5 sutram_compiler.asm.part6 \
    sutram_compiler.asm.part7 > src/sutram_compiler.asm
```

- Concatenated SHA-256 (verified here, and verified again after a fresh
  concatenation from the delivered parts):
  `d2d2f64b0238054d6e92b5815630f8107aeb87e8275de4735598e1b9b5db21b7`
- Part sizes: 99,934 / 99,984 / 99,983 / 99,945 / 99,987 / 99,997 / 2,079
  bytes. Each part ends at a newline, so concatenation is exact.
- Target: `src/sutram_compiler.asm`, mode 644.
- Content: current main's compiler plus the R38 guard only — the
  `r38_mark_alias` helper and its two call sites (declaration alias and
  assignment alias). Nothing else changed; verified by diff against main.
- After installing, rebuild with `gates.sh` (it rebuilds
  `sutram_compiler` from source). The rebuilt binary here is 424,920 B
  (was 424,568 B). Do NOT copy a binary through the API.

### The nine test files

| Whole file | Target path | Mode |
|---|---|---|
| `251_r38_alias_mala_oob.sm` | `examples/251_r38_alias_mala_oob.sm` | 644 |
| `252_r38_alias_kosh_oob.sm` | `examples/252_r38_alias_kosh_oob.sm` | 644 |
| `253_r38_alias_slice_oob.sm` | `examples/253_r38_alias_slice_oob.sm` | 644 |
| `251_r38_alias_mala_oob.out` / `.exit` | `tests/expect/251_r38_alias_mala_oob.out` / `.exit` | 644 |
| `252_r38_alias_kosh_oob.out` / `.exit` | `tests/expect/252_r38_alias_kosh_oob.out` / `.exit` | 644 |
| `253_r38_alias_slice_oob.out` / `.exit` | `tests/expect/253_r38_alias_slice_oob.out` / `.exit` | 644 |

Each `.out` is exactly `Sutram Error: mala ank seema atikram` + newline;
each `.exit` is exactly `1` + newline. These are the same files as the
R39 whole-file delivery, byte-identical — they were never installed, so
they are delivered again here rather than assumed present.

### Document edits — now valid, apply with the guard

In R40 I refused the 218 → 221 table because the tests and compiler were
not installed. With this delivery installed, the table is true, so it
follows in full (exact match, 5 files, 10 lines):

| File | Old line (exact) | New line (exact) |
|---|---|---|
| `PROJECT-MASTER.md` | `\| Gates (\`tools/gates.sh\`) \| **34 PASS, 0 FAIL, 1 NOT-RUN** (Windows execution) \|` | `\| Gates (\`tools/gates.sh\`) \| **37 PASS, 0 FAIL, 1 NOT-RUN** (Windows execution) \|` |
| `PROJECT-MASTER.md` | `\| Regression suite \| **218 pass, 4 no-expectation** \|` | `\| Regression suite \| **221 pass, 4 no-expectation** \|` |
| `PROJECT-MASTER.md` | `python3 tests/run_tests.py                        # expect PASS=218 NO-EXPECTATION=4` | `python3 tests/run_tests.py                        # expect PASS=221 NO-EXPECTATION=4` |
| `PROJECT-OVERVIEW.md` | `python3 tests/run_tests.py          # 218 pass, 4 no-expectation` | `python3 tests/run_tests.py          # 221 pass, 4 no-expectation` |
| `PROJECT-OVERVIEW.md` | `\| Regression suite \| **218 pass, 4 no-expectation** \|` | `\| Regression suite \| **221 pass, 4 no-expectation** \|` |
| `docs/sutram-design-parameters.html` | `working ones. <b>Today:</b> the gates are real and enforced — <b>218 pass / 4 no-expectation</b>,` | `working ones. <b>Today:</b> the gates are real and enforced — <b>221 pass / 4 no-expectation</b>,` |
| `docs/sutram-design-parameters.html` | `Status is measured against the compiler as tested: <b>218 pass / 4 no-expectation</b> · codegen 12/12 ·` | `Status is measured against the compiler as tested: <b>221 pass / 4 no-expectation</b> · codegen 12/12 ·` |
| `docs/sutram-project-status.html` | `<td class="ok">218 pass · 4 no-expectation</td></tr>` | `<td class="ok">221 pass · 4 no-expectation</td></tr>` |
| `docs/sutram-scorecard.html` | `Compiler source blob 7db83d38 (v246) &middot; suite 218 pass, 4 no-expectation &middot; 24 library modules (305 functions) &middot; 32 keywords<br>` | `Compiler source blob 7db83d38 (v246) &middot; suite 221 pass, 4 no-expectation &middot; 24 library modules (305 functions) &middot; 32 keywords<br>` |
| `docs/sutram-scorecard.html` | `<li><strong>Tests:</strong> 218 passing, including a deterministic codegen gate (12/12) that asserts instruction ceilings and loop shape.</li>` | `<li><strong>Tests:</strong> 221 passing, including a deterministic codegen gate (12/12) that asserts instruction ceilings and loop shape.</li>` |

## WS2 — re-measured, with the guard installed (not assumed)

Measured on current main + the whole files above installed locally,
guard compiler rebuilt from source, nasm on PATH:

- **Gates:** `sh tools/gates.sh` → EXIT=0, **PASS 37, FAIL 0, NOT-RUN 1**
  (Windows execution). Regression suite gate: NO-EXPECTATION=4 PASS=221.
  Doc signatures: 24 modules, 305 signatures, 0 mismatches. Stale claims:
  117 documents, 166 hits (gate passes; hits are review items, not
  failures, per R38).
- **Suite:** `python3 tests/run_tests.py` → **NO-EXPECTATION=4, PASS=221**
  (218 old + 3 new alias tests, 0 FAIL).
- **Library proofs:** `proof_lib` → **224 passed, 0 failed, 224 total**.
- **Properties:** **86/86 properties hold**.
- **Crash corpus:** **227 cases + manifest, 0 failed**.

No golden was updated or silently changed.

## WS3 — the guard: this round's number

Method (as in R40): committed binary vs fresh build, every `.sm` in
`examples/`, `tests/stdlib/`, and top-level `tests/r*/`, compiled from
the repo root, comparing executable bytes + compiler stdout/stderr +
exit status, with `--lang` per pack for the six pack examples.

- **Old committed binary vs guard compiler, 573 programs: 483
  byte-identical executables, 87 refused identically, 3 DIFFER.**
  The 3 DIFFER are exactly the 3 new alias tests — their generated
  binaries change because the guard adds the bounds check. That is the
  intended change, not a regression: no pre-existing program differs.
- **Guard compiler vs a fresh guard build, 573 programs: 486
  byte-identical, 87 refused identically, 0 DIFFER.** The fresh build is
  byte-identical to the working guard binary.
- Your WS3 figure of 476 byte-identical is not the Linux number; the
  Linux numbers this round are 483 (old vs guard, 3 intended DIFFER)
  and 486 (guard vs guard, 0 DIFFER).

## Delivery

- This report: `Muse-to-Sarvam/2026-10-27-round41-guard-whole-files.md`
- Whole files: `Muse-to-Sarvam/round41-whole-files/` (9 test files + 7
  compiler parts, 16 files total)
- `git push` has no credentials here, as before; delivery via the GitHub
  API as usual. The local tree was reset to main after measuring, so
  these outbox files are the delivery, not the local tree.

# ROUND-43 — lexer baseline, independently measured (no fix)

**Base:** `origin/main` at `3b1a9e7f` (v361; round written against v359),
compiler **v249** (`Sutram 1.0 (v249) - sampurna sutra`).
**Environment:** Linux x86-64 (this VM), nasm 2.16.03, Python 3.12.
PASS / FAIL / NOT-RUN separately throughout.
**No code changes made. No fix implemented — Claude owns the fix, per the
brief. No tree files added or modified.**

Note on base: main has moved past v359 to v361, and commit `90e3d4a3`
installed the R42 bounds guard (compiler v249). The guard touches
codegen marking, not the lexer, so this is still the v249 lexer baseline.
Commit `83587b62` added `docs/reports/LEXER-BOUNDARY-TEST.md`, which already
claims the Latin cases pass; the tests below are my own programs, run
independently, and they confirm that claim — plus they answer the
Devanagari case that document left open.

## WS1 — the five questions, each with a compile and the exact output

Compiler used: the committed main binary at `3b1a9e7f`. "PASS" here
means: compiles with exit 0 and runs to the expected output (a name
that was mis-tokenised would either fail to compile or produce the
wrong value).

### Q1 — Does `prakriya vartani_pratilip(...)` compile? — PASS

Program:
```
prakriya vartani_pratilip(x) {
    prati x + 10
}
mukhya() {
    likha(0)
}
```
Compiler output: `Siddh: 215 baait sankalit`, compile exit 0.
Run output: `0`, run exit 0. **The definition compiles.**

### Q2 — Does a CALL to `vartani_pratilip(x)` compile, or is it tokenised as `prati` + `lip`? — PASS, it is a call

Program:
```
prakriya vartani_pratilip(x) {
    prati x + 10
}
mukhya() {
    vitti y = vartani_pratilip(5)
    likha(y)
}
```
Compiler output: `Siddh: 228 baait sankalit`, compile exit 0.
Run output: `15`, run exit 0. **The call compiles and executes as a
call** (5 + 10 = 15). If it had been tokenised as `prati` + `lip`,
the program would not have compiled, and it certainly would not have
printed 15.

### Q3 — Does `vitti pratiX = 1` compile? — PASS

Program (value 3, to distinguish a correct run from a default 0):
```
mukhya() {
    vitti pratiX = 3
    likha(pratiX)
}
```
Compiler output: `Siddh: 183 baait sankalit`, compile exit 0.
Run output: `3`, run exit 0. **A variable whose name starts with the
keyword `prati` compiles as one identifier.**

### Q4 — Does a Devanagari identifier beginning with a Devanagari keyword compile? — PASS (both forms)

Premise correction: the Devanagari keyword for `prati` in
`lang/sanskrit.lang` is **प्रतियाति**, not प्रति (प्रति is its prefix).
I tested both, with `--lang sanskrit`:

(a) The briefed case, identifier **प्रतिलिपि**:
```
मुख्य()
    वित्ति प्रतिलिपि = 9।
    लिख(प्रतिलिपि)।
```
Compiler output: `भाषा-पुटः प्राप्तः: sanskrit` /
`सिद्धम्: 183 बाइट् सङ्कलिताः`, compile exit 0.
Run output: `9`, run exit 0. **PASS.**

(b) The stronger case, identifier **प्रतियातिता** (full keyword
प्रतियाति + ता):
```
मुख्य()
    वित्ति प्रतियातिता = 11।
    लिख(प्रतियातिता)।
```
Compiler output: same form, `सिद्धम्: 183 बाइट् सङ्कलिताः`,
compile exit 0. Run output: `11`, run exit 0. **PASS.**

So the boundary check is character-aware, not byte-naive prefix
matching: even the full Devanagari keyword plus a suffix compiles as
one identifier. This closes the open case in `docs/reports/LEXER-BOUNDARY-TEST.md`.

### Q5 — Does `mukhyata` (keyword `mukhya` + `ta`) compile as one identifier? — PASS

Program:
```
mukhya() {
    vitti mukhyata = 7
    likha(mukhyata)
}
```
Compiler output: `Siddh: 183 baait sankalit`, compile exit 0.
Run output: `7`, run exit 0. **PASS.**

### Summary

| Question | Result |
|---|---|
| Q1 `prakriya vartani_pratilip` definition | PASS |
| Q2 call to `vartani_pratilip(x)` | PASS (prints 15) |
| Q3 `vitti pratiX` | PASS (prints 3) |
| Q4 Devanagari `प्रतिलिपि` | PASS (prints 9) |
| Q4b Devanagari `प्रतियातिता` (full keyword + suffix) | PASS (prints 11) |
| Q5 `vitti mukhyata` | PASS (prints 7) |

**Baseline for the fix: there is no lexer defect to fix in any of
these cases on v249.** `vartani_pratilip` is legal today, in Latin
and in Devanagari, as a definition, a call, and a variable. The
project's word-avoidance (`anuk` instead of `pratilip`) was avoiding
a collision that does not occur — which is exactly what Sarvam's
document said, now independently confirmed, including Devanagari.

## WS2 — the guard: this round's number

Method as in R40–R42: committed `./sutram_compiler` (from `HEAD`) vs a
fresh build from `src/r68_compiler_entry.asm` (byte-identical to the
committed binary), every `.sm` in `examples/`, `tests/stdlib/`, and
top-level `tests/r*/`, compiled from the repo root, comparing
executable bytes + compiler stdout/stderr + exit status, with `--lang`
per pack for the six pack examples.

**Current main `3b1a9e7f`: 576 programs, 488 byte-identical
executables, 88 refused identically, 0 DIFFER.**

Context, measured on the same main (not asked for, but it changed):
suite `NO-EXPECTATION=4, PASS=223` — up from 221 in R42 because the
guard tests and other new tree tests are now on main. That is tree
growth, not a lexer result. Your WS3 figure of 476 is not the Linux
number; the Linux number this round is 488, with 0 DIFFER.

## Delivery

- This report: `Muse-to-Sarvam/2026-10-27-round43-lexer-baseline.md`
- No other files. The six test programs above are reproduced in full
  in this report so they can be added to `tests/` if desired; I did
  not add them to the tree, per WS3 ("nothing else this round").
- `git push` has no credentials here, as before; delivery via the
  GitHub API. The local tree was left at main, unmodified.

# Sutram — ROUND-77: the byte-vs-qword audit, and the whitespace mutator

**Base:** main at 2bd87b55, compiler v273 (built from `src/r68_compiler_entry.asm`)
· **Deliverable:** this report + `r77_audit_nirmmita.py` + `r77_mutator.py`
(re-runnable; the audit's full JSON is in the round's working notes, the
counts below are the deliverable) · **No tree changes.**

## WS1 — how widespread is the byte-vs-qword trap?

**Answer: zero. No program in the tree writes past its block today.**

The audit covered every `nirmmita(...)` site in `examples/` (recursive),
`tests/` (recursive) and `lib/`: **405 sites** — 373 with a literal or
foldable-literal size, 32 with a variable/expression size (out of the
brief's literal scope, checked separately below).

| Verdict | Count | Meaning |
|---|---|---|
| OK | 176 | literal size ≥ (highest literal index + 1) × 8 |
| BYTE-ONLY | 47 | only byte accessors (`pad8`/`likh8`/`akshar`) touch the block |
| VARIDX | 20 | indexed by a variable — each bound checked by hand, all safe (below) |
| OPAQUE | 128 | never indexed in-file — each use reviewed by pattern (below) |
| VIOLATION (literal rule) | 2 | `nirmmita(13)` with index 1 — saved by slot rounding (below) |
| OTHER (variable size) | 32 | `n * 8`, `c * 8`, `sz`, `oldcap * 33 + 1` — the ×8 idiom throughout |

**The 2 literal-rule flags are not live overflows.** Both are in
`tests/r73_scratch/reuse_zeroed.sm`: `nirmmita(13)` with `b[0]` and `b[1]`
written — the literal rule demands 16 bytes for 2 cells, and 13 < 16.
But the bump allocator rounds every request up to a 16-byte slot (R75),
so a 13-byte request reserves 16 bytes and the two cells fit exactly.
Probe-verified: `b = nirmmita(13); b[0] = 111; b[1] = 222` followed by a
marker block leaves the marker intact (777). Effective violation count: **0**.

**The 20 variable-index sites, resolved:** 217 (`koshtha`, j < 6, 22 cells),
r11 (`x`, i < 512, 512 cells; `num`, i < 1024, 1024 cells — both exact),
r39 (`guard`, i < 1024, 1024 cells — exact, twice), r8_list_growth (`g`,
i < 4, 4 cells), r8_split_model (`s`, i < n ≤ 9, 12 cells; `parts`, ≤ 13
cells read of 40 via `dikha`), r8_text_edges (`out`, i < 8, 9 cells),
strconv_pad (`buf`, pad to width 5 + terminator, 10 cells),
string_replace (`out`, "baz bar baz" 11 chars, 30 cells),
string_split_join (`jout`, "a,b,c" 5 chars, 10 cells),
r74 c6_adjacent (`a`, i < 8 of 64 bytes — exact; `b`, j < sz/8 of sz bytes),
and three input-bounded cases — 215 (`parts`, 512 cells, and `uptrs`/
`ulens`, 64 cells) and the `set_*` dumps (`arr`, 64 cells): safe for the
shipped inputs (215's text has 11 words, 8 unique; the set tests dump 3
short strings), but the allocation is a constant, not derived from the
input length, so a longer input would overflow. Latent, not live.
One deliberate exception: `tests/guard_page/control_proof_overread.sm`
reads 16 cells of an 8-cell block on purpose — a guard-page control, and
a *read*, not a write.

**The 128 never-indexed sites, by pattern:** rachana values (`p.x`/`p.y`
field access — N = fields × 8 exactly: 24/3, 16/2, 40/5, 32/4, 8/1);
lib buffers with a matching size parameter (bigint tests: 8 cells with
n = 8; serial/anukram tests: cap 16/64 below the buffer size);
byte-string outputs far inside their buffers (fmt tests: ≤ 20 chars in
128 bytes); the negative-test mutants (field-sized); the mandapa escape
probes (address-only, never indexed); NULL/returned/address-only blocks.
No hidden violation in any pattern.

**The 32 variable-size sites** are the correct idiom, not the trap:
every cell-count size is multiplied by 8 (`n * 8`, `c * 8`, `c * 2 * 8`,
`ncap * 8`), and the byte sizes (`sz`, `oldcap * 33 + 1`) are byte counts
for byte buffers. The trap shape — a bare element count passed as bytes
— appears nowhere in the tree.

**Why the trap didn't spread:** every literal site in the tree already
writes the size in the unit the use needs — `nirmmita(64 * 8)` for 64
cells, `nirmmita(128)` for a byte string. Gemini's `nirmmita(10)` +
`p[0..9]` is a real trap for a *new* program (it compiles and runs, and
writes 70 bytes past the block into adjacent arena), but no shipped
program falls into it. The fix that would close it for new programs is
Claude's R76-00 header prototype — which his own measurement shows
cannot be made sound without fat pointers (interior pointers everywhere).
That trade-off belongs to the language owner, not to this audit.

## WS2 — the whitespace mutator, built

**The five specified mutations, over all 244 top-level examples:**
199 compile and run deterministically (two pristine runs identical);
45 fail pristine by design (capacity tests, reject tests, parse-error
tests, the mandapa escape negatives — listed in the working notes) and
are excluded. Of the 199 × 5 = 995 mutation runs:

| Mutation | SAME | No-op | Fail |
|---|---|---|---|
| M1 blank lines with spaces inside indented blocks | 198 | 1 | **0** |
| M2 `\r\n` throughout | 199 | 0 | **0** |
| M3 trailing spaces after a statement | 199 | 0 | **0** |
| M4 a `prakriya` moved above `mukhya` | 2 | 197 | **0** |
| M5 tabs instead of spaces | 198 | 1 | **0** |

M4 is a no-op for 197 examples because only two (`46_language_reference`,
`func_demo`) have a `prakriya` after `mukhya` at all — both move
preserving output exactly.

**A harness correction, disclosed:** the first run showed 10 failures,
all in multi-module examples (149–155, 163, 166, 211). They were not
parser failures: the mutator wrote mutated files to a temp directory,
so the examples' relative imports (`examples/lib/*`) stopped resolving.
Re-run with the mutated file in `examples/` beside the original, all 10
× 4 mutations give byte-identical output. The 10 are counted as SAME
above, not as failures.

**The strengthened set (what a Windows student really produces):**
BOM prefix: 199/199 SAME. Combined (`\r\n` + trailing spaces on every
line including blank lines + a space-only line inside a block): 199/199
SAME. Every blank line becoming spaces: 199/199 SAME. **Mixed tabs and
spaces for indentation: 8 failures out of 199** — and they are the
whole story of this round's parser finding (below).

### The one real failure class: mixed indentation

8 examples fail under mixed indentation (alternate indented lines
converted to tabs, the rest left as spaces). All 8 are programs whose
bodies are written by indentation, not braces: 258 (R70 loop-indent),
260 (R71 indented bodies), 263 (R72 mandapa), 266, 267, 268, 269 (R73
mandapa probes), 271 (R75 nested-store data). Uniform tabs (M5) pass
everywhere; it is the *mixing* that breaks.

Root cause: the indented-block parser measures indentation in bytes, so
a tab counts as 1 column against 4 or 8 spaces. A tab-indented line
inside a space-indented block reads as a dedent, the block ends early,
and the next statement fails with a grammar error at the tab-indented
line (258: `vyakaran dosh, pankti 9:3, shabd 'vitti'`, pointing at the
tab-indented line). It is a hard compile error, not a silent
miscompilation — no wrong output is produced — but the error points at
a line that *looks* more indented than its neighbours, which is exactly
the confusion a Windows student mixing tabs and spaces will hit. The
fix direction is a column-counted indentation (tab = 4 or 8 columns) or
a dedicated "mixed indentation" diagnostic; either belongs to the
parser's owner.

### On the "four parser defects" premise

The brief says four parser defects survived because the goldens are
clean. On v273, with the five specified mutations plus the strengthened
set, the count of silent defects is **zero** — every failure above is a
loud compile error, and every silent-skip shape I probed (below) runs
the whole program, not a wrong one. Either the four were fixed since
Gemini's finding (the src/ log since R70 is the indented-body and
mandapa work, not whitespace fixes — so I cannot attribute a fix), or
they live in shapes this mutator does not cover (e.g. indentation
inside string literals, or the import path's own line handling — the
import cluster passed in-place, so not that). I report what I measured:
0 silent failures on 199 programs × 9 mutation shapes.

## WS3 — the Devanagari variant

13 examples contain Devanagari (keywords, identifiers, or string
content): 100, 110, 122 (kosh Devanagari), 218, 219 (Sanskrit), 256
(Sanskrit names), 78, 92–95, 97, and 38 (a negative Hindi parse test).
12 run; 38 fails pristine by design (it is a parse-error test) and is
excluded. **All 12 pass all five specified mutations, BOM, the combined
mutation, every-blank-line-spaces, and mixed indentation** (none of the
8 mixed-indent failures is a Devanagari file). Multi-byte UTF-8 in an
indented block with `\r\n` endings — the exact Windows-Sanskrit-keyboard
shape — compiles and runs byte-identically on v273.

## Appendix — the `ret` claim, characterized (not reproduced as stated)

The brief's second premise: the parser exits via `ret` on an unexpected
token instead of aborting, so a program can compile and run half of
itself. I probed the shapes that could produce that, on v273:

| Input | Result |
|---|---|
| `@@@` mid-program, or before `mukhya` | silently skipped; whole program runs (1 and 2 both print) |
| `;` alone on a line; a bare `5` as a statement | silently skipped; whole program runs |
| NUL byte; Ctrl-Z mid-program | silently skipped; whole program runs |
| Bare unknown identifier (`zzzqqq`) | `E_UNDEFINED_NAME`, compile fails |
| Malformed statement (`vitti = 5`); stray `)`; bare `yadi`; `likha(1 + )` | grammar error, compile fails |
| Unterminated block comment; unterminated string | error at EOF, compile fails |
| Stray `}` closing a braced block early | grammar error at the following statement (261 rule) |

What reproduces is narrower than the claim: the lexer/parser **silently
drops** unrecognized characters and vacuous statements instead of
erroring, but it does **not** truncate the program — everything else
still runs. I found no input on v273 that compiles to a strict prefix
of the program (a true "half"). The silent-drop itself is still a
defect worth fixing (a student's typo'd line compiling away to nothing
is the same class as the trap in WS1: the program that runs is not the
program written), but it is milder than stated, and it is not what any
of the mutator failures show.

## Verification status

- Compiler v273 built from `src/r68_compiler_entry.asm`; tree reset to
  `origin/main` (2bd87b55) after the runs; no temp files left in
  `examples/` (verified by `git status`).
- Pristine determinism: every runnable example run twice, identical
  output and exit code, empty stdin, CWD = repo root, 10 s timeout.
- NOT RUN: Windows, browser, implementation (the mixed-indentation fix
  and any silent-drop diagnostic belong to their owners).

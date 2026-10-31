# R77-00 — The byte-versus-qword trap is caught; one silent-misparse class found (mixed indentation) and closed; the mutator is a gate

**I missed this brief.** It landed at 19:16 while I was finishing R76, and my R76 check of the folder happened before it. It is done now, together with R78 and R79.

- **Commits on `main`, in order:** `34e03ca` (1/4 **v274**, the byte/cell check and its goldens) · `e998745` (2/4 the
  mutator and stray-token tests and gates; the R79 program and gate; two tests corrected) · `f35252f` (3/4 the
  reference §6c and the changelog) · `d1299ee` (4/4 **v275**, mixed indentation refused) · then the three
  hand-backs. Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v275) - sampurna sutra`.** Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=244`, FAIL=0** (four new examples). Library proofs **228/228**. Property proofs **86/86**.
- **Guard pages: controls 5/5, suite PASS=244 FAIL=0, library proofs 228/228, property proofs 86/86, 0 failed.**
- **Gates (`sh tools/gates.sh`, Xvfb display): 55 PASS / 0 FAIL / 1 NOT-RUN (Windows execution)** — three more:
  **`R77 format`** (2,186 checks), **`R77 stray`** (715), **`R79 real`** (3).
- **The guard, v273 → v275, `tools/guard_pair.py`, all three paths (Linux ELF, Linux PE, the Windows compiler under
  Wine): 491 byte-identical, 120 refused identically, 35 DIFFER, 7 new.** The 35 are the programs that index a
  buffer declared `vitti p = nirmmita(NUMBER)` with a computed index — they now carry the bounds check. **I ran
  every one, old and new, ELF and PE under Wine: all 35 give the same output and exit code**
  (`evidence-r77/guard-differ-outputs.txt`).

## WS1 — the byte-versus-qword trap (also R78 WS1)

**What v274 does.** When a name is declared `vitti p = nirmmita(SIZE)`, SIZE is a number (or `+ - *` of numbers),
and `p` is **never assigned again anywhere in that function**, then `p` is known to point at the start of SIZE
bytes. For such a `p`:

| | v273 | v274 |
|---|---|---|
| **`nirmmita(10)` then `p[9] = 1`** — your golden, `examples/273` | compiles | **refused when compiled** — `Sutram Error [E_NIRMMITA_SEEMA]: pankti 5:8 - p[9] nirmmita(10) bahih` / `Sanket: nirmmita bhaita-sankhyam ganayati, p[i] ashta-bhaita-ekakaih: p[9] hetu nirmmita(80) avashyakam` — *nirmmita counts bytes, p[i] counts 8-byte units: p[9] needs nirmmita(80)* |
| `nirmmita(1)` then `p[0] = 123456` (your R77 case) | compiles | **refused when compiled** (`p[0] hetu nirmmita(8)`) |
| **the student's loop:** `nirmmita(10)`, `yavat (i < 10) p[i] = i` — `examples/274` | **ran, exit 0, 70 bytes written past the block** | **stops at `p[1]`**: `Sutram Error: mala ank seema atikram`, exit 1 |
| `nirmmita(10 * 8)`, the same loop — `examples/275` | runs | runs, prints 9 |
| `p[0 - 1]` | compiles | refused (`p[-1] - rnatmakah ankah`) |
| `p = p + 8` later in the function | — | `p` is not tracked: unchecked, works as before |
| two sibling blocks each declaring `p` with a different size | — | each `p[i]` checked against its own block's `p` |
| inside a `mandapa` | — | the same (`p[3]` on `nirmmita(3 * 8)` refused) |

**Why only those names: it is the one case with no false alarms.** R76's header traps any address into the middle
of a buffer; this check needs no header, because a name that is never reassigned *is* the allocation. **The tree
under it before it shipped: suite 240/240, library proofs 227/227, properties 86/86 — no false alarm**
(`evidence-r77/ws1-tree-under-check.txt`).

**It found a real overrun on its first run — in my own test.** `tests/r73_scratch/reuse_zeroed.sm` (R73) asked
for `nirmmita(13)` and wrote `b[1]`: 16 bytes into 13 — exactly the trap. Fixed to `nirmmita(2 * 8)`.
**And one control changed for a good reason:** `tests/guard_page/control_proof_overread.sm` exists to prove the
guard-page build catches a read past a block; v274 now stops that read itself (exit 1, before the guard page), so
the control's size is computed at run time to keep it a test of the guard page.

**Cost (`evidence-r77/ws1-cost.txt`): the 8 shipped benchmarks and the sieve compile to identical binaries — 0%.**
A tight loop that only reads a constant-sized buffer: −2% (noise). **A tight loop that only writes one: +17–19%**
— the one `cmp`/`jae` per store. Under your 20% line, and paid only where the size is a written number.

**Round-up to 8 — already done, by more:** the arena rounds every block to 16 bytes (`lea 0xf(%rdx,%rsi,1)` /
`and $-16` in the emitted code, `evidence-r75/ws1-negative-size-disassembly.txt`), the scratch side to 16, `mmap` to
a page. So an 8-byte write into a `nirmmita(10)` block already never reached the next block. **It would not have
caught your loop**, which writes 80 bytes into 16 — which is why the run-time check matters more than the rounding.

**What is still not checked** (reference §6c, rewritten): a size computed at run time, a name assigned again, an
address computed from `p`, a parameter, `likh8`/`akshar_rakh` stores — bare addresses, as in C.

## WS2 — "silent partial compilation": one class was still open — mixed indentation. Closed in v275.

**What I found first, and wrote too soon.** The structure holds for *tokens*:
- **EOF at the end of top-level compilation is asserted**, since v266 (R71): `parse_program` refuses any token
  after `mukhya`'s body.
- **Every body loop leaves only at end of input, `}`, or a dedent:** `parse_func_block` (a braceless `mukhya`),
  `r70_indent_body` (every indented body — `prakriya`, `yadi`, `yavat`, `chakra`, `kuru`, `mandapa`, `anya`), and
  `parse_block` (braces).
- **Every other token goes to `parse_stmt`**, which refuses what it cannot parse. An unmatched `}` is refused at
  its own line and column.

`tests/r77_format/test_stray_tokens.py` (gate **`R77 stray`**, 715 programs) puts 45 stray tokens into 14 kinds
of body, and 17 more at the ends of lines, as a body's first line, and after a header. **No token is dropped.**

**But a token can be put in the wrong body, and that is the same danger.** Muse's R77 mutator (`9f9f943`, pushed
while I worked) mixed tabs and spaces and got 8 confusing compile errors. I tried the reverse mixing, a body
indented with tabs under a header indented with spaces:

```
mukhya()
    vitti c = 0
    yadi (1 == 2)          <- four spaces
<tab>c = c + 1             <- read as the yadi's one-statement body
<tab>c = c + 10            <- ran unconditionally
    likha(c)
```

**v273 and v274 compiled it and printed 10, not 0.** A tab counted as one column, which is less than four spaces,
so the body was "not deeper" than the header. **Exactly Gemini's case:** the compile succeeds, the program does
less than it says, and a beginner blames themself. In the tree itself, `examples/275` under Muse's mutation
**compiled and hung**: a loop's body had been cut in two.

**v275 closes it with Python's rule.** Two indentations are compared only if one line's leading whitespace begins
with the other's. Otherwise the compile stops at that line with `Sutram Error [E_ANTARAL_MISHRA]: pankti 4:2 -
pankti-arambhe tab space cha mishritau ...` / `Sanket: ekasmin khande sarvatra tab athava sarvatra space - ekam
eva upayujyatam`, meaning *tabs and spaces are mixed at the start of this line; use one or the other throughout a
block.* All three of my mixed cases are refused (`evidence-r77/mixed-indentation.txt`), and so are Muse's 8
(now with this message, at the mixed line). `examples/276` is the golden. **No valid program's binary changed:
the guard's 35 DIFFER are all from WS1.**

**So the claim, stated carefully:** after v275, no token is dropped (715 stray programs), and a token cannot land
in a different body because of how whitespace was typed (2,186 mutated programs, below). That is what I can test.
It is not a proof that no other parser class exists.

## WS3 — the mutator, built: **2,186 checks, 0 failed**

`tests/r77_format/test_format_mutator.py`, gate **`R77 format`**: every example with a golden, saved nine ways —
**CRLF** line endings; **trailing spaces and a tab** on every line; after every indented line **a line of only
spaces and a line of only a tab**; **tab indentation** (each 4-space step one tab); **no final newline**;
**three extra blank lines** at the end; **a UTF-8 byte-order mark** (Windows Notepad writes one); and, **added after Muse's R77 and my reverse case,
mixed tabs and spaces two ways** (every other line in tabs; bodies two levels deep in tabs under headers in
spaces). Each must compile and give the golden's output and exit code; a refusal golden must still be refused;
under the mixed mutations a refusal with `E_ANTARAL_MISHRA` is also right. **All 2,186 pass on v275. On v273
the same harness fails 9 programs under mixing: 8 refused with confusing errors, and one that hangs**
(`evidence-r77/r77-format-mutator-on-v273.txt`; the other v273 failures are the three new byte goldens, as
expected). I checked
the harness can fail: CRLF really reaches the file (103 `\r\n` in one example), and a body line moved between its
header's indentation and the body's is refused.

The one mutation in your list I did not make: **"a `prakriya` moved above `mukhya`"** — every example's `prakriya`
already is above `mukhya` (a braced `mukhya` may have nothing after it since v266; a braceless one runs to the end
of the file, so a `prakriya` after it is *inside* it — documented, R71).

## WS4 — your process change

Seen; R78 and R79 carry the `## Verified behaviour` block. One correction to it below (R78-00).

## What I did not do

- **No bounds check for computed sizes** (`nirmmita(n)`): it would need the size kept at run time beside every such
  name — a hidden local per buffer. Possible, not built.
- **Not run:** real Windows (Wine only).
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`.

**Document counts:** `doc_counts_gate` NOTEs (`evidence-r77/doc-counts.txt`): the suite is now 243, gates 55,
library proofs 228, functions 306 — `PROJECT-MASTER.md` and five other documents still carry older numbers.

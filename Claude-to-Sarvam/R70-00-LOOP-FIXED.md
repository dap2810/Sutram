# R70-00 — The loop is fixed. It was not the allocator: an indented body was one statement.

- **Commits on `main`, in order:** `f947ce9` (1/3: the parser, **v265**) · `f7fc23c` (2/3: the formatter) · `1a98f09`
  (3/3: the tests) · then this hand-back. Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v265) - sampurna sutra`.** Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=227`, FAIL=0** (two new examples). Library proofs **226/226**. Property proofs **86/86**.
- **Guard pages: controls 5/5, suite PASS=227 FAIL=0, library proofs 226/226, property proofs 86/86, 0 failed.**
- **Gates (`sh tools/gates.sh`, Xvfb display): 49 PASS / 0 FAIL / 1 NOT-RUN (Windows execution).**
- **The guard, v264 → v265, `tools/guard_pair.py`: 577 programs, 486 byte-identical, 91 refused identically,
  0 DIFFER — on Linux ELF, Linux PE, and the Windows compiler under Wine** (the Wine run also saw the two new
  examples as `2 new`). The fix changes no existing program, because no program in the tree wrote what it fixes.

## What the bug is — confirmed by reading the bytes, as you asked

**Your program loops forever on v261 too** — before the arena existed (`evidence-r70/repro-four-compilers.txt`:
v261, v263, v264 all print `i=0` forever). So the arena could not be the cause, and the register hypothesis does
not apply: nothing is clobbered.

**The disassembly of your program on v264** (`evidence-r70/v264-disassembly.txt`): `i` lives in `rbx`. The loop
runs from `0x97` to `0x140`: its body is **`likha("i=", i)` only**, then `cmp rax,3 ; jl 0x97`. **The `nirmmita`
sequence starts at `0x146` — after the loop — and `i = i + 1` after it.** The increment was never in the loop.

**Why:** before R70, a `yavat`/`yadi`/`anya` body without `{` was **one statement**, whatever the indentation
said — C's rule (`parse_body`, `src/sutram_compiler.asm`). **Nothing in the lexer or the parser ever read
indentation.** A braceless `mukhya()` body is "every statement until the end of the file", which is why
whole-program indentation *looked* like it worked.

**Your isolation table, explained** (`evidence-r70/isolation.txt`, re-run on v264 and v265):

| your row | what was really happening |
|---|---|
| `nirmmita` inside `yavat`: `i=0` forever | the loop body is the `likha`; the increment is after the loop |
| inside `yadi`: works | a one-statement body was all you needed there |
| after the increment: runs once, prints `i=3` | the loop body is `i = i + 1` alone: it counts to 3, then the rest runs once |
| 1,000 / 1,000,000 allocations never finish | the counter is outside the loop — infinite loops, not slow allocation |
| **(added) no allocation at all, `vitti q = i + 7`** | **the same infinite loop** — allocation is irrelevant |
| **(added) the same program with braces** | **works on v264** |

**Why no gate saw it:** no program in the tree writes a braceless multi-line body. Every `yavat` and `yadi` in
577 programs uses braces; the 41 examples without `{` only omit them on `mukhya()`. *(`MEMORY-DECISION.md`'s
"203 of the 229 examples use no braces at all" is not what the tree contains — reported, not edited.)*

## 1. The fix — `parse_body`, v265

**The rule the documents already describe, now in the compiler:** when a body does not open with `{` and its
first statement starts on a **later line, indented deeper than the header line**, the body is **every following
statement at that indentation**, ending at the first line indented less (or at `}` / end of input).

- **A line indented less than the body but more than the header is refused** — it is in neither place, and
  silently choosing one is exactly the bug. It is reported as a syntax error at that line:
  `Sutram Error: vyakaran dosh, pankti 7:9, shabd 'i'`. *(A specific message would need a new `sandesh` entry; I
  used the existing syntax error. Say if you want a dedicated one.)*
- **A body on the header's own line is still one statement**: `yadi (k == 4) likha("k=4")`.
- **A body on the next line but not indented deeper is still one statement**, as before.
- **Spaces and tabs count one column each.** Nested indented blocks, `anya` at the header's level, and `vitti`
  declared inside the block (scoped to it, as with braces) all work. ~110 lines in one place.
- **Braces still work exactly as before** — the guard shows every existing program is byte-identical.

**This is a language change, and I took it as decided:** `MEMORY-DECISION.md` says braces are optional and
shows `mandapa` as an indentation block; your program was written that way. If you would rather keep C's rule,
the other fix is to *refuse* a braceless header followed by deeper-indented lines — same detection, an error
instead of a block. One-line switch.

**The formatter had the old rule built in.** `tools/sutram_fmt.py` would have "reformatted" your program to show
the `likha` alone inside the loop — making the wrong meaning look right. It now opens an indented body by the
compiler's rule (2/3). The whole tree is still `FORMATTED`; `--verify` shows the formatter keeps the compiled
binary byte for byte on the new example and on a deliberately mis-indented program.

## 2. The tests that would have caught it — `examples/258`, `examples/259`

- **`examples/258_r70_loop_indent.sm`** (golden): your program verbatim → `i=0 i=1 i=2 done`; allocation after
  the increment → `1 2 3`; an indented `yadi`/`anya` nested in an indented loop; a same-line body; **1,000
  allocations in a loop, each written, `n=1000 s=499500`**.
- **`examples/259_r70_indent_ambiguous.sm`** (compile-fail golden): the ambiguous dedent is refused.
- **Both fail on v264** (258 by timeout — the loop never ends). Both pass on v265.

## 3. Re-run: guard pages, suite, benchmarks

- **Guard-page gate:** controls 5/5, suite PASS=227 FAIL=0 (the two new examples included), library proofs 226/226,
  property proofs 86/86 — 0 failed.
- **Suite** 227 PASS (225 + the two new), 0 FAIL. **All 49 gates PASS**, including `performance` (8 benchmarks,
  0 failed) and `formatted tree`.
- **`doc_counts_gate` NOTEs** (not failures, `evidence-r70/doc-counts.txt`): `PROJECT-MASTER.md` says 48 PASS
  (measured 49) and five documents say suite 225 (measured 227). Docs prose; the owner's to bump.

## 4. The per-allocation cost on v264's allocator — measured (`evidence-r70/per-allocation-cost-v265.txt`)

The allocator is unchanged since v264; v265 only changes the parser.

| program | result |
|---|---|
| **1,000 allocations** of 64 B (R59's `per_call.sm`, rdtsc around the loop) | **65,000–127,000 cycles total = 64–126 cycles per allocation ≈ 20–40 µs for all 1,000**, including the first touch of 16 fresh pages |
| **1,000,000 allocations** of 64 B | **75–94 cycles per allocation** (75–95 million cycles total) |
| **your program, indentation form, 1,000,000 allocations, each written** | **0.03 s wall, 62 MB peak RSS** (64 MB of blocks) |

**So yes: 1,000 allocations finish in microseconds, and the arena does what the design says.** The per-allocation
figure includes the loop and the write; R69 measured the loop alone at about the same, so the allocation itself
is a few instructions.

## What I did not do

- **Nothing further was built** (no Step 3), as the brief says.
- **Not edited:** `MEMORY-DECISION.md`'s "203 of 229 examples use no braces" (prose; the true count is 41 files with
  no `{` at all, and none with a braceless loop or `if` before R70).
- **Not run:** real Windows (Wine only).
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs.

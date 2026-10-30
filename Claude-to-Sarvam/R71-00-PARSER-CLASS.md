# R71-00 — The parser class: two more silent drops found and closed; the 6 ns checked; what is slow now

- **Commits on `main`, in order:** `ee98437` (1/5 nothing after `mukhya`, **v266**) · `75fcbae` (2/5 formatter) ·
  `3f402a3` (3/5 every construct as a golden) · `b79479a` (4/5 the same-line rule, **v267**) · `7323b4e` (5/5 its golden) ·
  then this hand-back. Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v267) - sampurna sutra`.** Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=230`, FAIL=0** (three new examples this round). Library proofs **226/226**. Property proofs **86/86**.
- **Guard pages: controls 5/5, suite PASS=230 FAIL=0, library proofs 226/226, property proofs 86/86, 0 failed.**
- **Gates (`sh tools/gates.sh`, Xvfb display): 49 PASS / 0 FAIL / 1 NOT-RUN (Windows execution).** (v266 was also gated: 49 / 0 / 1, `evidence-r71/gates-v266.txt`.)
- **The guard, one change at a time, `tools/guard_pair.py`, all three paths (Linux ELF, Linux PE, the Windows
  compiler under Wine):**
  - **v265 → v266: 0 DIFFER** (487 byte-identical, 92 refused identically, 2 new — the round's first two examples).
  - **v266 → v267: 0 DIFFER** (488 / 93, 1 new).
  - Neither change alters any program in the tree, because no program in the tree wrote either shape.

## WS1 — your 6 ns, reproduced independently: the allocation is ~2 ns; the number depends on whether you touch it

**1,000,000 `nirmmita(64)` in a braced loop, the same program on v265 and on v261** (v261 needs braces: its
parser made the indented form loop forever — the R70 bug). Wall time, median of 21 runs (v265) / 3 (v261);
the loop alone is subtracted (`evidence-r71/allocation-1M.txt`):

| program | **v265** wall | **v265 per allocation** | v261 wall | v261 per allocation | ratio | peak RSS v265 / v261 |
|---|---|---|---|---|---|---|
| the loop alone (`p = i`) | 1.12 ms | — | 1.09 ms | — | — | 264 KB / 264 KB |
| **allocate, never touch** | **2.84 ms** | **1.7 ns** | 619 ms | 618 ns | **~360×** | 264 KB / 264 KB |
| **allocate and write one cell** | **32.6 ms** | **31 ns** | 2,519 ms | 2,518 ns | **~80×** | 62 MB / **4.0 GB** |

**So I get the same order as you, but not the same figures, and the 10,000× does not hold:**
- **"6 ns"** sits between my two cases: 2.8 ns per allocation gross (untouched, loop included) and 31 ns when each
  block is written. Your 16 MB RSS suggests you touched part of the memory; I cannot tell which from the number.
- **The old path is not 62,500 ns.** Measured here, one `mmap` per allocation costs **618 ns untouched and
  2,518 ns with the first write** — R59 measured 4,600–8,200 cycles (1.5–2.7 µs), consistent with this. So the
  honest ratio is **~80× for allocations that are used, ~360× for ones that are not** — and **memory 4.0 GB → 62 MB
  (65×)**, which is the larger win: v261 spent a page on every 64-byte block.
- **What the 31 ns is:** not the allocator (1.7 ns) — it is the kernel's first-touch page fault, ~2 µs per fresh
  4 KiB page, 64 blocks per page. The arena never reuses memory, so every allocation in a loop touches new pages.
  That is exactly what a rewinding scratch side (Step 3) would remove for the uses it allows.

## WS2 — the parser class

### 1. Every construct whose body is indented — how many statements each accepts

`evidence-r71/bodies-matrix.md` (generator `bodies.py`): **25 programs, each body written with an indented body of
several statements and no braces, run on v264, v265, v266, v267.** Summary:

| construct | v264 (before R70) | v265+ |
|---|---|---|
| `yadi` | **first statement only** (a false `yadi` still ran the rest: printed 2, not 0) | all |
| `yadi` / `anya` / `anya yadi` | **refused** (the `anya` became a syntax error) | all |
| `yavat` | **first statement only → hangs** | all |
| `chakra … tak`, `chakra … arabhya … paryantam` | **first statement only** (printed 5, not 9) | all |
| `kuru … yavat (c)` | **refused** | all |
| `guna (x) { bhavana k: … }` with indented case bodies | **refused** | all |
| `guna (x)` itself without braces | refused | **refused — `guna` requires `{ }`** (loud, not silent; left as is) |
| `yadi dosh (q = f()) … anya …` | **refused** | all |
| `prakriya` without braces | **one statement** (a second line was a syntax error) | all |
| `mukhya()` without braces | all (it runs to end of file) | all |
| nested indented bodies; indented around braced; braced around indented | **hang / wrong count** | right |
| body on the header's line; next line not deeper; statement over two lines; tabs | right | right |
| **a statement after a braced `mukhya`'s `}`** | **silently dropped** | **refused (v266)** |
| **`yadi (c) a = 1; b = 2`** | **`b` silently outside the `yadi`** | **refused (v267)** |

**v264: 8 of 25 as written. v267: 25 of 25.** The two `guna`/`mukhya` rows are documented behaviour, not drops.

### 2. Did any of the 225 tests ever exercise a multi-statement indented body? **No — none, ever.**

`evidence-r71/braceless-bodies-before-r70.txt`: the tree at `96ba2ee` (before R70), **643 files** (examples, lib,
tests, benchmarks; not `tests/negative`): **0 braceless headers with an indented body on the following lines, and
0 with a body on the header's line.** Every `yadi`, `yavat`, `chakra`, `kuru` and `anya` in the project used braces.
The form the documents describe and the owner writes had **zero** tests. **You are right that this is a bigger hole
than the bug.** It now has: `examples/258` (R70), **`examples/260`** (every construct above, indented, golden),
`examples/259`, **`261`, `262`** (the refusals).

### 3. Other places where a body silently takes fewer statements than written — searched, two found, both closed

I read every place the parser takes a body (`parse_body` and its 11 callers, `parse_func_block`, `parse_block`,
the top-level loop in `parse_function`, R25's `phal` blocks) and wrote a program for each shape:

- **After a braced `mukhya`'s closing `}`, the parser stopped and never looked at the rest of the file.**
  `mukhya() { likha(1) }` then `likha(2)` **printed 1** — the second statement, or a whole `prakriya` written
  there, silently vanished. **v266: anything after `mukhya`'s body is a syntax error at its line** (`examples/261`).
- **A one-statement body on its header's line, followed by `;` and another statement:**
  `yadi (1 == 2) c = c + 1; c = c + 10` **ran `c = c + 10` unconditionally** — C's rule, but the line reads as one
  body. **v267 refuses a second statement on that line**; `anya`, `yavat` (the tail of `kuru`), `bhavana`, `}`,
  `)` may still follow, and several statements on one line *inside an indented block* all belong to it
  (`examples/262`). If you would rather keep C's rule here, it is one call to remove.
- **Not a drop, documented:** a braceless `mukhya()` runs to the end of the file, so a `prakriya` written after
  it is compiled *inside* it and is callable; `guna` needs braces and says so.

**Both new refusals change no existing program** (guard 0 DIFFER on all three paths each time) — the tree never
wrote either shape, which is the same reason they went unseen.

## WS3 — the benchmarks: what is slow now

**`benchmarks/`, v265, against the same programs in C** (`evidence-r71/benchmarks-vs-C.txt`; gcc -O0, and -O2 with
`-fno-inline` so calls stay calls; ns per iteration; outputs agree):

| benchmark | Sutram | C -O0 | C -O2 | Sutram / C -O0 |
|---|---|---|---|---|
| `bench_loop` (add) | 0.84 | 2.88 | 0.15 | 0.29 |
| `bench_fib` (per call) | 3.12 | 3.98 | 2.41 | 0.78 |
| `r46_hotcall_float` | 4.99 | 4.93 | 1.63 | 1.01 |
| `bench_nested` | 3.39 | 2.92 | 1.19 | 1.16 |
| `bench_arith` | 8.42 | 6.88 | 4.87 | 1.22 |
| `r46_hotcall_nested` | 9.01 | 7.37 | 2.34 | 1.22 |
| `r46_hotcall_stack` | 4.51 | 3.17 | 1.86 | 1.43 |
| `r46_hotcall_array` | 7.19 | 5.00 | 1.93 | 1.44 |

**Sutram runs at roughly unoptimised C speed — 0.3× to 1.4× of `gcc -O0`, 2–5× slower than `gcc -O2`.** To find
what that is made of, I timed single operations: 10,000,000 iterations each, the empty loop subtracted, **15
interleaved rounds** (a first single pass put one call at 5.9 ns; it was noise — this machine needs interleaving;
`evidence-r71/operation-costs.txt` has both passes):

| operation | net cost, least-disturbed run | median |
|---|---|---|
| **allocate 64 B and write it** | **26 ns** | 30 ns |
| **a call through three functions** | **8.2 ns** | 8.4 ns |
| `i / 7` | 2.5 ns | 2.5 ns |
| `i % 7` | 2.4 ns | 2.5 ns |
| `dasham` add | 2.1 ns | 2.2 ns |
| **one function call** | **2.0 ns** | 2.3 ns |
| index a `mala`, a `kosh`, a raw block; read a byte | 1.8 ns each | 1.9 ns |
| allocate 64 B, never touch it | 1.6 ns | 1.7 ns |
| `i * 7` | 0.2 ns | 0.3 ns |
| `yadi` compare | 0.2 ns | 0.2 ns |

**The top three costs now:**

1. **First touch of fresh memory — 26–30 ns for a 64-byte block that is used, ~2 µs per 4 KiB page.** The bump is
   1.6 ns; the rest is the kernel faulting in pages the arena has never handed out, because it never reuses one.
   Any allocation-in-a-loop program pays it per block. The cure is reuse — the scratch side's rewind (Step 3) for
   what it can hold — not a faster bump.
2. **Function calls — 2 ns for one, 8 ns for a chain of three** (most of 5 of the 8 benchmarks: `fib` and the
   four `hotcall`s). The caller pushes and pops `r12`–`r15` around **every** call whether or not they hold
   anything, the argument goes through the stack (`push`/`pop` into `rdi`), and the callee saves `rbp`, `rbx`,
   `rdi`, reserves a **2 KiB frame** (`sub rsp,0x800`) and reads its parameter back from memory — about 20
   instructions per call where C `-O0` uses ~8 (`evidence-r71/call-sequence.txt`).
3. **Division and remainder — ~2.5 ns:** every `/` and `%` is a hardware `div`, including by a constant (C `-O2`
   turns `% 7` into a multiply). It is most of `bench_arith` and `bench_nested`.

**Close behind:** `dasham` arithmetic round-trips through general registers (`movq rax↔xmm` around each `addsd`,
2.1 ns for an add), and every index is bounds-checked (1.8 ns — the price of the safety, and correct).

**Allocation itself is no longer on the list (1.6 ns); what remains of it is page faults — the kernel's cost of
memory that is never reused.**

## What I did not do

- **No Step 3.**
- **Not changed:** `guna` still requires braces (refused, not silent); the calling convention, division, `dasham`
  code generation — measured and named, not touched.
- **Not run:** real Windows (Wine only).
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `docs/` prose (the doc-count NOTEs are below).

**Document counts:** `doc_counts_gate` NOTEs (not failures, `evidence-r71/doc-counts.txt`): `PROJECT-MASTER.md`
says 48 PASS (measured 49); five documents say suite 225 (measured 230). Docs prose; the owner's to bump.

**One Wine run was disturbed:** the first v266 → v267 Wine guard reported `tests/stdlib/chandas_guru_count.sm` as
DIFFER (the Windows compiler exited 1 once). Compiled by hand four times it gives exit 0 and the same bytes on v266
and v267; the guard re-run on a quiet machine is **0 DIFFER**. Both transcripts are in `evidence-r71/`.

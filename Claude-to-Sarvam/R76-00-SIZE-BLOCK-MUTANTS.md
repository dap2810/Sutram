# R76-00 — Option 3 for `nirmmita`; the block's real users are in the library; no Madhava sign error, but two wrong answers in `kuttaka` and `meru`, fixed

- **Commits on `main`, in order:** `9f54350` (1/2 `kuttaka` and `meru` fixed, the known-values test, the wrong golden
  corrected) · `fc5f379` (2/2 the reference §6c, the changelog, the generated library page) · then this hand-back. Pushed
  with git, not `--force`.
- **Compiler: `Sutram 1.0 (v273) - sampurna sutra` — unchanged this round** (the default build from `src/` is
  byte-identical to the tree's binary; the bounds-check prototype is a patch in the evidence, not in `src/`).
  Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=240`, FAIL=0.** Library proofs **227/227** (one new). Property proofs **86/86**.
- **Guard pages: controls 5/5, suite PASS=240 FAIL=0, library proofs 227/227, property proofs 86/86, 0 failed.**
- **Gates (`sh tools/gates.sh`, Xvfb display): 52 PASS / 0 FAIL / 1 NOT-RUN (Windows execution).**
- **The guard, v273 tree → this tree, `tools/guard_pair.py`, all three paths (Linux ELF, Linux PE, the Windows compiler
  under Wine): 490 byte-identical, 120 refused identically, 35 DIFFER, 1 new.** The 35 are exactly the programs that
  import `ganita` or `chandas` (the whole module is compiled in). **I ran every one, old and new, ELF and PE under
  Wine: 34 give the same output and exit code; one changes — `tests/stdlib/numeric29`, whose first line was a wrong
  `kuttaka` answer** (below), and whose new ELF and PE outputs agree. `evidence-r76/guard-differ-outputs.txt`.

## WS1 — can `nirmmita` know its size? I built it and measured it. **Answer: 3.**

**I built the header (your option 1) as a real compiler variant** (`evidence-r76/prototype-bounds-check.patch`,
`nasm -dR76_PROTO`): `nirmmita(n)` reserves `n + 16`, stores `n / 8` at `[p − 8]` — the layout a `mala` already
uses — and **every raw index is checked against it** with the `mala` check. It catches your case
(`nirmmita(1)`, then `b[0] = …` → `mala ank seema atikram`, exit 1). Then I ran the tree under it:

| | the shipped compiler | the header prototype |
|---|---|---|
| suite | 240/240 | **240/240** |
| library proofs | 226/226 | **215/226 — 11 fail** |
| property proofs | 86/86 | **78/86 — 8 fail** |
| the 8 shipped benchmarks | — | **identical binaries: 0% cost** (none of them indexes a raw buffer) |
| raw read loop / raw write loop / sieve (new) | — | **−2% / +28% / ±3% (noise)** |

**Every one of the 19 failures is a false alarm, and they all have one cause.** I stopped each at its first trap in
gdb: **every base address is 8 bytes past a 16-byte boundary — an interior pointer** (`arr + (pos + 1) * 8`, the
library's length-prefixed text cells), where `[p − 8]` is not a header but the previous cell's data. Rounding the
header up instead of down changes nothing. **A header can only check a pointer to the start of a block, and the
library passes interior pointers everywhere** (sets, maps, split/join, `khand_bandh`). Making it sound needs fat
pointers — every address carrying its bounds, 16 bytes instead of 8, through every call — which is a different
language.

**Your option of "the mark as the header": it cannot work** — the mark is one per *block*, not per allocation; it
knows where the block's scratch began, not how big each buffer in it is.

**The shadow table (option 2)** handles interior pointers (it finds the allocation that *contains* the address),
so I estimated it in C — a range lookup per indexed write on the same raw-write pattern:

| live allocations | unchecked | checked | ratio |
|---|---|---|---|
| 1 | 0.49 ns | 1.49 ns | 3× |
| 1,000 | 0.46 ns | 10.2 ns | **22×** |
| 1,000,000 | 0.43 ns | 22.9 ns | **53×** |

**Far past your 20% line.** (`evidence-r76/ws1-size-check-measurements.txt` has every number, the programs and
`shadow.c`.)

**So: 3, said plainly. `nirmmita(n)` gives you `n` bytes; write more and it is your mistake, as in C.** It is now
in `docs/LANGUAGE-REFERENCE.md`: the built-in table says *"its cells are not bounds-checked"*, and **new §6c, "Raw
memory is not bounds-checked"**, says what happens, that `mala` and `kosh` *are* checked (and why — they own their
length; an address does not), and **how to find such a mistake: the `GUARD_PAGES` build** (`tools/guard_page.py`'s),
which puts every block flush against unmapped memory — **it stops your exact case with SIGSEGV** (checked). If you
want that as a user-facing `--raksha` debug switch, it is a small round: the build already exists.

## WS2 — how many programs would a scalar-only block help? **None of the tests. But nine library functions — and there it is not a curiosity.**

**Every program, run and measured** (`evidence-r76/ws2-census-per-program.tsv`): 244 examples + 226 library
proofs; 428 run (the other 42 are refusal goldens). **Every one peaks at 264–392 KB — the size of a program that
prints 0.** 27 examples and 88 proofs call `nirmmita` at all; none allocates enough for any block to save anything
measurable. **Counted your way, the answer is zero.**

**But that is the wrong place to look, because the tests are small and the allocation that repeats is inside the
library.** A `mandapa` is lexical: a block around a *call* does not reclaim what the callee allocates — so the place
a block helps is *inside* a library function that makes a temporary buffer. **26 of 306 library functions call
`nirmmita`; 9 of them throw the buffer away** (number → text in `roop`/`vakyank`/`aadhar`, `brihat_ghatmod`,
`mil_shreni`'s merge, `rakh_tak_mala`). **Measured:** a program calling `roop_ank` 1,000,000 times —

| | peak memory | time |
|---|---|---|
| the library as shipped | **171,904 KB** | 0.15 s |
| `roop_ank`'s body inside a `mandapa` | **264 KB** | 0.08 s |

**All nine accept a block** (the escape check finds no escape in any), and **with all nine wrapped, the library
proofs are 226/226 and the properties 86/86.** **I did not land it** — you asked for a count, and it changes the
binary of every program that uses those six modules. **It is ready:** `evidence-r76/proposed-lib-mandapa.patch`
applies cleanly. **My recommendation: describe the block as a tool for library authors and for scratch arithmetic in
loops, land the patch, and say "every number-to-text conversion in the library now runs in constant memory".**

## WS3 — the mutants. **There is no sign error in Madhava. There were two wrong answers elsewhere, and a golden that recorded one.**

### The Madhava "sign error" is a survivor from R15, already closed

**`PROJECT-MASTER.md`'s "15 bug-shaped mutants … including a sign error in `madhava_sin`/`cos`/`atan`" describes
R15's measurement.** A surviving *mutant* is not a wrong answer: it is a change to the code that no test notices.
The sign mutants (`atan`'s negative branch, the reduction's lower half) **have been killed since R18** by
`tests/stdlib/r18_madhava_reduction.sm` (atan(−20), atan(−1.5), sin/cos at −18 and −4); I re-scored the module
today — every one is killed. **And the functions are right:** sin, cos and atan against Python's `math` at
**24,003 points from −100 to 100: worst error 5×10⁻⁷ (the 6-decimal print), no sign wrong anywhere**; `madhava_pi`
is within 4×10⁻¹⁶ of π. The 27 Madhava mutants that still survive have **no witness** (308 inputs each; 1 for `madhava_pi`, which takes none) — 17
terms instead of 16, `>` instead of `>=` at an exact boundary: equivalent at the precision printed.
(`evidence-r76/ws3-madhava.txt`.)

### Working the list — two real wrong answers

**There is no 15-entry list** (Muse said so in R57); I took the survivors Muse's R57 named, re-scored them on
v273, and **ran a witness search on every one** — an input on which the mutant and the real function differ
(`evidence-r76/ws3-survivor-witnesses.txt`). **A witness means some behaviour no test pins; before pinning it I
checked the real answer against exact arithmetic — and two were wrong:**

1. **`kuttaka(a, b, c)` (Aryabhata's pulveriser) was wrong for large moduli.** The witness
   `kuttaka(−2, −(2⁶³ − 1), 16)` returned 9223372036854775791; −2 × that ≢ 16. Then I checked 600 random cases:
   **right 162/162 for |b| ≤ 2⁴⁰, right 0/438 above** — `old_s * mult` overflowed every time. **And
   `tests/stdlib/numeric29` had recorded one of those wrong answers as its golden** (2605677504891245458; the
   solution is 1483584605987376058) — **the "golden that locks in a bug" you asked about, found** — and
   `tools/proof_props.py` pinned the same wrong value on purpose as a known gap ("the exact result differs").
   **Fixed:** the product is taken modulo |b| by a new `kuttaka_gun_shesh(x, y, m)` (double-and-add, no value above
   m). **600/600 correct**; the golden and the property now hold the exact answer.
2. **`meru(n, k)` (Pingala's C(n, k)) wrapped silently past 2⁶³ − 1** — `meru(1000, 10)` printed C(1000, 10) mod
   2⁶⁴, `meru(67, 30)` a negative number. **Fixed: −1 when the answer does not fit** (a binomial is never
   negative, and 0 already means k out of range). **All 2,556 values for n ≤ 70 checked: 2,500 exact, 56 → −1.**

**Everything else on the list was right**, and is now pinned: `ank_gan(−9) = 1`, `seemit`/`ganit_seemit` with
lo > hi, `brahmagupta_kshetr(16, 5, 4, 1000) = 0`, `ganita_paripurna_kramgun(10⁹)` saturating.
**`tests/stdlib/r76_known_values.sm`** holds all of them **— every value checked against exact arithmetic, not
recorded from the implementation** — plus Madhava against exact values (sin π/6 = 0.5, cos π = −1, atan(−√3) =
−π/3 …). **After it, every survivor of `kuttaka`, `meru`, `kuttaka_gun_shesh`, `ank_gan`, `seemit`,
`ganit_seemit` and `brahmagupta_kshetr` has no witness** — equivalent — except two that differ only on inputs
outside the function's contract, and one (`kramgun`'s MAX literal) that differs only in running time.
(`evidence-r76/ws3-survivors-after.txt`, `ws3-kuttaka-meru-crosscheck.txt`.)

**One thing the tool got wrong, found on the way:** a mutant id can name two different mutants on one line
(`A:-@L32` is both `top - r` → `top + r` in the condition and in the assignment). The witness search keyed on the id
and tested only one. My `variants.py` (in the evidence) scores each variant separately; `lib_mutant_witness.py`
should do the same — not changed this round.

## On your v427 entry (pushed while I worked), checked against the tree

- **"Assert EOF at the end of compilation" is already there — since v266 (R71):** `parse_program` refuses anything
  after `mukhya`'s body, and v267 refuses a second statement on a one-statement body's line; `examples/261`, `262`
  are the goldens. What R71 did *not* do is turn every remaining `ret` on an unexpected token into an abort — that
  structural pass is still worth a round.
- **The byte-versus-qword trap is WS1 seen from the other side** — `nirmmita(10)` then `p[i]` for `i < 10` is
  exactly a write past `n` bytes, which §6c now states and which the header prototype traps. Gemini's two cheap
  fixes are compatible with option 3: a **compile-time** check when both the size and the index are literals costs
  nothing at run time and catches the student's case; **rounding allocations up to 8** stops a 10-byte buffer from
  being 2 bytes short of its second cell, but would not have caught your `p[i]` loop (it writes 80 bytes into 16).

## What I did not do

- **The library block patch is not landed** (WS2) — your decision; it is ready and proven.
- **No bounds check, no `--raksha` switch** (WS1) — option 3, documented; the switch is offered.
- **`suchi_srij` / `avali_srij`'s survivors are undecided** — their parameters are sizes that mostly fail to
  allocate, so the witness search had only 6 usable inputs. **Muse has the list this round too** (its R76 brief).
- **Not run:** real Windows (Wine only).
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`, the compiler source.

**Document counts:** `doc_counts_gate` NOTEs (not failures, `evidence-r76/doc-counts.txt`): `PROJECT-MASTER.md`
says 48 PASS (measured 52), suite 225 (240), library proofs 226 (227); several documents say 305 functions (306) —
and **`PROJECT-MASTER.md`'s "15 surviving mutants including a sign error in Madhava" is out of date** (above).
Docs prose; the owner's to change.

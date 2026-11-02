# Sutram — ROUND-98: the census (third run), `parimita` yes/no, and the `dasham`→`mala` dispute settled

**Base:** `origin/main` at `bbb7c17f` (compiler v283, verified `--version`).
**Deliver into:** `Muse-to-Sarvam/`. **No tree changes** — read-only audit,
census, and probes; nothing in `src/`, `lib/`, `examples/`, or `tests/`
was modified.

**What landed with this round.** Three "MEMORY ONLY" commits at 09:33
today added one inbox file each: `Sarvam-to-Claude/ROUND-102.md`,
`Sarvam-to-ChatGPT/ROUND-171.md`, and `Sarvam-to-Muse/ROUND-98.md`.
No `examples/`, `lib/`, `src/`, or `tests/` file changed in any of them
(verified: `git diff 85355da6..bbb7c17f -- examples/ lib/` is empty),
so the census tree is the same tree R96 and R97 measured. WS1 was
re-run anyway, not cited — see below.

## WS1 — the three allocation counts (third run, same method, same numbers)

| # | question | examples | lib functions | total |
|---|---|---|---|---|
| 1 | allocate inside a loop | 4 | 0 | **4** |
| 2 | grow a `kosh` more than 1,000 times | 0 definite, 1 potential | 0 | **0 definite, 1 potential** |
| 3 | allocate without a `mandapa` block at all | 57 | 26 | **83** |

Denominators re-verified: 274 examples, 306 lib functions, 580 combined.
The R96 scripts (`scan.py`, `loop_bodies.py`, `loop_local.py`) were
re-run against a pristine worktree of this base; `ex_flags.json` and
`lib_flags.json` are byte-identical to R97's, and the counted cases
were re-verified by line reads in R97 on files that have not changed
since (258: 1006 allocations in 3 fixed loops; 217: 8 loop calls; 237:
2 calls; 268: 1,000,000 calls freed per call; 286 `varg_yog(n)` pushes
exactly n times, own inputs 10/100; lib: 26 `nirmmita` functions, zero
`mandapa`, zero kosh declarations, zero kosh growth). Decisive cases
re-run on this base with the same results: the 286-shape probe with
n = 1001 printed 501501, exit 0; `chakra i = 0 tak 3.0` refuses
`E_CHAKRA_DASHAM`, no binary; `dasham avg = 15 / 4` prints `3.000000`;
example 258 standalone matches its golden byte-for-byte, exit 0.

**Interpretation, third confirmation.** Q1 and Q2 are near zero in the
sense that matters (zero unbounded loop allocations, zero kosh growths
past 1,000 on any program's own inputs, one input-dependent potential
now run-confirmed at 1001). The memory gaps are theoretical for our
own code, exactly as the 3-1-0 alias census settled that question.
Q3's 83 measures low `mandapa` adoption, not risk. **The budget is
documentary for the tree, not urgent** — urgent would require a tree
program that grows without bound, and there is none. This is the third
run of these numbers (R96, R97, R98) and they have not moved, because
the tree has not moved.

## WS2 — `parimita` only: yes

**Answer: YES.** `parimita` is approved for a `mandapa` byte budget,
on all four tests:

1. **Complete word, not a fragment?** Yes — परिमित, a full
   adjective/participle (`pari` = around + `mita` = measured). No
   shortening, no lost prefix.
2. **Collision anywhere in the tree?** **Count of hits: 0 in code.**
   Word-boundary grep over `src/`, `lib/`, `examples/`, `tests/`,
   `tools/`, and `docs/` returns zero lines; Devanagari परिमित over
   `src/`/`lib/`/`examples/`/`tests/` returns zero; a substring grep
   (which would catch a longer word containing it, e.g. a hypothetical
   `aparimita`) returns zero substring-only hits. The whole-repo
   grep returns 25 lines across 10 files — every one of them prose,
   none of them code: the R170 brief, the R171 and R102 briefs, the
   R97 and R98 briefs, the R96 and R97 reports, and the R96/R97 JSONs.
   So the collision count is 0 and the total grep count is 25, all
   non-code. There is nothing to collide with.
3. **Typeable and memorable?** 8 letters, regular (`pari` + `mita`),
   unambiguous. Manageable for a student whose first language is not
   Sanskrit; less familiar in everyday speech than `seema`, but
   familiarity in the wrong sense is worse than unfamiliarity, and
   `parimita` has no wrong sense competing with it.
4. **Does its literal meaning describe an enforced budget, rather than
   translate the English word "limit"?** Yes — and the distinction
   matters. "Limit" in English is a line: a boundary you may or may
   not cross. `parimita` is stronger than that: it says the thing has
   been *measured* — given a measure, an amount. A budget is exactly
   a measured amount that is held to: fail closed when the measure is
   reached, not a line that is merely drawn. That is why `parimita`
   beats `seema` for this concept (`seema` is the boundary OF a
   field — a line, and already doing "limit" duty in ~20 diagnostics
   and in `yog_seema`) and beats `maryada` (whose modern sense is
   propriety, not measurement). The fail-closed condition ChatGPT
   states for it is the right one: a `parimita` region that silently
   exceeds its measure would make the word a lie.

**Yes, `parimita`, for the `mandapa` byte budget.** No collision, no
caveat that changes the verdict.

## WS3 — the `dasham`→`mala` dispute: neither of us is wrong about the mechanism

Sarvam's challenge, quoted so there is no softening: "You reported it
stores 0. I measured `4613937818241073152` for `3.0` — the IEEE bit
pattern, not zero. Which path did you test? Give me the program.
Either your reading or mine is wrong, and the difference matters:
'stores zero' and 'stores the raw bits' are different bugs with
different fixes. Do not soften this. One of us is wrong and I would
rather find out now."

**The verdict, unsoftened: neither of us is wrong about the mechanism.
What was wrong is the reading of my "0".** Here is the evidence, in
order.

### The path I tested, and the program (R90, v281)

My report is `Muse-to-Sarvam/ROUND-90-RELEASE-NUMBER.md`, and the
program is saved at `~/workspace/r90/probes/conv_mala.sm`. It is, in
full:

```
mukhya() {
    mala a[2]
    dasham d = 3.7
    a[0] = d
    likha(a[0])
    likha("reached")
}
```

The path: a `dasham` VARIABLE stored into a `mala` element, read back
with `likha` (as an integer, since `mala` elements are integer slots).
R90's sentence, in full: "storing a `dasham` into a `mala` element
does not convert and does not refuse — **it stores the raw bits**."
The result on v281: `likha(a[0])` printed `4615514078110652826` (the
float64 bit pattern of 3.7, read back as an integer), exit 0.

### The "0" was the tree count, not the stored value

R90's next sentence: "Tree count for that trap: **0** (a scan of every
`name[i] = <dasham>` store in examples and library found only `kosh
dasham` stores, which are correct float stores...)." R95 repeated it:
"Dasham → `mala` element stores: 0 in examples (R90's count still
holds)." **Neither report says "stores zero".** The "0" counts how
many tree programs hit the trap (zero), not what the store writes.
Read as "stores 0," it describes a different bug (a store that writes
nothing) with a different fix. That reading is what is wrong — and it
is a misreading of my sentence, not a disagreement about the compiler.

### Re-run on v283: both numbers reproduce exactly

R90's exact program, re-run on v283 (this base): prints
`4615514078110652826` and `reached`, exit 0 — R90's number, exactly.
Sarvam's shape on v283, both forms:

```
mukhya() {                       mukhya() {
    mala a[2]                        mala a[2]
    dasham d = 3.0                   a[0] = 3.0
    a[0] = d                         likha(a[0])
    likha(a[0])                      likha("reached")
    likha("reached")             }
}
```

Both print `4613937818241073152` and `reached`, exit 0 — Sarvam's
number, exactly, whether the 3.0 arrives as a variable or a literal.
Literal versus variable makes no difference; v281 versus v283 makes
no difference. Both numbers were also verified independently as the
IEEE patterns (3.7 → 4615514078110652826; 3.0 → 4613937818241073152).
**The mechanism is the same on both sides: a raw qword store, no
conversion, no refusal.**

### One sharpening, from a further probe (new in R98)

Storing the bits is faithful, but the value is unrecoverable through
the language's own reads. A probe that stores 3.7 and reads the
element back into a `dasham` variable:

```
mukhya() {
    mala a[2]
    dasham d = 3.7
    a[0] = d
    dasham back = a[0]
    likha(back)
    likha(a[0])
}
```

prints `4615514078110652416.000000` for `back` and
`4615514078110652826` for `a[0]`. The integer read gives the bits;
the `dasham` read does NOT reinterpret the bits back to 3.7 — it
converts the bits-as-integer to a double (a huge number, float-rounded).
There is no read path that returns 3.7. So the trap is worse than
"reads back as bits" in one respect: the stored value cannot be
recovered as a `dasham` at all. That belongs in the trap's description
alongside R90's.

### The tree count, re-verified on v283: still 0

Every dasham-valued indexed store in `examples/` and `lib/` was
re-checked on this base, including the look-alikes R90 named. All are
`kosh` stores, not `mala` stores: 135 (`kosh dasham ank_suchi`,
`ank_suchi[0] = 100.0`), 140 (`kosh dasham ank_mala` — the name
contains "mala" but the variable is a `kosh`, `ank_mala[0] = 9.0`),
148 (`kosh dasham ank_suchi`), 110/118/123 (t18 `kosh` tests), 252
(`w[5] = 9.9`, `w` a kosh alias), lib kalana `ok[0] = 1.0` and
samanvaya `out[...] = 1.0/0.0` (both `kosh dasham`). Stores into
genuinely `mala`-declared variables (248 `a[i] = i + 1`, 251 `a[0] =
10`, 246 `x[0..7]`, 20 `nums[i] = i * i`) are all integer stores.
112's `a[0] = d` (dasham 4.8) is into `kosh a[1]`, an integer kosh,
and refuses `E_DASHAM_VITTI` as its own header states. 265's
`bahar[i] = buf` stores a `nirmmita` pointer and is refused
`E_SCRATCH_ESCAPE` anyway. **Tree count for the `dasham`→`mala`
trap on v283: 0, as R90 and R95 reported.** (R38's "a 3-cell mala
silently returned 0" is a different, pre-fix alias finding — an
out-of-bounds load through an unmarked alias, fixed in R38 — and is
not the referent here; it was checked and ruled out.)

### What follows for the fix

Since the mechanism is raw-bits on both sides, the fix (if the owners
want one) is the same fix: a `mala`-store check — refuse a `dasham`
stored into a `mala` element (the R90 "belongs to the owners" item),
or convert it. It is NOT a zero-store fix, because there is no
zero-store bug. And the trap description should now read: "stores the
raw bits; an integer read returns the bits, and a `dasham` read
converts the bits-as-integer to a huge double — the value 3.7 cannot
be read back."

## The R101 ~100 MB program (the brief's preamble question, answered)

The brief's verified behaviour says `kosh` pushes are essentially flat
(10k = 12,776 KB; 100k = 13,132 KB; 1M = 13,256 KB) and asks for "the
exact program behind" Claude R101's "about 100 MB" figure, which seems
to contradict it. **There is no contradiction — the two figures come
from two different programs, and R101's own tables agree with Sarvam's
on the shared one.**

The exact program behind the ~100 MB figure is R101's `kb1.sm`
(`Claude-to-Sarvam/evidence-r101/memory-measurements.txt`, also the
`KOSH_IN_BLOCK` gate program in `tests/r101/test_memory_claims.py`):

```
mukhya() {
    vitti i = 0
    vitti s = 0
    yavat (i < 100000) {
        mandapa {
            kosh k[1]
            vitti j = 0
            yavat (j < 100) {
                kosh_push(k, j)
                j = j + 1
            }
            s = s + k[99]
        }
        i = i + 1
    }
    likha("s ", s)
}
```

Peak RSS as measured by R101: **104,576 KB** with the block,
101,504 KB without it, and 0 KB for one `kosh` made before the loop
with `kosh_clear` each pass. The program makes **100,000 separate
koshes** (one per `mandapa` pass, 100 numbers each) and none is
reclaimed — that is where the 100 MB comes from. Sarvam's program
grows **one** kosh by pushing 10k/100k/1M times, which stays flat.
R101's own single-growing-kosh table says the same as Sarvam's:
100,000 pushes abandon about 1 MB (1.3x the kosh), 1,000,000 pushes
about 8 MB (1.05x) — bounded at ~2x, not unbounded. So both
measurements stand; they measure different shapes. The gap they
jointly pin is the one R101 states and §19 documents: **a `kosh`
made inside a `mandapa` is NOT reclaimed by the block** — which is
why the WS1 census counts (Q3's 83) and the RSS figures answer
different questions, and why "the block bounds memory" holds for
`nirmmita` and not for `kosh`. This section supplies the program as
asked; no RSS measurement was re-run here, so no new RSS number is
claimed.

## What this round did NOT do (NOT RUN)

Windows, browser, implementation (no `mala`-store check was
implemented — that belongs to the owners, as R90 stated; no name was
added to the compiler). Native-speaker review (WS2's Devanagari form
is best-effort). The full suite, proofs, gates, and guard were not
re-run: no `src/`/`lib/`/`examples/`/`tests/` file changed in this
round, and the tree is byte-identical to R96's/R97's base over
`examples/` and `lib/`, so R95's suite PASS=270 / NO-EXPECTATION=4
stands on that basis, cited not re-run. RSS measurement was not
attempted (the brief's verified behaviour and Claude R101's
measurements are cited, not reproduced). The preamble's R101 question
IS answered in the section above (the exact program, not a
re-measurement).

## Deliverables

- `Muse-to-Sarvam/ROUND-98-CENSUS-PARIMITA-MALA.md` (this report)
- `Muse-to-Sarvam/r98_census.json` (WS1 counts, WS2 hit counts and
  verdict, WS3 programs and run results)

Work staged in `~/workspace/r98/` (scripts in `ws1/`, probes in
`ws3/probes/`, worktree in `tree/` — read-only, removed after delivery).

# Sutram — ROUND-103: count what breaks — zero running programs, one error example, and the cost of a kosh

**Base:** `origin/main` at `1561bd2c` (compiler v288).
**Deliver into:** `Muse-to-Sarvam/`. **No tree changes by this round,
and no implementation** — the arena design is assessed here by
counting and measuring, not built. (Claude is counting WS1
independently; the method below is stated so the two counts can be
compared.)

## Where the project is (premise notes)

v288 is Claude's R106: `likha` prints a string's text (312),
a string is not a condition (313, `E_VARTANI_SATYA`), a kosh is not
a number (314, `E_KOSH_GANIT`), a dasham into a mala converts
exactly (315, fractional stops with `E_DASHAM_VITTI`). Suite 283,
guard 693 programs 0 DIFFER, gates 59 PASS / 1 FAIL (installer
v243 vs v288) — cited from the brief, not re-measured. **Examples
are 287 on this base, not 283:** v288 added 312–315, so the brief's
283 is the v287 count, stale for the fifth time (259, 274, 277,
283, now 287). All counts below use the v288 denominator.

## WS1 — the number that decides whether the arena design is small or large: zero running programs break

**Method (so Claude's independent count can be compared).** A kosh
counts as "made inside a `mandapa`" if its declaration is textually
inside a mandapa block — braced (`mandapa { ... }`) or indented
(`mandapa` + indented body), including the typed form
(`kosh dasham m[2]`, 299's form, which a naive `kosh NAME[`
pattern misses). It counts as "used after" if its name — **or any
alias assigned its address inside the block** (`bahar = k`) — is
used after that block's end. Name-only counting misses the alias
case, and the alias case is the whole story here.

**Result: 3 examples make a kosh inside a `mandapa`; 1 uses it
after the block; 0 running programs break.**

| example | kosh | made inside | used after | under the arena design |
|---|---|---|---|---|
| 286 (kosh in mandapa) | `k` | yes (braced block) | no — read inside only; the block returns a computed value `s`, not the kosh | unchanged |
| 299 (nonfinite kosh mandapa) | `m` | yes (`kosh dasham m[2]`) | no — pushed, read, and passed to `pratham` inside only | unchanged |
| 287 (kosh after mandapa) | `k` | yes (braced block) | **yes — via alias**: `bahar = k` inside, `padh(bahar, 0)` after | see below |

**287 is the one, and it is an error example, not a running
program.** Today it compiles, prints `22` (the in-block read), then
stops with `E_KOSH_MANDAPA` at runtime (exit 1) — the runtime
check, not a compile refusal: "kosh 'k' made at line 10 in a
mandapa; that mandapa has ended." Its golden is that stop, on v287
and v288 identically. Under the arena design, 287's fate depends on
one design choice: **if the post-block-use check is kept, 287 is
unchanged** (still a clean stop); **if the check is removed in
favor of the free, 287's clean stop becomes a crash** (unmapped
arena) **or a garbage read** (reused arena) — and its golden
changes either way. The design as stated says "no liveness table,
no generation check for regions," which reads as removing the
check — so the design must answer whether the check stays, because
287 is the test that proves it. (A name-only count would report
"0 after" and miss 287 entirely; an alias-aware count reports 1,
and the 1 is an error example. Claude's count should be compared
on that distinction.)

**Two further assessment notes, stated as costs, not designs:**

- **Growth-in-arena breaks the never-move guarantee for in-block
  koshes.** A new slot means a new address; an alias taken before
  growth reads the abandoned slot (stale, not crashed — the slot
  stays mapped until block exit). Outside-block koshes keep their
  region and their guarantee; in-block koshes would not. No
  example aliases a growing in-block kosh today, so nothing breaks
  — but the guarantee becomes "where you make it" in a second
  sense: outside koshes never move, inside koshes can.
- **`parimita` fits the design, with one open question.** Growth
  waste counts against the arena budget, so waste cannot run away
  (budget and block become one mechanism, as the brief says). What
  bounds an *unbudgeted* block's arena is not stated — that size
  is the design's to name.

**No function returns a whole kosh** (checked: `nivartanam`
returns values, elements, and lengths, never a kosh itself), so
the dynamic question — a kosh created by a call inside a block —
does not arise in the tree. The textual count above is complete.

**Verdict on the design's size: cheap.** Zero running programs
break; one error example needs the check kept. The design changes
nothing that exists, provided the post-block-use check stays.

## WS2 — the cost of a kosh today: virtual is exactly 64 MiB each, RSS is one page each, and 1,000 cannot be built

Measured on v288 by running probe programs that declare N live
koshes, then block on input while `/proc/<pid>/status` is read
(`VmPeak`, `VmSize`, `VmHWM`, `VmRSS` — peak RSS included). Two
variants: declared-only (reserved, untouched) and touched (one
`kosh_push` each).

| live koshes | VmSize (virtual) | VmRSS (resident) | note |
|---|---|---|---|
| 0 (baseline) | 236 kB | 16 kB | runtime alone |
| 1 declared / touched | 65,772 kB | 20 kB | +64 MiB virtual, +4 kB RSS |
| 10 declared / touched | 655,596 / 655,600 kB | 60 / 64 kB | +640 MiB virtual, +~4 kB each |
| 100 declared / touched | 6,553,844 / 6,553,880 kB | 424 / 464 kB | +6.4 GiB virtual, +~4 kB each |
| 1,000 | **cannot be built** | — | compiler refuses (below) |

**The invisibility problem, settled by number.** Virtual size is
exactly N × 64 MiB plus baseline (one 64 MiB `MAP_NORESERVE`
reservation per kosh, untouched pages costing nothing) — 100
koshes reserve 6.4 GiB of address space and use 0.4 MB of RAM.
That is harmless on a 64-bit system (6.4 GiB is 0.005% of the
128 TiB user address space; the pages are never committed until
touched). Resident cost is **one 4 KiB page per kosh** (the
region's header page, touched at creation) — touched and
declared-only differ by almost nothing for small koshes, because
one pushed element fits in the header page. So: virtual is
harmless because it is virtual, and resident is ~4 KiB per kosh,
not 64 MiB.

**Why there is no 1,000 row: the compiler refuses above ~256
statements in one function** (`khand kathan seema atikram` — a
section-statement limit). 256 koshes compile, 280 refuse; and
1,000 plain `vitti` declarations (zero koshes) refuse too, so the
cap is general, not kosh-specific. Top-level kosh declarations
are a syntax error (`vyakaran dosh`, line 1), so koshes cannot be
spread across the file to dodge the per-function cap — 1,000
simultaneously-live koshes would require global-address smuggling
(store kosh addresses in globals across functions), not a normal
program. Extrapolated from the measured per-kosh rates, 1,000
would be 64 GiB virtual and ~4 MB resident — but that row is
extrapolation, not measurement, and the compiler cap is the
binding constraint, not memory.

## WS3 — census eighth run, and the eight traps on v288: three fixed by v288, two remain live

### Census (same method)

| # | question | examples | lib | total | moved? |
|---|---|---|---|---|---|
| 1 | allocate inside a loop | 6 | 0 | **6** | no |
| 2 | grow a `kosh` more than 1,000 times | 0 definite, 1 potential | 0 | **0 definite, 1 potential** | no |
| 3 | allocate without a `mandapa` block at all | 58 | 26 | **84** | **yes: +1** |

Denominators: **287 examples, 306 lib functions, 593 combined.**
Method: R96 scripts re-run against a pristine worktree of this
base; flags differ from R102 only by the four added examples
(312–315). The Q3 move is entirely 314 (two kosh declarations,
two pushes, no mandapa) — with a stated caveat: **314 is
compile-refusing (`E_KOSH_GANIT`), so its allocation never runs;
textual Q3 is 58, runtime-true Q3 is 57.** The textual number is
reported for series comparability (prior runs were textual too,
and no earlier compile-refusing program carried
alloc-without-mandapa flags); the runtime number is the behavior.
Q1 and Q2 are unchanged (312, 313, 315 carry no allocation flags;
314 has no loop).

### The eight traps on v288 — v288 fixed three, and the live count is two, not five

| # | trap | on v288 | status |
|---|---|---|---|
| 1 | SUB/MUL/DIV on strings | refuses `E_VARTANI_GANIT` (at `s - t`) | fixed (by v287) |
| 2 | string ordering ("b" < "a") | `0`, `1` — content order, correct | fixed (by v287) |
| 3 | string truthiness (`yadi (e)`, `yadi ("")`) | refuses `E_VARTANI_SATYA` | **fixed (by v288)** |
| 4 | kosh == (both `[7]`) | refuses `E_KOSH_GANIT` | **fixed (by v288)** |
| 5 | `likha(kosh)` | prints an address (`132644689936400`) | **still live** |
| 6 | string into mala | prints an address (`4194681`) | **still live** |
| 7 | string + dasham literal | refuses `E_VARTANI_CAT` | fixed (by v286) |
| 8 | dasham → mala (3.7) | stops `E_DASHAM_VITTI`, exit 1 (fractional refuses; whole converts per 315) | **fixed (by v288)** |

**Reconciliation with the brief's "three fixed, five remain."**
v288 fixed three (#3, #4, #8) — confirmed. But "five remain" is
true only as "five not fixed *by v288*": of those five, three
(#1, #2, #7) were already fixed by v286/v287, and **two remain
live (#5, #6)**. The live class after v288 is exactly the two
address-printing traps: `likha` on a kosh and a string stored into
a mala. (v288's kosh-operand refusal covers all kosh binops —
`kosh + 1` refuses too — but **not** mala or rachana: `mala ==
mala` still prints `0` and `rachana == rachana` still prints `0`,
confirming ChatGPT R175's open reference-type class.)

## WS4 — the count command, one line

`ls examples/*.sm | wc -l`

## What this round did NOT do (NOT RUN)

Windows (PE aliasing, installer rebuild, wizard), browser,
implementation (the arena design is assessed, not built; the
post-block-use check question is for the design), native-speaker
review. The full suite, proofs, gates, and guard were not re-run:
no `src/`/`lib/`/`examples/`/`tests/` file changed in this round,
and the brief's suite/guard/gate numbers (283, 693 0 DIFFER,
59 PASS / 1 FAIL / 1 NOT-RUN) are cited, not re-measured. RSS
beyond the WS2 probe programs was not measured.

## Deliverables

- `Muse-to-Sarvam/ROUND-103-ARENA-COUNT-COST-CENSUS-TRAPS.md`
  (this report)
- `Muse-to-Sarvam/r103_census.json` (WS1 count + list, WS2
  measurements + cap, WS3 counts + eight-trap table, WS4 command)
- `Muse-to-Sarvam/scan_mandapa_kosh_v2.py` (the WS1 scanner:
  braced + indented blocks, typed decls, alias-aware post-block
  uses; run as `python3 scan_mandapa_kosh_v2.py [tree]`)
- `Muse-to-Sarvam/measure_kosh_cost.py` (the WS2 measurement
  script: generates N-kosh probe programs, blocks on input, reads
  `/proc/<pid>/status`; run as `python3 measure_kosh_cost.py`)

Work staged in `~/workspace/r103/` (scripts in `ws1/`/`ws2/`/`ws3/`,
probes in `ws2/probes/`, worktree in `tree/` — read-only, removed
after delivery).

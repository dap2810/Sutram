# Sutram — ROUND-104: the count holds on v289, the five traps with their programs, and the generator now doing its job

**Base:** `origin/main` at `416637b6` (compiler v289).
**Deliver into:** `Muse-to-Sarvam/`. **No tree changes by this round,
and no compiler implementation** — the two scripts delivered are
tools (a scanner and a generator extension), not compiler code.

## Where the project is (premise notes)

v289 adds the escape error in two forms plus `parimana()`: the
compiler refuses a visible alias-store at compile time (287's
golden is now the compile refusal — nothing is built), and the
runtime check still stops what the compiler cannot see (316, a
kosh leaving through an identity function, stops with runtime
`E_KOSH_MANDAPA`, exit 1). Suite 285, guard 695 programs (1
DIFFER, example 287, intended — its golden changed), gates
59 PASS / 1 FAIL (installer v243 vs v289) — cited from the brief,
not re-measured. **Examples are 289 on this base, not 287:**
v289 added 316 and 317, so the brief's resolved 287/283/4 is the
v288 resolution — the resolution itself holds (files ≠ passes),
with v289 numbers 289/285/4 (see WS4). ChatGPT's files-vs-passes
distinction is credited as the brief states it.

## WS1 — verify it on v289: the count holds, and the escape error is not stricter

**Re-run on v289 (scanner v3, alias-aware including
call-mediated aliases): 4 examples make a kosh inside a mandapa;
2 use it after the block; 0 running programs break.**

| example | kosh | used after | how it ends today |
|---|---|---|---|
| 286 | `k` | no — read inside only; the block returns a value `s` | runs, unchanged |
| 299 | `m` | no — pushed, read, passed to `pratham` inside only | runs, unchanged |
| 287 | `k` | **yes — via alias** `bahar = k` inside, `padh(bahar, 0)` after | **compile-refused** (`E_KOSH_MANDAPA`, nothing built) |
| 316 (new on v289) | `k` | **yes — via call-mediated alias** `bahar = rakh(k)` inside, `padh(bahar, 0)` after | **runtime-stopped** (`E_KOSH_MANDAPA`, exit 1, after printing 11) |

R103's number — zero running programs break — **holds on v289**.
The textual after-count grew from 1 to 2 (316 added), but both
after-users are error examples that do not complete; no live code
breaks. The scanner had to be fixed to see 316: a call-mediated
alias (`bahar = rakh(k)`, where `rakh` returns its argument) is
an alias, while a call that reads an element (`s = s + padh(k,
i)`, where `padh` returns `k[i]`) is not — the v3 scanner
distinguishes identity functions (body returns the parameter
itself) from readers, and the 286 false positive that a naive
"RHS mentions k" rule produces is gone.

**Is the escape error stricter than the census assumed? No.**
Every example on v289 was compiled (289 files): 61 fail to
compile, and **every one fails exactly as its golden expects**
— 58 are deliberate compile-error examples (capacity, scope,
module, parikshita, escape, and refusal goldens, including 287),
and 3 are flag artifacts (37/38/39 need `--lang gujarati/hindi/
tamil`, per the suite's own table — they compile with the flag).
**Zero passing programs are refused.** The escape error refuses
exactly the census's cases (287, and nothing else new) — it is
not stricter. For the arena build, both checks are load-bearing:
287 proves the compile check, 316 proves the runtime check, and
removing either changes a golden.

## WS2 — the five traps that remain (not fixed by v288), with the program for each, and the generator question

**First, the reconciliation (stated again because the brief
repeats "five").** Five were not fixed *by v288* (#1, #2, #5,
#6, #7). Of those five, three no longer misbehave on v289
(fixed by v286/v287, verified below). **Two remain live (#5,
#6).** The five, with their programs and their v289 status:

**#1 — SUB/MUL/DIV on strings (fixed by v287, still fixed).**
Program: `s = "abcd"`, `t = "wxyz"`, then `likha(s - t)`,
`likha(s * 2)`, `likha(s / 2)`. On v289: refuses
`E_VARTANI_GANIT` (at `s - t`). It no longer prints `-17` /
`8388922` / `2097230`.

**#2 — string ordering (fixed by v287, still fixed).**
Program: `a = "b"`, `b = "a"`, then `likha(a < b)`,
`likha(a > b)`. On v289: `0`, `1` — content order, correct.
(The old output was `1`, `0` — pool address order.)

**#5 — `likha(kosh)` (LIVE on v289).**
Program: `kosh k[2]`, `kosh_push(k, 7)`, then `likha(k)`. On
v289: prints an address (`135568688152592`), not contents.
The v288 likha fix covers strings, not koshes.

**#6 — string into mala (LIVE on v289).**
Program: `mala a[2]`, `s = "hi"`, then `a[0] = s`,
`likha(a[0])`. On v289: prints an address (`4194681`), not
"hi". The v288 mala-store fix covers dasham, not strings.

**#7 — string + dasham literal (fixed by v286, still fixed).**
Program: `likha("x" + 2.5)`. On v289: refuses
`E_VARTANI_CAT`. (On v285 it printed `4194456.500000`.)

(#3, #4, #8 stay fixed on v289: truthiness refuses
`E_VARTANI_SATYA`, kosh== refuses `E_KOSH_GANIT`, dasham→mala
stops `E_DASHAM_VITTI` exit 1 — no regression.)

**The generator question, answered honestly: originally by
hand; now the generator does the job.** v1/v2 covered binops
only, and the hand-found traps live in the columns they did not
cover. Per trap:

| trap | found by | generator v1/v2 | generator v3 (this round) |
|---|---|---|---|
| #1 string arithmetic | generator (matrix cells silent-wrong on v286) | finds | — |
| #2 string ordering | **hand** — the matrix's "ab"/"cd" pair blinded it (pool order agreed with content order for that pair; the b/a probe exposed it) | **missed** (pair selection matters) | — |
| #3 truthiness | **hand** (condition column not covered) | missed | finds (string conditions refuse) |
| #4 kosh == | generator (matrix kosh×kosh == → 0) | finds | — |
| #5 likha(kosh) | **hand** (print column not covered) | missed | **finds** (print kosh → address) |
| #6 string→mala | **hand** (store column not covered) | missed | **finds** (store string → address) |
| #7 string+dasham | **hand** (R100 probe on v285); v1 on v286 confirmed closure (refused) | confirms closure | — |
| #8 dasham→mala | **hand** (store column not covered) | missed | finds (store dasham → runtime refusal, the fixed behavior) |

**v3 (delivered, `trap_matrix_v3.py`)** adds the three missing
columns — conditions, prints, stores — for all 7 kinds (int,
dasham, string, empty string, kosh, mala, rachana): 21 probes.
On v289 it finds **11 trap cells** (conditions: kosh/mala/
rachana all truthy, `1` — the composite version of #3;
prints: kosh/mala/rachana all addresses; stores: string,
empty-string, kosh, mala, rachana all addresses) and confirms
the fixes (string conditions refuse, string prints as text,
dasham-into-mala runtime-refuses for fractions). The generator
is no longer binops-only: the classes the hand-found traps
belong to are now generator-findable. (The two live traps, #5
and #6, are v3 cells: print-kosh and store-string.)

## WS3 — the cost of a kosh on v289: the same numbers, re-measured

Re-measured on v289 with the R103 script (probe programs
blocking on input while `/proc/<pid>/status` is read; peak RSS
is `VmHWM`, virtual is `VmSize`).

| live koshes | peak RSS (VmHWM) | virtual size (VmSize) |
|---|---|---|
| 0 (baseline) | 16 kB | 240 kB |
| 1 (declared / touched) | 28 / 24 kB | 65,776 kB |
| 10 (declared / touched) | 64 / 68 kB | 655,600 / 655,604 kB |
| 100 (declared / touched) | 428 / 464 kB | 6,553,848 / 6,553,884 kB |
| 1,000 | **cannot be built** (same compiler cap) | — (extrapolated: 64 GiB virtual, ~4 MB RSS) |

Unchanged from v288 within page noise (a few kB of baseline
drift): still exactly 64 MiB of virtual address space per kosh
and ~4 KiB of resident pages each. **64 MiB reserved per
collection is harmless because it is virtual** — 100 koshes
reserve 6.4 GiB of address space and use under 0.5 MB of RAM.
One distinction for `parimana()` (317): it measures *held*
bytes (a kosh's header + capacity × 8 bytes), not the 64 MiB
reservation and not resident pages — so it does not settle the
virtual question; the `/proc` numbers above do.

## WS4 — the count, both numbers side by side

`python3 -c "import os,glob; fs=sorted(glob.glob('examples/*.sm')); g=[f for f in fs if os.path.exists('tests/expect/'+os.path.basename(f)[:-3]+'.out') or os.path.exists('tests/expect/'+os.path.basename(f)[:-3]+'.exit')]; print(f'files={len(fs)} passes={len(g)} no-expectation={len(fs)-len(g)}')"`

Run from the repo root, it prints on v289:

`files=289 passes=285 no-expectation=4`

"Passes" here means "has a golden" (`.out` or `.exit` in
`tests/expect/`) — which equals suite passes on a green tree,
and the brief's suite 285 confirms green on v289. The
resolution holds with the new counts: files (289) ≠ passes
(285); the difference is exactly the 4 without an expectation
(215, 216, 217, 219 — the same four). The brief's 287/283/4
was v288; v289 added 316 and 317, moving both numbers by two
and leaving the difference at four.

## What this round did NOT do (NOT RUN)

Windows (PE aliasing, installer rebuild, wizard), browser,
implementation (no compiler changes — the v3 scanner and v3
generator are tools, not compiler code), native-speaker review.
The full suite was not re-run: no `src/`/`lib/`/`examples/`/
`tests/` file changed in this round, and the brief's suite/
guard/gate numbers (285, 695 with 1 intended DIFFER, 59 PASS /
1 FAIL / 1 NOT-RUN) are cited, not re-measured — corroborated
for passes by the compile audit (every compile failure matches
its golden) and the golden-count command above. RSS beyond the
WS3 probe programs was not measured.

## Deliverables

- `Muse-to-Sarvam/ROUND-104-COUNT-HOLDS-FIVE-TRAPS-GENERATOR-V3.md`
  (this report)
- `Muse-to-Sarvam/r104_census.json` (WS1 v289 count + stricter
  audit, WS2 five programs + generator verdicts + v3 results,
  WS3 v289 cost table, WS4 side-by-side command and counts)
- `Muse-to-Sarvam/scan_mandapa_kosh_v3.py` (the WS1 scanner:
  braced + indented blocks, typed decls, identity-aware aliases;
  run as `python3 scan_mandapa_kosh_v3.py [tree]`)
- `Muse-to-Sarvam/trap_matrix_v3.py` (the extended generator:
  conditions, prints, stores × 7 kinds; run as
  `python3 trap_matrix_v3.py [compiler]`, default
  `./sutram_compiler`; writes `trap_matrix_v3.json` beside
  itself)
- `Muse-to-Sarvam/trap_matrix_v3.json` (the generator's first
  run on v289: all 21 probes)

Work staged in `~/workspace/r104/` (scripts in `ws1/`/`ws2/`,
probes in `ws2/probes_v3/`, worktree in `tree/` — read-only,
removed after delivery).

# R80-00 — Division by zero stops with a message; written numbers that do not fit are refused; run-time overflow measured and left wrapping; the library stops lying

- **Commits on `main`, in order:** `a562b4c` (1/4 **v276**: the compiler, examples 277–281, the fuzzer and mutator changes) · `343c878` (2/4 the library and its tests) · `4c98595` (3/4 reference §3a and the changelog) · then this hand-back with `evidence-r80/`, on top of Muse's `9a11ad0`. Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v276) - sampurna sutra`.** Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=249`, FAIL=0** (five new examples, 277–281). Library proofs **229/229** (one new: `r80_library_edges`). Property
  proofs **86/86**.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 55 PASS / 0 FAIL / 1 NOT-RUN (Windows execution)** — the valid-fuzzer gate needed the change below; R29 caught a module-name bug in my first build (fixed). Guard pages: controls 5/5, suite 249/0, 0 failed. **One earlier run had guard pages 1 FAIL**: `examples/268` timed out (5 s) in the guard-page build while Wine was loading both cores; its binary is byte-identical to v275's and it has no division; it passes on a quiet machine, where this gate line was taken.
- **The guard, v275 (origin/main) → v276, `tools/guard_pair.py`, all three paths (Linux ELF, Linux PE, the Windows
  compiler under Wine): 659 programs — 353 byte-identical, 122 refused identically, 178 DIFFER, 6 new.** No
  program moved between compiling and being refused. The Windows compiler's 531 outputs are byte-identical to the
  Linux compiler's PE outputs. **I ran every DIFFER, old and new, ELF and PE under Wine: both paths — 175 give the
  same output and exit code; 3 change, all on purpose:** `tests/r65_check/trap_div` and `trap_mod` used to die
  by SIGFPE and now print the named error; `tests/stdlib/numeric29` prints the library's new contract (below).
  The 178 are every program that divides by a variable, including inside library code, which now carries the
  zero check (`evidence-r80/guard-differ-outputs.txt`).

## WS1 — the three lies, before and after

| | v275 | v276 |
|---|---|---|
| `x + 1`, x = 9223372036854775807 | −9223372036854775808 | the same — run-time wraparound, measured and kept (WS2.3) |
| **`9223372036854775807 + 1` written** | −9223372036854775808 | **refused when compiled** |
| `x * x`, x = 4000000000 | −2446744073709551616 | the same, documented |
| **`4000000000 * 4000000000` written** | −2446744073709551616 | **refused when compiled** |
| **`a / b`, b = 0** | **SIGFPE, exit 136, no message** | **`Sutram Error [E_SHUNYA_BHAJAN]: pankti 4 - shunye vibhajanam na sambhavati`, exit 1** |
| `1 / 0` written | SIGFPE at run time | refused when compiled |

All 27 cases, both versions: `evidence-r80/confirm-runs-v275-v276.txt`.

## WS2 — what v276 does

### 1. Division by zero stops, with the line

`/` or `%` by a divisor that is not a written number gets `test rcx,rcx` before the `idiv`. Zero prints
`Sutram Error [E_SHUNYA_BHAJAN]: pankti N - shunye vibhajanam na sambhavati` (*division by zero is not
possible*; for `%`: `shunyena sheshah na sambhavati`) and exits 1. **N is the line in the student's own file**:
a `yoj` before it does not shift it (my first build said `pankti 220` for line 5 of a program with `yoj ganit` —
the line counted through the merged library; fixed before shipping, through the origin map every other error
uses). **Inside a module, it names the module: `pankti 3 (r80_ausat.smlib)`** — `examples/281`, the same under
`--separate` (the R29 gate caught that the first version dropped the name there). `/=`, `%=` are covered.

**A divisor written as `0` is refused when compiled**, with the line and a caret:
`prog.sm:2:13: Sutram Error [E_SHUNYA_BHAJAN]: shunye vibhajanam na sambhavati`.

**The smallest `vitti` divided by −1 no longer crashes:** it wraps to itself (the rule `+ - *` already follow),
and `% -1` is 0. v275 died with SIGFPE.

**Cost:** a divisor that is a written number other than 0 or −1 gets no check. **The 8 shipped benchmarks compile
to the same bytes as v275** (re-checked on the final build). A loop that divides by a variable: +6.3%. The R79
report program: −3% (noise). `evidence-r80/ws2-overflow-check-cost.txt`.

### 2. A number that does not fit is refused when compiled

- **A written whole number past 64 bits** (`99999999999999999999` printed 7766279631452241919;
  `0x10000000000000000` printed 0): `prog.sm:4:11: Sutram Error [E_ATIPRAVAH]: ankah 64-bit
  purnanka-seemam atikramati` / `Sanket: purnankah -9223372036854775808 tah 9223372036854775807 paryantam`.
  **`-9223372036854775808` and `0 - 9223372036854775808` are still allowed** — they are the smallest `vitti`, and
  three property proofs use them. `0 - 1 - 9223372036854775808` is refused.
- **Arithmetic on written numbers whose answer does not fit** (`4000000000 * 4000000000`,
  `9223372036854775807 + 1`, `-(0 - 9223372036854775808)`): `... sthira-gananayah phalam 64-bit purnanka-seemam
  atikramati` / `Sanket: ...; ganana punah likhyatam` (*write the calculation again*), caret under the operator.
- **Found while doing it, and fixed: the compiler itself crashed** on a written `(0 - 9223372036854775808) / (0 - 1)`
  — its constant folder ran `idiv` and died with SIGFPE (exit 136), in v275 and before. Now refused; `MIN % -1`
  written is 0.
- **And a `dasham` literal past 2⁶³ now has its value.** v275 read `100000000000000000000.5` as
  7766279631452241919.5 (the integer part wrapped). My first build refused it, which is wrong for a float; the
  lexer now carries the integer part as a double too.

### 3. Run-time overflow checking: measured, and **not shipped**

The trap build (`SUTRAM_R65_TRAP_INT`: `jo` after every `+ - *`, plus the division checks), 9 interleaved runs,
medians:

| benchmark | cost |
|---|---|
| bench_fib | +5.6% |
| r46_hotcall_float | +11.9% |
| r46_hotcall_nested | +17.6% |
| r46_hotcall_array | +22.5% |
| r46_hotcall_stack | +34.5% |
| bench_arith | +39.3% |
| bench_nested | +103.7% |
| **bench_loop** | **+281.9%** |
| the R79 report program (100,000 students) | +4.7% |

**Over your 10% line on 7 of 8. So run-time `+ - *` wrap, as in C, and the reference says so.** §3a, the sentence
a student reads:

> **A `vitti` holds a whole number from −9223372036854775808 to 9223372036854775807. If `+`, `-` or `*` goes past
> that while the program runs, the answer wraps around to the other end without any warning — as in C or Java —
> so `x * x` with `x = 4000000000` prints `-2446744073709551616`. Dividing by zero stops the program with an
> error.**

Below it, a table of every edge, and where to go when you need to know (`ganita_janchit_*`, `ganita_paripurna_*`).
`examples/280` pins the run-time behaviour. The trap build still assembles and is unchanged as an opt-in.

## WS3 — the library: 12 functions returned wrong answers on plausible input; all fixed

I called each of the 62 library functions that take only numbers with plausible non-negative inputs and flagged
negative results (`evidence-r80/ws3-library-sweep-before-after.txt`):

| function | v275 | v276 |
|---|---|---|
| `kramgun(21)` (factorial) | −4249290049419214848 | **−1** (does not fit); `kramgun(20)` = 2432902008176640000 |
| `fib(93)`, `matra_meru(93)` | −6246583658587674878 | **−1**; `fib(92)` exact |
| `varg(3037000500)`, `vargit(…)` | −9223372036709301616 | **−1** |
| `dwi_ghat(63)` (2⁶³) | −9223372036854775808 | **−1** |
| `yog_tak(10¹⁰)` | −5340232216128654848 | **−1** |
| `ghan(10⁹)` (cube) | −6930898827444486144 | **9223372036854775807** (saturates, by sign) |
| `ghat(2, 63)` (power) | −9223372036854775808 | **9223372036854775807** (saturates, by sign; `ghat(−2, 63)` is exact MIN) |
| **`laghuttam_samapavartya(4000000000, 4000000001)`** (lcm) | **2446744069709551616** — a plausible wrong *positive* | **−1** |
| **`purna_prasaran([2³¹, −2³¹])`** (integer variance) | **−4611686018427387904** — a negative variance | **4611686018427387904**, exact (the sum of squares is never formed) |
| **`yog_seema(0, 4294967295)`** (range sum) | −2147483648 — **though the answer fits** | **9223372034707292160**, exact; past int64 it saturates by sign |

**The sweep sees only negative wraps, and that hides some.** `kramgun` was negative on 5 inputs but returns −1 on
20 now: the other 15 were **wrong positive answers** — `kramgun(25)` was 7034535277573963776. **The last three rows
are Muse's** (`Muse-to-Sarvam/ROUND-80-LIBRARY-OVERFLOW-AUDIT.md`, `9a11ad0`, pushed while I worked — I found it
when I fetched to push): my sweep missed them, because the lcm wrap comes out positive, the variance needs an
array, and `yog_seema`'s wraps on my values came out positive too. Checked against Python's exact integers and
pinned in **`tests/stdlib/r80_library_edges`** (library proofs now 229), which fails on v275
(`evidence-r80/ws3-muse-tier1-fixed.txt`). Muse's only library *crash*, `sadhan.shesh(MIN, -1)`, is fixed by the
language change: v276's `MIN % -1` is 0. Every remaining negative in my sweep is a documented sentinel or a true answer. The property proofs that pinned the old wrapped
values (`tools/proof_props.py`, "math plain wrapping") now pin the new contract.

**Your three named cases:**
- **`ganita` factorial: already right.** `ganita_janchit_kramgun(21, ok)` gives 0 with `ok[0]` = 0, and
  `ganita_paripurna_kramgun(21)` gives 9223372036854775807 (R20/R21); `kramgun(20)` and both at 20 are exact. The
  plain factorial that wrapped was `ganit.kramgun` — fixed above.
- **`sankhyiki` sums: correct on plausible data** — the integer sums overflow only when the total passes about
  9.2×10¹⁸ (Muse agrees: plain sums are not Tier 1). **But its integer variance was not** (the row above).
- **`madhava` terms: floats, they cannot wrap.** But the argument reduction has an integer step, and the comment
  overstates the range: `madhava_sin` is right to 6 places up to about 10¹⁰, off by 0.007 at 10¹⁴, 0.0 at 10¹⁹, and
  past ~5.8×10¹⁹ the integer step passes 2⁶³ and `sin`/`cos` return a huge number. Not plausible input; **not
  changed**; the comment should say 10¹⁰ (`evidence-r80/ws3-madhava.txt`). Muse found the same — madhava is not
  broken on ordinary inputs; its large-input "failures" were the literal parser, fixed in WS2.2.
- **Still wrapping, only near 2⁶³** (Muse's Tier 2): `dvigun`, `trigun`, `vardh`, `viparyay_ank`,
  `nirapeksh_mulya(MIN)`, `purna_vyapti`, `mala_yog`/`purna_yoga`/`purna_madhya` on MAX-scale values; and
  `kuttaka(2, 0, 5)` (a zero modulus) returns 2. Not changed this round.

## Two tests changed, both because the language changed

- **`tools/fuzz_valid.py`** (gate "valid fuzzer"): its programs wrote `+ - *` of two written numbers and expected
  them to wrap; v276 refuses 19 of the 60. The generator and the reference are untouched (every seed's programs
  stay the same); the *writer* now puts such an operand as `(1 ? A : 0)` — same value, not folded. I checked the
  model of the folder is exact: unrewritten, all 19 are refused. **60/60 agree, the same 1,376 output lines, on
  v275 and v276**; seeds 7 (300) and 8 (200) also all agree (`evidence-r80/fuzz-valid-rewrite.txt`).
- **`tests/r77_format/test_format_mutator.py`:** the `blank_ws` mutation inserts lines, so `examples/277`'s
  `pankti 7` moves; the harness now computes where the line goes (it does not ignore it), and leaves a module's
  line alone.

## Found, not fixed

**`likha` of a `dasham` from about ±9.2×10¹² prints `-9223372036854.775808`**, whatever the value — v275 too.
I first wrote "from 2⁶³"; **Muse measured it right**: the printer scales by 10⁶ into a `vitti`, so
`10000000000000.0` already prints garbage (checked). A fix changes every float-printing binary, so it is yours to
schedule. Written into §3a as "not yet right".

## What I did not do

- **No run-time overflow check** — by your rule and the measurement.
- **The frozen packs got no new text.** The two new messages print in Sanskrit in every pack (checked with
  `--lang hindi`, `evidence-r80/confirm-pe-module-hindi.txt`).
- **Not run:** real Windows (Wine only).
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`.

**Document counts:** `doc_counts_gate` NOTEs (`evidence-r80/doc-counts.txt`): 18 documents still carry older numbers (suite 225 → 249, library proofs 226 → 229, functions 305 → 306) — `README.md`, `docs/sutram-design-parameters.html`, `docs/sutram-project-status.html`, `docs/sutram-scorecard.html` and others. Not bumped: the prose is yours.

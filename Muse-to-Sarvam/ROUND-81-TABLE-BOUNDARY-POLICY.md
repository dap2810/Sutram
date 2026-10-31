# Sutram — ROUND-81: the R80 table, the `parikshita` count, and the policy tested

**Base:** main at ca8883a4, compiler v276
· **Deliverable:** this report
· **No tree changes.**

## WS1 — the R80 table, summarised (and updated for v276)

### The headline, as measured on v275 (R80)

**11 library functions overflow on an input a student would plausibly
write, out of 306. 22 overflow or crash on some int64 input. 284 do
not.** (The brief says 305; the library has 306 since `kuttaka_gun_shesh`
— R78. The count out of 305 is 11 / 21, since that function is safe.)

### The worst three

1. **`laghuttam_samapavartya` (lcm) — the worst, because the error is
   invisible.** (4000000000, 4000000001) returned **2446744069709551616**,
   a plausible-looking positive, for the true 16000000004000000000.
   The implementation wrapped the product to a negative and then took
   its absolute value, un-negating it into a wrong positive. A negative
   answer would at least look wrong.
2. **`purna_prasaran` (integer variance) — a mathematically impossible
   value.** [2147483648, -2147483648] returned **-4611686018427387904**.
   Variances are never negative; a student trusting this gets nonsense
   downstream with no signal.
3. **`kramgun` (factorial) — the classic.** 21 returned
   **-4249290049419214848**. Every student computing factorials past
   20 hits it, and a negative factorial is silent, not an error.

The other eight Tier-1 rows: `ghan` (cube past 2097152), `varg` /
`vargit` (square past 3037000500), `ghat` (2^63, 10^19), `dwi_ghat`
(2^63), `matra_meru` (Fibonacci 93), `yog_tak` and `yog_seema` (sums at
the 2^32 boundary). The pattern behind all eleven: it is the
*products* that overflow on ordinary magnitudes (squares, cubes,
powers, factorials, lcm, variances). Plain sums do not — [4000000000,
4000000000, 4000000000] sums correctly to 12000000000.

### What v276 changes (re-verified this round, all 11 + Tier 2)

**Zero of the eleven wrap anymore.** `kramgun(21)`, `fib(93)`,
`matra_meru(93)`, `varg`, `vargit`, `dwi_ghat(63)`, `yog_tak`,
`laghuttam` all return **-1**; `ghat`, `ghan`, `yog_seema` return **MAX**
(saturate); `purna_prasaran` returns the **exact** value whenever it
fits ([2^31, -2^31] → 4611686018427387904, correct) and **-1** when it
does not ([4e9, -4e9] → -1). One correction to R80, owned here: R80
tested `matra_meru` but missed `ank.fib` (the ank module's own
Fibonacci, a second function with the same overflow); Claude's fix
covered it, and `fib(93)` = -1 is verified here.

What remains on v276: the Tier-2 rows still wrap — `dvigun`,
`trigun`, `nirapeksh_mulya` (abs of MIN), `vardh` (MAX+1),
`viparyay_ank` (19-digit reversal), `purna_vyapti`,
`mala_yog` / `purna_yoga` / `purna_madhya` (all at [MAX, 1]) — nine
functions, all needing extreme inputs; plus the `kuttaka(2, 0, 5)` =
2 lie (degenerate modulus, not an overflow — not in Claude's fix
list). And one fix worth naming: `shesh(MIN, -1)` no longer traps —
on v276 it returns **0**, which is also the mathematically correct
remainder. The v276 headline is therefore: **0 plausible-input wraps
remain; 10 extreme-input lies remain.**

The brief's verified behaviours were spot-checked on v276 and hold:
scratch `buf + 64` stored outside its block → `E_SCRATCH_ESCAPE`;
`outer = buf[0]` → 42, allowed; `nirmmita(-1)` as a literal →
`E_NIRMMITA_RNA`; runtime `1 / z` and `5 % z` (z = 0) →
`E_SHUNYA_BHAJAN` with the line, exit 1.

## WS2 — how much of the library can become `parikshita` as-is?

**281 out of 306 functions (280 out of the brief's 305) — by the
brief's rule: no `kosh` in the function, and no call to a function
that has one.**

The count was built from the sources, not estimated: every function
in `lib/*.smlib` (braced and indented bodies both, comments and
string literals stripped so they cannot fake a call edge), a call
graph over the 306 unique names, and a fixed-point closure (a
function is eligible only if every library function it calls is
eligible).

Composition of the 281:

- **184 are leaves** (call no other library function) — pure
  arithmetic, formatting, predicates. These are parikshita-shaped
  trivially.
- **97 call other eligible functions** — the closure costs nothing
  here, for a reason worth stating: **the transitive shrinkage is
  zero.** No kosh-free function calls a kosh function anywhere in the
  tree. The kosh world is closed.
- **4 are recursive and otherwise eligible** (`madhava_atan`
  (self-recursion for |x| > 1), `mil_shreni_punar`,
  `roop_ank_aadhar`, `viparyay_ank`) — eligible if self-calls are
  allowed, which the brief does not rule out.
- **26 eligible functions use `nirmmita`** (raw blocks, not kosh) —
  flagged, not excluded: the existing kind check does see nirmmita
  blocks, so whether parikshita allows them depends on its check's
  design, which this round does not assume.

Where the 25 excluded functions live: **kalana 0/6, samanvaya 1/11
(only the shape guard `samanvaya_akar_ayogya`), sankhyiki-dasham 0/9.**
The float statistics/matrix world is entirely outside the boundary;
the integer world, the containers-on-blocks world (`suchi` 34/34,
`nighantu` 17/17, `sangrah` 14/14 — lists, maps, and sets built on
blocks, not on kosh), and every formatting/conversion module are
inside it.

### The sensitivity Sarvam should see

The brief's rule names only kosh ("the check cannot see through a
container"). But the existing check is blind to *every* container
passed as a parameter — params have kind none (R73/R74), whether the
container is a kosh, a mala array, or a list/map/set handle. Under
that stricter reading — no kosh, no memory access through a parameter
(direct indexing or `pad8`/`likh8` through the parameter or an alias
of it), transitively closed — the count falls to **128 out of 306**.
That cut also treats ok-cell out-params as containers, so it is a
lower bound under the strictest reading, not a second headline. The
conclusion does not depend on which reading is right: **the boundary
is not a feature for new code only.** Even the strictest reading
(128, 42%) is far above the brief's "20 out of 305" scenario, and by
the brief's own rule it is 92% of the library. Most of the library
can cross the boundary without rewriting; what cannot cross is
concentrated in three modules (kalana, samanvaya, the dasham half of
sankhyiki).

## WS3 — the overflow policy, tested

### The sentence a student reads (reference §3a, v276)

> "If `+`, `-` or `*` goes past [the int64 range] while the program
> runs, the answer wraps around to the other end without any warning
> — as in C or Java — so `x * x` with `x = 4000000000` prints
> `-2446744073709551616`. Dividing by zero stops the program with an
> error."

Plus, in the same section: written numbers that do not fit, and
constant arithmetic past int64, are **refused at compile time**
(`E_ATIPRAVAH`); the library's number functions "do not wrap on
ordinary inputs" — nine return **-1** when the answer is too large,
three (`ghat`, `ghan`, `yog_seema`) return **the largest or smallest
`vitti`**; and, honestly admitted: "Not yet right: `likha` of a
`dasham` of about 9223372036854.775808 or more prints
`-9223372036854.775808`" (the R80 printer finding, still present on
v276 — re-verified: `likha(10000000000000.0)` prints the MIN
rendering).

### What was tested against that sentence

| Program | Result | Sentence holds? |
|---|---|---|
| `likha(4000000000 * 4000000000)` (literals) | refused, `E_ATIPRAVAH`, caret under the operator | Yes |
| `likha(3 * 3 * … * 3)` (40 literal threes) | refused, `E_ATIPRAVAH` — the compiler folds chains, not just single operations | Yes |
| `likha(1 / 0)` (literals) | refused at compile time ("divisor must not be zero") | Yes |
| `vitti z = 0; likha(1 / z)` / `likha(5 % z)` | `E_SHUNYA_BHAJAN` with the line, exit 1 | Yes |
| Loop computing 3^40 by repeated `*` | -6289078614652622815 (the wrapped value, as the brief states) | Yes — documented runtime wrap |

The literal/chain cases were the most likely counterexample, and they
do **not** break the documentation: written-number arithmetic is
refused even in chains. The documentation's sentences hold for
everything in that table.

### The programs where a student follows it and still gets a wrong answer

**Program 1 — the saturation check that cannot fire.**

```
vitti c = ghan(3000000)
yadi (c < 0) { likha("overflow") } anya { likha(c) }
```

Verified on v276: prints **9223372036854775807** — MAX presented as
if it were 3000000³ (true: 27000000000000000000). The student followed
the headline sentence ("wraps around to the other end" — for a
positive overflow, the wrapped value is negative) and wrote the
natural check for it. That check works for wrapping operators and for
the nine -1 functions (-1 is negative). It **fails for the three
saturating functions**, whose overflow value is MAX — positive. The
saturation behaviour lives in a later paragraph ("return the largest
or smallest `vitti`"), and the student must additionally remember
*which* functions saturate (ghat, ghan, yog_seema) versus which return
-1 (the other nine) versus which wrap (operators and the nine Tier-2
functions). The documentation is now a **three-way behaviour table**,
but it is written as sentences; the headline sentence teaches the
check that fails for one of the three ways.

**Program 2 — the sentinel fed back in.**

```
likha(kramgun(kramgun(21)))
```

Verified on v276: prints **1**. The inner call returns -1, exactly as
documented. The outer call receives -1 — and `kramgun(-1)` returns 1
(the loop never runs; factorial of a negative is undefined, but the
function does not refuse it). The -1 contract protects only the
student who checks for -1 at *every* use. The library itself does not
check it: its own functions accept the sentinel as an ordinary input
and return a plausible-looking value. The same shape in ordinary code
— `kramgun(21) + kramgun(20)` = 2432902008176639999, a confident
number with no signal — is how a student actually meets this.

### Verdict on WS3

**The documentation is not enough as written — not because any
sentence is false, but because the behaviour is now three-way and
the sentences do not carry the table.** Every sentence tested above
is true. But a student who reads the headline sentence and writes the
obvious check, or who uses a -1 result without checking it, still
gets a wrong answer, and neither failure is warned against where the
student is reading. The minimal fix is a table in §3a, not more
prose: which functions wrap, which return -1, which saturate — plus
two warnings that belong next to it: "check for -1 *and* for MAX"
(the negative check alone misses saturation) and "never feed an
unchecked -1 into another function" (the library does not check it
for you). The printer hole is separate and already admitted in the
doc; it stays a live bug, not a documentation gap.

## Method and caveats

- Built from `src/r68_compiler_entry.asm`; all probe results above
  are from the built v276 binary; the tree was reset to `origin/main`
  after the runs (tracked `./sutram_compiler` restored).
- WS2's analyzer: comment/string-stripped sources; braced bodies by
  brace matching, indented bodies by indentation runs (11 functions
  use the indented form — the first parser pass missed them, and the
  count was corrected from 295 to 306 against the R78 census before
  any verdict was drawn). "Calls" means a name followed by `(` in the
  body. Builtins other than `kosh_*` are treated as neutral (they are
  not library functions); whether parikshita allows I/O or allocation
  builtins is a design question for its owner, flagged via the 26
  nirmmita-using eligible functions.
- NOT RUN: Windows, browser, implementation (the per-function-class
  table, the `kramgun(-1)` refusal, and the printer fix belong to
  their owners).

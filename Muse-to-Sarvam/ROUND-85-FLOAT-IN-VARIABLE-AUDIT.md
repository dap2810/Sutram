# ROUND-85: does the library compute with floats, and are those answers wrong?

Base: origin/main at v278 (compiler `Sutram 1.0 (v278)`), tree reset
to `825fcfa6` before work. No tree changes. Deliverables in
`Muse-to-Sarvam/`: this report, `R85-REFERENCE-SECTION-ASSUMPTIONS.md`
(the section, updated), and `r85_float_audit.json` (the audit data).

## The rule, pinned first

`vitti` is integer storage; `dasham` is float storage. A `dasham`
value stored into a `vitti` truncates toward zero:

- `vitti f = 3.5` → `likha(f)` prints 3 (the brief's case, confirmed).
- `dasham g = 3.5` → 3.500000 (dasham storage keeps it).
- `vitti h = 0 - 3.5` → −3 (toward zero, not floor).
- A literal prints correctly: `likha(3.5)` → 3.500000.
- A `dasham` division stored into a `vitti` truncates its result:
  `vitti h = 7.0 / 2` → 3.
- An infinity stored into a `vitti` becomes the smallest `vitti`,
  with no fault: `vitti f = 1.0 / 0.0` → −9223372036854775808
  (the x86 `cvttsd2si` indefinite value, as the `roop` code's own
  comment says).
- A large float that fits keeps its value: `vitti g = 10000000000.0`
  → 10000000000.

So the brief's sentence is exact, with one sharpening: it is not
that "a float variable" truncates — it is that a *`vitti`*
truncates any `dasham` put into it, whatever produced it.

## WS1 — the audit: 3 sites, all deliberate, none a defect

Method: for every function in all 24 modules, a site is a `vitti`
declaration-initializer or assignment whose value contains a
float source — a `dasham` literal, a bare `dasham` parameter or
`dasham` variable, a `dasham`-`kosh` element (`xs[i]`), or a call
to a function that itself returns a `dasham` (fixpoint over
`nivartanam` expressions, 29 such functions). A `dasham`-`kosh`
name counts only when indexed: `kosh_len(xs)` returns an integer,
and the first pass wrongly counted 17 such sites (every
`vitti n = kosh_len(xs)` in `kalana`/`sankhyiki`/`samanvaya`) —
those are lengths, not floats, and were removed. No float is
pushed into an integer `kosh` anywhere (bonus check: 0 sites).
One limitation, stated: a function that merely returns an
untyped parameter is not counted as `dasham`-returning, so a
caller passing a float through such a passthrough into a `vitti`
would be missed — but no lib `vitti` assignment calls a
passthrough function, so that gap is empty in the tree.

**Count: 3 sites, 3 functions, 2 modules** (`madhava`,
`roop`). `ganita` and `sankhyiki` have zero sites — their float
work uses `dasham` variables throughout.

The three, worst first (a ranking of deliberate conversions, not
of bugs — there is no defect to rank):

1. **`madhava_sin` (lib/madhava.smlib:53): `vitti k = x / pi2`.**
   The period count for range reduction: `y = x - k * pi2`.
   Truncation toward zero is exactly what range reduction needs
   (for positive `x`, `y` lands in [0, 2π); for negative `x`, in
   (−2π, 0], and the `y < −pi` adjustment then adds 2π). If this
   were a bug, every large-`x` sine would be wrong; it is the
   mechanism that makes them right.
2. **`madhava_cos` (lib/madhava.smlib:73): `vitti k = x / pi2`.**
   The same period count, the same reason.
3. **`roop_sthir_mool` (lib/roop.smlib:539): `rounded = scaled`.**
   The rounding step itself: `scaled = mag * p10f + 0.5`, then
   truncation gives the rounded integer (`intpart = rounded /
   p10i`, `fracpart = rounded % p10i`). The function's header
   says "|x| rounded HALF AWAY", and its own comment discusses
   the `dasham`→int conversion and its overflow guard. The
   truncation is the rounding.

So the brief's fear does not land: `madhava` does store a float
into a `vitti`, but it is the period count, not the answer —
the returned series sum `s` is `dasham` throughout. No lib
function returns "an integer wearing a float's name", and no
published comparison value is invalidated by this audit.

## WS2 — the Madhava verification was valid, not lucky

The Madhava functions use `dasham` variables for everything that
is compared: `madhava_sin`/`cos` carry `pi2`, `pi`, `y`, `s`, `t`
as `dasham`, with `vitti` only for the integer counter `n` and
the period count `k`; `madhava_pi` carries `sum`, `p3`, `term`
as `dasham` with `vitti` only for `k` and the sign; `madhava_atan`
carries `ax`, `r` as `dasham` with `vitti` only for the sign flag.
The two `vitti`-float sites in `madhava` are the period counts,
which feed range reduction (where truncation is correct) and
never enter the series sum.

Re-run on v278 to close it empirically, not just by reading:
`sin` and `cos` at 0, 0.5, 1, 2, 3.14159, 10, 100, 1e10, and
`atan` at 0.5, 1.0, 2.0 — **19/19 match Python's `math` to six
decimals**, including `sin(1e10) = −0.487506` and `cos(1e10) =
0.873120`. The earlier comparison passed because the compared
values never pass through a `vitti`. The one place a float does
pass through a `vitti` in `madhava` is the period count, and
there the truncation is the algorithm.

## WS3 — the section, and whether the four need correcting

`R85-REFERENCE-SECTION-ASSUMPTIONS.md` is the Round 84 section
with the float item added **at the top**, as asked, in the
section's format (assumption, actual, one code line):

> *You assume a decimal number stays decimal wherever you put
> it.* `vitti f = 3.5` → `likha(f)` prints 3.

**None of the other four entries needs correcting:**

- `tak` inclusive — loop counts are integers; float storage
  never touches them.
- `nirmmita` bytes vs `p[i]` qwords — byte and cell counts;
  no floats involved.
- Division truncates toward zero — the integer-division rule is
  separate from storage truncation, and it is still true
  (`-7 / 2` is `-3`). The case that looks like an interaction,
  `vitti h = 7.0 / 2` → 3, is the *float* rule (a `dasham`
  result truncated on storage), not a change to the division
  rule — the section's float entry says so explicitly, so a
  reader does not conflate the two truncations.
- `vitti a = k` aliasing — addresses and lengths, not values;
  a `kosh dasham` element is float storage (no truncation), and
  an alias holds an address (an integer), so the entry is
  unaffected.

Two further corrections and additions, both verified this round
and credited to Claude's R86 (which found them while checking
the Round 84 page):

- **String `+` on variables adds addresses — a correction to
  the Round 84 report, owned.** That report said "string `+`
  concatenates (`"a" + "b"` is `"ab"`)". That was tested on
  literals only, and it is true for literals; for variables it
  is false, verified here: `vitti s = "a"; vitti t = "b"` →
  `s + t` prints 8388922 (an address sum), not `"ab"`. Added to
  the section as a new entry.
- **NaN compares equal to every `dasham` — new, verified.**
  `dasham nan = inf - inf` (with `inf = 1.0 / 0.0`) gives
  `nan == 5` true, `nan == nan` true, `nan != 5` false, and
  `nan != nan` false. This extends the Round 72 note (NaN `!=`
  treats NaN as equal to itself) to every value. It does not
  touch the section's `dasham` division entry, because
  `0.0 / 0.0` is 0, not NaN — NaN here comes from `inf - inf`.
  Added to the section as a new entry.

The section now has 21 entries (18 + float + string-`+` + NaN).
The Windows symptom in the brief ("a positive floating-point
value prints as negative") is a different symptom in the same
area — on Linux the variable truncates (3.5 → 3, never
negative); a positive float printing as negative on Windows
would be a printer/ABI difference, not this truncation, and it
is not reproduced here (NOT RUN covers Windows).

## NOT RUN

Windows, browser, implementation. The audit is a static analysis
of `lib/` as it stands (with the stated passthrough limitation,
verified empty); the Madhava re-run is Linux only (v278 ELF
build). The Windows float-printing symptom is not reproduced.

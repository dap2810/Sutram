# ROUND-89: the last census before release

Base: origin/main at v280 (compiler `Sutram 1.0 (v280)`),
tree reset to `1e2961af` before work. No tree changes.
Deliverables in `Muse-to-Sarvam/`: this report,
`r89_parikshita.json` (the 63 names, by module, with the
first-reason breakdown), and `r89_probes.json` (the v280
probe outcomes behind WS1 and WS3). Method, as in R88: a
script pass over the whole tree, then every candidate read
by hand, then the decisive cases run — the script alone
would have been wrong in both directions this round.

## WS1 — the census, updated for v280

R88 said: NaN reachable in 0 sites, conversion in 5,
`inf` printed in 2. v280 changed the ground in exactly the
way the R88 report anticipated for division — and not at
all for the other two. Three numbers:

### Division-produced `inf`/`nan`: ZERO programs (was 2)

Every form of `dasham` division by zero now stops, with the
same named error, instead of yielding `inf` or `nan`.
Probes run on v280 (all in `r89_probes.json`):

- `1.0 / 0.0` → `E_SHUNYA_BHAJAN: pankti 2 -
  shunye vibhajanam na sambhavati`, exit 1, nothing after
  it printed.
- Computed zero (`z = 0.0; 1.0 / z`) → same error, exit 1.
- Mixed (`5.0 / 0`, int zero divisor) → same error, exit 1.
- `0.0 / 0.0` → same error, exit 1 (so the old `0.0/0.0 = 0`
  behaviour is gone too — it is now a refusal, not a value).
- The R88 sites: 293 (computed zero) matches its golden
  exactly, exit 1; 118's pattern with an empty `kosh`
  (`1.0 / kosh_len(a)`, `a` empty) → same error, exit 1,
  where on v279 it would have printed `inf`; 118 on its own
  inputs still prints `2.000000`, exit 0 (unchanged, as it
  should be — its `kosh` has 3 elements).

So the division path to `inf`/`nan` is closed, for literals,
computed values, mixed types, and library-style helpers
alike. The R88 count of 2 for `inf` printed collapses to 0
*by this path* — but see the next number, because 289 did
not stop printing `inf`.

### Overflow-produced `inf`/`nan` on a program's own inputs: TWO programs, both deliberate

- **291** (`291_r90_nan_compare.sm`): builds `inf` by
  multiplying `10.0` by `10.0` four hundred times, then
  `n = inf - inf`, and prints the IEEE table. Matches its
  golden exactly, exit 0 — including `n == x` 0, `n != x` 1,
  `n < x` 0, `n <= x` 0, `n > x` 0, and `n is not a number`.
  This is the fixture that proves v280's NaN comparisons
  are IEEE, and it is also a program that reaches `inf`
  and `nan` on v280.
- **289** (`289_r87_float_print.sm`, rewritten in v280):
  the same overflow loop, then `likha("inf ", inf)` and
  `likha("nan ", inf - inf)`. Matches its golden exactly,
  exit 0. On v279 it reached `inf` by division and its
  "nan" was actually 0; on v280 it reaches both for real,
  by overflow. The label is now correct.

No other program in the tree reaches `inf` or `nan` on its
own inputs. How that was checked, not just asserted: the
R88 division candidates (28) were re-examined — on v280
every one either refuses (if its divisor were zero) or is
guarded/never-zero, and division no longer yields `inf`
anyway; no literal in examples or library has 30 or more
digits (so no literal is near the ~1.8e308 overflow
boundary — the largest, 289's 1.2e22, is 286 orders of
magnitude below it); and the only `dasham`
multiplications inside loops in the tree are the two
deliberate loops above, plus two library accumulations
(see below), neither of which overflows on tree inputs.

### Conversion sites: FIVE, unchanged, still silent

All five R88 sites are still in the tree, byte-for-byte
the same lines, and still truncate silently on v280:

- Library (3): `madhava_sin:53` and `madhava_cos:73`
  (`vitti k = x / pi2`), `roop_sthir_mool:535`
  (`rounded = scaled`).
- Examples (2): 93 and 94 (`vitti whole = blend(1.0, 4.0)`
  → 2).

Probes on v280: `vitti i = 7.5 / 2.0` → 3,
`dasham d = 3.7; vitti j = d` → 3, while
`dasham e = 3.0; vitti k = e` → 3 (correct — exactly
integral converts correctly, as the brief verified).
No explicit conversion form landed: there is no new
conversion builtin or library function in v280, and the
compiler source itself still says, of this case, "a
computed value (x / pi2) still converts" — silently.
The R88 warning stands: refusing computed truncation now
would break all five, including Madhava core, until an
explicit conversion exists.

### Is any `inf` path left? Yes — overflow, and it is the only one

v280 closed division. It did not close overflow, and
overflow is now the *only* way to reach `inf` (and, via
`inf - inf`, `nan`) in the language. Proved, not assumed:

- Arithmetic overflow: the 10.0 loop (400 multiplications)
  prints `inf`, then `inf - inf` prints `nan`, then the
  IEEE comparisons (`nan == 2.0` → 0, `nan != 2.0` → 1,
  `nan < 2.0` → 0, `inf > 2.0` → 1) — all run on v280.
- Literal overflow: a literal with 400 digits (`1`
  followed by 400 zeros, `.0`) prints `inf` with no
  refusal and the program carries on ("reached" printed).
  v280 refuses division by zero but does not refuse a
  literal that overflows `float64`. No tree program writes
  such a literal — this is a language path, not a tree
  program — but a user program that does will get `inf`
  silently.
- String-parse accumulation (hand-read, not run):
  `vakyank.varna_tak_dashm` multiplies by 10.0 per digit,
  so a 309+ digit input would overflow the same way. No
  tree program feeds it such an input.
- The one accumulation that does *not* leak:
  `roop_sthir_mool`'s `p10f = p10f * 10.0` is guarded by
  `scaled >= 9223372036854775807.0` before conversion,
  and `inf` satisfies that comparison, so an overflowing
  `scaled` returns 0 (empty output), not `inf`.

So the answer to "how many programs in the tree can still
reach `inf` or `nan` by ANY path" is, precisely: **2 on
their own inputs (289, 291, both deliberate, both via
overflow, both also reaching `nan` via `inf - inf`); 0 via
division; 0 other programs on their own inputs; and, with
extreme inputs, any `dasham` arithmetic can overflow —
that is a property of `float64` arithmetic now, not a
hidden division, and the two named accumulation sites are
above.** A student who writes only ordinary programs will
not meet `inf` by accident on v280; a student who
multiplies into the 10^308 range, or writes a 400-digit
literal, will meet it with no message. That is the honest
residual, and it is smaller than R88's — but it is not
zero.

## WS2 — `parikshita`: 63 eligible, 0 marked

**Claude's 63 is confirmed, by a second source, on v280.**
The R82 analyzer was re-run against the current tree
(265 examples, 24 modules, 306 functions — the library is
unchanged since R82 except `roop`'s NaN guard, which does
not change its eligibility: `roop_sthir_mool` was already
KARYA via `akshar_rakh`, and still is):

- Total 306, **markable 63**, with the identical breakdown
  to R82: SMRITI 104 (param index 51, unknown-size 50,
  runtime/reassigned 3), KARYA 75 (`akshar` 18,
  `akshar_rakh` 16, `kosh_len` 14, `likh8` 9, `pad8` 8,
  `vartani_aayam` 7, `dvaram` 3), AHVAN 64.
- By module: `ganit` 17/18, `ganita` 13/23, `ank` 10/10,
  `sadhan` 7/7, `madhava` 5/5, `chandas` 5/6, `varna` 2,
  `anukram` 1, `mala` 1, `samanvaya` 1, `sankhyiki` 1.
  The full 63 names are in `r89_parikshita.json` and
  listed by module at the end of this report.
- **Marked in the library: 0.** No `lib/*.smlib` file
  contains `parikshita`. So **63 functions have a
  `parikshita`-eligible body but are not marked** — that
  is the number, and the list is the file.
- Empirical check on v280 (the same marking tests as R82,
  re-run against the v280 compiler): **11/11 match the
  analyzer.** Four markable functions compile and run
  correctly when marked (`kramgun(5)` = 120,
  `madhava_atan(1)` = 0.785398,
  `laghuttam_samapavartya(4, 6)` = 12, `mala_nava`
  compiles); seven non-markable ones are refused with
  exactly the predicted error (`mala_yog` KARYA `pad8`,
  `kalana_trapiz` KARYA `kosh_len`, `suchi_srij`,
  `samasa`, `ganita_janchit_yuj`, `meru_mala` SMRITI, and
  one AHVAN case). The checker did not change in v280 —
  only NaN and division did — so the R82 table carries
  over, and this run re-proves it rather than assuming it.

Why the number cannot be counted from signatures alone
(the brief's phrasing, answered directly): 281 of 306
functions have no `kosh` parameter at all, so a
signature-only count would say 281 — but the checker
judges the whole body, and body violations remove 218 of
those (forbidden builtins, unknowable index sizes, calls
to unmarked functions). Eligibility is a whole-function
property with a transitive fixed point (a function is
eligible only if everything it calls is eligible); there
is no shortcut through the signature. The list in the
JSON is the fixed point, not a signature filter.

**Release-notes implication, as the brief framed it: the
boundary today protects new code, not the library.** A
new function written today can be marked `parikshita`
and checked — the mechanism works, as the 11 empirical
tests show. But the library itself has 0 of 306 marked,
and 243 of 306 could not be marked as they are. Saying
"the library is checked" would be false; saying "new
code can be checked" is true. Marking the 63 is the
owners' work, not done in this round (no tree changes).

## WS3 — the README sentence, for v280

The R88 sentence *was* sent — it is in the R88 report
(commit `251ea1a0`) — but v280 fixed two of its three
clauses, so sending it unchanged above the fold would now
be wrong. NaN no longer compares wrongly (it is IEEE on
v280, proved by 291), and dividing by zero in decimals no
longer prints `inf` (it stops with `E_SHUNYA_BHAJAN`,
proved by 293). Here is the sentence for v280, to go
above the fold:

> Still open, and stated plainly so you are not caught by
> them: a computed decimal stored into an integer silently
> loses its fraction, a decimal loop bound never
> terminates, and a decimal that grows past the largest
> finite value silently becomes infinity — anything else
> that surprises you is worth reporting as a bug.

**I would sign my name to it.** Each clause was verified
on v280 in this round: computed truncation
(`7.5 / 2.0` → `vitti` 3, `3.7` → 3), the decimal loop
bound (`chakra i = 0 tak 3.5` printed 228,059 lines in one
second and never stopped — the R86 sixth, still open on
v280), and silent overflow (the 10.0 loop prints `inf`,
the 400-digit literal prints `inf`, neither with a
message). The closing clause is deliberate, as in R88:
it does not claim everything else is perfect (aliasing
divergence, Tier-2 wraps, and the other documented gaps
remain), it invites a report — which is what makes the
rest trustworthy. And the sentence is shorter than R88's
for a good reason: v280 genuinely closed two things, and
a README that still warned about them would teach a
reader to distrust a book that is, on those two points,
now correct.

## The 63, by module

(Identical to `r89_parikshita.json`; the JSON is the
machine-readable deliverable, this list is the same data
in prose.)

- `ank` (10): `ank_gan`, `ank_yog`, `asti_sampurna`,
  `asti_viparyay_sam`, `asti_visham`, `asti_yugm`,
  `collatz_charan`, `fib`, `seemit`, `viparyay_ank`
- `anukram` (1): `anukram_maap_aayam_purva`
- `chandas` (5): `asti_guru`, `dwi_ghat`, `guru_gan`,
  `matra_meru`, `meru`
- `ganit` (17): `adhik2`, `asti_abhajya`, `bit_gan`,
  `dvigun`, `ganit_seemit`, `ghan`, `ghat`, `kramgun`,
  `laghu2`, `laghuttam_samapavartya`,
  `mahattam_samapavartak`, `nirapeksh_mulya`, `trigun`,
  `vardh`, `varg`, `vargit`, `yog_tak`
- `ganita` (13): `brahmagupta_kshetr`,
  `ganita_nirapeksh`, `ganita_paripurna_bhaj`,
  `ganita_paripurna_ghat`, `ganita_paripurna_gun`,
  `ganita_paripurna_kramgun`,
  `ganita_paripurna_nirapeksh`, `ganita_paripurna_nyun`,
  `ganita_paripurna_shesh`, `ganita_paripurna_yuj`,
  `ganita_vargmool`, `kuttaka`, `kuttaka_gun_shesh`
- `madhava` (5): `madhava_atan`, `madhava_cos`,
  `madhava_pi`, `madhava_sin`, `madhava_vargmool`
- `mala` (1): `mala_nava`
- `sadhan` (7): `ank_adhik`, `ank_chihna`,
  `antarveshan`, `bhaj_urdhva`, `satya_tak_ank`,
  `shesh`, `yog_seema`
- `samanvaya` (1): `samanvaya_akar_ayogya`
- `sankhyiki` (1): `sankhyiki_vargmool`
- `varna` (2): `avanat_sanket`, `unnat_sanket`

## NOT RUN

Windows, browser, implementation. The string-parse
overflow (`varna_tak_dashm` on 309+ digits) is hand-read
from the `* 10.0` accumulation, not run; the
extreme-input overflow claim for library functions in
general is a property of `float64` arithmetic, not a
run. Everything else in WS1 and WS3 was run on v280
(Linux ELF build), and the WS2 empirical marking tests
were run on v280. Marking the 63 on main, an explicit
conversion form, and a refusal (or message) for overflow
belong to the owners.

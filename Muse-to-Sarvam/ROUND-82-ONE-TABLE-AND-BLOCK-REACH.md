# Sutram — ROUND-82: one table for `parikshita`, and the block's real reach

**Base:** main at v277 (bb3084a1) · **Deliverables:** this report,
`R82-TEN-ASSUMPTIONS.md` (the reference page), `r82_parikshita_table.json`
(the 306-row machine table) · **No tree changes.**

## The one table

**63 of 306 library functions can be marked `parikshita` today, as they
are.** Claude's R81 number is right, and this round reproduces it
independently: a rule analysis of all 306 functions against the built
checker's rules (reference §20 + the checker's own walk) gives exactly
63, with the same module shape the reference states.

### The rule, exactly

A function can be marked `parikshita` as it is if and only if **every
one** of these holds, transitively (a function calling a non-markable
function is itself non-markable):

1. **No forbidden builtin.** Only `likha` (not the 3-argument
   `likha(fd, buffer, count)` form), `lkhb`, `likha_fmt`, `grahan`,
   and `nirmmita` are trusted. Everything else — `pad8`, `likh8`,
   `akshar`, `akshar_rakh`, `vartani_*`, `kosh_*`, `dvaram` (files),
   `smaran`, `shabda`, … — refuses with `E_APARIKSHITA_KARYA`.
2. **No indexing except through a size the checker knows.** An index
   is allowed only on a `mala` declared in the function, or on a
   `vitti p = nirmmita(CONSTANT)` name never assigned again.
   Indexing a parameter, a `p + 8`, a runtime-size block, or a
   reassigned name refuses with `E_APARIKSHITA_SMRITI`.
3. **No other refused construct:** `kosh` declarations, `rachana`
   fields (`p.x`), slices, function values, `prasar`, `yadi dosh`,
   inline assembly, vector literals, raw writes — all
   `E_APARIKSHITA_KARYA`. (In the library, none of these occur
   except through the builtins: zero functions declare a `kosh`
   local, zero use a true `rachana` field, zero use a slice.)
4. **Every library function it calls is itself markable** — otherwise
   `E_APARIKSHITA_AHVAN`, at the first bad call. Self-calls are
   allowed (a marked definition is marked); recursion is not a bar.

The reason given for each NO below is the **first** violation in
source order (the checker reports the first bad edge), interleaving
body violations and bad calls. The machine table
(`r82_parikshita_table.json`) carries the per-function verdict and
reason for all 306, so any row can be checked without trusting the
grouping.

### YES — 63 functions

- **ank (10/10):** ank_gan, ank_yog, asti_sampurna, asti_viparyay_sam,
  asti_visham, asti_yugm, collatz_charan, fib, seemit, viparyay_ank
- **madhava (5/5):** madhava_atan, madhava_cos, madhava_pi,
  madhava_sin, madhava_vargmool
- **sadhan (7/7):** ank_adhik, ank_chihna, antarveshan, bhaj_urdhva,
  satya_tak_ank, shesh, yog_seema
- **ganit (17/18):** adhik2, asti_abhajya, bit_gan, dvigun,
  ganit_seemit, ghan, ghat, kramgun, laghu2, laghuttam_samapavartya,
  mahattam_samapavartak, nirapeksh_mulya, trigun, vardh, varg,
  vargit, yog_tak — all but `ganit_yadricch` (indexes its state
  block through an alias, so its size is not known)
- **chandas (5/6):** asti_guru, dwi_ghat, guru_gan, matra_meru, meru —
  all but `meru_mala` (indexes a parameter)
- **ganita (13/23):** brahmagupta_kshetr, ganita_nirapeksh,
  ganita_paripurna_bhaj, ganita_paripurna_ghat, ganita_paripurna_gun,
  ganita_paripurna_kramgun, ganita_paripurna_nirapeksh,
  ganita_paripurna_nyun, ganita_paripurna_shesh, ganita_paripurna_yuj,
  ganita_vargmool, kuttaka, kuttaka_gun_shesh — all eight
  `ganita_janchit_*` are out (they write their `ok` cell through a
  parameter), as are `chakravala`, `samasa` (both index an output
  parameter)
- **Plus six singles:** anukram_maap_aayam_purva, mala_nava,
  samanvaya_akar_ayogya, sankhyiki_vargmool, avanat_sanket,
  unnat_sanket

### NO — 243 functions, by first reason

### E_APARIKSHITA_SMRITI (104 functions)
- **index on a name whose size is not known** (50): aadhar (1): brihat_ank_tak; ganit (1): ganit_yadricch; ganita (8): ganita_janchit_bhaj, ganita_janchit_ghat, ganita_janchit_gun, ganita_janchit_kramgun, ganita_janchit_nirapeksh, ganita_janchit_nyun, ganita_janchit_shesh, ganita_janchit_yuj; khand (3): khand_bhed, khand_mukt, khand_yuj; phal (2): phal_dosh, phal_siddhi; shreni (1): nivesh_shreni; suchi (17): avali_antah, avali_avalok, avali_nishkas, avali_pravesh, avali_tak_mala, chay_apanay, chay_avalok, suchi_antah, suchi_apanay, suchi_grah, suchi_khip, suchi_kramank, suchi_nivesh, suchi_sangrah, suchi_vardh, suchi_vinimay, suchi_viparyay; vakyank (6): ank_tak_aadhar_varna, ank_tak_varna, pad_vam, varna_tak_ank, varna_tak_ank_aadhar, varna_tak_dashm; varna (11): varna_aadi, varna_ant, varna_anwesh, varna_avanat, varna_bhed, varna_chhid, varna_pratisthap, varna_tul, varna_unnat, varna_viparyay, varna_yuj
- **index on a nirmmita name of runtime size or reassigned** (3): nighantu (1): nighantu_srij; suchi (2): avali_srij, suchi_srij
- **index on a parameter** (51): chandas (1): meru_mala; ganita (2): chakravala, samasa; nighantu (9): nighantu_koshtha_likh, nighantu_kunji_sam, nighantu_kunjika, nighantu_kunjika_ashtak, nighantu_maap, nighantu_mil, nighantu_mulya, nighantu_rikta, nighantu_vardh; phal (4): phal_asti_siddhi, phal_mulya, phal_mulya_va, phal_se_siddhi; samanvaya (7): ekaka_matrika, karna_yog, matrika_gunana, rekha_manak, saranik2, saranik3, vivartana; sangrah (6): rakh_asti_upasamuh, rakh_bhed, rakh_sampat, rakh_samroop_diff, rakh_sangam, rakh_tak_mala; sankhyiki (3): purna_adhikatama, purna_laghutama, purna_yoga; shreni (11): adhik, anwesh_sarak, asti_sorted, budbud_shreni, dwi_anwesh, gan, laghu, mil_shreni_punar, shankh_shreni, vinimay, yog; suchi (8): avali_maap, avali_rikta, avali_shunya, chay_rikta, suchi_adhik, suchi_laghu, suchi_maap, suchi_rikta

### E_APARIKSHITA_KARYA (75 functions)
- **builtin akshar** (18): anukram (1): anukram_grah_i64; gudh (1): fnv1a; khand (10): khand_aadi, khand_ant, khand_anwesh, khand_anwesh_akshar, khand_asti_sarv_ank, khand_chhid, khand_gan_akshar, khand_gan_swar, khand_pratisthap, khand_tul; varna (6): akshar_sanket, asti_akshar_akshar, asti_ank_akshar, asti_avakash_akshar, asti_avanat_akshar, asti_unnat_akshar
- **builtin akshar_rakh** (16): anukram (1): anukram_khip_i64; khand (5): khand_avanat, khand_bandh, khand_pratilip, khand_unnat, khand_viparyay; roop (10): roop_ank, roop_ank_aadhar, roop_chinhit, roop_pad_dakshin, roop_pad_madhya, roop_pad_vam, roop_sign_akshar, roop_sthir_mool, roop_varg_ank, roop_varg_sahaya
- **builtin dvaram** (3): patra (3): patra_asti, patra_likh_sarv, patra_path_sarv
- **builtin kosh_len** (14): kalana (5): bahu_ganana, dvitiya_pravan, kalana_trapiz, pravan, simpson; samanvaya (3): adish_gunan, matrika_yoga, skalar; sankhyiki (6): adhikatama, bindu_gunan, laghutama, madhya, prasaran, yoga
- **builtin likh8** (9): brihat (5): brihat_ank_se_laghu, brihat_bhajshesh, brihat_gun, brihat_pratilip, brihat_shunyank; mala (4): mala_pratilip, mala_purn, mala_sangrah, mala_sangrah_surakshit
- **builtin pad8** (8): brihat (5): brihat_ank_tak_laghu, brihat_asti_shunyank, brihat_nyun, brihat_tul, brihat_yuj; mala (3): mala_grah, mala_grah_surakshit, mala_yog
- **builtin vartani_aayam** (7): khand (1): khand_maap; varna (6): anwesh_akshar, asti_sarv_ank, gan_akshar, gan_swar, varna_maap, varna_sam

### E_APARIKSHITA_AHVAN (64 functions)
- **calls a non-markable function** (64): aadhar (1): brihat_ank_se; anukram (2): anukram_grah_aayam_purva, anukram_khip_aayam_purva; brihat (3): brihat_ghatmod, brihat_shesh, brihat_shesh_sahaya; gudh (1): fnv1a_varna; kalana (1): bahu_mula; khand (3): khand_antah, khand_gan, khand_sam; nighantu (7): nighantu_antah, nighantu_anwesh, nighantu_apanay, nighantu_grah, nighantu_grah_mool, nighantu_khip, nighantu_kunji_gudh; phal (8): phal_janchit_bhaj, phal_janchit_ghat, phal_janchit_gun, phal_janchit_kramgun, phal_janchit_nirapeksh, phal_janchit_nyun, phal_janchit_shesh, phal_janchit_yuj; roop (13): roop_ank_aadhar_saral, roop_ank_dhvaj, roop_ank_pre, roop_asht, roop_dash, roop_dwi, roop_shodash, roop_shodash_unnat, roop_sthir, roop_sthir_chinhit, roop_varg, roop_varg_bharatiya, roop_varg_vishwa; sangrah (8): rakh_antah, rakh_apanay, rakh_maap, rakh_rikta, rakh_sam, rakh_srij, rakh_vardh, rakh_yuj; sankhyiki (6): manak, purna_madhya, purna_prasaran, purna_vyapti, vichalan, vyapti; shreni (2): mil_shreni, viparyay_mala; suchi (7): chay_khip, suchi_anwesh, suchi_asti_sorted, suchi_dwi_anwesh, suchi_gan, suchi_shreni, suchi_yog; varna (2): varna_antah, varna_gan

## Which count is right, and why the other differs

**Claude's 63 is right.** It is the count under the checker as built
(v277), and this round confirms it two ways: the rule analysis above
reproduces 63 exactly (same total, same module shape), and 11
empirical marking tests — marking real functions together with their
transitive callees and compiling — all agree with the analysis,
including the error codes: `kramgun`, `madhava_atan` (recursion
passes), `laghuttam_samapavartya` + `mahattam_samapavartak`,
`mala_nava` all pass and run; `mala_yog` refuses `KARYA pad8`,
`kalana_trapiz` refuses `KARYA kosh_len`, `suchi_srij` refuses
`SMRITI l[...]`, `samasa` refuses `SMRITI out[...]`,
`ganita_janchit_yuj` refuses `SMRITI okp[...]`, `meru_mala` refuses
`SMRITI a[...]`, and a body-clean caller marked alone refuses
`AHVAN` naming its callee.

**My R81's 281 was a different question, asked before the checker
existed.** It counted functions with no `kosh` in them — one
necessary condition, not the checker's rule. The built checker
additionally refuses (a) every raw-memory builtin, including on a
function's *own* blocks (`pad8`/`likh8` in `mala`, `suchi`,
`nighantu`, `sangrah`, `brihat`, `anukram`; `akshar`/`akshar_rakh`
in `khand`, `varna`, `roop`; `vartani_*`; `dvaram` in `patra`) —
that whole container-on-blocks world is out even though it never
touches a `kosh`; (b) every index through a parameter — the
"cannot take a buffer" rule — which alone excludes 104 functions
by first reason, including all eight `ganita_janchit_*` (their `ok`
cell is a parameter) and the array-parameter modules (`shreni`,
`sankhyiki-purna`, `samanvaya`); and (c) transitively, 64 more
functions whose bodies are clean but which call something refused.
My R81's stricter 128 (container-parameter rule) was a hypothetical
in the same direction, not the built rule either — it allowed
raw-memory builtins on locals, which the checker forbids outright.
So: 281 was never a parikshita count; it was a kosh census. The
parikshita count is 63.

One correction to the brief's premise, stated plainly: my R81 report
contains no parikshita count of "11 / 21". Its two counts were 281
(kosh rule) and 128 (container-parameter rule). 11 / 22 were R80's
overflow counts (plausible / any-int64 inputs). The resolution above
does not depend on the "11 / 21" figure, whatever it referred to.

A correction to my own R81, owned here: its sensitivity number 271
("kosh + rachana") is withdrawn. Its "rachana-field" set (25
functions) was an artifact of the regex — it matched decimal
literals (`2.5`, `3.14159`) as fields. With a letter-anchored
pattern, the true count of functions using a `rachana` field in the
library is **0**, so the kosh+rachana cut coincides with the kosh
cut at 281. R81's headline (281) is unaffected; only the 271
sensitivity number was wrong.

Two checker details worth knowing, both verified empirically rather
than assumed: (i) size-knowledge comes only from a declaration
initializer — `vitti p = nirmmita(64)` qualifies, but `vitti p; p =
nirmmita(64)` does not, and **any** later assignment to `p` (even
`p = nirmmita(128)`) makes it unknown again; (ii) a marked function
with no `mukhya` in the file fails to parse at end-of-file — the
test files needed a trivial `mukhya` before the checker verdict
showed at all (a harness lesson, not a checker rule).

## WS1 — the block's reach: how many library functions create a `kosh`?

**Zero.** No library function declares a `kosh` local — every `kosh`
in the library arrives as a parameter (25 functions use one:
kalana 6, samanvaya 10, sankhyiki-dasham 9, all through `kosh_*`
builtins on the caller's `kosh`). Since nothing creates one,
nothing transitively creates one either. A block-safe `kosh` would
therefore unlock **no library function at all** — for the library,
vectors-in-a-block (or kosh-in-a-block) is a feature for user code
only. That is the fact before Claude spends a round on it.

The 25 kosh-using functions are a separate population, and they are
not blocked today: a `kosh` declared outside a block, pushed and
read inside a `mandapa`, compiles and runs (verified: push 10
outside, push 20 inside, read 20, length 2 after). The `kosh` lives
on the persistent arena, not scratch, so using a caller's `kosh`
from inside a block was never the problem — *creating* one inside
a block is, and no library function does that.

## WS2 — the documentation gaps

Of the brief's three: **`tak` is inclusive — not stated outright**
(the loop section shows `chakra i = 1 tak 5` with a break at 5,
which implies 5 is reached, and the one explicit "inclusive"
sentence covers the `arabhya … paryantam` form, not `tak`);
**`nirmmita` counts bytes but `p[i]` counts qwords — already
stated** (§6c is titled exactly that, and the summary table says
it too — not a gap); **integer division truncates toward zero —
not stated** (§3a covers division by zero and by −1, but never
says `-7 / 2` is `-3`).

The deliverable page (`R82-TEN-ASSUMPTIONS.md`) carries ten items
a programmer from another language will get wrong, each verified
on v277: `tak` inclusive; truncation toward zero (with the
remainder following the dividend: `-7 % 2` is `-1`); `==` on
strings compares addresses, not contents (use `vartani_tul`);
indexing a string reads qwords, not bytes (use `akshar(s, i)`);
dasham division by zero does not stop the program (`1.0 / 0.0`
is +inf, silently — §3a's "dividing by zero stops the program" is
about integers, but does not say so; `0.0 / 0.0` is 0, not NaN);
assignment is not an expression (`x = (y = 5)` fails to parse);
`vitti` is not a parameter type (integer parameters are untyped;
`dasham` is a parameter type); `kosh_push` on a `kosh` parameter
is refused (index within capacity works — grow in the caller);
an uninitialized `vitti` reads 0, even on a second call (locals
are zeroed, unlike C); and trailing statements after an indented
`mukhya` execute, while after a braced `mukhya` they are a
compile error.

Checked and found fine (not gaps, recorded so they are not
re-filed): `&&` and `||` both short-circuit (verified: `0 &&
(1/z == 0)` and `1 || (1/z == 0)` run without fault); `likha` of a
string variable printing its address now has its own section in
the reference; the `mukhya`-versus-`prakriya` brace inconsistency
is documented with the "always use braces" advice; the §3a
arithmetic policy is stated; the dasham printer limit is admitted
in §3a as "Not yet right".

## Method and caveats

- Built from `src/r68_compiler_entry.asm`; all probe results are
  from the built v277 binary; the tree was reset to `origin/main`
  after the runs (tracked `./sutram_compiler` restored).
- The analyzer strips comments and string literals before
  scanning (so neither can fake a call edge or a builtin), handles
  braced and indented bodies, and computes the transitive closure
  by fixed point. Builtins other than the trust base are treated
  as refusals; a lib function name appearing without `(` is
  treated as a function value. No lib function uses a slice, a
  `rachana` field, a `kosh` local, `prasar`, `yadi dosh`, inline
  assembly, or a vector literal — those rules therefore do not
  move the count, and the count is driven by builtins (75),
  parameter/unknown-size indexing (104), and transitivity (64).
- NOT RUN: Windows, browser, implementation (marking the 63 on
  main belongs to the owner; this round delivers the table, not
  the marking).

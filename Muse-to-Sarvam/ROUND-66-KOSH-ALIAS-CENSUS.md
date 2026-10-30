# ROUND-66 — the `kosh` alias census: the language change costs exactly two deliberate tests

Base: origin/main `c0fe2349` (compiler v263, Step 1 shipped),
checked against Claude's `R66-00` / `evidence-r67/kosh-alias-count.txt`
after my own count was done. No tree changes.

Method: a script that tracks `kosh` variables per file
(declarations + `kosh` parameters, ASCII and Devanagari),
then every assignment, call argument, and store mentioning
them — followed by hand verification of every hit (callee
parameter lists checked, scopes checked, single-line blocks
and continuation lines checked, Devanagari files read in
full). Negative tests excluded; docs reported separately.
The script is not shipped — the hits below are the record.

## Count 1 — one `kosh` variable assigned to another: 2

| File:line | Form | Note |
|---|---|---|
| `examples/252_r38_alias_kosh_oob.sm:7` | `w = v` | Deliberate alias test (bounds through alias) |
| `examples/255_r42_alias_kosh_push.sm:7` | `w = v` | Deliberate alias test (push through alias) |

Both use the two-step form (`vitti w = 0` then `w = v`).
**The `vitti a = k` initializer form occurs zero times in
the tree.** So the brief's question, answered in both
forms: `vitti a = k` — 0; `a = k` — 2; total — 2, both
deliberate tests of aliasing itself. There is nothing
incidental to preserve: no production program aliases a
kosh by assignment.

## Count 2 — a `kosh` passed to a `prakriya`: 166 arguments, 114 call lines

- User `prakriya` calls: **158 kosh arguments** (examples
  55, lib 16, tests/stdlib 87), including the one
  Devanagari pass (`122_t18_kosh_param_devanagari.sm:11`,
  `pratham(values)`).
- FFI calls: **8 kosh arguments** in 2 files
  (`tests/r33/kinds.sm`: `k_sum` ×2, `k_set`, `k_fsum`;
  `tests/r35/winffi.sm`: `w_sum` ×2, `w_set`, `w_fsum`).
- Builtins excluded: `kosh_push/len/cap/pop/peek/dequeue/
  enqueue` (by design) and the R63 builtins
  `kosh_empty/kosh_clear` (15 call sites in r63/r64
  checks and `257_r48_kosh_empty.sm`).

The unit matters, so both are stated: one call can pass
2–3 koshes (`matrika_gunana(a, b, c)`), so 166 arguments
sit on 114 call lines. Claude reports 162 call sites;
the two counts use different units and I could not
reproduce his unit exactly from his note alone — but the
population is the same list, and the decision-relevant
point is identical: passing is widespread (~160) and must
stay legal, which the proposed change already allows
(passing is not assignment).

Refinement Claude adds and I confirm: **of the callees
that take a `kosh` parameter, zero store it** — because
there are zero store sites at all (count 3).

## Count 3 — a `kosh` stored in a `mala`, a `rachana`, or a global: 0

- Into a `mala` cell (`m[i] = k`): 0.
- Into a `rachana` field (`d.f = k`): 0.
- Into a module-level global: 0 (the only module-level
  `vitti` in a real program is a counter in
  `236_guna_once.sm`; the r55/r56 global files are
  negative tests).
- Adjacent shape checked: a kosh handle pushed as an
  element of another kosh (`kosh_push(k, other_kosh)`): 0.

Caveat, stated so the zero is not over-read: the *shapes*
exist in evidence programs (Claude's R59 alias cases, my
R65 P3, my R67 P3′/P3′′) but not in shipped code. A fix
that bans only variable assignment leaves the store shapes
legal — today they alias (R67 P3′′ proves it on v263),
so a complete fix must cover stores too, or accept that
hole knowingly. The hole has zero tree instances.

## Count 4 — declarations in programs that also alias: 2 of 130

My enumerated denominator: **130 literal-capacity `kosh`
declarations** in tree `.sm`/`.smlib` outside negative
tests (125 ASCII + 5 Devanagari: `97`, `100`, `110`,
`122`, `219`). All 130 carry a literal capacity; no
computed-capacity `kosh` declaration exists in tree code
(the R59 "computed 1" was a `nirmmita`, not a `kosh`).

Of the 130, exactly **2 sit in aliasing programs**:
`252` (`kosh dasham v[4]`) and `255` (`kosh v[4]`) — one
each. **128 of 130 are unaffected by a ban.**

Denominator reconciliation (Claude reports 131, 129
unaffected): same 646-file population, same exclusion of
negative tests. I account for 130 after checking
Devanagari spellings, multi-line signatures (none),
same-line-brace declarations (none), non-literal caps
(none), `.py` driver strings (4 — would overshoot to
134, so not his scope), and docs prose (not code). One
declaration of difference remains unexplained by any
scope I can reproduce. It does not move the decision:
the alias count is 2 on either denominator (129 or 128
unaffected).

## The extra question — do `mala` and `rachana` assignments alias too? YES, both

- **Mala: yes, golden-backed.** `254_r42_alias_pankti_len.sm`
  (`vitti b = a` on a `mala`, then `b[1] = 7`, golden
  prints `a[1] = 7`) — write-through is specified
  behavior, not an accident. `251_r38_alias_mala_oob.sm`
  tests bounds-checking through a mala alias. Tree mala
  aliases: 2, both deliberate tests.
- **Rachana: yes, by mechanism.** My test (`vitti q = p`
  on a `nirmmita` block, `q.x = 99` → `p.x = 99` on v263)
  proves the pointer copy. Tree rachana aliases: 0.
- **Total variable-alias sites in the tree: 4** (2 kosh +
  2 mala), all deliberate tests.

**So the answer to "a `kosh` fix or a language-wide
rule" is: the mechanism is language-wide, the hazard is
kosh-specific.** Assignment copies the pointer for all
three container types (they are all block pointers), but
only `kosh` relocates — `mala` and `rachana` are fixed
blocks, so their aliases can never strand a buffer. A
language-wide ban on `vitti a = k` would break
golden-backed mala behavior (254) to fix a kosh-only
hazard. A kosh-scoped ban costs exactly the 2 kosh tests
above, which would become negative tests (reversing
R42's decision for `kosh` only — R42's mala half in 254
stands untouched).

Two further holes for the fix's spec, both with zero
tree instances today: (1) **return-alias** — a function
returning a `kosh` variable (`nivartanam k`) compiles
(R59 case D, evidence only); banning assignment does not
ban returning. (2) **store-alias** — count 3's shapes,
legal today, zero tree instances. If the ban is meant to
make "no second owner" a language invariant, it must
cover assignment + return + store, or say which it
leaves open.

## Verdict for the decision

- Banning kosh-variable assignment is **nearly free**:
  2 tree sites, both tests of the very behavior being
  banned, 128/130 declarations untouched, passing (~160
  sites) and the whole library unaffected.
- Banning assignment language-wide is **not free**: it
  reverses specified mala behavior (254's golden).
- Keeping aliasing and fixing the bins another way
  remains open — but the census says the "expensive"
  option is not expensive for `kosh`. The cost is 2
  tests, not a language.

## NOT RUN

- Windows / WSL: no Windows component in this round.
- Browser automation: no browser component in this round.

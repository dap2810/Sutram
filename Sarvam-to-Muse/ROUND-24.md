# Sutram — Round 24 handoff: Sarvam → Muse

**Date:** 2026-10-15
**Base:** main — **R23 merged.** Library **21 modules / 274 functions**.
Suite 187/3, proof_lib **175/175**, proof_props **65/65**.
**This is a HEAVY round.** Five workstreams. Each is independently acceptable.

## R23 accepted — verified

- Patch clean; **14/14 hashes**; proof_lib **175/175** (was 172), proof_props **65/65** (was 62),
  suite **187/3**; library now **21 modules / 274 functions**.
- **Every new test shipped `.sm` + `.out` + `.exit`** — that was the R21 lesson and you applied it.
  `proof_lib` is green on the first try.
- Reconciling `docs/KOSH-BUILTINS.md` against the *measured* R64 messages (rather than the R63 text)
  and correcting the `LANGUAGE-REFERENCE.md` §16 line is exactly the right kind of documentation work.
- `list_find` / `list_is_sorted` / `list_binary_search` completing the `sort.smlib` analytics, and
  `queue_to_array` giving a **non-destructive** FIFO read, are both real gaps closed.

## Workstream 1 — the `strb` / `str` surface, third pass: finish the parity table
You documented the slice-boundary rules in the headers. Now **close the remaining asymmetries** you
can close, and for each one that stays open, say why. Deliver the **complete parity table** — every
`str_*` beside its `strb_*` counterpart, with `added` / `deliberately not` / `cannot (compiler-side)`.

## Workstream 2 — the containers, final sweep
The R19–R23 audits have covered clear, resize, swap, reverse, find, sorted, search, merge, sym-diff,
and non-destructive queue reads. Do a **final sweep** and declare the container surface **complete**,
or name exactly what is left and why. Include `kosh` — if anything is still missing there, it belongs
to the compiler side; name it rather than working around it.

## Workstream 3 — the accumulated small gaps
Whatever you have flagged across `map`, `kosh`, `list`, `set`, `strb`, `str`, `ganita` that is still
open. For each: a test that would have failed or been wrong before, and the before/after output.

## Workstream 4 — the library half of the safety net, consolidated
You have `ganita_checked_*` (R18), `ganita_sat_*` (R18), and `ganita_checked_fact`/`ganita_sat_pow`
(R20). ChatGPT's compiler trap is **default-OFF** (ROUND-66 WS2). Consolidate the library's half into
one coherent doc section: the full checked/saturating surface, what each function returns on failure
(the rule is **0 on failure, never the wrapped value**), and the recommended choice for each case.
**Documentation + any missing companion function.** Do not edit `src/`.

## Workstream 5 — a property-test expansion
`proof_props.py` holds 65 properties. Add properties for the R23 additions (`list_find`,
`list_is_sorted`, `list_binary_search`, `queue_to_array`, `map_merge`, `set_sym_diff`) — in particular
the invariants that matter: `binary_search` agrees with `find` on a sorted list, `queue_to_array` does
not mutate, `map_merge` is src-wins, `set_sym_diff` is symmetric.

---

## Safety constraints — hard requirements
- **Least privilege.** No admin/root, no elevation, no writing outside the repo and sandbox.
- **No credentials** anywhere — placeholders only, including tests and commit messages.
- **No new network access.** The library stays pure.
- Do not rewrite accepted goldens. Frozen surfaces untouched: `map_keys`/`map_keys_bytes` (R17),
  `ganita_checked_*`/`ganita_sat_*` (R18), the R19–R23 additions — extend beside them.
- New tests use ASCII identifiers (the `0xE0` Devanagari lexer trap still applies).

## Definition of done
- Each workstream completed with evidence, or reported as not done and why.
- Suite still passes (187 + 3); new goldens additive — **every new `.sm` ships `.out` AND `.exit`**.
- Delivered as a **patch in `Muse-to-Sarvam/`** with the SHA-256 block for every file.
- `docs/sutram-stdlib.html` regenerated with the new count stated.

A verified partial beats a claim.

# Sutram — Round 25 handoff: Sarvam → Muse

**Date:** 2026-10-15
**Base:** main — **your R24 is merged.** Library **21 modules / 278 functions**.
Suite 187/4, proof_lib **176/176**, proof_props **68/68**.
**This is a HEAVY round.** Four workstreams. Each is independently acceptable.

## R24 accepted — verified

- Patch clean; **8/8 hashes**; proof_lib **176/176** (was 175), proof_props **68/68** (was 65),
  suite **187/4**; library now **21 modules / 278 functions**.
- **Declaring the container surface complete, and naming the `kosh` remainder compiler-side, was the
  right call** — a completeness statement with its exceptions named is worth more than another sweep.
- **The 30-row parity table is the document this needed.** Marking the `*_replace` `repl` case
  `cannot (compiler-side)` with the reason (a 7th argument would exceed the 6-argument cap) is exactly
  the honest kind of entry, and the `strb_dup` workaround is a real answer rather than a shrug.
- `ganita_sat_div` / `ganita_sat_mod` / `ganita_checked_abs` / `ganita_sat_abs` complete the arithmetic
  surface, and `docs/OVERFLOW-SAFETY.md` consolidates it.

## Context: ChatGPT's compiler work

R66 added **native Devanagari and Gujarati digit readers** and exact abbreviation aliases; the Sanskrit
pack grew 49 → 54 entries. **One part of R66 is not merged** — its Gujarati pack reserves `સંખ્યા`,
which an accepted test uses as a variable name, so that file is held back pending a fix. Nothing for
you to do about it; noted so you know the Gujarati pack on main is currently the older one.

## Workstream 1 — the safety net, verified rather than asserted
`docs/OVERFLOW-SAFETY.md` states the checked/saturating contract. **Prove it holds**: for every
`ganita_checked_*` and `ganita_sat_*`, a test that would fail if the failure-returns-0 rule were
broken, and one that shows the saturating form actually saturates at `INT64_MAX`/`INT64_MIN`.
Table the results. If any function does not honour the stated contract, say so — that is the finding.

## Workstream 2 — the string/byte parity table, executed
`docs/STRING-BYTE-PARITY.md` lists 30 rows. For every row marked `added`, confirm a test exists that
would have failed before it was added. For every `deliberately not`, confirm the stated reason still
holds. Report the rows with no coverage.

## Workstream 3 — the accumulated small gaps
Whatever you have flagged across `map`, `kosh`, `list`, `set`, `strb`, `str`, `ganita` that is still
open. For each: a test that would have failed or been wrong before, and the before/after output.

## Workstream 4 — a property-test expansion
`proof_props.py` holds 68 properties. Add properties for the R24 additions — in particular that
`saturating` and `checked` agree on their success path, that `sat_abs`/`checked_abs` agree for
non-`INT64_MIN` inputs, and that the saturating forms never wrap.

---

## Safety constraints — hard requirements
- **Least privilege.** No admin/root, no elevation, no writing outside the repo and sandbox.
- **No credentials** anywhere — placeholders only, including tests and commit messages.
- **No new network access.** The library stays pure.
- Do not rewrite accepted goldens. Frozen surfaces untouched: `map_keys`/`map_keys_bytes` (R17),
  `ganita_checked_*`/`ganita_sat_*` (R18), the R19–R24 additions — extend beside them.
- New tests use ASCII identifiers (the `0xE0` Devanagari lexer trap still applies).

## Definition of done
- Each workstream completed with evidence, or reported as not done and why.
- Suite still passes (187 + 4); new goldens additive — **every new `.sm` ships `.out` AND `.exit`**.
- Delivered as a **patch in `Muse-to-Sarvam/`** with the SHA-256 block for every file.
- `docs/sutram-stdlib.html` regenerated with the new count stated.

A verified partial beats a claim.

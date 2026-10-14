# Sutram — Round 22 handoff: Sarvam → Muse

**Date:** 2026-10-14
**Base:** main — **your R21 is merged.** Library **21 modules / 268 functions**.
**This is a HEAVY round.** Four workstreams. Each is independently acceptable.

## R21 accepted — verified

- Patch clean; **12/12 hashes**; proof_lib **172/172** (was 170), proof_props **62/62** (was 60),
  suite **187/3**; library now **21 modules / 268 functions**.
- **Writing the compiler-side `kosh` builtin spec was the right call** — the builtins existed but the
  contract did not. Documenting that `kosh_clear` zeroes the *logical length* but does **not** erase
  storage is exactly the kind of honesty that stops a future reader assuming secure erasure.

## Workstream 1 — the `kosh` spec, completed against the shipped builtins
R63/R64 landed the builtins; your spec describes them. Now reconcile it with what actually shipped:
- confirm the documented signatures/returns match the merged compiler (R64 added distinct
  `kosh_peek`/`kosh_dequeue` empty diagnostics — the spec must name all three messages accurately);
- state the empty-`peek` vs empty-`dequeue` vs empty-`pop` behaviour precisely.
**Documentation only.** Do not edit `src/`.

## Workstream 2 — the remaining container gaps
Continue the R19/R20/R21 audit. Where a gap cannot be closed in the library (no generic parameter
type / no overloading), **name it and assign it to the compiler side** — that was the right call for
`kosh` and it remains right.

## Workstream 3 — the accumulated small gaps
Pick up whatever you have flagged across `map`, `kosh`, `list`, `set`, `strb`, `str`, `ganita`. For
each: a test that would have failed or been wrong before, and the before/after output.

## Workstream 4 — the trap-vs-checked division of labour, finalised
ChatGPT is now implementing the compiler overflow trap **default-OFF** (ROUND-65 workstream 2). Write
the final note: when to use the opt-in trap, when `ganita_checked_*`, when `ganita_sat_*`; and confirm
the R18/R19 checked surface composes cleanly with a trapping compiler. **Do not edit `src/`.**

---

## Safety constraints — hard requirements
- **Least privilege.** No admin/root, no elevation, no writing outside the repo and sandbox.
- **No credentials** anywhere — placeholders only, including tests and commit messages.
- **No new network access.** The library stays pure.
- Do not rewrite accepted goldens. Frozen surfaces untouched: `map_keys`/`map_keys_bytes` (R17),
  `ganita_checked_*`/`ganita_sat_*` (R18), the R19–R21 additions — extend beside them.
- New tests use ASCII identifiers (the `0xE0` Devanagari lexer trap still applies).

## Definition of done
- Each workstream completed with evidence, or reported as not done and why.
- Suite still passes (187 + 3); new goldens additive.
- Delivered as a **patch in `Muse-to-Sarvam/`** with the SHA-256 block for every file.
- `docs/sutram-stdlib.html` regenerated with the new count stated.

A verified partial beats a claim.

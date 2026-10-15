# Sutram — Round 27 handoff: Sarvam → Muse

**Date:** 2026-10-16
**Base:** main — **your R26 is merged.** Library **21 modules / 281 functions**.
Suite 187/4, proof_lib **180/180**, proof_props **72/72**.
**This is a HEAVY round.** Four workstreams. Each is independently acceptable.

## R26 accepted — verified

- Patch clean; **12/12 hashes**; proof_props **72/72** (was 69), proof_lib **180/180** (was 177),
  suite **187/4**; library now **21 modules / 281 functions**.
- **You flagged your own overlap.** R26 touches `tools/proof_props.py`, the same file R25 touched and the
  same file the R24 sync once dropped — and you stated the resulting count (72) so the sync could be
  checked directly. That is the R24 lesson applied deliberately, and it is exactly right.
- **The three bug fixes are the most valuable part of this round.** `str_to_int` overflow guards,
  `int_to_str(MIN)`, and the `fmt_int_base`/`fmt_int_flags` MIN cases are real defects that would have
  produced wrong output silently. A round that fixes three real bugs beats a round that adds thirty
  functions.
- `docs/PROPERTY-NET.md` — stating, per property, what would have to break for it to fail — is the right
  way to audit a proof suite. A property nobody can describe the failure of is not testing anything.

## Context: the compiler moved

ChatGPT's R68 is merged. The compiler now has a **host-side UTF-8 precheck and an abbreviation-value
guard**, and it is built through an entry wrapper (`src/r68_compiler_entry.asm`). **Nothing in the
library should be affected**, but if any of your tests compile malformed source and expect a particular
message, re-check it.

## Workstream 1 — the safety net, across the module boundary
R25 and R26 proved the checked/saturating contract and its interactions. Extend that across modules:
show that `ganita`'s checked forms and `strconv`'s overflow guards agree on the same input, and that
neither silently wraps. Table the results.

## Workstream 2 — the property suite as a net, again
`proof_props.py` now holds 72 properties. For each new one, state what would have to break. Then: **is
there a property that has never failed and never could?** If so, say so and remove it — a property that
cannot fail is decoration.

## Workstream 3 — the accumulated small gaps
Whatever is still open across `map`, `kosh`, `list`, `set`, `strb`, `str`, `ganita`, `math`, `fmt`.
For each: a test that would have failed or been wrong before, and the before/after output.

## Workstream 4 — the library's honest boundary
The library is 281 functions. Write **one page** stating what it deliberately does not do — file I/O,
networking, time, threading, and anything else — with the reason for each. A stated boundary is worth
more than a longer function list.

---

## Safety constraints — hard requirements
- **Least privilege.** No admin/root, no elevation, no writing outside the repo and sandbox.
- **No credentials** anywhere — placeholders only, including tests and commit messages.
- **No new network access.** The library stays pure.
- Do not rewrite accepted goldens. Frozen surfaces untouched: `map_keys`/`map_keys_bytes` (R17),
  `ganita_checked_*`/`ganita_sat_*` (R18), the R19–R26 additions — extend beside them.
- New tests use ASCII identifiers (the `0xE0` Devanagari lexer trap still applies).

## Definition of done
- Each workstream completed with evidence, or reported as not done and why.
- Suite still passes (187 + 4); new goldens additive — **every new `.sm` ships `.out` AND `.exit`**.
- Delivered as a **patch in `Muse-to-Sarvam/`** with the SHA-256 block for every file.
- **Name every shared file you touch and state the resulting count** — as you did in R26.

A verified partial beats a claim.

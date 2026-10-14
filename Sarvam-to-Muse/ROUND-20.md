# Sutram — Round 20 handoff: Sarvam → Muse

**Date:** 2026-10-14
**Base:** main — your R19 is **merged**. Library **21 modules / 247 functions**.
**This is a HEAVY round.** Four workstreams. Each is independently acceptable.

## R19 accepted — verified, and the `kosh` finding was the best part

- Patch applied cleanly; **14/14 hashes match**. proof_lib **167/167** (was 164), proof_props
  **57/57** (was 54), suite **187/3**; library now **21 modules / 247 functions**.
- **Naming the `kosh` gap instead of forcing it was exactly right.** You proved by compiling failing
  test programs that there is no generic `kosh` parameter type and no overloading, so a library
  version would need type-suffixed names — which is *not* "same names, same semantics". That gap is
  now **ROUND-63 workstream 4** on ChatGPT's side. That is what a good handoff does.
- `map_clear` zeroing the **storage**, not just the count, and saying so plainly, is the difference
  between closing the stale-segment hazard and merely appearing to. `map_get_default` removing the
  `-1`-is-ambiguous hazard is the same kind of fix.

## NEW — the language now has Devanagari Sanskrit support (merged)

- **`lang/sanskrit.lang`** — the 31 core keywords in Devanagari; a whole program can be written in
  Devanagari and compiles to native machine code.
- **Danda `।` (U+0964) / double danda `॥` (U+0965)** now terminate statements like `;`.
- New example `examples/218_sanskrit_devanagari.sm` prints `योगः = 15`.
- **Relevant to you:** your library tests use ASCII identifiers. If you write any test with
  Devanagari identifiers, note that the lexer's `is_alpha` claims the `0xE0` lead byte, and a danda
  immediately after an identifier is now handled — but any *new* multi-byte punctuation would need
  the same care. All nine Indic scripts share that lead byte.

## Workstream 1 — the string/byte surface, completed
`strb` gained `reverse` and `count` in R19. Finish the family so the byte-string surface is
complete and consistent with the cell-array (`kosh`/`pankti`) surface:
- whatever `strb` still lacks that the cell form has (and vice versa) — audit both, list the
  differences, and close the ones where the fix is genuinely the same shape.
- **Per-pair table** of what was added and what was deliberately not, with the reason.

## Workstream 2 — the remaining container gaps
R19 covered clear for map/set/list/queue. Continue the audit:
- anything else the containers are missing that callers currently hand-roll (peek, empty, swap,
  resize/rehash, iteration helpers).
- Where a gap cannot be closed in the library for the same reason `kosh` could not (no generic
  parameter type / no overloading), **name it and assign it to the compiler side** rather than
  working around it. That was the right call in R19 and it is the right call here.

## Workstream 3 — the accumulated small gaps
Pick up whatever you have flagged as missing or awkward across `map`, `kosh`, `list`, `set`, `strb`,
`ganita` — the small ones that individually do not warrant a round. For each: a test that would have
failed or been wrong before, and the before/after output.

## Workstream 4 — the library half of the overflow safety net, now that the trap is being built
ChatGPT is implementing the compiler trap this round (ROUND-63 workstream 3). Your half:
- Confirm the `ganita_checked_*` / `ganita_sat_*` surface composes cleanly with a trapping compiler —
  the explicit, recoverable form must still work and stay the recommended one where a program must
  survive.
- Write the **trap-vs-checked division of labour** note in the handoff so the docs can state it once.
- **Do not edit `src/`.** If the trap needs a library change, describe it and leave it.

---

## Safety constraints — hard requirements
- **Least privilege.** No admin/root, no elevation, no writing outside the repo and sandbox.
- **No credentials** anywhere — placeholders only, including tests and commit messages.
- **No new network access.** The library stays pure.
- Do not rewrite accepted goldens. Do not touch the frozen surfaces: `map_keys`/`map_keys_bytes`
  (R17), `ganita_checked_*`/`ganita_sat_*` (R18), and the R19 additions — extend beside them.

## Definition of done
- Each workstream completed with evidence, or reported as not done and why.
- Suite still passes (187 + 3); new goldens additive.
- Delivered as a **patch in `Muse-to-Sarvam/`** with the SHA-256 block for every file.
- `docs/sutram-stdlib.html` regenerated with the new count stated.
- Per-container and per-pair tables of what changed and what deliberately did not.

A verified partial beats a claim.

# Sutram — Round 19 handoff: Sarvam → Muse

**Date:** 2026-10-14
**Base:** main, compiler R61 (ChatGPT, PE-padding fix, merged). Library **21 modules / 239 functions** — **your R18 is merged.**
**This is a HEAVY round.** Four workstreams. Work them in order; each is independently acceptable, so
if you run out of time, ship what is finished and say plainly what is not.

## R18 — accepted, and the reasoning was as good as the code

- Patch applied cleanly; **5/5 hashes match**. proof_lib **164/164**, proof_props **54/54**, suite
  **186/3**, stdlib reference reproduces **21 modules / 239 functions** exactly.
- **Opt-in checked functions with the operators unchanged** was the right mechanism: no accepted
  golden moves, no `src/` change. And failure returning **0, never the wrapped value** is the detail
  that makes it actually safe — a caller who forgets to check gets an obviously-wrong 0 rather than a
  plausible-but-wrong number. Measuring what the operators do today before changing anything was the
  correct first step.
- Your compiler-trap follow-on is now **workstream 4 below** (ChatGPT owns `src/`; you own the
  library half — see the split).

---

## Workstream 1 — `map_clear` (your friction note 3)
- A `map_clear(m)` that resets a map to empty **in place**, without the caller freeing and re-creating
  it, and **without leaking or aliasing** what the old contents referenced.
- **State** whether it also zeroes the storage or merely resets the count — the difference matters to
  anyone reading stale segments afterwards.
- **Evidence:** a before/after on the pattern that is currently awkward or wrong without it (the
  demonstration is the point, as in R17/R18), plus a property that would catch a clear-then-reuse bug
  if one is reachable. If it is not reachable, say so.

## Workstream 2 — Container breadth: the same gap, everywhere it exists
- Audit every container for the `map_clear` gap and the "stale segment after reset" hazard: `map`,
  `kosh`, `list`, `set`. Fix the ones where the fix is **genuinely the same shape**; do **not** force
  it where it is not.
- Give `kosh` the stack/queue primitives `list` already has, if they are missing — same names, same
  semantics, so the two are interchangeable at the call site.
- **Evidence:** a per-container table of what was added and what was deliberately not, with the
  reason. A gap you name and justify is worth more than one you quietly skip.

## Workstream 3 — Close the remaining library gaps you have flagged
Pick up whatever you have already identified as missing or awkward across `map`, `kosh`, `list`,
`set`, `strb`, `ganita` — the small ones that individually do not warrant a round. This is the round
for the accumulated list.
- For each: a test that would have failed or been wrong before, and the before/after output.
- **Do not** add a new module; extend the existing ones.

## Workstream 4 — The library half of the automatic overflow safety net
ChatGPT is adding the **compiler trap** (conditional `jo`/`jno` after `+ - *`, zero-divisor guard
before `idiv`, abort with file:line) in the same round. Your half:
- Make sure the `ganita_checked_*` / `ganita_sat_*` surface composes cleanly with a trapping compiler
  — i.e. the explicit, recoverable form still works and is still the recommended one where a program
  must survive.
- Write a short note (in the handoff) on the intended division of labour between the trap and the
  checked functions, so the docs can state it once.
- **Do not** edit `src/` — if the trap needs a library change to work, describe it and leave it.

---

## Safety constraints — hard requirements
- **Least privilege.** No admin/root, no elevation, no writing outside the repo and the sandbox, no
  touching credentials or system config.
- **No credentials.** Never handle, embed, log, or transmit secrets, tokens, or API keys — placeholders
  only, anywhere, including tests and commit messages.
- **No new network access.** The library stays pure; nothing calls out.
- Do not rewrite accepted goldens. Do not touch the frozen surfaces: `map_keys`/`map_keys_bytes`
  (R17) and `ganita_checked_*`/`ganita_sat_*` (R18) — extend beside them, not over them.

## Definition of done
- Each workstream completed with evidence, or reported as not done and why.
- Suite still passes (186 + 3); new goldens additive.
- Delivered as a **patch in `Muse-to-Sarvam/`** with the SHA-256 block for every file, built against
  the compiler SHA above.
- `docs/sutram-stdlib.html` regenerated with the new count stated.
- A per-container table of what changed and what deliberately did not.

A verified partial beats a claim. If only some workstreams land, say which and why.

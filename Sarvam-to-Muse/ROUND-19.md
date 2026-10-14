# Sutram — Round 19 handoff: Sarvam → Muse

**Date:** 2026-10-14
**Base:** main, compiler R61 (ChatGPT, PE-padding fix, merged). Library **21 modules / 239 functions** — **your R18 is merged.**

## R18 accepted — verified

- Patch applied cleanly to pristine main; **5/5 hashes match**.
- `proof_lib` **164/164**, `proof_props` **54/54**, suite **PASS=186 / NO-EXPECTATION=3**,
  `gen_stdlib_ref.py` reproduces **21 modules / 239 functions** exactly.
- **The mechanism choice was right and well argued:** opt-in checked functions with the operators
  unchanged, so no accepted golden moves and no `src/` change. And the failure value is **0, never the
  wrapped value** — so a caller who forgets to check `ok` gets an obviously-wrong 0 rather than a
  plausible-but-wrong number. That is the detail that makes this actually safe.
- Naming (`ganita_checked_*` / `ganita_sat_*`, Rust-recognisable) over a Sanskrit-only coinage is the
  right call for call-site clarity. Measuring what the operators do today (wrap; SIGFPE exit 136 on
  `/0` and `MIN/-1`) before changing anything was the correct first step.
- The compiler-trap follow-on is noted and stays queued for a round where `src/` changes are in scope.

## Round 19 — ONE big task

**`map_clear` — your own friction note 3, the last one queued.**

### What to build
- A `map_clear(m)` that resets a map to empty **in place**, without the caller having to free and
  re-create it, and **without leaking or aliasing** whatever the old contents referenced.
- Decide and state whether it also zeroes the storage or merely resets the count — the difference
  matters to anyone reading stale segments afterwards.
- Give the same treatment to the sibling containers if the same gap exists there (`kosh`, the list
  module) — but only if the fix is genuinely the same shape. Do not force it.

### Evidence I will look for
- A **before/after** on the pattern that is currently awkward or wrong without `map_clear` — the
  demonstration is the point, as in R17 and R18.
- A property that would catch a clear-then-reuse bug (stale segment read after clear) if one is
  reachable. If it is not reachable, say so.
- `proof_lib` / `proof_props` totals on the current compiler, with real output.
- Every changed file and every affected golden listed. No existing golden changed unless named.

### Definition of done
- `map_clear` exists, is tested, and its semantics (storage vs count) are stated.
- Suite still passes (186 + 3); new goldens additive.
- Delivered as a **patch in `Muse-to-Sarvam/`** with the SHA-256 block for every file, built against
  the compiler SHA above.
- `docs/sutram-stdlib.html` regenerated if the surface changed, with the new count stated.

### Explicitly NOT this round
Do not change the compiler. Do not add a new library module. Do not touch `map_keys` /
`map_keys_bytes` (R17 frozen) or the `ganita_checked_*` / `ganita_sat_*` surface (R18 frozen).

### Constraints (unchanged)
`.sm`, `lib/*.smlib`, pure NASM compiler underneath, no runtime dependency, Sanskrit keyword core.
Least privilege. Do not rewrite accepted goldens.

If `map_clear` cannot be made safe for some container shape, ship it for the shapes where it can and
say plainly which it does not cover — a verified partial beats a claim.

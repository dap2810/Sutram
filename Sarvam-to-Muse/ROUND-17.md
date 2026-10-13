# Sutram — Round 17 handoff: Sarvam → Muse

**Date:** 2026-10-13
**Base:** main, compiler `35d85b803924c96db111a62c2867a3f28b80a4778605526e8cf3175823e89aff` (ChatGPT R58, constant folding — merged), library **21 modules / 230 functions** (your R16 included).

## R16 accepted — verified, and the patch workflow is now the standard

- **All three hashes match exactly**: `lib/list.smlib` `9951eba4…`, `tools/proof_props.py` `efab4a6e…`,
  `docs/sutram-stdlib.html` `e195c942…`.
- `proof_lib` **161/161**, `proof_props` **49/49**, suite **PASS=186 / NO-EXPECTATION=3**.
- **21 modules / 230 functions** confirmed — regenerating the stdlib reference reproduces it exactly.
- Delivered as a patch, applied cleanly, reviewed before it touched `main`. Keep doing it this way.

## Round 17 — ONE big task

**Fix the friction you identified in R14: make map keys available as packed bytes.**

This is your own friction note 1, and it has been queued since R14 for exactly this round. It is a
**correctness** change, not a feature: right now every consumer of `map_keys` has to re-implement
the same walk-plus-`strb_pack` step, and you showed in R14 that getting it wrong produces
**silently wrong output rather than an error**. That class of bug should not be reachable.

### What to build
- A way to obtain a map's keys as **packed bytes** directly — either a new `map_keys_bytes`, or keys
  returned packed by default with the old cell form kept under an explicit name. Your call; state
  the reasoning.
- **Migrate the existing consumers** that currently do the walk-plus-pack dance: `set.smlib`,
  `map.smlib`'s own helpers, and anything in `list.smlib` that touches keys.
- **Keep the public API stable or clearly version it.** If a name changes meaning, say so loudly in
  the handoff and update the call sites in the same patch.

### Evidence I will look for
- A test that would have **failed silently before** and now either works or errors — that is the
  point of this round. Show the before/after behaviour explicitly.
- `proof_lib` and `proof_props` totals on the current compiler, with real output.
- No existing golden changed; `docs/sutram-stdlib.html` regenerated with the new count stated.
- Every changed call site listed in the handoff.

### Definition of done
- Suite still passes (186 + 3); new goldens are additive.
- Delivered as a **patch in `Muse-to-Sarvam/`** with the SHA-256 block for every file.
- Handoff naming the compiler SHA you built against.

### Explicitly NOT this round
Do not change the compiler. Do not add new library modules this round — this is a refactor of an
accepted surface and it must be reviewable on its own. Your notes 3 and 4 (`map_clear`, loud
overflow) stay queued behind it.

### Constraints (unchanged fundamentals)
`.sm`, `lib/*.smlib`, pure NASM compiler underneath, no runtime dependency, Sanskrit keyword core.
Least privilege. Do not rewrite accepted goldens.

If only part of the surface can be migrated safely, ship that part and say plainly which call sites
still need the old walk — a verified partial beats a claim.

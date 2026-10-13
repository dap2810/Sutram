# Sutram — Round 15 handoff: Sarvam → Muse

**Date:** 2026-10-13
**Base:** main, compiler `d0fe190cd1b8a94344777c0d20e1d210979eb2d871d533a95ab98eb183dec125` (ChatGPT R56), library **19 modules / 186 functions** (your R14 included).

## R14 accepted — but note how it arrived

Your R14 work is **verified and accepted**. I reproduced your gates on the R56 compiler:

- `proof_lib` **153/153**, `proof_props` **39/39**, suite **PASS=186** (your 185 is the known,
  pre-existing `79_ayojan_cwd` environment case — it passes from the repo root, so no action).
- All three of your claimed hashes match: `lib/set.smlib` `7574e5eb…`, `tools/proof_props.py`
  `41298c5b…`, `docs/sutram-stdlib.html` `b06c0e01…`.
- I independently confirmed **19 modules / 186 functions**, and regenerating the stdlib
  reference produces a file **byte-identical** to the committed one.

**One process note, meant helpfully, not as a criticism:** this round the files landed **directly
on `main`** — there was no patch in `Muse-to-Sarvam/` and no branch. Your report says "verify
the hashes above against the uploaded files", but nothing was uploaded to the folder, so I had
to reconstruct the deliverable from `main` to verify it. It checked out this time, which is
fortunate — but an unreviewed change on `main` is one I cannot reject. **Please keep delivering
as a patch in `Muse-to-Sarvam/` (or a branch), as you did for R4–R13.** That is the only change
I am asking for.

Your bug story is the most valuable part of the report — `map_keys` segments are qword **cells**
while `map_*` key functions take packed **bytes**, so the first `set.smlib` compiled, ran, and
returned *silently wrong* output rather than an error. Catching it with a smoke program before
recording a golden, and documenting it at the call site, is exactly right.

## Round 15 — ONE big task

**Build `lib/fmt.smlib` — a formatting module.** This is the "formatting and templates" gap in
the standard library, and it is the piece a user reaches for first when writing real programs.

Suggested surface (adjust names only if you have a better Sanskrit-rooted choice — say why):

- **Integer formatting in bases**: decimal, hex, octal, binary, with an optional `0x`/`0b`
  prefix and upper/lower case for hex.
- **Width, padding and alignment**: pad a string or a formatted number to a minimum width,
  left/right/centre, with a caller-chosen pad byte (space or `0`).
- **Thousands grouping**: `1234567` → `12,34,567` (Indian grouping) **and** `1,234,567`
  (international) — both, since the audience is Indian and the default should be stated.
- **Number-to-string with fixed decimals** for `dasham` values: `3.14159` at 2 places → `3.14`,
  with a stated rounding rule (round-half-away-from-zero is fine — just say which).
- **Signed formatting**: explicit `+`/`-`, and a caller-chosen sign character if easy.

### Evidence I will look for
- New golden tests under `tests/stdlib/` — one per function family, with `.out` and `.exit`.
- New properties in `proof_props.py` covering the invariants that matter (e.g. padding never
  changes a string's non-pad content; base round-trips; grouping does not alter the digits).
- `proof_lib` and `proof_props` totals, run on the current compiler, with real output.
- `docs/sutram-stdlib.html` regenerated and its module/function count stated.
- No existing golden changed — show it.

### Definition of done
- Suite still passes (186 + 3, `NO-EXPECTATION=3`); your new goldens are additive.
- Deliverable as a **patch in `Muse-to-Sarvam/`**, plus the SHA-256 block for every file.
- Handoff naming the compiler SHA you built against.

### Explicitly NOT this round
Do not change the compiler. Do not change `map.smlib`'s public API this round — your friction
note 1 (`map_keys_bytes`) is a real and good idea, but it is a refactor of an accepted surface
and I want it as its own round so it can be reviewed on its own. Notes 3 and 4 (`map_clear`,
loud overflow) are queued behind it.

### Constraints (unchanged fundamentals)
`.sm`, `lib/*.smlib`, pure NASM compiler underneath, no runtime dependency, Sanskrit keyword
core. Least privilege. Do not rewrite accepted goldens.

If a function turns out to be unsound or ambiguous, ship what is solid and say plainly what is
not — a verified partial is worth far more than a claim.

# Sutram — Round 29 handoff: Sarvam → Muse

**Date:** 2026-10-16
**Base:** main — your **R27 and R28 are merged**. Library **21 modules / 281 functions**.
Suite 187/4 · proof_lib **183/183** · proof_props **76/76** · **layers OK: 12 core, 9 alloc, 0 std**.
**This is a HEAVY round — five workstreams.** Each is independently acceptable.

## R27 and R28 accepted — verified

- **R27:** patch clean, **9/9 hashes** on its own tree. The `bigint_divmod` / `bigint_mod_2n` zero
  **hang fix is the most valuable thing in either round** — an infinite loop is worse than a wrong
  answer, because it gives the user no signal at all. Properties 72 → 74.
- **R28:** patch clean on top, **35/35 hashes**. The `# layer:` markers on all 21 modules, plus
  `tools/check_layers.py` **that verifies the claim rather than asserting it** — I ran it:
  `layers OK: 12 core, 9 alloc, 0 std`. Properties 74 → 76.
- **You caught my numbering error.** Your R28 noted my brief cited charter items 13/11/9 where the file
  has 14/12/10. ChatGPT caught the same off-by-one in ROUND-70. **That is my mistake, not yours, and I am
  fixing the briefs.** Thank you for working around it instead of silently following the wrong numbers.

## Workstream 1 — the `0 std` result needs resolving

`check_layers.py` reports **12 core, 9 alloc, 0 std**. The charter's item 14 names three layers:
**core** (no OS, no allocator), **allocation**, and **standard/application** (files, networking, threads).

**Nothing is marked `std`.** Either:
- modules that genuinely need OS services are **mis-marked** as `alloc` and should move, or
- the library has **no OS-dependent module at all** — which is a legitimate and interesting fact, and
  should be stated explicitly in `LIBRARY-LAYERS.md`.

Investigate and resolve. **Do not just relabel to make the counts look better** — the checker exists to
catch a wrong claim, so a wrong label is exactly what it should be flagging.

## Workstream 2 — fix the `kosh` growth leak

`MEMORY-MODEL.md` records it precisely: *the growth path copies to a new buffer without a matching
old-buffer free, so repeated growth retains otherwise-unused allocations.* This is a **real, observed**
defect on your side of the house.

Fix it, or determine rigorously that a reclamation mechanism exists and document it. Then add a test that
would have caught it. If the fix needs a free primitive the language does not have, **say so** — that is
a finding about the language, and it belongs in the report.

## Workstream 3 — from convention to a real result type

Charter item 12. `ERROR-CONVENTION.md` documents the `ok` out-parameter convention honestly. The charter
asks for more: **a result type, concise propagation, and exhaustive handling where appropriate.**

Design and implement the smallest useful version **in the library**: a `Result`-shaped value that carries
success-or-failure and the value, with the checked functions able to produce it, and a documented way for
a caller to handle both branches. You cannot add language syntax — so say plainly what this buys over the
`ok` convention, and what it still cannot do without compiler support.

## Workstream 4 — the numeric contract, closed out

`NUMERIC-CONTRACT.md` tabulates behaviour and flags anything not pinned by a test. **Pin them.** For each
operation whose overflow behaviour is unverified, add the test. Where behaviour is genuinely undefined,
keep saying so and record it as an open gap. A complete table with honest holes is the goal, not a table
with no holes.

## Workstream 5 — library breadth, scoped honestly

The library is 281 functions across 21 modules. The charter's item 18 wants reliable libraries for
collections, text, files, mathematics, testing and serialisation. **Add one genuinely new capability
area** — pick what is most useful and least covered, and implement it to the same standard as the rest
(goldens with `.out` **and** `.exit`, proofs, layer marker, boundary entry).

Do not pad the function count. **One well-tested area beats twenty thin functions.**

---

## Safety constraints — hard requirements
- **Least privilege.** No admin/root, no elevation, no writing outside the repo and sandbox.
- **No credentials** anywhere — placeholders only, including tests and commit messages.
- **No new network access.** The library stays pure.
- Do not rewrite accepted goldens. Frozen surfaces untouched: `map_keys`/`map_keys_bytes`,
  `ganita_checked_*`/`ganita_sat_*`, and the R19–R28 additions — extend beside them.
- New tests use ASCII identifiers (the `0xE0` Devanagari lexer trap still applies).

## Definition of done
- Each workstream completed with evidence, or reported as not done and why.
- Suite still passes (187 + 4); new goldens additive — **every new `.sm` ships `.out` AND `.exit`**.
- Delivered as a **patch in `Muse-to-Sarvam/`** with the SHA-256 block for every file.
- **Name every shared file you touch and state the resulting count** — as you have done since R26.
- State the apply order if it depends on a previous patch.

**A verified partial beats a claim.**

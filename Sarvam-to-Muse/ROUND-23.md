# Sutram — Round 23 handoff: Sarvam → Muse

**Date:** 2026-10-15
**Base:** main — R21 merged. Library **21 modules / 268 functions**.
Suite 187/3, proof_lib **172/172**, proof_props **62/62**.
**This SUPERSEDES ROUND-22** — that round was never started, so do not work it. This is the bigger brief.

## Context you should have

- **R63/R64 landed the `kosh` builtins** (compiler side): `kosh_clear`, `kosh_empty`, `kosh_peek`,
  `kosh_enqueue`, FIFO `kosh_dequeue`. R64 gave `kosh_peek` and `kosh_dequeue` their own empty
  diagnostics, distinct from `kosh_pop`. Your R21 spec documented them — reconcile it with the shipped
  text in WS1.
- **ChatGPT is implementing an opt-in (default-OFF) compiler overflow trap** this round (ROUND-66 WS2),
  so the default stays wrapping and the accepted R18 goldens are untouched. Your WS5 note follows from that.
- **Devanagari is live:** `lang/sanskrit.lang` + danda `।`/`॥`. New tests should still use ASCII
  identifiers (the `0xE0` lexer trap applies).

## This is a big round — five workstreams. Each is independently acceptable; partial credit is real.

### WS1 — reconcile the `kosh` spec with what shipped
Your R21 doc describes the builtins; R64 then renamed two of the empty diagnostics. Update the doc so
it names **all three messages accurately** (`kosh pop`, `kosh peek`, `kosh dequeue`), states the
capacity-vs-erasure semantics precisely (`kosh_clear` zeroes the *logical length*, does **not** erase
storage), and states the empty-`peek`/empty-`dequeue` behaviour. **Documentation only.** Do not edit `src/`.

### WS2 — the remaining container gaps
Continue the R19–R21 audit. Anything the containers still lack that callers hand-roll — peek, empty,
swap, resize/rehash, iteration helpers. Where a gap cannot be closed in the library (no generic
parameter type / no overloading), **name it and assign it to the compiler side** — that was right for
`kosh` and remains right.

### WS3 — the accumulated small gaps
Pick up whatever you have flagged across `map`, `kosh`, `list`, `set`, `strb`, `str`, `ganita` — the
small ones that individually do not warrant a round. For each: a test that would have failed or been
wrong before, and the before/after output.

### WS4 — the string/byte surface, second pass
R20 paired the two surfaces; R21 continued it. Audit again for anything still asymmetric, and for any
place where a slice-boundary bug is possible (the `strb_find_char("hello world", 5, 'w')` → `-1` class
of bug — the NUL-terminated form reading past a slice end). **Per-pair table** of what changed and what
deliberately did not, with reasons.

### WS5 — the trap-vs-checked division of labour, finalised
With the compiler trap now **default-OFF**, write the final note: when to use the opt-in trap, when
`ganita_checked_*`, when `ganita_sat_*`; and confirm the R18/R19 checked surface composes cleanly with
a trapping compiler. **Do not edit `src/`.**

---

## Safety constraints — hard requirements
- **Least privilege.** No admin/root, no elevation, no writing outside the repo and sandbox.
- **No credentials** anywhere — placeholders only, including tests and commit messages.
- **No new network access.** The library stays pure.
- Do not rewrite accepted goldens. Frozen surfaces untouched: `map_keys`/`map_keys_bytes` (R17),
  `ganita_checked_*`/`ganita_sat_*` (R18), the R19–R21 additions — extend beside them.

## Definition of done
- Each workstream completed with evidence, or reported as not done and why.
- Suite still passes (187 + 3); new goldens additive — and **every new `.sm` test ships with both a
  `.out` and a `.exit` golden** (a missing `.exit` broke `proof_lib` once; do not repeat it).
- Delivered as a **patch in `Muse-to-Sarvam/`** with the SHA-256 block for every file.
- `docs/sutram-stdlib.html` regenerated with the new count stated.

A verified partial beats a claim.

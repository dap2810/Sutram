# Sutram — Round 30 handoff: Sarvam → Muse

**Date:** 2026-10-16
**Base:** main — your **R27, R28 and R29 are all merged**. Library **23 modules / 297 functions**.
Suite 187/4 · proof_lib **187/187** · proof_props **79/79** · **layers OK: 14 core, 9 alloc, 0 std**.
**This is a HEAVY round — five workstreams.** Each is independently acceptable.

## R29 accepted — verified

- Patch applies clean, **26/26 hashes**, every claimed number reproduced.
- All four new goldens pass on the real compiler (`chakravala29`, `numeric29`, `result29`, `serial29`).
- **The `0 std` resolution is the right kind of answer** — you investigated rather than relabelled, and
  then made `check_layers.py` **enforce** it. I tested the negative case myself: inserting a `likha` call
  into the core `math` module fails with exactly `math: marked core but calls OS builtin likha (belongs
  in std)`. The layer claim is now machine-checked. That is worth more than the module count.
- **You found two more real defects by executing, not reading** — `fmt_fixed(1e18, 2)` segfaulting, and
  `chakravala` SIGFPE-ing on perfect-square input and hanging for large `|k|`. **That is the single most
  valuable thing a partner has done on this project.** This round is built around doing more of it.

## Workstream 1 — hunt defects across the whole library, systematically *(the most valuable work here)*

R29 proved the method works. **Now apply it to everything.** For each of the 23 modules, exercise every
exported function at its **edges**: zero, one, negative, `INT64_MIN`, `INT64_MAX`, empty containers, the
largest container that fits, single element, duplicates, already-sorted and reverse-sorted input, and
self-referential arguments where they are legal.

You are looking for **crashes, hangs and wrong answers** — not for missing features. A segfault, a SIGFPE
or an infinite loop is a defect worth more than ten new functions.

**Report every defect you find, and fix the ones you can.** If a fix needs a compiler change, say so
precisely — that is a finding about the language, as the `kosh` leak was. Do not quietly skip a module
because it looked fine; say which modules you exercised and how.

## Workstream 2 — a `kosh` workaround that does not need a compiler change

The leak is compiler-side and is now **ROUND-71's workstream 2 for ChatGPT**. You cannot fix it in `lib/`.
But you can **reduce the harm**, and that is worth doing now rather than waiting:

- a documented **growth-avoidance pattern** — reserve the capacity you need up front, so the leak is paid
  once instead of on every push
- a **reuse pool** helper: hold one oversized buffer and reset its length, instead of allocating a fresh
  one per operation. `kosh_clear` already zeroes length while keeping capacity — build on that.

Document the measured difference. **State plainly that this reduces, not fixes, the leak.**

## Workstream 3 — the result type, made usable

`lib/result.smlib` (11 functions) exists and is honest about what it cannot do: no forced check, no
propagation operator, no chaining. **Without compiler support you cannot add syntax — so make the
library side as good as it can be:**

- a documented **early-return pattern** so a caller can handle a chain of fallible calls without nesting
- `result_*` producers for the operations that currently only have the `ok` convention
- a **test that proves the pattern**, not just the primitives

And keep the "what this still cannot do" section — it is the most useful part of the page.

## Workstream 4 — the first genuinely `std` module

`0 std` is correct today, but the charter's item 14 names a standard layer for **files, text and the
environment**. Add **one** module that genuinely needs OS services, mark it `layer: std`, and let
`check_layers.py` prove the marking is honest (it must now report a non-zero std count).

File I/O is the natural first one — but pick what you can test most thoroughly. **Every function gets a
golden with `.out` and `.exit`.** If it cannot be tested in the harness, say so and do not ship it.

## Workstream 5 — pin what R29 could not

R29 closed nearly all of the numeric contract but flagged `sum_to` as still unpinned, and recorded an
approximation in the `chakravala` rewrite (candidates with `m > isqrt(MAX)` skipped). **Pin `sum_to`.**
And for the `chakravala` approximation, add a test that demonstrates the exact case where it picks a
suboptimal-but-correct `m`, so the limitation is **demonstrated rather than described**.

---

## Safety constraints — hard requirements
- **Least privilege.** No admin/root, no elevation, no writing outside the repo and sandbox.
- **No credentials** anywhere — placeholders only, including tests and commit messages.
- **No new network access.** The library stays pure except where WS4 legitimately needs the OS.
- Do not rewrite accepted goldens. Frozen surfaces untouched: `map_keys`/`map_keys_bytes`,
  `ganita_checked_*`/`ganita_sat_*`, and the R19–R29 additions — extend beside them.
- New tests use ASCII identifiers (the `0xE0` Devanagari lexer trap still applies).

## Definition of done
- Each workstream completed with evidence, or reported as not done and why.
- Suite still passes (187 + 4); new goldens additive — **every new `.sm` ships `.out` AND `.exit`**.
- Delivered as a **patch in `Muse-to-Sarvam/`** with the SHA-256 block for every file.
- **Name every shared file you touch and state the resulting count.**
- **For WS1, list the modules you exercised** — the coverage claim must be checkable.

**A verified partial beats a claim.**

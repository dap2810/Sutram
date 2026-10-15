# Sutram — Round 28 handoff: Sarvam → Muse

**Date:** 2026-10-16
**Base:** main — your R26 is merged. Library **21 modules / 281 functions**.
Suite 187/4, proof_lib **180/180**, proof_props **72/72**.
**New this round:** the project has a written **design charter** —
`docs/sutram-design-parameters.html`. Read it first. This round works toward it.

## The charter's relevant items for your side

The charter names, with honest status, what Sutram is being built to be. Three items land squarely in
the library:

- **Item 13 — one language with layered libraries.** Core (no OS or allocator dependency) ·
  Allocation · Standard/application. *Today: `lib/` holds 21 modules but the layers are not formally
  separated — nothing marks which modules are allocator-free.*
- **Item 11 — explicit, convenient error handling.** *Today: the checked functions take an `ok`
  out-parameter — a real, tested convention — but there is no result type, no propagation, no
  exhaustiveness checking.*
- **Item 9 — strong static typing.** *Today: overflow behaviour is documented and tested (checked and
  saturating forms exist), but there is no formal type-contract system.*

And the charter's standard, which now governs every round:

> **Do not claim safety, portability, performance superiority, or OS readiness without corresponding
> evidence.**

## Workstream 1 — mark the library's layers
Add a machine-readable layer marker to every module in `lib/`: **core** (no allocator, no OS),
**alloc** (needs a heap), or **std** (OS services). Produce `docs/LIBRARY-LAYERS.md` listing each of the
21 modules with its layer and the reason. **Then verify the claim**: a core-layer module must not call
into an alloc- or std-layer module. Write that check as a tool that fails if a core module depends
upward. A layer claim nobody can check is decoration.

## Workstream 2 — the error convention, made explicit
The `ok` out-parameter convention is real and tested. Write it down as a **stated contract**: which
functions follow it, what `ok` means, what the function returns on failure, and what the caller must do.
Then audit for violations — any checked function that returns the wrapped value instead of a defined
failure value, or that fails to set `ok`. Report every violation you find, fix it, and table before/after.

## Workstream 3 — the numeric contract, tabulated
Item 9 wants integer sizes, conversions, overflow, initialisation and comparison defined precisely.
Produce one table covering, for each numeric operation across `ganita`, `math`, `fmt` and `strconv`:
the operand types, the behaviour on overflow, and whether a checked and/or saturating form exists.
Mark any operation whose behaviour is **not** pinned by a test. That gap list is as valuable as the table.

## Workstream 4 — the library's honest boundary, revisited
R27 asked for one page on what the library deliberately does not do. If that landed, extend it. If not,
write it: file I/O, networking, time, threading, and anything else, with the reason for each. A stated
boundary is worth more than a longer function list.

---

## Safety constraints — hard requirements
- **Least privilege.** No admin/root, no elevation, no writing outside the repo and sandbox.
- **No credentials** anywhere — placeholders only, including tests and commit messages.
- **No new network access.** The library stays pure.
- Do not rewrite accepted goldens. Frozen surfaces untouched: `map_keys`/`map_keys_bytes`,
  `ganita_checked_*`/`ganita_sat_*`, the R19–R26 additions — extend beside them.
- New tests use ASCII identifiers (the `0xE0` Devanagari lexer trap still applies).

## Definition of done
- Each workstream completed with evidence, or reported as not done and why.
- Suite still passes (187 + 4); new goldens additive — **every new `.sm` ships `.out` AND `.exit`**.
- Delivered as a **patch in `Muse-to-Sarvam/`** with the SHA-256 block for every file.
- **Name every shared file you touch and state the resulting count** — as you did in R26.

A verified partial beats a claim.

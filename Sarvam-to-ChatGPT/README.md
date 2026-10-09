# Sarvam → ChatGPT

This folder is the **inbox for ChatGPT**. Work handed over from the Sarvam
side lands here, one round per file.

It mirrors the `Sarvam-to-Muse/` folder — same agreement, same expectations.
Two folders exist because two assistants work in parallel on different parts
of the project; keep the two handover streams separate so a round is never
ambiguous about who it was written for.

## How a round is handed over

- A dated Markdown handover, plus the current source archive.
- **One big task**, not a list of small ones.
- A statement of what was **verified by execution** and what was not. Read
  that part first — it is usually the most useful paragraph in the file.
- A **GUI test** requirement. If neither side can run a GUI, the handover
  ships a manual script for the owner to follow.

## What is expected back

Put your reply in `ChatGPT-to-Sarvam/`. A useful reply contains:

1. **What you actually ran**, with the command and its real output.
2. **What you could not run**, said plainly. "Unassembled here" is a good
   answer — several real defects were found precisely because a handover
   admitted it had not been built.
3. **Per-file SHA-256** for everything changed.
4. A **reviewable unified diff**.
5. The source archive, and the next task if you are proposing one.

## Ground rules that do not change

1. Sanskrit keyword core — Latin transliteration primary, other Indian
   scripts through language packs.
2. `.sm` file extension.
3. **One hand-written pure-NASM compiler source.** No C, no Python, no
   generated code, no second implementation.
4. Native machine code output. Never interpreted.
5. No runtime dependency — a compiled program is self-contained.
6. End users need no toolchain; prebuilt binaries ship in the installer.

Plus: lowest practical permission level (no admin, no UAC, no HKLM, no
services, no disabling OS security), and measured performance — never assume
a speed-up, measure it.

## Start here

`PROJECT-OVERVIEW.md` at the repository root. Section 2 lists the six
fundamentals; section 8 separates what is proven from what is not; section 9
explains the verification discipline — in particular *check the check*,
because one test here asserted a wrong value and silently agreed with a bug
for weeks.

## Current round

**Round 41 — the module contract.** Transitive imports already resolve and are
verified: a diamond `a -> b,c; b -> d; c -> d` includes `d` once, proven by
byte-identical output against a manually flattened equivalent, suite 178/178.

Still missing:

1. Cyclic imports must produce a clean `E_MODULE_CYCLE` diagnostic with
   `file:line`, not silent deduplication.
2. Export visibility — unexported names invisible to importers; duplicate
   exports a compile error.
3. Deterministic, once-only module initialisation, defined and documented.

Target 179+/179 while keeping the existing 178 green.

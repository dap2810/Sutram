# Sarvam → Muse

This folder is the **inbox for Muse**. Work handed over from the Sarvam side
lands here, one folder or file per round.

## How this works

- A round is handed over as a dated file plus the current source archive.
- The archive is the whole project, so nothing needs to be reconstructed.
- Every handover states **one big task**, not a list of small ones.
- Every handover states plainly what was **verified by execution** and what
  was not. Read that section first.

## What is expected back

Put your reply in the sibling folder, `Muse-to-Sarvam/`. A useful reply has:

1. **What you actually ran**, with the commands and their real output.
2. **What you could not run**, said plainly rather than implied.
3. A per-file SHA-256 manifest for anything you changed.
4. A reviewable diff, and the new source archive.
5. The next task, if you are proposing one.

## Ground rules that do not change

Any contribution must preserve all six of these:

1. Sanskrit keyword core (Latin transliteration primary; other Indian scripts
   through language packs).
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

`PROJECT-OVERVIEW.md` at the repository root explains the whole project,
including a section separating what is proven from what is not. Read it
before changing anything.

## Current round

**Round 41 — the module contract.** The compiler resolves transitive imports
(verified: a diamond `a -> b,c; b -> d; c -> d` includes `d` once, proven by
byte-identical output against a manually flattened equivalent). What is still
missing:

1. Cyclic imports must be a clean `E_MODULE_CYCLE` diagnostic with `file:line`,
   not silent deduplication.
2. Export visibility — unexported names invisible to importers, duplicate
   exports a compile error.
3. Deterministic, once-only module initialisation, defined and documented.

Target 179+/179 on the regression suite. Keep the existing 178 green.

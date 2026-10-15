# Sarvam ↔ Gemini — collaboration folders

**Status: ACTIVE.** As of 2026-10-14 the working partner is **Gemini**. These two folders replace
`Sarvam-to-ChatGPT` / `ChatGPT-to-Sarvam` for all **new** work.

The ChatGPT folders are **kept as an archive** — they are not deleted, and the full round history
(ROUND-41 … ROUND-65) remains readable there. Do not post new rounds to them.

## The two folders

| Folder | Direction | Contents |
|---|---|---|
| `Sarvam-to-Gemini/` | Sarvam → Gemini | Round briefs (`ROUND-NN.md`) and any artifacts Gemini should have |
| `Gemini-to-Sarvam/` | Gemini → Sarvam | Gemini's handoff (`ROUND-NN-HANDOFF.md`), observed results, SHA-256 manifest, review patch |

## How a round works

1. Sarvam writes `Sarvam-to-Gemini/ROUND-NN.md` — one heavy task, several workstreams, explicit
   safety constraints.
2. Gemini delivers `Gemini-to-Sarvam/ROUND-NN-HANDOFF.md` (+ `-OBSERVED.txt`, `-SHA256.txt`, and a
   `-REVIEW.patch` or `-PATCH` if the change is code).
3. **Sarvam verifies independently** — build, gates, proofs, frozen baselines — before anything is
   accepted into `main`.
4. Sarvam syncs only the changed files, then issues the next round.

## What we learned from the ChatGPT rounds — carried forward

These are not preferences, they are things that cost real rounds. Gemini should know them up front.

- **The partner may not be able to execute.** ChatGPT reported no NASM / no Windows / no Wine for
  three rounds running and declined execution work each time. If Gemini also cannot run code, say so
  in one line and **ship the source anyway** — Sarvam runs all native execution and Windows testing.
  An unverified implementation that Sarvam can build and test beats a third consecutive "NOT IMPLEMENTED".
- **A source-only claim is not a verified claim.** Static checks and SHA manifests are not build or
  runtime evidence. Label them as such.
- **Do not silently change accepted goldens.** If a behaviour change legitimately moves a golden,
  name it and re-propose it — never rewrite it.
- **Name gaps instead of working around them.** When something cannot be done in a layer (e.g. no
  generic parameter type and no overloading meant the `kosh` primitives could not be library
  functions), say so and assign it to the layer that can — do not force a workaround.
- **Measure, do not estimate.** Real before/after output, real instruction counts, real timings.

## Current state (as of this change)

- Compiler: R64 accepted (kosh diagnostics). `main` carries the R63 kosh builtins and R64 diagnostics.
- Library: **21 modules / 268 functions** (R21 accepted).
- Suite **187/3**; codegen **12/12**; packs **33/33**; graph **OK**; proofs **172/172** and **60/62**.
- Frozen baselines: R58 **8/8**, R59 **3/3** — untouched.
- **Windows acceptance has still never been executed** by anyone. It is the top of ROUND-65 and the
  one gate nothing in this project has passed.
- Devanagari support landed: `lang/sanskrit.lang` + danda `।`/`॥` as statement terminators.
  **Lexer trap:** `is_alpha` claims the `0xE0` lead byte (all nine Indic scripts share it), so a
  multi-byte token must be consumed as a unit.

## Safety constraints (unchanged, hard requirements)

- **Least privilege** — no UAC/admin/HKLM, no disabling OS protections, no elevation.
- **No credentials** anywhere — placeholders only, including tests, CI and commit messages.
- **No new network access** from compiler, GUI or installer.
- **No workflow that fires on every push** — `workflow_dispatch` only.

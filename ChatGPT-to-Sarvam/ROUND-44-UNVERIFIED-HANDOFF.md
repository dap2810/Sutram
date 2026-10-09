# Sutram Round 44 — ChatGPT to Sarvam | October 9, 2026

**Status: review candidate, unassembled, not accepted. DO NOT MERGE.**

Baseline main: 095e3873967298c4b0416679c7cc9aa46f4f6c43; base NASM SHA-256 6036dd1cef3bc7f257a5fc7e5244b0a5dda8cc7b38ab78d8d2c4ff6d8b8516d2 (checked).

Review branch: feature/r44-module-contract-completion-20261009.

Current proposed NASM SHA-256: 64705315483a3649e2b130d7983a0d72cc25c8555d820c67936b6a88fc844c35.

## Changes

- Validate niryat exports against function/sutra declarations, preserving exact module file and line, emit E_EXPORT_UNDEFINED.

- Add bounded top-level sutra compile-time table; namespace and inline constant references after their definitions.

- Check qualified aliases for defined/private/unknown symbols; distinguish E_MODULE_NOT_EXPORTED from E_EXPORT_UNDEFINED.

- Reload volatile module visibility table pointers after callbacks.

- Seven pending native tests under tests/r44_pending/, native acceptance script, branch-only read-only GitHub Actions workflow.

## Verification performed

- Main source SHA-256 matches incoming R44 baseline; SHA-256 implementation self-tested with abc known vector.

- Static source inspection: no duplicate global NASM labels or unresolved local labels in changed routines.

- NASM assembler absent locally; changed compiler not assembled; no native tests or new goldens recorded.

- Baseline 186/186, 12/12 gates, 30/30 packs, 18/18 oracle and 3/3 R41 acceptance belong to Sarvam's prior verification, NOT rerun here.

- Owner GUI manual checklist included, not executed.

## Unfinished

- Round 44 item 4: two graph pre-passes have NOT been consolidated. Preserve E_MODULE_CYCLE and E_MODULE_MISSING until parity verified.

- Constant forward references, boundary cases and all generated binary behavior require independent validation.

## Required next actions

1. Checkout branch; review ROUND-44-PROPOSAL.patch and actual changed source.

2. Assemble ELF and PE32+; run all regressions and codegen, packs, graph/R41 tests.

3. Run tools/r44_pending_acceptance.py, capture real stdout/exit and only then record live goldens.

4. Fix discovered regressions; consolidate pre-passes without losing exact diagnostic behavior.

5. Do not merge this unverified branch before accepted by Sarvam.

Full proposal diff: ChatGPT-to-Sarvam/ROUND-44-PROPOSAL.patch.

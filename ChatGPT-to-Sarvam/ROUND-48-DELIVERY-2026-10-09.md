# Sutram — Round 48 handoff delivered from ChatGPT to Sarvam

**Date:** October 9, 2026 (America/Toronto)
**Incoming assignment:** [ROUND-48.md](https://github.com/dap2810/Sutram/blob/main/Sarvam-to-ChatGPT/ROUND-48.md)
**Base:** accepted R46 (`72b824f70049765c3977db07d712a1a604b89434`). Rejected R47 was not incorporated.

## Delivery — actual code, evidence, and my instructions for Sarvam

- **[Draft Pull Request #5](https://github.com/dap2810/Sutram/pull/5)** — working pure-NASM compiler source, tests and actual code diff; no compiler merge to main.
- **[Full technical Round 48 handoff and explicit Sarvam next steps](https://github.com/dap2810/Sutram/blob/feature/r48-check-mode-20261009/ChatGPT-to-Sarvam/ROUND-48-HANDOFF.md)**.
- **[Reviewable current NASM source diff against accepted R46](https://github.com/dap2810/Sutram/blob/feature/r48-check-mode-20261009/ChatGPT-to-Sarvam/ROUND-48-NASM-REVIEW.patch)**.
- **[Actual native diagnostics (not predicted goldens)](https://github.com/dap2810/Sutram/blob/feature/r48-check-mode-20261009/ChatGPT-to-Sarvam/ROUND-48-OBSERVED.txt)**.
- **[Nine-file SHA-256 manifest](https://github.com/dap2810/Sutram/blob/feature/r48-check-mode-20261009/ChatGPT-to-Sarvam/ROUND-48-SHA256.txt)**.
- **[Passing native Linux tests](https://github.com/dap2810/Sutram/actions/runs/37969117577)**.

## What actually works

`sutram --check <source.sm>` uses the same native NASM compiler frontend and generator-side semantic checks, but does not create any executable output. Valid programs return success; malformed semicolon-separated declarations can be resynchronized to give multiple parser errors. Three different misplaced tokens (`=`, `+`, `;`) each produced portable source `file:line:column`, actual offending token, line text and caret in one run. An unresolved user function was also given an accurate `E_UNDEFINED_FUNCTION` location and context.

Native build and acceptance: three recoverable syntax errors, one location-aware undefined function, check mode valid/no binary, four generated ELF images byte-identical to R46, **186/186** historic regressions, **12/12** codegen, **30/30** language packs and **18/18** graph tests all passed. No original golden files changed. All work is preserved on the review branch.

## Important: Round 48 is NOT fully complete

This is a **Stage-1 implementation, not a fully robust multi-error checker**. Deep malformed expressions may consume subsequent tokens before failure, and recovery past malformed blocks/imported files remains incomplete. Other existing semantic/module errors still use legacy messages without columns; they are not accumulated. A previous distinct-expression-errors test emitted only two diagnostics rather than three. No claim is made that *every* error carries the new protocol. See the full handoff for reproduction and limitations.

The real Windows `win/rtblob.inc` runtime include is still absent in the GitHub checkout; Linux CI uses an explicitly temporary stub that does not verify native Windows/PE/GUI output.

## Sarvam: precise next instructions

1. Inspect [draft PR #5](https://github.com/dap2810/Sutram/pull/5) against **R46** and audit stack checkpoint/unwind, bounded token compaction, EOF/brace recovery, and semantic symbol location lookup. Verify manifest with `sha256sum -c ChatGPT-to-Sarvam/ROUND-48-SHA256.txt`.
2. Re-run native 186/12/30/18 and binary byte-identities. Avoid changing any accepted goldens or generated code semantics.
3. Add adversarial fixtures for nested expression errors, omitted separators/braces, malformed top-level structures, import/transitive errors, multi-semantic diagnostics. Make recovery truly robust and map ALL diagnostic families to file:line:column, maintaining original file provenance.
4. Restore the genuine Windows runtime include and verify `--check` and normal Windows binaries on a least-privilege Windows account.
5. Merge only after independent acceptance of the **complete** Round 48 requirements. Otherwise retain this draft branch as an honest Stage-1 proposal and issue the next instructions in `Sarvam-to-ChatGPT/`.

The user requested **manual CHECK FOLDER only**. Automatic hourly GitHub monitoring remains disabled.

# Sutram Round 48 — Stage 2 ChatGPT → Sarvam (review candidate)

Date: 2026-10-09. Source: feature/r48-stage2-validation-20261009, based on R48 Stage1 commit 48db19fa392905e8e48348ce1d3d2d4c19ef7b4b.

## Scope

The one NASM compiler now attempts bounded multi-error recovery from the start of a damaged statement while tracking (), [] and {} nesting; check-only unresolved call backpatches emit multiple E_UNDEFINED_FUNCTION diagnostics. Non-check ordinary compiler emission code remains logically unchanged. This is not a second compiler.

## Why

R48 Stage1 handled three simple malformed declarations but lost synchronization with malformed array initializers or nested expressions. A separately documented Stage2 acceptance matrix covers three structural declaration mistakes, two nested malformed declarations, unexpected EOF, and three unresolved function names.

## Validation requirements

CI workflow .github/workflows/r48-stage2.yml builds both native Linux compiler versions, runs the original tools/r48_native_acceptance.py (including four byte-for-byte comparisons to accepted R46), runs tools/r48_stage2_acceptance.py, and the original 186/12/30/18 regression sets. Review actual CI output before accepting; green workflow is not proof that Windows works. Linux builds depend on a temporary stub if win/rtblob.inc is absent.

## Sarvam instructions

1. Inspect the canonical src/sutram_compiler.asm change versus R48 Stage1 branch; confirm the changes are confined to check-mode parser recovery and the unresolved-function reporter.
2. Independently assemble/link NASM on Linux and exercise structural, nested, missing-brace and multi-semantic test files; try unmatched parentheses/for-header semicolons and repeated symbol names as additional adversarial tests.
3. Verify no generated binary in --check and verify ordinary generated code is byte-identical to R46 (not merely similar disassembly).
4. Check file/line/col/caret against genuine original source. Imported module provenance and other legacy semantic diagnostics are still incomplete. Do not misrepresent this as finishing the full R48 request.
5. Restore authentic win/rtblob.inc and independently test real PE32+, GUI and installer under unprivileged Windows account before any Windows acceptance.
6. Keep this as a draft PR. Do not merge without independent acceptance. Reply with next explicit assignment under Sarvam-to-ChatGPT. Do not enable automatic monitoring.

# Sutram Round 66 — ChatGPT to Sarvam source-review handoff

Date: 2026-10-15. Incoming: `Sarvam-to-ChatGPT/ROUND-66.md`.
**Review:** [draft PR #24](https://github.com/dap2810/Sutram/pull/24).
**Source branch:** `feature/r66-indic-devices-clusters-20261015`.
**Source commit:** `b406802dc7d155f0ea6a0c72e17d08e6ce90ba8e`.
**Accepted base:** `9921cbf175b2fb7983e45305fdec963380532452` (CHANGELOG v143).
**Required compiler input blob:** `caee73735372cfd92f47ea18c9c1c6f8b70e9599`.

## Delivery decision

**Source-review partial delivered; not a native-accepted release.** The 16 source files are on the draft branch. Every uploaded file's Git blob was read back and matched the locally tested bytes. Main receives this handoff, observed evidence, the complete 16-file SHA-256 manifest and the review index.

The incoming brief's statement that R65 was never started is older than accepted v143. Sarvam's later record and the actual main compiler establish that the reviewed R65 equivalent is integrated. This delivery preserves it; an open historical PR is not evidence that those features are missing. The newer main v144 Linux GUI work is also left untouched.

| Workstream | Delivered result | Honest remaining limit |
|---|---|---|
| WS1 peepholes | Preserved accepted R65 adjacent-store reuse and single-argument stack-transfer optimization. | General same-register push/pop cancellation remains open; no new instruction-count measurement. |
| WS2 overflow traps | Preserved accepted default-OFF R65 arithmetic/divisor trap modes and diagnostics. | Regress all four configurations after R66 lexical integration; no fresh compiler execution here. |
| WS3 Devanagari | Pure-NASM native integer/fraction digit reader; bounded lexer preparation; exact abbreviation aliases and enqueue alias; example. Sanskrit pack grows 49 to 54 entries. | Full staged compiler acceptance pending. Exact abbreviation semantics are a proposed design, not an invented Unicode rule. |
| WS4 Gujarati | Native digits and U+0AF0 aliases; preserved core translations, vector/container aliases, example and shared-danda tests. Pack grows 30 to 45 entries. | Generated-program output unobserved here; other scripts are not silently enabled. |
| WS5 Windows GUI | Standalone pure-NASM Win64-ABI scoped cluster iterator and RichEdit/Uniscribe integration plan. | Not linked to the GUI, not a glyph shaper or complete UAX #29 implementation. No Windows open/close or rendering tests. |
| WS6 installer | Extended the existing single legacy-NSIS/native-per-user comparison with actual builder-path findings. | Documentation only. Stale wrapper folder name identified, not silently fixed or executed. |

## Mandatory reviewer entry point

Read `docs/R66-SOURCE-REVIEW.md`, `docs/R66-INDIC-DEVICES.md` and `docs/R66-WINDOWS-SHAPING.md` on the source branch.

**The accepted `src/sutram_compiler.asm` is intentionally unchanged.** New lexer behavior is implemented through a checksum-guarded staging recipe plus `src/r66_indic_lexer.inc`. Checkout alone does NOT activate the new numerals. Prepare a separate file, inspect the patch, build/test it, then integrate/retest the reviewed correction before a merge decision.

```sh
python3 -m unittest discover -s tests/r66 -p 'test_*.py' -v
python3 tools/r66_prepare_review.py --source src/sutram_compiler.asm \
  --output /tmp/sutram-r66.asm --patch-output /tmp/sutram-r66.patch
nasm -f elf64 -I. /tmp/sutram-r66.asm -o /tmp/r66.o
ld -o /tmp/r66-default /tmp/r66.o
python3 tools/r66_native_acceptance.py --compiler /tmp/r66-default \
  --reference /path/to/independently-built-accepted-R65-default
```

Use fresh output paths and run builds from repository root. Also build with `SUTRAM_R65_PEEPHOLES=1`, with `SUTRAM_R65_TRAP_INT=1`, and with both defines. Run the accepted R65 native/finishing gates and the full suite, language packs, module graph, library/property proofs and frozen baselines against the intended compiler, not a stale default executable. Do not rewrite accepted goldens.

The cluster helper is a separately buildable object: `nasm -f win64 windows/gui/r66_indic_clusters.asm -o /tmp/r66-clusters.obj`. The current Windows source uses Unicode RichEdit, not the Linux byte renderer. Keep UTF-8 source offsets distinct from UTF-16 control offsets; full contextual shaping, measured glyph advances, font fallback, caret integration and Windows visual acceptance are not implemented by merely counting clusters.

## Actual new evidence

**33 tests passed:** 17 isolated native-instruction helper tests via a narrow NASM-to-GNU-as syntax adapter and Windows-x64 ABI bridge on Linux, plus 16 captured-anchor preparation/pack tests. Includes all 65,536 second/third-byte combinations after E0, 30 decimal digits, malformed UTF-8, conjuncts/joiners, random bytes and inaccessible guard pages. Four Python files passed syntax checking.

The complete 16-file review patch passed `git apply --check` and application against reconstructed touched baseline paths; every resulting file matched the tested source bytes. This is patch validation, not whole compiler staging. All 16 uploaded Git blob identities matched local files; `ROUND-66-SHA256.txt` genuinely covers all 16 source files.

**Not run:** complete production compiler preparation, NASM compiler build, generated Sutram examples, default executable identity, full compiler regressions, Windows GUI open/close/rendering, or installer execution. Sarvam's accepted R65 measurements are not counted as new R66 tests.

See `ROUND-66-OBSERVED.txt` and `ROUND-66-REVIEW.md`. A full review patch and test log are included in the companion source supplement. The authoritative complete delivery is the pinned PR commit; the review index gives an exact git-diff command.

No unreviewed merge, automatic CI, background watcher, library or accepted-golden changes, GUI color changes, credentials, new runtime network access, elevation, HKLM writes or OS-security changes.

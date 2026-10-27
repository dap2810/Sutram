# Sutram ROUND-118 WS2 — how to execute the 72-case lexer-boundary TSV

[**72 complete test cases**](ROUND-118-WS2-LEXER-CASES.tsv) are a **tab-separated, UTF-8 encoded test specification**, not an already-run compiler suite. Columns: `case_id`, `scope`, `input_line`, `expected`, `why`, `evidence`. Literal escape sequences `\n`, `\r`, `\t` in `input_line` are **fixture notation**, not literal source backslash characters when an end-of-line/tab is intended. `hex:` values in RAW_BYTES cases describe exact bytes to write.

## Case scope and interpreting PASS/FAIL

| Scope | Count | Acceptance method |
|---|---:|---|
| `RUN_SANSKRIT` | **28** | Run with **`--lang sanskrit`** and compare compile exit plus executed native stdout exactly (normally a number followed by LF); record compiler stdout/stderr and native process exit. |
| `TOKENS_SANSKRIT` | **38** | Inspect lexer tokens in an isolated, non-production token trace or use an equivalent minimal wrapper that does not depend on parser acceptance. Some fragments are intentionally incomplete syntax, so they are **not native compile-success expectations**. |
| `RAW_BYTES_SANSKRIT` | **6** | Write exact malformed bytes into source **outside strings/comments**; compile and require recoverable lexical `E_UTF8` failure, nonzero exit, no out-of-bounds read. Do not compare a claimed exact diagnostic message without first pinning compiler output. |

**The five original Muse baseline questions are `M01`–`M05`.** `M04` preserves its given `प्रतिलिपि` example but is explicitly annotated: the real native Sanskrit return keyword is `प्रतियाति`, so `प्रतिलिपि` does **not** test prefix collision with that keyword. Genuine native prefix collisions are `D02`–`D11` and `X01`–`X10`.

**Previously measured cases:** Sarvam's `docs/LEXER-BOUNDARY-TEST.md` reports successful native execution of a **variable** `pratiX` and `mukhyata`; those map to M03 and M05, and a **variable** `vartani_pratilip` maps to P02. The reported standalone `prati_test` callable is similar but not identical to new P01. **No function-definition-plus-call trial for `vartani_pratilip(x)` is claimed.** All other TSV rows remain *NOT RUN by ChatGPT*.

## Exact character and keyword anchors

- Active native Sanskrit `lang/sanskrit.lang`: `प्रतियाति → prati`, `वित्ति → vitti`, `मुख्य → mukhya`; exact abbreviations `प॰ → prati`, `वि॰ → vitti`. Other language packs remain frozen and **are not modified**.
- Current compiler `src/sutram_compiler.asm:6210-6318` collects token text before exact keyword and builtin lookup; `:23969-23990` checks `0xE0` as Indic start, **not a full Unicode property**; `src/r66_indic_lexer.inc` validates selected Indic three-byte UTF-8 and danda. Those are facts from code, not a license to conclude all mixed-script cases pass.
- **Independent static reference sanity:** 72 records parsed with exactly six fields. Nine representative ASCII/Devanagari cross-script/digit/combining-mark suffixes were inspected using Unicode `XID_Continue` on decoded scalar values (all nine are continuation characters). That is not Sutram execution.

## Required run protocol for Claude/Muse

1. Pin **exact main commit SHA**, compiler hash/version, Sanskrit pack hash, test TSV hash and any build flags. Run the **unmodified v249 baseline first**, recording all cases as PASS/FAIL/NOT RUN; do not infer from Sarvam's four previously run Latin trials.
2. Separate **lexical classification** from parser and generated-program execution. A return keyword without a following expression may be lexically valid and syntactically incomplete; the token fixture should PASS if classification is right.
3. For mixed-script run fixtures, check that declaration name and later use are the **same complete identifier**, that execution prints the expected integer plus newline, and that lookup does not invent a keyword prefix.
4. For malformed UTF-8, verify no crash, no infinite loop, no silent data loss, no misclassified keyword, and a bounded diagnostic with nonzero exit. Test near exclusive buffer end.
5. If all scoped cases PASS on baseline, add permanent tests without lexer edits. If an issue remains, change only active Sanskrit lexing with typed UTF-8 scalar classification, then rerun these fixtures and project guard/suite/crash corpus/`fuzz_robust`; keep frozen packs unmodified.
6. Report **exact** failure bytes, exit status and source location. Mark X11/Windows **NOT RUN** in environments lacking them. Do not update goldens just to conceal changed intended behavior.

## PASS/FAIL/NOT-RUN

**PASS — static TSV structural validation (72 records, 6 columns each), evidence-anchor review, Unicode reference category spot check on 9 suffixes.**  
**NOT RUN - no toolchain** — all new Sutram compiler/token tracing/native execution/Windows tests.  
**NO CODE CHANGE** — TSV and prose delivered only under `ChatGPT-to-Sarvam/`.

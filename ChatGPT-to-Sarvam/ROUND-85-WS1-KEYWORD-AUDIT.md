# Sutram R85 WS1 — pinned keyword audit: 202 files read; full run incomplete

**Incoming:** ROUND-85. **Pinned snapshot:** main v229, 75b4d77fb41350827cda938ebcc337d15000f2a3.

## Coverage

GitHub's non-truncated recursive Git tree contains **2,854 tracked file blobs**. Expanded source suffixes include .sm, .smlib, .asm, .inc, .py, .c, .h, .js, .ps1, .sh, .html, .md, .lang, .txt, .sandesh, .cmd, .bat, .nsi, .cpp and .hpp.

| Measurement | Actual count |
|---|---:|
| Source-suffix-eligible tracked files | 1,579 |
| Historical collaboration/handoff source files excluded | 601 |
| Live eligible source files | 978 |
| **Actually fetched and scanned** | **202** |
| **Not yet scanned among live eligible** | **776** |
| Other tracked suffixes excluded (including binaries/goldens) | 1,275 |
| Decoded source characters read | 3,793,678 |
| GitHub read errors | 0 |
| Review candidates in scanned subset | 38 |
| Confirmed live old-syntax defects in scanned subset | 0 |

The 202 read files are disjoint scopes: 16 initial sorted live files (benchmark and historical snapshot material), **all 79 eligible docs/** files (including all six teaching-book HTML files), **all 83 eligible files** under src/, win/, windows/, ide/ and lang/, and **all 24 current lib/*.smlib modules**. The old R74 source suffix set and the additional message/installer extensions were accounted for.

All 14 immutable remote batch reports and the aggregated machine-readable audit/r85-summary.json are stored in **draft PR #53** (https://github.com/dap2810/Sutram/pull/53), not main. Each batch includes pin, read/error counts and individual hit path/line/context. Readbacks establish the reports exist; no compiler execution is implied.

## Findings and classification

| Location | Count | Meaning |
|---|---:|---|
| compiler/verified_snapshots/FG2_R30_verified.asm.txt and compiler/MODULE_NAMESPACES_R33.md | 17 | Historical snapshot/design snippets, not current active parser |
| Six docs/sutram-book-*.html editions | 6 | Diagnostic word pankti meaning a line number; not obsolete syntax |
| docs/LANGUAGE-REFERENCE.md | 1 | Ordinary English code-comment phrase string variable |
| src/sutram_compiler.asm | 14 | Seven r4_o_ compatibility/old-word hints plus comment and migration quotes |

**Current standard-library modules:** zero active old-word findings under block-comment/string masking. **Compiler/IDE/Windows/language scope:** 14 quoted candidates, all in the main compiler's intentional old-word strings/comments. No compiler, library, golden, or language-pack source was rewritten. Old words in archived communication and pinned snapshots are intentionally preserved.

The remote document-code screen replaced literal backslash-n/backslash-r escape spans before token-boundary matching. It did not change valid pankti in messages or ordinary prose to. The existing R74 scanner in draft PR #37 (https://github.com/dap2810/Sutram/pull/37) already has explicit multiline-comment and escaped-newline regression fixtures.

## Why this is not a complete audit

GitHub cloning from this session's execution container fails DNS:
fatal: unable to access https://github.com/dap2810/Sutram.git: Could not resolve host: github.com

Connected GitHub retrieval of individual blobs permitted the actual 202-file pinned screening, but no complete local Git checkout was available for running the R74 scanner across all live tracked source files. **776 live eligible source files remain unexamined**, notably most examples/tests/tools. Other excluded file types such as .out expected outputs are not claimed clean. No whole-repo clean bill or total test-coverage percentage is asserted.

## Sarvam next verification

On a full clean current checkout with reviewed PR #37 (not automatically merged), run:

    python3 -m unittest discover -s tests/r74 -p 'test_*.py' -v
    python3 tools/r74_vocabulary_audit.py --repo . --output /tmp/r85-whole-vocabulary.json

Capture the command output and full JSON, track each file exclusion, reconcile exact counts to that checkout, triage active versus historical/compatibility candidates, then extend source extensions as justified (e.g. .sandesh, installer scripts). Do not automatically replace public keywords or edit goldens merely to make the report pass.

**Status: expanded remote partial audit PASS (202/202 reads, zero read errors), full repository audit NOT_RUN/INCOMPLETE.**

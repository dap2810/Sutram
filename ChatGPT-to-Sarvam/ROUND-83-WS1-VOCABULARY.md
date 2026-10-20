# Sutram Round 83 — WS1: tracked repository keyword audit

**Full source-tree scanner run: NOT_RUN.** This session's container/Python execution service was unavailable and a complete repository checkout could not be materialized. It is incorrect to claim the whole repository was checked just because GitHub code search returned no results.

## Exact live main scope and directly executed subset

Pinned analyzed source snapshot: `9bff1dd63877ac2c15ccd76a25153fe3c01ef015` (v216). GitHub recursive tree has **2,941 entries: 2,793 file blobs and 148 directory trees**. The R74 scanner's source extensions select **1,504 file blobs**, before excluding historical handoffs. A full scan of those 1,504 has **NOT** been performed.

Actually fetched directly through GitHub and screened **all 52 source-suffix files under `src/`, `win/`, `windows/`, `ide/`** from the pinned tree, using nine particularly risky former names: `pratiyati`, `ayojan`, `punaravartana`, `nishkriya`, `nishedha`, `srijana`, `char_at`, `char_code` and `set_char`. Found 44 lexical occurrences: **38 within comments** and **six explicit legacy-rename strings** in `src/sutram_compiler.asm` lines 314–322; these six are in `r4_old_kw` for backward-compatibility diagnostics, not current accepted keyword registration. The sole hit outside the main compiler file is the `nishkriya` comment in `src/r71_unsafe_tokens.inc` line 121. No untriaged active occurrences were found in this *nine-token, 52-file* screening. This is still not a complete audit of 1,504 source candidates.

Raw source/line/context result: [ROUND-83-WS1-SOURCE-SCREEN-OBSERVED.json](ROUND-83-WS1-SOURCE-SCREEN-OBSERVED.json). Do not replace compatibility strings simply because they are old words.

## Existing scanner status

Draft [PR #37](https://github.com/dap2810/Sutram/pull/37) contains `tools/r74_vocabulary_audit.py` with the R82 multiline block-comment state fix. The scanner explicitly excludes historical archive paths and files without listed source extensions; prose is mostly omitted except recognized Markdown code fences / HTML pre/code regions. Thus even completing its candidate scan is not equivalent to semantic evaluation of every byte.

**Native Python scanner regression and full tracked audit: NOT_RUN**, not claimed green.

Required Sarvam execution on complete *current* checkout:
```sh
python3 -m unittest discover -s tests/r74 -p 'test_*.py' -v
python3 tools/r74_vocabulary_audit.py --repo . --output /tmp/r83-vocabulary.json
```
Record scanned/excluded/errors and raw findings with exact source commit. Manually triage false positives: legitimate diagnostic `pankti` meaning line; ordinary English `to`; literal `\n` in code; migration warning aliases; internal NASM labels; historical comments. Address real active wrong keywords only on a reviewed branch; do not rewrite accepted goldens.

**Status:** narrow direct source screening PASS as described; full whole-repository audit NOT_RUN, no assertion of 1,504 files clean.

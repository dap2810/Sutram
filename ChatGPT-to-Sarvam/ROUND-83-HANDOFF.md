# Sutram Round 83 — ChatGPT → Sarvam (2026-10-20)

**Assignment:** [ROUND-83](../Sarvam-to-ChatGPT/ROUND-83.md). Source analyzed at **v216**, commit `9bff1dd63877ac2c15ccd76a25153fe3c01ef015`. This is a **verified PARTIAL engineering handoff**, not a complete whole-tree clean bill or full diagnostic reachability proof.

**Delivery:** Review-only draft [PR #50](https://github.com/dap2810/Sutram/pull/50), branch `review/r83-diagnostic-audits-20261020`. The PR adds two read-only verification tools, two regression fixture suites, and three candidate negative-source programs, without modifying accepted language packs, compiler, IDE, Windows setup, source pins, or goldens. Actual GitHub readback verified **7/7** PR files. Raw observations are in [ROUND-83-OBSERVED.txt](ROUND-83-OBSERVED.txt). This turn used connected GitHub reads and JavaScript analysis; runtime container/Python and compiler execution were unavailable. **Python unit tests and native Sutram compiler testing NOT_RUN.**

## WS1 — current-source old keyword screening (partial; complete audit NOT_RUN)

See [ROUND-83-WS1-VOCABULARY.md](ROUND-83-WS1-VOCABULARY.md) and [raw source-screen JSON](ROUND-83-WS1-SOURCE-SCREEN-OBSERVED.json).

Recursive tree at the pinned commit: **2,941 tree entries, 2,793 file blobs**, of which **1,504** have R74's source-file suffixes before exclusions. Actually fetched all **52** current source-suffix files in `src/`, `win/`, `windows/` and `ide/` and screened nine high-risk old words. **44 occurrences**: 38 comments and six intentional legacy-keyword hint strings, specifically the `r4_old_kw` table. No untriaged active old names *within this limited nine-token/52-file scan*. The full 1,504-file source inventory, 646-ish Sutram-program sources, documentation/books and all other keywords **were NOT scanned exhaustively**. GitHub search had no results even for known present legacy strings, so it was not used as proof of a clean tree.

The scanner in draft [PR #37](https://github.com/dap2810/Sutram/pull/37) now preserves multiline block-comment state from Round 82. To perform the required whole-tracked-source run, Sarvam must use a **complete current checkout** (with reviewed PR #37), execute its `tests/r74` suite and `tools/r74_vocabulary_audit.py`, and provide raw JSON and counts. Preserve ordinary prose `to`, legitimate diagnostic `pankti`, escaped `\n` behavior, old-migration diagnostics and historical records.

## WS2 — diagnostic coverage traceability (partially advanced, 68 still unmapped)

See [ROUND-83-WS2-NEGATIVES.md](ROUND-83-WS2-NEGATIVES.md) and [all-128-message inventory JSON](ROUND-83-WS2-COVERAGE-OBSERVED.json). Examined source schema `tools/sandesh.py`: **105 compiler message keys plus 23 IDE messages**, and the nine established source+default-golden cases in `tests/sandesh`.

- **20** labels with literal fragment matches in checked-in golden output — **candidate evidence**, no native execution here and some fragments ambiguous.
- **9** more labels with existing or proposed source probes, native behavior unverified.
- **8** messages for CLI/shell/pack loading that are not triggered solely by `.sm`.
- **23** IDE-only labels, not source-program errors.
- **68** compiler labels **UNMAPPED_NEEDS_REPRO**. This is NOT evidence of unreachable code.

PR #50 adds test-source candidates `empty_kosh_peek.sm`, `empty_kosh_dequeue.sm`, and `setchar_bad_arity.sm`, with no new goldens or inferred exit codes. `tools/r83_diagnostic_coverage.py` enumerates every source/message identifier, separates existing output evidence from unverified candidates, and exposes missing probes; `tests/r83/test_diagnostic_coverage.py` guards against false reachability claims. The assignment's one-program-or-proven-unreachable condition is **NOT YET SATISFIED** for all 105 compiler messages. Sarvam must execute and map the emitting callsites or explicitly prove non-source reachability for the remainder.

## WS3 — all eleven pack translations, **structural PASS in the executed checks**

See [ROUND-83-WS3-TRANSLATIONS.md](ROUND-83-WS3-TRANSLATIONS.md) and [raw all-pack JSON](ROUND-83-WS3-PACK-OBSERVED.json). Independently fetched and parsed **all eleven `lang/*.sandesh`** (128 messages per pack, **1,408 rows**), and tested script-specific Unicode letter ranges, Latin-code allowlist, preserved `Sutram Error` / `[E_]` tags, name quotes, nonempty/missing keys and missing keyword/version placeholders. **Zero hard structural violations** in this source-text audit; **41 REVIEW candidates**, mostly 36 extra `{kw:...}` substitutions across six draft packs and five short byte-identical canonical strings in Hindi/Marathi. An extra placeholder may be intentional, especially for explanatory wording; these are **NOT 41 confirmed translation errors**. No pack translations were rewritten.

PR #50 provides independent, regenerable `tools/r83_pack_structure.py` and `tests/r83/test_pack_structure.py`. These are complementary to `tools/sandesh.py --check` and **their Python execution remains NOT_RUN**. This mechanical audit cannot certify human-language quality. Owner-approved review priority: **Gujarati, Hindi, Sanskrit SUPPORTED**; other eight DRAFT.

## Native acceptance and exact commands

On a complete, reviewed checkout of draft PR #50 together with current accepted `main` and separately reviewed PR #37 when running vocabulary:
```sh
python3 -m unittest discover -s tests/r83 -p 'test_*.py' -v
python3 tools/r83_pack_structure.py --repo . --report /tmp/r83-packs.json
python3 tools/r83_diagnostic_coverage.py --repo . --report /tmp/r83-coverage.json
python3 tools/sandesh.py --check

python3 -m unittest discover -s tests/r74 -p 'test_*.py' -v
python3 tools/r74_vocabulary_audit.py --repo . --output /tmp/r83-vocabulary.json
```

Then compile the three new diagnostic probe files with the actual compiler, distinguish compile-time vs runtime failures, capture exit/stdout/stderr and timeout separately, and add goldens only after source-driven independent review. Verify that the complete audit's tracked/scanned/excluded counts match the current checkout and triage every active spelling hit. None of these commands were executed by ChatGPT in this session.

**Boundary:** zero accepted compiler changes, zero diagnostic-pack mutations, zero golden rewrites, zero CI dispatch, zero user elevation/download/network outside connected GitHub, zero automatic monitoring, zero PR merges. All substantial source additions are isolated in **draft PR #50**; only handoff/evidence artifacts were committed to `main`. Do not represent the narrow 52-file scan as the full-repository audit or the 20 golden-fragment matches as accepted native label tests.

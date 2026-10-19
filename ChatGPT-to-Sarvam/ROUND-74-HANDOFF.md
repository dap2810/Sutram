# Sutram Round 74 — ChatGPT → Sarvam
Date: 2026-10-19. Incoming: Sarvam-to-ChatGPT/ROUND-74.md.
Main snapshot inspected: 04aa7bb31f44062458f82440ef2e686e6dfe2dbc (v176).
Review: [Draft PR #37](https://github.com/dap2810/Sutram/pull/37) on review/r74-reproducibility-audit-20261019 (four code/test files).
Round 73 draft [PR #36](https://github.com/dap2810/Sutram/pull/36) remains separately open; do not blindly reapply older compiler patches.

## Exactly what was completed
1. **WS1 source-integrity PASS:** all **14/14** current R69 lock Git blobs matched live v176 main Git tree (expanded from old 12). Added two-independent-clean-local-clone canonical compiler reproducibility harness, with explicit dirty-tree and output-mismatch refusal. Synthetic harness regression **3/3 PASS**. **Actual NASM/compiler build, binary SHA-256, execution and proof gates NOT_RUN.**
2. **WS2 NOT_RUN:** reviewed R73 deferred staging status; no unsafe reclamation integration or manufactured memory measurements.
3. **WS3 NOT_RUN:** module emitter/linker not implemented; old textual yoj still not separate compilation.
4. **WS4 scanner implemented:** read-only tracked-source stale keyword candidate inventory, escaped-\\n false-negative guard, and prose/compatibility false-positive classification strategy; synthetic regressions **7/7 PASS**. Actual complete-checkout repository sweep NOT_RUN. Examined compiler, GUI, and language reference examples without rewriting intentionally retained names.

**Total actually executed unit tests:** 10/10 PASS (with mocked build and synthetic vocabulary fixtures, not native compiler tests). Exact source hashes and observed commands in ROUND-74-SHA256.txt and ROUND-74-OBSERVED.txt.

## Files delivered
- Main handoffs: ROUND-74-WS1-BASELINE.md, ROUND-74-WS2-KOSH.md, ROUND-74-WS3-MODULES.md, ROUND-74-WS4-VOCABULARY.md, ROUND-74-OBSERVED.txt, ROUND-74-SHA256.txt, this ROUND-74-HANDOFF.md.
- Draft review branch, unaccepted source: tools/r74_repro_build.py, tools/r74_vocabulary_audit.py, tests/r74/test_repro_build.py, tests/r74/test_vocab_audit.py.

## Sarvam commands on a complete clean checkout of the PR #37 branch
1. `python3 -m unittest discover -s tests/r74 -p 'test_*.py' -v`
2. `python3 tools/r74_repro_build.py --repo . --report /tmp/r74-repro.json`
3. `python3 tools/r74_vocabulary_audit.py --repo . --output /tmp/r74-vocab.json`
4. Run the supported `tools/gates.sh` invocation per that script, record real PASS/FAIL/NOT_RUN and exact compiler binary hashes.
5. Adjudicate all vocabulary candidates using `docs/sutram-vocabulary.html` and actual accepted compiler spellings. Look out for intentionally retained migration strings, GUI/CLI backward-compatible names and multi-line comment scan false positives.
6. Separately carry forward R73 draft PR #36 kosh work with live native A/B mapping measurements and actual two-source module emission, without touching Claude's Windows work.

## Environment limitation and honesty boundary
The local container has Python, Git, and GNU ld, but not NASM. Outbound git clone to github.com could not resolve DNS. Source was accessed through the connected GitHub interface, and uploads were read back. Therefore no actual production compiler was assembled or run, and no binary SHA-256 can be supplied. No changes were made to accepted golden files, compiler, library, Windows source, or current source locks. No CI job was initiated. **Keep review PR #37 draft pending Sarvam's native acceptance and do not merge automatically.**

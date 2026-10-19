# Round 74 WS4 — repository-wide Sanskrit keyword audit

**Status: scanner implemented and unit-tested; full current checkout run NOT_RUN.**

A read-only scanner, `tools/r74_vocabulary_audit.py`, is in [draft PR #37](https://github.com/dap2810/Sutram/pull/37). It enumerates tracked files, reviews active `.sm` / `.smlib` tokens without comments or strings, checks code snippets in Markdown/HTML and quoted literals in source, and provides path/line/context for manual triage. It excludes historical multi-agent handoff directories, accepted .out/.exit goldens and non-source binaries. It does **not** rewrite words or decide automatically whether compatibility diagnostics should be retired.

Synthetic fixture tests: **7/7 PASS**, including detection after a literal escaped newline (`\n`) and suppression of ordinary English prose containing `to`. All 10 Round 74 tool tests PASS.

Live source examination (not full sweep):
- `src/sutram_compiler.asm` blob `185b7f06ad01b5b80f123b694b0025034698bd35`: old words `pratiyati` / `ayojan` / `punaravartana` appear in internal symbol names and the intentional migration diagnostics. Active string values `kw_pratiyati = "prati"`, `kw_ayojan = "yoj"`, `kw_punaravartana = "chakra"` were inspected; do not mechanically replace the old internal labels.
- `windows/gui/sutram_gui.asm` blob `0c590c3ef5ab3916a45195a4277beba1cbf5c0f6`: active GUI builtins list contains older English-looking names such as `likha_fmt` and `char_from`; those also exist as literal builtin names in current compiler, so changing only GUI tokens would introduce a mismatch.
- `docs/LANGUAGE-REFERENCE.md` blob `fd70bc594b88597d702645ce99ca11d1f56ac376` still lists old-looking builtin names and CLI `--lang`; source also still includes `--lang` and those builtin strings. Treat as API/vocabulary consistency review rather than confirmed defect.

**NOT_RUN:** full production-tree scanner against actual v176 checkout, semantic adjudication of all candidates, full regression. A local Git checkout was unavailable. This must not be called an exhaustive completed audit.

Sarvam:
`python3 tools/r74_vocabulary_audit.py --repo . --output /tmp/r74-vocab.json`
Review every JSON candidate by category. Check `docs/sutram-vocabulary.html` for authority, and compiler accepted symbols for truth. Do not treat all string/prose matches as bugs. Scanner's block-comment state resets per line (possible false positives in multi-line block comments); this is explicitly a known classification limitation for review.

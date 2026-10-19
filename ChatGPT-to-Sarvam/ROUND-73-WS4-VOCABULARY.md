# Round 73 — WS4 obsolete-keyword audit handoff (2026-10-19)

Review: [PR #36](https://github.com/dap2810/Sutram/pull/36). Exact line findings: [R73-OLD-KEYWORD-AUDIT.md](https://github.com/dap2810/Sutram/blob/review/r73-repin-and-lexical-audit-20261019/docs/R73-OLD-KEYWORD-AUDIT.md).

**Actual source scan PASS:** scanned all **22,808 lines** of `src/sutram_compiler.asm` against 11 obsolete keyword spellings. Only old quoted tokens in NASM source/data were lines 293–303: the deliberate old-vocabulary diagnostic table. `pankti` on line 304 refers to error line numbering, not the obsolete array type. Inspected five raw keyword compare sites and offset/length assumptions for `yoj`, `niryat`, `tak`, `prakriya`, Devanagari `प्रक्रिया`, and `sutra`. Found stale comments and arity annotations, not proof of a misparsed active keyword.

**NOT_RUN:** repository-wide exhaustive sweep of every tracked source/document/example and all other hardcoded numeric constants. This audit intentionally does not modify migration hints or frozen golden files. Sarvam should run `rg` against vocabulary on a clean checkout, classify active parser paths separately from historical lessons, and test any edits.

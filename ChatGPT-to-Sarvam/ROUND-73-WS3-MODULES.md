# Round 73 — WS3 separate compilation handoff (2026-10-19)

Review: [PR #36](https://github.com/dap2810/Sutram/pull/36). Current compiler integration design: [R73-SEPARATE-COMPILATION.md](https://github.com/dap2810/Sutram/blob/review/r73-repin-and-lexical-audit-20261019/docs/R73-SEPARATE-COMPILATION.md).

**Source analysis PASS:** documented exact current functions: `graph_preflight_v1` line 2263; `expand_imports` 2513; `mg_parse_niryat` 3562; `r56_patch_global_storage` 21078. Proposed versioned SUO1 object/interface layout, explicit public/private symbol visibility, native relocation/linking and deterministic failure rules.

**NOT IMPLEMENTED:** production .sm object emitter, independent module unit compile, native linker integration, or real two-.sm-module executable. Earlier R71 42-exit fixture was handcrafted machine code, not this acceptance. Sarvam must approve object ABI and perform staged compiler changes; no speculative time estimate.

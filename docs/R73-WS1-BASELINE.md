# ROUND-73 / WS1 — source-lock baseline, distinct from native acceptance

Checked 2026-10-19, **main input** `c504e3c652f13b7352d0579e9a2445d0e3621bc8` (v173). Canonical assembly entry: `src/r68_compiler_entry.asm` (`42389aaf73179726d91e23359aee2199734036e1`). Existing release lock: `tools/r69_build.lock.json` (`ce40ecf0782894599044dc4bc632d67edc688e2f`).

## Previously blocked four files: reviewed current disposition

| Old pin in R72 | Main v173 pin | Reason present in reviewed lock/history |
|---|---|---|
| Compiler `ea2a1e910952120c1f1db8bac1890338af68d3e9` | `4b137114d5b67aab0df61e356aad9af94056ae1b` | R4 undefined-name error after earlier R3 diagnostic change. Not merely a freshness update; semantics changed, so accepted main source gets a new identity. |
| `win/rtblob.inc` old `3cdc4f7916e08930a79e8c277539620ac46264f4` | `f855c01ed63d673c41ac0ca9bde2d99cb5654f99` | v171 Windows runtime merge, reviewed and recorded in the R4 lock note. |
| `win/winrt.inc` old `d296c62fd5afd4b820778677865a83d86b1ab613` | `9e73bd45cf0b1f2fbd0f86452d8e9fcaf5fb8b37` | Same accepted Windows runtime/layout change. |
| `win/winrt_blob.asm` old `d556399d94cd922906a2249604a6943968fbed9d` | `69a4618028e9c6ac16af4b3a389854962227b69c` | Same accepted Windows runtime/layout change. |

The lock additionally lists new `win/pe_layout.inc` and `win/pe_imports.inc`. **All 14/14 currently pinned blobs matched the actual v173 main files by GitHub readback.** The lock's documented R3/R4 audit trail is explicit; do not erase or replace it with a bare updated hash.

## Actual execution and boundary

**PASS — 14/14 GitHub source-blob identity comparisons.** This is a remote source audit, not a native compiler build. The inherited R72 local Python tests were also rerun on Linux and passed **3/3**.

**NOT_RUN — clean-checkout NASM assembly/link, actual binary SHA-256, repeat binary parity, full regression/codegen/packs/proofs/layers.** NASM is unavailable in this session's Linux container; direct GitHub access from its filesystem is DNS-blocked. The new feature branch intentionally changes `src/sutram_compiler.asm`; the *accepted release lock is not silently repinned to unaccepted feature code*. Run release Gate 1 on the pinned main checkout, and R73 experimental tests on a separate PR worktree.

Suggested independent command on a clean v173 checkout:

```sh
python3 tools/r69_build.py --check-only
python3 tools/r69_build.py --target linux --output ./sutram-r73-main --report ./r73-main-build.json
sh tools/gates.sh
```

Record toolchain versions, compiler ELF binary SHA-256, stdout/stderr/return codes, and PASS/FAIL/SKIP/NO-EXPECTATION/NOT_RUN separately. Run a second clean build in a different fresh checkout before claiming bit-for-bit reproducibility. The script `tools/gates.sh` exists on main; previous Sarvam numbers are **not** independently rerun numbers here.

**Decision:** the four source pins belong in the provenance lock and were legitimately updated for accepted changes. Gate 1 **source identity** is unblocked on main; Gate 1 **full binary/reproducibility acceptance** is not yet demonstrated by this round.

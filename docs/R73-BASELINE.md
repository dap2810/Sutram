# R73 WS1 — review of accepted source provenance and reproducible-build limit

Source snapshot: main `5efb592f46a7862d573f55b3a95439a35e0c9ad5`, 2026-10-19.
Supported compiler entry: `src/r68_compiler_entry.asm`, blob `42389aaf73179726d91e23359aee2199734036e1`.
This branch updates only four inputs in `tools/r69_build.lock.json`; the core `tools/r69_build.py` already uses `COMPILER_BLOB=4b137114d5b67aab0df61e356aad9af94056ae1b` from accepted Claude R04.

| Changed pin | Earlier stored blob | Current blob | Provenance / why changed |
|---|---|---|---|
| src/sutram_compiler.asm | ea2a1e910952120c1f1db8bac1890338af68d3e9 | 4b137114d5b67aab0df61e356aad9af94056ae1b | Accepted compiler fixes, culminating in Claude R04 undefined-name diagnostics, commit 169dbb78d993213a23d5478180f4677e69607a26 |
| win/rtblob.inc | 3cdc4f7916e08930a79e8c277539620ac46264f4 | f855c01ed63d673c41ac0ca9bde2d99cb5654f99 | Generated embedded Windows runtime changed in ROUND-03 Windows integration, commit 539632fb6ea87c864c11b80710ca7d2499c41459 |
| win/winrt.inc | d296c62fd5afd4b820778677865a83d86b1ab613 | 9e73bd45cf0b1f2fbd0f86452d8e9fcaf5fb8b37 | Windows OS shim changed in ROUND-03 Windows integration, commit 58c97e7576f39b7b52c7f4d3401308b4f7a641b7 |
| win/winrt_blob.asm | d556399d94cd922906a2249604a6943968fbed9d | 69a4618028e9c6ac16af4b3a389854962227b69c | Native PE runtime changed in ROUND-03 Windows integration, commit 58847d1e5b747bc78356ac40f6a1dc44336c6a07 |

All 12 input blobs checked independently against current GitHub main returned **12/12 MATCH** on this proposed lock, eight unchanged and four updated. The historical lock's old blobs remain in the Git history; this is a *new versioned release candidate*, not a proof of binary provenance.

**No NASM available in local environment** and no clean checkout materialized here: build binary hash, reproducibility-by-two-builds, suite/codegen/packs/proof/layers all **NOT_RUN**. No fabricated compiler binary SHA-256. Sarvam must build/execute them and independently accept the four upstream changes before merging.

Commands in a clean reviewed branch checkout:
```sh
python3 tools/r69_build.py --check-only
python3 tools/r69_build.py --target linux --output /tmp/sutram-r73-first --report /tmp/sutram-r73-first.json
python3 tools/r69_build.py --target linux --output /tmp/sutram-r73-second --report /tmp/sutram-r73-second.json
sha256sum /tmp/sutram-r73-first /tmp/sutram-r73-second
SUTRAM_COMPILER=/tmp/sutram-r73-first sh tools/gates.sh
```
Run `tools/gates.sh` using its documented invocation and record discrete PASS/FAIL/SKIP/NO-EXPECTATION/NOT_RUN; the displayed invocation is a reviewer starting point, not an executed run. **Do not change the old golden outputs to pass a new build.**

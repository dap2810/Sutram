# Round 72 — source-locked baseline findings (2026-10-19)

API snapshot main: `d7d2c73a478b9fb057a6b05982745716ad279e19`.
Only supported compiler entry: `src/r68_compiler_entry.asm`, blob `42389aaf73179726d91e23359aee2199734036e1`.

**Gate 1 is NOT accepted.** Current `main` differs from `tools/r69_build.lock.json` in four pin locations:

| File | Current Git blob | Existing lock |
|---|---|---|
| `src/sutram_compiler.asm` | `f4fefe6ca438bf2f76f68e6742bb71e8a836ccb6` | `ea2a1e910952120c1f1db8bac1890338af68d3e9` |
| `win/rtblob.inc` | `f855c01ed63d673c41ac0ca9bde2d99cb5654f99` | `3cdc4f7916e08930a79e8c277539620ac46264f4` |
| `win/winrt.inc` | `9e73bd45cf0b1f2fbd0f86452d8e9fcaf5fb8b37` | `d296c62fd5afd4b820778677865a83d86b1ab613` |
| `win/winrt_blob.asm` | `69a4618028e9c6ac16af4b3a389854962227b69c` | `d556399d94cd922906a2249604a6943968fbed9d` |

Eight other exact include pins agree. The four differences MUST be reviewed, not automatically re-pinned to hide an integration defect. They may arise from concurrent accepted source changes.

`tools/r72_baseline.py` verifies a pinned commit, clean checkout, regular unsymlinked source files and exact blobs, then assembles canonical ELF64 with an installed NASM/ld, printing SHA-256 of the actual binary. Reviewer uses it externally against a clean checkout of the pinned snapshot and `tests/r72/main-source-manifest.json`. Neither script nor test suite installs tools, changes runtime settings, writes goldens or launches CI. Three local Python unit tests passed on Linux; no NASM binary was available, so production build, bit-for-bit binary comparison and accepted suites are NOT_RUN.

Remaining workstreams:
- WS2: `kosh` reclamation is staged in R71 PR #30 but not rebased/integrated on fully Sanskrit-renamed `main`. Explicit alias invalidation contract, integer/float native A/B, retained mappings and Windows policy still open. NOT_RUN.
- WS3: R71 linker primitives are not full two-unit `.sm` separate compilation. Object emitter, niryat visibility, missing/private/duplicate diagnostics remain NOT IMPLEMENTED.
- WS4: Actual Windows console UTF-8, compiler and GUI execution NOT_RUN. Requires genuine Windows standard-user host; do not confuse PE structure with execution.
- WS5: Three previously broken raw-length comparison families are known (module expander, range parser, module graph parser). An exhaustive line-by-line audit of the newer 545KB compiler was NOT_RUN; no guarantee that remaining constants are correct.

No compiler/library/golden/installer/GUI/workflow/credential changes. This is a verified PARTIAL, not a successful release.

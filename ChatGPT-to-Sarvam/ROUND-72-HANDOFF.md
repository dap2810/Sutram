# Round 72 — ChatGPT → Sarvam (verified partial)

Date: 2026-10-19. Incoming: `Sarvam-to-ChatGPT/ROUND-72.md`. Review: [draft PR #34](https://github.com/dap2810/Sutram/pull/34). Baseline API commit `d7d2c73a478b9fb057a6b05982745716ad279e19`; PR source commit `7dd3aaf74f76f6de5a553e3f8b561b1d4527ef63`.

## Status by gate

| Gate | Actual work | Verified limitation |
|---|---|---|
| WS1 reproducible baseline | Added exact-source manifest, clean-checkout Git blob/commit guard, controlled NASM/ld ELF builder, source mismatch report. 12 includes inspected: 8 match R69 lock, **4 do not**. Three Python unit tests PASS, syntax PASS. | Baseline currently **BLOCKED** by four mismatching lock pins. No clean compiler build or binary SHA-256 was run. |
| WS2 `kosh` reclamation | R71 patch reviewed as staged historical input, not silently applied to Sanskrit-renamed compiler. | Native integration, live mapping barrier measurements, alias contract and Windows separate policy **NOT_RUN**. |
| WS3 separate compilation | Reviewed prior R71 linker groundwork. | Actual 2-module `.sm` object emission/link **NOT IMPLEMENTED**. |
| WS4 Windows | Native Windows acceptance requirements itemized. | No real Windows execution or Unicode console/GUI evidence: **NOT_RUN**. |
| WS5 old keyword assumptions | Known three affected families recorded. | Exhaustive current-main line audit **NOT_RUN**. |

The four changed Git blobs are compiler: `ea2a1e910952120c1f1db8bac1890338af68d3e9` → `f4fefe6ca438bf2f76f68e6742bb71e8a836ccb6`, win/rtblob.inc: `3cdc4f7916e08930a79e8c277539620ac46264f4` → `f855c01ed63d673c41ac0ca9bde2d99cb5654f99`, win/winrt.inc: `d296c62fd5afd4b820778677865a83d86b1ab613` → `9e73bd45cf0b1f2fbd0f86452d8e9fcaf5fb8b37`, win/winrt_blob.asm: `d556399d94cd922906a2249604a6943968fbed9d` → `69a4618028e9c6ac16af4b3a389854962227b69c`. This is a real FAIL for the *old lock against current main*, not proof of faulty compiler output. Do not automatically repin without accepting concurrent changes.

**Commands actually executed locally:** `python -m unittest discover -s /mnt/data/r72_delivery/tests/r72 -v` → 3 PASS/0 FAIL; `python -m py_compile` two Python files → exit 0. NASM is absent in the execution environment. No CI, Windows or full compiler regression run was triggered. `source_binary_sha256`: **NOT_AVAILABLE**.

**Reviewer:** inspect PR #34 and `docs/R72-BASELINE-OBSERVED.md`; read `sarvam/INSTRUCTIONS-FOR-SARVAM.md`. Verify modified source and Windows include files before repinning, run clean worktree with the manifest and checker, build canonical `src/r68_compiler_entry.asm`, and execute all gates. Do not merge until independently accepted. No `lib/*.smlib`, accepted goldens, production compiler or workflow changed. Output blob of production core remains `f4fefe6ca438bf2f76f68e6742bb71e8a836ccb6` on baseline branch; new tool source hash is available from PR, no generated native executable.

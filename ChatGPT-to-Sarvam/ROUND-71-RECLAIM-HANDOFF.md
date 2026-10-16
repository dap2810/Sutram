# Round 71 revised assignment — kosh reclamation returned to Sarvam

Date: **2026-10-16**. Incoming `ROUND-71.md` blob:
`38b607afa51f479fa6d12abbfbac740b04000e76`.
Source follow-up: `b08c74630d3f7aa460acceb5eb6864a9a4fd822a`.
Parent R71 delivery: `bb7910611055edc11302cc3bc58206cef7afd3d6`.
Review: [draft PR #30](https://github.com/dap2810/Sutram/pull/30), still on the R69 branch.

**13 additive source/test/document files are uploaded and verified.** PR #30 now
has 43 changed files relative to R69, preserving the original 30. This is a
staged source implementation, NOT a fully built/integrated compiler release.

## Revised workstream 2

The incoming brief explicitly withdraws its earlier skipped-R69 claim and says
R69 was accepted/synced. It replaces the canonical-build workstream with the
compiler's kosh growth leak. This follow-up addresses that replacement instead
of creating an invented Round 72 or repeating the old build-path task.

The NASM helper and pinned preparation tool add three hooks to the existing
`.ge_call_koshpush` path: check capacity before size arithmetic, reject allocation
failure before memory writes, and emit `munmap` of the old mapping after successful
copy and pointer publication. Runtime registers and stack depth needed for append
are preserved. The no-growth branch skips the new payloads.

The new profile is Linux-ELF-only. It deliberately rejects kosh-push PE emission
because the inspected Windows runtime has no release implementation. It does not
pretend syscall 11 releases a VirtualAlloc buffer. Windows VirtualFree integration
and regeneration/execution of embedded runtime blobs remain open.

**Growth invalidates old backing-store aliases.** That compatibility boundary
requires review; there is no borrow checker enforcing it. Final live buffers,
clear/pop/dequeue cleanup, general allocations and scope destructors are not
fixed by this change. No general free primitive was silently added. The source
document recommends a separately reviewed typed-disposal/owned-resource contract.
This does not make Sutram memory-safe.

## What actually ran

- **44 passing local tests, uid 1000:** 19 native payload methods, 18 source-
  preparation methods, seven acceptance-tool methods.
- Native payloads used a narrow GNU-as syntax bridge and C test driver, with real
  Linux mmap/munmap/mincore calls, not mocked unmapping.
- Recorded probe: 16 growths, 16 old mappings released, **527 successful old-page
  unmapping checks**, live values retained; exit 0, empty stderr. This is an
  isolated runtime-sequence result, NOT a compiled Sutram leak measurement.
- Three Python files passed syntax checks.
- All 13 local source-file Git identities reproduced uploaded tree
  `6b5d9e81aa6ed702722f99dbcb4640c3209aa41c` exactly (48273 bytes).

Read `ROUND-71-RECLAIM-OBSERVED.txt`, `ROUND-71-RECLAIM-TESTS.txt`,
`ROUND-71-RECLAIM-PROBE.json`, and `ROUND-71-RECLAIM-SHA256.txt` alongside this file.
The prior 66 R71 tests were not rerun and are not added to this total.

## Input/output identities and integration

Required original compiler: `64ea028a5ccf56117c132a7efd0673cbe2df3fc6`.
Canonical entry: `42389aaf73179726d91e23359aee2199734036e1`.
New helper: `e9a6f5d02f2b4c98343de6f85c3442ab8890d59a`.

The checked-in core remains unchanged. **Full production staging was not run**:
the complete 545722-byte core was not available locally; direct retrieval failed
DNS and NASM is absent. No staged-core or executable hash is invented. Preparation
checks all 13 inputs and writes the real output core hash into its stage report
when Sarvam runs it. Source-preparation unit tests use a marked synthetic scaffold.

In a complete PR #30 checkout:

```sh
python3 -m unittest discover -s tests/r71_reclaim -p 'test_*.py' -v
python3 tools/r71_reclaim_prepare.py --stage /tmp/sutram-r71-reclaim
cd /tmp/sutram-r71-reclaim
nasm -f elf64 -I. src/r68_compiler_entry.asm -o reclaim.o
ld -o reclaim-compiler reclaim.o
nasm -DSUTRAM_R71_KEEP_OLD_KOSH=1 -f elf64 -I. src/r68_compiler_entry.asm -o legacy.o
ld -o legacy-compiler legacy.o
```

Return to the complete review checkout and execute:

```sh
python3 tools/r71_reclaim_acceptance.py \
  --compiler /tmp/sutram-r71-reclaim/reclaim-compiler \
  --legacy /tmp/sutram-r71-reclaim/legacy-compiler \
  --report /tmp/r71-reclaim-native.json
```

Read `docs/R71-KOSH-RECLAMATION.md` first. The acceptance command requires exact
integer/float output, an unaffected byte-identical control, two-barrier process
VmSize measurements against the legacy compiler, and PE rejection/no output.
Those .sm expectations are pending, not newly observed native results. Afterwards
run the full accepted regression/packs/codegen/proofs, other R65 configurations
and alias review. Integrate only after acceptance and update source locks as a
reviewed change, never by weakening pin checks. Do not rewrite accepted goldens.

## All five current workstreams — no silent completion claims

| Workstream | Current status / remaining verification |
|---|---|
| WS1 real modules | Original linker primitives retained. Production .sm objects/module driver/niryat linkage remain not implemented. |
| WS2 kosh leak | Staged Linux emission implemented; isolated unmapping tested. Full compiler integration, native .sm A/B, alias compatibility and Windows reclamation remain unverified/open. |
| WS3 memory boundary | Original experimental asurakshit source retained. Full frontend/profile verification still pending; no safety guarantee. |
| WS4 boot path | Original BIOS source retained. Image not booted, not Sutram-generated; no demonstrated kernel. |
| WS5 semantics | Original two evidenced clauses/probes retained. New full-compiler specification probes remain pending. |

The old combined handoff remains the historical original delivery record; this
addendum governs the revised WS2. No core, lib/*.smlib, existing golden, GUI,
installer, workflow, security-setting or credential change was merged into main.
No automatic CI, background watch, new product networking or elevated test ran.

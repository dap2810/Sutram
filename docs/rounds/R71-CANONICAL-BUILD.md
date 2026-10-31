# Round 71 with returned Round 69 — canonical build and document migration

## Base and decision

This supplement applies on the returned R69 source commit
`cdc1bd32c8b8455d4ad3b7df906a2714a6f3354b` (draft PR #29). That branch, not main,
contains the 21 R69 source/test/document changes and the corrected installer
wrappers. The branch is still unmerged as of this review.

The ordinary release entry remains **`src/r68_compiler_entry.asm`**. R69's Linux
and Windows builders select it explicitly. It includes the original compiler
and the accepted UTF-8/abbreviation diagnostics. The original core file remains
an implementation input, not the recommended standalone release build command.
No new compiler backend or runtime dependency is introduced.

The R71 entry is an **explicit experimental profile** for the raw-operation
boundary. It retains those same R68 diagnostics. It is not silently substituted
into the installer. Default/core byte parity still needs the actual native
compiler builds; the source-level wrapper relationship is not that proof.

## Complete the previously unapplied current-document migration

The returned R69 supplied a patch generator but did not apply its full repository
sweep. R71 adds a reviewed-plan/apply path over **current tracked documents**,
including shell backslash and PowerShell backtick command continuations.
It verifies the exact R69 migration-tool blob, records every scanned document,
rejects inventory/content drift, checks the patch with git and applies it only
when explicitly requested.

```sh
python3 tools/r71_migrate_build_docs.py --plan /tmp/r71-doc-plan.json
# Review the plan's changed paths and replacement text.
python3 tools/r71_migrate_build_docs.py --apply-plan /tmp/r71-doc-plan.json
python3 tools/r71_migrate_build_docs.py --check
```

Historical handoffs, CHANGELOG and per-round reports remain snapshot evidence,
not current release instructions. Untracked documents and non-UTF-8 documents are outside this tracked UTF-8
sweep and must be reviewed separately. The plan is documentation-only; it does
not build the compiler or certify the installer. Concurrent changes must be
reconciled; no multi-file transactional editing guarantee is claimed.

**This full production-repository sweep has not been run/applied here.** The local
unit tests applied real patches only to a temporary git fixture. Do not report
all project guides as already migrated before the three commands above succeed.

## Native build and profile acceptance

Using a full checkout of R69 with this additive patch:

```sh
python3 tools/r69_build.py --check-only
python3 tools/r69_build.py --output /tmp/sutram-r69 --report /tmp/r69-build.json
python3 tools/r71_prepare_review.py --output /tmp/r71-entry.asm
nasm -DSUTRAM_R71_UNSAFE_BOUNDARY=1 -f elf64 -I. /tmp/r71-entry.asm -o /tmp/r71-boundary.o
ld -o /tmp/r71-boundary /tmp/r71-boundary.o
python3 tools/r71_native_acceptance.py --compiler /tmp/sutram-r69 --boundary-compiler /tmp/r71-boundary --report /tmp/r71-native.json
```

Use fresh paths. Re-run the accepted R68 diagnostics, R70 negatives, codegen,
packs, library proofs and frozen baselines against the actual intended default
compiler. R70's accepted Sanskrit banner correction must be preserved. Existing
R65 modes and the R69 pair A/B runner remain additional acceptance gates.

Required inherited core blob: `64ea028a5ccf56117c132a7efd0673cbe2df3fc6`.
Required canonical entry blob: `42389aaf73179726d91e23359aee2199734036e1`.
Produced R71 entry blob: `6ba05e206556d9b18349b633ac1bda73ac89aab1` (902 bytes).
The core is not rewritten; there is no new expanded-core or compiler-binary hash.

## Windows

Use R69's real corrected `windows/build-windows-setup.ps1` only after review.
Its source gates, per-user install contract and no-bypass policy remain intact.
No Windows compiler/GUI/installer execution, registry changes or open/close
acceptance occurred in this session. No setup executable is produced here.

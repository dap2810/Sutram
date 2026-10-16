# Round 69 — returned to Sarvam

Date: 2026-10-16. Explicit owner request to revisit ROUND-69, then work on ROUND-71.
Source: `cdc1bd32c8b8455d4ad3b7df906a2714a6f3354b`.
Base: `11f41d3fcc8377dbcc1453f36a47a6122e3b1954`.
Review: [draft PR #29](https://github.com/dap2810/Sutram/pull/29).
Branch: `feature/r69-canonical-build-return-20261016`.

**21 changed source/test/doc files delivered. Not a native-accepted release.**
All 21 local Git blob IDs reproduced uploaded tree
`9ef30f475bafb20cb75e62235bb78c8b4bf2df52` exactly after correcting one README
copy mismatch before publication. No branch merge or automatic CI was performed.
This return preserves newer R70 work and does not modify `lib/*.smlib` or goldens.

## One line per workstream

| Workstream | Delivered | Could not verify / remaining |
|---|---|---|
| WS1 canonical build | README + locked Linux/Windows build tools select `src/r68_compiler_entry.asm`; wrong/missing/unlocked/symlink input fails. Five modes and output reports. | Complete NASM build and production include-closure check NOT RUN. Whole-repository document migration is supplied as a drift-checked patch generator but NOT executed/applied. Do not claim all guides are already migrated. |
| WS2 pair probe | Three explicit independent compiler files, all 15 non-RSP registers, default/reference exact bytes and unchanged controls. Derives expected 46 bytes; writes measured delta only after actual compilation/execution. | Full Sutram A/B NOT RUN. Fixture validation explicitly reports measured delta null. No timing/speed claim. |
| WS3 Indic remainder | `docs/INDIC-COVERAGE.md` names all 11 packs; Malayalam-native numerals are explicitly deferred under the brief's allowed named-gap option. Existing Malayalam keywords with ASCII digits remain. | Malayalam native digits not implemented. No invented sign or silent claim that every script is complete. |
| WS4 installer wrapper | The actual setup/native PS1 files and CMD launcher are replaced in the branch: canonical compiler, GUI rebuild, actual native-installer path, payload hashes, bounded tests, no policy-bypass arguments. | No PowerShell/Windows build, GUI or installer execution. Native installer's own source/payload/least-privilege gates are preserved, but require independent review. Timeout cannot certify descendant-process cleanup. |

## Input and output

Core input AND unchanged source output:
`64ea028a5ccf56117c132a7efd0673cbe2df3fc6` (545722 bytes).
Canonical entry input AND unchanged output:
`42389aaf73179726d91e23359aee2199734036e1` (713 bytes).
`tools/r69_build.lock.json` locks those and the conditional include files.
No new compiler executable was produced here. Source hashes are not a runtime certificate.

## Reviewer commands

In a complete checkout, first review the changed wrappers and sources:

```sh
python3 -m unittest discover -s tests/r69 -p 'test_*.py' -v
python3 tools/r69_pair_probe.py --validate-fixtures
python3 tools/r69_build.py --check-only
python3 tools/r69_build.py --output ./sutram-r69 --report ./r69-build.json
python3 tools/r69_build.py --mode pairs --output ./sutram-r69-pairs --report ./r69-pairs-build.json
python3 tools/r69_pair_probe.py --compiler ./sutram-r69 --reference /path/to/independent-accepted-R68 --pair-compiler ./sutram-r69-pairs --report ./r69-pair-measurements.json
python3 tools/r69_build_doc_migration.py --patch /tmp/r69-build-docs.patch
```

Review and apply the documentation-only patch; it refuses unexpected changed documents
that still contain a bare-core build command. Preserve concurrent edits. Then run its
`--check` mode. Historical round snapshots/CHANGELOG are intentionally excluded.
Run R68 diagnostics/examples, R70 negatives, accepted suite/codegen/packs/proofs
against the actual selected compiler. Do not auto-record or rewrite expectations.

On genuine non-elevated Windows PowerShell 5.1:

```powershell
.\windows\build-windows-setup.ps1
```

The new canonical source lock replaces the obsolete package-layout preflight path;
it does not erase, waive or relabel the old integrity manifest. The native installer
builder retains its existing least-privilege/payload checks. Inspect staged compiler
copies in both bin/ and win/, GUI hash, native stderr/stdout, install/cancel/uninstall,
Unicode console and GUI open/close before accepting a release. Existing output
replacement requires an explicit switch. Do not elevate or bypass security policy.

## Actual evidence

39 Python unit methods PASS; final local rerun 0.008 s. Build subprocess results
in unit tests are mocked. Four Python files passed syntax checks. Fixture validator
returned FIXTURES_VALID, compiler_executed false, native_status NOT_RUN,
expected_removed_bytes 46, measured_removed_bytes null. None of these numbers
are a new native compiler measurement. Full raw local test log and all 21 source
files are in the companion source supplement.

Round 71 is a separate follow-on review. Keep this PR draft until native acceptance;
do not silently treat an uploaded branch as integration on main.

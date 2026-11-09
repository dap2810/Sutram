# Windows v309 fixes — implemented and verified

**The two outstanding v309 issues are fixed in [draft PR #68](https://github.com/dap2810/Sutram/pull/68), and the rebuilt candidate is installed on the owner's machine.** Linux/Windows payload files and manifests now match; late interrupted recovery reuses all 657 files with zero staging copies. User edits are preserved. The observer no longer fails while clicking the error dialog; the final screenshot captures the actual completed wizard.

The owner's standing request is **fix and verify issues before handing off**, rather than stop at a diagnostic report. [Exact request](OWNER-INSTRUCTIONS.md). Product changes are on `codex/windows-v309-fixes`; these reports do not merge or grant release acceptance.

| Check | Verified result |
| --- | --- |
| Native Windows vs native Linux packaging | **657/657 payload files plus manifest byte-identical** |
| Three fresh Windows checkout samples | All match the payload; no CRLF |
| Existing checkout with CRLF | Staging normalizes bytes without rewriting the checkout |
| Initial upgrade | Finish **21.81 s**, engine 0; **656 reused, 1 staged** |
| Early interruption | Stopped **0.371 s** after Install, 0 files; retry Finish **26.51 s**, engine 0 |
| Late interruption | 657 files present, pending record still present; retry Finish **22.30 s**, engine 0; **657 reused, 0 staged** |
| Edited-file retry | Explicit refusal, engine 1; edited bytes preserved; no observer exception |
| Staging/publication regression fixture | **14/14**, including edits/removal after a reuse check |
| Existing installer gates | **R130 16/16; R134 24/24** |
| Installed compiler bundle | Both `bin` and `win` compile `yoj ganit` from an unrelated directory and print **81** |
| Final installation | **657/657 hashes**, exact candidate manifest and uninstaller, canonical v309 PATH |
| Final native capture | Full successful Finish page; closes after Finish |
| Processes / lock | **18/18 owned processes closed**, no installer lock, pending file or transaction |

## Provenance

Built product source: `4536cc36a083a64a0382cfff14a78a298a5bae1b`. Review head with expanded regression tests: `5da6318f002875929a2b684d14523fd0f29b7f21`.

| Artifact | SHA-256 |
| --- | --- |
| Candidate setup | `9dfe6b5ea185a6915918bb1d76abff474cec7d0d2c34d8a82d76e8850e00886f` |
| Embedded install engine | `c8a18505d40d5182d661acc165753eabed31d04efa0742f8ac4fc17a8a47690c` |
| Payload manifest (both platforms) | `0523ff8050787c529777727998aaffd3d1c144e2fd8ed31100c0e220b559d096` |
| Unchanged compiler | `05b23d56d40aaa4b71c6d67d13996d75da6e4d2e2b2ac47fbf4960a1a52fb481` |

The candidate is retained at `<repo>\build\windows-v309-fixes\build\native-v309-fix\Sutram-Setup.exe`. Generated setup binaries/pins remain local; the PR contains source and tests. No compiler/runtime, library, examples, frozen expectations or workflow triggers were edited. No full CI was launched.

## What changed

1. Root LF rules cover documentation/fixture text; explicit overrides keep frozen tests and Windows evidence as bytes. Both builders normalize the declared UTF-8 extensions in staging, then hash them. Binary payloads are unchanged. Ordinal UTF-16 ordering fixes the punctuation-order discrepancy found during real Windows/Linux comparison.
2. Staging checks matching installed files before creating copies. Publication still verifies each target; if a previously reused file changes or disappears, it refuses before moving a file without a staged replacement. Fourteen native fixture checks exercise the actual engine functions/publication loop.
3. The Windows builder locates import libraries beside its linker, fixing the failure of this relocated MinGW installation.
4. Test button clicks use asynchronous messages so destruction of a dialog does not create a false synchronous-click failure. The screenshot helper captures only the foreground owned window with DPI-aware coordinates. The original partial D2 PrintWindow image is retained; the corrected confirmation image shows the full page.

## Native timings and copy counts

| Phase | Result | Seconds | Engine exit | Already installed | Staging copies |
| --- | --- | ---: | ---: | ---: | ---: |
| initial | FINISH | 21.81 | 0 | 656 | 1 |
| d1-stop | INTERRUPTED | 0.37 | -1 | 0 | 0 |
| d1-retry | FINISH | 26.51 | 0 | 0 | 657 |
| d2-stop | INTERRUPTED | 25.40 | -1 | 0 | 657 |
| d2-retry | FINISH | 22.30 | 0 | 657 | 0 |
| d3-stop | INTERRUPTED | 17.49 | -1 | 0 | 657 |
| final-upgrade | FINISH | 21.43 | 0 | 657 | 0 |
| capture-confirmation | FINISH | 22.15 | 0 | 657 | 0 |

These single-run timings are observations, not a speedup claim. The fixed late retry (22.30 s) did not beat the earlier unmodified v309 observation (21.25 s), despite avoiding all 657 transaction-stage copies. Extraction, integrity checks, ownership checks and finalisation still run.

## Evidence and boundaries

- [Payload comparison](PAYLOAD.md), [every compared entry](payload-comparison.json), [exact package checks](candidate.json).
- [Recovery and preservation](RECOVERY.md), [full final screenshot](capture-confirmation-finish.png), [all native phase results](summary.json).
- [14 regression checks](reuse-fixture-final.txt), [R130](r130.txt), [R134](r134.txt), [installed bundle execution](installed-smoke.json).
- [Final identity](handoff-identity.json), [process closure](final-processes.json), [commands and retained initial failures](COMMANDS.md).

The unchanged compiler's earlier 7 arithmetic checks, 32 OOM cases and 322 native suite passes remain [dated v309 evidence](../win-v309-2026-11-07/RESULTS.md), not newly rerun claims. This repair tested the changed installer/build paths and the actually installed bundle. No new IDE, Linux runtime, whole-ZIP/setup byte-reproducibility, universal security-product compatibility or release acceptance is claimed. Source pins/release artefacts require Sarvam's normal independent rebuild/review before promotion.

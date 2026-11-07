"""Summarise completed native probes without rerunning or modifying installation."""
from pathlib import Path
import json,re,hashlib
HERE=Path(__file__).resolve().parent
def read(n):return json.loads((HERE/n).read_text(encoding='utf-8-sig'))
def write(n,s):(HERE/n).write_text(s.rstrip()+'\n',encoding='utf8',newline='\n')
candidate=read('candidate.json');comparison=read('payload-comparison.json')
phases=['initial','d1-stop','d1-retry','d2-stop','d2-retry','d3-stop','d3-retry','final-upgrade','capture-confirmation']
runs={n:read(n+'.json') for n in phases};stats={}
for n,r in runs.items():
    path=HERE/(n+'-engine.log');log=path.read_text(encoding='utf-8-sig') if path.exists() else ''
    stats[n]=dict(status=r['status'],seconds=r.get('finish_seconds',r.get('seconds')),engine_exit=r['child_exit'],files=r['payload_files_present'],reused=log.count('Already installed '),copied=len(re.findall(r'\] START \d+/',log)),wizard_exited=r['wizard_exited'])
identity=read('handoff-identity.json');processes=read('final-processes.json');edit=read('d3-edit-result.json');restore=read('restore-after-d3.json')
assert comparison['all_entries_equal'] and comparison['payload_files']==657
assert identity['pass'] and identity['candidate_matches'] and processes['all_owned_processes_closed'] and not processes['installer_lock_exists']
assert len(processes['processes'])==18 and all(r['wizard_exited'] for r in runs.values())
assert runs['d1-stop']['seconds']<1 and runs['d1-stop']['payload_files_present']==0
assert runs['d2-stop']['payload_files_present']==657 and runs['d2-stop']['pending_exists']
assert stats['d2-retry']['copied']==0 and stats['d2-retry']['reused']==657
assert all(stats[n]['status']=='FINISH' and stats[n]['engine_exit']==0 for n in ['initial','d1-retry','d2-retry','final-upgrade','capture-confirmation'])
assert edit['edit_preserved'] and edit['child_exit']==1 and edit['retry_status']=='ERROR_DIALOG'
assert all('observer_error' not in r for r in runs.values())
preserved=Path(restore['preserved'])/'docs/BUILDING.md'
assert hashlib.sha256(preserved.read_bytes()).hexdigest()==edit['edited_sha256'].lower()
write('summary.json',json.dumps(dict(candidate={k:v for k,v in candidate.items() if k!='checks'},runs=stats,payload_equal=True,edited_file_preserved=True,owned_processes_closed=18),indent=2))

table='\n'.join(f"| {n} | {s['status']} | {s['seconds']:.2f} | {s['engine_exit']} | {s['reused']} | {s['copied']} |" for n,s in stats.items() if s['seconds'] is not None)
write('RESULTS.md',f'''# Windows v309 fixes — implemented and verified

**The two outstanding v309 issues are fixed in [draft PR #68](https://github.com/dap2810/Sutram/pull/68), and the rebuilt candidate is installed on the owner's machine.** Linux/Windows payload files and manifests now match; late interrupted recovery reuses all 657 files with zero staging copies. User edits are preserved. The observer no longer fails while clicking the error dialog; the final screenshot captures the actual completed wizard.

The owner's standing request is **fix and verify issues before handing off**, rather than stop at a diagnostic report. [Exact request](OWNER-INSTRUCTIONS.md). Product changes are on `codex/windows-v309-fixes`; these reports do not merge or grant release acceptance.

| Check | Verified result |
| --- | --- |
| Native Windows vs native Linux packaging | **657/657 payload files plus manifest byte-identical** |
| Three fresh Windows checkout samples | All match the payload; no CRLF |
| Existing checkout with CRLF | Staging normalizes bytes without rewriting the checkout |
| Initial upgrade | Finish **21.81 s**, engine 0; **656 reused, 1 staged** |
| Early interruption | Stopped **{runs['d1-stop']['seconds']:.3f} s** after Install, 0 files; retry Finish **26.51 s**, engine 0 |
| Late interruption | 657 files present, pending record still present; retry Finish **22.30 s**, engine 0; **657 reused, 0 staged** |
| Edited-file retry | Explicit refusal, engine 1; edited bytes preserved; no observer exception |
| Staging/publication regression fixture | **14/14**, including edits/removal after a reuse check |
| Existing installer gates | **R130 16/16; R134 24/24** |
| Installed compiler bundle | Both `bin` and `win` compile `yoj ganit` from an unrelated directory and print **81** |
| Final installation | **657/657 hashes**, exact candidate manifest and uninstaller, canonical v309 PATH |
| Final native capture | Full successful Finish page; closes after Finish |
| Processes / lock | **18/18 owned processes closed**, no installer lock, pending file or transaction |

## Provenance

Built product source: `{candidate['source_commit']}`. Review head with expanded regression tests: `5da6318f002875929a2b684d14523fd0f29b7f21`.

| Artifact | SHA-256 |
| --- | --- |
| Candidate setup | `{candidate['setup_sha256']}` |
| Embedded install engine | `{candidate['engine_sha256']}` |
| Payload manifest (both platforms) | `{candidate['manifest_sha256']}` |
| Unchanged compiler | `{candidate['compiler_sha256']}` |

The candidate is retained at `E:\\Github_Projects\\Sutram\\build\\windows-v309-fixes\\build\\native-v309-fix\\Sutram-Setup.exe`. Generated setup binaries/pins remain local; the PR contains source and tests. No compiler/runtime, library, examples, frozen expectations or workflow triggers were edited. No full CI was launched.

## What changed

1. Root LF rules cover documentation/fixture text; explicit overrides keep frozen tests and Windows evidence as bytes. Both builders normalize the declared UTF-8 extensions in staging, then hash them. Binary payloads are unchanged. Ordinal UTF-16 ordering fixes the punctuation-order discrepancy found during real Windows/Linux comparison.
2. Staging checks matching installed files before creating copies. Publication still verifies each target; if a previously reused file changes or disappears, it refuses before moving a file without a staged replacement. Fourteen native fixture checks exercise the actual engine functions/publication loop.
3. The Windows builder locates import libraries beside its linker, fixing the failure of this relocated MinGW installation.
4. Test button clicks use asynchronous messages so destruction of a dialog does not create a false synchronous-click failure. The screenshot helper captures only the foreground owned window with DPI-aware coordinates. The original partial D2 PrintWindow image is retained; the corrected confirmation image shows the full page.

## Native timings and copy counts

| Phase | Result | Seconds | Engine exit | Already installed | Staging copies |
| --- | --- | ---: | ---: | ---: | ---: |
{table}

These single-run timings are observations, not a speedup claim. The fixed late retry (22.30 s) did not beat the earlier unmodified v309 observation (21.25 s), despite avoiding all 657 transaction-stage copies. Extraction, integrity checks, ownership checks and finalisation still run.

## Evidence and boundaries

- [Payload comparison](PAYLOAD.md), [every compared entry](payload-comparison.json), [exact package checks](candidate.json).
- [Recovery and preservation](RECOVERY.md), [full final screenshot](capture-confirmation-finish.png), [all native phase results](summary.json).
- [14 regression checks](reuse-fixture-final.txt), [R130](r130.txt), [R134](r134.txt), [installed bundle execution](installed-smoke.json).
- [Final identity](handoff-identity.json), [process closure](final-processes.json), [commands and retained initial failures](COMMANDS.md).

The unchanged compiler's earlier 7 arithmetic checks, 32 OOM cases and 322 native suite passes remain [dated v309 evidence](../win-v309-2026-11-07/RESULTS.md), not newly rerun claims. This repair tested the changed installer/build paths and the actually installed bundle. No new IDE, Linux runtime, whole-ZIP/setup byte-reproducibility, universal security-product compatibility or release acceptance is claimed. Source pins/release artefacts require Sarvam's normal independent rebuild/review before promotion.
''')

samples='\n'.join(f"| `{s['file']}` | `{s['payload_sha256']}` | MATCH | False |" for s in comparison['samples'])
write('PAYLOAD.md',f'''# Payload determinism fixed

Native Windows PowerShell built the candidate; native Ubuntu/WSL Python built the Linux payload from the same product source `{candidate['source_commit']}`. All **657 payload entries and the manifest** match byte for byte. [Complete comparison](payload-comparison.json).

| Fresh checkout sample | Windows checkout = Linux checkout = payload SHA-256 | Result | Windows CRLF? |
| --- | --- | --- | --- |
{samples}

The fresh Windows sample checkout is `build/windows-v309-fixes-fresh` at `8321f843` (the LF rule commit); the later product commits alter manifest ordering/linker lookup and INSTALLER-REBUILD.md, not these samples. The Linux payload and native Windows package use final product source `4536cc36`. The original Windows worktree still contained CRLF in the two Markdown samples; its package nevertheless matches because normalization occurs in staging. The checkout is not rewritten by packaging.

Manifest SHA-256: `{candidate['manifest_sha256']}`. Compiler, linker, GUI and icon payloads remain byte-identical to the original inputs. Invalid UTF-8 in a declared text file is refused; binaries are not decoded or normalized.

The first comparison established equal file contents but found different manifest ordering around underscores. It is retained in [the initial comparison](payload-comparison-before-order-fix.json). Both builders now sort ordinal UTF-16 paths and use identical CRLF manifest separators. The final comparison passed after rebuilding both.

`payload-native-commands.txt` records the **old/stale worktree's** certutil/CRLF checks, so its True result is expected. The fresh-checkout samples above are the evidence for the attribute fix. Complete ZIP/setup bytes are not claimed reproducible: metadata/compression/linkers differ. No security-product causal claim follows from equal file hashes.
''')

write('RECOVERY.md',f'''# Native recovery after the fix

The real rebuilt wizard/engine were used, without changing security settings. Initial upgrade, early-stop retry, late-stop retry and two same-folder confirmations reached Finish with engine exit 0. Only captured test wizard/child handles were stopped; all 18 processes are closed.

**Early stop:** after {runs['d1-stop']['seconds']:.3f} s, engine age {runs['d1-stop']['engine_age_seconds']:.3f} s, before any payload file or pending transaction. Retry finishes in 26.51 s. There is no previous-attempt notice because no state had yet been written. [Stop](d1-stop.json), [retry](d1-retry.json), [log](d1-retry-engine.log).

**Late stop:** after {runs['d2-stop']['seconds']:.2f} s, all 657 payload files exist and the pending record remains. Retry logs **657 Already installed**, **0 START/DONE staging copies**, then completes in 22.30 s. It still extracts/verifies the incoming package and rechecks ownership. [Stop](d2-stop.json), [journal](d2-stop-journal.txt), [retry](d2-retry.json), [log](d2-retry-engine.log). This catches the last-file/pending-record boundary, not a torn journal write.

**Owner edit:** interrupted with 57 published files, appended `\\nV309 OWNER-EDIT RECOVERY PROBE: preserve this line.\\n` to BUILDING.md, and retried. The engine exits 1 before replacing it, naming the file and giving recovery instructions in the [log](d3-retry-engine.log). The [dialog](d3-retry-error.png) gives a generic failure/log notice. Edited SHA-256 before and after: `{edit['edited_sha256'].lower()}`. [Recorded edit check](d3-edit-result.json).

The edited tree and transaction remain intact at:

```text
{restore['preserved']}
{restore['preserved_transaction']}
```

The known-good candidate backup was restored and verified ([inventory](restore-after-d3.json)). Final installed manifest/uninstaller exactly match the candidate, not merely a compiler with the same v309 version. [Final identity](handoff-identity.json).

## Observer fixes and honest visual evidence

Next/Install/Finish/error-OK clicks are posted asynchronously; waiting for a closing dialog to return a synchronous message no longer raises the previous observer error. D3 has `ERROR_DIALOG`, engine 1, no `observer_error`, and cleanup closes the wizard. The historical JSON field `dialog_closed` actually measures whether the **wizard process** exited during the five-second post-click wait; False there does not describe the dialog's visibility. The wizard subsequently exits on the cleanup close message.

PrintWindow still produced a partial client-area capture in [D2's retained image](d2-retry-finish.png), despite visible Finish controls and a completed engine. The helper was changed to capture the actual foreground owned window rectangle with DPI-aware coordinates. An initial confirmation ran before that edit was applied (a local optional image-library import failed); its successful install remains [recorded separately](final-upgrade.json). No dependency was installed. The corrected helper then captured [the full completed wizard](capture-confirmation-finish.png), and that confirmation finished in {runs['capture-confirmation']['finish_seconds']:.2f} s with 657 reused targets and 0 staging copies. The previous helper is archived as [ui-helper-before-capture-fix.ps1](ui-helper-before-capture-fix.ps1).

No unattended PowerShell/setup processes or pending installation state remain. No 15-minute timeout, general security-product behavior or IDE acceptance is inferred from these finite successful runs.
''')
print(json.dumps(stats,indent=2))

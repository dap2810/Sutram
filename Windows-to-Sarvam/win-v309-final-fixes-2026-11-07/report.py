from pathlib import Path
import json,re

out=Path(__file__).resolve().parent
read=lambda name:json.loads((out/name).read_text(encoding='utf-8-sig'))
candidate=read('candidate.json');identity=read('handoff-identity.json');processes=read('final-processes.json')
ide=read('ide.json');payload=read('payload-comparison.json');edit=read('d3-edit-result.json')
phases=[]
for name in ['initial','d1-stop','d1-retry','d2-stop','d2-retry','d3-stop','d3-retry','final-upgrade']:
    row=read(name+'.json');log=out/(name+'-engine.log');text=log.read_text(encoding='utf-8-sig') if log.exists() else ''
    phases.append(dict(name=name,status=row['status'],seconds=row.get('finish_seconds',row.get('engine_age_seconds',row.get('observed_seconds'))),
                       engine_exit=row.get('child_exit'),files=row['payload_files_present'],
                       reused=text.count('Already installed '),copies=len(re.findall(r'\] START ',text)),capture_warnings=row.get('capture_warnings',[])))
assert all(read(name+'.json')['status']=='FINISH' for name in ['initial','d1-retry','d2-retry','final-upgrade'])
late=next(r for r in phases if r['name']=='d2-retry')
assert late['reused']==657 and late['copies']==0
assert edit['edit_preserved'] and edit['child_exit']==1 and edit['retry_status']=='ERROR_DIALOG'
assert identity['pass'] and processes['all_owned_processes_closed'] and not processes['installer_lock_exists']
assert all(ide[k] for k in ['c1_pass','c2_pass','c3_pass','originals_unchanged','process_exited'])
assert payload['all_entries_equal'] and all(r['pass'] for r in read('global-after.json')) and all(r['pass'] for r in read('global-linux.json'))
summary=dict(candidate={k:v for k,v in candidate.items() if k!='checks'},phases=phases,
             owned_process_count=len(processes['processes']),all_owned_processes_closed=True,installed_identity_pass=True,
             native_cases={s:sum(r['status']==s for r in read('native-cases.json')) for s in sorted({r['status'] for r in read('native-cases.json')})},
             arithmetic=read('arithmetic/results.json')['summary'],oom=read('oom/results.json')['summary'],
             global_before_failed=sum(not r['pass'] for r in read('global-before-expanded.json')),global_after_passed=42,
             ide_pass=True,edit_preserved=True,payloads_equal=True)
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
table='\n'.join(f"| {r['name']} | {r['status']} | {r['seconds']:.2f} | {r['engine_exit']} | {r['files']} | {r['reused']} | {r['copies']} |" for r in phases)
results=f'''# Final v309 repair: implemented, installed and verified

Source/product commit **{candidate['source_commit']}**, [draft PR #68](https://github.com/dap2810/Sutram/pull/68). This final candidate supersedes the earlier same-day packaging-only candidate. Independent Sarvam acceptance is pending. This evidence does not promote release binaries or frozen source pins.

## Fixes

- LF text policy and normalization during packaging; Windows/Linux ordinal manifest ordering; adjacent Windows linker import libraries.
- Recovery reuses an installed file after checking its incoming hash. Publication refuses a changed or missing reused target before moving the only copy. Existing ownership/reparse checks remain.
- The concurrent R208 global-initializer finding was reproduced: **21 of 42 expanded cases failed before**. Global initializers now receive expression validation and the global ownership check. Global/local analysis contexts are separated. The validator uses a separate traversal stack and refuses budget exhaustion. See [entry-point audit](ENTRY-PATHS.md).
- The installer now acquires its destination lock before registry/discovery, old-state and pending reads. A real two-process fixture exercises refusal while held and fresh ownership reads after the prior owner updates state and releases it.

## Final package verification

| Check | Result |
| --- | --- |
| Global/local regression cases | 42/42 native Windows and 42/42 native Linux |
| Existing R137 slice gate | 59/59 on each platform |
| Existing R134 ownership predicate | 21/21 on each platform |
| Forced analysis exhaustion | Local and global refuse; production source unchanged |
| Native Windows example suite | 322 PASS; 3 without expectations; 6 deliberate skips; no failures |
| Requested arithmetic probes | 7/7, including original add/XOR and valid length |
| Requested native Job Object limits | 32/32; exact 32-byte stderr, LF, exit 1; no stack-overflow status |
| Existing installer gates | R130 16/16; R134 28/28, including four actual ownership reads |
| Native file/lock fixtures | 14/14 staging/publication; 7/7 lock/snapshot checks |
| Windows/Linux payload | 657 entries plus manifest byte-identical; same reviewed PE input |
| Installed CLI | Both bin/win layouts compile an imported library from unrelated cwd and print 81 |
| Native IDE | Hello Run, refused-load Save protection, global compiler refusal pass; original files unchanged |
| Final installed identity | Canonical PATH/v309; 657/657 hashes; exact candidate manifest/uninstaller |
| Final owned processes | {summary['owned_process_count']}/{summary['owned_process_count']} closed; no installer lock or pending transaction |

Native Linux means Ubuntu under WSL, with a freshly assembled ELF host from the canonical NASM entry. Its three compiler gates execute real Linux outputs. The Linux package comparison uses payload-only mode and the identical newly built Windows PE input; no Linux-linked setup or Wine install is claimed. Full ZIP/executable reproducibility is not claimed.

## Native installation/recovery

| Phase | Result | Seconds | Engine | Files present | Reused | Staging copies |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
{table}

Early retry and final upgrade complete normally. D2 stops after all files are published while pending metadata remains; it is **not a torn-journal-write test**. D3 stops after 56 published files, then deliberately edits docs/BUILDING.md: retry refuses and preserves the exact edited SHA-256 `{edit['edited_sha256'].lower()}`. The edited tree/transaction remain preserved at the paths in [restore-after-d3.json](restore-after-d3.json). The verified working installation is restored and the final upgrade succeeds. Timings vary and are not a performance claim.

The first recovery attempt's early retry actually reached Finish, engine 0, but the screenshot helper rejected a lost-foreground capture and marked OBSERVER_ERROR. Its raw records and controller error are retained in [recovery-attempt1](recovery-attempt1/). The helper now retries foreground acquisition and records skipped captures without aborting installation observation. The complete rerun passes. `dialog_closed` is a legacy misnamed field recording wizard exit during the five-second acknowledgement wait; the error dialog's dismissal is not inferred from that field.

The final process observer initially treated JSON arrays as process records (PowerShell's null-property enumeration); this caused a PID-0/null-start-time error both inside and outside the sandbox. The observer now accepts only individual records with explicit pid/start fields. Both errors are retained. A mistyped R130 command and initial temporary-directory sandbox restrictions are also disclosed in [commands](COMMANDS.md). No product failure is hidden by these observer corrections.

## Identity and limits

- Setup: `{candidate['setup_sha256']}`
- Compiler: `{candidate['compiler_sha256']}`
- Engine: `{candidate['engine_sha256']}`
- Manifest: `{candidate['manifest_sha256']}`
- Local setup: `<repo>\\build\\windows-v309-fixes\\build\\native-v309-final-fix\\Sutram-Setup.exe`

This is the working installed candidate, with original/working/interrupted/edited trees preserved. New source remains in PR #68; main carries handoff/evidence only. Native IDE checks above are specific exercised scenarios, not every IDE or uninstall acceptance gate. No uninstall, arbitrary concurrent-write proof, 15-minute timeout, full Linux example suite, general security-product compatibility, or universal language safety is claimed. No security settings, frozen baselines, workflow files or automatic CI triggers were changed. Release source pins intentionally still describe upstream v309 and must be updated only after independent review/rebuild.

Read [commands and provenance](COMMANDS.md), [all summary values](summary.json), [successful wizard](initial-finish.png), [IDE refusal screenshot](C3-global-refusal.png), [payload comparison](payload-comparison.json), and [final process evidence](final-processes.json).
'''
(out/'RESULTS.md').write_text(results,encoding='utf8',newline='\n')
commands='''# Commands and provenance

All Windows commands below ran from `<repo>\\build\\windows-v309-fixes` on 7 November 2026. Source edits were committed as 664ff188; generated executables stay local. The process-local linker preference was `C:\\Program Files\\mingw64\\bin` prepended to PATH. The ordinary native build scripts and the canonical NASM entry were used; the frozen source-pinned release build was not re-pinned.

```powershell
python tests/r137/test_global_initializers.py --compiler win/sutram.exe --report Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/global-before-expanded.json
& windows/build-windows-native.ps1
Copy-Item win/sutram.exe sutram.exe -Force
python tests/r137/test_global_initializers.py --compiler win/sutram.exe --report Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/global-after.json
python tests/r137/test_slice_number.py --compiler win/sutram.exe
python tests/r134/test_one_predicate.py --compiler win/sutram.exe
python tests/r137/test_analysis_limit.py --nasm nasm --linker 'C:\\Program Files\\mingw64\\bin\\ld.exe' --report Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/analysis-limit.json
$env:SUTRAM_EVIDENCE=Join-Path $PWD 'Windows-to-Sarvam\\win-v309-final-fixes-2026-11-07'
python tools/test_windows_native.py
& tests/windows/test_installer_lock.ps1
& tests/windows/test_installer_reuse.ps1
& windows/native-installer/build-installer.ps1
python tests/r130/test_installer_engine.py
python tests/r134/test_install_transaction.py
python Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/pin-fix-package.py
```

The original host's first narrower run was 38 cases/19 failures; expanded baseline was 42/21. Baseline tests precede the native rebuild. Commands, source programs, compiler diagnostics, absence/presence of output, and positive native runs are recorded in `global-*.json`. `analysis-limit.json` records the disposable forced-budget build's argv. `native-cases.json` records all suite argv. Build logs are original PowerShell UTF-16 output.

`prepare.py` copies prior proven native harnesses to this round with new backup/setup paths and pins, and copies the actual lock fixture evidence. `prepare-ide.py` derives the isolated IDE test. Subsequent observer corrections are in the final scripts; `recovery-attempt1` retains the earlier scripts. Do not regenerate these scripts over archived executed versions.

```powershell
& Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/initial-install.ps1
python Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/probes.py arithmetic
python Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/probes.py oom
& Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/recovery-tests.ps1
# First attempt was preserved; corrected observer; complete controller repeated once.
& Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/recovery-tests.ps1
& Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/ide.ps1
& Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/run-install.ps1 -Name final-upgrade
python Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/installed-smoke.py
& Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/verify-saved.ps1
```

The recovery controller copies/verifies the known-good install, vacates only guarded canonical paths, stops only its own captured process handles, preserves edited trees, and restores the working backup. Every actual engine command is in the phase JSON. No broad process termination, recursive deletion of user installations, security-policy change or security-suspended-thread resume occurred. GUI windows are visible only for these requested UI tests; helper processes use hidden windows. Final process verification matches PID and start time, including the failed attempt.

```powershell
wsl -d Ubuntu -- git -C /mnt<repo>/build/windows-v309-linux-checkout fetch /mnt<repo> codex/windows-v309-fixes
wsl -d Ubuntu -- git -C /mnt<repo>/build/windows-v309-linux-checkout checkout --detach 664ff188
wsl -d Ubuntu --cd /mnt<repo>/build/windows-v309-linux-checkout python3 /mnt<repo>/build/windows-v309-fixes/Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/linux-check.py
python Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/compare-payloads.py
```

`linux-check.json` contains every nested NASM/linker/build/test argv and full output. The same PE compiler input is copied into the Linux checkout for payload parity. Windows LF sample checkout remains at 8321f843; the three sampled source files are unchanged at final 664ff188. Existing stale CRLF worktree files are normalized only in staging; fresh checkout samples are LF. All 657 files and the manifest are compared, including compiler/linker/GUI/icon bytes.

Observed harness/environment errors: initial Python temporary-directory access was denied by the sandbox and approved reruns succeeded; the initial static-gate filename was mistakenly `test_installer_identity.py` (retained as `r130-command-error.txt`), then the actual `test_installer_engine.py` passed 16/16. The first process-check error was initially suspected to be sandbox access; the same error outside the sandbox established the actual JSON-array/PID-0 observer defect. Logs retain the original filenames and errors. The screenshot guard failure is described in RESULTS and its archived raw record. These are separate from product test results.

No full CI was launched. No automatic workflow was added. Release acceptance and artifact/source-pin promotion remain with Sarvam after independent review.
'''
(out/'COMMANDS.md').write_text(commands,encoding='utf8',newline='\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['candidate','phases']},indent=2))

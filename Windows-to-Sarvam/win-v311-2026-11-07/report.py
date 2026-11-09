from pathlib import Path
import json,collections,re
HERE=Path(__file__).resolve().parent
def read(p):return json.loads((HERE/p).read_text(encoding='utf-8-sig'))
def write(p,s):(HERE/p).write_text(s,encoding='utf8',newline='\n')
c=read('candidate.json');ex=read('expressions/results.json');cases={r['name']:r for r in ex['cases']};n=read('nesting/results.json');sup=read('supplemental/results.json')
identity=read('handoff-identity.json');process=read('final-processes.json');initial=read('initial.json');suite=collections.Counter(r['status'] for r in read('native-cases.json'))
c1=read('ownership/c1-suffix-result.json');c2=read('ownership/c2-result.json');c3=read('ownership/c3-result.json');c4=read('ownership/c4-unequal-existing-result.json');ordinary=read('ownership/ordinary-result.json')
fixtures=read('fixtures/commands.json');counts={r['name']:len(re.findall(r'^PASS ',r['stdout'],re.M)) for r in fixtures}
counts['reuse']=len(re.findall(r'"[^"\n]+":\s*true',next(r['stdout'] for r in fixtures if r['name']=='reuse')))
assert counts=={'boundaries':19,'reuse':14,'lock':7}
assert identity['pass'] and process['all_owned_processes_closed'] and not process['installer_lock_exists']
assert all(r['pass'] for r in ex['cases']) and all(r['pass_'] for r in sup[:2])
assert suite['PASS']==322 and not any(suite[k] for k in ['FAIL','COMPILE_FAIL','TIMEOUT'])
assert c1['owned_copies_after'] and c2['pass_'] and c3['edit_survived'] and ordinary['exit']==0
assert c4['engine_exit']==1 and c4['target_after_sha256']==c4['owned_sha256'] and c4['owned_copies_after']==['target/docs/BUILDING.md']
assert all(r['exit']==0 for r in fixtures)
c4log=(HERE/'ownership/c4-unequal-existing-engine.log').read_text(encoding='utf8');assert 'copy already kept under its name differs' in c4log and 'Nothing was deleted' in c4log
wrong=read('ownership/c4-unequal-existing-fixture.json')['superseded_before_sha256'];assert wrong==c4['superseded_after_sha256']
lines=[line for line in c4log.splitlines() if 'Not removed' in line or 'ERROR:' in line]
text='# v311 initializer verification\n\nAll requested snippets were compiled anew against the pinned v311 compiler. Full argv, outputs and source hashes are in [expressions/results.json](expressions/results.json).\n\n'
for name in ['global-direct','global-add','valid-global','two-globals-no-main','record-literal','default-argument','two-globals-with-main']:
    r=cases[name];text+=f"## {name}\n\nExit {r['compile']['exit']}; executable produced: {r['output_file_exists']}.\n\n```text\n{r['compile']['stdout']}{r['compile']['stderr']}```\n\n"
    if 'run' in r:text+=f"Native run: exit {r['run']['exit']}; stdout `{r['run']['stdout'].strip()}`.\n\n"
text+='''The two-global snippet fails at end-of-file because it lacks `mukhya`. The same globals with main compile and print 3. This is not proof that globals are syntactically absent or that the expression class is closed; global initialization is the known checked path. The supplied default-argument example fails at `vitti`, whereas the additional `f(n = 5)` example fails at `=`. See [supplemental results](supplemental/results.json).

Direct local kosh binding remains a valid positive control and prints 7; local kosh arithmetic refuses. v311's scorer incorporates the disclosed v310 harness corrections: valid local binding expects 7 and slice arithmetic accepts the precise E_VIBHAG_ANKA diagnostic. All 12 primary expression observations meet their scoped expectations. This is not a formal class-wide safety proof.
''';write('INITIALIZER.md',text)
assert len(n['cases'])==1024 and n['boundary']['depth']==1023 and n['boundary']['status']=='REFUSED' and n['last_compiled_run']['stdout']=='1\n'
write('BUDGET.md',f'''# v311 nesting boundary

New native run: every integer depth 0 through 1023, adding one balanced parenthesis pair per probe inside `likha(...)`. Depths 0–1022 compile. Depth 1023 refuses, exit 1, no executable, empty stderr:

```text
{n['boundary']['compile']['stdout']}```

The depth-1022 binary exits 0 and prints 1. No crash or timeout in 1024 compiler invocations (15-second per-process deadline). This verifies the parser nesting boundary, not exhaustion of the analysis walk's node budget. No budget-exhaustion experiment was performed, as directed by the owner's brief.

[All source files and raw outputs](nesting/results.json); [last compiled](nesting/depth-1022.sm); [first refused](nesting/depth-1023.sm).
''')
write('ARITHMETIC.md','''# v311 arithmetic verification

New native executions of both the brief's add/XOR wrappers and the original preserved reproductions exit 1 with no executable. Exact refusal:

```text
'''+sup[0]['compile']['stdout']+'''```

The valid length control compiles and prints 2, exit 0. [Brief cases/control](expressions/results.json); [original sources and argv](supplemental/results.json). No v309/v310 pass count is reused.
''')
disappeared='\n'.join('- `'+r['file']+'`: '+r['sha256']+'; same bytes at '+', '.join(r['copies_after']) for r in ordinary['diff']['disappeared']) or '- None.'
manifest={r['file'].replace('\\','/'):r['expected'].lower() for r in c['checks']};after=read('ownership/c2-after.json')['target'];assert all(after[k]['sha256']==v for k,v in manifest.items())
write('OWNERSHIP.md',f'''# v311 ownership — independently verified repair

**The C4 unequal-backup defect reproduced on v310 now refuses safely on v311.** The test ran the complete unchanged engine and ZIP extracted from setup `{c['setup_sha256']}` at the canonical per-user installation. No product source was edited.

## C1 — suffix preservation

The actual setup GUI was interrupted after {read('c1-stop.json')['payload_files_present']}/657 target files. An ordinary clean interruption has no superseded file; absence is not a pass. A documented synthetic journal-owned intermediate and older backup were then seeded to exercise replacement. The engine preserved the exact intermediate bytes at `{c1['owned_copies_after'][0]}`, SHA-256 `{c1['owned_sha256']}`. A non-delete-sharing read handle on the later staged compiler deliberately stops its rename and keeps the transaction inspectable. C1 exit 1 is that controlled fixture boundary.

## C2 — simultaneous installer engines

Two complete embedded engine processes launched {c2['launch_gap_seconds']:.6f} seconds apart. Exits: {c2['exit_codes']}. Exactly one proceeds; the other refuses:

```text
{c2['lock_message'][0]}
{c2['completion'][0]}
```

All 657 payload hashes match afterward. No target pathname disappeared; only install log/journal/state metadata changed. This is actual engine concurrency, not two wizard windows. The separate lock fixture below tests delayed acquisition/fresh reads with stubbed registry/discovery functions.

## C3 — edit while publishing

A line appended to already-published `docs/BUILDING.md` survived with SHA-256 `{c3['after_sha256']}`. The observer recorded the engine running, the final compiler not yet published, and that compiler still staged. Installer exit 0. The edited installation was preserved, then a hash-verified baseline restored. [Exact edit and timing observations](ownership/c3-result.json).

## C4 — differing bytes at the expected prefix-name

Same construction as the v310 defect: target bytes declared owned by an interrupted journal; an older backup; the expected 12-hex-prefix filename precreated with unequal bytes. No hash collision is needed. v311 refuses before moving/deleting the target:

```text
{chr(10).join(lines)}
```

- Original target hash remains `{c4['owned_sha256']}` at `target/docs/BUILDING.md`.
- Unequal existing backup remains `{wrong}`.
- Engine exit 1; no preexisting target pathname disappeared and no preexisting target file changed bytes.
- The later staged-compiler lock was never reached in this case; the unequal-copy check refused earlier.

[Result](ownership/c4-unequal-existing-result.json), [fixture construction](ownership/c4-unequal-existing-fixture.json), [complete log](ownership/c4-unequal-existing-engine.log), [before/after inventories](ownership/c4-unequal-existing-before.json), [journal](ownership/c4-unequal-existing-after-journal.txt). This closes the reproduced stable unequal-copy case. It does not establish atomicity against an arbitrary writer between a successful equal-hash comparison and deletion: v311 still uses hash-then-delete in the equal-copy branch. Keep that source-level limitation open; moving to a unique backup avoids the deduplication deletion.

## Ordinary interrupted retry: every disappearance

A separate unmodified setup was interrupted after {read('ordinary-stop.json')['payload_files_present']}/657 files, then completed by retry (exit 0, observed {read('ownership/ordinary-retry.json')['seconds']:.3f} seconds). Before/after:

{disappeared}

No other target pathname disappeared; {len(ordinary['diff']['changed'])} existing target files changed bytes. Final 657/657 installed hashes match. Raw comparisons enumerate both lost pathnames and changed contents; pathname-only checks would have missed the v310 failure.

## Additional upstream native fixtures

The unchanged v311 tests ran in isolated workspace trees: **{counts.get('boundaries',0)} boundary assertions, {counts.get('reuse',0)} reuse assertions, {counts.get('lock',0)} lock assertions**, all successful. Boundary coverage includes 18 injected interruption points, 36 stopped-and-rerun upgrades with whole/torn records, absent/equal/unequal superseded copies, suffix preservation, and selected publication-edit windows. These execute AST-extracted actual engine code with deliberate injected boundaries; they are distinct from the full-engine canonical tests above. Lock tests use real child processes but stub registry/discovery reads. Fixture files and full stdout/stderr are under [fixtures](fixtures/commands.json).

Backups and edited/partial trees remain preserved at paths in backup/vacate/restore JSON. Final installation is v311, one fresh-shell compiler, no pending transaction/lock, and all 12 full-install wizard/engine processes closed. Fixture child processes also completed before their successful test exits. No full GUI uninstallation, IDE acceptance, arbitrary-writer safety, or release acceptance is implied.
''')
write('RESULTS.md',f'''# v311 repair verification — 7 November 2026

**Verified the upstream repair of the recovery defect found during v310 testing. v311 is installed and working; no release acceptance is claimed.** v311 arrived while the v310 evidence was being prepared. The owner's brief explicitly permits a later version. Both candidates have separate full native evidence; no product code/library/example/golden/installer changes were made by this verification round.

Source: `{c['source_commit']}`. Exact version: `Sutram 1.0 (v311) - sampurna sutra`.

| Artifact | SHA-256 |
|---|---|
| Setup | `{c['setup_sha256']}` |
| Compiler | `{c['compiler_sha256']}` |
| Embedded engine | `{c['engine_sha256']}` |
| Manifest | `{c['manifest_sha256']}` |

Embedded and installed payloads: 657/657 file hashes match; embedded compiler equals the tested repository compiler; exact engine source bytes occur inside the setup. Final uninstaller hash equals the setup. [Identity](handoff-identity.json), [package checks](candidate.json).

| Test | Expected | Actual | Pass? |
|---|---|---|---|
| A direct global kosh | Refuse | Exit 1, E_KOSH_DVARA, no executable | Yes |
| A global kosh + zero | Refuse | Exit 1, E_KOSH_GANIT, no executable | Yes |
| A1 scalar global | 7 | 7, exit 0 | Yes |
| A2 two globals without main | Syntax error | EOF error; with main prints 3 | Literal yes; class inference unsupported |
| A2 record literal | Syntax error | At colon | Yes |
| A2 default argument | Syntax error | At vitti; extra untyped probe fails at = | Yes |
| B nesting | No crash/hang | 0–1022 compile; 1023 clean refusal | Yes |
| C1 superseded suffix | Exact preservation | Matching full hash in suffixed backup | Yes, seeded fixture |
| C2 concurrency | One refuses, no corruption | Actual engines 1/0, 657 matching hashes | Yes |
| C3 live edit | Survives/reported | Exact edit survives | Yes |
| C4 unequal backup | No lost bytes | Refusal names differing copies; both preserved | **Yes: v310 reproduction fixed** |
| C4 ordinary retry | No lost file | Only pending pathname removed; bytes in final manifest | Yes |
| D identity | One canonical path/version | v311, registry 1.0.311, 657/657 hashes | Yes |
| D suite | 322+ PASS, no failure | 322 PASS, 0 FAIL/COMPILE_FAIL/TIMEOUT | Yes |
| E add/XOR | Refuse | Brief/original cases: E_VIBHAG_ANKA, exit 1 | Yes |
| E length | 2 | 2, exit 0 | Yes |

Native installer reached Finish in {initial['finish_seconds']:.3f} seconds, child exit 0, closed after Finish; [viewed screenshot](initial-finish.png). Suite separately records 3 NO_EXPECTATION and 6 skipped platform/side-effect cases. Additional native fixtures: {counts.get('boundaries',0)} boundary + {counts.get('reuse',0)} reuse + {counts.get('lock',0)} lock assertions, all pass. All 12 full-install test wizard/engine processes are closed; final lock/pending state absent. Original installations and test trees are preserved.

Detailed reports: [INITIALIZER](INITIALIZER.md), [BUDGET](BUDGET.md), [OWNERSHIP](OWNERSHIP.md), [ARITHMETIC](ARITHMETIC.md), [commands](COMMANDS.md). Every probe, raw result, source hash, inventory and relevant screenshot is retained. Evidence hashes are in EVIDENCE.sha256.

Remaining limits: full-hash-then-delete still has an arbitrary-writer race; this test closes the stable unequal-copy defect only. No new OOM claim (not rerun in this requested round), expression-budget exhaustion, gate-mutation validation, IDE/full uninstall acceptance, or cross-platform package reproducibility claim. Historical results keep their own artifact identities. Sarvam must acknowledge and independently review the exact candidate and remaining scope. No CI run was launched.
''')
write('COMMANDS.md','''# v311 commands

Pinned checkout: `<repo>\\build\\windows-v311-verification`, source fae5319d2abf6dc1368d683b1aa4b80a8831ab5d.

```powershell
# Original repository: isolated checkout and adaptation of the v310 observation helpers
git worktree add -b codex/windows-v311-2026-11-07 build/windows-v311-verification fae5319d
python build/prepare-v311.py
# From the new checkout
python Windows-to-Sarvam/win-v311-2026-11-07/pin-fix-package.py
win/sutram.exe --version
python Windows-to-Sarvam/win-v311-2026-11-07/compiler-probes.py expressions
python Windows-to-Sarvam/win-v311-2026-11-07/compiler-probes.py nesting
python Windows-to-Sarvam/win-v311-2026-11-07/supplemental.py
$env:SUTRAM_EVIDENCE=Join-Path (Get-Location) 'Windows-to-Sarvam/win-v311-2026-11-07'
python tools/test_windows_native.py
& Windows-to-Sarvam/win-v311-2026-11-07/full-native.ps1
python Windows-to-Sarvam/win-v311-2026-11-07/installer-fixtures.py
python Windows-to-Sarvam/win-v311-2026-11-07/report.py
```

Compiler/suite and isolated workspace fixtures ran independently alongside native installation. full-native.ps1 serially performs initial backup/upgrade, concurrent engines, edit-during-publication, seeded suffix/unequal-copy tests, unmodified interruption/retry, and final identity/process closure. Exact subprocess argv is in JSON reports; fixtures/commands.json includes the unchanged upstream test commands and complete outputs. All nested probe sources and inventories are retained.

No security changes, unowned process termination, source patch, baseline rewrite, installer rebuild or workflow launch. Canonical installation trees and transactions are hash-verified and preserved before tests. Background engines use hidden/no-window process creation; only the intended setup wizard is visible. Fixture's staged-compiler read handle prevents commit cleanup if reached; v311's unequal-copy check correctly stops earlier. 15-second compiler deadlines, 180-second engine deadlines and 240-second GUI observer bounds are used; no timeout fired. Fixture assertions have explicit scoped instrumentation; full engine tests use unchanged embedded source.

Fresh shell identity rebuilds registry Machine + User PATH and runs from an unrelated directory. Complete native logs, source probes and screenshots are separate from the v310 run. Use fresh output/backup locations for reproduction; duplicate/stale-artifact guards are intentional.
''')
print('v311 reports generated: reproduced C4 case now preserves both copies.')

from pathlib import Path
import json,hashlib,datetime,collections,shutil,os
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def read(n):return json.loads((HERE/n).read_text(encoding='utf-8-sig'))
def write(n,s):(HERE/n).write_text(s,encoding='utf8',newline='\n')
c=read('candidate.json');identity=read('reinstall-identity.json');suite=read('suite-timing.json');cases=read('native-cases.json');budget=read('budget.json')
before=read('before-uninstall-inventory.json');after=read('after-uninstall-inventory.json');state=read('after-uninstall-state.json')
obs=read('uninstall-observer.json');settings=read('settings-uninstall.json');final=read('final-check.json');lic=read('capture-retry-install.json')
assert identity['pass'] and identity['candidate_matches']
assert not any(x['same_process_alive'] for x in final['processes'])
assert obs['finished'] and all(p['exit']==0 for p in obs['process_results'])
assert not obs['samples'] and not obs['window_events'] and not obs['dialogs']
assert not any(state[x] for x in ['install_exists','menu_exists','desktop_exists'])
assert state['commands'][0]['exit']==1
assert all(state['registry'][x]['exit']==1 for x in ['extension','class','uninstall'])
assert state['user_path']==read('before-install-state.json')['user_path']
assert state['machine_path']==read('before-install-state.json')['machine_path']
counts=collections.Counter(x['status'] for x in cases)
assert counts['PASS']==322 and not any(counts[x] for x in ['FAIL','COMPILE_FAIL','TIMEOUT']) and suite['exit']==0
source=(ROOT/'LICENSE.txt').read_text(encoding='utf8')
licence_text=(HERE/'capture-retry-licence.txt').read_bytes().decode('utf8')
assert licence_text==source.replace('\n','\r\n')
assert all(x['pass'] for x in budget if x['name']!='literal-20000')
engine=next(x for x in obs['process_results'] if x['pid']==16088)
engine_seconds=(datetime.datetime.fromisoformat(engine['exit_time'])-datetime.datetime.fromisoformat(engine['started'])).total_seconds()
confirmed_seconds=(datetime.datetime.fromisoformat(engine['exit_time'])-datetime.datetime.fromisoformat(settings['confirmed'])).total_seconds()
newroots={p:rows for p,rows in after['roots'].items() if rows and not before['roots'].get(p)}
assert len(newroots)==1
elapsed=suite['elapsed_seconds'];delta=elapsed-18.6;pct=(elapsed/18.6-1)*100
write('.gitattributes','* -text\n')
write('LICENCE.md',f'''# v312 licence page — native Windows observation

The em dash, line breaks and Devanagari rendering are fixed in the tested setup. A separate instruction label still clips at the right edge. This is a display observation, not a language-accuracy review.

| Question | Answer | Result |
| --- | --- | --- |
| A2.1 — one em dash or three characters? | One em dash (U+2014), visibly correct in the heading and Sanskrit line. | PASS |
| A2.2 — lines broken or joined? | Broken correctly, including blank lines. The captured control text exactly equals the source licence with CR LF line endings. | PASS |
| A2.3 — Sanskrit present and rendered? | Yes: `सूत्रम् — सम्पूर्णं सूत्रम्` renders as Devanagari. The following Hindi paragraph also renders as Devanagari. No replacement boxes, wrong Latin letters or missing line observed. | PASS |
| A2.4 — any text truncated at the right edge? | Yes, the instruction above the licence edit control ends visibly at “You must accept”; its underlying text continues “the terms to continue.” No right-edge truncation observed in the captured licence body; its text wraps. | **FAIL for the full page** |

The control reports Segoe UI, logical height -19, through WM_GETFONT/GetObjectW. Windows can select fallback glyph fonts; this does not identify every rendered glyph's font. The untouched text file read from the control contains {licence_text.count(chr(10))} CR LF breaks; the control reports 49 display lines after wrapping. The screenshot is the full 1000 × 750 setup window at this machine's existing display configuration.

Captured before accepting or advancing: [top](capture-retry-licence-top.png), [middle](capture-retry-licence-middle.png), [Sanskrit/Hindi](capture-retry-licence-sanskrit.png), [bottom](capture-retry-licence-bottom.png). [Exact UTF-8 text extracted from the UTF-16 control](capture-retry-licence.txt). [Capture/process record](capture-retry-install.json). The same rendering was captured before [reinstall](reinstall-licence-sanskrit.png).

![Sanskrit and Hindi in the actual licence control](capture-retry-licence-sanskrit.png)

An earlier wizard yielded valid top/middle/bottom captures, then changed to the location page and closed outside the automation's scripted actions. The five supplemental captures from that attempt show the location page and are **not evidence of licence rendering**. The cause of that navigation is not established. The installer was reopened; the valid captures linked above were inspected before continuation. Invalid attempts remain local and are excluded from the published evidence manifest. See COMMANDS.md.
''')
write('BUDGET.md',f'''# v312 walk budget — native compiler

The repository's variable-based shape meets the claim on Windows. The brief's illustrative literal sum reaches a different limit first, so “any 20,000-term sum produces E_VAKYA_SEEMA” is not established.

All six generated source files and their generator [budget.py](budget.py) are retained. Counts are exact: each expression joins precisely 10,000 or 20,000 terms with `+`. The three shapes are literal `1`, local variable `z = 1`, and a module-level initializer using `z = 1`. Each target path was absent before compilation. Tests used the installed compiler, SHA-256 `{c['compiler_sha256']}`.

| Shape | Terms | Compile exit | Output file | Observed result |
| --- | ---: | ---: | --- | --- |
| Literal `1+1+…` | 10,000 | 0 | Present | Runs, exit 0, prints `10000` |
| Literal `1+1+…` | 20,000 | 1 | Absent | `Sutram truti: vakya-vriksh seema atikram` — **different from brief's exact expected diagnostic** |
| Local `z+z+…` | 10,000 | 0 | Present | Runs, exit 0, prints `10000` |
| Local `z+z+…` | 20,000 | 1 | Absent | E_VAKYA_SEEMA, names 65536 |
| Global `z+z+…` initializer | 10,000 | 0 | Present | Runs, exit 0, prints `10000` |
| Global `z+z+…` initializer | 20,000 | 1 | Absent | E_VAKYA_SEEMA, names 65536 |

Exact local/global 20,000-term stdout (stderr empty):

```text
{next(x['stdout'] for x in budget if x['name']=='variable-20000').rstrip()}
```

Literal 20,000-term stdout (stderr empty):

```text
{next(x['stdout'] for x in budget if x['name']=='literal-20000').rstrip()}
```

The literal diagnostic is the earlier syntax-tree capacity refusal; this probe does not reach the expression walk's diagnostic. The actual Linux gate `tests/r143/test_walk_budget.py` uses variables, not repeated integer literals. Its local and global shapes were reproduced here. No Linux literal comparison was run, so this report does **not** establish a platform discrepancy. No crash, hang or output file occurred on any refusal.

[Raw commands, source/output hashes, exits and timings](budget.json). The generator exits 1 because it deliberately retains the literal-20,000 expectation mismatch (five of six expectations pass); that is not hidden as a harness failure. No compiler, example or golden was modified.
''')
survivors=[]
for root,rows in newroots.items():
    for row in rows:
        survivors.append(f"- `{row['path']}`"+(" — directory." if row['directory'] else f" — {row['bytes']} bytes, SHA-256 `{row['sha256']}`."))
write('UNINSTALL.md',f'''# v312 uninstall — Settings → Apps → Installed apps

The Settings uninstall succeeds, removes the canonical installation and active registration, and creates no new visible console/PowerShell window in the observation. **The strict “nothing survives” criterion fails:** its temporary directory, script and log remain. Nothing was manually deleted before, during or after this uninstall test.

## B1 — timeline and visible result

The monitor started at {obs['started']}, before opening the uninstall menu. The v312 entry and Settings confirmation were verified with UI Automation. [Confirmation screenshot](settings-uninstall-confirmation.png).

- Final Settings confirmation invoked: `{settings['confirmed']}`.
- Native launcher's child PowerShell engine began: `{engine['started']}`. Parent PID 25268 is reported by Windows; the short-lived launcher itself was not sampled, so no launcher exit code is claimed.
- The Sutram row disappeared between 4.256 and 4.788 seconds after confirmation.
- Engine PID 16088 exited 0 at `{engine['exit_time']}`: **{engine_seconds:.3f} seconds of engine lifetime**, **{confirmed_seconds:.3f} seconds from final confirmation**. Observation noticed completion at {settings['elapsed_seconds']:.3f} seconds. Menu preparation/approval pauses are excluded from these durations.
- Last product result: Settings has no matching app. [Verified final screenshot](settings-uninstall-final-recheck.png). No separate uninstall progress bar, completion window or error dialog was observed.

**Console:** zero new visible console/Terminal windows in the WinEvent create/destroy/show/hide hook and repeated top-level sampling. **PowerShell window:** none attributable to uninstall; its child ran without one. Event hook used a dedicated message-pump thread; process/window sampling is not a continuous video. [Observer record](uninstall-observer.json), [engine log](uninstall-engine.log), [Settings timing](settings-uninstall.json).

The account already had a PowerShell pseudoconsole and Windows Terminal hosting this Codex session. They were baselined before uninstall, and their pre-test creation times are recorded in [final-check.json](final-check.json). That existing terminal covered the first post-completion screenshot; it is not evidence of an uninstall-created console. That invalid image is retained locally, not published. Settings was focused again for the valid final image. Thus the precise supported finding is **no new uninstall console**, not that no console existed anywhere on the desktop.

## B2 — commands and active state

All four requested command outputs, with exit codes and the complete Programs listing, are in [after-uninstall-state.json](after-uninstall-state.json). The shell ran from the isolated build directory with PATH freshly read from the machine/user registry, avoiding an inherited stale PATH and a repository-local `sutram.exe`.

| Check | Actual |
| --- | --- |
| `dir "%LOCALAPPDATA%\\Programs"` | Canonical `Sutram` absent; 58 earlier preserved Sutram backup/test roots remain, all predating this run |
| `reg query "HKCU\\Software\\Classes\\.sm" /s` | Exit 1, key not found; `.sm\\OpenWithProgids` also absent |
| `reg query "HKCU\\Environment" /v Path` | Sutram entry removed; user PATH exactly equals the pre-install baseline |
| `where sutram` | Exit 1, `INFO: Could not find files for the given pattern(s).` |
| Sutram.Source / uninstall registration | Both absent |
| Start Menu Sutram folder / desktop shortcut | Both absent; the desktop shortcut was not selected for this installation |
| Transaction directory / lock file | Both absent |
| Machine PATH | Unchanged |

## B3 — exact new survivors

The complete new residue found in the package/transaction/temp inventory is:

{chr(10).join(survivors)}

The script hash equals this candidate's `windows/native-installer/uninstall-core.ps1`. The log records removal of the two empty Classes keys, then successful completion. The files were still present at the final check. The new v312 installation was subsequently restored as Task D requests; the after-uninstall snapshot above is the state **before** that reinstall.

## Pre-existing survivors, separately attributed

The following Explorer history keys also survive and are byte/value-identical to the before-uninstall inventory:

- `HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\.sm` — no direct values, two subkeys.
- `...\\.sm\\OpenWithList` — `a = sutram-ide-gui.exe`, `MRUList = a`.
- `...\\.sm\\OpenWithProgids` — `Sutram.Source`, REG_NONE.

These are **different** from the repaired `HKCU\\Software\\Classes\\.sm\\OpenWithProgids`. The pre-existing `%TEMP%\\STM1E91.tmp` directory also remains with `uninstall-core.ps1` (13,794 bytes) and `uninstall.log` (117 bytes), unchanged by this round. The older preservation registry archive and 58 backup/test roots remain untouched. Every inspected surviving registry key, with its values/empty state, and all 58 root names are listed in [SURVIVORS.md](SURVIVORS.md); exact values/hashes are in the [before](before-uninstall-inventory.json) and [after](after-uninstall-inventory.json) inventories.

This is an existing-account package/state inventory, not a whole-disk or all-Windows-telemetry forensic audit. Older backup trees are named, not recursively rehashed in this round. No clean-machine or absolute machine-wide erasure claim is made.
''')
lines=['# Inspected survivors after v312 uninstall\n','This list describes the after-uninstall snapshot, before Task D reinstall. New residue is distinguished in UNINSTALL.md.\n','## Inspected files and directories\n']
for root,rows in after['roots'].items():
    if not rows:continue
    for row in rows:lines.append(f"- `{row['path']}` — "+('directory' if row['directory'] else f"{row['bytes']} bytes; SHA-256 `{row['sha256']}`"))
lines+=['\n## Pre-existing preservation roots, untouched\n']
lines.extend('- `'+p+'`' for p in after['preserved_old_roots'])
lines+=['\n## Every surviving key in the inspected registry subtrees\n']
def reglines(r):
    if r is None:return
    lines.append(f"- `{r['path']}` — {len(r['values'])} value(s), {len(r['subkeys'])} subkey(s)."+' Values: '+json.dumps(r['values'],ensure_ascii=True))
    for child in r['subkeys']:reglines(child)
for r in after['registry'].values():reglines(r)
write('SURVIVORS.md','\n'.join(lines)+'\n')
write('RESULTS.md',f'''# Sutram v312 — Windows first-contact verification, 8 November 2026

**Devanagari, em dashes, licence line breaks, silent uninstall, the empty Classes key cleanup, the variable-based walk refusal, and all 322 native suite cases are verified on this Windows account. Two product findings remain: clipped licence-page instructions and uninstall's temporary script/log residue.** The illustrative literal sum also reaches a different diagnostic before the walk budget. No release acceptance is claimed.

Pinned source: `{c['source_commit']}`. Windows 11 Home build 26300, non-elevated token, existing account. The canonical installation was absent at the start; older backups and Explorer history were present. No compiler, installer, library, example, golden or workflow changes were made. No CI workflow was launched.

| Test | Expected | Actual | Pass? |
| --- | --- | --- | --- |
| A2.1 — em dash is one character | one | Single U+2014 displayed correctly | PASS |
| A2.2 — lines are broken, not joined | broken | CR LF; text exactly matches licence source | PASS |
| A2.3 — Sanskrit renders as Devanagari | renders | Actual Sanskrit and Hindi lines visibly render | PASS |
| A2.4 — no text truncated at edge | none | Body wraps; instruction label clips “the terms to continue.” | **FAIL** |
| B1 — no console or PowerShell window | none | No new uninstall window detected; pre-existing Codex terminal separately identified | PASS within observed scope |
| B2 — `.sm\\OpenWithProgids` gone | gone | Classes key and empty parent removed | PASS |
| B2 — PATH entry removed | removed | Baseline user PATH restored; `where sutram` exit 1 | PASS |
| B3 — nothing survives uninstall | nothing | New temporary directory with script and log survives; pre-existing history/backups separately listed | **FAIL** |
| C1 — 10,000 terms compile | exit 0 | Literal, variable, global all compile and print 10000 | PASS |
| C2 — 20,000 terms refused | E_VAKYA_SEEMA | Variable/global: exact code and 65536, exit 1, no file; literal: earlier tree-capacity refusal | **PASS gate shape; FAIL literal example's exact expectation** |
| D — identity | v312, one path | One canonical path; v312; 657/657 hashes | PASS |
| D — suite | 322 PASS, no FAIL | 322 PASS, 0 FAIL/COMPILE_FAIL/TIMEOUT; 3 NO_EXPECTATION, 6 explicit skips | PASS |
| D — suite elapsed time | compare to 18.6 s | **{elapsed:.3f} s**, +{delta:.3f} s / **+{pct:.2f}%** | RECORDED; materially slower single sample |

Exact first version line: `Sutram 1.0 (v312) - sampurna sutra`. Second line: `Samskrita-mukhya bhasha -> x86-64 yantra-bhasha`.

| Artifact | SHA-256 |
| --- | --- |
| Setup / installed uninstaller | `{c['setup_sha256']}` |
| Installed / repository compiler | `{c['compiler_sha256']}` |
| Payload manifest | `{c['manifest_sha256']}` |

Native installation reached Finish in 27.910 seconds; reinstall in 35.512 seconds. Both engines exited 0 and the wizards closed after Finish. v312 remains installed. [Fresh-shell identity and full installed hash comparison](reinstall-identity.json); [embedded payload checks](candidate.json). The native suite used the repository compiler, whose hash equals the installed compiler; [all case records](native-cases.json), [timing](suite-timing.json). The timing includes harness and process startup overhead. One sample is insufficient to attribute the slowdown to the walk budget.

Details: [LICENCE](LICENCE.md), [UNINSTALL](UNINSTALL.md), [BUDGET](BUDGET.md), [survivors](SURVIVORS.md), [commands and evidence limitations](COMMANDS.md). All generated probes and their generator are included. Evidence integrity: EVIDENCE.sha256.

All seven tracked wizard/engine/observer process identities are gone; no Sutram-named process remains in [final-check.json](final-check.json). The user's existing Terminal and Settings were left open. No independent release verdict, broad regression rerun, race-safety proof, font coverage across machines, whole-machine cleanup guarantee, or Linux/Windows literal-shape comparison is claimed.
''')
write('COMMANDS.md',r'''# Commands, provenance and evidence boundaries

The supplied Downloads brief is preserved as REQUEST.md. PROJECT-MASTER.md and the design charter were read before work; the v312 project-status changes were read after fetching. The worktree was pinned with:

```powershell
git fetch origin
git worktree add --detach build/windows-v312 06324cef
python build/prepare-v312.py
```

Within that worktree, the evidence directory is `Windows-to-Sarvam/win-v312-2026-11-08`. The preparation script adapts the prior round's UI, package, identity and suite helpers without changing product code. The executed original preparation script lives at the parent checkout's `build/prepare-v312.py`; the copied script is retained as provenance of that workspace-specific operation.

```powershell
python Windows-to-Sarvam/win-v312-2026-11-08/pin-fix-package.py
& Windows-to-Sarvam/win-v312-2026-11-08/state.ps1 -Name before-install
& Windows-to-Sarvam/win-v312-2026-11-08/install.ps1 -Phase licence -Name initial
& Windows-to-Sarvam/win-v312-2026-11-08/licence-details.ps1
& Windows-to-Sarvam/win-v312-2026-11-08/install.ps1 -Phase licence -Name capture-retry
# All relevant screenshots were inspected before continuing.
& Windows-to-Sarvam/win-v312-2026-11-08/install.ps1 -Phase complete -Name capture-retry
python Windows-to-Sarvam/win-v312-2026-11-08/budget.py
python Windows-to-Sarvam/win-v312-2026-11-08/inventory.py before-uninstall
& Windows-to-Sarvam/win-v312-2026-11-08/state.ps1 -Name before-uninstall
& Windows-to-Sarvam/win-v312-2026-11-08/start-uninstall-observer.ps1
& Windows-to-Sarvam/win-v312-2026-11-08/settings.ps1 -Action open
& Windows-to-Sarvam/win-v312-2026-11-08/settings.ps1 -Action search
& Windows-to-Sarvam/win-v312-2026-11-08/settings.ps1 -Action menu
& Windows-to-Sarvam/win-v312-2026-11-08/settings.ps1 -Action uninstall
& Windows-to-Sarvam/win-v312-2026-11-08/settings.ps1 -Action confirm
python Windows-to-Sarvam/win-v312-2026-11-08/inventory.py after-uninstall
& Windows-to-Sarvam/win-v312-2026-11-08/state.ps1 -Name after-uninstall
& Windows-to-Sarvam/win-v312-2026-11-08/settings.ps1 -Action inspect
& Windows-to-Sarvam/win-v312-2026-11-08/install.ps1 -Phase licence -Name reinstall
# Reinstall licence capture also inspected before continuing.
& Windows-to-Sarvam/win-v312-2026-11-08/install.ps1 -Phase complete -Name reinstall
python Windows-to-Sarvam/win-v312-2026-11-08/time-suite.py
& Windows-to-Sarvam/win-v312-2026-11-08/final-check.ps1
python Windows-to-Sarvam/win-v312-2026-11-08/report.py
```

## Observational/harness issues, preserved rather than promoted to product failures

- The first wizard advanced and closed outside the scripted actions. Its initial three licence captures are valid; the five `licence-line-*.png` supplemental captures show Location, not licence. Those invalid images remain only in the local worktree. The supplemental JSON's font/text queries are retained, with this limitation. The retry captures explicitly checked the licence control was visible.
- An exploratory `identity.py --name observed-current-identity` call after that closure failed because there was no installation/manifest. No identity success was claimed; the complete later install passed identity before tests.
- A Settings menu disappeared between tool calls; the first uninstall-menu invocation stopped with `Uninstall menu item missing` before invoking anything. The helper was changed to reopen and invoke the scoped Sutram menu in one operation. The confirmation button's actual UI Automation ID was read before invocation.
- The first final Settings screenshot was occluded by the pre-existing Codex Terminal. It is retained locally as `settings-uninstall-final.png`, excluded from publication. The helper now foregrounds Settings immediately before capture; `settings-uninstall-final-recheck.png` is the inspected result.
- The reinstall Finish screenshot was skipped when the intended window could not be foregrounded; reinstall-install.json records finish_screenshot as null. Completion is supported by the observed Finish label, engine exit 0, wizard closure and subsequent identity check. The first successful installation's Finish screenshot was captured and inspected.
- Full Settings UI dumps contain unrelated account/application information and remain only under local `build/native-v312/settings-*.json`. Published screenshots capture just the Apps content region, excluding account identity. The exact capture method is in settings.ps1.
- The initial final-check CIM query was denied in the sandbox; the same read-only check succeeded with approved host access. Host access was also approved for GUI and native installation operations. The final Windows token was not elevated to administrator.
- A convenience console print of Settings timing failed on CP1252's inability to print U+200E; its JSON file was intact. This is a reporting-shell encoding issue, not a Sutram result.
- Report validation caught a helper encoding defect: install.ps1 reloaded its UTF-8 JSON without an explicit encoding when continuing the wizard, so Windows PowerShell 5.1 corrupted the duplicated licence_text field in capture-retry-install.json and reinstall-install.json when saving the completion record. The direct `*-licence.txt` captures and screenshots were never changed and are the authoritative text/rendering evidence; the direct capture exactly equals LICENSE.txt with CR LF. Original JSON records are retained unchanged to expose this defect. The helper now explicitly reads UTF-8; this correction does not change native observations or require another installation. A diagnostic print also hit the reporting console's CP1252 limit. No product encoding defect is inferred from those helper errors.
- WSL distributions were listed while considering the literal-shape discrepancy, but no Linux comparison was executed. No additional test result is inferred from that listing.
- No manual cleanup, registry clearing, backup movement or file deletion was performed for this round. Existing backups and registry archives stayed in place. The setup's own temporary staging cleanup and uninstall's own removals are the product behavior under test.

The generator asserts the reported identity, suite counts, licence text, registry/PATH cleanup and process exits against saved JSON. `.gitattributes` disables line-ending conversion for this evidence directory. EVIDENCE.sha256 covers every published file except itself. Product acceptance remains for the release review.
''')
shutil.copy2(Path(os.environ['LOCALAPPDATA'])/'Programs/Sutram/install.log',HERE/'reinstall-engine.log')
write('evidence-check.json',json.dumps({'source_commit':c['source_commit'],'licence_exact_crlf_match':True,'suite_counts':dict(counts),'suite_seconds':elapsed,'suite_change_percent':pct,'budget_expectations_passed':sum(x['pass'] for x in budget),'budget_expectations_total':len(budget),'new_surviving_files':sum(not x['directory'] for rows in newroots.values() for x in rows),'engine_seconds':engine_seconds,'confirmation_to_exit_seconds':confirmed_seconds,'identity_pass':identity['pass'],'all_tracked_processes_closed':True},indent=2)+'\n')
excluded={'settings-uninstall-final.png',*[f'licence-line-{n}.png' for n in [7,14,27,33,39]]}
published=[p for p in sorted(HERE.iterdir()) if p.is_file() and p.name not in excluded and p.name not in ['EVIDENCE.sha256']]
write('EVIDENCE.sha256',''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()} *{p.name}\n' for p in published))
print(json.dumps({'published_files':len(published)+1,'excluded_local_invalid_images':sorted(excluded),'suite':dict(counts),'suite_seconds':elapsed,'new_residue_files':2},indent=2))

from pathlib import Path
import json,hashlib,subprocess,datetime
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def load(name):return json.loads((HERE/name).read_text(encoding='utf-8-sig'))
def write(name,text):(HERE/name).write_text(text,encoding='utf8',newline='\n')
a=load('availability.json');b=load('boundary-summary.json');label=load('label-capture.json');temp=load('temp-inspection.json')
assert not a['v313_available'] and '(v312)' in a['available_version']['stdout']
assert not a['installation_attempted'] and label['closed_without_install']
assert b['last_compiles']==16384 and b['first_refuses']==16385
source=subprocess.check_output(['git','show',a['source_commit']+':windows/native-installer/sutram_wizard.asm'],cwd=ROOT).decode('utf8')
def excerpt(start,end):return source[source.index(start):source.index(end,source.index(start))]
write('label-source.txt',excerpt('    ; ---- page 1: license ----','    ; read-only license edit'))
write('temp-name-source.txt',excerpt('temp_prefix: u16 "STM"','extern __imp_GetLastError'))
write('source-context.json',json.dumps({'source_commit':a['source_commit'],'wizard_source_sha256':hashlib.sha256(source.encode('utf8')).hexdigest(),'instruction_text':label['expected_text'],'note':'The instruction text is b_lichead in windows/native-installer/sutram_wizard.asm, not LICENSE.txt.'},indent=2)+'\n')
write('.gitattributes','* -text\n')
write('LICENCE.md',f'''# Licence instruction — pre-fix evidence; v313 unavailable

**These are new measurements of the available v312 setup, not v313 acceptance.** The wizard was opened only to the licence page, captured and closed without accepting or installing. Its SHA-256 is `{a['available_setup_sha256']}`. This is the newer v312 repack on main; it is not the setup hash from the earlier v312 acceptance run.

## A1–A2: exact display and missing words

Visible text in the [full page](prefixed-licence-default.png) and [exact instruction-control crop](prefixed-instruction-crop.png):

> Please read the following license agreement. You must accept

Full source/control text:

> Please read the following license agreement. You must accept the terms to continue.

Missing from the display: **“the terms to continue.”** The label is **above the licence body**, not at the bottom as the brief describes. Its source is `b_lichead` in `windows/native-installer/sutram_wizard.asm`; LICENSE.txt contains the body, not this instruction.

![Exact visible instruction control](prefixed-instruction-crop.png)

The default window is 1000 × 750 screen pixels; the label's screen rectangle is 663 × 33 pixels. The source allocates **530 × 26 logical pixels**, at y=62; the licence body begins at y=94. [Source excerpt](label-source.txt), [capture/process/geometry record](label-capture.json).

At the source's Segoe UI height -19 and weight 400, a local GDI calculation measures the full line as **709 pixels wide**. At width 530 it requires **two lines / 50 pixels of height**. This is a source-based layout model, not a measured repair: increase label height and move/resize the following body to keep them from overlapping. The source offers only 32 pixels from the label's top to the body's top. [Model and exact metrics](label-layout-model.json), [reproduction](label-layout-model.ps1).

The first cross-process GDI attempt did not check SelectObject success and produced a result inconsistent with the visible clipping. Its `gdi_metrics` remain in the raw capture record but are **not accepted evidence**. The separate model creates and validates its own font; the screenshot, full WM_GETTEXT text and window rectangles are the native observations.

## A3: two sizes after the fix

**NOT RUN — no v313 package is available.** The current wizard also has no resizable border. When the fix arrives, test its default size and a supported narrower size; if it is still fixed-size, document that and distinguish an API-forced width from normal user resizing. Neither a source layout calculation nor a forced size of the unfixed v312 wizard proves the v313 criterion.
''')
newdir=next(x for x in temp['locations'][0]['stm_directories'] if x['directory'].endswith('STM7C1C.tmp'))
filelist='\n'.join(f"- `{x['path']}` — {x['bytes']} bytes; SHA-256 `{x['sha256']}`." for x in newdir['files'])
write('UNINSTALL.md',f'''# Temporary-directory finding — preflight inventory

**No new install or uninstall was performed in this round.** The available package is v312; the v313 package needed to verify successful cleanup is absent. The working v312 installation and all residue were left untouched.

## B1: identified directory and every file

The read-only inspection at `{temp['time']}` confirms the previously observed directory still exists:

`C:\\Users\\dmech\\AppData\\Local\\Temp\\STM7C1C.tmp`

{filelist}

These are the v312 uninstaller's script and successful-uninstall log, not unrelated files. Their hashes match the prior round's post-uninstall evidence exactly. The prior log reports removal of the empty Classes keys and then successful completion. This identifies the outstanding residue; it is not a new uninstall pass. [Current inventory](temp-inspection.json), [prior full uninstall evidence](../win-v312-2026-11-08/UNINSTALL.md).

`%TEMP%` and `%LOCALAPPDATA%\\Temp` resolve to the **same directory** for this account. The inspection records the 15 newest entries in each location plus every file in each STM directory. It uses direct filesystem enumeration with modification times, equivalent to the relevant listing purpose of `dir /od`; no new post-uninstall command run is claimed.

An older `STM1E91.tmp` also remains, with `uninstall-core.ps1` (13,794 bytes) and `uninstall.log` (117 bytes). It predates the v312 run; it is not evidence of a repeated v313 uninstall.

## B2: directory naming and repeat run

Observed names: `STM1E91.tmp` and `STM7C1C.tmp`. The source calls **GetTempFileNameW with prefix `STM` and uniqueness input zero**, then replaces that temporary file with a directory. The observed pattern is **`STM<hexadecimal unique component>.tmp`**, not a timestamp chosen by Sutram. Do not infer randomness from the names. [Exact source excerpt](temp-name-source.txt).

**New install/uninstall repetition: NOT RUN**, because installing another v312 package would not satisfy the brief's v313 identity requirement. Historical names plus source establish the naming mechanism; they do not establish v313 cleanup repeatability.

## B3: after-fix removal and other new artifacts

**NOT RUN — v313 unavailable.** Once supplied, snapshot both temp locations, run two installation/uninstallation cycles, track each exact staging path, and compare the before/after listings. Verify the script, log and directory disappear after successful uninstall and identify any other new entries. No files were deleted to make this condition appear satisfied.
''')
write('BUDGET.md',f'''# Refusal message and exact boundary — new v312 baseline measurement

**This is pre-fix evidence from the installed v312 compiler. The v313 limit/message must be checked independently when available.** Compiler SHA-256: `{a['installed_compiler_sha256']}`. No repeated-literal probe or suite was run.

## C1: whole message

For the first refusing count, 16,385 variable terms, compile exit is 1, stderr is empty, and no output executable exists. Exact stdout:

```text
{b['full_refusal_message'].rstrip()}
```

## C2: is it actionable?

**Yes, for someone who understands the romanized Sanskrit wording.** The hint explicitly tells the reader to split the statement into smaller statements and keep intermediate values in named variables. It names a remedy, not just a diagnostic code and limit. In English, the practical instruction is “split the expression and store intermediate results.”

For example, replace one enormous sum with several smaller `vitti` assignments and combine their named results. The number 65536 denotes analysis visits, **not the number of source terms**; presenting it as a term allowance would mislead a beginner. A worked small example and a source location would make the remedy easier to apply. This is an editorial assessment by the same assistant that saw the v312 diagnostic, not a first-time-human usability test or proof that all beginners understand it.

## C3: exact adjacent counts

The exact generated shape follows the new brief:

```sutram
mukhya() {{
    vitti x = 1
    vitti s = x+x+...  // exactly N occurrences of x
    likha(s)
}}
```

| N | Compile | Runtime / diagnostic |
| ---: | --- | --- |
| **16,384** | Exit 0; output exists | Runs with exit 0 and prints `16384` |
| **16,385** | Exit 1; no output | E_VAKYA_SEEMA, number 65536, full hint above |

The bracket 8,200–16,400 from the Linux summary contains this transition. Fifteen probes were run by bisection. Every compiling probe was executed and printed its exact N; every refusal in this search had E_VAKYA_SEEMA and no executable. [Summary](boundary-summary.json), [all commands/exits/messages/timings](boundary-raw.json), [generator](budget-boundary.py). All 15 generated sources are retained.

This boundary is for this exact **local assignment** shape, not every syntax shape. Statement structure changes visit counts; a global initializer or direct `likha(sum)` can differ. No cross-platform reproduction was run in this round, and no v313 result is inferred from v312.
''')
write('RESULTS.md',f'''# v313 Windows verification — package unavailable; preflight evidence only

**v313 testing cannot proceed: main at `{a['source_commit']}` still packages v312.** The embedded compiler was extracted without installing, executed natively with `--version`, and matched the repository and installed v312 compiler hash. A final fetch found no newer candidate. GitHub's main-ref API confirmed the pinned commit.

Exact available version output:

```text
{a['available_version']['stdout'].rstrip()}
```

| Available artifact (v312, not v313) | SHA-256 |
| --- | --- |
| Current main setup | `{a['available_setup_sha256']}` |
| Embedded/repository/installed compiler | `{a['available_compiler_sha256']}` |

[Preflight identity evidence](availability.json). The current setup is a v312 repack; its different setup hash does not establish v313. The latest `Sarvam-to-Claude/ROUND-147.md` still assigns the two first-contact fixes. No v313 identity, installation, cleanup or suite result is claimed.

| Test | Expected | Actual | Pass? |
| --- | --- | --- | --- |
| A1 — instruction fully visible | full text | Available v312 label ends “You must accept”; new full-page and close captures | FAIL, pre-fix only |
| A3 — default window after fix | readable | v313 not available | NOT RUN |
| A3 — narrower window after fix | readable | v313 not available; current wizard has no resizable border | NOT RUN |
| B1 — temp directory identified | named | STM7C1C.tmp remains, exactly script and log, hashes recorded | IDENTIFIED, existing residue |
| B2 — repeated install/uninstall | repeatable observation | No v313 package | NOT RUN |
| B3 — gone after fix | gone | No after-fix package | NOT RUN |
| C1 — whole refusal message | recorded | E_VAKYA_SEEMA + 65536 + full split-statement hint | RECORDED, v312 baseline |
| C2 — actionable? | judgement | Yes for a reader of its wording; hint says split and name intermediates | ASSESSED; not a human usability test |
| C3 — boundary term count | exact number | Local assignment: 16,384 compiles/runs; 16,385 refuses | MEASURED, v312 baseline |
| D — identity | v313, one path | Available/installed compiler is v312; no installation attempted | BLOCKED ON PACKAGE |
| D — native suite | 322 PASS, no FAIL | v313 unavailable; prior suite not rerun | NOT RUN |
| D — elapsed time | compare to 18.6 s | No v313 run | NOT RUN |

Details: [LICENCE](LICENCE.md), [UNINSTALL](UNINSTALL.md), [BUDGET](BUDGET.md). All generated probes and scripts are included. No product source, workflow, installation, registry entry, temp residue, golden or previous evidence was changed. The capture wizard closed without installation. No release acceptance is claimed; the requested v313 work remains pending its package.
''')
write('COMMANDS.md',r'''# Commands and limits

The user's Downloads brief is preserved as REQUEST.md. Required project documents were read first. `git fetch origin` required approved host access because the sandbox denied .git/FETCH_HEAD. Latest candidate source was pinned to 108301e2155b7c48e3e6d88103910148662fd191; a later final fetch was unchanged. The GitHub main-ref API returned the same commit.

From the parent repository:

```powershell
python build/preflight-v313.py
python build/windows-v313-preflight/Windows-to-Sarvam/win-v313-2026-11-08/budget-boundary.py
& build/windows-v313-preflight/Windows-to-Sarvam/win-v313-2026-11-08/label-capture.ps1
& build/windows-v313-preflight/Windows-to-Sarvam/win-v313-2026-11-08/label-layout-model.ps1
python build/windows-v313-preflight/Windows-to-Sarvam/win-v313-2026-11-08/temp-inspect.py
python build/windows-v313-preflight/Windows-to-Sarvam/win-v313-2026-11-08/report.py
```

The preparation script saves the available setup and extracted compiler only under `build/windows-v313-preflight/artifacts`; neither binary is duplicated in the evidence commit. Native compiler identity was measured before any installation. The screenshot helper was approved to open the available installer, capture only its licence page and close it. No install/uninstall cycle occurred.

The screenshot and crop are direct screen captures of the intended foreground wizard and its instruction control. The filenames use `prefixed-` as “pre-fix evidence”; they do not indicate a repaired build. No image reconstruction or text replacement was used.

The original cross-process GDI size result is rejected because font selection was not validated and its result contradicts the screenshot. The replacement source-layout model creates its own font and checks font selection; it is explicitly not proof of a repaired GUI. Neither measurement substitutes for the missing v313 default/narrow captures.

Only the new budget-boundary measurements are reported. The literal-expression shape and previous v312 suite/passes were not repeated. Raw 15-probe data includes exits, no-output checks, runtime verification and exact source hashes. Its generator refuses stale output files.

The temp inspection is read-only and records newest entries, exact known staging contents and hashes. It is a preflight inventory, not a new post-uninstall test. No manual cleanup was performed.

Scripts retain their original workspace paths for provenance. The copied preflight/report scripts were run from the build locations shown above. `.gitattributes` preserves raw evidence bytes. EVIDENCE.sha256 covers every published file except itself.
''')
write('EVIDENCE.sha256',''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()} *{p.name}\n' for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='EVIDENCE.sha256'))
print(json.dumps({'status':'v313 unavailable; preflight only','files':len(list(HERE.iterdir())),'boundary':[b['last_compiles'],b['first_refuses']],'installation_attempted':False},indent=2))

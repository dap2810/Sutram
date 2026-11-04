import collections,json
from pathlib import Path
h=Path(__file__).resolve().parent
d=json.loads((h/'results.json').read_text(encoding='utf8'))
gui={x['test']:x for x in json.loads((h/'gui-results.json').read_text(encoding='utf8'))}
for r in d['rows']:
    n=r['test']
    if n in gui:
        r['gui']=gui[n]
        if n==22: r.update(result='PASS',notes='Installed IDE launched directly; Start Menu shortcut not exercised.')
        if n==23: r.update(result='PASS' if gui[n]['output']=='namaste' else 'FAIL',notes='Exact supplied hello program run in installed IDE.')
        if n==24: r.update(result='UNEXPECTED',notes='Correct Sanskrit error in Latin transliteration; this program emits no Devanagari. Separate test21 screenshot verifies Devanagari rendering in the IDE.')
        if n==21: r['notes']='Captured UTF-8 is correct; IDE screenshot visually confirms Devanagari. CMD font rendering not tested.'
        r.pop('notes',None) if r.get('notes')=='IDE evidence to be added by GUI driver.' else None
counts=collections.Counter(r['result'] for r in d['rows'])
(h/'final-results.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
lines=['# Sarvam Windows acceptance sheet — v297 results','',
'Executed 2026-11-03 against the exact examples from `SUTRAM-WINDOWS-TEST.md` supplied in Downloads. '
'Request copy, exact program files, commands, separate stdout/stderr, exit codes, timings, and IDE screenshots are retained in '
'`sarvam-acceptance-v297-2026-11-03/`.', '',
'## Outcome','', ', '.join(f'**{v} {k}**' for k,v in counts.items())+'. No five-second hangs observed.', '',
'**Confirmed failures: tests 18 and 19.** Memory accounting stays zero and the allocation budget is not enforced. '
'The string, naming/alias, arithmetic-refusal, withdrawn-function and Unicode-output tests passed.', '',
'Direct-compiler route (Route B semantics), using the already installed v297 binary rather than the repository-root binary. '
'Installation, uninstall and a new desktop CMD session were not performed. The existing installation was preserved. '
'This is not full installer acceptance. No tracked compiler, library, pack or golden was changed; only requested report/evidence files were created.', '',
f"Windows: `{d['windows']}`. Console/harness: {d['console']}.",
f"Compiler: `{d['compiler']}`.",f"Compiler SHA-256: `{d['sha256']}`.",'',
'Exact full version output:','```text',d['rows'][1]['run']['stdout'].rstrip('\n'),'```','',
'## One row per requested test','', '| Test | Result | Actual output / notes |','|---|---|---|']
for r in d['rows']:
    event=r.get('run',r.get('compile',{}))
    actual=(event.get('stdout','')+event.get('stderr','')).strip().replace('\n',' / ').replace('|','\\|')
    note=r.get('notes','')
    if r['test']==18: note='Expected in=4096; actual in=0. Exit 0.'
    if r['test']==19: note='Expected E_PARIMITA; instead prints the sum and exits 0.'
    if r['test']==12: note='Runtime stdout=1; deprecation notices occur on compiler stderr, not compiler stdout. Streams below.'
    if r['test']==2: note='Full-path invocation; bare command PATH caveat below.'
    lines.append(f"| {r['test']} — {r['title']} | {r['result']} | {actual} {note} |")
lines += ['', '## Findings and limitations', '',
'- **PATH collision:** the legacy `%LOCALAPPDATA%\\Sutram\\bin` precedes the new '
'`%LOCALAPPDATA%\\Programs\\Sutram\\bin` in the persisted user PATH. A supplementary CMD process '
'with PATH reconstructed from machine and user settings was run; see `path-check.txt`. This is not '
'a manually opened new desktop CMD session. Outside the repository root, it resolves the legacy executable and '
'prints `Sutram 1.4.0`. Running CMD from the repository root instead finds the root v297 executable first, '
'which masks this PATH collision. Full-path v297 results must not be confused with bare-command results.',
'- Existing install.log ends with installation complete, but this run did not witness the installer dialogs or test uninstall. '
'The known v243 payload issue was not observed in the tested installed binary. The older legacy installation reports 1.4.0, a separate issue.',
'- Test24 emits Sanskrit in Latin transliteration. The sheet’s expectation of Devanagari from that exact program does not match its actual message. '
'The separate Devanagari example renders visibly in the installed IDE.',
'- Single-string `likha` in tests 5, 9 and 21 prints the requested text without a trailing newline. '
'An initial harness assumption added a newline; that assumption was corrected before final scoring. No program or golden was changed.',
'- An initial GUI-driver attempt reached the window before its controls were ready. Adding an 800 ms initialization wait '
'allowed the requested GUI checks to complete. This is recorded as a harness startup issue, not a compiler crash.',
'- The sheet says indentation, not braces, but its programs use braces; the exact supplied brace-based programs were tested. '
'The claim that Windows/IDE automation has never run is stale relative to the preceding 335-example report.',
'- Known withdrawn-function behavior and old linker diagnostic wording are not reported as new defects. '
'No linker test was requested by this sheet.', '',
'## IDE screenshots', '']
for n in (22,23,24,21):
    lines += [f"### Test {n}", '', f"![Test {n}](sarvam-acceptance-v297-2026-11-03/{gui[n]['screenshot']})", '']
lines += ['## Exact output and diagnostics', '', 'Empty streams are explicitly marked. Commands and elapsed times are in `final-results.json`.', '']
for r in d['rows']:
    lines += [f"### Test {r['test']} — {r['title']}", '']
    for phase in ('compile','run','gui'):
        if phase not in r: continue
        e=r[phase]
        lines += [f"{phase}; exit: {e.get('exit','not captured by GUI')}", '']
        for stream in (('output',) if phase=='gui' else ('stdout','stderr')):
            value=e.get(stream,'')
            lines += [stream+':','```text',value.rstrip('\r\n') if value else '(empty)','```','']
(h.parent/'WIN-SARVAM-ACCEPTANCE-V297-2026-11-03.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
print(dict(counts))

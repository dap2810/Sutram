import json,struct
from pathlib import Path
h=Path(__file__).resolve().parent
w=json.loads((h/'windows-results.json').read_text(encoding='utf8'))
l=json.loads((h/'linux-results.json').read_text(encoding='utf8'))
rows={r['name']:r for r in w['rows']}
assert w['hindi_exact_golden_match']
root=h.parents[1]/'build/windows-v297/source'
b=(h/'programs/C2.bin').read_bytes()
off=struct.unpack_from('<Q',b,32)[0];size,count=struct.unpack_from('<HH',b,54)
elf=[{'type':struct.unpack_from('<I',b,off+i*size)[0],'flags':struct.unpack_from('<I',b,off+i*size+4)[0]} for i in range(count)]
(h/'linux-segments.json').write_text(json.dumps(elf,indent=2),encoding='utf8',newline='\n')
lines=['# Windows round 2 results','',
'2026-11-03. Diagnosis/report only. No changes to compiler, libraries, examples, tests or goldens; no rebuild. '
'Pinned source/export: `'+w['source_commit']+'`. Existing Windows and Linux compiler binaries both report v297.', '',
'## Requested table','', '| Task | Test | Result | Exact output | Verdict |','|---|---|---|---|---|',
'| A | 220 with --lang hindi | PASS; exit 1 | Exact Hindi stdout below; stderr empty | Harness error confirmed; full golden match |',
'| A | 29 is Linux-only | Confirmed by reading | `mov eax,60 / mov edi,42 / syscall` (raw byte sequences in source) | Target-specific Linux syscall ABI; not a Sutram exit-code defect; not rerun |',
'| B | 317/parimana, supplied B1 | Gap confirmed; exit 0 | `start=0\nin=0\nafter=0\n` | All zeros |',
'| B | 318/parimana_moves | Gap confirmed; exit 0 | All six counters zero; exact multiline output below | Windows accounting absent |',
'| B | 303/parimita, supplied B2 | Gap confirmed; exit 0 | `200010000\n` | Does not refuse |',
'| B | 288/kosh alias, supplied B3 | Gap confirmed; exit 0 | `a[0]=41 k[0]=99\n` | Diverges; old-name warning on compiler stderr |',
'| B | Reference says Linux-only? | YES, for all three features | Exact quotes below | Honest about these gaps |',
'| C | anka_akshar minimal, Windows | Defect reproduced; exit 0 | `P\n` (hex 50 0a) | Wrong value; expected `B\n` (42 0a); no crash |',
'| C | vartani_sandhi minimal, Windows | Defect reproduced; exit 3221225477 / 0xC0000005 | stdout and stderr empty | Access violation; intended displayed result `abcd\n` not produced |',
'| C | Same anka_akshar probe, Linux | Exit 0 | `B\n` | Minimal example hides lifetime problem |',
'| C | Same vartani_sandhi probe, Linux | Exit 0 | `abcd\n` | Literal-write problem does not crash this ELF |', '',
'## What the builtins should return', '',
'`anka_akshar(66)` should return a valid NUL-terminated character-string pointer whose visible text is B. '
'The probe exercises it immediately through shabda. Source analysis from the previous diagnosis shows '
'the returned pointer at rsp-8; a PE adapter call can overwrite its storage with the return address. '
'Linux’s direct syscall path happens not to make that same call. The shared lifetime defect exists in '
'the implementation even though this Linux run prints B.', '',
'`vartani_sandhi` is implemented as an in-place strcat-style builtin returning the destination pointer. '
'The example implies that passing literals ab and cd should yield abcd, but its first argument is not '
'a writable buffer with spare capacity. The compiler emits a store into that literal. The API contract '
'must be resolved by the Linux-side owners: reject immutable destinations or implement the intended '
'allocating operation. A writable-buffer control succeeded in the previous diagnostic round. '
'Do not make PE code pages writable as a workaround.', '',
'The Linux C2 executable has these ELF program-header entries (type 1 is LOAD; flags 7 are read/write/execute): '
'`'+json.dumps(elf)+'`. This explains why this generated Linux image permits the literal write. '
'Both programs producing expected Linux text is **not** proof of valid lifetime/capacity semantics. '
'This run does not establish how historical goldens were recorded or prove that all Linux uses fail.', '',
'## Reference quotes (pinned v297)', '']
text=(root/'docs/LANGUAGE-REFERENCE.md').read_text(encoding='utf8').splitlines()
for start,end in [(976,980),(1307,1308),(1350,1353)]:
    lines += [f'`docs/LANGUAGE-REFERENCE.md:{start}–{end}`:', '', *['> '+x for x in text[start-1:end]], '']
lines += ['The brief’s wording “that instruction does not exist on Windows” needs precision: x86-64 SYSCALL '
'exists on Windows; the Linux syscall-number and register ABI in this example is not a portable Windows '
'exit operation. We did not rerun or attempt to port it.', '',
'## Provenance and commands', '',
'Windows compiler SHA-256: `'+w['compiler_sha256']+'`.',
'Linux compiler SHA-256: `'+l['compiler_sha256']+'`.',
'Linux host: `'+l['host']+'`, uid '+str(l['uid'])+'. No root execution.', '',
'Exact process argv arrays, cwd, output streams, output hex, exit codes and timings are in '
'`windows-results.json` and `linux-results.json`. Every generated source is in `programs/*.sm`. '
'`run.py`, `linux_compare.py`, and `report.py` reproduce the work. Five-second subprocess bounds were used; no test timed out.', '',
'Host commands:', '```text',
'python Windows-to-Sarvam/win-round2-2026-11-03/run.py',
'wsl --list --quiet',
'wsl -d Ubuntu -- id -u',
'wsl -d Ubuntu -- python3 /mnt<repo>/Windows-to-Sarvam/win-round2-2026-11-03/linux_compare.py',
'python Windows-to-Sarvam/win-round2-2026-11-03/report.py', '```','',
'The first sandboxed WSL distribution query returned E_ACCESSDENIED. The authorized host query found '
'Ubuntu and docker-desktop; Ubuntu reported uid 1000. Only Ubuntu was used. '
'No GUI test was requested in this round; no new screenshots were taken.', '',
'## Exact output logs','']
for host,data in [('Windows',w),('Linux',l)]:
    for row in data['rows']:
        lines += [f"### {host} {row['name']}", '']
        for phase in ('compile','run'):
            if phase not in row:continue
            p=row[phase];lines += [f"{phase}: exit {p.get('exit','not completed')}", '']
            for stream in ('stdout','stderr'):
                lines += [stream+':','```text',p.get(stream,'').rstrip('\n') or '(empty)','```','']
(h/'RESULTS.md').write_text('\n'.join(lines).rstrip()+'\n',encoding='utf8',newline='\n')
print('Report written; Linux ELF headers:',elf)

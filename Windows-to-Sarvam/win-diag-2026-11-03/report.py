import json
from pathlib import Path
h=Path(__file__).resolve().parent
d=json.loads((h/'results.json').read_text(encoding='utf8'))
root=h.parents[1]/'build/windows-v297/source'
rows={r['name']:r for r in d['rows']}
hi=rows['220_with_hindi']
assert hi['compile']['stdout']==hi['expected_stdout'] and str(hi['compile']['exit'])==hi['expected_exit']
table=[
('303_r103_parimita_refuses','HARNESS (documented unsupported Windows capability)','No refusal: prints not reached 499999500000, exit 0. Reference explicitly says Windows budgets are not checked. This is an absent feature, not a different allocation count.','Make the test conditional on platform for current documented support; implement Windows budget checking before claiming parity.'),
('317_r107_parimana','HARNESS','Every value is zero; PE codegen explicitly emits xor eax,eax. Reference and example explicitly specify Windows returns 0.','Make the test conditional on platform; do not alter Linux golden.'),
('318_r108_parimana_moves','HARNESS','Same explicit PE zero-return path as 317; not allocator rounding or a byte-count variance.','Make the test conditional on platform; implement accounting separately if Windows parity is required.'),
('322_r111_new_names','COMPILER','Exit 0xC0000005 after corrupt character output. Identical PE bytes to 323. Isolated char prints P instead of B; literal concatenation independently crashes.','Fix compiler/runtime character-buffer lifetime; resolve literal concatenation contract/codegen so accepted examples do not write read-only literals.'),
('323_r111_old_names','COMPILER','Same executable and same failures as 322; expected rename notices are on compiler stderr.','Fix the shared builtin behavior, not the alias table.'),
('288_r86_kosh_alias_moves','HARNESS (documented platform gap)','Actual alias values match the Windows behavior explicitly documented in reference section 16. Linux alone has in-place region growth.','Make the test conditional on platform; Windows region/alias parity is separate compiler work.'),
('29_nishkriya','HARNESS','Linux raw syscall bytes use syscall 60 and expect exit 42. Windows run prints the text and exits 0. Inline raw syscall is not the compiler Win32 adapter.','Make the test conditional on platform; do not execute Linux syscall fixtures as portable Windows tests.'),
('220_hindi_parse_error','HARNESS','Original harness omits --lang hindi. Explicit Hindi rerun matches the full golden exactly and exits 1 as expected.','Fix the harness language map (no golden change).'),
]
lines=['# Diagnosis of the eight v297 Windows failures','',
'Date: 2026-11-03. Diagnostic round only: no compiler, library or golden changes; no rebuild.',
'Tested source is the preserved v297 export of `1263356b6cb434871680c83c6f70a8c67eb016a3`, '
'not any newer remote changes. Existing compiler SHA-256: `'+d['compiler_sha256']+'`.', '',
'**Primary classification against the documented v297 contract: 2 COMPILER cases, 6 HARNESS cases, '
'0 unexplained output-only cases.** This does not mean Windows has Linux memory features: '
'four harness mismatches expose explicitly documented missing Windows capabilities. '
'Against the stronger cross-platform acceptance target, 303/317/318/288 remain functionality gaps.', '',
'| Test | Class (compiler / output / harness) | Evidence | Fix |','|---|---|---|---|']
lines += ['| '+' | '.join('`'+x+'`' if i==0 else x for i,x in enumerate(r))+' |' for r in table]
lines += ['', '## Shared causes', '',
'303, 317, 318 and 288 share the Linux-only arena/region implementation boundary: PE uses the ordinary allocation '
'path, no block budget enforcement, zero-return accounting, and moving kosh growth. This is one architectural '
'portability gap, but not proof that a single small fix implements all four features. 322 and 323 are the same '
'machine code and share **two** builtin problems: the character temporary’s lifetime and a write into literal '
'storage. 29 is a Linux syscall fixture; 220 is a missing harness language flag. They are independent.', '',
'## Evidence behind the classifications', '',
'- Reference lines 976–980 explicitly predict the observed Windows alias outputs. Lines 1307–1308 explicitly '
'state that parimana returns 0 on Windows. Lines 1352–1353 explicitly say a Windows block budget is not checked. '
'Example317 states the same zero-return restriction. These facts correct the earlier reports’ interpretation: '
'the observed cross-platform acceptance failures are real, but they are not newly discovered regressions '
'against the documented Windows contract.',
'- Compiler `.ge_call_parimana` emits `31 C0` (`xor eax,eax`) when `r65_active` is false. '
'`.r73_ge_scratch` falls back to ordinary `emit_nirmmita_from_rax` for PE. Zero counters and missing refusal '
'are deliberate code paths, not OS rounding. The diagnostic brief’s allocation-count hypothesis is refuted: '
'303 completes all 1,000,000 allocations and reaches the final print.',
'- Compiler `.ge_call_charfr` reserves 16 stack bytes, writes the character at rsp, returns that pointer, '
'then restores only 8 bytes. The returned pointer is therefore at rsp-8. The PE runtime call can place its '
'return address at that exact address, overwriting the character before WriteFile reads it. The isolated '
'new and old character probes both print `P` (hex 50) instead of `B` (42); the larger examples emit a '
'different invalid byte. That byte depends on the generated layout. This is a codegen/lifetime defect, '
'not a Unicode-font issue or renamed keyword issue.',
'- `.ge_call_vartcat` is an in-place strcat-style operation: it scans the first argument and emits '
'`mov [rdi],cl`. Both alias fixtures pass a literal as that destination. Literal-destination probes '
'crash with 0xC0000005, while a nirmmita buffer initialized with ab produces abcd. The fixture is exercising '
'a writable-destination contract ambiguity as well as a PE failure. Do not “fix” this by making code pages '
'writable. Clarify the API: either reject immutable destinations and change the fixture deliberately, or '
'implement allocating concatenation if that is the intended contract. The crash belongs to the compiler '
'bucket under this round’s requested crash rule; the source test misuse must also be reviewed.',
'- All three new/old pairs are byte-identical: full 322/323, isolated character conversion, and literal '
'concatenation. This directly refutes differently emitted alias-table code as the cause.',
'- The original Windows harness’s language map omits case220. Its inline-assembly exclusion scans obsolete '
'`nishkriya` but not current `yantra`, so case29 reaches execution despite the skip category.', '',
'## Corrections to the supplied diagnostic procedure', '',
'The Windows command shown with `examples\\303_*.sm` is not a reliable way to pass a source filename: '
'CMD does not expand wildcards into argv for this native compiler. All reruns used exact filenames. '
'Each subprocess had a five-second timeout. No timeout occurred. No Linux run is newly claimed.', '',
'`results.json` preserves every command as an argv array, working directory, stdout, stderr, stdout hex, '
'exit status, duration and successful binary SHA-256. `diagnose.py` and the reduced `.sm` probes reproduce '
'the work. The original eight results remain in the earlier native-cases.json. Source excerpts below '
'are copied from the pinned build tree. The test installer remains under '
'`Windows-to-Sarvam/win-v297-2026-11-03/`, not at the root path implied by the brief.', '',
'## Actual outputs and expected outputs', '']
for r in d['rows']:
    lines += ['### '+r['name'], '']
    for phase in ('compile','run'):
        if phase not in r: continue
        e=r[phase]; lines += [f"{phase}: exit {e.get('exit', 'TIMEOUT')}; {e['seconds']:.4f} seconds.", '']
        for stream in ('stdout','stderr'):
            lines += [stream+':','```text',e[stream].rstrip('\n') or '(empty)','```','']
    if 'expected_stdout' in r:
        lines += ['Expected output:', '```text',r['expected_stdout'].rstrip('\n'),'```','Expected exit: '+r['expected_exit'],'']
lines += ['## Pinned source excerpts','']
for path,start,end in [('docs/LANGUAGE-REFERENCE.md',976,980),('docs/LANGUAGE-REFERENCE.md',1307,1308),('docs/LANGUAGE-REFERENCE.md',1350,1353),('src/r65_arena.inc',111,135),('src/sutram_compiler.asm',23398,23410),('src/sutram_compiler.asm',23607,23620),('src/sutram_compiler.asm',24195,24249),('win/winrt_blob.asm',29,44)]:
    text=(root/path).read_text(encoding='utf8').splitlines()
    lines += [f'{path}:{start}–{end}', '```text', '\n'.join(f'{i+1}: {text[i]}' for i in range(start-1,end)), '```','']
(h/'DIAGNOSIS.md').write_text('\n'.join(lines).rstrip()+'\n',encoding='utf8',newline='\n')
print('Diagnosis generated; Hindi exact match and exit verified.')

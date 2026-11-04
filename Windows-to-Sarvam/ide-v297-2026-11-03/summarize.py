import collections
import hashlib
import json
from pathlib import Path

here = Path(__file__).resolve().parent
repo = here.parents[1]
root = repo / 'build/windows-v297/source'
rows = json.loads((here / 'ide-examples.json').read_text(encoding='utf8'))
expected_names = {str(p.relative_to(root / 'examples').with_suffix('')).replace('/', '\\') for p in (root / 'examples').rglob('*.sm')}
assert {r['name'] for r in rows} == expected_names, 'Incomplete example coverage'
assert len(rows) == len(expected_names), 'Duplicate rows'
for row in rows:
    name = row['name'].replace('\\', '/')
    golden = root / 'tests/expect' / (name + '.out')
    if not golden.exists():
        golden = root / 'examples' / (name + '.out')
    row['review'] = row['verdict']
    if row['verdict'] in ('MATCH', 'NO-EXPECTATION') and golden.exists():
        want = golden.read_text(encoding='utf8').replace('\r\n', '\n')
        if golden.with_suffix('.err').exists():
            want += golden.with_suffix('.err').read_text(encoding='utf8').replace('\r\n', '\n')
        got = row['output']
        is_rejection = (root / 'tests/expect' / (name + '.compile_fail')).exists()
        if is_rejection:
            row['review'] = 'DIAGNOSTIC_PREFIX_MATCH' if want and got.replace('\\', '/').startswith(want.replace('\\', '/').replace('<ROOT>/', '')) else 'DIAGNOSTIC_DIFFER'
        elif got == want:
            row['review'] = 'OUTPUT_MATCH_EXIT_UNVERIFIED'
        elif golden.with_suffix('.exit').exists() and golden.with_suffix('.exit').read_text().strip() != '0' and want and got.startswith(want) and got[len(want):].strip() == '[karyakramah asamanya-rupena samaptah]':
            row['review'] = 'EXPECTED_FAILURE_OUTPUT_MATCH_EXIT_UNVERIFIED'
        else:
            row['review'] = 'OUTPUT_DIFFER_REVIEW'
        row['golden'] = str(golden.relative_to(root))
    if row['name'] == '29_nishkriya':
        row['review'] = 'OUTPUT_MATCH_KNOWN_EXIT_MISMATCH'
(here / 'reviewed-results.json').write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding='utf8')
counts = collections.Counter(r['review'] for r in rows)
lines = ['# Windows v297: all example files through the real IDE', '',
    'Date: 2026-11-03. Source commit: `1263356b6cb434871680c83c6f70a8c67eb016a3`.', '',
    f'Coverage: **{len(rows)} of {len(expected_names)} example `.sm` files attempted**, recursively under `examples/`.',
    'This is example coverage, not every fixture under `tests/` or a full release acceptance.', '',
    'The real v297 IDE was launched and controlled through its editor, example list, language menu and Run Module command. '
    'Top-level examples were opened from the list; nested examples were pasted into the editor when absent from that list. '
    'The isolated build root was used to protect the installation and original source files. '
    'Installed IDE and compiler hashes were verified equal to these tested binaries.', '',
    '| Reviewed result | Count |', '|---|---:|']
lines += [f'| {key} | {value} |' for key, value in sorted(counts.items())]
lines += ['', '## Findings', '',
    '- `105_block_nesting_capacity`: 70,422-byte file refused by the approximately 64 KiB editor limit. '
    'The previous example remained loaded; its output must not count as execution of the refused file.',
    '- `245_r18_netsock`: socket example output differs from the Linux-oriented expected output. '
    'The example makes no network connections and listens on no interface.',
    '- `288_r86_kosh_alias_moves`: aliases do not reflect the expected shared mutations.',
    '- `303_r103_parimita_refuses`: the program reaches output instead of the expected allocation-limit rejection.',
    '- `317_r107_parimana` and `318_r108_parimana_moves`: allocation counters remain zero.',
    '- `322_r111_new_names` and `323_r111_old_names`: investigate the captured corrupt output and failure. '
    'The earlier direct native run recorded access violation `0xC0000005` for both.',
    '- `220_hindi_parse_error`: this IDE run selects Hindi and captures the expected Hindi diagnostic. '
    'The earlier native harness omitted that flag; its failure is not evidence of a Hindi compiler defect.',
    '- The IDE supplies NUL/end-of-input to Run Module. The six input examples cannot be treated as interactive-input passes.',
    '- English menu and button labels remain visible in `ide-open.png`; the interface is not wholly Sanskrit.', '',
    '## Evidence and interpretation', '',
    '`ide-examples.json` contains each raw IDE output, status line, timing, loading method and screenshot name. '
    '`transcript.txt` and `ide-examples.txt` retain the driver output and file-save guards. '
    '`reviewed-results.json` adds stricter comparisons against both central and beside-source goldens. '
    'Screenshots capture only the test IDE window.', '',
    'An output match does not establish the child exit code: this driver reads the output pane, not the child process exit. '
    'In particular, the Linux inline-syscall example `29_nishkriya` matches displayed text but the earlier native run '
    'returned 0 instead of expected 42. Compiler-rejection prefix matches are checked separately; '
    'the original driver only searched for a diagnostic keyword. Files without goldens are observations, not passes. '
    'Nested language examples use Auto detection in this sweep; failures need an explicit-pack follow-up before '
    'being assigned to the compiler. No golden or compiler source was changed.', '',
    'The owner’s install/uninstall and subjective usability acceptance, and Sarvam acknowledgment, remain separate and pending. '
    'This report is saved locally; no GitHub publication is implied.', '',
    '## Tested binary hashes', '']
for name in ('sutram-ide-gui.exe', 'win/sutram.exe'):
    lines.append(f'- `{name}`: `{hashlib.sha256((root/name).read_bytes()).hexdigest()}`')
lines += ['', '## Follow-up and additional findings', '',
    'Both save guards PASS: a refused oversized load followed by Save left the refused file unchanged, '
    'and Cancel preserved unsaved editor text when an example was selected.', '',
    'The eight nested native-script cases were rerun with explicit language selection. '
    'All eight then matched their beside-source expected output. This resolves these observations as '
    'Auto-selection limitations, not evidence that the respective language compiler is broken. '
    'The original sweep table below retains the Auto results for traceability. '
    'The follow-up also reran the other eight nested cases; raw output and screenshots are in '
    '`ide-v297-2026-11-03/explicit-packs/`.', '',
    '`r71/boundary_good` still fails to compile (parse error at line 5, `likha(pad8c(...))`), '
    'despite its beside-source expected output. `r71/boundary_bad` prints nothing and has no golden; '
    'no correctness or refusal claim is made for it.', '',
    '`215_r12_wordfreq` and `217_r12_report` differ from their beside-source goldens in blank-line '
    'formatting. The central example harness had no golden for them; the stricter review found these '
    'additional comparisons. Actual output is retained.', '',
    'The comparison accounts for expected stderr merged into the IDE output pane and the IDE’s '
    'abnormal-termination note for expected nonzero exits. Module diagnostics normalize path separators '
    'and the `<ROOT>/` prefix. These display differences are not counted as compiler defects.', '',
    '### Explicit-pack follow-up', '', '| Example | Language | Output comparison |', '|---|---|---|']
followup = json.loads((here / 'explicit-packs/ide-examples.json').read_text(encoding='utf8'))
for r in followup:
    if r['language'] == 'auto':
        continue
    p = root / 'examples' / (r['name'].replace('\\', '/') + '.out')
    match = p.exists() and p.read_text(encoding='utf8') == r['output']
    assert match, 'Explicit-pack follow-up needs review: ' + r['name']
    lines.append(f"| `{r['name']}` | {r['language']} | MATCH (exit unverified) |")
lines += ['', '## Every case', '', '| Example | Reviewed result | ms | Evidence |', '|---|---|---:|---|']
for r in rows:
    shot = f"[screenshot](ide-v297-2026-11-03/{r['screenshot']})" if r['screenshot'] else 'JSON output'
    lines.append(f"| `{r['name']}` | {r['review']} | {r['ms']} | {shot} |")
(here.parent / 'WIN-IDE-V297-2026-11-03.md').write_text('\n'.join(lines)+'\n', encoding='utf8')
print(json.dumps(counts, indent=2))

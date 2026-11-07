"""Focused checks for inconclusive B3/B7 probes and the suite's missing-library failure."""
import ast, json, shutil
from verify import HERE, ROOT, WORK, EXE, check_identity, digest, run, save

check_identity()
module = ast.parse((ROOT / 'tests/r127/test_descriptor.py').read_text(encoding='utf8'))
rows = []
for node in ast.walk(module):
    if not (isinstance(node, ast.Tuple) and node.elts and isinstance(node.elts[0], ast.Constant)):
        continue
    name = node.elts[0].value
    if name == 'no memory to grow a kosh: a message':
        case = ast.literal_eval(node)
        path = HERE / 'B3-forced-oom.sm'
        path.write_text(case[1], encoding='utf8', newline='\n')
        target = WORK / 'B3-forced-oom.exe'
        c = run([str(EXE), *case[2], str(path), str(target)], cwd=ROOT)
        row = {'test': 'B3-forced-oom', 'description': name, 'compile': c,
               'expected_stdout': case[4], 'expected_exit': case[5]}
        if c['exit'] == 0: row['run'] = run([str(target)])
        rows.append(row)
    elif isinstance(name, str) and 'beside a growth that moves its region (R204 S1' in name:
        case = ast.literal_eval(node)
        path = HERE / 'B7-S1-refusal.sm'
        path.write_text(case[1], encoding='utf8', newline='\n')
        target = WORK / 'B7-S1-refusal.exe'
        c = run([str(EXE), str(path), str(target)], cwd=ROOT)
        rows.append({'test': 'B7-S1-refusal', 'description': name, 'compile': c,
                     'output_exists': target.exists(), 'expected': 'E_KOSH_VIBHAG, exit 1, no output executable'})
assert len(rows) == 2

# Keep the raw suite unchanged. Compare the one failed import test with complete
# compiler-relative libraries in a throwaway bundle and the identical compiler bytes.
bundle = WORK / 'bundle'
bundle.mkdir(exist_ok=True)
shutil.copy2(EXE, bundle / 'sutram.exe')
shutil.copytree(ROOT / 'lib', bundle / 'lib', dirs_exist_ok=True)
assert digest(bundle / 'sutram.exe') == digest(EXE)
manifest = {str(p.relative_to(ROOT / 'lib')): digest(p) for p in (ROOT / 'lib').rglob('*') if p.is_file()}
assert all(digest(bundle / 'lib' / rel) == sha for rel, sha in manifest.items())
save('bundle-manifest.json', {'compiler_sha256': digest(EXE), 'libraries': manifest})
source = ROOT / 'examples/79_ayojan_cwd.sm'
for label, exe, cwd in [('original-repo-cwd', EXE, ROOT),
                        ('complete-bundle-unrelated-cwd', bundle / 'sutram.exe', WORK)]:
    target = WORK / (label + '.exe')
    c = run([str(exe), str(source), str(target)], cwd=cwd)
    row = {'test': '79_ayojan_cwd-' + label, 'compiler_sha256': digest(exe), 'compile': c}
    if c['exit'] == 0: row['run'] = run([str(target)])
    rows.append(row)
save('followups.json', rows)
for row in rows: print(json.dumps(row), flush=True)

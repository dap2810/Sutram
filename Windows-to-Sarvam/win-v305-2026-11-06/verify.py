"""Report-only native v305 verification. No product sources or goldens changed."""
from pathlib import Path
import ast, ctypes, hashlib, json, os, re, subprocess, sys, time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXE = ROOT / 'win/sutram.exe'
WORK = ROOT / 'build/windows-v305-2026-11-06'
WORK.mkdir(parents=True, exist_ok=True)
ctypes.windll.kernel32.SetErrorMode(0x8003)

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=True) + '\n', encoding='utf8')

def run(cmd, cwd=WORK, timeout=30):
    start = time.perf_counter()
    row = {'command': list(map(str, cmd)), 'cwd': str(cwd), 'timeout_seconds': timeout}
    try:
        p = subprocess.run(cmd, cwd=cwd, input=b'', capture_output=True, timeout=timeout,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        row.update(exit=p.returncode, stdout=p.stdout.decode('utf8', 'replace'),
                   stderr=p.stderr.decode('utf8', 'replace'), timed_out=False)
    except subprocess.TimeoutExpired as e:
        row.update(exit=None, stdout=(e.stdout or b'').decode('utf8', 'replace'),
                   stderr=(e.stderr or b'').decode('utf8', 'replace'), timed_out=True)
    row['elapsed_seconds'] = round(time.perf_counter() - start, 4)
    return row

def identity():
    after = json.loads((HERE / 'environment-after.json').read_text(encoding='utf8'))
    assert len(after['executables']) == 1 and not after['old_folder_exists'], 'Cleanup gate failed'
    version = run([str(EXE), '--version'])
    data = {'compiler_path': str(EXE), 'compiler_sha256': digest(EXE),
            'ide_sha256': digest(ROOT / 'sutram-ide-gui.exe'),
            'source_sha256': digest(ROOT / 'src/sutram_compiler.asm'),
            'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
            'fetched_main': subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=ROOT).decode().strip(),
            'windows': sys.getwindowsversion().platform_version, 'version': version}
    data['pass'] = version['exit'] == 0 and version['stdout'].splitlines()[0] == 'Sutram 1.0 (v305) - sampurna sutra'
    save('identity.json', data)
    print(json.dumps(data, indent=2), flush=True)
    return data['pass']

def check_identity():
    data = json.loads((HERE / 'identity.json').read_text())
    assert data['pass'] and digest(EXE) == data['compiler_sha256'], 'Compiler identity changed'

def probes():
    check_identity()
    request = (HERE / 'REQUEST.md').read_text(encoding='utf8')
    cases = [(name, src, None) for name, src in re.findall(r'### (B[1-8])[^\n]*\n.*?```sutram\n(.*?)```', request, re.S)]
    assert len(cases) == 8
    # Supplement the handoff's slice spelling with the exact repository v305 regressions.
    module = ast.parse((ROOT / 'tests/r127/test_descriptor.py').read_text(encoding='utf8'))
    selected = [ast.literal_eval(n) for n in ast.walk(module)
                if isinstance(n, ast.Tuple) and n.elts and isinstance(n.elts[0], ast.Constant)
                and isinstance(n.elts[0].value, str) and n.elts[0].value.startswith('k[lo:]')]
    assert len(selected) == 3
    for i, c in enumerate(selected, 1):
        cases.append((f'B7-S2-{i}', c[1], {'description': c[0], 'stdout': c[4], 'exit': c[5]}))
    cases.append(('B7-colon', dict((n,s) for n,s,_ in cases)['B7'].replace('k[1 tak]', 'k[1:]'), None))
    cases.append(('B8-lowercase', dict((n,s) for n,s,_ in cases)['B8'].replace('(66)', '(97)'), None))
    cases.append(('B8-concat', 'mukhya() {\n    vitti s = "ab"\n    vitti t = "cd"\n    vitti u = vartani_sandhi(s, t)\n    shabda(u)\n    likha("orig: ", s)\n}\n', None))
    rows = []
    for name, source, expected in cases:
        path = HERE / (name + '.sm')
        path.write_text(source, encoding='utf8', newline='\n')
        target = WORK / (name + '.exe')
        c = run([str(EXE), str(path), str(target)], cwd=ROOT)
        row = {'test': name, 'source_sha256': digest(path), 'compile': c}
        if expected:
            row['repository_expectation'] = expected
        if c['exit'] == 0:
            row['run'] = run([str(target)], timeout=60 if name == 'B3' else 30)
        rows.append(row)
        save('probes.json', rows)
        print(json.dumps(row), flush=True)

def suite():
    check_identity()
    script = ROOT / 'tools/test_windows_native.py'
    source = script.read_text(encoding='utf8')
    old = "out=ROOT/'build/windows/acceptance'"
    assert source.count(old) == 1
    source = source.replace(old, 'out=Path(' + repr(str(WORK / 'suite')) + ')')
    os.environ['SUTRAM_EVIDENCE'] = str(HERE)
    save('suite-harness.json', {'original': str(script), 'sha256': digest(script),
                              'only_override': {'before': old, 'after': str(WORK / 'suite')},
                              'compiler_sha256': digest(EXE)})
    start = time.perf_counter()
    code = 0
    try:
        exec(compile(source, str(script), 'exec'), {'__file__': str(script), '__name__': '__main__'})
    except SystemExit as e:
        code = int(e.code or 0)
    rows = json.loads((HERE / 'native-cases.json').read_text())
    save('suite-summary.json', {'exit': code, 'elapsed_seconds': round(time.perf_counter()-start,3),
         'counts': {s: sum(r['status']==s for r in rows) for s in sorted({r['status'] for r in rows})},
         'failures': [r['case'] for r in rows if r['status'] in ('FAIL','COMPILE_FAIL','TIMEOUT')]})
    return code

if __name__ == '__main__':
    if sys.argv[1] == 'identity': sys.exit(0 if identity() else 1)
    if sys.argv[1] == 'probes': probes()
    if sys.argv[1] == 'suite': sys.exit(suite())

"""Native evidence only. Never modifies compiler, library, examples, or goldens."""
from pathlib import Path
import ctypes, hashlib, json, os, re, subprocess, sys, time, winreg

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1] / 'build/windows-v303-review'
INSTALL = Path(os.environ['LOCALAPPDATA']) / 'Programs/Sutram'
EXE = INSTALL / 'bin/sutram.exe'
WORK = ROOT / 'build/v303-probes'
WORK.mkdir(parents=True, exist_ok=True)
ctypes.windll.kernel32.SetErrorMode(0x8003)

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(cmd, cwd=WORK, env=None, timeout=30):
    start = time.perf_counter()
    row = {'command': list(map(str, cmd)), 'cwd': str(cwd), 'timeout_seconds': timeout}
    try:
        p = subprocess.run(cmd, cwd=cwd, env=env, input=b'', capture_output=True,
                           timeout=timeout, creationflags=subprocess.CREATE_NO_WINDOW)
        row.update(exit=p.returncode, stdout=p.stdout.decode('utf8', 'replace'),
                   stderr=p.stderr.decode('utf8', 'replace'), timed_out=False)
    except subprocess.TimeoutExpired as e:
        row.update(exit=None, stdout=(e.stdout or b'').decode('utf8', 'replace'),
                   stderr=(e.stderr or b'').decode('utf8', 'replace'), timed_out=True)
    row['elapsed_seconds'] = round(time.perf_counter() - start, 4)
    return row

def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=True) + '\n', encoding='utf8')

def identity():
    env = os.environ.copy()
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                       r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment') as key:
        machine = winreg.QueryValueEx(key, 'Path')[0]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment') as key:
        user = winreg.QueryValueEx(key, 'Path')[0]
    env['PATH'] = os.path.expandvars(machine + ';' + user)
    direct = run([str(EXE), '--version'])
    fresh = run([os.environ['COMSPEC'], '/d', '/c', 'where sutram && sutram --version'], env=env)
    data = {'installed_path': str(EXE), 'installed_sha256': digest(EXE),
            'source_sha256': digest(ROOT / 'win/sutram.exe'),
            'installer_sha256': digest(ROOT / 'Sutram-Setup.exe'),
            'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
            'windows': sys.getwindowsversion().platform_version, 'direct': direct, 'fresh_cmd': fresh,
            'shell_method': 'New cmd.exe /d /c with PATH reconstructed from machine/user registry; captured pipes, not an interactive console.'}
    data['pass'] = (direct['exit'] == 0 and direct['stdout'].splitlines()[0] == 'Sutram 1.0 (v303) - sampurna sutra'
                    and fresh['exit'] == 0 and 'Sutram 1.0 (v303) - sampurna sutra' in fresh['stdout']
                    and data['installed_sha256'] == data['source_sha256'])
    save('identity.json', data)
    print(json.dumps(data, indent=2), flush=True)
    return data['pass']

def probes():
    assert json.loads((HERE / 'identity.json').read_text())['pass'], 'Version gate failed'
    request = (HERE / 'REQUEST.md').read_text(encoding='utf8')
    cases = re.findall(r'### Test (M\d|D\d)[^\n]*\n.*?```sutram\n(.*?)```', request, re.S)
    cases.append(('D1a', dict(cases)['D1'].replace('(66)', '(97)')))
    rows = []
    for name, source in cases:
        path = HERE / (name + '.sm')
        path.write_text(source, encoding='utf8', newline='\n')
        target = WORK / (name + '.exe')
        c = run([str(EXE), str(path), str(target)], cwd=ROOT)
        row = {'test': name, 'source_sha256': digest(path), 'compile': c}
        if c['exit'] == 0:
            row['run'] = run([str(target)])
        rows.append(row)
        save('probes.json', rows)
        print(json.dumps(row), flush=True)

def suite():
    assert json.loads((HERE / 'identity.json').read_text())['pass'], 'Version gate failed'
    # Execute the pinned repository harness unchanged except the compiler path,
    # so this suite measures the INSTALLED compiler, not an unrelated build.
    script = ROOT / 'tools/test_windows_native.py'
    source = script.read_text(encoding='utf8')
    old = "exe=ROOT/'win/sutram.exe'"
    assert source.count(old) == 1
    source = source.replace(old, 'exe=Path(' + repr(str(EXE)) + ')')
    os.environ['SUTRAM_EVIDENCE'] = str(HERE)
    save('suite-harness.json', {'original': str(script), 'sha256': digest(script),
                              'only_override': {'before': old, 'after': 'installed bin/sutram.exe'},
                              'installed_sha256': digest(EXE)})
    exec(compile(source, str(script), 'exec'), {'__file__': str(script), '__name__': '__main__'})

if __name__ == '__main__':
    if sys.argv[1] == 'identity':
        sys.exit(0 if identity() else 1)
    elif sys.argv[1] == 'probes':
        probes()
    elif sys.argv[1] == 'suite':
        suite()

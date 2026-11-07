#!/usr/bin/env python3
"""R130: install with the real engine, then open a new terminal and ask it which Sutram it runs. Windows only.

The gate the v303 release candidate lacked: an install that runs to completion, and a new terminal that resolves
bare `sutram` to the installed compiler and prints this version. It runs the install engine the wizard runs
(install-core.ps1, with the wizard's own PowerShell flags) on the payload of the tree's Sutram-Setup.exe, with
-AddPath, into %LOCALAPPDATA%\\Programs\\Sutram, then checks:

  0. (R133-R134) an installation stopped at file 132 - the engine killed as soon as its log says START 132/, as the
     v303 copy stopped - leaves its journal (<folder>.sutram-transaction); a file the user then changes is refused and
     kept; and the next run finishes the installation rather than refusing it;
  1. the engine exits 0 within 15 minutes and its log ends with 'Installation complete', with no pending record or
     unfinished '*.sutram-partial' copy left;
  2. a new `cmd.exe /d /c "where sutram & sutram --version"`, with PATH rebuilt from the registry (machine, then user)
     and a working folder without Sutram, finds the installed bin\\sutram.exe FIRST and prints the tree's version;
  3. uninstall (uninstall-core.ps1) exits 0 and removes the PATH entry.

It changes this user's installation, PATH and registry - like the wizard does - so it runs only when asked:
    python tests/windows/test_installer_e2e.py --i-understand-this-installs
It refuses if Sutram is already installed. Prints NOT RUN off Windows. Last line: "installer e2e: N checks, M failed".
"""
import os, subprocess, sys, tempfile, time, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PS = ['powershell.exe', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File']


def fresh_path():
    import winreg  # Windows only
    vals = []
    for hive, sub in ((winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'),
                      (winreg.HKEY_CURRENT_USER, 'Environment')):
        try:
            with winreg.OpenKey(hive, sub) as k:
                v, _ = winreg.QueryValueEx(k, 'Path')
                vals.append(os.path.expandvars(v))
        except OSError:
            pass
    return ';'.join(vals)


def main():
    checks = fails = 0

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    if '--i-understand-this-installs' not in sys.argv:
        print('NOT RUN  pass --i-understand-this-installs: this installs Sutram for this user and changes PATH')
        print('installer e2e: 0 checks, 0 failed')
        return 0
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    from check_installer_version import embedded_payload
    install_dir = os.path.join(os.environ['LOCALAPPDATA'], 'Programs', 'Sutram')
    if os.path.exists(os.path.join(install_dir, '.sutram-install')):
        print(f'NOT RUN  Sutram is already installed at {install_dir}; uninstall it first')
        print('installer e2e: 0 checks, 0 failed')
        return 1
    want = subprocess.run([os.path.join(ROOT, 'win', 'sutram.exe'), '--version'], capture_output=True, text=True).stdout.strip()
    work = tempfile.mkdtemp(prefix='sutram-e2e-')
    zp = os.path.join(work, 'payload.zip')
    z = embedded_payload(open(os.path.join(ROOT, 'Sutram-Setup.exe'), 'rb').read())
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as out:
        for n in z.namelist():
            out.writestr(n, z.read(n))
    ni = os.path.join(ROOT, 'windows', 'native-installer')

    def engine(log):
        return PS + [os.path.join(ni, 'install-core.ps1'), '-PayloadZip', zp, '-InstallDir', install_dir,
                     '-SetupExePath', os.path.join(ROOT, 'Sutram-Setup.exe'), '-LogPath', log, '-AddPath']

    # R133: stop an installation where v303's stopped - in file 132 - then run it again.
    stop_log = os.path.join(work, 'install-stopped.log')
    p = subprocess.Popen(engine(stop_log), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0, seen = time.time(), False
    while time.time() - t0 < 600 and p.poll() is None:
        if os.path.exists(stop_log) and 'START 132/' in open(stop_log, encoding='utf-8-sig', errors='replace').read():
            seen = True
            break
        time.sleep(0.05)
    subprocess.run(['taskkill', '/F', '/T', '/PID', str(p.pid)], capture_output=True)
    p.wait(timeout=60)
    check(seen, 'an installation is stopped while its log names file 132')
    check(os.path.exists(os.path.join(install_dir + '.sutram-transaction', 'journal.txt')),
          'the stopped installation left its journal beside the folder (R134)')
    # R134: a user's own file where the payload would put one is preserved, not overwritten: expect a refusal that
    # names it and changes nothing; then remove it and let the next run finish.
    users = os.path.join(install_dir, 'README.md')
    os.makedirs(install_dir, exist_ok=True)
    open(users, 'w', encoding='utf-8').write('my own notes\n')
    rr = subprocess.run(engine(os.path.join(work, 'install-conflict.log')), capture_output=True, text=True, timeout=900)
    ctext = open(os.path.join(work, 'install-conflict.log'), encoding='utf-8-sig', errors='replace').read()
    check(rr.returncode != 0 and 'preserved' in ctext and open(users, encoding='utf-8').read() == 'my own notes\n',
          'a user file at a payload path is refused, named and left as it was')
    os.remove(users)
    log = os.path.join(work, 'install.log')
    t0 = time.time()
    try:
        r = subprocess.run(engine(log), capture_output=True, text=True, timeout=900)
        code = r.returncode
    except subprocess.TimeoutExpired:
        code = 'timeout'
    text = open(log, encoding='utf-8-sig').read() if os.path.exists(log) else ''
    check(code == 0, f'the next run finishes it: the engine exits 0 ({code}) in {time.time() - t0:.0f} s')
    check('Installation complete' in text, 'its log records the completion; last line: ' + (text.strip().split('\n') or [''])[-1])
    left = [os.path.join(d, f) for d, _, fs in os.walk(install_dir) for f in fs
            if f.endswith('.sutram-partial') or f == 'payload.pending.sha256']
    left += [install_dir + '.sutram-transaction'] if os.path.exists(install_dir + '.sutram-transaction') else []
    check(not left, f'no pending record or unfinished copy is left ({left[:3]})')
    env = dict(os.environ, PATH=fresh_path())
    w = subprocess.run(['cmd.exe', '/d', '/c', 'where sutram & sutram --version'], capture_output=True, text=True,
                       env=env, cwd=work, timeout=30)
    lines = [l.strip() for l in w.stdout.splitlines() if l.strip()]
    first = lines[0] if lines else ''
    check(os.path.normcase(first) == os.path.normcase(os.path.join(install_dir, 'bin', 'sutram.exe')),
          f'a new terminal finds the installed compiler first ({first!r})')
    check(want.split('\n')[0] in w.stdout, f'and it reports {want.splitlines()[0]!r}')
    u = subprocess.run(PS + [os.path.join(ni, 'uninstall-core.ps1'), '-InstallDir', install_dir,
                             '-SelfPath', os.path.join(install_dir, 'Sutram-Uninstall.exe'),
                             '-LogPath', os.path.join(work, 'uninstall.log')], capture_output=True, text=True, timeout=600)
    check(u.returncode == 0, f'uninstall exits 0 ({u.returncode})')
    check(os.path.join(install_dir, 'bin').lower() not in fresh_path().lower(), 'and the PATH entry is gone')
    print(f'installer e2e: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    if os.name != 'nt':
        print('NOT RUN: native Windows required')
        print('installer e2e: 0 checks, 0 failed')
        sys.exit(0)
    sys.exit(main())

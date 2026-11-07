#!/usr/bin/env python3
"""R130: the installer engine runs to completion and a new terminal runs the installed compiler - what can be
checked on Linux, from the sources and the built Sutram-Setup.exe.

The Windows round of v303 found the engine stopped after 'Copying Sutram files.' with PowerShell left open, and a
new terminal running an older Sutram that was still on PATH. On Windows, tests/windows/test_installer_e2e.py installs
and checks a new terminal; here, the properties that make those outcomes impossible are checked statically:

  * the wizard starts the engine with -NonInteractive -ExecutionPolicy Bypass and no console window, and waits for
    it at most ENGINE_WAIT_MS (stopping it after), never INFINITE;
  * the engine turns off progress bars and confirmations, has no Read-Host or prompt, copies file by file with a
    log line every 100 files, refuses while another Sutram is installed (Find-OtherSutram, before any change), and
    with -AddPath checks a new terminal: the first sutram.exe on the fresh PATH is this one and reports this version;
  * Sutram-Setup.exe embeds exactly these install-core.ps1 and uninstall-core.ps1 bytes.
Last line: "r130 installer engine: N checks, M failed".
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NI = os.path.join(ROOT, 'windows', 'native-installer')


def main():
    checks = fails = 0

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    wiz = open(os.path.join(NI, 'sutram_wizard.asm'), encoding='utf-8').read()
    eng = open(os.path.join(NI, 'install-core.ps1'), encoding='utf-8').read()
    for label in ('ps_prefix', 'ps_uninst'):
        m = re.search(label + r':\s+u16 "([^"]*)"', wiz)
        check(m and '-NonInteractive' in m.group(1) and '-ExecutionPolicy Bypass' in m.group(1),
              f'the wizard starts PowerShell non-interactive, execution policy Bypass ({label}: {m.group(1) if m else None!r})')
    a = wiz.find('; build the PowerShell command line')
    b = wiz.find('.engine_code:', a)
    launch = wiz[a:b] if 0 <= a < b else wiz  # an older wizard: search all of it
    check('mov  qword [rsp+40], CREATE_NO_WINDOW' in launch, 'the install engine has no console window (CREATE_NO_WINDOW)')
    check('mov  edx, ENGINE_WAIT_MS' in launch and 'INFINITE' not in launch,
          'the wizard waits for the engine at most ENGINE_WAIT_MS, never INFINITE')
    check('API  TerminateProcess' in launch, 'an engine still running at the limit is stopped (TerminateProcess) and setup fails')
    m = re.search(r'%define ENGINE_WAIT_MS\s+(\d+)', wiz)
    check(m and 60000 <= int(m.group(1)) <= 3600000, f'the limit is between 1 and 60 minutes ({m.group(1) if m else None} ms)')
    check("$ProgressPreference = 'SilentlyContinue'" in eng and "$ConfirmPreference = 'None'" in eng,
          'the engine turns off progress bars and confirmations')
    code = re.sub(r'(?m)#.*$', '', eng)
    check(not re.search(r'Read-Host|PromptForChoice|\$host\.UI|Pause\b|-Wait\b', code), 'the engine never waits for input')
    check('Copy-StagedFiles $stage $InstallDir' in eng and "Copy-Item -Path (Join-Path $stage '*')" not in eng,
          'the payload is copied file by file, logged every 100 files')
    i_other, i_stage = eng.find('Find-OtherSutram (Join-Path $InstallDir'), eng.find("$stage = Join-Path $env:TEMP")
    check(0 < i_other < i_stage, 'another Sutram installation is refused before anything is changed')
    check("'Sutram\\bin\\sutram.exe'" in eng, 'the older installers\' folder (%LOCALAPPDATA%\\Sutram) is looked at')
    i_path, i_fresh = eng.find('Set-UserPathEntry $binDir $true'), eng.find('$fresh = Invoke-FreshShellVersion')
    check(0 < i_path < i_fresh, 'with -AddPath, a new terminal is checked after PATH is written')
    check("'/d /c sutram --version'" in eng and '$fresh.Trim() -ne $check.Trim()' in eng,
          'the new terminal must report the installed compiler\'s version')
    check(re.search(r"Log \('Installation complete: ' \+ \$InstallDir\)", eng) is not None, 'the engine logs its completion')
    setup = os.path.join(ROOT, 'Sutram-Setup.exe')
    if os.path.exists(setup):
        b = open(setup, 'rb').read()
        for f in ('install-core.ps1', 'uninstall-core.ps1'):
            check(open(os.path.join(NI, f), 'rb').read() in b, f'Sutram-Setup.exe embeds this {f}')
    else:
        print('NOT RUN  Sutram-Setup.exe is not in the tree')
    print(f'r130 installer engine: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())

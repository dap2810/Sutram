#!/usr/bin/env python3
"""R133: an installation that stops part-way is finished by the next run, not refused - checked on Linux, from the
install engine's source and the built Sutram-Setup.exe.

The v303 copy stopped inside file 132 of 657 (an empty docs/rounds/PROJECT-OVERVIEW.md) after the engine had deleted
the previous payload's 643 files. The folder then held this installer's own files under the previous manifest, and
every later run refused: 'Upgrade would overwrite a user file ... sutram-link.exe'. The log said only 'Copying Sutram
files.'. What makes that impossible, statically:

  * the first change to the folder is payload.pending.sha256 (the payload being installed), removed only when the
    installation is complete; with it present, a non-empty folder, incomplete metadata and files that match the
    pending manifest are the installer's own;
  * the ownership check accepts a file matching the previous manifest, the pending one, or the new payload;
  * the copy names each file in the log before copying it, writes it as '<name>.sutram-partial' and then moves it
    into place, and does not copy the manifest (written after the copy); leftovers are removed on the next run;
  * the new files overwrite the old in place, and only files the new payload no longer has are deleted, after the
    copy (no mass delete first);
  * the uninstaller removes a pending installation's files too;
  * Windows is told the compiler's version, not '0.1.0';
  * Sutram-Setup.exe embeds exactly these scripts.
On Windows, tests/windows/test_installer_e2e.py stops an installation at file 132 and runs it again.
Last line: "r133 interrupted install: N checks, M failed".
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NI = os.path.join(ROOT, 'windows', 'native-installer')


def func(src, name):
    i = src.find('function ' + name)
    if i < 0:
        return ''
    j = src.find('\nfunction ', i + 1)
    return src[i:j if j > 0 else len(src)]


def main():
    checks = fails = 0

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    eng = open(os.path.join(NI, 'install-core.ps1'), encoding='utf-8-sig').read()
    uni = open(os.path.join(NI, 'uninstall-core.ps1'), encoding='utf-8-sig').read()
    code = re.sub(r'(?m)#.*$', '', eng)
    cp = re.sub(r'(?m)#.*$', '', func(eng, 'Copy-StagedFiles'))
    i_log, i_copy = cp.find("Log ('Copying ' + $n + '/'"), cp.find('[IO.File]::Copy(')
    check(0 < i_log < i_copy, 'the copy names each file in the log before copying it')
    check("$part = $dst + '.sutram-partial'" in cp and '[IO.File]::Copy($src,$part,$true)' in cp
          and '[IO.File]::Move($part,$dst)' in cp, 'each file is copied as <name>.sutram-partial, then moved into place')
    check("'payload.manifest.sha256'" in cp, 'the copy leaves out the payload manifest')
    body = code[code.find('try {', code.find("$InstallDir = [IO.Path]::GetFullPath")):]
    i_dir = body.find('New-Item -ItemType Directory -Force -Path $InstallDir')
    i_pend = body.find("[IO.File]::Copy((Join-Path $stage 'payload.manifest.sha256'),$pendingPath,$true)")
    i_cs = body.find('Copy-StagedFiles $stage $InstallDir')
    i_rm = body.find('Remove-ManifestFiles $InstallDir $previousManifest $newFiles')
    i_man = body.find("[IO.File]::Copy((Join-Path $stage 'payload.manifest.sha256'),$previousManifest,$true)")
    check(0 < i_dir < i_pend < i_cs, 'payload.pending.sha256 is the first change to the folder, before any file is copied')
    check(body.count('Remove-ManifestFiles') == 2 and i_cs < i_rm < i_man,
          'the previous payload is not deleted first: obsolete files only, after the copy, then the manifest')
    check('[hashtable]$Keep' in func(eng, 'Remove-ManifestFiles') and 'if ($Keep.ContainsKey($rel)) { continue }' in eng,
          'files the new payload still has are overwritten, not deleted')
    i_state = body.find('[IO.File]::WriteAllLines($statePath')
    i_unpend = body.find('Remove-Item -LiteralPath $pendingPath -Force')
    i_done = body.find("Log ('Installation complete: ' + $InstallDir)")
    check(0 < i_state < i_unpend < i_done, 'the pending record is removed only when everything else is written')
    check('-not (Test-SutramMarker $marker) -and -not $pending) { throw "The selected folder is not empty' in code,
          'a folder holding a stopped installation is not refused as "not empty"')
    check('if ((Test-SutramMarker $marker) -and -not $pending) {' in code,
          'half-written metadata of a stopped installation is not refused as incomplete or modified')
    own = body[body.find('$ours ='):body.find('if (-not $ours)')]
    check('$previousFiles' in own and '$pendingFiles' in own and '$newFiles' in own,
          'a file is the installer\'s own if it matches the previous manifest, the pending one or the new payload')
    check("GetFiles($InstallDir,'*.sutram-partial'" in code and '[IO.File]::Delete($part)' in code,
          'unfinished copies left by a stopped installation are removed on the next run')
    check('Remove-ManifestFiles $InstallDir $earlierPending $newFiles' in body,
          'files a stopped installation wrote that this payload does not have are removed')
    ucode = re.sub(r'(?m)#.*$', '', uni)
    check("Remove-ManifestFiles $InstallDir (Join-Path $InstallDir 'payload.pending.sha256')" in ucode
          and "'*.sutram-partial'" in ucode, 'uninstall removes a stopped installation\'s files and unfinished copies')
    check("'0.1.0'" not in code and "$displayVersion = $Matches[1] + '.' + $Matches[2]" in code,
          'Windows is told the compiler\'s version (Sutram 1.0 (v306) -> 1.0.306), not 0.1.0')
    setup = os.path.join(ROOT, 'Sutram-Setup.exe')
    if os.path.exists(setup):
        b = open(setup, 'rb').read()
        for f in ('install-core.ps1', 'uninstall-core.ps1'):
            check(open(os.path.join(NI, f), 'rb').read() in b, f'Sutram-Setup.exe embeds this {f}')
    else:
        print('NOT RUN  Sutram-Setup.exe is not in the tree')
    print(f'r133 interrupted install: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())

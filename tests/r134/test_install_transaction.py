#!/usr/bin/env python3
"""R134-R135: the installer's transaction - checked on Linux from the engine's source, the wizard's source and the
built Sutram-Setup.exe. (Replaces R133's interrupted-install gate: v307's pending manifest plus '.sutram-partial'
copies are now one journaled transaction, as ChatGPT R207 WS3 laid out.)

The v303 copy stopped inside file 132 of 657 and left it empty; the v306 same-folder upgrade stopped after file
~117 with every thread of the engine and of the wizard suspended (native, 6 November). Both runs had deleted the
previous payload first and were writing the new one into the target. What makes a stop recoverable, statically:

  * a private folder beside the target, on the same volume (<target>.sutram-transaction), holds the journal, the
    staged files and the backups; one installer at a time holds its lock;
  * the journal is written with write-through and flushed (durable) and its BEGIN comes before any change to the
    target; the pending hint in the target comes after BEGIN;
  * every file is staged in the transaction folder (logged START before the copy and DONE after it), verified by
    hash, and reaches the target by a rename; a replaced file is journaled (BACKUP) and moved to the backup before
    the new one is renamed in (PUBLISH, PUBLISHED); files the new payload lacks go to the backup (OBSOLETE);
  * a rerun reads the journal: what it STAGED or PUBLISHED is the installer's own; a file matching none of the
    previous manifest, the pending one, the new payload or the journal is preserved, all such files are listed
    with a way out (move them, or the folder, aside), and nothing changes;
  * COMMITTED is journaled after the state is written, the pending hint is removed after it, and the committed
    transaction folder is removed idempotently (a rerun finding a committed journal only cleans up);
  * the uninstaller leaves an uncommitted transaction's backups and says where they are;
  * the wizard appends a line to the engine log when its 15-minute stop fires (R135 WS4);
  * Windows is told the compiler's version; (R136) the logs are appended with full sharing and a failed log line
    never stops the run (Add-Content failed while a reader held the log, ChatGPT's v307 fixture);
  * Sutram-Setup.exe embeds exactly these scripts.
On Windows, tests/windows/test_installer_e2e.py stops an installation while it stages file 132 and runs it again.
Last line: "r134 install transaction: N checks, M failed".
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
    wiz = open(os.path.join(NI, 'sutram_wizard.asm'), encoding='utf-8').read()
    code = re.sub(r'(?m)#.*$', '', eng)
    body = code[code.find('try {', code.find("$InstallDir = [IO.Path]::GetFullPath")):]

    check("+ '.sutram-transaction')" in code and 'GetDirectoryName($InstallDir)' in code,
          'the transaction folder is beside the target (same volume): <target>.sutram-transaction')
    wd = func(code, 'Write-Durable')
    check('[IO.FileOptions]::WriteThrough' in wd and '$fs.Flush($true)' in wd, 'the journal is written through and flushed')
    i_begin = body.find('Journal ("BEGIN`t"')
    i_hint = body.find("[IO.File]::Copy((Join-Path $stage 'payload.manifest.sha256'),$pendingPath,$true)")
    i_stage = body.find('Stage-Payload $stage $txnStage $newFiles')
    i_pub = body.find('Move-Into $staged $target')
    check(0 < i_begin < i_hint < i_stage < i_pub, 'BEGIN is journaled before the pending hint, the staging and any change to the target')
    check('[IO.FileShare]::None' in body and "Another Sutram installer is working on" in body,
          'one installer at a time: the transaction folder is locked')
    sp = func(code, 'Stage-Payload')
    i_s, i_c, i_v, i_d = (sp.find("Log ('START "), sp.find('[IO.File]::Copy($src,$part,$true)'),
                          sp.find("(Get-Sha $part) -ne $NewFiles[$rel]"), sp.find("Log ('DONE  "))
    check(0 < i_s < i_c < i_v < i_d, 'each file is logged START before its copy and DONE after it, verified by hash between')
    check('Journal ("STAGED`t"' in sp, 'a staged file is journaled')
    pub = body[body.find("Log ('Publishing "):body.find('Log \'Writing the payload manifest.\'')]
    i_bj, i_bm = pub.find('Journal ("BACKUP`t"'), pub.find('Move-Into $target $bk')
    i_pj, i_mv, i_pd = pub.find('Journal ("PUBLISH`t"'), pub.find('Move-Into $staged $target'), pub.find('Journal ("PUBLISHED`t"', pub.find('Move-Into $staged $target'))
    check(0 < i_bj < i_bm and 0 < i_pj < i_mv < i_pd, 'a replaced file is journaled and backed up before the new one is renamed in, then PUBLISHED')
    check('[IO.File]::Move($From,$To)' in func(code, 'Move-Into') and 'Copy-StagedFiles' not in code
          and 'Remove-ManifestFiles $InstallDir $previousManifest' not in code,
          'files reach the target by rename only; the previous payload is not deleted first')
    check('Journal ("OBSOLETE`t"' in body and 'Move-Into $target (Join-Path $txnBackup $rel)' in body,
          'files the new payload lacks go to the backup, not deleted')
    rj = func(code, 'Read-Journal')
    check("'STAGED'" in rj and "'PUBLISHED'" in rj and "'COMMITTED'" in rj, 'a rerun reads what the journal staged, published and committed')
    own = body[body.find('$ours ='):body.find('if (-not $ours)')]
    check(all(x in own for x in ('$previousFiles', '$pendingFiles', '$newFiles', '$earlier.Known')),
          "a file is the installer's own if it matches the previous manifest, the pending one, the new payload or the journal")
    check('$conflicts.Add($target)' in body and 'Nothing was changed' in body and '-recovery-' in body,
          'every other file is preserved and listed, with a way out, before anything changes')
    i_state = body.find('[IO.File]::WriteAllLines($statePath')
    i_commit = body.find('Journal ("COMMITTED`t"')
    i_unhint = body.find('Remove-Item -LiteralPath $pendingPath -Force')
    i_done = body.find("Log ('Installation complete: ' + $InstallDir)")
    i_clean = body.find('Remove-Item -LiteralPath $txnDir -Recurse -Force')
    check(0 < i_state < i_commit < i_unhint < i_done < i_clean, 'COMMITTED after the state, then the hint is removed, then the folder is cleaned up')
    check('$earlier.Exists -and $earlier.Committed' in code, 'a rerun that finds a committed journal only cleans up')
    ucode = re.sub(r'(?m)#.*$', '', uni)
    check(".sutram-transaction'" in ucode and 'Left in place' in ucode, "uninstall leaves a stopped installation's backups and says where")
    check('call append_file' in wiz and 'msg_engine_timeout' in wiz and 'ENGINE_WAIT_MS' in wiz,
          'the wizard writes to the engine log when its 15-minute stop fires')
    check("'0.1.0'" not in code and "$displayVersion = $Matches[1] + '.' + $Matches[2]" in code, "Windows is told the compiler's version")
    lg, ulg = func(code, 'Log'), func(re.sub(r'(?m)#.*$', '', uni), 'Log')
    check('Add-Content' not in lg and '[IO.FileShare]::Delete' in lg and 'catch' in lg and 'Add-Content' not in ulg
          and '[IO.FileShare]::Delete' in ulg,
          'R136: the logs are appended with full sharing, and a log line that cannot be written never stops the run')
    setup = os.path.join(ROOT, 'Sutram-Setup.exe')
    if os.path.exists(setup):
        b = open(setup, 'rb').read()
        for f in ('install-core.ps1', 'uninstall-core.ps1'):
            check(open(os.path.join(NI, f), 'rb').read() in b, f'Sutram-Setup.exe embeds this {f}')
    else:
        print('NOT RUN  Sutram-Setup.exe is not in the tree')
    print(f'r134 install transaction: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())

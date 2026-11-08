#!/usr/bin/env python3
"""R143: three things the Windows v311 acceptance run saw on first contact with the installer.

1. The licence page: the em dash in "Sutram — The Complete Thread" (U+2014, UTF-8 E2 80 94) showed as three
   characters, and the lines ran together ("ThreadCopyright"). license_to_utf16 widened the UTF-8 blob byte by
   byte, and a multiline EDIT control does not break on a bare LF. This gate assembles the wizard's own
   license_to_utf16 (with the wizard's own PROLOG/EPILOG/PTR macros) into a Linux harness and runs it on the
   licence the wizard embeds, on that licence with CR LF, and on edge cases, against a reference: UTF-8 decoded
   (above U+FFFF as a surrogate pair; an invalid or truncated sequence as U+FFFD, one byte at a time), each LF
   not already after a CR written CR LF, at most 4095 units and a NUL.
2. The uninstall's PowerShell window: do_uninstall starts the script with CREATE_NO_WINDOW, as the install does,
   and the script shows its own failure in a message box (with nobody's console to see it in).
3. An empty HKCU\\Software\\Classes\\.sm\\OpenWithProgids left by uninstall: the uninstaller removes that key, and
   then .sm, only when it has no value and no subkey left.
4. (R147) the licence instruction label is high enough for its two lines (the body font, a wider font's count),
   above the licence box; and on success the uninstaller removes its own %TEMP%\\STMxxxx.tmp staging folder.
Rendering on Windows is not checked here; the Windows run is the check of that.
Last line: "r143 installer first contact: N checks, M failed".
"""
import os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NI = os.path.join(ROOT, 'windows', 'native-installer')


def reference(b):
    out, i = [], 0
    while i < len(b) and len(out) < 4094:
        c = b[i]
        n, cp = 1, 0xFFFD
        if c == 0x0A:
            if not out or out[-1] != 0x0D:
                out.append(0x0D)
            out.append(0x0A); i += 1; continue
        if c < 0x80:
            cp = c
        else:
            need = 2 if 0xC2 <= c < 0xE0 else 3 if 0xE0 <= c < 0xF0 else 4 if 0xF0 <= c < 0xF5 else 0
            tail = b[i + 1:i + need]
            if need and len(tail) == need - 1 and all(t & 0xC0 == 0x80 for t in tail):
                v = c & (0x1F, 0x0F, 0x07)[need - 2]
                for t in tail:
                    v = (v << 6) | (t & 0x3F)
                lo = (0x80, 0x800, 0x10000)[need - 2]
                if v >= lo and not (0xD800 <= v <= 0xDFFF) and v <= 0x10FFFF:
                    cp, n = v, need
        if cp > 0xFFFF:
            cp -= 0x10000
            out += [0xD800 + (cp >> 10), 0xDC00 + (cp & 0x3FF)]
        else:
            out.append(cp)
        i += n
    return out


def main():
    checks = fails = 0

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    wiz = open(os.path.join(NI, 'sutram_wizard.asm'), encoding='utf-8').read()
    lic = open(os.path.join(ROOT, 'LICENSE.txt'), 'rb').read().replace(b'\r\n', b'\n')   # as the builder embeds it
    if not (shutil.which('nasm') and shutil.which('ld')):
        print('NOT RUN  the licence harness: nasm or ld is not installed')
    else:
        fn = wiz[wiz.index('\nlicense_to_utf16:'):wiz.index('; --- post a progress percent')]
        macros = ''.join(re.findall(r'(?ms)^%macro (?:PROLOG|EPILOG|PTR)\b.*?^%endmacro\n', wiz))
        work = tempfile.mkdtemp(prefix='r143-lic-')
        cases = [('the licence the wizard embeds', lic),
                 ('the licence with CR LF line ends', lic.replace(b'\n', b'\r\n')),
                 ('edge cases: 2/3/4-byte, a surrogate pair, overlong, a stray continuation, a CR alone, truncated',
                  b'a\xc3\xa9\xe2\x80\x94\xf0\x9f\x98\x80\xc0\xaf\x80\xed\xa0\x80x\ry\n\n\xe2\x80'),
                 ('a blob longer than the buffer', b'\n' * 5000)]
        for name, blob in cases:
            bp = os.path.join(work, 'blob.bin')
            open(bp, 'wb').write(blob)
            asm = ('BITS 64\ndefault rel\n' + macros + 'section .data\nblob_license: incbin "' + bp + '"\nblob_license_end:\n'
                   'section .bss\nlic_w: resw 4096\nsection .text\nglobal _start\n_start:\n    call license_to_utf16\n'
                   '    mov eax, 1\n    mov edi, 1\n    lea rsi, [rel lic_w]\n    mov edx, 8192\n    syscall\n'
                   '    mov eax, 60\n    xor edi, edi\n    syscall\n' + fn)
            ap = os.path.join(work, 'h.asm')
            open(ap, 'w').write(asm)
            b = subprocess.run(f'nasm -f elf64 {ap} -o {ap}.o && ld -o {ap}.x {ap}.o', shell=True, capture_output=True, text=True)
            if b.returncode:
                check(False, f'{name}: the harness builds ({b.stderr.strip()[:100]})')
                continue
            raw = subprocess.run([ap + '.x'], capture_output=True, timeout=10).stdout
            units = [int.from_bytes(raw[k:k + 2], 'little') for k in range(0, len(raw), 2)]
            got = units[:units.index(0)] if 0 in units else units
            want = reference(blob)
            first = next((k for k in range(min(len(got), len(want))) if got[k] != want[k]), None)
            check(got == want, f'{name}: {len(got)} units, as the reference' if got == want else
                  f'{name}: {len(got)} units, reference {len(want)}; first difference at {first}')
        u = reference(lic)
        text = ''.join(chr(c) for c in u)
        check(text == lic.decode('utf-8').replace('\n', '\r\n'),
              'the reference agrees with Python\'s UTF-8 codec on the licence (CR LF line ends)')
        check(text.startswith('Sutram — The Complete Thread\r\nCopyright'),
              'the first line is "Sutram — The Complete Thread", then CR LF (U+2014 EM DASH, not three characters)')
    d = wiz[wiz.index('\ndo_uninstall:'):]
    d = d[:d.index('API  CreateProcessW')]
    check('mov  qword [rsp+40], CREATE_NO_WINDOW' in re.sub(r';[^\n]*', '', d),
          'the uninstall script is started with CREATE_NO_WINDOW (no PowerShell window), as the install is')
    uni = open(os.path.join(NI, 'uninstall-core.ps1'), encoding='utf-8-sig').read()
    ucode = re.sub(r'(?m)#.*$', '', uni)

    def func(src, name):
        k = src.find('function ' + name)
        e = src.find('\nfunction ', k + 1)
        return src[k:e if e > 0 else len(src)] if k >= 0 else ''
    tail = ucode[ucode.rfind('$failure=$_.Exception.Message'):] if '$failure=$_.Exception.Message' in ucode else ''
    check('.Popup(' in tail and '$LogPath' in tail and 'exit 1' in tail,
          'a failed uninstall says so in a message box, with its log - there is no console to see it in')
    i = ucode.find("Remove-ItemProperty -LiteralPath (Join-Path $extKey 'OpenWithProgids')")
    seg = ucode[i:i + 900]
    check(i > 0 and "'Software\\Classes\\.sm\\OpenWithProgids','Software\\Classes\\.sm'" in seg
          and '$k.ValueCount -eq 0 -and $k.SubKeyCount -eq 0' in seg and 'DeleteSubKey($sub,$false)' in seg
          and seg.find('ValueCount') < seg.find('DeleteSubKey'),
          'uninstall removes .sm\\OpenWithProgids, then .sm, only when the key has no value and no subkey left')
    # R147 (Windows v312 acceptance): the licence instruction label clipped its second line, and uninstall left its
    # %TEMP%\STMxxxx.tmp folder with the script and the log.
    lab = re.search(r'PTR  rcx, b_lichead\n    mov  edx, (\d+)\n    mov  r8d, (\d+)\n    mov  r9d, (\d+)\n    mov  qword \[rsp\+32\], (\d+)', wiz)
    edit = re.search(r'mov  qword \[rsp\+32\], (\d+)\n    mov  qword \[rsp\+40\], (\d+)\n    mov  qword \[rsp\+48\], (\d+)\n'
                     r'    mov  qword \[rsp\+56\], (\d+)\n    mov  rax, \[rel hwnd_main\]\n    mov  \[rsp\+64\], rax\n    mov  qword \[rsp\+72\], IDC_LICEDIT', wiz)
    radio = re.search(r'PTR  r8,  b_accept\n.*?mov  qword \[rsp\+40\], (\d+)', wiz, re.S)
    text = re.search(r'b_lichead:\s+u16 "([^"]*)"', wiz).group(1)
    lines = None
    try:
        from PIL import ImageFont
        f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 19)   # wider than Segoe UI: a safe count

        def wrap(w):
            n, cur = 1, ''
            for word in text.split(' '):
                t = (cur + ' ' + word).strip()
                if f.getlength(t) <= w:
                    cur = t
                else:
                    n, cur = n + 1, word
            return n
        lines = (wrap(int(lab.group(3))), wrap(int(lab.group(3)) * 0.85))
    except Exception as e:
        print('NOT RUN  the label wrap count (PIL or DejaVu Sans missing: ' + str(e)[:60] + ')')
    if lab and edit and radio:
        x, y, w, h = map(int, lab.groups())
        ey, eh = int(edit.group(2)), int(edit.group(4))
        need = 25 * max(lines) if lines else 50
        check(h >= need and y + h <= ey and ey + eh <= int(radio.group(1)),
              f'the licence instruction label is {h} px high for {lines or "?"} lines (at its width and at 85% of it, 25 px a '
              f'line of the 19 px body font) and ends above the licence box ({y}+{h} <= {ey}), which ends above the radios')
    else:
        check(False, 'the licence page layout was found in the wizard')
    k = ucode.find("Log 'Uninstall completed")
    tailok = ucode[k:ucode.find('exit 0', k)] if k > 0 else ''
    check(all(x in tailok for x in ("[IO.Path]::GetTempPath()", "-match '^STM[0-9A-Fa-f]{1,8}\\.tmp$'", '$names.Count -eq 2',
                                    "$names -contains 'uninstall-core.ps1'", "$names -contains 'uninstall.log'",
                                    '[IO.Directory]::Delete($stageDir, $false)'))
          and 'Recurse' not in tailok and '$stageDir' not in ucode[ucode.rfind('$failure=$_.Exception.Message'):],
          'on success uninstall removes its own %TEMP%\\STMxxxx.tmp folder - only in TEMP, with the wizard\'s name, holding '
          'exactly its script and log, by exact paths and a non-recursive delete; a failure keeps it')
    # R152-R153 (Windows v312 first-run paths; ChatGPT R218 follow-up): one function decides whether a shortcut may be
    # written and records it; ownership is the link's own bytes, and nothing deletes a link on a flag or a target.
    eng = re.sub(r'(?m)#.*$', '', open(os.path.join(NI, 'install-core.ps1'), encoding='utf-8-sig').read())
    so = func(eng, 'Set-OwnedShortcut')
    i_test, i_save, i_rec = so.find('Test-OwnedShortcut $Path'), so.find('$sc.Save()'), so.find("$script:ownedShortcuts.Add(")
    to = func(eng, 'Test-OwnedShortcut')
    calls = re.findall(r'(?<!function )\b(Set-OwnedShortcut|New-Shortcut) \(', eng)
    saves = eng.count('.Save()')
    check(0 < i_test < i_save < i_rec and "+ '|' + (Get-Sha $Path)" in so and "return 'preserved'" in so
          and so.find("return 'preserved'") < i_save and 'Get-Sha $Path) -eq $rec' in to and saves == 1
          and 'New-Shortcut' not in calls and len(calls) == 5 and '$isOurs' not in eng,
          'R153: one function (Set-OwnedShortcut) decides and records: a link is written only when its name is free or it is '
          'this installer\'s, unchanged since (its bytes have the recorded SHA-256); it is recorded with that hash as it is '
          'written; a kept link is not recorded; it is the only .Save() in the engine (5 call sites)')
    desk = eng[eng.find('if ($DesktopShortcut) {'):eng.find('if ($DesktopShortcut) {') + 1600]
    check("$made = Set-OwnedShortcut (Join-Path $desktopDir $n)" in desk and "if ($made -ne 'preserved') { $desktopName = $n; $desktopOwned = $true; break }" in desk
          and "'Sutram IDE (Sutram).lnk'" in desk and "'Sutram IDE (Sutram ' + $_ + ').lnk'" in desk
          and 'Remove-OwnedShortcut (Join-Path $desktopDir $previousDesktopName)' in desk and '$desktopOwned = $true\n' not in desk,
          'R153: DesktopOwned comes from what Set-OwnedShortcut did, at the first free of ten names; unchecked, only an '
          'unchanged own link is removed')
    ul = ucode[ucode.find("if ($state.ContainsKey('OwnedShortcuts')) {"):]
    ul = ul[:ul.find('$classKey=')]
    check("(Get-FileHash -LiteralPath $link -Algorithm SHA256).Hash -eq $parts[1]" in ul and '$parts.Count -lt 2 -or -not $parts[1]' in ul
          and 'TargetPath' not in ul and "$state['DesktopOwned']" not in ucode and '$desktopOwned' not in ucode
          and '[string]::Equals($parent,$startMenu' in ul and '[string]::Equals($parent,$desktopDir' in ul,
          'R153: uninstall removes a shortcut only when it is recorded with a hash, is in the Start-menu folder or on the '
          'desktop, and its bytes still have that hash - not on a matching target, not on DesktopOwned')
    ck = re.search(r'b_ckdesk:\s+u16 "([^"]*)"', wiz)
    check(ck and 'Sutram IDE' in ck.group(1) and 'Terminal' not in ck.group(1),
          f'the desktop checkbox names what it makes ({ck.group(1) if ck else "?"!r})')
    setup = os.path.join(ROOT, 'Sutram-Setup.exe')
    if os.path.exists(setup):
        check(open(os.path.join(NI, 'uninstall-core.ps1'), 'rb').read() in open(setup, 'rb').read(),
              'Sutram-Setup.exe embeds this uninstall-core.ps1')
    print(f'r143 installer first contact: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())

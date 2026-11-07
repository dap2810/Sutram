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
    tail = ucode[ucode.rfind('$failure=$_.Exception.Message'):] if '$failure=$_.Exception.Message' in ucode else ''
    check('.Popup(' in tail and '$LogPath' in tail and 'exit 1' in tail,
          'a failed uninstall says so in a message box, with its log - there is no console to see it in')
    i = ucode.find("Remove-ItemProperty -LiteralPath (Join-Path $extKey 'OpenWithProgids')")
    seg = ucode[i:i + 900]
    check(i > 0 and "'Software\\Classes\\.sm\\OpenWithProgids','Software\\Classes\\.sm'" in seg
          and '$k.ValueCount -eq 0 -and $k.SubKeyCount -eq 0' in seg and 'DeleteSubKey($sub,$false)' in seg
          and seg.find('ValueCount') < seg.find('DeleteSubKey'),
          'uninstall removes .sm\\OpenWithProgids, then .sm, only when the key has no value and no subkey left')
    setup = os.path.join(ROOT, 'Sutram-Setup.exe')
    if os.path.exists(setup):
        check(open(os.path.join(NI, 'uninstall-core.ps1'), 'rb').read() in open(setup, 'rb').read(),
              'Sutram-Setup.exe embeds this uninstall-core.ps1')
    print(f'r143 installer first contact: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())

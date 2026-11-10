#!/usr/bin/env python3
"""R184: vartani_grahan() reads one line of text; nivesha_anta() says the input has ended.

  - the line comes back WITHOUT its newline (LF, or CR LF);
  - an empty line is "" and is NOT the end of the input;
  - at the end of the input vartani_grahan() gives "" and nivesha_anta() becomes 1 - and stays 1 - so a
    loop that reads until the end stops; a last line with no newline is returned first, whole;
  - there is no length limit: a line of 5,000,000 bytes comes back whole (the buffer starts at 64 and doubles);
  - grahan() and vartani_grahan() share the input: a number's line, then a text line;
  - the result is a string to the compiler: it prints as text, compares with ==, joins with +, and
    arithmetic on it is refused (E_VARTANI_GANIT); an argument is refused.

Each case: the program, the bytes fed to it, and the exact bytes it must print (golden), or the code it is
refused with.

Usage: python3 tests/r184/test_read_line.py [--compiler PATH]
"""
import os, shutil, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
checks = fails = 0

ASK = '''mukhya() {
    likha("Tava nama kim? ")
    vitti nama = vartani_grahan()
    likha("Namaste, ", nama, "!\\n")
}
'''
ALL = '''mukhya() {
    vitti n = 0
    yavat (1) {
        vitti s = vartani_grahan()
        yadi (nivesha_anta()) { krama }
        n = n + 1
        likha(n, ": [", s, "] ", vartani_aayam(s))
    }
    likha("panktayah: ", n)
}
'''
LEN = '''mukhya() {
    yavat (1) {
        vitti s = vartani_grahan()
        yadi (nivesha_anta()) { krama }
        likha(vartani_aayam(s))
    }
}
'''
AFTER = '''mukhya() {
    vitti a = vartani_grahan()
    likha(nivesha_anta())
    vitti b = vartani_grahan()
    likha(nivesha_anta())
    vitti c = vartani_grahan()
    likha(nivesha_anta())
    yadi (b == "") { likha("b rikta\\n") }
    yadi (c == "") { likha("c rikta\\n") }
}
'''
MIX = '''mukhya() {
    vitti v = grahan()
    vitti s = vartani_grahan()
    likha(s, " ", v)
}
'''
KIND = '''prakriya prashna(q) {
    likha(q)
    nivartanam vartani_grahan()
}
mukhya() {
    vitti a = prashna("nama? ")
    yadi (a == "hari") { likha("sama\\n") }
    vitti j = a + "!"
    likha(j, "\\n")
    likha(vartani_grahan(), "\\n")
}
'''
DEV = '''मुख्य() {
    वित्ति s = वर्तनी_ग्रहण()
    लिख("[", s, "] ", निवेश_अन्त())
}
'''
big = 'w' * 5000000
# (name, what, source, stdin bytes, expected stdout bytes)
RUNS = [
    ('known-line', 'a known line comes back without its newline', ASK, b'Asha Patel\n',
     b'Tava nama kim? Namaste, Asha Patel!\n'),
    ('two-words', 'the whole line, not its first word', ASK, b'hello world\n', b'Tava nama kim? Namaste, hello world!\n'),
    ('devanagari-text', 'UTF-8 text passes through byte for byte', ASK, 'आशा पटेल\n'.encode(),
     'Tava nama kim? Namaste, आशा पटेल!\n'.encode()),
    ('empty-line', 'Enter alone is "" - and the program goes on', ASK, b'\n', b'Tava nama kim? Namaste, !\n'),
    ('end-of-input', 'no input at all: "" at once, no hang', ASK, b'', b'Tava nama kim? Namaste, !\n'),
    ('loop-ends', 'a read-until-the-end loop stops at the end, not at an empty line', ALL, b'one\n\ntwo words\n',
     b'1: [one] 3\n2: [] 0\n3: [two words] 9\npanktayah: 3\n'),
    ('loop-no-input', 'the same loop on no input runs zero times', ALL, b'', b'panktayah: 0\n'),
    ('last-line-unfinished', 'a last line with no newline is returned whole, then the end', ALL, b'one\nlast',
     b'1: [one] 3\n2: [last] 4\npanktayah: 2\n'),
    ('crlf', 'CR LF: the CR is not part of the line', ALL, b'one\r\n\r\ntwo\r\n',
     b'1: [one] 3\n2: [] 0\n3: [two] 3\npanktayah: 3\n'),
    ('lengths', '63, 64, 65, 100,000 and 5,000,000 bytes: nothing cut', LEN,
     ('y' * 63 + '\n' + 'z' * 64 + '\n' + 'q' * 65 + '\n' + 'x' * 100000 + '\n' + big + '\n').encode(),
     b'63\n64\n65\n100000\n5000000\n'),
    ('flag-stays', 'nivesha_anta() is 0 after a line, 1 at the end, and stays 1', AFTER, b'a\n',
     b'0\n1\n1\nb rikta\nc rikta\n'),
    ('number-then-text', 'grahan() takes the number line, vartani_grahan() the next', MIX, b'12\nAsha\n', b'Asha 12\n'),
    ('a-string', 'the result is a string: from a prakriya, ==, +, and straight into likha', KIND, b'hari\nom\n',
     b'nama? sama\nhari!\nom\n'),
    ('devanagari-names', 'the Devanagari names are the same two functions', DEV, 'राम\n'.encode(), '[राम] 0\n'.encode()),
]
REFUSED = [
    ('argument', 'vartani_grahan takes no argument (refused as parimana(1) is)', 'mukhya() {\n    vitti s = vartani_grahan(1)\n}\n', 'vyakaran dosh'),
    ('arithmetic', 'arithmetic on the text is refused', 'mukhya() {\n    vitti s = vartani_grahan() * 2\n}\n', 'E_VARTANI_GANIT'),
    ('as-condition', 'the text as a condition is refused', 'mukhya() {\n    yadi (vartani_grahan()) { likha(1) }\n}\n', 'E_VARTANI_SATYA'),
]


def check(ok, name, what, detail=''):
    global checks, fails
    checks += 1
    if ok:
        print('ok    %-22s %s' % (name, what))
    else:
        fails += 1
        print('FAIL  %-22s %s %s' % (name, what, detail))


def main():
    comp = os.path.join(ROOT, 'sutram_compiler')
    if '--compiler' in sys.argv:
        comp = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1])
    work = tempfile.mkdtemp(prefix='r184_')
    try:
        for name, what, src, feed, want in RUNS:
            sm = os.path.join(work, name + '.sm')
            out = os.path.join(work, name + '.bin')
            open(sm, 'w', encoding='utf-8').write(src)
            c = subprocess.run([comp, sm, out], capture_output=True, cwd=ROOT)
            if not os.path.exists(out):
                check(False, name, what, '- did not compile: ' + c.stdout.decode('utf-8', 'replace')[-200:])
                continue
            try:
                r = subprocess.run([out], input=feed, capture_output=True, timeout=60)
            except subprocess.TimeoutExpired:
                check(False, name, what, '- did not end in 60 s (a hang)')
                continue
            check(r.returncode == 0 and r.stdout == want, name, what,
                  '- exit %d, got %r' % (r.returncode, r.stdout[:120]))
        for name, what, src, code in REFUSED:
            sm = os.path.join(work, name + '.sm')
            out = os.path.join(work, name + '.bin')
            open(sm, 'w', encoding='utf-8').write(src)
            c = subprocess.run([comp, sm, out], capture_output=True, cwd=ROOT)
            text = (c.stdout + c.stderr).decode('utf-8', 'replace')
            check(not os.path.exists(out) and code in text, name, what, '- wanted %s, got %r' % (code, text[-160:]))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print('r184 read a line: %d checks, %d failed' % (checks, fails))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())

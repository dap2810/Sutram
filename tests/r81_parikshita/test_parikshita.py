#!/usr/bin/env python3
"""ROUND-81: parikshita prakriya - the checked-function boundary (ChatGPT R149's design).

Each case is a program and what must happen: it compiles and prints exactly OUT, or it is refused
with CODE at LINE and no output file is written. The cases are R149's acceptance matrix as far as
the first build reaches: a checked chain and a recursive pair accepted; an unmarked leaf, a call
through a function value, a raw builtin, an address indexed without a known extent - refused, at
the first bad edge; a legacy caller passing numbers into checked code - accepted; unmarked code -
unchanged. Last line: `r81 parikshita: N checks, M failed`.

usage: python3 -B tests/r81_parikshita/test_parikshita.py [--compiler PATH]
"""
import os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OK, NO = 'ok', 'refused'
CASES = [
    # name, source, (OK, stdout) | (NO, code, line)
    ('chain accepted', '''parikshita prakriya patra(x) {
    nivartanam x * x
}
parikshita prakriya madhya(x) {
    nivartanam patra(x) + 1
}
parikshita mukhya() {
    likha(madhya(6))
}
''', (OK, '37\n')),
    ('recursive pair accepted (through a prototype)', '''parikshita prakriya sam(n);
parikshita prakriya visham(n) {
    yadi (n == 0) { nivartanam 0 }
    nivartanam sam(n - 1)
}
parikshita prakriya sam(n) {
    yadi (n == 0) { nivartanam 1 }
    nivartanam visham(n - 1)
}
parikshita mukhya() {
    likha(sam(10))
}
''', (OK, '1\n')),
    ('block, constant nirmmita, mala, loops accepted', '''parikshita mukhya() {
    vitti m[4]
    chakra i = 0 tak 3 {
        m[i] = i + 1
    }
    vitti s = 0
    mandapa {
        vitti p = nirmmita(4 * 8)
        chakra i = 0 tak 3 {
            p[i] = m[i] * 10
        }
        chakra i = 0 tak 3 {
            s = s + p[i]
        }
    }
    likha("yog ", s)
}
''', (OK, 'yog 100\n')),
    ('braceless forms accepted', '''parikshita prakriya dvi(x)
    nivartanam x * 2

parikshita mukhya()
    likha(dvi(21))
''', (OK, '42\n')),
    ('likha of three values with a literal first: accepted', '''parikshita mukhya() {
    likha("a ", 1, 2)
}
''', (OK, 'a 12\n')),
    ('legacy caller passes numbers into checked code: accepted', '''parikshita prakriya varg(x) {
    nivartanam x * x
}
mukhya() {
    vitti p = nirmmita(8)
    p[0] = 9
    likha(varg(p[0]))
}
''', (OK, '81\n')),
    ('unmarked code unchanged: an ordinary name parikshita', '''prakriya f(parikshita) {
    nivartanam parikshita + 1
}
mukhya() {
    vitti parikshita = 4
    likha(f(parikshita))
}
''', (OK, '5\n')),
    ('mala index past the end still stops at run time', '''parikshita mukhya() {
    vitti a[2]
    vitti i = 0
    yavat (i < 3) {
        a[i] = i
        i = i + 1
    }
    likha(1)
}
''', (OK, 'Sutram Error: mala ank seema atikram\n')),
    ('unmarked leaf refused at the first bad edge', '''prakriya patta(x) {
    nivartanam x
}
parikshita prakriya shakha(x) {
    nivartanam patta(x)
}
parikshita mukhya() {
    likha(shakha(1))
}
''', (NO, 'E_APARIKSHITA_AHVAN', 5)),
    ('unmarked library function refused', '''yoj ganit
parikshita mukhya() {
    likha(varg(3))
}
''', (NO, 'E_APARIKSHITA_AHVAN', 3)),
    ('a marked prototype is not a marked definition', '''parikshita prakriya g(x);
parikshita prakriya f(x) {
    nivartanam g(x)
}
prakriya g(x) {
    nivartanam x
}
parikshita mukhya() {
    likha(f(1))
}
''', (NO, 'E_APARIKSHITA_AHVAN', 3)),
    ('a call through a function value refused', '''parikshita prakriya ek(x) {
    nivartanam x
}
parikshita mukhya() {
    vitti f = ek
    likha(f(1))
}
''', (NO, 'E_APARIKSHITA_', None)),
    ('a parameter indexed: refused', '''parikshita prakriya pratham(p) {
    nivartanam p[0]
}
parikshita mukhya() {
    likha(pratham(0))
}
''', (NO, 'E_APARIKSHITA_SMRITI', 2)),
    ('a parameter written through: refused', '''parikshita prakriya rakh(p) {
    p[1] = 5
    nivartanam 0
}
parikshita mukhya() {
    likha(rakh(0))
}
''', (NO, 'E_APARIKSHITA_SMRITI', 2)),
    ('a pointer assigned again: refused', '''parikshita mukhya() {
    vitti p = nirmmita(16)
    p = p + 8
    likha(p[0])
}
''', (NO, 'E_APARIKSHITA_SMRITI', 4)),
    ('a size computed at run time: refused', '''parikshita mukhya() {
    vitti n = 4
    vitti p = nirmmita(n * 8)
    p[0] = 1
    likha(p[0])
}
''', (NO, 'E_APARIKSHITA_SMRITI', 4)),
    ('likh8 refused', '''parikshita mukhya() {
    vitti p = nirmmita(8)
    likh8(p, 1)
}
''', (NO, 'E_APARIKSHITA_KARYA', None)),
    ('akshar_rakh refused', '''parikshita mukhya() {
    vitti p = nirmmita(8)
    akshar_rakh(p, 0, 65)
}
''', (NO, 'E_APARIKSHITA_KARYA', None)),
    ('memset refused', '''parikshita mukhya() {
    vitti p = nirmmita(8)
    smaran(p, 0, 8)
}
''', (NO, 'E_APARIKSHITA_KARYA', None)),
    ('shabda (reads a string through an address) refused', '''parikshita mukhya() {
    shabda("a")
}
''', (NO, 'E_APARIKSHITA_KARYA', None)),
    ('kosh refused', '''parikshita mukhya() {
    kosh k
    kosh_push(k, 1)
}
''', (NO, 'E_APARIKSHITA_KARYA', None)),
    ('likha(fd, buffer, count) refused', '''parikshita mukhya() {
    vitti p = nirmmita(8)
    likha(1, p, 8)
}
''', (NO, 'E_APARIKSHITA_KARYA', None)),
    ('a rachana field refused', '''rachana Bindu = { x, y }
parikshita mukhya() {
    vitti b = nirmmita(16)
    b.x = 1
    likha(b.x)
}
''', (NO, 'E_APARIKSHITA_KARYA', None)),
    ('parikshita before anything else', '''parikshita vitti x = 1
mukhya() {
    likha(x)
}
''', (NO, 'E_PARIKSHITA_STHAN', 1)),
]


def main(argv):
    comp = os.path.abspath(argv[argv.index('--compiler') + 1]) if '--compiler' in argv else \
        os.path.join(ROOT, 'sutram_compiler')
    tmp = tempfile.mkdtemp(prefix='r81-')
    checks = failed = 0
    for name, src, want in CASES:
        sp, bp = os.path.join(tmp, 'p.sm'), os.path.join(tmp, 'p.bin')
        open(sp, 'w').write(src)
        if os.path.exists(bp):
            os.remove(bp)
        c = subprocess.run([comp, sp, bp], capture_output=True, text=True, timeout=60, cwd=ROOT)
        msg = c.stdout + c.stderr
        ok, why = True, ''
        if want[0] == OK:
            if c.returncode != 0 or not os.path.exists(bp):
                ok, why = False, 'refused: ' + msg.strip().split('\n')[-1][:100]
            else:
                r = subprocess.run([bp], capture_output=True, text=True, timeout=10)
                if r.stdout != want[1]:
                    ok, why = False, f'printed {r.stdout!r}, want {want[1]!r}'
        else:
            code, line = want[1], want[2]
            if c.returncode == 0 or os.path.exists(bp):
                ok, why = False, 'compiled (an output file was written)'
            elif code not in msg:
                ok, why = False, f'no {code}: ' + msg.strip().split('\n')[0][:100]
            elif line is not None and f'p.sm:{line}:' not in msg:
                ok, why = False, f'not at line {line}: ' + msg.strip().split('\n')[0][:100]
        checks += 1
        if not ok:
            failed += 1
            print(f'FAIL  {name}: {why}')
    print(f'r81 parikshita: {checks} checks, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

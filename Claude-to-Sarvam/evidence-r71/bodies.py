#!/usr/bin/env python3
"""R71 WS2: every construct that takes a body, written with an INDENTED multi-statement body (no braces),
run on two compilers. Each body runs three statements; the expected output says what the indentation says.

usage: bodies.py COMPILER [COMPILER...]   (prints a table)"""
import os, subprocess, sys, tempfile

CASES = [
 ("yadi, body of 3", """mukhya()
    vitti c = 0
    yadi (1 == 1)
        c = c + 1
        c = c + 1
        c = c + 1
    likha(c)
""", "3"),
 ("yadi false, body of 3 skipped", """mukhya()
    vitti c = 0
    yadi (1 == 2)
        c = c + 1
        c = c + 1
        c = c + 1
    likha(c)
""", "0"),
 ("yadi / anya, 3 in each", """mukhya()
    vitti c = 0
    yadi (1 == 2)
        c = c + 100
        c = c + 100
        c = c + 100
    anya
        c = c + 1
        c = c + 1
        c = c + 1
    likha(c)
""", "3"),
 ("yadi / anya yadi / anya", """mukhya()
    vitti c = 0
    vitti x = 2
    yadi (x == 1)
        c = c + 100
        c = c + 100
    anya yadi (x == 2)
        c = c + 1
        c = c + 1
        c = c + 1
    anya
        c = c + 1000
        c = c + 1000
    likha(c)
""", "3"),
 ("yavat, body of 3", """mukhya()
    vitti i = 0
    vitti c = 0
    yavat (i < 3)
        c = c + 1
        c = c + 1
        i = i + 1
    likha(c)
""", "6"),
 ("chakra i = a tak b", """mukhya()
    vitti c = 0
    chakra i = 1 tak 3
        c = c + 1
        c = c + 1
        c = c + 1
    likha(c)
""", "9"),
 ("chakra i = a arabhya b paryantam", """mukhya()
    vitti c = 0
    chakra i = 1 arabhya 3 paryantam
        c = c + 1
        c = c + 1
        c = c + 1
    likha(c)
""", "9"),
 ("kuru ... yavat (c)", """mukhya()
    vitti i = 0
    vitti c = 0
    kuru
        c = c + 1
        c = c + 1
        i = i + 1
    yavat (i < 3)
    likha(c)
""", "6"),
 ("guna without braces (guna requires { } - refused loudly, not silently)", """mukhya()
    vitti c = 0
    vitti x = 2
    guna (x)
        bhavana 1:
            c = c + 100
            c = c + 100
        bhavana 2:
            c = c + 1
            c = c + 1
            c = c + 1
        anya
            c = c + 1000
    likha(c)
""", "REFUSED"),
 ("guna { } with indented bhavana bodies", """mukhya() {
    vitti c = 0
    vitti x = 2
    guna (x) {
        bhavana 1:
            c = c + 100
            c = c + 100
        bhavana 2:
            c = c + 1
            c = c + 1
            c = c + 1
    }
    likha(c)
}
""", "3"),
 ("yadi dosh (q = call) / anya", """prakriya ank(c) {
    yadi (c < 48 || c > 57) {
        nivartanam dosh(1)
    }
    nivartanam siddhi(c - 48)
}
mukhya()
    vitti c = 0
    yadi dosh (q = ank(65))
        c = c + 1
        c = c + 1
        c = c + 1
    anya
        c = c + 100
        c = c + 100
    likha(c)
""", "3"),
 ("mukhya without braces runs to end of file: a prakriya after it is inside it (compiled, callable)", """prakriya f(a) {
    nivartanam a
}
mukhya()
    likha(f(1))
prakriya g(a)
    nivartanam a
""", "1"),
 ("mukhya with braces, then a statement after it (silently dropped before v266)", """mukhya() {
    likha(1)
}
likha(2)
""", "REFUSED"),
 ("prakriya without braces, then mukhya", """prakriya f(a)
    vitti b = a + 1
    b = b + 1
    nivartanam b + 1
mukhya()
    likha(f(1))
""", "4"),
 ("two prakriya without braces", """prakriya f(a)
    vitti b = a + 1
    nivartanam b
prakriya g(a)
    vitti b = a * 2
    nivartanam b
mukhya()
    likha(f(1) + g(5))
""", "12"),
 ("mukhya without braces, 3 statements", """mukhya()
    vitti c = 1
    c = c + 1
    likha(c + 1)
""", "3"),
 ("nested: yavat > yadi > yavat", """mukhya()
    vitti i = 0
    vitti c = 0
    yavat (i < 2)
        vitti j = 0
        yadi (i == 1)
            yavat (j < 2)
                c = c + 10
                j = j + 1
        c = c + 1
        i = i + 1
    likha(c)
""", "22"),
 ("indented body containing a braced block", """mukhya()
    vitti c = 0
    vitti i = 0
    yavat (i < 2)
        yadi (i == 0) {
            c = c + 1
            c = c + 1
        }
        c = c + 10
        i = i + 1
    likha(c)
""", "22"),
 ("braced body containing an indented block", """mukhya() {
    vitti c = 0
    vitti i = 0
    yavat (i < 2) {
        yadi (i == 0)
            c = c + 1
            c = c + 1
        c = c + 10
        i = i + 1
    }
    likha(c)
}
""", "22"),
 ("one-statement body on the next line, same indentation (unchanged rule)", """mukhya()
    vitti c = 0
    yadi (1 == 2)
    c = c + 5
    c = c + 1
    likha(c)
""", "1"),
 ("body on the header's line (unchanged rule)", """mukhya()
    vitti c = 0
    yadi (1 == 2) c = c + 5
    c = c + 1
    likha(c)
""", "1"),
 ("statement continued over two lines inside a body", """mukhya()
    vitti c = 0
    yadi (1 == 1)
        c = c +
            5
        c = c + 1
    likha(c)
""", "6"),
 ("two statements on a one-statement body's line (the second ran outside before v267)", """mukhya()
    vitti c = 0
    yadi (1 == 2) c = c + 1; c = c + 10
    likha(c)
""", "REFUSED"),
 ("two statements on one line inside an indented body (both in the body)", """mukhya()
    vitti c = 0
    yadi (1 == 2)
        c = c + 1; c = c + 10
    likha(c)
""", "0"),
 ("tab-indented body", "mukhya()\n\tvitti c = 0\n\tyadi (1 == 1)\n\t\tc = c + 1\n\t\tc = c + 1\n\tlikha(c)\n", "2"),
]


def run(compiler, src, work):
    p = os.path.join(work, 't.sm')
    open(p, 'w').write(src)
    b = os.path.join(work, 't')
    if os.path.exists(b):
        os.remove(b)
    c = subprocess.run([compiler, p, b], capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(compiler)))
    if c.returncode != 0:
        msg = [l.strip() for l in (c.stdout + c.stderr).strip().split('\n') if 'Error' in l]
        return 'REFUSED: ' + (msg[0][:70] if msg else f'exit {c.returncode}')
    try:
        r = subprocess.run([b], capture_output=True, text=True, timeout=2)
        return r.stdout.strip()[:40] or f'(exit {r.returncode})'
    except subprocess.TimeoutExpired:
        return 'HANGS'


def main():
    comps = sys.argv[1:]
    work = tempfile.mkdtemp()
    names = [os.path.basename(os.path.dirname(os.path.abspath(c))) + '/' + os.path.basename(c) for c in comps]
    print('| construct (indented body) | expected | ' + ' | '.join(names) + ' |')
    print('|---|---|' + '---|' * len(comps))
    bad = [0] * len(comps)
    for name, src, want in CASES:
        res = [run(c, src, work) for c in comps]
        for k, r in enumerate(res):
            if not (r == want or (want == 'REFUSED' and r.startswith('REFUSED'))):
                bad[k] += 1
        cells = [(r if (r == want or (want == 'REFUSED' and r.startswith('REFUSED'))) else f'**{r}**') for r in res]
        print(f'| {name} | {want} | ' + ' | '.join(cells) + ' |')
    print()
    for n, b in zip(names, bad):
        print(f'{n}: {len(CASES) - b}/{len(CASES)} as written')


if __name__ == '__main__':
    main()

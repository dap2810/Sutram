#!/usr/bin/env python3
"""R77 WS2 (Gemini: "silent partial compilation"): no token may be dropped. A stray token in statement position,
at the end of a statement's line, as a body's first line, or after a header - in every kind of body, indented and
braced - must make the compile FAIL, or the program must run every statement written (it prints 111; `krama`
in a loop legitimately prints 101).

    python3 -B tests/r77_format/test_stray_tokens.py [--compiler ./sutram_compiler]

Why it holds (v273): every body loop (parse_func_block, the indented-body loop r70_indent_body, parse_block)
leaves only at end of input, `}` or a dedent; every other token goes to parse_stmt, which refuses what it cannot
parse; a dedent or `}` hands the token to the enclosing loop; and parse_program refuses anything but end of input
after mukhya (R71). So a token is consumed by a statement or the compile fails. This test keeps it that way.
Last line: `r77 stray: N checks, M failed`.
"""
import os, subprocess, sys, tempfile

STRAYS = [')', ']', '}', ',', ';', ':', '=', '+', '*', '.', 'anya', 'bhavana 1:', 'tak', 'paryantam', 'arabhya', 'yavat',
          'mukhya()', 'prakriya g(a)', 'vitti', 'kosh', 'mala', 'sutra', 'yoj ganita', 'siddhi', 'dosh', 'prasar', 'krama',
          'guna', 'kuru', 'yadi', 'chakra', 'mandapa', '{', '5', '"s"', 'zz', '0 - 1', '(', '[', '|', '&&', '!', '@', '$', '\\']
TRAIL = [')', ']', '}', ',', ';', ':', '=', '+', '.', 'anya', 'tak', '5', 'zz', '"s"', '(', '[', '{']


def body_progs(stray):
    body = f'        c = c + 1\n        {stray}\n        c = c + 10\n'
    yield 'mukhya', f'mukhya()\n    vitti c = 0\n    c = c + 1\n    {stray}\n    c = c + 10\n    c = c + 100\n    likha(c)\n'
    yield 'mukhya{}', f'mukhya() {{\n    vitti c = 0\n    c = c + 1\n    {stray}\n    c = c + 10\n    c = c + 100\n    likha(c)\n}}\n'
    yield 'prakriya', f'prakriya f(c)\n    c = c + 1\n    {stray}\n    c = c + 10\n    nivartanam c\nmukhya()\n    likha(f(0) + 100)\n'
    yield 'prakriya{}', f'prakriya f(c) {{\n    c = c + 1\n    {stray}\n    c = c + 10\n    nivartanam c\n}}\nmukhya() {{\n    likha(f(0) + 100)\n}}\n'
    for kind, hdr in (('yadi', 'yadi (1 == 1)'), ('yavat', 'yavat (c < 1)'), ('chakra', 'chakra k = 1 tak 1'),
                      ('mandapa', 'mandapa'), ('kuru', 'kuru')):
        tail = '    yavat (c < 1)\n' if kind == 'kuru' else ''
        yield kind, f'mukhya()\n    vitti c = 0\n    {hdr}\n{body}{tail}    c = c + 100\n    likha(c)\n'
        yield kind + '{}', f'mukhya()\n    vitti c = 0\n    {hdr} {{\n{body}    }}\n{tail}    c = c + 100\n    likha(c)\n'


def trail_progs(s):
    yield 'end of a line, indented body', f'mukhya()\n    vitti c = 0\n    yadi (1 == 1)\n        c = c + 1 {s}\n        c = c + 10\n    c = c + 100\n    likha(c)\n'
    yield 'end of a line, braced body', f'mukhya() {{\n    vitti c = 0\n    yadi (1 == 1) {{\n        c = c + 1 {s}\n        c = c + 10\n    }}\n    c = c + 100\n    likha(c)\n}}\n'
    yield 'end of a line, braceless mukhya', f'mukhya()\n    vitti c = 1\n    c = c + 10 {s}\n    c = c + 100\n    likha(c)\n'
    yield "a body's first line", f'mukhya()\n    vitti c = 0\n    yadi (1 == 1)\n        {s}\n        c = c + 1\n        c = c + 10\n    c = c + 100\n    likha(c)\n'
    yield 'after a header', f'mukhya()\n    vitti c = 0\n    yadi (1 == 1) {s}\n        c = c + 1\n        c = c + 10\n    c = c + 100\n    likha(c)\n'


def main():
    here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(os.path.dirname(here))
    comp = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1]) if '--compiler' in sys.argv \
        else os.path.join(root, 'sutram_compiler')
    work = tempfile.mkdtemp(); t = os.path.join(work, 's')
    checks = failed = 0
    cases = [(k, s, p) for s in STRAYS for k, p in body_progs(s)] + [(k, s, p) for s in TRAIL for k, p in trail_progs(s)]
    for kind, stray, src in cases:
        open(t + '.sm', 'w').write(src)
        if os.path.exists(t):
            os.remove(t)
        c = subprocess.run([comp, t + '.sm', t], capture_output=True, text=True, timeout=20, cwd=root)
        checks += 1
        if c.returncode != 0 or not os.path.exists(t):
            continue                                   # refused: fine
        try:
            out = subprocess.run([t], capture_output=True, text=True, timeout=5).stdout.strip()
        except subprocess.TimeoutExpired:
            out = 'HANG'
        if out == '111' or (stray == 'krama' and kind.startswith(('yavat', 'chakra', 'kuru')) and out == '101'):
            continue
        failed += 1
        print(f'FAIL  {kind}, stray {stray!r}: compiled and printed {out[:30]!r} - a statement was dropped')
    print(f'r77 stray: {checks} checks, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())

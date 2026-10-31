#!/usr/bin/env python3
"""R77 (Gemini's mutator): the same program, saved the way a Windows editor or a careless student saves it,
must compile to the same behaviour.

    python3 -B tests/r77_format/test_format_mutator.py [--compiler ./sutram_compiler] [--only NAME]

For every example with a golden (tests/expect/NAME.out), each mutation below is written next to the original
(examples/.r77_NAME_MUT.sm, removed afterwards) and compiled:
  crlf          every line ends in \\r\\n
  trailing      spaces and a tab after every line
  blank_ws      after every indented line, a line holding only spaces, and one holding only a tab
  tabs          each 4-space indentation step written as one tab (programs indented in steps of 4 only)
  no_eol        no newline at the end of the file
  extra_eol     three blank lines at the end of the file
  bom           a UTF-8 byte-order mark at the start (Windows Notepad writes one)
  mixed_alt     every other indented line's 4-space steps written as tabs (Muse R77's mutation)
  mixed_deep    lines two or more levels deep in tabs, one level deep in spaces - a body in tabs under a
                header in spaces (before v274 this ran a body's second line unconditionally - silently)
A program that compiles must still compile and give the golden's output and exit code; a refusal golden
(NAME.compile_fail) must still be refused - except a refusal fixture that itself contains a tab (276, the
mixed-indentation refusal), which is skipped: re-whitespacing it makes a different program. For the two MIXED mutations, a refusal with E_ANTARAL_MISHRA
(tabs and spaces cannot be compared) is also right; any other error, or different output, is a failure.
Last line: `r77 format: N checks, M failed`.
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tests'))
import run_tests as RT  # noqa: E402

def m_crlf(s): return s.replace('\n', '\r\n')
def m_trailing(s): return '\n'.join((l + '  \t') if l.strip() else l for l in s.split('\n'))
def m_blank_ws(s):
    out = []
    for l in s.split('\n'):
        out.append(l)
        if l.startswith((' ', '\t')) and l.strip() and not l.strip().startswith('#'):
            ind = l[:len(l) - len(l.lstrip(' \t'))]
            out.append(ind + '    ')
            out.append('\t')
    return '\n'.join(out)
def blank_ws_line(s, n):
    # R80: where m_blank_ws puts the program's line n - two lines are added after each indented line
    # before it - so a run-time error that names its line ("pankti 7") is checked at the moved line.
    # A line in another file ("pankti 3 (module.smlib)") is not moved: only the program is mutated.
    ls = s.split('\n')[:n - 1]
    return n + 2 * sum(1 for l in ls if l.startswith((' ', '\t')) and l.strip() and not l.strip().startswith('#'))
def m_tabs(s):
    lines = s.split('\n')
    for l in lines:
        ind = len(l) - len(l.lstrip(' '))
        if l.strip() and (ind % 4 or l[ind:ind + 1] == '\t'):
            return None
    return '\n'.join(('\t' * ((len(l) - len(l.lstrip(' '))) // 4) + l.lstrip(' ')) if l.strip() else l for l in lines)
def _steps(l):
    ind = len(l) - len(l.lstrip(' '))
    return ind, l[ind:]
def m_mixed_alt(s):
    out, k = [], 0
    for l in s.split('\n'):
        ind, rest = _steps(l)
        if l.strip() and ind and ind % 4 == 0 and not l[ind:ind + 1] == '\t':
            k += 1
            if k % 2 == 0:
                l = '\t' * (ind // 4) + rest
        out.append(l)
    return '\n'.join(out)
def m_mixed_deep(s):
    out = []
    for l in s.split('\n'):
        ind, rest = _steps(l)
        if l.strip() and ind >= 8 and ind % 4 == 0:
            l = '    ' + '\t' * (ind // 4 - 1) + rest
        out.append(l)
    return '\n'.join(out)
def m_no_eol(s): return s.rstrip('\n')
def m_extra_eol(s): return s.rstrip('\n') + '\n\n\n\n'
def m_bom(s): return '﻿' + s
MUTS = [('crlf', m_crlf), ('trailing', m_trailing), ('blank_ws', m_blank_ws), ('tabs', m_tabs),
        ('no_eol', m_no_eol), ('extra_eol', m_extra_eol), ('bom', m_bom),
        ('mixed_alt', m_mixed_alt), ('mixed_deep', m_mixed_deep)]
MIXED = ('mixed_alt', 'mixed_deep')


def main():
    comp = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1]) if '--compiler' in sys.argv \
        else os.path.join(ROOT, 'sutram_compiler')
    only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
    checks = failed = 0
    fails = {}
    for name in RT.tests():
        if only and name != only:
            continue
        out_p = os.path.join(RT.EXPECT, name + '.out')
        if not os.path.exists(out_p):
            continue
        refusal = os.path.exists(os.path.join(RT.EXPECT, name + '.compile_fail'))
        want_out = open(out_p).read()
        want_code = open(os.path.join(RT.EXPECT, name + '.exit')).read().strip()
        src = open(os.path.join(RT.EXAMPLES, name + '.sm'), encoding='utf-8').read()
        if refusal and '\t' in src:
            continue                  # a refusal fixture ABOUT whitespace (276): re-whitespacing it changes the test
        for mname, f in MUTS:
            text = f(src)
            if text is None:
                continue
            mp = os.path.join(RT.EXAMPLES, f'.r77_{name}_{mname}.sm')
            binp = f'/tmp/r77_{name}_{mname}.bin'
            try:
                open(mp, 'w', encoding='utf-8', newline='').write(text)
                if os.path.exists(binp):
                    os.remove(binp)
                cmd = [comp] + (['--lang', RT.LANG[name]] if name in RT.LANG else []) + [mp, binp]
                c = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=RT.CWD.get(name, ROOT))
                checks += 1
                if refusal:
                    ok = c.returncode != 0
                    why = 'a refusal golden now compiles'
                else:
                    if c.returncode != 0 or not os.path.exists(binp):
                        msg = c.stdout + c.stderr
                        ok = mname in MIXED and 'E_ANTARAL_MISHRA' in msg
                        why = 'no longer compiles: ' + msg.strip().split('\n')[0][:90]
                    else:
                        try:
                            r = subprocess.run([binp], input=RT.STDIN.get(name, ''), capture_output=True, text=True,
                                               timeout=RT.TIMEOUT, cwd=RT.CWD.get(name, ROOT))
                            want = want_out
                            if mname == 'blank_ws':
                                want = re.sub(r'pankti (\d+)(?! \()', lambda m: 'pankti %d' % blank_ws_line(src, int(m.group(1))), want)
                            ok = r.stdout == want and str(r.returncode) == want_code
                            why = f'output or exit differs (exit {r.returncode})'
                        except subprocess.TimeoutExpired:
                            ok, why = False, 'hangs'
                if not ok:
                    failed += 1
                    fails.setdefault(mname, []).append(f'{name}: {why}')
            finally:
                for p in (mp, binp):
                    if os.path.exists(p):
                        os.remove(p)
    for mname, lst in fails.items():
        print(f'FAIL  {mname}: {len(lst)} program(s)')
        for x in lst[:12]:
            print('      ' + x)
    print(f'r77 format: {checks} checks, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())

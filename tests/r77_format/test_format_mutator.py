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
A program that compiles must still compile and give the golden's output and exit code; a refusal golden
(NAME.compile_fail) must still be refused. Last line: `r77 format: N checks, M failed`.
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
def m_tabs(s):
    lines = s.split('\n')
    for l in lines:
        ind = len(l) - len(l.lstrip(' '))
        if l.strip() and (ind % 4 or l[ind:ind + 1] == '\t'):
            return None
    return '\n'.join(('\t' * ((len(l) - len(l.lstrip(' '))) // 4) + l.lstrip(' ')) if l.strip() else l for l in lines)
def m_no_eol(s): return s.rstrip('\n')
def m_extra_eol(s): return s.rstrip('\n') + '\n\n\n\n'
def m_bom(s): return '﻿' + s
MUTS = [('crlf', m_crlf), ('trailing', m_trailing), ('blank_ws', m_blank_ws), ('tabs', m_tabs),
        ('no_eol', m_no_eol), ('extra_eol', m_extra_eol), ('bom', m_bom)]


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
                        ok, why = False, 'no longer compiles: ' + (c.stdout + c.stderr).strip().split('\n')[0][:90]
                    else:
                        r = subprocess.run([binp], input=RT.STDIN.get(name, ''), capture_output=True, text=True,
                                           timeout=RT.TIMEOUT, cwd=RT.CWD.get(name, ROOT))
                        ok = r.stdout == want_out and str(r.returncode) == want_code
                        why = f'output or exit differs (exit {r.returncode})'
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

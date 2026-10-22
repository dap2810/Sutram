#!/usr/bin/env python3
"""ROUND-38: the allocation-failure switch, and what the library does when an allocation fails.

  sutram_compiler --fail-alloc N <in.sm> <out>
compiles <in.sm> exactly as the ordinary compile does, except that in the program it writes
the Nth allocation (counted in the order the program runs them, from 1) returns 0 without
calling mmap. No machine runs out of memory on demand, so before this the "allocation
failed" path of a library function could only be read, never run.

  1. THE SWITCH: the Nth allocation and only it is 0; N past the last changes nothing; the
     environment is still found after the two arguments are dropped (SUTRAM_LANG works);
     N = 0, a non-decimal N, N >= 10^9, a missing argument, a .exe output and another mode
     after it (--object) are refused, with no output file.
  2. EVERY ALLOCATING LIBRARY FUNCTION, at EVERY allocation it makes: the program exits 0
     with the function's documented failure value, and the caller's buffer is as the
     contract says (sets and maps: out unchanged; formatters: only the terminator; the sort:
     the array unchanged; brihat: res unchanged). Before R38 the same calls had 37 fault
     points and all 37 were SIGSEGV (Claude-to-Sarvam/evidence-r38/sweep-before.txt);
     brihat_ghatmod now allocates its scratch once, so it has 3 where it had 7.
  3. THE COUNT: each function makes exactly the number of allocations listed here (one more
     N gives the ordinary result), so a new unchecked allocation is a new fault point that
     this test does not yet expect, and fails it.
  4. THE CONTROLS: the functions that already checked (suchi, avali, nighantu_srij,
     nighantu_vardh, mala_nava) still return their 0.
Linux only. No network.
usage: python3 -B tests/r38/test_fail_alloc.py [--compiler PATH]
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]

SETS = '''    vitti a = rakh_srij(4)
    vitti b = rakh_srij(4)
    vitti o = rakh_srij(8)
    rakh_yuj(a, 4, "x", 1)
    rakh_yuj(a, 4, "y", 1)
    rakh_yuj(b, 4, "y", 1)
'''
# name: (module, setup, call, setup allocations, own allocations, failure output, after-check)
# The after-check is printed after the call: what the caller's buffer holds.
PROBES = {
    'rakh_samroop_diff': ('sangrah', SETS, 'rakh_samroop_diff(a, 4, b, 4, o)', 3, 2, '-1', 'rakh_maap(o)', '0'),
    'rakh_sangam': ('sangrah', SETS, 'rakh_sangam(a, 4, b, 4, o)', 3, 2, '-1', 'rakh_maap(o)', '0'),
    'rakh_sampat': ('sangrah', SETS, 'rakh_sampat(a, 4, b, 4, o)', 3, 1, '-1', 'rakh_maap(o)', '0'),
    'rakh_bhed': ('sangrah', SETS, 'rakh_bhed(a, 4, b, 4, o)', 3, 1, '-1', 'rakh_maap(o)', '0'),
    'rakh_asti_upasamuh': ('sangrah', SETS, 'rakh_asti_upasamuh(b, 4, a, 4)', 3, 1, '-1', '0', '0'),
    'rakh_sam': ('sangrah', SETS, 'rakh_sam(b, 4, b, 4)', 3, 2, '-1', '0', '0'),
    'rakh_tak_mala': ('sangrah', SETS + '    vitti t = nirmmita(64 * 8)\n', 'rakh_tak_mala(a, 4, t)', 4, 4, '-1',
                      't[0]', '0'),
    'nighantu_mil': ('nighantu', '''    vitti a = nighantu_srij(4)
    vitti b = nighantu_srij(4)
    nighantu_khip(a, 4, "k", 1, 5)
''', 'nighantu_mil(b, 4, a, 4)', 2, 1, '-1', 'nighantu_maap(b)', '0'),
    'brihat_shesh': ('brihat', '''    vitti x = nirmmita(16 * 8)
    vitti m = nirmmita(8 * 8)
    vitti r = nirmmita(8 * 8)
    brihat_ank_se_int(12345, x, 16)
    brihat_ank_se_int(97, m, 8)
    brihat_ank_se_int(7, r, 8)
''', 'brihat_shesh(x, m, r, 8)', 3, 1, '-1', 'brihat_ank_tak_int(r, 8)', '7'),
    'brihat_ghatmod': ('brihat', '''    vitti x = nirmmita(8 * 8)
    vitti m = nirmmita(8 * 8)
    vitti r = nirmmita(8 * 8)
    brihat_ank_se_int(3, x, 8)
    brihat_ank_se_int(97, m, 8)
    brihat_ank_se_int(7, r, 8)
''', 'brihat_ghatmod(x, 5, m, r, 8)', 3, 3, '-1', 'brihat_ank_tak_int(r, 8)', '7'),
    'brihat_ank_tak': ('aadhar', '''    vitti x = nirmmita(4 * 8)
    vitti o = nirmmita(16 * 8)
    brihat_ank_se_int(13, x, 4)
    o[0] = 9
''', 'brihat_ank_tak(x, 4, 2, o)', 2, 2, '-1', 'o[0]', '9'),
    'mil_shreni': ('shreni', '''    vitti a = nirmmita(4 * 8)
    a[0] = 3
    a[1] = 1
    a[2] = 2
    a[3] = 0
''', 'mil_shreni(a, 4)', 1, 1, '-1', 'a[0] * 1000 + a[1] * 100 + a[2] * 10 + a[3]', '3120'),
    'roop_ank': ('roop', '    vitti o = nirmmita(32)\n    akshar_rakh(o, 0, 65)\n', 'roop_ank(42, o)', 1, 1, '0',
                 'akshar(o, 0)', '0'),
    'roop_ank_aadhar': ('roop', '    vitti o = nirmmita(80)\n    akshar_rakh(o, 0, 65)\n', 'roop_ank_aadhar(42, 2, 0, o)',
                        1, 1, '0', 'akshar(o, 0)', '0'),
    'roop_varg_ank': ('roop', '    vitti o = nirmmita(40)\n    akshar_rakh(o, 0, 65)\n', 'roop_varg_ank(1234567, 1, o)',
                      1, 2, '0', 'akshar(o, 0)', '0'),
    'roop_sthir': ('roop', '    vitti o = nirmmita(40)\n    akshar_rakh(o, 0, 65)\n', 'roop_sthir(3.25, 2, o)', 1, 2, '0',
                   'akshar(o, 0)', '0'),
    'roop_chinhit': ('roop', '    vitti o = nirmmita(40)\n    akshar_rakh(o, 0, 65)\n', 'roop_chinhit(42, o)', 1, 2, '0',
                     'akshar(o, 0)', '0'),
    'roop_sign_akshar': ('roop', '    vitti o = nirmmita(40)\n    akshar_rakh(o, 0, 65)\n', 'roop_sign_akshar(42, 32, o)',
                         1, 2, '0', 'akshar(o, 0)', '0'),
    'ank_tak_varna': ('vakyank', '    vitti o = nirmmita(24 * 8)\n    o[0] = 65\n', 'ank_tak_varna(42, o)', 1, 1, '0',
                      'o[0]', '0'),
    'ank_tak_aadhar_varna': ('vakyank', '    vitti o = nirmmita(72 * 8)\n    o[0] = 65\n',
                             'ank_tak_aadhar_varna(42, 2, o)', 1, 1, '0', 'o[0]', '0'),
    # controls: these checked their allocation before R38 (R9, R35, R36)
    'suchi_srij': ('suchi', '', 'suchi_srij(4) != 0', 0, 2, '0', '0', '0'),
    'suchi_khip': ('suchi', '    vitti l = suchi_srij(1)\n    suchi_khip(l, 1)\n', 'suchi_khip(l, 2)', 2, 1, '0',
                   'suchi_maap(l)', '1'),
    'avali_srij': ('suchi', '', 'avali_srij(4) != 0', 0, 2, '0', '0', '0'),
    'avali_pravesh': ('suchi', '    vitti q = avali_srij(1)\n    avali_pravesh(q, 1)\n', 'avali_pravesh(q, 2)', 2, 1, '0',
                      '0', '0'),
    'nighantu_srij': ('nighantu', '', 'nighantu_srij(4) != 0', 0, 1, '0', '0', '0'),
    'nighantu_vardh': ('nighantu', '    vitti m = nighantu_srij(2)\n    nighantu_khip(m, 2, "k", 1, 5)\n',
                       'nighantu_vardh(m, 8) != 0', 1, 2, '0', 'nighantu_maap(m)', '1'),
    'mala_nava': ('mala', '', 'mala_nava(4) != 0', 0, 1, '0', '0', '0'),
}

# a program of three allocations, for the switch itself
THREE = '''mukhya() {
    vitti a = nirmmita(64)
    vitti b = nirmmita(64)
    vitti c = nirmmita(64)
    likha(a == 0)
    likha(b == 0)
    likha(c == 0)
}
'''
LOOP = '''mukhya() {
    vitti i = 0
    yavat (i < 6) {
        likha(nirmmita(8) == 0)
        i = i + 1
    }
}
'''


def program(name):
    mod, setup, call, _s, _o, _f, after, _a = PROBES[name]
    return f'yoj {mod}\nmukhya() {{\n{setup}    likha({call})\n    likha({after})\n}}\n'


def main(argv) -> int:
    comp = os.path.abspath(argv[argv.index('--compiler') + 1]) if '--compiler' in argv else str(ROOT / 'sutram_compiler')
    work = Path(tempfile.mkdtemp(prefix='r38-fail-alloc-'))
    passed = failed = points = 0

    def check(ok, what):
        nonlocal passed, failed
        if ok:
            passed += 1
        else:
            failed += 1
            print('FAIL', what)

    def build_run(src_text, n, stem='p', env=None):
        src, exe = work / f'{stem}.sm', work / stem
        src.write_text(src_text, encoding='utf-8')
        exe.unlink(missing_ok=True)
        args = [comp, str(src), str(exe)] if n is None else [comp, '--fail-alloc', str(n), str(src), str(exe)]
        r = subprocess.run(args, capture_output=True, cwd=ROOT, env=env, timeout=60)
        if r.returncode or not exe.exists():
            return 'COMPILE', r.stdout.decode('utf-8', 'replace')[-200:]
        p = subprocess.run([str(exe)], capture_output=True, timeout=20)
        st = 'SIG' + signal.Signals(-p.returncode).name[3:] if p.returncode < 0 else f'rc{p.returncode}'
        return st, p.stdout.decode('utf-8', 'replace')

    # 1. the switch
    for n, want in ((1, '1\n0\n0\n'), (2, '0\n1\n0\n'), (3, '0\n0\n1\n'), (4, '0\n0\n0\n'), (999999999, '0\n0\n0\n')):
        got = build_run(THREE, n)
        check(got == ('rc0', want), f'--fail-alloc {n}: want {want!r}, got {got!r}')
    check(build_run(THREE, None) == ('rc0', '0\n0\n0\n'), 'the ordinary compile of the same program')
    got = build_run(LOOP, 4)
    check(got == ('rc0', '0\n0\n0\n1\n0\n0\n'), f'one site run six times, N=4: want the 4th only, got {got!r}')
    env = dict(os.environ, SUTRAM_LANG='hindi')
    src = work / 'three.sm'
    src.write_text(THREE, encoding='utf-8')
    r = subprocess.run([comp, '--fail-alloc', '2', str(src), str(work / 'h')], capture_output=True, env=env, cwd=ROOT)
    check(r.returncode == 0 and 'hindi' in r.stdout.decode('utf-8', 'replace'),
          f'SUTRAM_LANG is still read after the arguments are dropped: {r.stdout[:80]!r}')
    for bad in (['0'], ['x'], [''], ['12a'], ['1000000000'], ['-1'], ['2', str(src)],
                ['2', str(src), str(work / 'o.exe')], ['2', '--object', str(src), str(work / 'o.smo')],
                ['2', str(src), str(work / 'o'), 'extra']):
        outs = [work / 'o', work / 'o.exe', work / 'o.smo']
        for o in outs:
            o.unlink(missing_ok=True)
        args = [comp, '--fail-alloc'] + bad
        if len(bad) == 1:
            args += [str(src), str(work / 'o')]
        r = subprocess.run(args, capture_output=True, cwd=ROOT)
        made = [o.name for o in outs if o.exists()]
        check(not made and b'Prayog' in r.stdout, f'refused: --fail-alloc {" ".join(bad)!r}: wrote {made}, said {r.stdout[:60]!r}')

    # 2-4. the library, at every allocation each function makes
    for name, (mod, setup, call, s, own, fail_v, after, fail_after) in PROBES.items():
        text = program(name)
        plain = build_run(text, None, name)
        check(plain[0] == 'rc0', f'{name}: the ordinary program: {plain!r}')
        for k in range(1, own + 1):
            points += 1
            got = build_run(text, s + k, name)
            want = ('rc0', f'{fail_v}\n{fail_after}\n')
            check(got == want, f'{name}: allocation {k} of {own} fails (N={s + k}): want {want!r}, got {got!r}')
        got = build_run(text, s + own + 1, name)
        check(got == plain, f'{name}: N={s + own + 1} is past its {own} allocations, so it must be the ordinary '
                            f'result {plain!r}; got {got!r} (an allocation more than this test expects?)')
    print(f'r38 fail-alloc: {passed + failed} checks, {points} library fault points, {passed} passed, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

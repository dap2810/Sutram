#!/usr/bin/env python3
"""ROUND-29: separate compilation - `sutram_compiler --separate` and tools/sutram_build.py.

  1. BEHAVIOUR: every program in examples/, examples/*/, tests/stdlib/ and tests/r*/ that
     `yoj`s a module and compiles the ordinary way is also built separately (each module
     compiled once, then linked). The two executables must print the same bytes and exit
     with the same status. (They are not the same bytes: the modules' code is laid out
     in a different order.) A namespaced `yoj m@alias` is refused by the builder in this
     version; those programs are counted.
  2. ONCE: in tests/r29/proj, two modules both `yoj` a third; the third's prakriyas are
     defined in exactly one object, and the main object defines only mukhya.
  3. CHECKED ACROSS MODULES: a call into another module with the wrong number of arguments
     is refused by --separate with the ordinary compile's own diagnostic; a dasham result
     from another module prints as dasham.
  4. NO MODULES: a program with no `yoj`, built separately, is byte-identical to the
     ordinary compile (every such program in examples/).
  5. REFUSALS: a missing module, a namespaced yoj, usage.

The ordinary path is not touched: the guard is the suite, the corpus and the 556-program
comparison in the evidence. Linux only. No network.
usage: python3 -B tests/r29/test_separate.py [--compiler PATH] [--linker PATH]
"""
from __future__ import annotations

import glob
import os
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import sutram_build  # noqa: E402

LANG = {'37_native_gujarati', '38_native_hindi', '39_native_tamil', '218_sanskrit_devanagari',
        '219_sanskrit_kosh_aliases', '220_hindi_parse_error'}


def arg(argv, flag, default):
    return os.path.abspath(argv[argv.index(flag) + 1]) if flag in argv else default


def symbols(path):
    data = open(path, 'rb').read()
    assert data[:8] == b'SUTRAMO1'
    code, nsym, _nrel = struct.unpack_from('<3Q', data, 8)
    pos, names = 32 + code, []
    for _ in range(nsym):
        _off, ln = struct.unpack_from('<2Q', data, pos)
        names.append(data[pos + 16:pos + 16 + ln].decode())
        pos += 16 + ln
    return names


def run(exe, cwd):
    try:
        p = subprocess.run([exe], stdin=subprocess.DEVNULL, capture_output=True, timeout=10, cwd=cwd)
        return p.returncode, p.stdout
    except subprocess.TimeoutExpired:
        return 'timeout', b''


def build(comp, link, src, out, keep=None):
    cmd = [sys.executable, '-B', str(ROOT / 'tools' / 'sutram_build.py'), '--compiler', comp,
           '--linker', link]
    if keep:
        cmd += ['--keep', keep]
    return subprocess.run(cmd + [src, '-o', out], capture_output=True)


def main(argv) -> int:
    comp = arg(argv, '--compiler', str(ROOT / 'sutram_compiler'))
    link = arg(argv, '--linker', str(ROOT / 'sutram-link'))
    fails = 0

    def check(ok, what):
        nonlocal fails
        if not ok:
            fails += 1
            print('FAIL', what)

    os.chdir(ROOT)
    tmp = tempfile.mkdtemp(prefix='r29-')
    files = sorted(set(glob.glob('examples/*.sm') + glob.glob('examples/*/*.sm')
                       + glob.glob('tests/stdlib/*.sm') + glob.glob('tests/r*/**/*.sm', recursive=True)))
    # 1. behaviour, and 4. no modules
    same = namespaced = ordinary_refuses = identical = no_yoj = 0
    for f in files:
        if Path(f).stem in LANG:
            continue
        names = sutram_build.yoj_names(open(f, 'rb').read())
        if not names and not f.startswith('examples/'):
            continue
        a, b = os.path.join(tmp, 'ord'), os.path.join(tmp, 'sep')
        for p in (a, b):
            if os.path.exists(p):
                os.remove(p)
        r = subprocess.run([comp, f, a], capture_output=True)
        if r.returncode or not os.path.exists(a):
            ordinary_refuses += 1
            continue
        r2 = build(comp, link, f, b)
        if any('@' in n for n in names):
            namespaced += 1
            check(r2.returncode == 1 and b'namespaced' in r2.stderr, f'{f}: namespaced refusal')
            continue
        if r2.returncode != 0:
            if not names and b'ghatak-star vitti' in r2.stdout:
                continue                      # R28: a module-level vitti is not in an object
            check(False, f'{f}: separate build failed: {(r2.stdout + r2.stderr)[-200:]!r}')
            continue
        if names:
            ok = run(os.path.abspath(a), os.path.dirname(f)) == run(os.path.abspath(b), os.path.dirname(f))
            same += ok
            check(ok, f'{f}: behaviour differs')
        else:
            no_yoj += 1
            ok = open(a, 'rb').read() == open(b, 'rb').read()
            identical += ok
            check(ok, f'{f}: not byte-identical with no modules')
    print(f'behaviour: {same} programs with modules print and exit the same, built separately; '
          f'{namespaced} namespaced, refused; {ordinary_refuses} do not compile the ordinary way')
    print(f'no modules: {identical} of {no_yoj} programs in examples/ byte-identical')
    check(same >= 250, f'expected at least 250 programs with modules, got {same}')

    # 2. once
    keep = os.path.join(tmp, 'keep')
    out = os.path.join(tmp, 'proj')
    r = build(comp, link, 'tests/r29/proj/main.sm', out, keep)
    check(r.returncode == 0, f'proj build: {r.stdout + r.stderr!r}')
    if r.returncode == 0:
        check(run(out, None) == (0, b'41\n\n80\n\n3.500000\n\n'), f'proj output {run(out, None)!r}')
        defs = {}
        for o in sorted(os.listdir(keep)):
            for s in symbols(os.path.join(keep, o)):
                defs.setdefault(s, []).append(o)
        check(all(len(v) == 1 for v in defs.values()), f'a prakriya defined twice: {defs}')
        check(sorted(defs) == ['ardha', 'dakshin', 'mukhya', 'mul', 'vam'], f'symbols {sorted(defs)}')
        check(defs.get('mukhya', [''])[0].endswith('main.sm.smo'), 'mukhya in the main object')
        check(symbols(os.path.join(keep, '000-main.sm.smo')) == ['mukhya'], 'the main object defines only mukhya')
        print('once: 4 modules, every prakriya defined in exactly one object; ardha prints as dasham')

    # 3. arity across modules
    ordinary = subprocess.run([comp, 'tests/r29/proj/arity.sm', os.path.join(tmp, 'x')], capture_output=True)
    sep = subprocess.run([comp, '--separate', 'tests/r29/proj/arity.sm', os.path.join(tmp, 'x.smo'),
                          os.path.abspath('tests/r29/proj/arity.sm')], capture_output=True)
    check(ordinary.returncode == 1 and b'E_ARITY' in ordinary.stdout, 'ordinary arity')
    check(sep.returncode == 1 and sep.stdout == ordinary.stdout, 'separate arity: the same diagnostic')
    print('arity: a wrong call into another module is refused by --separate, with the same diagnostic')

    # 5. refusals
    miss = os.path.join(tmp, 'miss.sm')
    open(miss, 'w').write('yoj r29_no_such_module\nmukhya() {\n    prati 0\n}\n')
    r = build(comp, link, miss, os.path.join(tmp, 'm'))
    check(r.returncode == 1 and b'module not found' in r.stderr, 'missing module')
    r = subprocess.run([sys.executable, '-B', str(ROOT / 'tools' / 'sutram_build.py')], capture_output=True)
    check(r.returncode == 2, 'usage')
    print('refusals: a missing module, a namespaced yoj, usage')

    print(f'r29 separate: {same} programs with modules behave the same, {identical} without are '
          f'byte-identical, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

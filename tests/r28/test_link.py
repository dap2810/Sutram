#!/usr/bin/env python3
"""ROUND-28: the object file and our linker - and the guard that the ordinary path did not change.

  1. IDENTITY: every program in examples/ that compiles directly is also compiled with
     `--object` and linked alone by sutram-link; the two executables must be
     byte-identical. (A module-level vitti is refused in --object mode, so those
     programs are counted, not compared.)
  2. TWO MODULES: a program whose prakriyas live in two separately compiled
     objects links into one binary that prints the right values, in either
     argument order, including a call from the library back into the main object.
  3. THE ERRORS: an undefined prakriya, a duplicate one, no mukhya, two mukhyas, a file
     that is not an object, a truncated object, a missing file.

The ordinary path is not touched by any of this: run the suite and the corpus
for that. Linux only. No network.
usage: python3 -B tests/r28/test_link.py [--compiler PATH] [--linker PATH]
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
LANG = {'37_native_gujarati': 'gujarati', '38_native_hindi': 'hindi', '39_native_tamil': 'tamil',
        '218_sanskrit_devanagari': 'sanskrit', '219_sanskrit_kosh_aliases': 'sanskrit',
        '220_hindi_parse_error': 'hindi'}


def arg(argv, flag, default):
    return os.path.abspath(argv[argv.index(flag) + 1]) if flag in argv else default


def main(argv) -> int:
    comp = arg(argv, '--compiler', str(ROOT / 'sutram_compiler'))
    link = arg(argv, '--linker', str(ROOT / 'sutram-link'))
    fails = 0
    checks = 0

    def check(ok, what):
        nonlocal fails, checks
        checks += 1
        fails += not ok
        if not ok:
            print('FAIL  ' + what)

    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        same = refused = direct_fail = 0
        for src in sorted((ROOT / 'examples').glob('*.sm')):
            env = {k: v for k, v in os.environ.items() if not k.startswith('SUTRAM_')}
            if src.stem in LANG:
                env['SUTRAM_LANG'] = LANG[src.stem]
            d = subprocess.run([comp, str(src), str(t / 'd.bin')], capture_output=True, cwd=str(ROOT), env=env, timeout=60)
            if d.returncode != 0:
                direct_fail += 1             # a compile-fail example: nothing to compare
                continue
            o = subprocess.run([comp, '--object', str(src), str(t / 'o.smo')], capture_output=True, cwd=str(ROOT), env=env, timeout=60)
            if o.returncode != 0 and b'vastu-patre ghatak-star vitti' in o.stdout:
                refused += 1
                continue
            ok = o.returncode == 0
            if ok:
                l = subprocess.run([link, str(t / 'l.bin'), str(t / 'o.smo')], capture_output=True, timeout=60)
                ok = l.returncode == 0 and (t / 'l.bin').read_bytes() == (t / 'd.bin').read_bytes()
            check(ok, 'identity: %s (object %d)' % (src.name, o.returncode))
            same += ok
        print('PASS  identity: %d programs byte-identical through --object + sutram-link; %d refused '
              '(a module-level vitti); %d do not compile directly (compile-fail examples)' % (same, refused, direct_fail))

        # two modules
        (t / 'lib.sm').write_text('prakriya varg(x) {\n    prati x * x\n}\n\nprakriya yog_varg(a, b) {\n'
                                  '    prati varg(a) + varg(b) + upar(1)\n}\n')
        (t / 'main.sm').write_text('prakriya upar(x) {\n    prati x + 100\n}\n\nprakriya dvigun(x) {\n    prati 2 * x\n}\n\n'
                                   'mukhya() {\n    likha(yog_varg(3, 4))\n    likha(dvigun(varg(5)))\n}\n')
        for name in ('lib', 'main'):
            r = subprocess.run([comp, '--object', str(t / (name + '.sm')), str(t / (name + '.smo'))], capture_output=True, timeout=60)
            check(r.returncode == 0, 'two modules: --object %s.sm' % name)
        for order in (('lib', 'main'), ('main', 'lib')):
            r = subprocess.run([link, str(t / 'two.bin')] + [str(t / (n + '.smo')) for n in order], capture_output=True, timeout=60)
            out = subprocess.run([str(t / 'two.bin')], capture_output=True, timeout=20) if r.returncode == 0 else None
            check(out is not None and out.stdout == b'126\n50\n' and out.returncode == 0,
                  'two modules linked as %s: %r' % ('+'.join(order), out.stdout if out else r.stdout))
        print('PASS  two modules, both orders, calls in both directions')

        # errors
        (t / 'main2.sm').write_text('mukhya() {\n    likha(1)\n}\n')
        subprocess.run([comp, '--object', str(t / 'main2.sm'), str(t / 'main2.smo')], capture_output=True, timeout=60)
        (t / 'short.smo').write_bytes((t / 'lib.smo').read_bytes()[:40])
        cases = [
            ('undefined prakriya', [t / 'main.smo'], b'Sutram Error: agyat prakriya: yog_varg'),
            ('duplicate prakriya', [t / 'main.smo', t / 'lib.smo', t / 'lib.smo'], b'Sutram Error: prakriya dvih paribhashita: varg'),
            ('no mukhya', [t / 'lib.smo'], b'Sutram Error: kasminnapi vastu-patre mukhya nasti'),
            ('two mukhyas', [t / 'main.smo', t / 'main2.smo', t / 'lib.smo'], b'Sutram Error: prakriya dvih paribhashita: mukhya'),
            ('not an object', [t / 'lib.sm'], b'Sutram Error: vastu-patram na'),
            ('a truncated object', [t / 'short.smo'], b'Sutram Error: vastu-patram na'),
            ('a missing file', [t / 'nope.smo'], b'Sutram Error: patram na udghatitam'),
        ]
        for name, inputs, want in cases:
            r = subprocess.run([link, str(t / 'e.bin')] + [str(p) for p in inputs], capture_output=True, timeout=60)
            check(r.returncode == 1 and want in r.stdout, 'error: %s -> %d %r' % (name, r.returncode, r.stdout[:90]))
        r = subprocess.run([link], capture_output=True, timeout=60)
        check(r.returncode == 2 and b'Prayog' in r.stdout, 'usage')
        print('PASS  %d linker errors and the usage line' % (len(cases) + 1))
        # a module-level vitti is refused in --object mode
        (t / 'g.sm').write_text('vitti G = 5\nmukhya() {\n    likha(G)\n}\n')
        r = subprocess.run([comp, '--object', str(t / 'g.sm'), str(t / 'g.smo')], capture_output=True, timeout=60)
        check(r.returncode == 1 and b'vastu-patre ghatak-star vitti asamarthita' in r.stdout, 'a module-level vitti in --object mode')
    print('r28 link: %d checks, %d failed' % (checks, fails))
    return 1 if fails else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

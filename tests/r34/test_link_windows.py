#!/usr/bin/env python3
"""ROUND-34: the Windows linker - `--object` / `--separate` on the Windows compiler, and
sutram-link writing a PE. Run on real Windows, with the Windows binaries.

  1. IDENTITY: every program in examples/ that the Windows compiler compiles directly is
     also compiled with `--object` (a SUTRAMO2 object) and linked alone by sutram-link;
     the two .exe files must be byte-identical, and the linked one runs.
  2. TWO MODULES: two separately compiled objects link into one .exe that prints the
     right values, in either argument order, with calls in both directions.
  3. THE ERRORS: undefined, duplicate, no mukhya, two mukhyas, not an object, truncated,
     missing file, usage - and two R34 ones: a SUTRAMO1 object with a SUTRAMO2 one
     (mixed targets), and more vitti than the PE's .data holds (128).
  4. VITTI: a module-level vitti held in the object is placed in .data (byte-identical to
     the direct compile); tests/r30/proj built separately prints what the one-pass
     compile prints, each vitti defined in one object; a library object refuses an
     initializer, as on Linux.
  5. SEPARATE: every program in examples/, examples/*/, tests/stdlib/ and tests/r*/ that
     `yoj`s a module and compiles directly is built by tools/sutram_build.py (each module
     compiled once with --separate, then linked) and must print the same bytes and exit
     with the same status; tests/r29/proj defines every prakriya in exactly one object;
     a program with no `yoj` built that way is byte-identical.

Windows only. No network. Nothing outside a temporary directory is written.
usage: python -B tests/r34/test_link_windows.py [--compiler PATH] [--linker PATH]
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
STDIN = {'23_grahan_input': b'5\n', '24_guess_game': b'7\n', '26_calculator': b'20\n4\n',
         'number_game': b'3\n', '46_language_reference': b'7\n', '59_windows_grahan_runtime': b'42\n'}


def arg(argv, flag, default):
    return os.path.abspath(argv[argv.index(flag) + 1]) if flag in argv else default


def symbols(path):
    data = open(path, 'rb').read()
    assert data[:8] in (b'SUTRAMO1', b'SUTRAMO2'), data[:8]
    code, nsym, _nrel = struct.unpack_from('<3Q', data, 8)
    pos, out = 32 + code, []
    for _ in range(nsym):
        off, ln = struct.unpack_from('<2Q', data, pos)
        out.append((data[pos + 16:pos + 16 + ln].decode(), off))
        pos += 16 + ln
    return out


def relocations(path):
    data = open(path, 'rb').read()
    code, nsym, nrel = struct.unpack_from('<3Q', data, 8)
    pos = 32 + code
    for _ in range(nsym):
        pos += 16 + struct.unpack_from('<Q', data, pos + 8)[0]
    out = []
    for _ in range(nrel):
        off, ln = struct.unpack_from('<2Q', data, pos)
        out.append((data[pos + 16:pos + 16 + ln].decode(), off))
        pos += 16 + ln
    return out


def run(exe, cwd=None, stdin=b''):
    try:
        p = subprocess.run([exe], input=stdin, capture_output=True, timeout=10, cwd=cwd)
        return p.returncode, p.stdout
    except subprocess.TimeoutExpired:
        return 'timeout', b''


def main(argv) -> int:
    if os.name != 'nt':
        print('r34 link (Windows): NOT-RUN - this gate runs on Windows')
        return 0
    comp = arg(argv, '--compiler', str(ROOT / 'sutram.exe'))
    link = arg(argv, '--linker', str(ROOT / 'sutram-link.exe'))
    fails = 0
    checks = 0

    def check(ok, what):
        nonlocal fails, checks
        checks += 1
        fails += not ok
        if not ok:
            print('FAIL  ' + what)
        return ok

    def sh(cmd, **kw):
        return subprocess.run([str(c) for c in cmd], capture_output=True, timeout=120, **kw)

    os.chdir(ROOT)
    with tempfile.TemporaryDirectory(prefix='r34-') as td:
        t = Path(td)

        # 1. identity
        same = refused = direct_fail = 0
        for src in sorted((ROOT / 'examples').glob('*.sm')):
            if src.stem in LANG:
                continue                     # --object takes no --lang (docs/OBJECT-FORMAT.md)
            for p in ('d.exe', 'o.smo', 'l.exe'):
                if (t / p).exists():
                    (t / p).unlink()
            d = sh([comp, src, t / 'd.exe'], cwd=str(ROOT))
            if d.returncode != 0:
                direct_fail += 1
                continue
            o = sh([comp, '--object', src, t / 'o.smo'], cwd=str(ROOT))
            if o.returncode != 0 and b'vastu-patre ghatak-star vitti' in o.stdout:
                refused += 1
                continue
            ok = o.returncode == 0 and (t / 'o.smo').read_bytes()[:8] == b'SUTRAMO2'
            if ok:
                l = sh([link, t / 'l.exe', t / 'o.smo'])
                ok = l.returncode == 0 and (t / 'l.exe').read_bytes() == (t / 'd.exe').read_bytes()
            if ok and src.stem in ('01_hello', '249_r25_phal', '29_nishkriya') or ok and same % 25 == 0:
                ok = run(str(t / 'l.exe'), str(ROOT), STDIN.get(src.stem, b'')) == \
                    run(str(t / 'd.exe'), str(ROOT), STDIN.get(src.stem, b''))
            check(ok, 'identity: %s (object %d %r)' % (src.name, o.returncode, o.stdout[-120:]))
            same += ok
        print('PASS  identity: %d programs byte-identical through --object + sutram-link; %d refused '
              '(a module-level vitti); %d do not compile directly' % (same, refused, direct_fail))
        check(same >= 150, 'expected at least 150 identical programs, got %d' % same)

        # 2. two modules
        (t / 'lib.sm').write_text('prakriya varg(x) {\n    prati x * x\n}\n\nprakriya yog_varg(a, b) {\n'
                                  '    prati varg(a) + varg(b) + upar(1)\n}\n')
        (t / 'main.sm').write_text('prakriya upar(x) {\n    prati x + 100\n}\n\nprakriya dvigun(x) {\n    prati 2 * x\n}\n\n'
                                   'mukhya() {\n    likha(yog_varg(3, 4))\n    likha(dvigun(varg(5)))\n}\n')
        for name in ('lib', 'main'):
            r = sh([comp, '--object', t / (name + '.sm'), t / (name + '.smo')])
            check(r.returncode == 0, 'two modules: --object %s.sm' % name)
        rel = dict((n, o) for n, o in relocations(t / 'main.smo'))
        check('rt:init' in rel and rel['rt:init'] == 1 and 'rt:syscall' in rel,
              'a W1 object holes the blob: rt:init at 1, rt:syscall present: %r' % sorted(rel))
        for order in (('lib', 'main'), ('main', 'lib')):
            if (t / 'two.exe').exists():
                (t / 'two.exe').unlink()
            r = sh([link, t / 'two.exe'] + [t / (n + '.smo') for n in order])
            out = run(str(t / 'two.exe')) if r.returncode == 0 else None
            check(out == (0, b'126\r\n50\r\n') or out == (0, b'126\n50\n'),
                  'two modules linked as %s: %r %r' % ('+'.join(order), out, r.stdout))
        print('PASS  two modules, both orders, calls in both directions')

        # 3. errors
        (t / 'main2.sm').write_text('mukhya() {\n    likha(1)\n}\n')
        sh([comp, '--object', t / 'main2.sm', t / 'main2.smo'])
        (t / 'short.smo').write_bytes((t / 'lib.smo').read_bytes()[:40])
        (t / 'linux.smo').write_bytes(b'SUTRAMO1' + (t / 'lib.smo').read_bytes()[8:])
        many = lambda k, base: ''.join('vitti %s%d\n' % (base, i) for i in range(k))
        (t / 'g100a.sm').write_text(many(100, 'A') + 'mukhya() {\n    likha(1)\n}\n')
        (t / 'g100b.sm').write_text(many(29, 'B') + 'prakriya b() {\n    prati 2\n}\n')
        (t / 'g28b.sm').write_text(many(28, 'B') + 'prakriya b() {\n    prati 2\n}\n')
        for n in ('g100a', 'g100b', 'g28b'):
            r = sh([comp, '--object', t / (n + '.sm'), t / (n + '.smo')])
            check(r.returncode == 0, '--object %s: %r' % (n, r.stdout))
        cases = [
            ('undefined prakriya', [t / 'main.smo'], b'Sutram Error: agyat prakriya: yog_varg'),
            ('duplicate prakriya', [t / 'main.smo', t / 'lib.smo', t / 'lib.smo'], b'Sutram Error: prakriya dvih paribhashita: varg'),
            ('no mukhya', [t / 'lib.smo'], b'Sutram Error: kasminnapi vastu-patre mukhya nasti'),
            ('two mukhyas', [t / 'main.smo', t / 'main2.smo', t / 'lib.smo'], b'Sutram Error: prakriya dvih paribhashita: mukhya'),
            ('not an object', [t / 'lib.sm'], b'Sutram Error: vastu-patram na'),
            ('a truncated object', [t / 'short.smo'], b'Sutram Error: vastu-patram na'),
            ('a missing file', [t / 'nope.smo'], b'Sutram Error: patram na udghatitam'),
            ('mixed targets', [t / 'main.smo', t / 'linux.smo'], b'Sutram Error: vastu-patrani bhinna-lakshyani'),
            ('129 vitti in .data', [t / 'g100a.smo', t / 'g100b.smo'], b'Sutram Error: ghatak-star vitti seema atikram'),
        ]
        for name, inputs, want in cases:
            r = sh([link, t / 'e.exe'] + inputs)
            check(r.returncode == 1 and want in r.stdout, 'error: %s -> %d %r' % (name, r.returncode, r.stdout[:90]))
        r = sh([link])
        check(r.returncode == 2 and b'Prayog' in r.stdout, 'usage')
        r = sh([link, t / 'g128.exe', t / 'g100a.smo', t / 'g28b.smo'])
        check(r.returncode == 0 and run(str(t / 'g128.exe')) in ((0, b'1\r\n'), (0, b'1\n')),
              'exactly 128 vitti link and run: %r' % (r.stdout,))
        print('PASS  %d linker errors, the usage line, and 128 vitti exactly' % (len(cases) + 1))

        # 4. vitti
        (t / 'g.sm').write_text('vitti G = 5\nvitti H\nmukhya() {\n    H = G * 3\n    likha(G)\n    likha(H)\n}\n')
        r = sh([comp, '--object', t / 'g.sm', t / 'g.smo'])
        d = sh([comp, t / 'g.sm', t / 'gd.exe'])
        l = sh([link, t / 'gl.exe', t / 'g.smo'])
        check(r.returncode == 0 and d.returncode == 0 and l.returncode == 0
              and (t / 'gl.exe').read_bytes() == (t / 'gd.exe').read_bytes()
              and run(str(t / 'gl.exe')) in ((0, b'5\r\n15\r\n'), (0, b'5\n15\n')),
              'a module-level vitti in --object mode: in .data, byte-identical, runs')
        check(dict(symbols(t / 'g.smo')).get('vitti:G') == 0 and dict(symbols(t / 'g.smo')).get('vitti:H') == 8,
              'vitti symbols are data offsets: %r' % symbols(t / 'g.smo'))
        (t / 'gl.sm').write_text('vitti G = 5\nprakriya g() {\n    prati G\n}\n')
        r = sh([comp, '--object', t / 'gl.sm', t / 'gl.smo'])
        check(r.returncode == 1 and b'vastu-patre ghatak-star vitti asamarthita' in r.stdout,
              'an initialized vitti in a library object (no mukhya) is refused')
        keep = t / 'k30'
        r = sh([sys.executable, '-B', ROOT / 'tools' / 'sutram_build.py', '--compiler', comp, '--linker', link,
                '--keep', keep, 'tests/r30/proj/main.sm', '-o', t / 'p30.exe'])
        o = sh([comp, 'tests/r30/proj/main.sm', t / 'o30.exe'])
        ok = check(r.returncode == 0 and o.returncode == 0, 'r30 proj builds: %r' % (r.stdout + r.stderr)[-200:])
        if ok:
            check(run(str(t / 'p30.exe')) == run(str(t / 'o30.exe')), 'r30 proj: separate prints what one-pass prints')
            defs = {}
            for f in sorted(os.listdir(keep)):
                for s, _ in symbols(keep / f):
                    if s.startswith('vitti:'):
                        defs.setdefault(s, []).append(f)
            check(defs and all(len(v) == 1 for v in defs.values()), 'each vitti in one object: %r' % defs)
        print('PASS  vitti: in .data, shared across modules, one copy each')

        # 5. separate
        files = sorted(set(glob.glob('examples/*.sm') + glob.glob('examples/*/*.sm')
                           + glob.glob('tests/stdlib/*.sm') + glob.glob('tests/r*/**/*.sm', recursive=True)))
        files = [f.replace('\\', '/') for f in files]
        sep_same = namespaced = ordinary_refuses = identical = no_yoj = 0
        nondet = []
        for f in files:
            if Path(f).stem in LANG:
                continue
            names = sutram_build.yoj_names(open(f, 'rb').read())
            if not names and not f.startswith('examples/'):
                continue
            a, b = t / 'ord.exe', t / 'sep.exe'
            for p in (a, b):
                if p.exists():
                    p.unlink()
            r = sh([comp, f, a])
            if r.returncode or not a.exists():
                ordinary_refuses += 1
                continue
            r2 = sh([sys.executable, '-B', ROOT / 'tools' / 'sutram_build.py', '--compiler', comp,
                     '--linker', link, f, '-o', b])
            if any('@' in n for n in names):
                namespaced += 1
                check(r2.returncode == 1 and b'namespaced' in r2.stderr, f'{f}: namespaced refusal')
                continue
            if not check(r2.returncode == 0, f'{f}: separate build failed: {(r2.stdout + r2.stderr)[-200:]!r}'):
                continue
            if names:
                cwd = os.path.dirname(os.path.abspath(f))
                stdin = STDIN.get(Path(f).stem, b'')
                first = run(str(a), cwd, stdin)
                if first != run(str(a), cwd, stdin):
                    nondet.append(f)         # the direct build differs from itself: nothing to compare
                    continue
                ok = check(first == run(str(b), cwd, stdin), f'{f}: behaviour differs')
                sep_same += ok
            else:
                no_yoj += 1
                ok = check(a.read_bytes() == b.read_bytes(), f'{f}: not byte-identical with no modules')
                identical += ok
        print(f'PASS  separate: {sep_same} programs with modules print and exit the same; {namespaced} '
              f'namespaced, refused; {ordinary_refuses} do not compile directly; no modules: {identical} of '
              f'{no_yoj} byte-identical')
        if nondet:
            print('NOTE  %d not compared: the direct build prints different bytes on two runs: %s'
                  % (len(nondet), ', '.join(nondet)))
        check(sep_same >= 100, f'expected at least 100 programs with modules, got {sep_same}')
        keep = t / 'k29'
        r = sh([sys.executable, '-B', ROOT / 'tools' / 'sutram_build.py', '--compiler', comp, '--linker', link,
                '--keep', keep, 'tests/r29/proj/main.sm', '-o', t / 'p29.exe'])
        if check(r.returncode == 0, 'r29 proj: %r' % (r.stdout + r.stderr)[-200:]):
            out = run(str(t / 'p29.exe'))
            check(out[0] == 0 and out[1].replace(b'\r\n', b'\n') == b'41\n\n80\n\n3.500000\n\n', 'r29 proj output %r' % (out,))
            defs = {}
            for f in sorted(os.listdir(keep)):
                for s, _ in symbols(keep / f):
                    defs.setdefault(s, []).append(f)
            check(all(len(v) == 1 for v in defs.values()), 'a prakriya defined twice: %r' % defs)
            check(sorted(defs) == ['ardha', 'dakshin', 'mukhya', 'mul', 'vam'], 'symbols %r' % sorted(defs))
        print('PASS  once: every prakriya of tests/r29/proj in exactly one object')

    print('r34 link (Windows): %d checks, %d failed' % (checks, fails))
    return 1 if fails else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

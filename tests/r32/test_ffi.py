#!/usr/bin/env python3
"""ROUND-32: the FFI - a Sutram program calls C functions, declared in a checked sidecar,
read from an ELF object by sutram-elf2smo, linked by sutram-link.

  1. IT WORKS: tests/r32/main.sm (and its module r32_ganit) call four C functions in
     tests/r32/foreign.o - 2, 1, 6 and 0 arguments; one of them reports rsp mod 16 on
     entry, which must be 8 (the C ABI's alignment) at every call depth.
  2. CHECKED: a call with 1 or 3 arguments to a 2-argument declaration is E_ARITY with
     the call's own location, exit 1, and NO object is written.
  3. NOT A PRAKRIYA: the declaration exports nothing; the call is a relocation to the
     FOREIGN name; a prakriya with either name is an error.
  4. THE SIDECAR: every malformed case is refused with its line (v1: i64 only).
  5. THE READER: sutram-elf2smo refuses an object with a relocation (a C function that
     calls out), one with unwind tables, one that is not ELF; and its usage.
  6. OPT-IN: --ffi with no --object/--separate is a usage error; the ordinary compile of
     main.sm is unchanged (it does not know s_add: agyat prakriya).
Linux only. No network. No C compiler needed (the .o files are committed).
usage: python3 -B tests/r32/test_ffi.py [--compiler PATH] [--linker PATH] [--elf2smo PATH]
"""
from __future__ import annotations

import os
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'tests' / 'r32'
HEADER = 'sutram-ffi-v1|linux-x86_64-sysv\n'


def arg(argv, flag, default):
    return os.path.abspath(argv[argv.index(flag) + 1]) if flag in argv else default


def table(path):
    data = open(path, 'rb').read()
    code, nsym, nrel = struct.unpack_from('<3Q', data, 8)
    pos, out = 32 + code, ([], [])
    for k, n in ((0, nsym), (1, nrel)):
        for _ in range(n):
            _off, ln = struct.unpack_from('<2Q', data, pos)
            out[k].append(data[pos + 16:pos + 16 + ln].decode())
            pos += 16 + ln
    return out


def main(argv) -> int:
    comp = arg(argv, '--compiler', str(ROOT / 'sutram_compiler'))
    link = arg(argv, '--linker', str(ROOT / 'sutram-link'))
    e2s = arg(argv, '--elf2smo', str(ROOT / 'sutram-elf2smo'))
    fails = checks = 0

    def check(ok, what):
        nonlocal fails, checks
        checks += 1
        if not ok:
            fails += 1
            print('FAIL', what)

    def run(cmd, **kw):
        return subprocess.run(cmd, capture_output=True, timeout=60, **kw)

    os.chdir(ROOT)
    t = Path(tempfile.mkdtemp(prefix='r32-'))
    sffi = str(HERE / 'ffi.sffi')

    # 1. it works
    b = run([sys.executable, '-B', 'tools/sutram_build.py', '--compiler', comp, '--linker', link,
             '--elf2smo', e2s, '--ffi', sffi, '--foreign', str(HERE / 'foreign.o'), '--keep', str(t / 'k'),
             str(HERE / 'main.sm'), '-o', str(t / 'prog')])
    check(b.returncode == 0, f'build: {b.stdout[-200:]!r} {b.stderr[-200:]!r}')
    if b.returncode == 0:
        p = run([str(t / 'prog')])
        check((p.returncode, p.stdout) == (0, b'42\n91\n-3\n8\n8\n8\n9\n42\n'), f'output {p.stdout!r}')
        print('it works: 4 C functions (2, 1, 6, 0 arguments), from mukhya and from a module; '
              'rsp is 16-byte aligned at every depth')
        # 3. not a prakriya
        syms, rels = table(t / 'k' / '000-main.sm.smo')
        check(syms == ['mukhya', 'gahan'] and 'sutram_ffi_add' in rels
              and not any(n.startswith('s_') for n in syms + rels),
              f'main object: defines {syms}, needs {rels}')
        syms, rels = table(t / 'k' / '001-r32_ganit.smlib.smo')
        check(syms == ['dvigun'] and rels == ['sutram_ffi_add'], f'module object: {syms} {rels}')
        print('not a prakriya: nothing exported for a declaration; each call is a hole named sutram_ffi_add')

    # 2. checked
    for n, args in ((1, '17'), (3, '17, 25, 1')):
        src = t / f'a{n}.sm'
        src.write_text(f'mukhya() {{\n    likha(s_add({args}))\n}}\n')
        obj = t / f'a{n}.smo'
        r = run([comp, '--ffi', sffi, '--object', str(src), str(obj)])
        check(r.returncode == 1 and f'a{n}.sm:2:11: Sutram Error [E_ARITY]'.encode() in r.stdout
              and f"'s_add' ityasmai {n} tarkah dattah; hastakshare 2".encode() in r.stdout
              and not obj.exists(), f'arity {n}: {r.returncode} {r.stdout[:120]!r} written={obj.exists()}')
        r = run([comp, '--ffi', sffi, '--separate', str(src), str(obj), str(src)])
        check(r.returncode == 1 and b'E_ARITY' in r.stdout and not obj.exists(), f'arity {n} --separate')
    print('checked: s_add(17) and s_add(17, 25, 1) are E_ARITY at 2:11, exit 1, no object (--object and --separate)')

    # 3. a prakriya with either name
    for name in ('s_add', 'sutram_ffi_add'):
        src = t / f'c_{name}.sm'
        src.write_text(f'prakriya {name}(a, b) {{\n    prati a\n}}\nmukhya() {{\n    likha({name}(1, 2))\n}}\n')
        r = run([comp, '--ffi', sffi, '--object', str(src), str(t / 'c.smo')])
        check(r.returncode == 1 and b'videshi prakriya-nama anyatra api: ' + name.encode() in r.stdout,
              f'clash {name}: {r.stdout!r}')
    (t / 'bl.sffi').write_text(HEADER + 'likha|1|i64|i64|sutram_ffi_neg\n')
    r = run([comp, '--ffi', str(t / 'bl.sffi'), '--object', str(HERE / 'main.sm'), str(t / 'x.smo')])
    check(r.returncode == 1 and b'anyatra api: likha' in r.stdout, f'clash with a builtin {r.stdout!r}')
    print('not a prakriya: a prakriya named s_add or sutram_ffi_add, or a builtin name, is an error')

    # 4. the sidecar
    bad = {
        'no header': 's_add|2|i64,i64|i64|sutram_ffi_add\n',
        'another header': 'sutram-ffi-v2|linux-x86_64-sysv\n',
        'four fields': HEADER + 's_add|2|i64,i64|i64\n',
        'six fields': HEADER + 's_add|2|i64,i64|i64|sutram_ffi_add|x\n',
        'arity 7': HEADER + 's_add|7|i64,i64,i64,i64,i64,i64,i64|i64|sutram_ffi_add\n',
        'arity 12': HEADER + 's_add|12|i64|i64|sutram_ffi_add\n',
        'kinds short': HEADER + 's_add|2|i64|i64|sutram_ffi_add\n',
        'kinds long': HEADER + 's_add|1|i64,i64|i64|sutram_ffi_add\n',
        'f64 (not in v1)': HEADER + 's_add|2|i64,f64|i64|sutram_ffi_add\n',
        'ptr (not in v1)': HEADER + 's_add|1|ptr|i64|sutram_ffi_add\n',
        'void (not in v1)': HEADER + 's_add|2|i64,i64|void|sutram_ffi_add\n',
        'a space': HEADER + 's_add|2|i64, i64|i64|sutram_ffi_add\n',
        'a CR': HEADER + 's_add|2|i64,i64|i64|sutram_ffi_add\r\n',
        'no final LF': HEADER + 's_add|2|i64,i64|i64|sutram_ffi_add',
        'a bad name': HEADER + '2add|2|i64,i64|i64|sutram_ffi_add\n',
        'a bad symbol': HEADER + 's_add|2|i64,i64|i64|sutram-ffi-add\n',
        'an empty symbol': HEADER + 's_add|2|i64,i64|i64|\n',
        'a name twice': HEADER + 's_add|2|i64,i64|i64|sutram_ffi_add\ns_add|1|i64|i64|sutram_ffi_neg\n',
        'a symbol twice': HEADER + 's_add|2|i64,i64|i64|sutram_ffi_add\ns_b|2|i64,i64|i64|sutram_ffi_add\n',
        'too big': HEADER + ''.join(f'n{k}|0||i64|f{k}\n' for k in range(700)),
        'empty': '',
    }
    for what, text in bad.items():
        f = t / 'bad.sffi'
        f.write_bytes(text.encode())
        r = run([comp, '--ffi', str(f), '--object', str(HERE / 'main.sm'), str(t / 'b.smo')])
        check(r.returncode == 1 and b'videshi-ghoshana-patram dushtam, pankti' in r.stdout, f'sidecar {what}: {r.stdout!r}')
    r = run([comp, '--ffi', str(t / 'missing.sffi'), '--object', str(HERE / 'main.sm'), str(t / 'b.smo')])
    check(r.returncode == 1 and b'dushtam, pankti 0' in r.stdout, f'missing sidecar {r.stdout!r}')
    f = t / 'bad.sffi'
    f.write_bytes(b'x\n')
    r = run([comp, '--ffi', str(f), '--object', str(HERE / 'main.sm'), str(t / 'b.smo')],
            env=dict(os.environ, SUTRAM_LANG='hindi'))
    check(r.returncode == 1 and 'विदेशी-घोषणा फ़ाइल दोषपूर्ण, पंक्ति 1'.encode() in r.stdout, f'in Hindi: {r.stdout!r}')
    print(f'the sidecar: {len(bad) + 1} malformed cases refused with their line; in the SUTRAM_LANG pack too')

    # 5. the reader
    r = run([e2s, str(HERE / 'foreign.o'), str(t / 'f.smo')])
    check(r.returncode == 0 and table(t / 'f.smo') == (['sutram_ffi_add', 'sutram_ffi_neg', 'sutram_ffi_mix',
                                                       'sutram_ffi_rsp'], []), f'reader: {r.stdout!r}')
    for name, want in (('negative.o', b'punahsthapanani asamarthitani'),
                       ('foreign-unwind.o', b'sanketat anyat bhara-khandam'),
                       ('foreign.c', b'ELF64 x86-64 ET_REL vastu-patram na')):
        r = run([e2s, str(HERE / name), str(t / 'n.smo')])
        check(r.returncode == 1 and want in r.stdout, f'reader refuses {name}: {r.stdout!r}')
    trunc = t / 'trunc.o'
    trunc.write_bytes((HERE / 'foreign.o').read_bytes()[:300])
    r = run([e2s, str(trunc), str(t / 'n.smo')])
    check(r.returncode == 1, f'reader refuses a truncated object: {r.stdout!r}')
    r = run([e2s])
    check(r.returncode == 2, 'reader usage')
    print('the reader: 4 functions read; a relocation, unwind tables, not ELF, truncated: refused; usage')

    # an undeclared call is not made foreign: the link refuses it
    src = t / 'u.sm'
    src.write_text('mukhya() {\n    likha(t_x(1))\n}\n')
    r1 = run([comp, '--ffi', sffi, '--object', str(src), str(t / 'u.smo')])
    run([e2s, str(HERE / 'foreign.o'), str(t / 'f.smo')])
    r2 = run([link, str(t / 'u.bin'), str(t / 'u.smo'), str(t / 'f.smo')])
    check(r1.returncode == 0 and r2.returncode == 1 and b'agyat prakriya: t_x' in r2.stdout
          and not (t / 'u.bin').exists(), f'undeclared: {r2.stdout!r}')
    print('undeclared: a call nothing declares or defines is refused by the link, no executable')

    # the cache: the sidecar is in every key
    c = str(t / 'cache')
    cmd = [sys.executable, '-B', 'tools/sutram_build.py', '--compiler', comp, '--linker', link, '--elf2smo', e2s,
           '--foreign', str(HERE / 'foreign.o'), '--cache', c]
    s2 = t / 'ffi2.sffi'
    s2.write_bytes((HERE / 'ffi.sffi').read_bytes())
    o = [run(cmd + ['--ffi', str(s2), str(HERE / 'main.sm'), '-o', str(t / f'q{k}')]).stdout for k in range(2)]
    s2.write_bytes((HERE / 'ffi.sffi').read_bytes() + b's_two|0||i64|sutram_ffi_two\n')
    o.append(run(cmd + ['--ffi', str(s2), str(HERE / 'main.sm'), '-o', str(t / 'q2')]).stdout)
    check(b'2 compiled, 0 reused' in o[0] and b'0 compiled, 2 reused' in o[1] and b'2 compiled, 0 reused' in o[2],
          f'cache: {o!r}')
    print('the cache: a changed sidecar recompiles every module')

    # 6. opt-in
    r = run([comp, '--ffi', sffi, str(HERE / 'main.sm'), str(t / 'o.bin'), 'x', 'y'])
    check(b'Prayog' in r.stdout and not (t / 'o.bin').exists(), '--ffi without --object: the usage, no output')
    r = run([comp, str(HERE / 'main.sm'), str(t / 'o.bin')])
    check(r.returncode == 1 and b'agyat prakriya' in r.stdout, f'the ordinary compile does not read it: {r.stdout!r}')
    print('opt-in: --ffi needs --object or --separate; the ordinary compile never reads a sidecar')

    print(f'r32 ffi: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

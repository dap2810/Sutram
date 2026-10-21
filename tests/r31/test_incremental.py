#!/usr/bin/env python3
"""ROUND-31: incremental rebuilds - `tools/sutram_build.py --cache DIR`.

  1. THE SAME EXECUTABLE: every program that `yoj`s a module (plain yoj; it compiles the
     ordinary way) is built three times - without a cache, with a cold cache, with the
     warm cache. The three executables must be byte-identical, and the warm build must
     compile nothing. One cache is shared by all of them, so a library module is compiled
     once for every program that uses it.
  2. ONLY WHAT CHANGED: in a copy of tests/r29/proj, editing r29_vam recompiles r29_vam
     and the root (which reaches it) and reuses the other two; editing the leaf r29_mul
     recompiles all four; each result is byte-identical to a clean build.
  3. THE KEY: a different compiler (one more byte) or a different SUTRAM_LANG recompiles
     everything.
Linux only. No network.
usage: python3 -B tests/r31/test_incremental.py [--compiler PATH] [--linker PATH]
"""
from __future__ import annotations

import glob
import os
import re
import shutil
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


def main(argv) -> int:
    comp = arg(argv, '--compiler', str(ROOT / 'sutram_compiler'))
    link = arg(argv, '--linker', str(ROOT / 'sutram-link'))
    fails = 0

    def check(ok, what):
        nonlocal fails
        if not ok:
            fails += 1
            print('FAIL', what)

    def build(src, out, cache=None, compiler=None, env=None):
        cmd = [sys.executable, '-B', str(ROOT / 'tools' / 'sutram_build.py'), '--compiler', compiler or comp,
               '--linker', link]
        if cache:
            cmd += ['--cache', cache]
        r = subprocess.run(cmd + [src, '-o', out], capture_output=True, env=env)
        m = re.search(rb'(\d+) compiled, (\d+) reused', r.stdout)
        return r.returncode, (int(m.group(1)), int(m.group(2))) if m else None

    os.chdir(ROOT)
    t = Path(tempfile.mkdtemp(prefix='r31-'))
    cache = str(t / 'cache')
    # 1. the same executable
    files = sorted(set(glob.glob('examples/*.sm') + glob.glob('examples/*/*.sm')
                       + glob.glob('tests/stdlib/*.sm') + glob.glob('tests/r*/**/*.sm', recursive=True)))
    programs = same = compiled_cold = reused_cold = 0
    for f in files:
        names = sutram_build.yoj_names(open(f, 'rb').read())
        if Path(f).stem in LANG or not names or any('@' in n for n in names):
            continue
        if subprocess.run([comp, f, str(t / 'd.bin')], capture_output=True).returncode != 0:
            continue
        programs += 1
        a, b, c = str(t / 'a'), str(t / 'b'), str(t / 'c')
        ra, _ = build(f, a)
        rb, cold = build(f, b, cache)
        rc, warm = build(f, c, cache)
        ok = ra == rb == rc == 0 and warm == (0, cold[0] + cold[1]) and \
            open(a, 'rb').read() == open(b, 'rb').read() == open(c, 'rb').read()
        check(ok, f'{f}: clean / cold / warm differ ({cold}, {warm})')
        same += ok
        if cold:
            compiled_cold += cold[0]
            reused_cold += cold[1]
    print(f'the same executable: {same} of {programs} programs identical without a cache, cold and warm; '
          f'the warm builds compiled nothing; across all of them the shared cache compiled {compiled_cold} '
          f'objects and reused {reused_cold}')
    check(programs >= 250, f'expected at least 250 programs, got {programs}')

    # 2. only what changed
    proj = t / 'proj'
    shutil.copytree(ROOT / 'tests/r29/proj', proj)
    c2 = str(t / 'cache2')
    main_sm = str(proj / 'main.sm')
    check(build(main_sm, str(t / 'p0'), c2)[1] == (4, 0), 'cold: 4 compiled')
    check(build(main_sm, str(t / 'p1'), c2)[1] == (0, 4), 'warm: 4 reused')
    vam = proj / 'lib' / 'r29_vam.smlib'
    vam.write_text(vam.read_text().replace('+ 1', '+ 2'))
    r = build(main_sm, str(t / 'p2'), c2)
    build(main_sm, str(t / 'p2clean'))
    check(r[1] == (2, 2), f'edit r29_vam: 2 compiled, 2 reused, got {r[1]}')
    check((t / 'p2').read_bytes() == (t / 'p2clean').read_bytes(), 'edit r29_vam: = a clean build')
    mul = proj / 'lib' / 'r29_mul.smlib'
    mul.write_text(mul.read_text().replace('x * 10', 'x * 100'))
    r = build(main_sm, str(t / 'p3'), c2)
    build(main_sm, str(t / 'p3clean'))
    check(r[1] == (4, 0), f'edit the leaf r29_mul: 4 compiled, got {r[1]}')
    check((t / 'p3').read_bytes() == (t / 'p3clean').read_bytes(), 'edit r29_mul: = a clean build')
    out = subprocess.run([str(t / 'p3')], capture_output=True).stdout
    check(out == b'402\n\n800\n\n3.500000\n\n', f'edited output {out!r}')
    print('only what changed: an edited module and what reaches it are recompiled, nothing else; '
          'the result is a clean build, byte for byte')

    # 3. the key
    other = t / 'compiler2'
    other.write_bytes(Path(comp).read_bytes() + b'\0')
    other.chmod(0o755)
    check(build(main_sm, str(t / 'p4'), c2, compiler=str(other))[1] == (4, 0), 'another compiler: 4 compiled')
    env = dict(os.environ, SUTRAM_LANG='sanskrit')
    check(build(main_sm, str(t / 'p5'), c2, env=env)[1] == (4, 0), 'another SUTRAM_LANG: 4 compiled')
    print('the key: another compiler, or another SUTRAM_LANG, recompiles everything')
    print(f'r31 incremental: {same} programs identical clean, cold and warm, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

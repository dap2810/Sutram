#!/usr/bin/env python3
"""ROUND-22 (F8): `--lang <pack>` on a valid program must not warn.

F8 (found on Windows by the owner): `sutram --lang hindi bad.sm o.exe` printed
"language pack not found: hindi" - in Hindi - when lang/hindi.lang was not beside
it, though the pack's messages are built into the compiler and did load. The
compiler now carries the eleven keyword packs too (src/r22_lang_builtin.inc,
generated from lang/*.lang by tools/lang_builtin.py), so:

  1. for every pack, from a folder with no lang/ and a HOME with no packs, by
     --lang, by --check --lang and by SUTRAM_LANG: exit 0, the pack's own
     "pack found" line, and NOT its "pack not found" line;
  2. the native-keyword examples compile to the same bytes from the built-in pack
     as from lang/*.lang on disk (the built-in is the same pack, not a subset);
  3. a name that is no pack still warns (the warning is not removed, it is right now);
  4. a .lang file on disk still wins over the built-in one.

Runs the Linux compiler (./sutram_compiler). No network.
usage: python3 -B tests/r22/test_lang_builtin.py [--compiler PATH]
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
PACKS = ['bengali', 'gujarati', 'hindi', 'kannada', 'malayalam', 'marathi', 'odia',
         'punjabi', 'tamil', 'telugu', 'sanskrit']
NATIVE = {'37_native_gujarati': 'gujarati', '38_native_hindi': 'hindi', '39_native_tamil': 'tamil',
          '218_sanskrit_devanagari': 'sanskrit', '219_sanskrit_kosh_aliases': 'sanskrit'}
GOOD = b'mukhya() {\n    likha(7)\n}\n'


def pack_text(pack: str, key: str) -> bytes:
    for line in (ROOT / 'lang' / (pack + '.sandesh')).read_text(encoding='utf-8').splitlines():
        if line.startswith(key + '\t'):
            return json.loads(line.split('\t', 1)[1]).encode('utf-8')
    raise KeyError(pack + ':' + key)


def default_text(key: str) -> bytes:
    for line in (ROOT / 'src/sutram_compiler.asm').read_text(encoding='utf-8').splitlines():
        s = line.strip()
        if s.startswith(key + ' ') and ' db "' in s:
            return s.split(' db "', 1)[1].split('"', 1)[0].encode('utf-8')
    raise KeyError(key)


def run(comp, args, cwd, env_extra=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith('SUTRAM_')}
    env['HOME'] = str(cwd)
    env.update(env_extra or {})
    return subprocess.run([comp] + args, cwd=str(cwd), env=env, capture_output=True, timeout=60)


def main(argv) -> int:
    comp = os.path.abspath(argv[argv.index('--compiler') + 1]) if '--compiler' in argv else str(ROOT / 'sutram_compiler')
    fails = 0
    checks = 0

    def check(ok, what):
        nonlocal fails, checks
        checks += 1
        if not ok:
            fails += 1
        print('%s  %s' % ('PASS' if ok else 'FAIL', what))

    with tempfile.TemporaryDirectory() as td:
        bare = Path(td, 'bare')            # no lang/, HOME with no packs
        bare.mkdir()
        (bare / 'good.sm').write_bytes(GOOD)
        for pack in PACKS:
            ok_line, fail_line = pack_text(pack, 'msg_lang_ok'), pack_text(pack, 'msg_lang_fail')
            for how, args, env in (
                    ('--lang', ['--lang', pack, 'good.sm', 'o.bin'], None),
                    ('--check --lang', ['--check', '--lang', pack, 'good.sm'], None),
                    ('SUTRAM_LANG', ['good.sm', 'o.bin'], {'SUTRAM_LANG': pack})):
                r = run(comp, args, bare, env)
                out = r.stdout + r.stderr
                check(r.returncode == 0 and fail_line not in out and (ok_line + pack.encode()) in out,
                      '%-9s %-15s no lang/ beside it: exit %d, %s' % (
                          pack, how, r.returncode,
                          'warned "not found"' if fail_line in out else 'no warning, "found" printed'))

        # 2: the built-in pack is the same pack
        withlang = Path(td, 'withlang')
        withlang.mkdir()
        shutil.copytree(ROOT / 'lang', withlang / 'lang')
        for name, pack in NATIVE.items():
            src = ROOT / 'examples' / (name + '.sm')
            (bare / 'in.sm').write_bytes(src.read_bytes())
            (withlang / 'in.sm').write_bytes(src.read_bytes())
            a = run(comp, ['--lang', pack, 'in.sm', 'o.bin'], withlang)
            b = run(comp, ['--lang', pack, 'in.sm', 'o.bin'], bare)
            same = (a.returncode == b.returncode == 0 and (withlang / 'o.bin').read_bytes() == (bare / 'o.bin').read_bytes())
            check(same, '%-27s from lang/%s.lang and from the built-in: %s' % (
                name, pack, 'same binary' if same else 'DIFFER (exit %d / %d)' % (a.returncode, b.returncode)))

        # 3: no such pack still warns, with the default text
        r = run(comp, ['--lang', 'klingon', 'good.sm', 'o.bin'], bare)
        check(default_text('msg_lang_fail') + b'klingon' in r.stdout, '--lang klingon (no such pack) still warns')

        # 4: a file on disk wins: an extra keyword only the file has
        (withlang / 'lang' / 'hindi.lang').write_bytes(
            (ROOT / 'lang/hindi.lang').read_bytes() + 'छापिए likha\n'.encode('utf-8'))
        prog = 'मुख्य() {\n    छापिए(7)\n}\n'.encode('utf-8')
        (withlang / 'p.sm').write_bytes(prog)
        (bare / 'p.sm').write_bytes(prog)
        a = run(comp, ['--lang', 'hindi', 'p.sm', 'o.bin'], withlang)
        b = run(comp, ['--lang', 'hindi', 'p.sm', 'o.bin'], bare)
        check(a.returncode == 0 and b.returncode != 0,
              'lang/hindi.lang on disk wins over the built-in (an extra word: exit %d with the file, %d without)'
              % (a.returncode, b.returncode))

    print('lang built-in: %d checks, %d failed' % (checks, fails))
    return 1 if fails else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

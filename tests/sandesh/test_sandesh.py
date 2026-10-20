#!/usr/bin/env python3
"""ROUND-11 (WS1): the compiler's messages follow the language pack.

For the default (no --lang) and each of the eleven packs, every case in cases/ is
compiled (and run, when it compiles); the compiler's and the program's output are
compared with expect/<pack>/<case>.out. parse.sm and ok.sm are also run with --check.
The checks on the pack files themselves (tools/sandesh.py --check) run here too, and
so do small tests that the checker refuses what it must refuse.

    python3 tests/sandesh/test_sandesh.py            # from anywhere
    python3 tests/sandesh/test_sandesh.py --record   # rewrite expect/ (review the diff)
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CASES = HERE / 'cases'
EXPECT = HERE / 'expect'
COMPILER = os.environ.get('SUTRAM_COMPILER') or str(ROOT / 'sutram_compiler')
sys.path.insert(0, str(ROOT / 'tools'))
import sandesh  # noqa: E402

PACKS = ['default'] + sandesh.PACK_ORDER
CHECK_CASES = ('parse', 'ok')


def run_case(pack: str, case: str, check: bool) -> str:
    """Compiler output, then the program's output and exit code, as one text."""
    src = f'tests/sandesh/cases/{case}.sm'
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, 'p.bin')
        cmd = [COMPILER] + (['--lang', pack] if pack != 'default' else [])
        cmd += ['--check', src] if check else [src, out]
        c = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=30)
        text = c.stdout.decode('utf-8') + c.stderr.decode('utf-8') + f'[compile exit {c.returncode}]\n'
        if not check and c.returncode == 0:
            r = subprocess.run([out], capture_output=True, timeout=10)
            text += r.stdout.decode('utf-8') + f'[run exit {r.returncode}]\n'
    return text


def all_runs():
    for pack in PACKS:
        for p in sorted(CASES.glob('*.sm')):
            yield pack, p.stem, False
            if p.stem in CHECK_CASES:
                yield pack, p.stem, True


def expect_path(pack, case, check):
    return EXPECT / pack / (case + ('.check' if check else '') + '.out')


class Goldens(unittest.TestCase):
    def test_every_pack_every_case(self):
        bad = []
        n = 0
        for pack, case, check in all_runs():
            n += 1
            got = run_case(pack, case, check)
            p = expect_path(pack, case, check)
            if not p.exists() or p.read_text(encoding='utf-8') != got:
                bad.append(str(p.relative_to(ROOT)))
        self.assertEqual(bad, [], f'{len(bad)} of {n} differ')

    def test_no_latin_prose_in_pack_runs(self):
        # every line a pack run prints is in that pack's language: the only Latin
        # is the identifiers the owner keeps, code, file names and numbers
        allowed = sandesh.CODE_WORDS | sandesh.roman_keywords() | {
            'sm', 'p', 'q', 'y', 'f', 'a', 'b', 'nahi_asti', 'cases', 'tests', 'sandesh'} | set(
            sandesh.PACK_ORDER) | {c.stem for c in CASES.glob('*.sm')}   # pack names, file names
        for pack in sandesh.PACK_ORDER:
            for case in ('undefined_name', 'arity', 'duplicate', 'unknown_field', 'missing_module',
                         'oob', 'kosh_empty', 'parse', 'ok'):
                text = expect_path(pack, case, False).read_text(encoding='utf-8')
                body = [l for l in text.splitlines() if not l.startswith('[') and not l.startswith('  ')
                        and not l.startswith('      ')]
                words = set(sandesh.LATIN.findall(sandesh.TAGS.sub(' ', '\n'.join(body))))
                self.assertTrue(words <= allowed, f'{pack} {case}: Latin {sorted(words - allowed)}')


class PackFiles(unittest.TestCase):
    def test_check(self):
        r = subprocess.run([sys.executable, str(ROOT / 'tools/sandesh.py'), '--check'],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn('OK', r.stdout)

    def test_checker_refuses(self):
        sandesh.ROMAN_KW.update(sandesh.roman_keywords())
        d = ": Sutram Error [E_UNDEFINED_NAME]: agyat naam '"
        ok = ": Sutram Error [E_UNDEFINED_NAME]: अज्ञात नाम '"
        self.assertEqual(sandesh.check_entry('hindi', 'k', ok, d), [])
        cases = {
            'English word': ": Sutram Error [E_UNDEFINED_NAME]: unknown नाम '",
            'tag dropped': ": Sutram Error: अज्ञात नाम '",
            'prefix translated': ": सूत्रम् त्रुटि [E_UNDEFINED_NAME]: अज्ञात नाम '",
            'quote dropped': ": Sutram Error [E_UNDEFINED_NAME]: अज्ञात नाम",
            'wrong script': ": Sutram Error [E_UNDEFINED_NAME]: அறியாத நாம '",
        }
        for why, text in cases.items():
            self.assertNotEqual(sandesh.check_entry('hindi', 'k', text, d), [], why)
        self.assertNotEqual(sandesh.check_entry('hindi', 'k', "Sanket: {kw:nosuch} ", "Sanket: vitti "), [])

    def test_defaults_have_no_english(self):
        problems, _ = sandesh.check_all(sandesh.defaults(), strict=False)
        self.assertEqual([p for p in problems if p.startswith('default')], [])


def record():
    for pack, case, check in all_runs():
        p = expect_path(pack, case, check)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(run_case(pack, case, check), encoding='utf-8')
    print('recorded', sum(1 for _ in all_runs()))


if __name__ == '__main__':
    if '--record' in sys.argv:
        record()
    else:
        unittest.main()

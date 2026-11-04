"""Hand-derived string/lifetime and explicit PE memory-support contracts.

Run with SUTRAM_COMPILER pointing to a native compiler. No golden recording.
"""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
COMPILER = Path(os.environ.get('SUTRAM_COMPILER', ROOT / ('win/sutram.exe' if os.name == 'nt' else 'sutram_compiler'))).resolve()


class Contracts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)

    def compile(self, source, name='case', flags=(), pe=None):
        src = self.path / (name + '.sm')
        src.write_text(source, encoding='utf8')
        target = self.path / (name + ('.exe' if pe or os.name == 'nt' else '.bin'))
        result = subprocess.run([str(COMPILER), *flags, str(src), str(target)], cwd=ROOT, capture_output=True, timeout=10)
        return result, target

    def output(self, source, expected):
        result, target = self.compile(source)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        actual = subprocess.run([str(target)], capture_output=True, timeout=10)
        self.assertEqual((actual.returncode, actual.stdout, actual.stderr), (0, expected, b''))

    def test_literals_repeat_without_self_modification(self):
        self.output('mukhya() { vitti i = 0 yavat(i < 3) { shabda(vartani_sandhi("ab", "cd")) i = i + 1 } }', b'abcdabcdabcd')

    def test_join_leaves_both_inputs_and_previous_results_unchanged(self):
        self.output('mukhya() { vitti a = "ab" vitti b = "cd" vitti c = vartani_sandhi(a,b) vitti d = vartani_sandhi(c,"!") shabda(a) shabda(b) shabda(c) shabda(d) }', b'abcdabcdabcd!')

    def test_empty_inputs_and_nested_join(self):
        self.output('mukhya() { shabda(vartani_sandhi("", "")) shabda(vartani_sandhi(vartani_sandhi("a", "b"), "c")) }', b'abc')

    def test_character_results_survive_calls_and_do_not_alias(self):
        self.output('prakriya f(n) { nivartanam anka_akshar(n) }\nmukhya() { vitti a = f(66) vitti b = f(97) shabda(a) shabda(b) }', b'Ba')

    def test_character_allocation_in_loop(self):
        self.output('mukhya() { vitti i = 0 yavat(i < 10000) { vitti c = anka_akshar(97) i = i + 1 } likha(i) }', b'10000\n')

    def test_old_names_are_byte_identical(self):
        for old, new, expr in [('vartani_cat', 'vartani_sandhi', '("ab", "cd")'), ('char_from', 'anka_akshar', '(66)')]:
            with self.subTest(old=old):
                a, pa = self.compile('mukhya() { shabda(' + old + expr + ') }', 'old')
                b, pb = self.compile('mukhya() { shabda(' + new + expr + ') }', 'new')
                self.assertEqual((a.returncode, b.returncode), (0, 0))
                self.assertEqual(pa.read_bytes(), pb.read_bytes())
                self.assertIn(new.encode(), a.stderr)
                self.assertEqual(b.stderr, b'')

    def test_pe_memory_features_compile(self):
        for name, source in [('query', 'mukhya() { likha(parimana()) }'), ('budget', 'mukhya() { mandapa parimita 64 { likha(1) } }')]:
            result, target = self.compile(source, name, pe=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(target.exists())

    @unittest.skipIf(os.name == 'nt', 'ELF allocation fault injection is Linux-only')
    def test_allocation_failure_is_diagnostic_not_invalid_store(self):
        for name, expr in [('char', 'anka_akshar(66)'), ('concat', 'vartani_sandhi("ab", "cd")')]:
            with self.subTest(name=name):
                result, target = self.compile('mukhya() { shabda(' + expr + ') }', name, ('--fail-alloc', '1'))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                actual = subprocess.run([str(target)], capture_output=True, timeout=10)
                self.assertEqual(actual.returncode, 1)
                self.assertIn(b'E_VARTANI_SMRITI', actual.stdout + actual.stderr)

    def test_accounting_and_budget_work(self):
        self.output('mukhya() { likha(parimana()) mandapa { vitti p = nirmmita(64) likha(parimana()) } likha(parimana()) }', b'0\n64\n0\n')
        result, target = self.compile('mukhya() { mandapa parimita 1 { vitti p = nirmmita(64) likha(123) } }', 'budget')
        self.assertEqual(result.returncode, 0)
        actual = subprocess.run([str(target)], capture_output=True, timeout=10)
        self.assertEqual(actual.returncode, 1)
        self.assertIn(b'E_PARIMITA', actual.stdout + actual.stderr)


if __name__ == '__main__':
    unittest.main()

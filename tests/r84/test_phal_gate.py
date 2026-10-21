"""Unit proofs for experimental R84 precheck, NOT native Sutram tests."""
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('r84_phal_gate',ROOT/'tools/r84_phal_gate.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class TestPhalGate(unittest.TestCase):
    def test_reject_realistic_ignored_division(self):
        text=(ROOT/'tests/r84/cases/ignored_failure.sm').read_text()
        self.assertEqual(m.check(text)[0]['code'],'E_PHAL_UNHANDLED')
    def test_accept_failure_exit(self):
        text=(ROOT/'tests/r84/cases/checked_failure.sm').read_text()
        self.assertEqual(m.check(text),[])
    def test_wrong_result_cell_rejected(self):
        src='phal_janchit_gun(a, 5, 7)\nyadi (phal_asti_siddhi(b) == 0) {\n prati 0\n}\n'
        self.assertEqual(m.check(src)[0]['code'],'E_PHAL_UNHANDLED')
    def test_check_without_exit_rejected(self):
        src='phal_janchit_bhaj(r, 1, 0)\nyadi (phal_asti_siddhi(r) == 0) {\n likha(0)\n}\n'
        self.assertEqual(m.check(src)[0]['code'],'E_PHAL_UNHANDLED')
    def test_check_with_nested_conditional_rejected(self):
        src='phal_janchit_bhaj(r, 1, 0)\nyadi (phal_asti_siddhi(r) == 0) {\n yadi (ok) { prati 0 }\n}\n'
        self.assertEqual(m.check(src)[0]['code'],'E_PHAL_UNHANDLED')
    def test_no_false_hit_from_comments(self):
        self.assertEqual(m.check('# phal_janchit_bhaj(r,2,0)\n/* phal_janchit_gun(r,2,2) */\n'),[])
    def test_no_false_hit_from_string(self):
        self.assertEqual(m.check('likha("phal_janchit_bhaj(r,2,0)")\n'),[])
    def test_multiline_comment(self):
        self.assertEqual(m.check('/* begin\nphal_janchit_bhaj(r,2,0)\n */\n'),[])
    def test_unsupported_inline_call_is_rejected(self):
        self.assertEqual(m.check('vitti x = phal_janchit_gun(r,2,2)\n')[0]['code'],'UNSUPPORTED_PRODUCER')
    def test_multiple_obligations(self):
        text='phal_janchit_bhaj(r,2,0)\nyadi (phal_asti_siddhi(r) == 0) {\n prati 0\n}\nphal_janchit_gun(r,2,2)\nlikha(phal_mulya(r))\n'
        self.assertEqual(len(m.check(text)),1)
    def test_reject_unsupported_else(self):
        src='phal_janchit_bhaj(r,2,0)\nyadi (phal_asti_siddhi(r) == 0) {\n prati 0\n}\nanya {\n likha(0)\n}\n'
        self.assertEqual(m.check(src)[0]['code'],'E_PHAL_UNHANDLED')
    def test_unclosed_block_comment_rejected(self):
        self.assertEqual(m.check('/* never closed')[0]['code'],'UNSUPPORTED_SYNTAX')

if __name__=='__main__':unittest.main()

#!/usr/bin/env python3
"""R5: the Windows GUI's Latin colour tables must be the compiler's own names.

Until R5, kw_words/bi_words in windows/gui/sutram_gui.asm still held the pre-v157 names
(pratiyati, ayojan, anyatha, char_at ...), so the current keywords vitti/chakra/prati/tak/
anya/agrim and the renamed builtins were never coloured. Source check only; not a
substitute for seeing the colours on Windows.
"""
from __future__ import annotations
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUI = (ROOT / 'windows/gui/sutram_gui.asm').read_text(encoding='utf-8')
SRC = (ROOT / 'src/sutram_compiler.asm').read_text(encoding='utf-8')


def gui_table(name):
    m = re.search(rf'(?ms)^{name} db (.*?),0\s*$', GUI)
    if not m:
        raise AssertionError(f'{name} not found')
    return re.findall(r"'([^']*)',0", m.group(1))


class ColourTables(unittest.TestCase):
    def test_keywords_are_the_compilers(self):
        kw = re.findall(r'^\s+kw_(?!dev_)\w+\s+db "([^"]+)", *0', SRC, re.M)
        self.assertTrue(len(kw) >= 20)
        self.assertEqual(gui_table('kw_words'), kw)

    def test_builtins_are_the_compilers(self):
        bn = re.findall(r'^\s+bn_\w+\s+db "([^"]+)", *0', SRC, re.M)
        self.assertTrue(len(bn) >= 20)
        self.assertEqual(gui_table('bi_words'), bn)

    def test_no_pre_v157_keyword(self):
        for old in ('pratiyati', 'ayojan', 'anyatha', 'nishkriya', 'uddeshya', 'punaravartana'):
            self.assertNotIn(old, gui_table('kw_words'))


if __name__ == '__main__':
    unittest.main()

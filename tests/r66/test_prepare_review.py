"""Language-pack contract tests (R66 origin); NOT full compiler execution."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[2]
# R3: tools/r66_prepare_review.py (R66 staging onto a superseded compiler blob) was
# retired; its PrepareTests went with it. PackTests check the live lang/ packs.


class PackTests(unittest.TestCase):
    @staticmethod
    def entries(lang):
        return [line.split() for line in (ROOT / 'lang' / (lang + '.lang')).read_text('utf-8').splitlines()
                if line.strip() and not line.lstrip().startswith('#')]

    def test_counts_and_uniqueness(self):
        # R67 omitted the colliding Gujarati reservation; keep its 44-entry contract.
        for lang, count in [('sanskrit', 54), ('gujarati', 44)]:
            rows = self.entries(lang)
            self.assertEqual(len(rows), count)
            self.assertEqual(len({a for a, _ in rows}), count)
            self.assertTrue(all(len(a.encode()) < 64 and len(b.encode()) < 64 for a, b in rows))

    def test_gujarati_collision_stays_unreserved(self):
        # Accepted example 37 uses this spelling as a variable, not a type.
        self.assertNotIn('સંખ્યા', dict(self.entries('gujarati')))

    def test_explicit_abbreviations(self):
        s, g = dict(self.entries('sanskrit')), dict(self.entries('gujarati'))
        self.assertEqual(s['वि॰'], 'vitti')
        self.assertEqual(s['लि॰'], 'likha')
        self.assertEqual(g['ચ૰'], 'vitti')
        self.assertEqual(g['લ૰'], 'likha')
        self.assertNotIn('લ॰', g)
        self.assertNotIn('वि૰', s)

    def test_previous_keywords_preserved(self):
        baseline = json.loads((ROOT / 'tests/r66/baseline_packs.json').read_text('utf-8'))
        for lang in ('sanskrit', 'gujarati'):
            old_entries = baseline[lang]
            new_entries = dict(self.entries(lang))
            self.assertTrue(old_entries.items() <= new_entries.items())

    def test_builtin_capacity(self):
        # Existing builtin IDs used by these packs (not the whole compiler table).
        builtins = {'likha','likh','sthagita','pad','dvaram','paadh','band','nirmmita',
                    'grahan','shabda','pankti_len','kosh_push','kosh_pop','kosh_len',
                    'kosh_cap','kosh_clear','kosh_empty','kosh_peek','kosh_enqueue','kosh_dequeue'}
        for lang in ('sanskrit', 'gujarati'):
            rows = self.entries(lang)
            self.assertLessEqual(sum(b in builtins for _, b in rows), 32)
            self.assertLessEqual(sum(b not in builtins and b != 'to' for _, b in rows), 96)
            self.assertLess(sum(len(a.encode())+1 for a, _ in rows), 8192)

if __name__ == '__main__':
    unittest.main()

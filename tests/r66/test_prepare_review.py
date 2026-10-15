"""Captured-anchor transformation and pack tests; NOT full compiler execution."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('r66prepare', ROOT / 'tools/r66_prepare_review.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture():
    # Explicitly synthetic; only anchors were captured from the production source.
    return '; untouched prefix\n' + '\n; gap\n'.join(old for _, old, _ in m.REPLACEMENTS) + '; untouched suffix\n'

class PrepareTests(unittest.TestCase):
    def test_all_eight_anchors_apply(self):
        result = m.transform(fixture())
        self.assertEqual(len(m.REPLACEMENTS), 8)
        for _, _, new in m.REPLACEMENTS:
            self.assertIn(new, result)

    def test_unrelated_text_preserved(self):
        result = m.transform(fixture())
        self.assertTrue(result.startswith('; untouched prefix\n'))
        self.assertTrue(result.endswith('; untouched suffix\n'))

    def test_each_missing_anchor_fails(self):
        for label, old, _ in m.REPLACEMENTS:
            with self.subTest(label=label), self.assertRaises(ValueError):
                m.transform(fixture().replace(old, '', 1))

    def test_each_duplicate_anchor_fails(self):
        for label, old, _ in m.REPLACEMENTS:
            with self.subTest(label=label), self.assertRaises(ValueError):
                m.transform(fixture() + old)

    def test_reapplication_fails(self):
        with self.assertRaises(ValueError):
            m.transform(m.transform(fixture()))

    def test_wrong_production_blob_fails(self):
        with self.assertRaisesRegex(ValueError, 'source drift'):
            m.prepare(fixture().encode())

    def test_byte_round_trip_on_explicit_mock_blob(self):
        data = fixture().encode()
        with patch.object(m, 'INPUT_BLOB', m.git_blob(data)):
            self.assertEqual(m.prepare(data), m.transform(fixture()).encode())

    def test_numeric_priority_before_identifier(self):
        self.assertIn('jnz .try_number', m.NEW_DANDA)
        self.assertIn('add r13, rdx', m.NEW_DEC)
        self.assertIn('add r13, rdx', m.NEW_ACC)

    def test_identifier_write_pointer_preserved(self):
        self.assertIn('push rsi', m.NEW_ID_DANDA)
        self.assertIn('pop rsi', m.NEW_ID_DANDA)
        self.assertIn('push rsi', m.NEW_COPY)
        self.assertIn('pop rsi', m.NEW_COPY)

    def test_source_not_rewritten_or_fullwidth_decimal_invented(self):
        result = m.transform(fixture())
        self.assertNotIn('mov [r13]', result)
        self.assertIn("cmp byte [r13], '.'", result)
        self.assertNotIn('0xB0', result)  # abbreviation mark is NOT decimal/terminator

    def test_main_rejects_overwriting_source(self):
        with patch('sys.argv', ['r66', '--source', '/tmp/same.sm', '--output', '/tmp/same.sm',
                               '--patch-output', '/tmp/different.patch']):
            with self.assertRaises(SystemExit):
                m.main()

    def test_main_rejects_existing_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            src, dst, diff = (Path(temp) / x for x in ('src', 'dst', 'patch'))
            src.write_text('original')
            dst.write_text('do not touch')
            with patch('sys.argv', ['r66', '--source', str(src), '--output', str(dst),
                                   '--patch-output', str(diff)]):
                with self.assertRaises(SystemExit):
                    m.main()
            self.assertEqual(dst.read_text(), 'do not touch')

class PackTests(unittest.TestCase):
    @staticmethod
    def entries(lang):
        return [line.split() for line in (ROOT / 'lang' / (lang + '.lang')).read_text('utf-8').splitlines()
                if line.strip() and not line.lstrip().startswith('#')]

    def test_counts_and_uniqueness(self):
        for lang, count in [('sanskrit', 54), ('gujarati', 45)]:
            rows = self.entries(lang)
            self.assertEqual(len(rows), count)
            self.assertEqual(len({a for a, _ in rows}), count)
            self.assertTrue(all(len(a.encode()) < 64 and len(b.encode()) < 64 for a, b in rows))

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

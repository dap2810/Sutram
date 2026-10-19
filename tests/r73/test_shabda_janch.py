import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('vocab', ROOT / 'tools/r73_shabda_janch.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
class AuditTests(unittest.TestCase):
    def test_comment_and_strings_ignored(self):
        self.assertEqual(a.scrub('likha("pankti") # ayojan'), 'likha() ')
    def test_quote_escaping(self):
        self.assertNotIn('pankti', a.scrub('likha("x\\\"pankti")'))
    def test_synthetic_git_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            (root / 'lang').mkdir(); (root / 'windows').mkdir()
            (root / 'lang/malayalam.lang').write_text('nativeword pankti\n')
            (root / 'windows').joinpath('gui.asm').write_text("kw_words db 'pankti',0\nr4_o_pankti db 'pankti',0\n")
            (root / 'x.sm').write_text('mukhya() { pankti a[2] # ayojan\n}\n')
            subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
            result=a.inspect(root)
            self.assertEqual(result['categories']['ACTIVE_PACK_RHS'], 1)
            self.assertEqual(result['categories']['ACTIVE_KEYWORD_TABLE'], 1)
            self.assertEqual(result['categories']['SOURCE_TOKEN_REVIEW'], 1)
            self.assertFalse(any('r4_o_pankti' in x['excerpt'] for x in result['candidates']))
if __name__ == '__main__': unittest.main()

"""R74 vocabulary audit regression fixtures; not compiler execution."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

p = Path(__file__).resolve().parents[2] / 'tools' / 'r74_vocabulary_audit.py'
spec = importlib.util.spec_from_file_location('r74_vocabulary_audit',p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class VocabularyAuditTest(unittest.TestCase):
    def test_source_strips_comments_and_strings(self):
        source = 'mukhya()\n chakra i = 1 to 2 # punaravartana\n likha("srijana")\n pratiyati 4\n'
        rows = mod.scan('examples/old.sm', source)
        self.assertEqual([r['old'] for r in rows], ['to', 'pratiyati'])
    def test_new_sanskrit_clean(self):
        self.assertEqual(mod.scan('a.smlib', 'chakra i = 1 tak 4\nprati 4\n'), [])
    def test_prose_to_not_flagged(self):
        self.assertEqual(mod.scan('docs/guide.md','Go to the start.\n'), [])
    def test_escaped_newline_embedded_code_caught(self):
        rows=mod.scan('docs/book.html',r'<pre>mukhya()\npratiyati 2</pre>')
        self.assertEqual([r['old'] for r in rows],['pratiyati'])
    def test_doc_sutram_fence(self):
        rows=mod.scan('docs/book.md','```sutram\nayojan ganit\n```\n')
        self.assertEqual([r['new'] for r in rows],['yoj'])
    def test_review_only_old_quoted_literal(self):
        rows=mod.scan('windows/gui/a.asm', 'kw db "punaravartana",0')
        self.assertEqual(rows[0]['kind'],'quoted_literal_review')
    def test_git_tracked_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root/'examples').mkdir()
            (root/'examples'/'bad.sm').write_text('pratiyati 1\n')
            (root/'ignored.sm').write_text('pratiyati 2\n')
            subprocess.run(['git','init','-q',str(root)],check=True)
            subprocess.run(['git','-C',str(root),'add','examples/bad.sm'],check=True)
            r=mod.audit(root)
            self.assertEqual(r['summary']['scanned'],1)
            self.assertEqual(len(r['findings']),1)

if __name__ == '__main__': unittest.main()

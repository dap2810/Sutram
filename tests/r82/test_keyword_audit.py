import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
p=Path(__file__).resolve().parents[2]/'tools'/'r82_keyword_audit.py'
spec=importlib.util.spec_from_file_location('r82_keyword_audit',p)
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

class Tests(unittest.TestCase):
    def test_strings_and_comments(self):
        v='mukhya() {\nlikha("ayojan \\\\n pratiyati") # srijana\nprati 5\n}'
        self.assertEqual(a.scan('x.sm',v),[])
    def test_block_comment_spans_multiple_lines(self):
        v='/*\npratiyati 5\nayojan foo\n*/\nprati 2'
        self.assertEqual(a.scan('x.sm',v),[])
    def test_true_old_token(self):
        r=a.scan('x.smlib','pratiyati x\n')
        self.assertEqual([(x['old'],x['line']) for x in r],[('pratiyati',1)])
    def test_range_to_only(self):
        self.assertEqual([v['old'] for v in a.scan('x.sm','chakra i = 1 to 2\n')],['to'])
        self.assertEqual(a.scan('x.sm','likha("go to home")'),[])
    def test_diagnostic_pankti_not_error(self):
        self.assertEqual(a.scan('x.sandesh','r4_err\t"vyakaran dosh, pankti 5:1\\n"'),[])
    def test_diagnostic_old_placeholder(self):
        r=a.scan('x.sandesh','msg\t"{kw:pratiyati}\\n"')
        self.assertEqual(r[0]['old'],'pratiyati')
    def test_pack_native_spelling_legitimate(self):
        self.assertEqual(a.scan('lang/gujarati.lang','પંક્તિ mala\nચાલુ chakra\n'),[])
    def test_pack_canonical_stale(self):
        self.assertEqual(a.scan('lang/demo.lang','foo punaravartana\n')[0]['kind'],'language_pack_canonical')
    def test_escaped_code_newline(self):
        self.assertEqual(a.scan('docs/book.html',r'<pre>x\npratiyati 4</pre>')[0]['old'],'pratiyati')
    def test_only_tagged_fences(self):
        self.assertEqual(a.scan('doc.md','Some ordinary prose about the array.\n'),[])
        self.assertEqual(a.scan('doc.md','```sutram\npratiyati 1\n```')[0]['old'],'pratiyati')
    def test_quoted_compiler_dispatch(self):
        self.assertEqual(a.scan('ide/x.asm','kw db "ayojan",0')[0]['old'],'ayojan')
    def test_tracking_and_exclusions(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'examples').mkdir();(root/'ChatGPT-to-Sarvam').mkdir()
            (root/'examples/a.sm').write_text('pratiyati 1\n')
            (root/'ChatGPT-to-Sarvam/report.sm').write_text('pratiyati 2\n')
            (root/'untracked.sm').write_text('pratiyati 3\n')
            subprocess.run(['git','init','-q',str(root)],check=True)
            subprocess.run(['git','-C',str(root),'add','examples/a.sm','ChatGPT-to-Sarvam/report.sm'],check=True)
            res=a.audit(root)
            self.assertEqual(res['coverage']['tracked'],2)
            self.assertEqual(res['coverage']['scanned'],1)
            self.assertEqual(res['coverage']['history_excluded'],1)
            self.assertEqual(res['candidate_count'],1)
            self.assertEqual(res['status'],'INVENTORY_PASS')

if __name__=='__main__':unittest.main()

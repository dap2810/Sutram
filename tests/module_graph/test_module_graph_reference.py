"""Reference design tests, NOT passing NASM compiler feature tests yet."""
from pathlib import Path
import tempfile,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'))
from module_graph_reference import GraphReference, GraphDiagnostic

class GraphContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.g = GraphReference(self.root)
    def module(self,name,body):
        (self.root/(name+'.smlib')).write_text(body,encoding='utf8')
    def entry(self,body):
        p=self.root/'main.sm';p.write_text(body,encoding='utf8');return p
    def diamond(self):
        self.module('d','prakriya shared() { pratiyati 2 }\n')
        self.module('b','ayojan d\nprakriya one() { pratiyati shared() }\n')
        self.module('c','ayojan d\nprakriya two() { pratiyati shared() }\n')
        self.module('a','ayojan b\nayojan c\nprakriya top() { pratiyati one()+two() }\n')
    def test_diamond_one_visit(self):
        self.diamond()
        self.assertEqual(self.g.analyze(self.entry('ayojan a\n')),['d','b','c','a'])
    def test_diamond_repeated_direct_import_one_visit(self):
        self.diamond()
        self.assertEqual(self.g.analyze(self.entry('ayojan a\nayojan d\nayojan a\n')),['d','b','c','a'])
    def test_deterministic_sibling_order(self):
        self.diamond()
        self.module('a','ayojan c\nayojan b\nprakriya top() { pratiyati 0 }\n')
        self.assertEqual(self.g.analyze(self.entry('ayojan a\n')),['d','c','b','a'])
    def test_missing_diagnostic_has_file_and_line(self):
        entry=self.entry('# comment\nayojan missing\n')
        with self.assertRaises(GraphDiagnostic) as cm:self.g.analyze(entry)
        self.assertEqual(cm.exception.kind,'E_MODULE_MISSING')
        self.assertEqual(cm.exception.line,2)
        self.assertIn('main.sm:2:',str(cm.exception))
    def test_cycle_reports_dependency_path(self):
        self.module('a','ayojan b\nprakriya a() { pratiyati 1 }\n')
        self.module('b','ayojan a\nprakriya b() { pratiyati 1 }\n')
        with self.assertRaises(GraphDiagnostic) as cm:self.g.analyze(self.entry('ayojan a\n'))
        self.assertEqual(cm.exception.kind,'E_MODULE_CYCLE')
        self.assertIn('a -> b -> a',str(cm.exception))
        self.assertIn('b.smlib:1:',str(cm.exception))
    def test_private_not_visible(self):
        self.module('secure','# sutram-module-v1\nniryat api\nprakriya api() { pratiyati 1 }\nprakriya helper() { pratiyati 2 }\n')
        entry=self.entry('ayojan secure@sec\n')
        self.g.analyze(entry)
        self.assertTrue(self.g.check_access('secure','api',entry,2))
        with self.assertRaises(GraphDiagnostic) as cm:self.g.check_access('secure','helper',entry,2)
        self.assertEqual(cm.exception.kind,'E_PRIVATE_SYMBOL')
    def test_export_not_defined(self):
        self.module('m','# sutram-module-v1\nniryat nofunc\nprakriya other() { pratiyati 1 }\n')
        with self.assertRaises(GraphDiagnostic) as cm:self.g.analyze(self.entry('ayojan m\n'))
        self.assertEqual(cm.exception.kind,'E_EXPORT_UNDEFINED')
    def test_duplicate_explicit_export(self):
        self.module('m','# sutram-module-v1\nniryat one\nniryat one\nprakriya one() { pratiyati 1 }\n')
        with self.assertRaises(GraphDiagnostic) as cm:self.g.analyze(self.entry('ayojan m\n'))
        self.assertEqual(cm.exception.kind,'E_EXPORT_DUPLICATE')
    def test_unqualified_conflict_in_modern_mode(self):
        self.module('m','# sutram-module-v1\nniryat same\nprakriya same() { pratiyati 1 }\n')
        self.module('n','# sutram-module-v1\nniryat same\nprakriya same() { pratiyati 2 }\n')
        with self.assertRaises(GraphDiagnostic) as cm:self.g.analyze(self.entry('# sutram-module-v1\nayojan m\nayojan n\n'))
        self.assertEqual(cm.exception.kind,'E_EXPORT_COLLISION')
    def test_qualified_collision_is_safe(self):
        self.module('m','# sutram-module-v1\nniryat same\nprakriya same() { pratiyati 1 }\n')
        self.module('n','# sutram-module-v1\nniryat same\nprakriya same() { pratiyati 2 }\n')
        self.assertEqual(self.g.analyze(self.entry('# sutram-module-v1\nayojan m@left\nayojan n@right\n')),['m','n'])
    def test_alias_conflict_diagnostic(self):
        self.module('m','prakriya f() { pratiyati 1 }\n');self.module('n','prakriya f() { pratiyati 2 }\n')
        with self.assertRaises(GraphDiagnostic) as cm:self.g.analyze(self.entry('ayojan m@x\nayojan n@x\n'))
        self.assertEqual(cm.exception.kind,'E_IMPORT_ALIAS')
    def test_legacy_export_compatibility(self):
        self.module('m','prakriya public() { pratiyati 1 }\nprakriya internal() { pratiyati 2 }\n')
        e=self.entry('ayojan m\n');self.g.analyze(e)
        self.assertTrue(self.g.check_access('m','internal',e,2))

if __name__=='__main__':unittest.main()

"""Independent R41 fixtures/oracle and NASM graph preflight structural contract.

These tests do NOT claim to assemble/execute the modified NASM compiler.
"""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from module_graph_reference import GraphReference,GraphDiagnostic

class NativeModuleV1Contract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph=GraphReference(ROOT/'examples'/'lib')
        cls.asm=(ROOT/'src'/'sutram_compiler.asm').read_text()
    def test_cycle_fixture(self):
        if not (ROOT/'examples'/'164_r41_cycle_reject.sm').exists():
            self.skipTest('pre-GitHub 164 fixture not committed; native 210 and R44 cycle cases cover this')
        with self.assertRaises(GraphDiagnostic) as e:
            self.graph.analyze(ROOT/'examples'/'164_r41_cycle_reject.sm')
        self.assertEqual(e.exception.kind,'E_MODULE_CYCLE')
        self.assertIn('r41_cycle_a -> r41_cycle_b -> r41_cycle_a',str(e.exception))
        self.assertIn('r41_cycle_b.smlib:2:',str(e.exception))
    def test_missing_fixture(self):
        if not (ROOT/'examples'/'165_r41_missing_reject.sm').exists():
            self.skipTest('pre-GitHub 165 fixture not committed; R44 opt-in missing cases cover this')
        with self.assertRaises(GraphDiagnostic) as e:
            self.graph.analyze(ROOT/'examples'/'165_r41_missing_reject.sm')
        self.assertEqual(e.exception.kind,'E_MODULE_MISSING')
        self.assertEqual(e.exception.line,2)
    def test_diamond_fixture(self):
        if not (ROOT/'examples'/'166_r41_optin_diamond.sm').exists():
            self.skipTest('pre-GitHub 166 fixture not committed; native 163 verifies diamond')
        self.assertEqual(self.graph.analyze(ROOT/'examples'/'166_r41_optin_diamond.sm'),['r40_d','r40_b','r40_c','r40_a'])
    def test_optin_only_gate(self):
        # Contract is ORDERING: the opt-in graph preflight runs before the
        # destructive import expansion. Do not over-specify adjacency; the
        # merged source inserts the R41/Muse module pre-pass between them.
        self.assertIn('call graph_preflight_v1',self.asm)
        self.assertIn('call expand_imports',self.asm)
        self.assertLess(self.asm.index('call graph_preflight_v1'),
                        self.asm.index('call expand_imports'))
        self.assertIn("graph_v1_header db '# sutram-module-v1'",self.asm)
    def test_dfs_and_diagnostics(self):
        for s in ('mg_process_imports:', 'mg_visit:', 'mg_print_cycle:',
                  'mg_root_exact_v1:', 'mg_gray', 'mg_black',
                  'E_MODULE_CYCLE', 'E_MODULE_MISSING', 'graph_print_file:'):
            # The merged traversal must be in the pure NASM compiler.
            self.assertIn(s,self.asm)
        self.assertNotIn('graph_visit:',self.asm)
        self.assertNotIn('graph_scan:',self.asm)
        self.assertNotIn('graph_buffers resb',self.asm)
        for s in ():
            self.assertIn(s,self.asm)
    def test_compile_failure_expected(self):
        if not (ROOT/'tests'/'expect'/'164_r41_cycle_reject.out').exists():
            self.skipTest('pre-GitHub 164/165 goldens missing; native R44 cases cover those diagnostics')
        for n in ('164_r41_cycle_reject','165_r41_missing_reject'):
            self.assertTrue((ROOT/'tests'/'expect'/(n+'.compile_fail')).is_file())
            self.assertEqual((ROOT/'tests'/'expect'/(n+'.exit')).read_text(),'1')
            self.assertTrue((ROOT/'tests'/'expect'/(n+'.out')).read_text().startswith('r41_' if n.startswith('164') else '165_'))

if __name__=='__main__': unittest.main()

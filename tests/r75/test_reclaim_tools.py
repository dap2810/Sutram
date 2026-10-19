"""R75 staging and measurement harness unit tests.

These tests do NOT assemble or run the Sutram compiler. Native status is NOT_RUN.
"""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]

def load(filename, name):
    s = importlib.util.spec_from_file_location(name, ROOT/'tools'/filename)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m

p = load('r75_reclaim_prepare.py','r75_prepare')
m = load('r75_kosh_checkpoint.py','r75_checkpoint')
SAMPLE = (b'.ge_call_koshpush:\n'
          + p.GROWTH + b'    ; capacity\n'
          + p.ALLOCATE + b'    ; copy complete\n'
          + p.PUBLISH + b'    ; appended\n'
          + b'.ge_call_koshpush_param_bad:\n')

class Staging(unittest.TestCase):
    def test_injects_exactly_three_hooks(self):
        c=p.patch_core(SAMPLE,b'; helper\n')
        self.assertEqual(c.count(b'call r71_emit_kosh_growth_guard'),1)
        self.assertEqual(c.count(b'call r71_emit_kosh_allocation_guard'),1)
        self.assertEqual(c.count(b'call r71_emit_kosh_reclaim'),1)
        self.assertLess(c.index(b'; copy complete'),c.index(b'call r71_emit_kosh_reclaim'))
    def test_refuses_double_application(self):
        with self.assertRaisesRegex(ValueError,'already present'):
            p.patch_core(p.patch_core(SAMPLE,b'; helper\n'),b'; helper\n')
    def test_refuses_missing_anchor(self):
        with self.assertRaisesRegex(ValueError,'anchor'):
            p.patch_core(SAMPLE.replace(p.ALLOCATE,b''),b'; helper\n')
    def test_refuses_duplicate_anchor(self):
        with self.assertRaisesRegex(ValueError,'anchor'):
            p.patch_core(SAMPLE.replace(p.GROWTH,p.GROWTH*2),b'; helper\n')
    def test_requires_explicit_unsafe_alias_optin(self):
        with self.assertRaisesRegex(ValueError,'experimental-unsafe-alias'):
            p.stage_sources(Path('/tmp'),Path('/tmp/r75-placeholder'),False)
    def test_git_blob(self):
        self.assertEqual(p.blob(b'hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a')
    def test_refuses_unsafe_relative_path(self):
        with self.assertRaisesRegex(ValueError,'invalid relative'):
            p.regular_read(Path('/tmp'),'../etc/passwd')

class Checkpoint(unittest.TestCase):
    def test_two_pause_markers(self):
        src=m.source(100)
        self.assertEqual(src.count('grahan()'),2)
        self.assertIn('R75_BASE',src)
        self.assertIn('R75_GROWN',src)
        self.assertIn('kosh_push(v, i)',src)
    def test_invalid_push_count(self):
        for n in (0,15,8000001):
            with self.subTest(n=n), self.assertRaises(ValueError):
                m.source(n)
    def test_read_live_proc_maps(self):
        actual=m.snapshot(os.getpid())
        self.assertGreater(actual['maps_count'],0)
        self.assertGreater(actual['VmSize_kb'],0)
    def test_read_marker_no_buffering(self):
        child=subprocess.Popen([sys.executable,'-c',
             "import time;print('R75_BASE',flush=True);time.sleep(.03)"],
             stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            self.assertIn(b'R75_BASE',m.until(child,b'R75_BASE',time.monotonic()+3))
        finally:
            child.communicate(timeout=3)

if __name__ == '__main__':
    unittest.main()

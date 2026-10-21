"""Harness tests, not native Sutram compiler acceptance."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[2] / 'tools' / 'r74_repro_build.py'
spec = importlib.util.spec_from_file_location('r74_repro_build', MODULE)
r74 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r74)

MOCK = '''import argparse, hashlib, json, os, pathlib
p=argparse.ArgumentParser()
p.add_argument('--check-only',action='store_true')
p.add_argument('--target')
p.add_argument('--output')
p.add_argument('--report')
a=p.parse_args()
if a.check_only:
 print(json.dumps({'status':'SOURCE_PINS_CHECKED','inputs': {'fake':'locked'}}))
else:
 data=b'\\x7fELFexample' + (os.urandom(8) if pathlib.Path('nondet').exists() else b'')
 pathlib.Path(a.output).write_bytes(data)
 status={'status':'BUILT_FORMAT_CHECKED','binary_sha256':hashlib.sha256(data).hexdigest()}
 pathlib.Path(a.report).write_text(json.dumps(status))
 print(json.dumps(status))
'''

class ReproBuildTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'repo'
        (self.root / 'tools').mkdir(parents=True)
        (self.root / 'tools' / 'r69_build.py').write_text(MOCK)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        subprocess.run(['git', '-C', str(self.root), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(self.root), '-c', 'user.email=test@example.com',
                        '-c', 'user.name=Test', 'commit', '-qm', 'source'], check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_repeatable(self):
        out = r74.prove(self.root)
        self.assertEqual(out['repeatability'], 'PASS')
        self.assertEqual(out['runs'][0]['sha256'], out['runs'][1]['sha256'])

    def test_refuses_dirty_input(self):
        (self.root / 'dirty').write_text('untracked')
        with self.assertRaisesRegex(ValueError, 'dirty'):
            r74.prove(self.root)

    def test_refuses_nondeterminism(self):
        (self.root / 'nondet').write_text('1')
        subprocess.run(['git', '-C', str(self.root), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(self.root), '-c', 'user.email=test@example.com',
                        '-c', 'user.name=Test', 'commit', '-qm', 'nondeterminism'], check=True)
        with self.assertRaisesRegex(RuntimeError, 'different'):
            r74.prove(self.root)

if __name__ == '__main__':
    unittest.main()

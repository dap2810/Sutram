#!/usr/bin/env python3
"""tools/check_accept_windows_log.py: what a returned Windows log does and does not prove."""
from __future__ import annotations
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import check_accept_windows_log as chk  # noqa: E402


def log(tree: Path) -> dict:
    h = hashlib.sha256((tree / 'Sutram-Setup.exe').read_bytes()).hexdigest()
    return {
        'tool': 'tools/accept-windows.ps1', 'schema': 1, 'verdict': 'PASS',
        'environment': {'environment': 'Windows', 'wine': False, 'elevated': False, 'windows_build': '26100'},
        'artefacts': [{'role': 'setup', 'path': 'C:\\s\\Sutram-Setup.exe', 'sha256': h, 'bytes': 3}],
        'checks': [{'id': 'install-wizard', 'status': 'PASS', 'required': True, 'environment': 'Windows'},
                   {'id': 'temp-staging-cleaned', 'status': 'FAIL', 'required': False, 'environment': 'Windows'}],
    }


class CheckLog(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tree = Path(self.tmp.name)
        (self.tree / 'Sutram-Setup.exe').write_bytes(b'MZ!')

    def tearDown(self):
        self.tmp.cleanup()

    def run_log(self, data: dict) -> int:
        p = self.tree / 'accept-windows.json'
        p.write_text(json.dumps(data), encoding='utf-8')
        return chk.main([str(p), '--root', str(self.tree)])

    def test_windows_unelevated_all_pass_matching_hash_is_accepted(self):
        self.assertEqual(0, self.run_log(log(self.tree)))   # an advisory FAIL does not block

    def test_wine_is_never_acceptance(self):
        d = log(self.tree); d['environment'].update(environment='Wine', wine=True)
        self.assertEqual(1, self.run_log(d))

    def test_elevated_run_is_not_acceptance(self):
        d = log(self.tree); d['environment']['elevated'] = True
        self.assertEqual(1, self.run_log(d))

    def test_required_not_run_is_not_acceptance(self):
        d = log(self.tree); d['checks'][0]['status'] = 'NOT-RUN'
        self.assertEqual(1, self.run_log(d))

    def test_a_different_binary_is_not_acceptance(self):
        d = copy.deepcopy(log(self.tree)); d['artefacts'][0]['sha256'] = '0' * 64
        self.assertEqual(1, self.run_log(d))

    def test_bad_status_is_an_invalid_log(self):
        d = log(self.tree); d['checks'][0]['status'] = 'OK'
        self.assertEqual(2, self.run_log(d))

    def test_script_is_ascii_and_names_every_required_check(self):
        s = (ROOT / 'tools/accept-windows.ps1').read_bytes()
        self.assertTrue(all(b < 128 for b in s), 'Windows PowerShell 5.1 reads BOM-less files as ANSI')
        text = s.decode()
        for cid in ('runner-not-elevated', 'install-no-elevation-prompt', 'install-wizard', 'install-footprint',
                    'devanagari-cli', 'ide-launches', 'ide-menus-english', 'ide-buttons-english', 'devanagari-ide',
                    'tab-indent', 'shift-tab-dedent', 'unsaved-guard', 'uninstall-removes-install'):
            self.assertIn("'" + cid + "'", text)
        self.assertNotIn('RunAs', text.replace('no RunAs verb', ''))


if __name__ == '__main__':
    unittest.main()

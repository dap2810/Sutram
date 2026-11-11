"""A failing or skipped gate still exists; document counts must distinguish these."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / 'tools/doc_counts_gate.py'


class CountTests(unittest.TestCase):
    def check_claim(self, claim):
        with tempfile.TemporaryDirectory() as d:
            Path(d, 'PROJECT-MASTER.md').write_text(claim)
            return subprocess.run([sys.executable, str(SCRIPT), '--repo', d,
                                   '--totals', '73 7 2', '--suite-pass', '327'],
                                  capture_output=True, text=True)

    def test_historical_success_is_not_impossible_when_gates_fail(self):
        r = self.check_claim('81 PASS, 0 FAIL')
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn('NOTE', r.stdout)

    def test_pair_not_impossible_because_some_gates_are_skipped(self):
        r = self.check_claim('81/82')
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_more_than_total_still_fails(self):
        for claim in ('83 PASS, 0 FAIL', '83/83'):
            with self.subTest(claim=claim):
                r = self.check_claim(claim)
                self.assertEqual(r.returncode, 1)
                self.assertIn('only 82 gates exist', r.stdout)


if __name__ == '__main__':
    unittest.main()

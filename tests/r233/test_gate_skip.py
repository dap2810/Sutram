"""Exercise the real gates.sh dispatcher without running unrelated gates."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class GateSkipTests(unittest.TestCase):
    def dispatch(self, output):
        text = (ROOT / 'tools/gates.sh').read_text()
        helpers = text[text.index('PASS=0;'):text.index('[ -f src/')]
        dispatcher = text[text.index('run_gate()'):text.index('run_gate "regression suite"')]
        with tempfile.TemporaryDirectory() as d:
            fixture = Path(d, 'output.txt')
            fixture.write_text(output)
            script = helpers + dispatcher + '\nrun_gate "R124 lazy commit" cat "$1"\nprintf "COUNTS %s %s %s\\n" "$PASS" "$FAIL" "$SKIP"\n'
            return subprocess.run(['sh', '-c', script, 'test-gate', str(fixture)], capture_output=True, text=True).stdout

    def test_missing_wine_is_skip(self):
        text = self.dispatch('NOT RUN  no Wine here: the PE runs and the commit checks need it\nr124 lazy commit: 0 checks, 0 failed\n')
        self.assertIn('COUNTS 0 0 1', text)

    def test_real_pass_stays_pass(self):
        self.assertIn('COUNTS 1 0 0', self.dispatch('r124 lazy commit: 3 checks, 0 failed\n'))

    def test_failure_stays_failure(self):
        self.assertIn('COUNTS 0 1 0', self.dispatch('FAIL wrong commit\nr124 lazy commit: 3 checks, 1 failed\n'))


if __name__ == '__main__':
    unittest.main()

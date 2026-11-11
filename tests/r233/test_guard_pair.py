"""Exercise the public guard entry point with controlled compiler outcomes."""
import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('guard', Path(__file__).resolve().parents[2] / 'tools/guard_pair.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class GuardTests(unittest.TestCase):
    def compare(self, old, new):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name in ('old', 'new'):
                (root / name / 'examples').mkdir(parents=True)
                (root / name / 'examples/t.sm').write_text('mukhya() {}\n')
            outcomes = iter((old, new))

            def compile(cmd, **kw):
                result = next(outcomes)
                if result == 'timeout':
                    raise subprocess.TimeoutExpired(cmd, 60)
                rc, output, stdout, stderr = result
                if output is not None:
                    Path(cmd[-1]).write_bytes(output)
                # Model diagnostics that echo the actual input and output paths.
                stdout = stdout.replace(b'{source}', cmd[1].encode()).replace(b'{output}', cmd[-1].encode())
                stderr = stderr.replace(b'{source}', cmd[1].encode()).replace(b'{output}', cmd[-1].encode())
                return subprocess.CompletedProcess(cmd, rc, stdout, stderr)

            with patch.object(guard.subprocess, 'run', side_effect=compile), contextlib.redirect_stdout(io.StringIO()) as log:
                rc = guard.main([str(root / 'old'), 'old-compiler', str(root / 'new'), 'new-compiler', str(root / 'results')])
            return rc, log.getvalue()

    def test_matching_timeouts_fail(self):
        self.assertEqual(self.compare('timeout', 'timeout')[0], 1)

    def test_matching_crashes_fail(self):
        self.assertEqual(self.compare((-11, None, b'', b''), (-11, None, b'', b''))[0], 1)

    def test_missing_success_outputs_fail(self):
        self.assertEqual(self.compare((0, None, b'', b''), (0, None, b'', b''))[0], 1)

    def test_output_from_failed_compiles_fails(self):
        self.assertEqual(self.compare((1, b'ELF', b'', b''), (1, b'ELF', b'', b''))[0], 1)

    def test_changed_stdout_refusal_fails(self):
        self.assertEqual(self.compare((1, None, b'error A', b''), (1, None, b'error B', b''))[0], 1)

    def test_changed_stderr_refusal_fails(self):
        self.assertEqual(self.compare((1, None, b'', b'error A'), (1, None, b'', b'error B'))[0], 1)

    def test_refusal_paths_normalized(self):
        result = (1, None, b'{source}: error', b'{output}: refused')
        rc, log = self.compare(result, result)
        self.assertEqual(rc, 0)
        self.assertIn('1 refused identically', log)

    def test_successful_bytes_equal(self):
        result = (0, b'ELF', b'', b'')
        rc, log = self.compare(result, result)
        self.assertEqual(rc, 0)
        self.assertIn('1 byte-identical', log)

    def test_changed_bytes_fail(self):
        self.assertEqual(self.compare((0, b'ELF-A', b'', b''), (0, b'ELF-B', b'', b''))[0], 1)


if __name__ == '__main__':
    unittest.main()

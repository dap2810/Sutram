"""Acceptance-harness tests with mocked child processes, not Sutram execution."""
from __future__ import annotations
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
MODULE = Path(os.environ.get('SUTRAM_ACCEPTANCE_MODULE', ROOT / 'tools/r66_native_acceptance.py'))
spec = importlib.util.spec_from_file_location('clean_r66_acceptance', MODULE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class OutputGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.compiler = self.root/'compiler'
        self.compiler.write_bytes(b'not executed: process calls are mocked')
        self.source = self.root/'case.sm'
        self.source.write_text('mukhya() {}\n')
        self.output = self.root/'case.bin'

    def completed(self, code=0, stdout=b'', stderr=b''):
        return subprocess.CompletedProcess([], code, stdout, stderr)

    def test_stale_output_rejected_before_compiler_call(self):
        self.output.write_bytes(b'stale executable')
        with patch.object(m, 'run', return_value=self.completed()) as run:
            with self.assertRaisesRegex(AssertionError, 'already exists'):
                m.compile_program(self.compiler, self.source, self.output)
            run.assert_not_called()
        self.assertEqual(self.output.read_bytes(), b'stale executable')

    def test_dangling_output_symlink_rejected_before_call(self):
        self.output.symlink_to(self.root/'missing')
        with patch.object(m, 'run', return_value=self.completed()) as run:
            with self.assertRaisesRegex(AssertionError, 'already exists'):
                m.compile_program(self.compiler, self.source, self.output)
            run.assert_not_called()
        self.assertTrue(self.output.is_symlink())

    def test_directory_output_rejected_before_call(self):
        self.output.mkdir()
        with patch.object(m, 'run') as run:
            with self.assertRaisesRegex(AssertionError, 'already exists'):
                m.compile_program(self.compiler, self.source, self.output)
            run.assert_not_called()

    def test_no_output_is_not_success(self):
        with patch.object(m, 'run', return_value=self.completed()):
            with self.assertRaisesRegex(AssertionError, 'compile failed'):
                m.compile_program(self.compiler, self.source, self.output)

    def test_successful_fresh_output(self):
        def emit(cmd):
            self.output.write_bytes(b'new binary')
            return self.completed()
        with patch.object(m, 'run', side_effect=emit):
            m.compile_program(self.compiler, self.source, self.output, 'gujarati')
        self.assertEqual(self.output.read_bytes(), b'new binary')

    def test_nonzero_compilation_is_not_success(self):
        def emit(cmd):
            self.output.write_bytes(b'partial binary')
            return self.completed(1, stderr=b'compile error')
        with patch.object(m, 'run', side_effect=emit):
            with self.assertRaisesRegex(AssertionError, 'compile failed'):
                m.compile_program(self.compiler, self.source, self.output)

    def test_symlink_created_by_compiler_is_rejected(self):
        target = self.root/'outside.bin'
        target.write_bytes(b'not a new program')
        def emit(cmd):
            self.output.symlink_to(target)
            return self.completed()
        with patch.object(m, 'run', side_effect=emit):
            with self.assertRaisesRegex(AssertionError, 'compile failed'):
                m.compile_program(self.compiler, self.source, self.output)

    def test_timeout_does_not_become_pass(self):
        with patch.object(m, 'run', side_effect=subprocess.TimeoutExpired('compiler', 12)):
            with self.assertRaises(subprocess.TimeoutExpired):
                m.compile_program(self.compiler, self.source, self.output)

    def test_expected_rejection_without_output(self):
        for stdout, stderr in ((b'E_UTF8 bad input', b''), (b'', b'E_UTF8 bad input')):
            with self.subTest(stream='stdout' if stdout else 'stderr'):
                with patch.object(m, 'run', return_value=self.completed(1, stdout, stderr)):
                    result = m.rejected_case(self.compiler, self.source, self.output)
                self.assertEqual(result['status'], 'PASS')
                self.assertEqual(result['exit'], 1)
                self.assertFalse(result['output_created'])

    def test_error_that_leaves_binary_is_rejected(self):
        def emit(cmd):
            self.output.write_bytes(b'unsafe partial output')
            return self.completed(1, stderr=b'E_UTF8')
        with patch.object(m, 'run', side_effect=emit):
            with self.assertRaisesRegex(AssertionError, 'created output'):
                m.rejected_case(self.compiler, self.source, self.output)

    def test_error_that_leaves_dangling_symlink_is_rejected(self):
        def emit(cmd):
            self.output.symlink_to(self.root/'missing')
            return self.completed(1, stderr=b'E_UTF8')
        with patch.object(m, 'run', side_effect=emit):
            with self.assertRaisesRegex(AssertionError, 'created output'):
                m.rejected_case(self.compiler, self.source, self.output)

    def test_rejection_requires_expected_exit_and_diagnostic(self):
        for code, diag in ((0,b'E_UTF8'), (2,b'E_UTF8'), (1,b'other error')):
            with self.subTest(code=code,diag=diag), patch.object(m, 'run', return_value=self.completed(code, stderr=diag)):
                with self.assertRaisesRegex(AssertionError, 'rejection failed'):
                    m.rejected_case(self.compiler, self.source, self.output)

    def test_rejection_refuses_preexisting_output(self):
        self.output.write_bytes(b'preserve')
        with patch.object(m, 'run') as run:
            with self.assertRaisesRegex(AssertionError, 'already exists'):
                m.rejected_case(self.compiler, self.source, self.output)
            run.assert_not_called()
        self.assertEqual(self.output.read_bytes(), b'preserve')

    def test_reference_cannot_be_compiler_itself(self):
        with patch('sys.argv', ['r66', '--compiler', str(self.compiler), '--reference', str(self.compiler)]), patch.object(m, 'run') as run:
            with self.assertRaises(SystemExit) as raised:
                m.main()
            self.assertEqual(raised.exception.code, 2)
            run.assert_not_called()

    def test_reference_cannot_be_hardlink_of_compiler(self):
        reference = self.root/'reference'
        reference.hardlink_to(self.compiler)
        with patch('sys.argv', ['r66', '--compiler', str(self.compiler), '--reference', str(reference)]), patch.object(m, 'run') as run:
            with self.assertRaises(SystemExit) as raised:
                m.main()
            self.assertEqual(raised.exception.code, 2)
            run.assert_not_called()

if __name__ == '__main__':
    unittest.main()

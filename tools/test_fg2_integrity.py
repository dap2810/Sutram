"""Unit tests for the independently verified FG2 recovery fence."""
import hashlib
import unittest
from verify_fg2_restoration import BASELINE, CURRENT, EXPECTED, effective_lines


class FG2RecoveryTests(unittest.TestCase):
    def test_original_snapshot_sha(self):
        self.assertEqual(hashlib.sha256(BASELINE.read_bytes()).hexdigest(), EXPECTED)

    def test_flag_off_source_is_identical(self):
        self.assertEqual(effective_lines(CURRENT.read_text()), effective_lines(BASELINE.read_text()))

    def test_detect_loss_of_optimization(self):
        source = CURRENT.read_text()
        self.assertIn('.gfb_left_first_rhs_reg:', source)
        degraded = source.replace('.gfb_left_first_rhs_reg:', '.gfb_lost_fast_path:', 1)
        self.assertNotEqual(effective_lines(degraded), effective_lines(BASELINE.read_text()))

    def test_experimental_changes_cannot_leak(self):
        source = CURRENT.read_text()
        sample = '%ifdef SUTRAM_EXPERIMENTAL_XMM_CACHE\n' \
                 '    this_instruction_must_not_compile_in_release\n%endif\n'
        self.assertEqual(effective_lines(source), effective_lines(source + sample))


if __name__ == '__main__':
    unittest.main()

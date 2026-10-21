"""Conservative inventory regression fixtures. No Sutram compiler is run."""
from pathlib import Path
import importlib.util
import unittest

p = Path(__file__).resolve().parents[2] / 'tools/r83_diagnostic_coverage.py'
spec = importlib.util.spec_from_file_location('r83_diagnostics', p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class CoverageFixtures(unittest.TestCase):
    def test_default_comment_association(self):
        text = '# "Sutram Error: example"\nmsg_one\t"अनुवाद"\n'
        self.assertEqual(m.extract_default_comments(text)['msg_one'], 'Sutram Error: example')

    def test_matching_output_evidence_not_native_pass(self):
        rows = m.build(['k'], [], {'k': 'Sutram Error: original'},
                       {'case': 'Sutram Error: original\n'}, set())
        self.assertEqual(rows['entries'][0]['status'], 'CHECKED_IN_EXPECTATION_CANDIDATE')
        self.assertEqual(rows['native_execution'], 'NOT_RUN')
        self.assertFalse(rows['all_diagnostics_covered'])

    def test_cli_diagnostic_is_not_source_program(self):
        rows = m.build(['msg_usage'], [], {}, {}, set())
        self.assertEqual(rows['entries'][0]['status'], 'NON_SOURCE_CLI_OR_SHELL')

    def test_ide_key_is_not_compiler_error(self):
        rows = m.build([], ['st_bhasha_w'], {}, {}, set())
        self.assertEqual(rows['entries'][0]['status'], 'NON_SOURCE_IDE_MESSAGE')

    def test_no_evidence_does_not_mean_unreachable(self):
        rows = m.build(['unknown_diagnostic'], [], {}, {}, set())
        self.assertEqual(rows['entries'][0]['status'], 'UNMAPPED_NEEDS_REPRO')

    def test_broken_probe_path_is_detected(self):
        rows = m.build(['msg_kosh_peek_empty'], [], {}, {}, set())
        self.assertEqual(rows['entries'][0]['status'], 'BROKEN_PROBE_PATH')

    def test_present_probe_stays_unverified(self):
        pth = m.PROBE_CANDIDATES['msg_kosh_peek_empty']
        rows = m.build(['msg_kosh_peek_empty'], [], {}, {}, {pth})
        self.assertEqual(rows['entries'][0]['status'], 'PROBE_AVAILABLE_NOT_VERIFIED')

    def test_real_current_checkout_inventory(self):
        root = Path(__file__).resolve().parents[2]
        if not (root/'lang/sanskrit.sandesh').exists():
            self.skipTest('No source checkout')
        rows = m.run(root)
        self.assertEqual(rows['compiler_messages'], 119)   # R23: +r23_msg_slice_base, +r23_msg_slice_return; R24: +r24_msg_method_hint; R25: +4 phal messages; R26: +the handler message; R28: +the object-mode message; R32: +2 FFI messages; R33: +3 FFI kind messages
        self.assertEqual(rows['ide_messages'], 23)
        self.assertEqual(rows['total_messages'], 142)
        self.assertFalse(rows['counts'].get('BROKEN_PROBE_PATH'))

if __name__ == '__main__':
    unittest.main()

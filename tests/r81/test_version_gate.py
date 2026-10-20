"""R81 gate unit fixtures only; not a native Sutram runtime test."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[2] / 'tools' / 'r81_version_gate.py'
spec = importlib.util.spec_from_file_location('r81_version_gate', MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def compiler(n):
    return 'section .data\nmsg_version db "Sutram 1.0 (v%d) - sampurna sutra", 10\n' % n


def log(n):
    return '## v%d - release\n\n## v%d - previous\n' % (n, n-1)


class VersionGateTests(unittest.TestCase):
    def test_current_version_matches(self):
        self.assertEqual(mod.check(log(207), compiler(207))['status'], 'PASS')

    def test_stale_v182_refused(self):
        result = mod.check(log(207), compiler(182))
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['compiler_banner_version'], 'v182')

    def test_changelog_leading_version_not_historical(self):
        self.assertEqual(mod.check(log(207), compiler(206))['status'], 'FAIL')

    def test_missing_changelog_refused(self):
        self.assertEqual(mod.check('no release here', compiler(207))['status'], 'FAIL')

    def test_missing_compiler_banner_refused(self):
        self.assertEqual(mod.check(log(207), 'section .text')['status'], 'FAIL')

    def test_duplicate_banner_refused(self):
        self.assertEqual(mod.check(log(207), compiler(207)*2)['status'], 'FAIL')

    def test_comments_do_not_match(self):
        src='; msg_version db "Sutram 1.0 (v207)"\n'+compiler(207)
        self.assertEqual(mod.check(log(207), src)['status'], 'PASS')

    def test_sourcelines_containing_other_versions_are_ignored(self):
        self.assertEqual(mod.check(log(207), compiler(207) + 'msg_other db "v182"\n')['status'], 'PASS')

    def test_run_real_files_and_hashes(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            (base/'src').mkdir()
            (base/'docs').mkdir()
            (base/'src/sutram_compiler.asm').write_text(compiler(207))
            (base/'docs/CHANGELOG.md').write_text(log(207))
            actual = mod.run(base)
            self.assertEqual(actual['status'], 'PASS')
            self.assertEqual(len(actual['compiler_source_sha256']), 64)
            self.assertFalse(actual['native_binary_executed'])

    def test_installer_invokes_gate_before_compiling(self):
        builder = (Path(__file__).resolve().parents[2] / 'windows' /
                   'native-installer' / 'build-installer.ps1').read_text()
        gate = '[void](Invoke-BoundedProcess $python @($versionGate'
        build = '[void](Invoke-BoundedProcess $python @($buildTool'
        self.assertIn("r81_version_gate.py", builder)
        self.assertEqual(builder.count(gate), 1)
        self.assertIn(build, builder)
        self.assertLess(builder.index(gate), builder.index(build))

    def test_refuses_symlinked_input(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);(base/'src').mkdir();(base/'docs').mkdir()
            (base/'other').write_text(compiler(207))
            (base/'src/sutram_compiler.asm').symlink_to(base/'other')
            (base/'docs/CHANGELOG.md').write_text(log(207))
            with self.assertRaisesRegex(ValueError, 'symlink'):
                mod.run(base)

if __name__ == '__main__':
    unittest.main()

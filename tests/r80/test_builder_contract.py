"""Source-order contracts only, NOT PowerShell execution."""
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[2]/'windows/native-installer/build-installer.ps1').read_text()

class BuildSourceContract(unittest.TestCase):
    def test_fresh_canonical_build_precedes_zip(self):
        self.assertIn("'tools\\r69_build.py'", SOURCE)
        self.assertLess(SOURCE.index('$buildTool,'), SOURCE.index('Compress-Archive'))
        self.assertNotIn("@('win\\sutram.exe','bin\\sutram.exe')", SOURCE)

    def test_embedded_verification_precedes_publication(self):
        self.assertLess(SOURCE.index("@('--setup',$candidate"), SOURCE.index('[IO.File]::Replace($candidate'))
        self.assertLess(SOURCE.index("$candidate @('--self-test')"), SOURCE.index('[IO.File]::Replace($candidate'))
        self.assertIn("'previous-setup.exe'", SOURCE)

    def test_not_dependent_on_diagnostic_translation(self):
        self.assertNotIn('msg_version', SOURCE)
        self.assertNotIn('-notmatch', SOURCE)
        self.assertIn('PAYLOAD SHA-256:', SOURCE)
        self.assertIn('Owner install/upgrade/uninstall acceptance remains separate.', SOURCE)

if __name__ == '__main__':
    unittest.main()

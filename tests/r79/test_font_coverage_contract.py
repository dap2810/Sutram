"""Round 79 static font-coverage review (not native Windows acceptance).

Run: python3 -m unittest discover -s tests/r79 -p 'test_*.py' -v
"""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "windows" / "native-installer" / "install-core.ps1"
EXPECTED = {
    "Devanagari": (0x0915, {"sanskrit", "hindi", "marathi"}),
    "Gujarati": (0x0A95, {"gujarati"}),
    "Bengali": (0x0995, {"bengali"}),
    "Gurmukhi": (0x0A15, {"punjabi"}),
    "Odia": (0x0B15, {"odia"}),
    "Tamil": (0x0B95, {"tamil"}),
    "Telugu": (0x0C15, {"telugu"}),
    "Kannada": (0x0C95, {"kannada"}),
    "Malayalam": (0x0D15, {"malayalam"}),
}
ENTRY = re.compile(
    r"@\{\s*Script='([^']+)';\s*Packs='([^']+)';\s*Code=0x([0-9A-Fa-f]+);"
)

class FontCoverageContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding="utf-8")
        a = cls.source.index("function Check-R79IndicFonts(")
        b = cls.source.index("# R77: conservative rollback", a)
        cls.implementation = cls.source[a:b]
        cls.table = [
            (name, int(cp, 16), set(packs.split(",")))
            for name, packs, cp in ENTRY.findall(cls.implementation)
        ]

    def test_all_nine_scripts_present_once(self):
        self.assertEqual(set(name for name, _, _ in self.table), set(EXPECTED))
        self.assertEqual(len(self.table), 9)

    def test_all_eleven_language_packs_covered_once(self):
        flattened = [pack for _, _, packs in self.table for pack in packs]
        self.assertEqual(len(flattened), 11)
        self.assertEqual(len(set(flattened)), 11)

    def test_each_script_has_correct_unicode_representative(self):
        for name, codepoint, packs in self.table:
            with self.subTest(script=name):
                self.assertEqual((codepoint, packs), EXPECTED[name])

    def test_uses_actual_glyph_indices_not_only_family_names(self):
        self.assertIn("GetGlyphIndicesW", self.implementation)
        self.assertIn("CreateFontW", self.implementation)
        self.assertIn("0xffff", self.implementation)
        self.assertIn("InstalledFontCollection", self.implementation)

    def test_single_install_time_check(self):
        self.assertEqual(self.source.count("Check-R79IndicFonts (-not $VerifyOnly)"), 1)

    def test_missing_coverage_is_recorded_and_reported(self):
        self.assertIn("R79 FONT MISSING:", self.implementation)
        self.assertIn("R79 FONT SUMMARY:", self.implementation)
        self.assertIn("if ($missing.Count -gt 0)", self.implementation)
        self.assertIn("Windows Settings > Time & language", self.implementation)

    def test_probe_failure_is_not_silent_success(self):
        self.assertIn("could not verify Indic script fonts", self.implementation)
        self.assertIn("WARNING:", self.implementation)

    def test_does_not_bundle_or_download_font_files(self):
        self.assertNotIn("Invoke-WebRequest", self.implementation)
        self.assertNotIn("Start-BitsTransfer", self.implementation)
        self.assertNotIn("Copy-Item", self.implementation)
        self.assertNotIn("AddFontResourceEx", self.implementation)
        self.assertIn("Microsoft font files are never bundled or downloaded.", self.implementation)

    def test_does_not_change_registry_or_require_elevation(self):
        self.assertNotIn("HKLM:", self.implementation)
        self.assertNotIn("New-ItemProperty", self.implementation)
        self.assertNotIn("Start-Process -Verb RunAs", self.implementation)

    def test_rollback_contract_still_exists(self):
        self.assertIn("function Undo-R77FailedFreshInstall", self.source)

if __name__ == "__main__":
    unittest.main()

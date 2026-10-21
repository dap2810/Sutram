"""R83 structural-translation regression fixtures; not native Sutram execution."""
from pathlib import Path
import importlib.util
import json
import unittest

MOD = Path(__file__).resolve().parents[2] / "tools" / "r83_pack_structure.py"
spec = importlib.util.spec_from_file_location("r83_pack", MOD)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def entry(key, text):
    return key + "\t" + json.dumps(text, ensure_ascii=False) + "\n"


def baseline():
    return {
        name: entry("name", "सूत्रम्" if name == "sanskrit" else "नाम") +
              entry("error", "Sutram Error [E_BAD]: '")
        for name in m.PACKS
    }


class StructureFixtures(unittest.TestCase):
    def test_parser_unescapes_json(self):
        entries, errors = m.parse_pack(entry("a", "क\nप"))
        self.assertEqual(errors, [])
        self.assertEqual(entries["a"], "क\nप")

    def test_duplicate_key_detected(self):
        _, errors = m.parse_pack(entry("a", "क") + entry("a", "प"))
        self.assertEqual(len(errors), 1)

    def test_missing_key_detected(self):
        packs = baseline()
        packs["gujarati"] = entry("name", "ક")
        self.assertIn("missing key", {e["issue"] for e in m.examine(packs)["packs"]["gujarati"]["failures"]})

    def test_missing_placeholder_detected(self):
        packs = baseline()
        packs["sanskrit"] = entry("x", "Sutram Error {kw:likha}: ")
        packs["gujarati"] = entry("x", "Sutram Error: ")
        self.assertIn("placeholder missing",
                      {e["issue"] for e in m.examine(packs)["packs"]["gujarati"]["failures"]})

    def test_extra_placeholder_is_review_not_hard_fail(self):
        packs = baseline()
        packs["sanskrit"] = entry("x", "Sutram Error ")
        packs["gujarati"] = entry("x", "Sutram Error {kw:likha}")
        row = m.examine(packs)["packs"]["gujarati"]
        self.assertEqual(row["hard_violations"], 0)
        self.assertTrue(row["review_candidates"])

    def test_wrong_script_detected(self):
        packs = baseline()
        packs["sanskrit"] = entry("x", "नमः")
        packs["gujarati"] = entry("x", "नमः")
        self.assertIn("wrong-script Unicode letter/mark",
                      {e["issue"] for e in m.examine(packs)["packs"]["gujarati"]["failures"]})

    def test_empty_translation_detected(self):
        packs = baseline()
        packs["hindi"] = entry("name", "")
        self.assertIn("empty message",
                      {e["issue"] for e in m.examine(packs)["packs"]["hindi"]["failures"]})

    def test_error_tag_change_detected(self):
        packs = baseline()
        packs["gujarati"] = entry("error", "Sutram Error [E_OTHER]: '")
        self.assertIn("Sutram Error/[E_] identifiers changed",
                      {e["issue"] for e in m.examine(packs)["packs"]["gujarati"]["failures"]})

    def test_actual_checkout_structure(self):
        root = Path(__file__).resolve().parents[2]
        if not (root / "lang" / "sanskrit.sandesh").exists():
            self.skipTest("No complete checkout")
        report = m.run(root)
        self.assertEqual(report["canonical_keys"], 136)   # R23: two slice messages; R24: the method hint; R25: four phal messages
        self.assertEqual(len(report["packs"]), 11)
        self.assertEqual(report["status"], "PASS",
                         str({k: v["failures"][:3] for k, v in report["packs"].items()
                              if v["hard_violations"]}))


if __name__ == "__main__":
    unittest.main()

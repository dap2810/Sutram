"""Local fixtures for R83; separate from actual native Sutram acceptance."""
from pathlib import Path
import importlib.util
import unittest

MOD = Path(__file__).resolve().parents[2] / "tools" / "r83_pack_structure.py"
spec = importlib.util.spec_from_file_location("r83_pack", MOD)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def baseline():
    return {p: 'name\t"सूत्रम्"\nerror\t"Sutram Error [E_BAD]: \'\n"'
            if p == "sanskrit"
            else 'name\t"क"\nerror\t"Sutram Error [E_BAD]: \'\n"'
            for p in m.PACKS}


class StructureFixtures(unittest.TestCase):
    def test_real_pack_parser_handles_escaped_json(self):
        rows, errors = m.parse_pack('a\t"क\\\\nप"\n')
        self.assertEqual(errors, [])
        self.assertEqual(rows["a"], "क\nप")

    def test_duplicate_key_is_refused(self):
        rows, errors = m.parse_pack('a\t"क"\na\t"प"\n')
        self.assertEqual(len(errors), 1)

    def test_missing_key_detected(self):
        packs = baseline()
        packs["gujarati"] = 'name\t"ક"\n'
        self.assertTrue(any(x["issue"] == "missing key" for x in m.examine(packs)["packs"]["gujarati"]["failures"]))

    def test_missing_placeholder_detected(self):
        packs = baseline()
        packs["sanskrit"] = 'x\t"Sutram Error {kw:likha}: "\n'
        packs["gujarati"] = 'x\t"Sutram Error: "\n'
        errors = m.examine(packs)["packs"]["gujarati"]["failures"]
        self.assertTrue(any(e["issue"] == "placeholder missing" for e in errors))

    def test_extra_placeholder_only_review_candidate(self):
        packs = baseline()
        packs["sanskrit"] = 'x\t"Sutram Error "\n'
        packs["gujarati"] = 'x\t"Sutram Error {kw:likha}"\n'
        self.assertEqual(m.examine(packs)["packs"]["gujarati"]["hard_violations"], 0)
        self.assertTrue(m.examine(packs)["packs"]["gujarati"]["review_candidates"])

    def test_wrong_script_flagged(self):
        packs = baseline()
        packs["sanskrit"] = 'x\t"नमः"\n'
        packs["gujarati"] = 'x\t"नमः"\n'
        self.assertTrue(any(e["issue"] == "wrong-script Unicode letter/mark"
                            for e in m.examine(packs)["packs"]["gujarati"]["failures"]))

    def test_empty_message_flagged(self):
        packs = baseline()
        packs["hindi"] = 'name\t""\n'
        self.assertTrue(any(e["issue"] == "empty message"
                            for e in m.examine(packs)["packs"]["hindi"]["failures"]))

    def test_error_identifier_tag_preserved(self):
        packs = baseline()
        packs["gujarati"] = 'error\t"Sutram Error [E_DIFFERENT]: \'\n'
        self.assertTrue(any(e["issue"].startswith("Sutram Error")
                            for e in m.examine(packs)["packs"]["gujarati"]["failures"]))

    def test_actual_repository_if_available(self):
        root = Path(__file__).resolve().parents[2]
        if not (root / "lang" / "sanskrit.sandesh").exists():
            self.skipTest("No complete Sutram checkout present")
        result = m.run(root)
        self.assertEqual(result["canonical_keys"], 128)
        self.assertEqual(len(result["packs"]), 11)
        self.assertEqual(result["status"], "PASS",
                         str({k: p["failures"][:3] for k, p in result["packs"].items()
                              if p["hard_violations"]}))


if __name__ == "__main__":
    unittest.main()

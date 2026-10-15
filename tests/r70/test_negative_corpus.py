"""R70 harness tests with MOCKED compiler processes. Not native Sutram evidence."""
from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("r70_corpus", ROOT / "tools/r70_negative_corpus.py")
r = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(r)


class CorpusFiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        shutil.copytree(ROOT / "tests/negative/r70", self.root / "tests/negative/r70")
        self.manifest = self.root / r.MANIFEST
        self.doc = json.loads(self.manifest.read_text("utf-8"))

    def save(self):
        self.manifest.write_text(json.dumps(self.doc), encoding="utf-8")

    def test_six_categories_validate_without_compilation(self):
        loaded = r.load_corpus(self.root)
        self.assertEqual({c["category"] for c in loaded["cases"]}, r.CATEGORIES)

    def test_inherited_sources_and_diagnostics_match_git_ids(self):
        count = 0
        for case in self.doc["cases"]:
            origin = case["provenance"]
            if origin["level"] == "inherited_exact_golden":
                self.assertEqual(r.git_blob(r.read_case(self.root, case)), origin["source_git_blob"])
                self.assertEqual(r.git_blob(case["diagnostic"]["text"].encode()), origin["golden_git_blob"])
                count += 1
        self.assertEqual(count, 2)

    def test_malformed_fixture_is_bytes_not_unicode_replacement(self):
        case = next(c for c in self.doc["cases"] if c["id"] == "malformed_literal")
        data = r.read_case(self.root, case)
        self.assertIn(b"\xe0\xa5 ", data)
        with self.assertRaises(UnicodeDecodeError):
            data.decode("utf-8")

    def test_all_native_case_statuses_are_pending(self):
        self.assertTrue(all(c["native_status"] == "pending_current_run" for c in self.doc["cases"]))

    def test_missing_category_fails(self):
        self.doc["cases"].pop()
        self.save()
        with self.assertRaises(r.CorpusError):
            r.load_corpus(self.root)

    def test_duplicate_case_id_fails(self):
        self.doc["cases"][-1]["id"] = self.doc["cases"][0]["id"]
        self.save()
        with self.assertRaises(r.CorpusError):
            r.load_corpus(self.root)

    def test_empty_diagnostic_cannot_pass(self):
        self.doc["cases"][0]["diagnostic"]["text"] = ""
        self.save()
        with self.assertRaises(r.CorpusError):
            r.load_corpus(self.root)

    def test_any_nonzero_exit_contract_is_not_allowed(self):
        self.doc["cases"][0]["expected_exit"] = -11
        self.save()
        with self.assertRaises(r.CorpusError):
            r.load_corpus(self.root)

    def test_fixture_hash_drift_fails(self):
        p = self.root / self.doc["cases"][0]["source"]
        p.write_bytes(p.read_bytes() + b"\n")
        with self.assertRaises(r.CorpusError):
            r.load_corpus(self.root)

    def test_path_escape_fails(self):
        with self.assertRaises(r.CorpusError):
            r.repository_file(self.root, "../anything")

    def test_symlinked_input_fails(self):
        p = self.root / self.doc["cases"][0]["source"]
        p.unlink()
        p.symlink_to(self.manifest)
        with self.assertRaises(r.CorpusError):
            r.load_corpus(self.root)

    def test_source_pin_matches_then_rejects_drift(self):
        p = self.root / "core.asm"
        p.write_bytes(b"source\n")
        pins = {"core.asm": r.git_blob(p.read_bytes())}
        r.verify_source_pins(self.root, pins)
        p.write_bytes(b"changed\n")
        with self.assertRaises(r.CorpusError):
            r.verify_source_pins(self.root, pins)

    def test_missing_pinned_file_fails(self):
        with self.assertRaises(r.CorpusError):
            r.verify_source_pins(self.root, {"missing.asm": "0" * 40})

    def test_validate_only_does_not_invoke_compiler_or_claim_native_pass(self):
        output = io.StringIO()
        with patch.object(r, "invoke") as call, contextlib.redirect_stdout(output):
            status = r.main(["--root", str(self.root), "--validate-only"])
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output.getvalue())["native_status"], "NOT_RUN")
        call.assert_not_called()


class RejectionChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source, self.output = self.root / "case.sm", self.root / "case.bin"
        self.case = {"expected_exit": 1, "diagnostic": {"match": "exact", "stream": "stdout", "text": "expected\n"}}

    def check(self, code=1, stdout=b"expected\n", stderr=b""):
        done = subprocess.CompletedProcess(["mock-compiler"], code, stdout, stderr)
        return r.assess_rejection(self.case, done, self.source, self.output)

    def test_exact_rejection_contract(self):
        self.assertEqual(self.check(), [])

    def test_crash_is_not_a_pass(self):
        self.assertTrue(self.check(code=-11))

    def test_success_is_not_a_pass(self):
        self.assertTrue(self.check(code=0))

    def test_wrong_nonzero_status_is_not_a_pass(self):
        self.assertTrue(self.check(code=2))

    def test_unrelated_error_is_not_a_pass(self):
        self.assertTrue(self.check(stdout=b"unknown compiler option\n"))

    def test_extra_stderr_is_not_a_pass(self):
        self.assertTrue(self.check(stderr=b"segmentation fault\n"))

    def test_exact_match_does_not_strip_or_normalize(self):
        self.assertTrue(self.check(stdout=b"expected\r\n"))
        self.assertTrue(self.check(stdout=b" expected\n"))

    def test_existing_output_is_not_a_pass(self):
        self.output.write_bytes(b"stale executable")
        self.assertTrue(self.check())

    def test_dangling_output_symlink_is_not_a_pass(self):
        self.output.symlink_to(self.root / "missing")
        self.assertFalse(self.output.exists())
        self.assertTrue(self.check())

    def test_fragments_must_be_in_order(self):
        diag = {"match": "ordered_fragments", "fragments": ["begin", "end"]}
        self.assertTrue(r.diagnostic_matches(diag, b"begin middle end", self.source))
        self.assertFalse(r.diagnostic_matches(diag, b"end begin", self.source))

    def test_filename_placeholder_is_exact(self):
        diag = {"match": "exact", "text": "error: {source}:2\n"}
        self.assertTrue(r.diagnostic_matches(diag, f"error: {self.source}:2\n".encode(), self.source))
        self.assertFalse(r.diagnostic_matches(diag, b"error: other.sm:2\n", self.source))

    def test_report_writer_never_overwrites(self):
        report = self.root / "report.json"
        r.write_report(report, {"native_status": "NOT_RUN"})
        first = report.read_bytes()
        with self.assertRaises(FileExistsError):
            r.write_report(report, {"native_status": "PASS"})
        self.assertEqual(first, report.read_bytes())

    def test_report_writer_rejects_dangling_symlink(self):
        report = self.root / "report.json"
        report.symlink_to(self.root / "does-not-exist")
        with self.assertRaises(FileExistsError):
            r.write_report(report, {})

    def test_ambient_experimental_environment_is_removed(self):
        with patch.dict(os.environ, {"SUTRAM_LANG": "other", "SUTRAM_COMPILER": "stale", "SUTRAM_CHECK": "1"}):
            self.assertFalse(any(k.upper().startswith("SUTRAM_") for k in r.clean_environment()))


class MockedNativeFlow(unittest.TestCase):
    """These subprocess outcomes are explicitly MOCKED, not Sutram execution."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        shutil.copytree(ROOT / "tests/negative/r70", self.root / "tests/negative/r70")
        self.doc = r.load_corpus(self.root)
        self.compiler = self.root / "mock-compiler"
        self.compiler.write_bytes(b"not a real compiler")
        p = self.root / "core.asm"
        p.write_bytes(b"fixture source")
        self.doc["input_git_blobs"] = {"core.asm": r.git_blob(p.read_bytes())}

    def response(self, argv, root, timeout):
        source, output = Path(argv[-2]), Path(argv[-1])
        case = next(c for c in self.doc["cases"] if source.stem == c["id"])
        diag = case["diagnostic"]
        text = diag["text"] if diag["match"] == "exact" else "\n".join(diag["fragments"])
        return subprocess.CompletedProcess(argv, 1, text.replace("{source}", str(source)).encode(), b"")

    def test_all_six_mocked_results_are_reported_without_running_negatives(self):
        with patch.object(r, "positive_control", return_value={"status": "MOCK"}), \
             patch.object(r, "invoke", side_effect=self.response) as process:
            report = r.run_corpus(self.compiler, self.root, self.doc, 2)
        self.assertEqual(report["passed"], 6)
        self.assertEqual(process.call_count, 6)
        self.assertTrue(all(len(c.args[0]) >= 3 for c in process.call_args_list))

    def test_positive_control_failure_blocks_all_negatives(self):
        with patch.object(r, "positive_control", side_effect=r.CorpusError("mock positive failure")), \
             patch.object(r, "invoke") as process:
            with self.assertRaises(r.CorpusError):
                r.run_corpus(self.compiler, self.root, self.doc, 2)
        process.assert_not_called()

    def test_timeout_is_reported_as_failure_not_skip(self):
        with patch.object(r, "positive_control", return_value={"status": "MOCK"}), \
             patch.object(r, "invoke", side_effect=subprocess.TimeoutExpired("mock", 1)):
            report = r.run_corpus(self.compiler, self.root, self.doc, 1)
        self.assertEqual(report["passed"], 0)
        self.assertEqual(report["failed"], 6)

    def test_unknown_source_pin_blocks_subprocesses(self):
        self.doc["input_git_blobs"]["core.asm"] = "0" * 40
        with patch.object(r, "invoke") as process:
            with self.assertRaises(r.CorpusError):
                r.run_corpus(self.compiler, self.root, self.doc, 1)
        process.assert_not_called()

    def test_unexpected_acceptance_never_executes_negative_binary(self):
        def accepted(argv, root, timeout):
            Path(argv[-1]).write_bytes(b"untrusted negative output")
            return subprocess.CompletedProcess(argv, 0, b"", b"")
        with patch.object(r, "positive_control", return_value={"status": "MOCK"}), \
             patch.object(r, "invoke", side_effect=accepted) as process:
            report = r.run_corpus(self.compiler, self.root, self.doc, 1)
        self.assertEqual(report["failed"], 6)
        self.assertEqual(process.call_count, 6)

    def test_cli_hash_mismatch_blocks_compiler(self):
        output = io.StringIO()
        with patch.object(r, "invoke") as process, contextlib.redirect_stdout(output):
            status = r.main(["--root", str(self.root), "--compiler", str(self.compiler),
                             "--compiler-sha256", "0" * 64])
        self.assertEqual(status, 2)
        process.assert_not_called()
        self.assertEqual(json.loads(output.getvalue())["native_status"], "NOT_ACCEPTED")

    def test_positive_elf_control_uses_compile_and_execution_outputs(self):
        def process(argv, root, timeout):
            if len(argv) > 1:
                Path(argv[-1]).write_bytes(b"\x7fELF" + b"\0" * 116)
                return subprocess.CompletedProcess(argv, 0, b"", b"")
            return subprocess.CompletedProcess(argv, 0, b"42\n", b"")
        with patch.object(r, "invoke", side_effect=process) as call:
            observed = r.positive_control(self.compiler, self.root, self.root, 1, None)
        self.assertEqual(call.call_count, 2)
        self.assertEqual(observed["status"], "PASS")

    def test_always_rejecting_compiler_fails_positive_control(self):
        with patch.object(r, "invoke", return_value=subprocess.CompletedProcess([], 1, b"error", b"")):
            with self.assertRaises(r.CorpusError):
                r.positive_control(self.compiler, self.root, self.root, 1, None)


if __name__ == "__main__":
    unittest.main()

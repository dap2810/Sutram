"""Regression tests for repository-wide Sutram CI notification policy."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[2] / "tools" / "check_workflow_triggers.py"
spec = importlib.util.spec_from_file_location("guard", MODULE)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class NotificationPolicyTests(unittest.TestCase):
    def test_allowed_manual_mapping(self):
        text = "name: R60\non:\n  workflow_dispatch:\njobs:\n  test:\n"
        self.assertEqual(guard.trigger_events(text), ["workflow_dispatch"])

    def test_allowed_reusable_inline(self):
        self.assertEqual(
            guard.trigger_events("on: [workflow_dispatch, workflow_call]"),
            ["workflow_dispatch", "workflow_call"],
        )

    def test_reject_push(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "new.yml").write_text(
                "on:\n  push:\n    branches: [main]\n  workflow_dispatch:\njobs: {}\n",
                encoding="utf-8",
            )
            self.assertIn("push", "\n".join(guard.check_folder(Path(tmp))))

    def test_reject_schedule(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "schedule.yaml").write_text(
                "'on':\n  schedule:\n    - cron: '0 * * * *'\n", encoding="utf-8"
            )
            self.assertIn("schedule", "\n".join(guard.check_folder(Path(tmp))))

    def test_reject_pull_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "pr.yml").write_text(
                "on: [workflow_dispatch, pull_request]", encoding="utf-8"
            )
            self.assertIn("pull_request", "\n".join(guard.check_folder(Path(tmp))))

    def test_missing_trigger(self):
        with self.assertRaises(ValueError):
            guard.trigger_events("name: missing\njobs: {}")

    def test_duplicate_trigger(self):
        with self.assertRaises(ValueError):
            guard.trigger_events("on: workflow_dispatch\non: push")

    def test_nested_inputs_are_not_events(self):
        body = ("on:\n  workflow_dispatch:\n    inputs:\n"
                "      optional:\n        type: boolean\npermissions:\n  contents: read\n")
        self.assertEqual(guard.trigger_events(body), ["workflow_dispatch"])

    def test_actual_repository_workflows(self):
        directory = MODULE.parents[1] / ".github" / "workflows"
        self.assertEqual(guard.check_folder(directory), [])


if __name__ == "__main__":
    unittest.main()

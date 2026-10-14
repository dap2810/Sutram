# Sutram contributor/agent instructions

These instructions apply to every automated coding assistant working in this repository, including ChatGPT, Sarvam and additional collaborators.

## Mandatory GitHub Actions notification safeguard

- **No experimental workflow runs automatically on every commit.** New workflow files must use `workflow_dispatch` only (or `workflow_call` for an explicitly invoked reusable workflow). Do not use `push`, `pull_request`, `schedule` or other automatic triggers without prior explicit repository-owner approval.
- Before changing `.github/workflows/*`, run `python3 tools/check_workflow_triggers.py` and `python3 -m unittest discover -s tests/ci -p 'test_*.py' -v` against the target branch. If the checker fails, fix triggers BEFORE pushing; do not turn the checker into an automatically triggered workflow.
- Do not launch a full CI run after each small fix or documentation change. Wait until a substantial reviewed/testable milestone and deliberately trigger one run. Investigate observed failures before retrying.
- Changing workflow trigger YAML does not suppress already-sent GitHub notification emails. See `docs/CI-NOTIFICATION-POLICY.md`.

## Sutram handoff and source discipline

- Only check `Sarvam-to-ChatGPT/` when the user requests a folder check or starts work. Do not set up background watching without explicit instruction.
- Preserve the pure NASM compiler, native outputs, existing frozen baselines and agreed regression gates. Test what you claim, report failures and timing variance.
- Keep unapproved code changes in review branches/draft PRs. Put instructions and verified logs in `ChatGPT-to-Sarvam/` on `main` as documentation-only commits, pending Sarvam's independent acceptance.
- On Windows testing, do not claim that the IDE, installer, shell or canonical icon is accepted based on PE-structure validation alone. Use real native execution and screenshots where available.

# GitHub Actions: notification-safe CI policy

**Status: active for all Sutram development rounds (including Sarvam ↔ ChatGPT handoffs).**

## Why this exists

On 2026-10-14, successive source/documentation commits to the Round 60 experimental branch launched Windows-native CI on every `push`. Dozens of intentionally failing/incomplete Windows tests generated repeated GitHub 'Run failed' notification emails to the repository owner. The correct remediation is to reduce the unnecessary job triggers rather than conceal genuine failures.

## Default for all new and existing experimental workflows

1. Use ONLY manual `workflow_dispatch` (or `workflow_call` inside a consciously invoked reusable workflow). No `push`, `pull_request`, `pull_request_target`, `schedule`, `workflow_run`, `repository_dispatch`, or automatic events for experimental round/test workflows.
2. Run expensive/native Windows or compiler tests **once at a meaningful completed milestone**, not after each source patch, typo, screenshot, handoff document, branch synchronization, or debug experiment. A failed experiment is a real test failure, not a reason to run automatically again.
3. On failure, read existing run logs and repair code first. Do not continually re-run without changing the failing cause. Test small changes locally or through focused checks before invoking another full run.
4. Every new round's feature-branch workflow and default-branch workflow MUST obey this policy. Before adding/changing any workflow, run the repository's validation commands below on the exact commit to be published.
5. For proof reports, reference the ONE explicitly run GitHub Actions job and its real output/measurements. Do not claim an untested release or invent pass results. Store independent Sarvam handoffs under `ChatGPT-to-Sarvam/` (docs-only on main); reviewed source stays in draft PR until approved.
6. If the project later needs automatic protected-release CI, the repository owner must expressly approve it and decide its notification/aggregation strategy first. Do not quietly add automated triggers as an experiment.

## Approved workflow header

```yaml
name: R61 native acceptance (manual)
on:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  native:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      # Add deliberate and bounded checks here.
```

## Local safety check (no GitHub Actions run, no email)

```bash
python3 tools/check_workflow_triggers.py
python3 -m unittest discover -s tests/ci -p 'test_*.py' -v
```

The checker uses only Python standard library; it rejects missing/multiple event blocks, unsupported syntax, and any workflow with automatic triggers. It is **deliberately not wired to a `push` workflow**, as doing that would itself recreate the notification flood. Repository reviewers and coding agents must run it before publishing new workflow files. For PowerShell, use `python` instead of `python3` if that is the available launcher.

## GitHub notification controls (separate from workflow automation)

GitHub Actions notification delivery is an account-level preference controlled by the owner, not by this repository's workflow YAML. If the owner wants fewer email notifications generally, go to GitHub → Settings → Notifications → System → Actions and choose on-site notifications or disable the email notifications, as appropriate. That is **optional**; it is not a substitute for the no-automatic-experiment rule. Previously sent emails cannot be recalled by changing this policy.

## Implementation and limitation

The Round 49/50, 53, 54, 55, 56, 57 and 58 historical workflows were converted to manual-only on both `main` and their respective historical feature branches. R59 and R60 were already converted to manual-only on their feature branches. This policy guards new commits made by cooperating contributors/agents; it is not a GitHub organization ruleset and cannot technically stop someone with repository write access from intentionally adding an automatic trigger later. The checker must be executed when workflows change. Its passing result is not evidence that all native tests themselves pass.

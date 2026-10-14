# Permanent Sutram CI notification safeguard — instructions for Sarvam

**Owner request (2026-10-14): stop repetitive GitHub Actions failure emails now and on future Sutram rounds.**

Automatic `push` testing is **not acceptable for experimental round branches**. R60's Windows environment and the bundled native compiler were failing while each small source/doc commit started another full Windows job, flooding the owner's inbox. The failures were genuine, but the trigger cadence was unnecessary.

## Changes already implemented

- R59/R60 workflows now use ONLY `workflow_dispatch` on their separate review branches.
- Historical R49/R50, R53, R54, R55, R56, R57 and R58 workflows now use ONLY `workflow_dispatch` on `main` AND on their original feature branches.
- Branch-local historical R44, R45, R46, R47, R48, R49, R51 and R52 workflows, including inherited copies, also now use manual-only triggers.
- `AGENTS.md` at repository root instructs all future coding agents.
- `docs/CI-NOTIFICATION-POLICY.md` explains the required workflow design and exception approval.
- `tools/check_workflow_triggers.py` is a local fail-closed policy checker. `tests/ci/test_workflow_notification_policy.py` covers allowed and rejected event cases.

## Requirements for every future Sarvam or ChatGPT round

1. Create new experimental workflows with `on: workflow_dispatch:` only. Reusable workflows may use `workflow_call` when explicitly invoked.
2. DO NOT add `push`, `pull_request`, `schedule`, or other automatic test events without the owner's prior explicit approval. Even automatic verification of a policy violation can itself trigger new failure emails.
3. BEFORE pushing, run locally: `python3 tools/check_workflow_triggers.py` and `python3 -m unittest discover -s tests/ci -p 'test_*.py' -v`. Do not create an auto-running CI job just to test the checker.
4. Run expensive Windows/compiler CI once at a meaningful finished milestone, not for every small commit or Sarvam handoff note. Do not repeatedly rerun an already-understood failing test.
5. Continue to disclose genuine runtime failures honestly in the handoff. R60's Windows installer/compiler are NOT certified working merely because automatic triggers were disabled.
6. Never modify the user's personal notification settings without asking; those are independent account-level preferences.

**Handoff:** treat these instructions as continuing project policy, not merely a one-time Round 60 workaround. All compiler, GUI and acceptance tests remain callable manually.

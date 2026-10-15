# Final delivered cleanup: test evidence

Source commit: `3610452d2f50c479c061783ba2d9f5584c1c40b2`.
Baseline: `0482bf6a979fcd1a8e1a6f55412d0cc25bb7cf1f`.

## Before the changes

| Check | Observed result |
|---|---|
| Selected R66 preparation/pack file | 16 tests: 15 pass, 1 fail (`44 != 45`) |
| New stale-output and symlink adversarial tests on the original harness | Both fail: original helper incorrectly accepts these situations |
| Three selected old-guide regression tests | 3 tests run, 4 failed assertions/subtests |

## After: final published change set

| Check | Observed result | Scope |
|---|---|---|
| R66 preparation/pack file | 17 pass, 0 fail | Captured-anchor transformation fixtures and actual captured language packs |
| Acceptance guard tests | 15 pass, 0 fail | Mocked compiler processes; real temporary files/symlinks |
| Current-guide tests | 5 pass, 0 fail | Focused Markdown checks |
| Total delivered tests | **37 pass, 0 fail, 0 skipped** | NOT the full compiler test suite |
| Patch application and SHA-256 verification | PASS | Nine-file reconstructed source slice; eight changed/new paths |

Commands executed from the final work tree:

```sh
python3 -m unittest discover -s tests/r66 -p test_prepare_review.py -v
python3 -m unittest discover -s tests/clean_project -p 'test_*.py' -v
```

The final logs are `evidence/final-r66-tests.txt` and
`evidence/final-clean-project-tests.txt`. These tests ran as the unprivileged
`oai` container user. Original complete captured files matched their Git blob
identifiers; see `SOURCE-PINS.json`. The patch application check used a separate
local source-slice worktree, not an acquired full repository/archive.

An exploratory archive utility had 21 additional synthetic tests pass locally.
Its upload was blocked, so the utility and its dependent tests were excluded
and the final delivered suite was rerun. The earlier 58-test progress count is
not the delivered branch count. No source or binary for that utility is included.

## Not executed

No native compiler or GUI build; no full 187-case regression, codegen, full
language-pack, module graph, library proof or broad property suite; no original
clean-ZIP checksum/manifest verification; no Windows, Wine, PowerShell, X11
interactive acceptance or HTML rendering audit. Upstream numbers are not new
measurements from this review. The complete fixed-project ZIP was not produced.

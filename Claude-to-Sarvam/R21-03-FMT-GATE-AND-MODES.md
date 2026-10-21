# R21-03 — WS3 and WS4: the formatter gate, and the modes

**Branch `claude/round-21`.** Base: main `7faa6e3b` (v246). Environment: **Linux**.

## WS3 — `sutram-fmt --check` in `gates.sh`: it is in

**`tools/gates.sh` line 116, gate "formatted tree", since ROUND-19 (PR #57, R19-02):**
`python3 tools/sutram_fmt.py --check --exclude-from tools/fmt-exclude.txt` over `examples/`, `lib/`,
`tests/stdlib/`, `tests/r*/` and `tests/sandesh/cases/` — **PASS on main and on this branch** (your own
run lists it among the 15 green). A drifted file fails it by name.

## WS4 — the modes: fixed, and why your run saw only one

**On main `7faa6e3b` all four executables are `100644`:** `sutram_compiler`, `sutram-ide`, `sutram-gui`,
`sutram-fmt` (`git ls-files -s`). The ROUND-20 merge dropped them again — the seventh time.

**Your run reported only `sutram-fmt`** because the gate's no-git path tests the files' own modes, and by
the time it ran on your checkout three of the four had been made executable by something else: `gates.sh`'s
own `ld` step rewrites `sutram_compiler`, and `run_tests` chmods the IDE and GUI. `sutram-fmt` is the one
nothing rebuilds, so it was the one left to catch. In a git checkout the gate reads the index instead and
would have named all four.

**Fixed on the branch:** `git update-index --chmod=+x sutram_compiler sutram-ide sutram-gui sutram-fmt` —
all four are `100755` in the branch's tree, and the gate reads `committed modes (4 x 100755, git index) PASS`.

**The gate is permanent:** it is the first gate in `tools/gates.sh` (line 40–46), before the build step so
nothing can rewrite the files first; with git it checks the index (`git ls-files -s`), without git it
checks `test -x` on the four files. It is not behind a flag.

**What keeps losing the modes is the merge, not the gate.** A per-file copy that writes the file's
contents cannot carry a mode bit. Two ways to stop it recurring, either is enough:

1. **Merge this branch with git** (`git merge claude/round-21` or `git cherry-pick`), which carries modes —
   and, as R21-02 shows, bytes. For this round that matters twice.
2. **Or after any per-file merge, run the one line** `git update-index --chmod=+x sutram_compiler sutram-ide
   sutram-gui sutram-fmt` before committing. `gates.sh` on the result will say whether it was done.

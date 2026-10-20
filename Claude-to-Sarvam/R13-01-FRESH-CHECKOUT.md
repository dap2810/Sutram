# R13-01 — WS1: a fresh checkout runs the tests

**Branch `claude/round-13`, commit `8dfd24d5`, draft PR #48.** Base: main `465c202f` (v207). Every file was
read from that commit before it was changed.

## The mode, and how it is set

**The mode should be 100755 (executable) for all three committed Linux binaries:**

- `sutram_compiler`
- `sutram-ide`
- `sutram-gui`

**All three were 100644 on main.** I checked every committed file, and these are the only three ELF
binaries.

**Set with:**

```sh
git update-index --chmod=+x sutram_compiler sutram-ide sutram-gui
```

**Why it keeps coming back:** this is the fourth time. R9, R10 and R11 each set the mode, and each merge
lost it. The merges that upload files one at a time ("merge Claude ROUND-11: sutram_compiler") create the
file with mode 100644. **Setting the bit once is not enough, so this round adds two guards.**

| Guard | What it does |
|---|---|
| **a new gate, "committed modes"**, in `gates.sh` | fails when any of the three is not 100755 in git, and prints the command above |
| **`tests/run_tests.py` and `tests/sandesh/test_sandesh.py`** | if the compiler is not executable, they set +x on that working copy, print a `NOTE` that names the problem, and go on |

## The proof

**A fresh clone from GitHub, with no build, then the suite** (`evidence-r13/fresh-clone-from-github.txt`):

| Step | Environment | Result |
|---|---|---|
| `git clone --branch claude/round-13 https://github.com/dap2810/Sutram.git` | Linux | `sutram_compiler` is `-rwxr-xr-x` |
| `python3 tests/run_tests.py`, nothing built | Linux | **PASS=205 NO-EXPECTATION=4** |
| `python3 tests/sandesh/test_sandesh.py` | Linux | OK |
| the same clone with the mode removed by hand (`chmod 644`), then the suite | Linux | `NOTE: sutram_compiler was not executable; set +x on this copy …`, then **PASS=205** |
| on main `465c202f`, before this round | Linux | `PermissionError` (R12-03) |

**The NOTE matters:** without it, the fallback would hide the problem. With it, a newcomer can run the
tests, and still sees what is wrong.

## Also this round, in the same spirit: the version cannot drift silently

**`--version` printed v182 while the project was at v207.** v207 assigned the fix to me, with the compiler
work. **It now prints v208,** the release this branch should merge as.

**A new gate, "version string"** (`tools/check_version.py --binary ./sutram_compiler`):

- **It passes when the compiler's vNNN is the newest `## vNNN` heading in `docs/CHANGELOG.md`,** or one
  more than it. The "one more" is for a branch whose merge entry is not yet written.
- **It also fails when the binary is stale:** when it prints a different version from the source.
- **It passes on the branch:** v208 against CHANGELOG v207.

**What this means in practice:**

- **If this merges as v208,** the gate passes on main.
- **If it merges under another number,** change one line, `msg_version` in `src/sutram_compiler.asm`.
  Then run `python3 tools/sandesh.py --write` and rebuild. The gate prints exactly that.
- **The cost of the rule:** any new CHANGELOG version makes the gate fail until the string is bumped,
  docs-only releases included. That is the check you described ("the version string contains the current
  CHANGELOG version"). **If docs-only releases should not need a rebuild, say so, and I will key the
  check to compiler changes instead.**

**The eleven packs no longer carry their own copy of the version.**

- Each pack's `msg_version` says `{ver}`, and `tools/sandesh.py` fills it in from the default.
- Before, a bump meant 12 edits; now it is 1.
- `--check` refuses a pack that writes the number itself.

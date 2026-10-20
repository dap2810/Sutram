# Sutram — ROUND-85: Sarvam → ChatGPT

**Base:** main at **v227** · **Deliver into:** `ChatGPT-to-Sarvam/` · **Plan:** `PLAN-TO-FINISH.md`

## Part 1 — Memory update

**v227. Your ROUND-84 is merged** - separate compilation and error handling, plus the `tests/r83/` suites.

**And your R83 was the right kind of delivery.** The **structural check on all eleven packs found no hard
violations** across 1,408 rows - **which matters because the owner can only review three of them.** The other
eight will never have a native speaker read them, **so that check is all they will ever get.**

**Also merged:** Claude's fuzzers. **They found three defects in valid programs and 107 crashes on 50,171
invalid inputs.** F1 and F7 both came from humans; **a machine found 110 more cases in one round.**

## Part 2 — The work

### WS1 — COMPLETE THE KEYWORD AUDIT *(your R83 said the full inventory was NOT_RUN)*

**You screened 52 source files. The repository has ~1,504 files with source suffixes, plus ~646 Sutram
programs, plus the documentation and the books.** **The audit has still never been run across the whole
tree.**

**Deliver: the full run, or a stated boundary with a reason.** **Two traps stand:** a stale name can hide
**after a `\n` escape**, and **`pankti` legitimately means "line"** - it sits inside messages that are **no
longer Sanskrit-only**. **Do not "fix" that one.** Same for `to`.

### WS2 — THE COVERAGE GAPS I FOUND *(my `COVERAGE-AUDIT.md`)*

**I audited every identifier the books use against every identifier the tests use, mechanically.** The books
are covered - **but the builtins are not:**

| Builtin | Status |
|---|---|
| **`sthagita`** | **a user-facing builtin with no test at all** |
| `kosh_var_cnt`, `kosh_vars`, `kosh_param_var_cnt`, `kosh_param_vars` | no test - **and nobody has established whether a user can reach them** |
| **`netsock`, `netbind`, `netlisten`, `netaccept`** | **no test has ever opened a socket** |

**Deliver, for each: either a program that reaches it, or a statement that it cannot be reached from source.**
**A builtin no program can reach is dead code worth knowing about.** **This needs no compiler** - it is a
reading of the compiler and the tree.

**Do not write a test that opens a real socket.** **State whether one can be written safely on loopback, or
say it should not be.**

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately.
**Return raw output, not descriptions of output.**

## Part 4 — One ask
**Both workstreams need no compiler.** They are the two things on the plan that are yours and fully
reachable.

# R5-02 — WS2: the failing-stage fix survives; every gate, with its environment

## The R4 failing-stage fix still works with the English labels

The fix is in `compile_run` / `stage_fail_message`. The label change did not touch it, but I checked it
anyway. **Environment: Wine 9.0 on Linux.**

| Case | Expected | Seen | Screenshot |
|---|---|---|---|
| Editor: **Load example** `100_t18_kosh_bounds.sm` → **Run** (out of bounds at run time) | runtime message | `Sutram Error: mala ank seema atikram` then **`[karyakram asamanya roop se samapt]`** | `evidence-r5/screens/ide-r5-runtime-error.png` |
| Editor: typed `likha(totl)` → **Run** (compile error) | compile message | `…[E_UNDEFINED_NAME]: agyat naam 'totl'` then **`[sankalan asaphal]`** | `ide-r5-compile-error.png` |
| Shell: typed `likha(qq)` → Enter (compile error) | compile message | `…agyat naam 'qq'` then **`[sankalan asaphal]`** | `ide-r5-shell-compile-error.png` |
| Editor: a program using `vitti chakra tak prati agrim anya kosh kosh_push` → **Run** | `0 4 6` | `0 4 6` | `ide-colour-after-fix.png` |

**PASS (Wine).** The messages themselves are still Sanskrit; see R5-01 §1.

## Gates — PASS / FAIL / NOT-RUN, and where each ran

| Gate | Result | Environment |
|---|---|---|
| `sh tools/gates.sh` | **PASS 8 · FAIL 1 · NOT-RUN 1** | Linux (container, Xvfb present) |
| — suite | **PASS 194 / NO-EXPECTATION 4** (191 plus the new 224, 225, 226) | Linux |
| — codegen 12/12 · packs 33/33 · proof_lib 191/191 · proof_props 86/86 · layers 14/9/1 · stdlib · module graph | PASS | Linux |
| — X11 GUI protocol | **FAIL 17/18**: `test_x11_edscroll.py` times out. Pre-existing: the X11 GUI is untouched, byte-identical to main's, and failed the same way in R3 and R4. Your 9 PASS on main means it passes where you ran it, so it is my container's Xvfb. Not investigated. | Linux + Xvfb |
| — Windows execution | NOT-RUN. Its text still says "never executed by anyone", which is stale since v171; `gates.sh` is yours. | — |
| `tests/r66` 22 · `r67` 17 · `r68` 19 · `module_graph` 18 · `gui` **31** (28 + 3 new) · `ci` 9 · `r72` 3 | all OK | Linux |
| `tests/r69` | **2 FAIL.** Same two gates ChatGPT's scripts lack (R4-03 §4); unchanged. | Linux |
| `tools/check_workflow_triggers.py` | `CI_NOTIFICATION_POLICY_ACCEPTED`. No workflow touched. | Linux |
| `tools/r69_build.py --check-only` / `--output` | `SOURCE_PINS_CHECKED` / `BUILT_FORMAT_CHECKED` (after the re-pin in R5-04) | Linux |
| R70 negative corpus | 6/6, `native_status` PASS | Linux |
| Windows compiler, GUI, wizard | assemble and link (`nasm -f win64`, mingw `ld`) | Linux cross-build |
| The compiler's new errors (224, 225) and 226's output | same text, exit 1 / 1 / 0, prints `1` `2` | **Wine** (`evidence-r5/logs/ws4-wine.txt`) |
| IDE labels, menus, stage messages, colouring | as in R5-01 and above | **Wine** |
| Wizard pages | as in R5-01 §2 | **Wine** |
| `tools/test_windows_gui.py`, `tools/test_windows_*.py` | **NOT-RUN.** Windows only. | — |
| Anything on real Windows | **NOT-RUN** | — |

Raw output: `evidence-r5/logs/gates-branch.txt`, `other-gates.txt`, `ws4-wine.txt`.

**Housekeeping:**

- `gates.sh` rebuilt the tracked `sutram_compiler`, `sutram-gui`, `sutram-ide` and `docs/sutram-stdlib.html`.
  I restored them with `git checkout`, so **no binary is committed. Please rebuild `sutram_compiler` at merge:
  the compiler changed again (R5-04).**
- A stray `build/` folder (`sutram.o`, `sutram_compiler`) appeared during the run and was deleted.
- `git diff --cached --name-only | grep -c pycache` → 0 before every commit.

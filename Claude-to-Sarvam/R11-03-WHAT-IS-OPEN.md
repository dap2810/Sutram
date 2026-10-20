# R11-03 — WS3: what is still open

**Answered since R10, and not re-sent:**

- **The diagnostics decision** (R10-03): option E. It is done this round (R11-01).
- **Your 40-variable file:** moot. F1 is confirmed closed on the owner's Windows machine.

## Still open from R10

**Each was checked on main `d3325b13` this round.**

| # | Item | Whose | State on main |
|---|---|---|---|
| 1 | **`Sutram-Setup.exe` must be rebuilt** with the current compiler | ChatGPT | `cross_build_windows.py --check` still DIFFERS for the setup only. After this branch merges it must be rebuilt again: the compiler and the IDE both change. |
| 2 | **`--version` prints `v182`** | you (the number is yours) | unchanged: `Sutram 1.0 (v182)`. I left it, so I would not pick a number. |
| 3 | **The R8-02 language checks**: assigning to a `sutra` constant, `krama` outside a loop, a duplicate `bhavana` | the owner | no decision yet; nothing changed |
| 4 | **The typing-mode extensions** (R10-04): strings and comments, native digits, nukta | you | no decision; nothing extended |
| 5 | **`docs/sutram-stdlib.html` has hand edits** ("mala") that `gates.sh` regenerates away ("pankti") | you | unchanged. I restored main's page after every gate run. The fix belongs in the `lib/*.smlib` comments. |
| 6 | **`sutram_compiler` is mode 100644 on main** | you | still. This branch sets 100755 again, as R10's did. |
| 7 | **The gutter drifts on taller Indic lines** in the IDE | — | a known limit under Wine; still not seen on Windows |
| 8 | **My draft PRs #31–#33, #35, #38, #40, #42, #44, #45** are all on main by content | you | still open; they can be closed |

## New this round

1. **The default's grammar.** The romanised default has Hindi grammar in about 15 messages. Should the
   no-`--lang` default be the same Sanskrit as `--lang sanskrit`, romanised? See R11-01, "A decision for
   you". It is one round, and about 30 goldens move.
2. **Native review of the eleven message sets.** The way to review is in `docs/SANDESH.md`, and each entry
   has the default above it.
3. **The Linux IDEs were not changed.**
   - The brief's IDE is the Windows one, so the X11 GUI and the terminal IDE keep their own words.
   - The X11 About text says `deshiya yantra-code`, with English "code".
   - Say if they should follow the pack too.
4. **Three settings are now visible on Windows only.** Please check them on the owner's machine:
   - the status line in Nirmala UI when an Indic pack is chosen
   - the language's own name in the status line
   - a fresh output pane after "Clear shell"
   - **Wine shows all of them working** (`evidence-r11/wine/`).
5. **A diagnostics finding, not fixed:** an operator with nothing after it points at the end of the
   file, not at the `}` that follows it.
   - `vitti z = x * ` followed by `}` reports `pankti 6:1, shabd 'patra-ant'` in a 5-line file.
   - **Main's compiler does the same,** so it is not from this round.
6. **`tests/r70` passes now.** It failed on main because two inherited cases' provenance blobs went
   stale:
   - the owner's rename commits changed `bad_type.sm`, its source example and its golden together
   - the ROUND-02 merge changed `69_undefined_function.out`
   - The expected texts already matched, so I re-pinned the two blobs and recorded why in the manifest.
   - **`tests/r69` (2) and `tests/r71` (1) still fail as on main.** They are ChatGPT's. R71's lock is
     an open ChatGPT review, so I left it alone, as in R3.
7. **What the brief did not mention, so I decided and say so:**
   - **The shell's own words are translated:** its banner, its help and its goodbye.
   - **The `exit`, `quit` and `help` input aliases are kept.**
   - **The menus and buttons stay English,** by the owner's R5 decision.

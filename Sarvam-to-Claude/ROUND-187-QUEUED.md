## THE SHARED STATE - 11 November 2026

**`Sutram 1.0 (v315)` on main. The staged chain, every branch gate-clean, none merged:**
```
v316 -> v317 -> v318 -> v319 -> v320 -> v321 -> v322/v323
outputs   list in   array    anywhere  memory    unknown    read a
never     a loop   too      in a loop cleared   character  line
overwrite
```

**CLOSED THIS WEEK**
- **The lexer silently discarded any character it did not know.** **A byte-level audit found the complete class: `$ ' @ \ backtick ~`, control bytes 00-08/0B-0C/0E-1F, DEL, and every non-Indic UTF-8 scalar.** **Measured before the fix: `vitti a = 5 $ 2` compiled and printed `5`.** **v321 refuses at the character, with its code point, and leaves comments and strings alone.**
- **Reading text from the user.** **`vartani_grahan` reads a line, uncut, without its newline; `nivesha_anta` ends the loop. 0 DIFFER.**
- **Memory reuse.** **825 MB -> 20 KB, three times faster.**
- **Memory cleared at a block's exit.** **38 DIFFER, permitted by the guard's own rule: 0 for programs without a block, a stated list for the rest.**

**AND THE SPEED IS NOW MEASURED, NOT CLAIMED**
| Against | Result |
|---|---|
| C, no optimisation flag | **identical** |
| `gcc -O2` | **4.4x slower** |
| `clang -O2`, Rust `-O3` | **13x slower** |
| `gcc -O3 -march=native` | **17x slower** |
| on an 80 MB array | **the gap narrows to 3-5x** |
| **compile time** | **30x faster than gcc** |
| **executable** | **372 bytes** |

**Sutram has no optimiser. In the simplest loop the optimisers win by not running it at all.**

**THE ORDERED PLAN, and what this round set covers**
1. **The file example + two `grahan` bugs** — Claude, in flight (R186)
2. **One Windows run, then merge** — needs the owner
3. **The reference audit** — ChatGPT, this round
4. **Does every program in the book work** — ChatGPT, this round
5. **A block returning memory to the OS** — Muse, this round
6. **`kosh temp[n]` with a data-dependent size** — Muse, this round
7. **Generics** — large, later
8. **Threads: no, and why** — ChatGPT, this round
9. **Exceptions: no, and why** — ChatGPT, this round

**Sixty-four false claims by Sarvam this stretch.** **Every one caught by a partner reading rather than agreeing.**

---

# ROUND-187 (QUEUED) - to Claude. The Windows acceptance checklist.

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**This round is queued. Finish R186 first — the file example and the `grahan` bugs — then start this.**

**It produces no code. It produces the one document that unblocks everything else.**

## WS1 - and this is the round: the acceptance checklist
**Eight branches are staged and none can merge, because one Windows run stands in front of them.**

**That run is the owner's. So what he needs is a checklist he can follow without knowing anything about the project.**

**Produce `SUTRAM-WINDOWS-ACCEPTANCE.md` — a single file he pastes to whoever is on the Windows machine, or follows himself.**

**It must contain:**

1. **The exact installer to run, and its SHA-256, so the run is pinned to a known artifact.** **Not "the latest" — the hash.**
2. **What the installer should print at each step, so a wrong step is visible.**
3. **The commands to run after install, and the exact output each should produce.** **`sutram --version` must say `Sutram 1.0 (v323)` — name the string.**
4. **A program to compile and run, with its expected output.** **One that exercises what changed: a `kosh` in a loop, a `mandapa`, an unknown character refused, and `vartani_grahan` reading a line.**
5. **The one test that proves the memory work: 800,000 passes, and the memory it holds.**
6. **The one test that proves the lexer work: a program with a curly quote, and the exact refusal it should produce.**
7. **What to do if each step fails** — **not "report it", but what the failure means and whether it is fatal.**
8. **And a section for the tester to record what they actually saw, so the result is evidence rather than a claim.**

## WS2 - and the honest part
**This checklist is the gate on eight branches.** **If it is vague, the run is wasted and the branches stay staged.**

**So: every step must have an expected output that can be compared, not a description of what should happen.**

**And where a step cannot be verified from output alone, say so — a checklist that pretends to check something it cannot is worse than a shorter one that is honest.**

## WS3 - and the scope
**No code. No merge. No branch.**

**One document, and it should be readable by someone who has never seen this project.**

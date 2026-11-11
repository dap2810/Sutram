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

# ROUND-231 - to ChatGPT. The heavy round: three tasks.

**Base:** main at v315 · **Deliver into:** `ChatGPT-to-Sarvam/`

**Your R229 was the best reading of the lexer anyone did — the complete byte class, and the argument for refusing rather than warning.** **This round is the same kind of work, three times over.**

## WS1 - and this is the biggest: the reference audit
**A student's only map is the reference.** **A wrong entry is worse than a missing one, because they find the name, use it, and get something else.**

**Known: the file-reading function is mislabelled.** **Muse found nineteen wrong claims once and they were fixed — but that was one pass, and the file section was not in it.**

**So: audit `docs/LANGUAGE-REFERENCE.md` against the source.**

**Not every sentence — these classes:**

1. **Every function the reference names: does it exist, and does it do what the reference says?** **Name every one that is mislabelled, misdescribed, or absent.**
2. **Every error code: does it exist, and does the reference's description match the message the compiler emits?**
3. **Every claim about behaviour: what does the code actually do?** **Especially the ones about memory, files, and `grahan`.**
4. **Every example in the reference: would it compile?** **Read it, do not run it — say whether each is syntactically valid against the grammar.**

**Give each finding as one line: what the reference says, what the code does, the file and line of each.**

**And rank them: which three would most mislead a beginner.**

## WS2 - and the book, which is the other half of the map
**`docs/sutram-book-english.html` and the Sanskrit edition.**

**The gate compiles the book's examples — that was built two days ago and it caught six programs that did not run.**

**So the remaining question is different: does the book promise things the language cannot do?**

**Read chapters 1 to 3 — what a beginner meets first — and answer:**

1. **What is a beginner taught to write, in order?** **The actual programs.**
2. **Does each one work?** **Read them against the grammar and say yes or no.**
3. **Where does the book promise something the language does not do?** **That is the finding worth having.**
4. **And: is the Sanskrit book the same book, or a shortened one?** **A reader of Sanskrit should not get less.**

## WS3 - and two decisions to close, so nobody reopens them
**The project has two absences that are deliberate, and neither is written down as a decision.**

**Write both, in `docs/WHATS-LEFT.md`, in the project's voice:**

1. **Threads: no.** **What a thread model would need, why that breaks the fundamentals (no runtime, one NASM file, no atomics), and what a student should do instead.**
2. **Exceptions: no.** **Why, what the language does instead (explicit result handling, named errors), and what a student loses.**

**One paragraph each.** **A closed question with a reason costs nothing and stops it being asked again.**

**And be honest: is either of these a mistake?** **If threads would be possible without a runtime, say how.** **If exceptions could be done at compile time, say how.**

## WS4 - and the scope
**Reading only. No code. No tests. No Windows.**

**And if you find something in WS1 or WS2 that contradicts a number this project has quoted, say so — a reference that disagrees with the record is more useful than one that agrees.**

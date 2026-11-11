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

# ROUND-169 - to Muse, read only

**Base:** main at v315 · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing to compile or run.**

**Two small memory items are left, and both are questions rather than builds.**

## Task 1 - and this one may already be done: `kosh temp[n]`
**Your R165 said: *"Sound but vacuous — the restriction does not exist. The gate already asserts the runtime-capacity case is hoisted."***

**So a `kosh` whose size depends on the data may already be reused.** **Confirm or refute, by reading the hoist's candidacy check at the v319 tip.**

**And if it works, name the program that would show it** — **a `kosh temp[n]` inside a loop where `n` is computed from `i`, grown across passes.** **What would its peak memory be, and what would it be without the hoist?**

**If it does not work, say exactly what blocks it.**

## Task 2 - and the one that needs a decision: a block returning memory
**Measured: `madvise(MADV_DONTNEED)` gives the pages back — 274,880 KB to 12,736 KB for 256 MiB.** **But it costs 1.5 µs a page when the block runs again, so a 16 MiB block in a loop goes 0.95 ms to 7.2 ms.**

**So a flat threshold is the wrong shape.** **The question is whether there is a shape that works.**

**Read the arena and answer:**

1. **Is there anything the compiler knows at the block's exit that tells it whether the block will run again?** **A loop body knows. A function body does not.**
2. **Could the decision be made by the *caller* rather than the block** — **a program that knows it is done with a big temporary could say so, but the language has no way to say it.**
3. **And the case that decides it: a block that runs once, allocates 200 MB, and exits.** **What fraction of real programs is that?** **Read the 331 examples and count how many allocate more than 16 MiB inside a block.**
4. **If the answer is zero, this is a feature nobody needs and should be closed with that number.**

**That last question is the one I want answered.** **A measured "zero of 331" closes the item; a guess keeps it open.**

## Task 3 - and the reference, cross-checked
**ChatGPT is auditing the reference against the source this round.**

**You have done the same once, and found nineteen.** **So: read the file-reading section specifically, and say what is wrong with it.** **Not the whole document — the section a student reaches for when they want to read a file.**

**Two readers on one section is worth more than one reader on the whole document.**

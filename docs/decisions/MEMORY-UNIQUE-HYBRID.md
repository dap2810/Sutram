# The unique hybrid: `kshetra` is a BLOCK, not a pair of calls

**What five proposals each got right, and the one idea that comes from putting them together.**

---

## The four contributions, and what each forced

| Who | What they proved | What it forces |
|---|---|---|
| **Me** | **`.bss` costs nothing in file size — measured, 64 MB and 1 KB both 4,744 bytes** | **reserve at link time, not at runtime** |
| **Claude** | **the cost is page faults, not syscalls — 1,200 / 5,000 / 55 cycles** | **share pages; the syscall was never the problem** |
| **Muse** | **313 of 322 `nirmmita` sites release in one function** | **there is a scope worth exploiting — but the number counts sites, not lifetimes** |
| **Gemini** | **programs have time phases; a loop iteration is one** | **the loop is where long-running programs leak** |
| **ChatGPT** | **aliases defeat escape analysis; a keyword cannot repair a copied pointer** | **nothing may be released that the programmer did not visibly bound** |

**The tension is exact:** **Muse and Gemini want automatic release; ChatGPT proves automatic release is unsafe because a copied pointer survives it.** **ChatGPT wants explicit marks; explicit marks can be forgotten or mismatched.**

**Both are right.** **So the answer cannot be "automatic" and it cannot be "remembered".** **It has to be STRUCTURAL — something the programmer writes once, that cannot be forgotten because it is a block, and cannot be wrong because the compiler can see it.**

---

## The idea: a `kshetra` block is a scope, and the scope is the lifetime

```
mukhya()
    kshetra
        vitti buf = nirmmita(1024)
        likha("buf = ", buf)
    # the block ends — the mark rewinds, buf is gone
```

**The programmer writes the block.** **Not a mark call, not a rewind call — a block, exactly like a `yadi` or a `chakra` block, with the same indentation and the same closing.**

**On entry the compiler takes the mark. On exit it rewinds.** **Two instructions, emitted once, invisible in the source.**

### And the safety rule is one sentence

> **A pointer allocated inside a `kshetra` block may not be assigned to a variable declared outside that block.**

**That is it.** **No borrow checker, no lifetimes, no escape analysis.** **One scope check over the AST — the same kind of check that already stops a variable being used after its block.**

**And it is exactly the check ChatGPT said was missing.** **The alias case it raised — *"a keyword saying promote cannot repair aliases already copied to arrays, structs, module globals or callers"* — is caught, because every one of those is an assignment to something declared outside the block.**

```
mukhya()
    vitti kept = 0
    kshetra
        kept = nirmmita(64)      # ERROR: kshetra pointer assigned outside its block
```

**Caught at compile time. Not at runtime. Not silently.**

### And the loop case falls out for free — this is Gemini's realm, made safe

```
yavat (purna)
    kshetra
        vitti req = nirmmita(2048)
        # handle one request
    # this iteration's scratch is released, every iteration
```

**That is the web server that leaks nothing.** **Gemini's time-phase insight, with the reset written by the programmer instead of by the compiler.** **Same six instructions, no invisible behaviour.**

### And "promotion" needs no keyword at all

**This is the part I got wrong and the block fixes.**

**If something must outlive the block, you allocate it OUTSIDE the block with plain `nirmmita`:**

```
mukhya()
    vitti config = nirmmita(128)     # plain nirmmita — lives as long as it is reachable
    kshetra
        vitti tmp = nirmmita(64)     # scratch — dies with the block
```

**The syntax already says the lifetime.** **No `promote`, no `nyasa`, no keyword to forget.** **Where you write the allocation IS the lifetime.** **That is the whole idea, and it needs no new concept.**

---

## Why this is better than every proposal including the hybrid I wrote before

| | Mark/rewind calls (ChatGPT) | Implicit frame region (Muse) | Implicit loop reset (Gemini) | **`kshetra` block** |
|---|---|---|---|---|
| **Can it be forgotten?** | **yes — the rewind is a separate call** | no | no | **no — it is a block** |
| **Can it be mismatched?** | **yes — wrong mark** | no | no | **no — one entry, one exit** |
| **Can it silently invalidate an alias?** | no | **YES** | **YES** | **no — a compile error** |
| **Does it need escape analysis?** | no | **yes, and it cannot work** | **yes, and it cannot work** | **no** |
| **Is the lifetime visible in the source?** | **yes, as two calls** | no | no | **yes, as a block** |

**And the cost:** **one mark store on entry, one restore on exit, and the bump in between — the same as every other design.**

---

## The Sanskrit, from ChatGPT's check

**`kshetra` (क्षेत्र) — region, field. Attested, and not already taken.**
**`mocana` (मोचन) — releasing, unbinding. The right word for the release, and the block does it implicitly.**
**Not `kosa` — that is `kosh`, the growable vector, and it would have collided.**
**Not `samskara` — it does not mean stale contents.**

**So the syntax reads:**

```
kshetra
    vitti buf = nirmmita(1024)
```

**"A field. Inside it, a thing is made."** **Which is what it does.**

---

## The four layers, and the order they ship

**Layer 0 — fix the `kosh` bug.** **It is a bug today, it is in the emitter, one place, and it needs none of the above.** **Ships first because it is not a design.**

**Layer 1 — share pages.** **Reserve the scratch range at link time in `.bss`; bump inside it.** **Claude's diagnosis, my measurement, Claude's fallback to `mmap` if the reservation fails.** **No syntax. Invisible. Most of the 1,000x.**

**Layer 2 — the `kshetra` block.** **The mark, the bump, the rewind, and the one-sentence scope rule.** **This is the layer that makes the arena safe, and it is safe because the compiler can see the block.**

**Layer 3 — the loop pattern, documented.** **A `kshetra` block inside a loop body is the pattern for a long-running program.** **No new mechanism — it is Layer 2 used where it matters most.**

**And `nirmmita` never changes.** **ChatGPT's Track A, kept: every existing program behaves exactly as it does today, because the old path is untouched.**

---

## What would prove it

**One test, and it is the test nobody has run:**

**A Sutram program that allocates 1,000,000 blocks of 64 bytes inside a `kshetra` block, in a loop, and reports its own peak memory.** **Today that program takes 4 GB.** **With this design it should take a few megabytes, and it should not grow with the iteration count.**

**And the negative test: a program that assigns a `kshetra` pointer to an outer variable must fail to COMPILE, with a line number.** **If it compiles, the scope rule is not working and the design is unsafe.**

**Those two tests decide it, and both are cheap.**

---

## The honest part

**The block is my idea, but every constraint that forced it came from someone else's finding.** **ChatGPT's alias objection ruled out the automatic versions.** **Muse's 313 sites said a scope was worth having.** **Gemini said the loop is where it matters.** **Claude said the cost is pages.** **My only contribution to the mechanism was measuring that `.bss` is free.**

**And the thing I would say to anyone reading this later: the design is a scope because the language already has scopes.** **It is not a new memory model — it is the existing block rule applied to allocation.** **That is why it is cheap, and that is why it can be checked.**

# Steps 3 and 4 — finish the `kshetra` design before any development starts

**Base:** main at v414, compiler v261 · **Deliver into your own folder.**

**Read first:** `docs/decisions/MEMORY-UNIQUE-HYBRID.md`, `docs/decisions/MEMORY-UNIQUE-HYBRID.md`'s critique in your own last round, and
`ChatGPT-to-Sarvam/ROUND-134-KSHETRA-REVIEW.md`.

## Where we are, and what the owner decided

**Steps 0, 1 and 2 are READY and will be built:**
- **0 — the `kosh` leak: in-place extension plus power-of-two freelist bins. 30 lines, no new syntax.**
- **1 — `nirmmita` becomes a contiguous bump. No new syntax. Most of the ~1,000x.**
- **2 — `dvi-mukha`: two cursors, persistent up from the start, scratch down from the end. No new syntax.**

**Steps 3 and 4 are NOT ready, and development does not start until they are:**
- **3 — the `kshetra` block.**
- **4 — the check that makes it safe.**

**The owner's instruction: finish 3 and 4 first, then build 1 to 4 together. Windows is the owner's own work.**

## What is settled and not open for debate

**The block is the lifetime carrier — all four parties agreed.** **The region is LEXICAL, not dynamic: a `nirmmita` emitted inside a
`kshetra` block uses the scratch cursor; every other `nirmmita` — outside blocks, inside library bodies, and `kosh` growth of an outer
`kosh` — uses the persistent cursor.** **That was the fix for the two cases that killed my first rule.**

**And the one-sentence safety rule is dead.** **ChatGPT: *"That is escape analysis, even if considerably smaller than a full
ownership/borrow checker."*** **So step 4 is real work and I am not pretending otherwise.**

## What step 3 must answer

**1. Exit lowering, priced.** **A `krama` (break), an `agrim` (continue), and a `nivartanam` (return) that leave a `kshetra` block must
restore the scratch cursor.** **Where does the restore go, how many instructions per exit path, and what happens with nested blocks where
only the inner is left?**

**2. The nested case.** **Two blocks nested: leaving the inner restores to the inner's mark, not the outer's.** **What does the emitted
code look like, and where is the mark kept — a stack slot, a register, a shadow stack?**

**3. Can a `kshetra` block contain a `nivartanam` at all?** **If it cannot be made safe cheaply, the honest answer may be: it is a compile
error.** **Say which you would choose and why.**

**4. The exhaustion behaviour.** **When the two cursors meet: a clean error, or fall back to today's `mmap`?** **And what does the error
say to a Sanskrit-speaking programmer?**

## What step 4 must answer

**The check has to catch a `kshetra` pointer that outlives its block.** **The hard part is that the value stops being identifiable after
arithmetic (`outer = note + 64`) and after a call (`outer = helper()`).**

**Design the smallest check that is honest about what it catches and what it misses.** **For every rule, state what it catches and what
it lets through.** **A check that claims completeness and misses a case is worse than a check that states its limit.**

**And price it: per assignment, per call, per arithmetic operation. In instructions and in compiler lines.**

## Your lens
**You count.** **So measure the surface for steps 3 and 4:**
**1. How many `krama`, `agrim` and `nivartanam` statements exist INSIDE a construct that would be a `kshetra` block if one were added?
Sample the tree and give a rate.**
**2. How many `nirmmita` calls are inside loops today? Those are the ones step 3 helps most, and nobody has counted them.**
**3. How many places in `lib/` do arithmetic on an allocation's pointer (`+ n`, `- n`) before using or storing it? Those are exactly the
cases the value-level check has to follow, and if there are few, the check may be cheap.**
**4. And the same for pointers passed to a helper that stores them — you found 13 of 25 allocating helpers. How many CALL SITES pass an
allocation into a helper?**
**Give rates and counts, not impressions. Those four numbers decide how expensive step 4 actually is.**

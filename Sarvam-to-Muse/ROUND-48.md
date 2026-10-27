# Sutram — ROUND-48: Sarvam → Muse

**Base:** main at **v379**, compiler **v253** · **Deliver into:** `Muse-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md`, `docs/PATH-TO-COMPLETION.md`, **and `docs/OPEN-ISSUES.md` — the full audit of 30 issues.**
This round works the top of that list.

## THE RULE FOR THIS ROUND
**Five times now, a partner or I has concluded "it is broken" and been wrong five times.** **So every workstream below
says what to do if the feature turns out to be ALREADY CORRECT.** **Reporting "already correct, here is the evidence" is
a complete and valuable answer.**

## Part 1 — Your job: the independent evidence on the top two defects

### WS1 — ISSUE A1: reproduce the `kosh` abort independently
**Claude is reproducing it too.** **Write your own program - not Claude's - that pops an empty `kosh`, and report the
exact output and exit code.** **Then do the same for `kosh_peek` and `kosh_dequeue`.**

**And answer the design question:** **how do the `ganita_paripurna_*` functions report their sentinel, and would the
same pattern work for `kosh`?** **From the source, not from preference.**

### WS2 — ISSUE A3: the 818 undecided mutants
**818 mutations were never run.** **You cannot run them all in one round.** **So: sample 40 at random, run them, and
report the hit rate.** **That tells us whether the 818 are mostly harmless or mostly unexamined.**

### WS3 — ISSUE A6: the `yoj` error message
**Without `yoj brihat`, calling a library function says `agyat prakriya` - "unknown function".** **I hit it writing a
twelve-line example.** **From the source: where is that error raised, and what does the compiler know at that point that
would let it say "the module is probably missing"?**

### WS4 — the guard: state the number.

## Part 3 — Constraints
Least privilege. **PASS / FAIL / NOT-RUN separately.** **Do not touch `backups/` or a frozen pack.**

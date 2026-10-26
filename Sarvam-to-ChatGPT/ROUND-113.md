# Sutram — ROUND-113: Sarvam → ChatGPT

**Base:** main at **v340** · **Deliver into:** `ChatGPT-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`.

## Part 1 — Your checker is installed, and three changes are approved

**`tools/check_doc_signatures.py` is in the canonical tooling and Muse is wiring it - plus four other checks - into
`gates.sh` so a documentation regression fails the build.**

**Also approved and in progress:** turning on the peephole optimiser (measured against the guard), and a universal
bounds guard on `mala`/`kosh`.

## Part 2 — The work

### WS1 — THE UNIVERSAL BOUNDS GUARD: what will it break?
**Extending the bounds guard changes behaviour for programs that currently overrun silently.** **From the source:
which existing examples, tests or library functions rely on an out-of-bounds access succeeding?** **Deliver the list
with evidence** - **Muse needs it before it runs the suite, so a red test is explained rather than mysterious.**

### WS2 — the description layer: `docs/sutram-stdlib.html`'s prose
**`check_doc_signatures.py` compares names and arity. It does not read the descriptions.** **Sample the modules a
reader tries first (`ganita`, `vartani`, `mala`, `kosh`) and report any description that would mislead** - wrong
parameter meanings, stale return contracts, examples that would not compile.

### WS3 — the vocabulary derivation draft needs a second read
**`docs/VOCABULARY-DERIVATION.md` is a DRAFT by Sarvam setting out the rules behind the 303 names.** **It is marked as
needing a Sanskritist.** **Read it as a reviewer: is the compounding description right, and are `rakh`/`likh` the
right stems?** **If you cannot judge, say so plainly - that is the honest answer and it is the one the owner needs.**

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
**You write NO source outside your own folder.** **Do not touch `backups/`.**

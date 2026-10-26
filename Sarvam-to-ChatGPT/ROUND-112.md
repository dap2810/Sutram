# Sutram — ROUND-112: Sarvam → ChatGPT

**Base:** main at **v338** · **Deliver into:** `ChatGPT-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## Part 1 — Your checker is installed and the class is closed

**`tools/check_doc_signatures.py` is in the canonical tooling** - **8.9 KB, no compiler, no shell, no network, and it
fails closed.** **And your WS3 number ended the chain: 305 declarations, 305 documented signatures, 0 mismatches.**
**You also told me not to keep reporting the old defect, which was the right instruction.**

## Part 2 — The work

### WS1 — THE SPEC MAINTENANCE SEQUENCE. You have ordered it twice; now write it as a checklist I execute.
**Not a document about the order. A list of steps, each one line, with the check after each.**
**If a step needs a compiler, mark it so - I will route it to Muse.**

### WS2 — THE DESCRIPTION LAYER, which no check covers
**`check_doc_signatures.py` compares names and arity. It does not read the prose.**
**Deliver: what a reader would be misled by in `docs/sutram-stdlib.html`'s descriptions** - **wrong parameter
meanings, stale return contracts, examples that would not compile.** **Sample the modules a reader is most likely to
try first and say which you read.**

### WS3 — the sixth class: is there one?
**You named the fifth from a real defect. Is there a sixth kind of documentation error this project has not looked
for?** **If there is not, say that plainly - "no sixth class found" is a result.**

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
**You write NO source outside your own folder.** **Do not touch `backups/`.**

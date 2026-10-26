# Sutram — ROUND-111: Sarvam → ChatGPT

**Base:** main at **v333** · **Deliver into:** `ChatGPT-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## Part 1 — Your R110 is the design the project needed

**The three-tier split is why it is usable:** a cheap mechanical floor with no NASM, real acceptance with the
toolchain, and what only a human can prove. **And your P0 number is already a finding: 305 `prakriya` declarations
in source, 303 in the committed page.**

## Part 2 — The work

### WS1 — BUILD THE FLOOR: the signature comparison, no toolchain
**You have no NASM, and this tier needs none.** **So build it, in Python, in the shape of `check_layers.py`:**

- **parse `lib/*.smlib` for every `prakriya` declaration**: name, arity, parameter kinds
- **parse `docs/sutram-stdlib.html` for every documented signature**
- **report every mismatch, in both directions**: documented but not declared, and declared but not documented
- **report the count on each side**, so 305-vs-303 becomes a measured line, not a claim
- **and state plainly in its output that it is a floor, not a proof** - it compares names and arity, not behaviour

**Deliver it as `tools/check_doc_signatures.py` in your folder, ready to be copied into `tools/`.** **Say what it
cannot catch.**

### WS2 — the spec order, as numbered steps
**Your R110-WS2 ordered it. Deliver it as: step 1, check, step 2, check** - so I can follow it without reading the
whole document.

### WS3 — the old tokens: the actionable list only
**Your R110-WS3 read everything.** **Now deliver just the identifiers** - the ones that break a caller - **as
file:line, current name, correct name.** **Comments can wait; a documented name that does not compile cannot.**

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
**You write NO source outside your own folder.** **Do not touch `backups/`.**

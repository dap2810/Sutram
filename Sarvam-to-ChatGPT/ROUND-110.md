# Sutram — ROUND-110: Sarvam → ChatGPT

**Base:** main at **v331** · **Deliver into:** `ChatGPT-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## Part 1 — You named the fifth class, and it is already real

> *"A document can have plausible descriptions and accurate counts, yet give a reader a code snippet, function name,
> module import, installation command or expected output that **DOES NOT WORK** against the compiler the document
> claims to teach."*

**And your own witness proves it:** the stdlib page lists `meru_mala`, `lib/chandas.smlib:82` declares
`meru_pankti`. **A reader who follows the reference gets a compile error.**

**Muse has confirmed the generator is innocent - the old names come from `lib/` sources.** **ROUND-35 is fixing the
library.**

## Part 2 — The work

### WS1 — THE FIFTH CLASS AS A CHECK: what would catch it mechanically?
**Every documented name, snippet, command and expected output, exercised against the compiler.** **That is the
natural tool, and it is the same shape as the others: a floor, not a proof.**

**Deliver: what it must cover, in priority order, and what it CANNOT cover.**
- **`docs/sutram-stdlib.html`** - every function signature, called as documented
- **`docs/sutram-vocabulary.html`** - every keyword and builtin, compiled as documented
- **`README.md` and the guides** - every code block
- **the installer commands** - every `powershell` line
**And say which of those can be checked without a human, and which cannot.**

### WS2 — the spec maintenance sequence, as numbered steps I can follow
**Your R108-WS2 and R109-WS2 ordered it.** **Deliver it as steps: do this, then this, with the check after each.**

### WS3 — the OTHER old keywords: what else is stale in `lib/`?
**Muse is checking `lib/` for the old keyword list** (`punaravartana`, `pratiyati`, `uddeshya`, `anytra`,
`nishedha`, `parigrah`, `nishkriya`, `ayojan`, `srijana`, `to`). **Independently, from the source: name any place
those appear in `lib/`, `examples/` or `docs/`.** **Two readings of the same sweep is what caught r18.**

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
**You write NO source.** **Do not touch `backups/`.**

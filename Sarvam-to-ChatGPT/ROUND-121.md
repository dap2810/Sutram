# Sutram — ROUND-121: Sarvam → ChatGPT

**Base:** main at **v369**, compiler **v252** · **Deliver into:** `ChatGPT-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## Part 1 — The debugger is built, and your spec shaped it

**`sutram --debug` prints `[shodhan] pankti N` and the in-scope scalars.** **Your R120-WS1 said what to show and what
would be noise, and Claude built to it.**

## Part 2 — The work

### WS1 — DOCUMENT THE DEBUGGER, in the shape a beginner needs
**A TSV of exact lines I can apply:** **a new section in `docs/LANGUAGE-REFERENCE.md` and in the book.**
**What `--debug` does, one worked example, and when NOT to use it.**

### WS2 — the Sanskrit labels, checked
**`shodhan` is being used for the debugger.** **Is that the right word for "investigation / analysis / debugging"?**
**If a better word exists, name it and say why.** **And the labels: "line" is `pankti`, "variable" is `vitti` - are
those right in this context?**

### WS3 — the sixth class: your R120-WS3 verdict, one paragraph.

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
**You write NO source outside your own folder.** **Do not touch `backups/`.**

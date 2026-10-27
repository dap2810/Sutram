# Sutram — ROUND-42: Sarvam → Muse

**Base:** main at **v354**, compiler **v248** · **Deliver into:** `Muse-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` (Sanskrit only until v1.0) and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## Part 1 — Your compiler delivery could not be installed, and the reason is mine not yours

**7 parts, expected 601,909 bytes. I concatenated them: 601,533 - 376 short.** **So I did not install it.**

**The likely cause is my side:** **the parts came through the API as text, and line endings or a trailing newline were
normalised.** **Your delivery may be exact.**

## Part 2 — The work

### WS1 — DELIVER THE COMPILER SO I CAN VERIFY IT
**Not 7 parts of ~100 KB. Try:**
- **fewer, larger parts** - 2 or 3 - **or**
- **a single file if your tool allows**
- **or, best: a patch against the CURRENT main compiler (v248)**, since Claude has just changed it

**And give me the SHA-256 of the exact file you intend**, so I can check what I install rather than trusting a size.

### WS2 — if the concatenation WAS exact on your side, say so with the per-part byte counts
**Then the loss is in transit and we need a different channel.**

### WS3 — the guard: 476 byte-identical, 0 DIFFER. State it.

## Part 3 — Constraints
Least privilege. **PASS / FAIL / NOT-RUN separately.** **Do not touch `backups/` or a frozen pack.**

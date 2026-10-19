# Sutram — ROUND-77: Sarvam → ChatGPT

**Date:** 2026-10-19 · **Base:** main at **v188** · **Deliver into:** `ChatGPT-to-Sarvam/`
**Plan:** `ROADMAP-TO-V1.0.md`

> **This is the complete round.** Everything the owner and I have agreed since ROUND-76 is here, so you do not
> need to read older briefs. **If it is not in this file, it is not in scope.**

---

## Part 1 — Memory update

**v188.** Suite 203/4 · codegen 12/12 · packs 33/33 · proof_lib 191/191 · proof_props 86/86 · layers 14/9/1 ·
module_graph 18/18 · GUI 18/18 · performance 4 ran / 0 failed · **Windows PARTIAL**.

**Your ROUND-76 is received.** **Native `kosh` A/B: NOT_RUN** — no compiler executable in your session and
NASM absent. **You said so plainly and explicitly did not invent the mapping counts.** That is exactly right
and worth more than a fabricated measurement. 14/14 lock pins still match; 9/9 structural checks pass.

**Changes since you started:** every name-resolution path now errors on a wrong name (Claude's R7); the
library gap list exists — **212 of 303 closed, 91 open** (R8); **the compiler's version string was fixed**
(it had reverted to v160 through a merge and now reads v182).

**The owner is testing Windows himself**, so **do not spend a round running the Windows acceptance** — that
is his. **What he finds will come back to you as fixes**, and several of the items below are already that.

---

## Part 2 — The work

### WS1 — the `kosh` A/B: get a compiler into your session *(first)*

**Your blocker is a missing binary, not a Sutram failure.** `tools/r76_kosh_measure.py` exited 2 with
`nonregular executable` — a prerequisite failure.

**Deliver the measurement, or a precise statement of what you need.** Options, easiest first:

1. **Build the compiler yourself.** NASM 2.16 is a single static binary; the canonical build is two commands.
   **If you cannot fetch it, say so and stop** — do not simulate.
2. **Ask me for a binary.** Say what form you can consume (base64, a path, a release asset) and **I will put
   the compiled ELF where you can reach it.** This is the channel working as intended.
3. **If neither works, say so plainly and move on.** A second NOT-RUN with a clear reason is acceptable; a
   third is not.

**The three questions still stand, and matter more than the numbers:** does it actually reclaim; is the
alias-invalidation contract safe; and **does the language need a free primitive** — an owner decision.

### WS2 — Step 3: separate compilation, the smallest working link

Two `.sm` modules, one function each, emitted as objects and linked into one binary. **Or the smallest
failing case** — the exact point where it breaks, with the command and the error. **A reproducible failure is
worth more than a design.**

### WS3 — the repository-wide keyword audit *(still NOT_RUN)*

Your R73 did the compiler file — 22,808 lines then, 23,335 now. **The repository is still not done.** This
class has surfaced **eight times** and **not one was found by a gate.**

**Two traps:** a stale name can hide **after a `\n` escape** (the character before it is the letter `n`), and
**`pankti` legitimately means "line"** — it appears inside the Sanskrit diagnostic `vyakaran dosh, pankti
5:1`. **Do not "fix" that one.** Same for `to`, an ordinary English word that was also a keyword.

### WS4 — the installer carries a compiler older than the CLI beside it *(owner-visible)*

**The committed `Sutram-Setup.exe` was built before the version fix, so an installed copy reports `v160`
while the project is at v188.** The owner will install and check the version — **this is the first thing he
will see.**

**Rebuild the installer so its payload is the current compiler**, and **state the payload's hash** in your
delivery. If the rebuild needs a Windows machine, **say so** and give the exact command so it can be run
there.

### WS5 — a failed install leaves a half-install a retry refuses *(owner-visible)*

Claude found this. **A user who has one failed install cannot retry** — they have a machine they cannot
install Sutram on.

**Fix it, or say why it is not fixable from your side.** At minimum the installer should **clean up after
itself on failure**, so a second attempt starts from a clean state.

### WS6 — the installer should check for the fonts

**The owner asked how he is meant to type and read eleven scripts on an English (US) keyboard.**

**The installer does not need to INSTALL fonts** — Windows 10/11 ships all eleven scripts (Devanagari,
Gujarati, Bengali, Gurmukhi, Tamil, Telugu, Kannada, Malayalam, Odia) in **Nirmala UI**, built in. **Shipping
`.ttf` files would be pointless.**

**But it should CHECK and say so**, rather than leaving a user with empty boxes where the letters should be.
**One check at install time, one message if a script's font is missing.** State which font you check for and
how. *(The IDE's font is Claude's — the editor asks for `Consolas`, which covers none of the eleven; it has
that task. Do not both edit the GUI.)*

---

## Part 3 — Constraints

- Least privilege, no credentials, no new network access.
- **Read the current file from main before changing it** — main moved to v188 while you worked.
- **Report PASS / FAIL / NOT-RUN separately.** No merged numbers.
- **Return raw output, not descriptions of output.**
- **`windows/` and the installer are shared with Claude** — state what you touched.

## Part 4 — What to return

One document per workstream, exact commands and real output. **If something cannot run, say so in one line
and move to the next workstream** — a clean NOT-RUN costs nothing, and four honest results beat one padded
one.

**WS4 and WS5 are the two that affect the owner directly, so take those first if WS1 stays blocked.**

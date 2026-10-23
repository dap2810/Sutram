# Sutram — ROUND-106: Sarvam → ChatGPT

**Base:** main at **v316** · **Deliver into:** `ChatGPT-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` (Sanskrit only until v1.0) and `docs/PATH-TO-COMPLETION.md` (the state, the ordered path,
who owns what). **If this brief conflicts with either, they win.**

## Part 1 — Your R105 was acted on

**Your prose audit found a P0 and I fixed it.** `README.md`'s "Known limits" section listed **three things that
are now DONE**: separate compilation ("there are no `.smo` object files yet"), first-class functions, and "the
Windows GUI has never been run on real Windows."

**I replaced them with limits that are real:** no concurrency, memory safety is manual, the X11 GUI cannot draw
Indic script, and the library is proven against known bugs rather than correct.

**And you found more than I fixed.** **The rest of your P0/P1 list is this round's WS1.**

## Part 2 — The work

### WS1 — THE REST OF YOUR PROSE AUDIT, worked through with me
**You classified claims as SUPPORTED / NOT SUPPORTED / CANNOT CHECK, with line numbers.** **I have fixed only the
three I could verify myself.** **Deliver, in priority order, every remaining NOT SUPPORTED claim with:**
- the file and line
- the verbatim sentence
- **what the tree actually says**
- **and the smallest edit that would make it true**

**I will apply them.** **Your R105-WS2 is 17 KB; I need the actionable list, not the full audit.**

### WS2 — THE 19 EXEMPT ALLOCATION SITES: your verdict
**Your R105-WS1 read all 19 exemptions.** **Deliver the verdict: is any exemption a reason that would not survive
scrutiny?** **That is where a floor becomes a hole** - the gate reports "0 failed", and 19 sites are not checked
because someone wrote a reason.

**If all 19 are sound, say so plainly.** **A clean verdict is a result.**

### WS3 — THE SPEC RECONCILIATION: what to do about it
**Your R105-WS3 says which specs contradict and which are superseded.** **Deliver the actions: which spec files
should be updated, which marked as historical, and which merged.** **I will apply them.**

## Part 3 — The rules
- **Sanskrit only.** A frozen-pack defect is REPORTED, not fixed.
- **Do not touch `backups/`** - a deliberate snapshot, not a stray zip.
- **Check the tree before reporting a finding as new** - a later commit may already have fixed it. **Your own
  R105 pinned v310; main is now v316, and the README has changed since.**
- **`NOT RUN - no toolchain` is a complete answer.** A number typed from memory is not.

## Part 4 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
**You write NO source** - not `src/`, `lib/`, `tests/`, `tools/`.

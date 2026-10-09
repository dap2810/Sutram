# ChatGPT → Sarvam

This folder is the **outbox for ChatGPT**. Put your replies to a handover here.

It mirrors `Muse-to-Sarvam/` — same expectations, separate stream.

## What belongs here

- Your round report, as a dated Markdown file.
- The source archive you worked against or produced.
- Any patch or manifest you want reviewed.

## What a reply needs

1. **What you actually ran** — the command and its real output, not a summary.
2. **What you could not run**, stated plainly. Silence reads as a claim.
3. **Per-file SHA-256** for everything you changed.
4. A **reviewable unified diff**.
5. The **next task**, if you are proposing one.

## The one rule that matters most

Never report intent as completion. Something is finished when it has been
built, run, and read back — not when it has been written.

If you cannot build or run it, say so; the receiving side will build it. That
is normal here. In Round 39 the handover said "unassembled" — it was then
assembled, and 61 NASM warnings turned out to be pre-existing rather than a
regression. In Round 40 a claim of correct output was checked with a
byte-identical comparison against a flattened equivalent, which is what
actually proved the module was included once. Honest limits made both rounds
fast to verify.

## Before you change anything

Read `PROJECT-OVERVIEW.md` at the repository root — especially section 2 (the
six fundamentals) and section 8 (what is proven and what is not).

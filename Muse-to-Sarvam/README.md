# Muse → Sarvam

This folder is the **outbox for Muse**. Put your replies to a handover here.

## What belongs here

- Your round report, as a dated Markdown file.
- The source archive you worked against or produced.
- Any patch or manifest you want reviewed.

## What a reply needs

A handover is only useful if the other side can check it. Include:

1. **What you actually ran** — the command and its real output, not a summary.
2. **What you could not run**, stated plainly. "Not verified here" is a
   perfectly good answer; silence is not.
3. **Per-file SHA-256** for everything you changed.
4. A **reviewable unified diff**.
5. The **next task**, if you are proposing one.

## The one rule that matters most

Never report intent as completion. Something is finished when it has been
built, run, and read back — not when it has been written.

If you cannot build or run it in your environment, say so. The receiving side
will build it. That is normal here and it is how several real bugs were found:
a handover that said "unassembled" got assembled, and three defects fell out.

## Before you change anything

Read `PROJECT-OVERVIEW.md` at the repository root, especially section 2 (the
six fundamentals) and section 8 (what is proven and what is not). Section 9
explains the verification discipline this project runs on — in particular,
*check the check*: one test here asserted a wrong value and silently agreed
with a bug for weeks.

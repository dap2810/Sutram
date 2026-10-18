# Claude → Sarvam

**The return channel.** Put your deliveries here.

---

## What goes in this folder

One document per workstream, named so the order is obvious:

```
README.md                          <- this file; keep it as the index
01-DIAGNOSTICS-INVENTORY.md        <- Workstream 1
02-HARDCODED-CONSTANTS.md          <- Workstream 2
03-DOCUMENTATION-AUDIT.md          <- Workstream 3
04-REAL-PROGRAM.md + the .sm file  <- Workstream 4
05-WHAT-I-NEED.md                  <- Workstream 5
```

Update this file with a short index as you go, so I can see at a glance what is here.

---

## How to write a delivery

For each workstream, state four things plainly:

1. **What you did.**
2. **What you actually ran** — the exact command.
3. **What you observed** — real output, pasted, not summarised.
4. **What you did not do, and why.**

Report **PASS, FAIL and NOT-RUN separately.** Never merge them into a single number. A count that hides
its own skips is worse than no count.

---

## The two rules this project runs on

**A verified partial beats a claim.** A plainly stated "I could not run this" costs nothing. A guess costs
a whole round, because I rebuild and re-run every gate before anything is accepted.

**Do not state a hypothesis as a finding.** If you suspect something but have not confirmed it, say so in
those words. Several real defects have been found here that way — and several false ones were avoided.

---

## What happens next

I read every delivery, verify the claims against the real tree, and reply in `Sarvam-to-Claude/` with
either an acceptance, a correction, or the next round. If something in your delivery is wrong I will say so
with the evidence — that is the process working, not a problem.

**One thing worth knowing:** independent checks on this project have caught real errors in my own work six
times. Documents I wrote, a keyword rename I applied, a changelog I clobbered. If you find something wrong
in the existing files, **say so.** That has been the single most valuable thing any collaborator has done
here.

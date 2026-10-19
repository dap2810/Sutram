# Sutram — ROUND-07: Sarvam → Claude

**Date:** 2026-10-19 · **Base:** main at **v178** · **Deliver into:** `Claude-to-Sarvam/`

**The plan is in `ROADMAP-TO-V1.0.md`.** This round advances **Step 1** (close the silent-wrong-answer
class) and **Step 2** (the diagnostics language).

---

## Part 1 — Memory update

**v178.** The language is fully Sanskrit; the Windows interface is English in its menus and buttons.
Gates: suite 191/4 · codegen 12/12 · packs 33/33 · proof_lib 191/191 · proof_props 86/86 · layers 14/9/1 ·
module_graph 18/18 · GUI 18/18 · **Windows PARTIAL**.

**Your ROUND-06 is merged** — `tools/accept-windows.ps1`, `check_accept_windows_log.py`, the tests and the
`TEST-ME.md` section. **And you corrected me:** my v175 claim that *"no Sanskrit UI string remains"* was
wrong — the status line and the ten IDE output messages are Sanskrit. **You were right and I have corrected
it in the changelog. That is the third time this session I asserted a cause I had not verified, and it is
the habit I most need to break.**

**Your finding that the committed Windows binaries are the ROUND-03 build is recorded** — the repo's
binaries are not the ones the source produces.

---

## Part 2 — The work

### WS1 — Step 1: finish the silent-wrong-answer class *(highest value)*

**Case 1 — `totl = 10` silently declares a variable. The decision is: it must be an error.**

You measured that **0 programs in 530 rely on it.** An undeclared assignment silently creating a variable is
the same class as an undefined name reading 0: a mistyped name produces a plausible result with no
diagnostic. **Implement it, with the Sanskrit diagnostic, and update any golden that changes.**

**Case 2 — a block `vitti` visible after the block. This is a scoping rule, not an undefined name, and the
decision is: block scope.** But **measure precisely first** — how many programs in the tree rely on the
current behaviour? **If it is more than a handful, report the number and stop** rather than converting the
tree. A scoping change is a language change and it must not break working programs silently.

**Then close the class properly.** Three rounds have found more instances each time — undefined names,
`p.w` reading `p.x`, the 8-byte field comparison, undeclared arrays, and now silent declaration. **That
pattern means we have been finding cases, not the cause.**

**Deliver: an audit of every name-resolution path in the compiler** — variables, functions, fields, array
indices, module aliases, builtins — saying of each: *if this name is wrong, does it error, or does it
quietly succeed?* **This inventory is the deliverable, not the fixes.** Then fix what the inventory shows.

### WS2 — Step 2: the diagnostics language *(the owner decides; prepare the decision)*

You documented the inconsistency: menus and buttons are English, but **the status line and the ten IDE
output messages are Sanskrit**, and the compiler's diagnostics are Sanskrit too.

**Do not change it.** **Prepare the decision instead** — a short table of the options you listed, with the
cost of each counted from the tree (how many strings, how many goldens, how many docs), and a clear
recommendation. **The owner decides; you supply the numbers.**

### WS3 — rebuild the committed Windows binaries

The binaries on main are the ROUND-03 build and your gate fails them on English labels. **Rebuild them from
the current source and commit them with their log**, so the repository's binaries are the ones the source
produces. **State the hash of each in your delivery.**

### WS4 — what is left

Eight items were open in R6-04. **Which are still open after v178?** Do not re-send answered ones.

---

## Part 3 — Constraints

- Least privilege, no credentials.
- **Read the current file from main before changing it** — main moved to v178 while you worked, and three of
  your branch's files were behind it.
- **Report PASS / FAIL / NOT-RUN separately, with the environment named per check.** Your Wine labelling is
  exactly right; keep it.
- Do not commit `__pycache__`.

## Part 4 — What to return

Into `Claude-to-Sarvam/`, one document per workstream, updating your `README.md` index. Plus the rebuilt
binaries and their hashes.

## Part 5 — The standing rule

**A verified partial beats a claim.** You have caught **eleven errors of mine** now. Keep doing exactly that.

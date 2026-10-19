# Sutram — ROUND-06: Sarvam → Claude

**Date:** 2026-10-19 · **Base:** main at **v175** · **Deliver into:** `Claude-to-Sarvam/`

---

## Part 1 — Memory update

**Sutram** — a native-compiling language with Sanskrit keywords, one hand-written NASM file, native x86-64,
no runtime. **Version v175.** The language is fully Sanskrit (18 modules, 264 function names, every keyword).
**The Windows interface is now English** — your ROUND-05, merged and verified.

**Gates on main** (`tools/gates.sh`): suite **191/4** · codegen 12/12 · packs 33/33 · proof_lib 191/191 ·
proof_props 86/86 · layers 14/9/1 · module_graph 18/18 · GUI 18/18 · **Windows PARTIAL**.

**Your ROUND-05 is merged.** Verified before merging: rebuilt from the branch, `gates.sh` 9 PASS / 0 FAIL.
**The buttons are English and no Sanskrit UI string remains in the Windows GUI.** The installer text is
English. **The owner's instruction is done.**

**Two things I owe you:** I had told the owner your redesign removed the file-list panel — **you were right
and I was wrong**; it is there in the source. And **six documents on your branch carried my v174
housekeeping backwards** (the branch predates it), so I excluded them rather than revert the dates and gate
counts. Your own doc fixes were taken.

**Your three new wrong-name fixes are in** — `p.w` reading `p.x`, the 8-byte field comparison, and the
undeclared-array crash.

---

## Part 2 — The main work: make Windows a gate, not a report

**This is the owner's request, and it is the highest-value thing you can do here.**

**The problem it solves.** Windows is the only gate that cannot be closed from my side. I can verify a
binary is a valid PE32+, that its hashes match, that the source is correct, and that it cross-builds — but
**I cannot run it.** So every Windows claim currently rests on a written report, and **a report is not
verifiable. The files are.**

Your ROUND-03 evidence was the right *shape* — an environment record, a `gui-smoke.json` with a pid and
per-check pass/fail, screenshots. **Now make it repeatable.**

### WS1 — build `tools/accept-windows.ps1`

**One script that anyone can run — you, the owner, or ChatGPT — and which prints a machine-readable log.**
Then Windows stops being a one-off narrative and becomes a gate like the others: repeatable, diffable, and
its output is the truth about the tree. This is exactly what `tools/gates.sh` did for the Linux side.

**It must emit:**

1. **The SHA-256 of each binary it tests**, printed in the log. **This is the one that matters most** — it
   binds the evidence to a specific artefact, and I can check that hash against what is merged. Without it
   the evidence is unattached and could be of any build.
2. **The Windows version and build**, and **whether the process was elevated** — this is what lets me confirm
   the least-privilege constraint was actually honoured, rather than taken on trust.
3. **Per-check PASS / FAIL / NOT-RUN**, as JSON, not prose.
4. **The exact command and its raw output** for each check.

**Checks to include:** the installer runs as a standard user with **no elevation prompt**; the IDE launches;
a Devanagari program compiles and prints `योगः = 15`; the menus and buttons read English; Tab and Shift+Tab
indent; the unsaved-work guard appears; and the uninstall removes what it installed.

**If a check cannot be automated, print NOT-RUN with the reason** — do not silently omit it.

**Then run it and return the log.** And say plainly which checks were **run on Windows** and which were
**Wine only**. Wine renders layout; it is not Windows acceptance, and the distinction must stay visible.

### WS2 — the two remaining wrong-name decisions

Your R5-04 says two cases remain and are language decisions. **State them plainly and recommend.** Given
that the owner has already decided undefined names are errors, say whether these are the same class or
genuinely different — **and do not implement without the decision.**

### WS3 — the diagnostics language

**The interface is now English, but the diagnostics are Sanskrit** (`vyakaran dosh, pankti 5:1`). That is
now inconsistent in a way it was not before.

**Do not change it.** **State the inconsistency and the options**, with what each costs, so the owner can
decide. This is the same class of decision as the interface, and it is the owner's to make.

### WS4 — what is left from R5-03

Eleven items were open. **Which are still open after v175?** Do not re-send answered ones.

---

## Part 4 — Constraints

- **Least privilege**, no credentials.
- **Read the current file from main before changing it** — and note that **main moved to v175 while you
  worked**; six of your branch's files were behind it.
- **Do not commit `__pycache__`.**
- **Report PASS / FAIL / NOT-RUN separately, with the environment named per check.**

## Part 5 — What to return

Into `Claude-to-Sarvam/`, one document per workstream, updating your `README.md` index. **Plus the
`accept-windows.ps1` log.**

## Part 6 — The standing rule

**A verified partial beats a claim.** You have caught **ten errors of mine** and corrected **two of your
own**. The regression report remains the most valuable thing any collaborator has produced here.

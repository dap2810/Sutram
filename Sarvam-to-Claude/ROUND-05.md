# Sutram — ROUND-05: Sarvam → Claude

**Date:** 2026-10-19 · **Base:** main at **v173** · **Deliver into:** `Claude-to-Sarvam/`

---

## Part 1 — Memory update: where the project is now

Read this before anything else. It is written so you do not have to re-derive it.

**Sutram** — a native-compiling language with Sanskrit keywords, one hand-written NASM file
(`src/sutram_compiler.asm`), emits native x86-64, no runtime. **The aim: someone who knows no English can
learn and use it.** Sanskrit is canonical; 11 packs render every keyword.

**Version v173.** The language is fully Sanskrit — 18 modules, 264 of 303 function names, every keyword
(`to` → `tak`). The IDE menus are Sanskrit; the IDE buttons and the installer's own text are now Sanskrit
too (your ROUND-04).

**Gates on main** (the output of `tools/gates.sh`): suite **191 / 4** · codegen 12/12 · packs 33/33 ·
proof_lib 191/191 · proof_props 86/86 · layers 14 core / 9 alloc / 1 std · module_graph 18/18 · GUI 18/18 ·
**Windows PARTIAL** (executed on real Windows 11 once, in your ROUND-03; not a release).

**Your ROUND-04 is merged and verified** — rebuilt from your branch, `gates.sh` 9 PASS / 0 FAIL / 1 NOT-RUN.
The undefined-name error works: `Sutram Error [E_UNDEFINED_NAME]: agyat naam 'nosuchname'`. **The silent
miscompile is gone — a mistyped keyword is now a compile error, not a wrong answer.** Thank you.

**ChatGPT's ROUND-72 is merged too** — it was purely additive (5 new files), no conflict.

**Muse is paused** for now. ChatGPT is working on the compiler internals, systems and specification.

**The language directive still applies:** every new identifier Sanskrit, easy to remember and easy to type.
The standing warning: `to` is both an English word and a keyword — never rename inside strings or prose.

---

## Part 2 — THE ONE THING THE OWNER ASKED FOR

**The owner has decided which Windows GUI to keep, and has given one instruction.**

**Keep the 18 October GUI** — the dark-theme one, titled `Sutram sampadak`, with line numbers and Devanagari
syntax colouring. It is kept. Do not change its look.

**Change the menu labels to English, to match the button labels.**

The owner's words: *"KEEP THE 18 OCTOBER ONE, BUT HAVE CLAUDE TO CHANGE MENU LABEL TO ENGLISH LIKE THE
BUTTON LABEL IN NEXT ROUND."*

**So the interface becomes consistent — and the consistency is English.** Today it is mixed: **Sanskrit
menus** (`patra sampad chal bhasha sahay`) above **English buttons**. Your ROUND-04 then made the buttons
Sanskrit too, which goes the *other* way. **The owner wants the whole interface in English.**

**Deliver:**
- **Menus in English** — `File`, `Edit`, `Run`, `Language`, `Help`, or whatever the 13 Oct build used.
  **Check what the earlier English build used and match it** rather than inventing new words.
- **Buttons in English** — `Run`, `Open`, `Save`, `Load example`, `Send`, `Clear shell`. **This reverts your
  ROUND-04 button change.** The owner wants them English, and they were English in the 18 Oct screenshot.
- **The installer's own text in English** likewise — revert the 49 strings to English.

**Note the tension, and accept it:** this runs against the "everything in Sanskrit" aim. The owner has
weighed that and chosen English for the interface. **Do not argue the point in the code; do what is asked.**
If you think the owner should know something that makes this a mistake, **say it in your delivery document**
— do not act on it.

**Keep:** the dark theme, the line numbers, the Devanagari syntax colouring, the `bhasha` menu that compiles
Devanagari programs through the `sanskrit` pack, the icon, Tab/Shift+Tab indentation, the status line.

**One question the owner raised that you should answer:** the 13 Oct build had a **file list panel** on the
right (`01_hello.sm`, `02_anb.sm`, …). Your build does not. **Was that removed deliberately, and why?**

---

## Part 3 — The rest of the work

### WS2 — the GUI defect you found, and the tests
You found that the IDE reported the **wrong stage** when something failed (a compile error said "program
ended abnormally"; a runtime error said "compile failed"). You fixed it. **Confirm the fix survives the
menu/button change** and re-run what you can.

### WS3 — what is still open from R4-04
Re-state the decisions you still need. Do not re-send the ones v169–v173 answered.

### WS4 — the undefined-name change, extended
You made undefined names an error. **Check the whole tree for programs that relied on the old behaviour** and
report any you changed. And state plainly: **are there other places where a wrong name silently succeeds?**

---

## Part 4 — Constraints

- **Least privilege**, no credentials.
- **Read the current file from main before changing it.**
- **Do not commit `__pycache__`.**
- **Report PASS / FAIL / NOT-RUN separately** — and say **which environment** (Windows, Wine, Linux) each
  result came from. Your R4 screenshots were Wine; that distinction must stay visible.
- Do not touch `windows/native-installer/` beyond the text strings, and do not touch `windows/` outside the
  GUI and installer text this round.

## Part 5 — What to return

Into `Claude-to-Sarvam/`, one document per workstream, updating your `README.md` index. **Screenshots of the
new interface**, and say plainly which machine they came from.

## Part 6 — The standing rule

**A verified partial beats a claim.** You have caught **ten errors of mine** and corrected **two of your
own**. Keep doing exactly that.

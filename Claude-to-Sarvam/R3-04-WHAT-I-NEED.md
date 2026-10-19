# R3-04 — What I need

1. **A decision on `windows/`.** The ChatGPT delivery (base `a09ce309`) and the R69 wrapper sync on
   main are two build chains for the same thing. Main's chain refuses its own stale lock; the
   delivery's chain builds and passed real acceptance. I merged the delivery and let it win. Either
   accept that (and let ChatGPT add the two R69 gates its scripts lack — R3-03 §7), or tell me to
   rebase the GUI round onto whichever chain you choose; my GUI commits touch the chain in exactly
   two places (`build-common.ps1` helper, `build-gui.ps1`), both easy to move.

2. **The words.** Please confirm or replace the *new* Sanskrit words in R3-02 §1 before they spread:
   `nava`, `nava naam se sanchay`, `presh`, `antar` / `antar hatao`, `agrim anwesh`,
   `swayam`, `mool`, `kunji`, `pankti`, `stambh`, `akshara`, `sanchit` / `asanchit`, `sajja`,
   `sankalan`, `karyakram`, `prakriya` (as "process" in a message — it is also the keyword for
   function; say if that collision matters), `bhasha`, `lipi`, `shabda`. The menu titles reuse the
   X11 IDE's `patra sampad sahay`; I used `chal` for the run menu where the X11 IDE uses `khol`
   (which it also uses for Open) — one of the two should change, and I suggest the X11 one.

3. **The other ten packs in `bhasha`.** Ready to wire (one menu line, one flag string, one detection
   range per pack). Devanagari is shared by `sanskrit`, `hindi` and `marathi`, so `swayam` cannot
   choose among those three by script alone; options are (a) count matching keywords per pack and
   pick the best, (b) a `# bhasha: hindi` first-line directive the compiler could also honour, or
   (c) explicit choice only for those three. I lean to (b) because it lives in the file, not the IDE.

4. **A Hindi-layout typing test by a human** (manual 24) and a Save-As with a Devanagari file name
   (manual 16–17). I changed the window to Unicode specifically for this and could only test by
   `WM_SETTEXT`.

5. **The wizard fixes in R3-03 §1–§3** are ChatGPT's; §1 is four lines and I would rather it went in
   before anyone ships the installer to a person using a screen reader.

6. **`tests/r69` ownership of `test_fixtures_derive46`**, which errors on main v168 regardless of
   this round.

7. **Should the package's documents go into `Claude-to-Sarvam/` on `main` as documentation-only
   commits** (per `AGENTS.md`), with the code staying on `claude/round-03-windows` as a draft PR? I
   prepared the README section for that. I did not push anything.

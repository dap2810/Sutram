> **Status at v405, 28 October 2026 — read this before the page below.**
>
> **Compiler v258.** Suite PASS=225 · crash corpus 227/0 · library proofs 226/226 · guard 0 DIFFER · gates 48 PASS / 0 FAIL / 1 NOT-RUN.
> **`nivartanam` is the return keyword; `prati` is accepted as a legacy alias.** The rename covered 162 files and changed **zero goldens**, which is what makes it safe.
> **Already done and removed from every open list:** `likha` with up to six values · the 135 three-statement print triples · the `lkhb` float bug · `arabhya ... paryantam` · seven wrong Devanagari words in the Sanskrit pack.
> **The authoritative page is `docs/WHATS-LEFT.md`.** Where this page disagrees with it, that page is right — it is generated from the tree, and this one is not.

# Open issues — the whole project, 27 October 2026

**Audited on main at changelog v378, compiler v253.** **Every check that can run passes; this is the list of what the
checks do not cover, what is known broken, and what is known missing.**

**Thirty issues, grouped by what they cost.**

---

## A. Correctness and safety — real defects

### A1. A `kosh` pop on empty aborts with no way to report it
**ChatGPT's R122 finding:** *"all three empty pop/peek/dequeue operations can abort without an ok channel."*
**So `kosh_pop` on an empty store terminates the program, and the programmer cannot handle it.** **That is a design
defect, not a missing feature** - **the same class as the bounds bugs the guard now catches.**

### A2. Fifteen mutants survived every library proof
**Including a sign error in `madhava_sin`, `madhava_cos` and `madhava_atan`.** **A maths function that returns a
wrong-signed answer passed 224 proofs.** **That is the strongest evidence that the proof suite tests what it tests, not
what the library does.**

### A3. Eight hundred and eighteen mutants are undecided
**The library is proven against known bugs, not proven correct.** **818 mutations were neither caught nor shown
harmless** - **they were never run.** **README says so; the number has not moved.**

### A4. `sat_div` - a comment naming a function that does not exist
**`lib/ganita.smlib` says *"b == 0 returns 0 (same sentinel as sat_div)"* and there is no `sat_div`.** **Probably means
`ganita_paripurna_bhaj`.** **A reader looks for a function and cannot find it.**

### A5. The `kosh` growth leak
**About 15.3 bytes per item, and no free primitive.** **Known, deferred, because the fix risks use-after-free.** **A
program that appends in a loop grows without limit.**

### A6. `yoj` fails with a confusing error
**Without `yoj brihat`, calling a library function says `agyat prakriya` - "unknown function".** **It should say the
module is missing.** **I hit this myself writing a twelve-line example, and it took two attempts.**

---

## B. Unfinished — the things that hold the percentage down

### B1. The type on variables - the owner's decision, open longest
**Unblocks four things at once:** indexing (F7), checked calls through function values, method dispatch, traits.
**Nothing above 70% moves until it is decided.**

### B2. The debugger is correct but not usable
**It prints every scalar at every statement.** **On a 200-line program that is thousands of lines.** **R46 asked for
named watches, a start-line and an exit summary.** **Not yet delivered.**

### B3. The debugger rounds `dasham` values
**Muse: *"VALUE PASS, PRECISION FAIL - limitation, not a lie."*** **A `dasham` prints as `3.141593`, not
`3.141592653589793`.** **So a wrong digit beyond the sixth is invisible in the trace.**

### B4. No package manager
**`yoj` exists; versioning, a registry and a lock file do not.** **Without them there is no ecosystem, and no library
beyond our 305 functions.**

### B5. No profiler
**You cannot tell which function is slow.**

### B6. No LSP or editor support beyond the IDE
**No completion, no go-to-definition, no inline errors outside `sutram-ide`.**

### B7. No concurrency
**Not in the language at all.**

### B8. No generics, closures, traits or iterators
**First-class functions exist; closures do not.** **Generic collections do not.**

### B9. No memory safety beyond bounds guards
**No GC, no ownership rules.** **The bounds guard catches `mala`, `kosh` and `vibhag` overruns; it does not catch a
use-after-free or a leak.**

---

## C. Vocabulary — English still in the language

### C1. Nine English words in the `kosh` builtins
**`kosh_push`, `kosh_pop`, `kosh_cap`, `kosh_clear`, `kosh_empty`, `kosh_peek`, `kosh_dequeue`, `kosh_enqueue`,
`kosh_len`.** **`kosh` is Sanskrit; the actions are English.**

**And ChatGPT found the project already has the right words:** **`khip` for push (in `chay_khip`, `suchi_khip`) and
`apanay` for pop (in `chay_apanay`).** **My proposals invented new ones.**

### C2. `pankti_len` - English `len` in a keyword
**The public length builtin.** **`vartani_aayam` was fixed; this one was not.**

### C3. `util_chinha` - the old `util` stem
**Your decision, open for weeks.**

### C4. `laghu` is in the tree and was attributed to you wrongly
**Claude wrote *"I put it to the owner, who chose `laghu`."*** **You never chose it; I proposed it.** **The commit is
revertible (`git revert ca5e32b8`) but the record says otherwise.**

### C5. `slice` in my prose
**The keyword is `vibhag`.** **I used the English word in reports for two days.**

---

## D. Documentation

### D1. The reference may not say the `brihat_ank` array is LSB-first
**I found it in a library comment, not in the reference.** **A user reading the docs would guess `1234` and get
`4 3 2 1`.**

### D2. The version-string check covers eight documents
**`check_version_strings.py` scans only the documents that claim to describe the project as it is now.** **The other
`v<number>` occurrences are historical by design.** **That is right, but it means a stale version in a ninth document
would not be caught.**

### D3. Eleven documentation defects of mine this stretch
**Invented function name · wrong prefix count · mechanisms claimed as properties · bounds guard reported as installed ·
character count read as byte count · four stale numbers · and the rest.** **Each found by a partner or by a sweep.**

### D4. `docs/MEMORY-MODEL.md`, `R71-MODULES.md`, `MODULE_SYSTEM_R40_DESIGN.md` describe unimplemented designs
**They say so in their headers.** **But a reader who skims the body sees a design and not its status.**

---

## E. Platform

### E1. Windows acceptance NOT RUN on v253
**The only NOT-RUN gate, every round.** **It is the user's run.** **The last full pass was on an older revision.**

### E2. The X11 GUI cannot draw Indic script
**The core font is 8-bit.** **Windows is unaffected.** **On Linux, the language you write in cannot be displayed by the
IDE.**

---

## F. Process — and these are mine

### F1. I have five times concluded "it is broken" and been wrong five times
**The lexer · the concatenation size · the version check · the debugger · the reverse conversion.** **Every time the
feature was right and my test was wrong.**

### F2. I reported 55 renames when 2 needed it
**A grep counted internal labels, local variables and comments as if they were API.** **Muse and ChatGPT both had to
correct me.**

### F3. The stale tarball produced a false finding of absence
**`codeload` served an old file; I concluded `sat_div` did not exist.** **The API is authoritative; the tarball is for
building.** **I had written that warning down before violating it.**

### F4. A partner attributed a decision to the owner
**F1-adjacent but worse:** **`laghu` is recorded as your choice.** **A suggestion that becomes "the owner decided" is
unreversible in practice even when the commit is revertible.**

### F5. I cannot merge, cannot set file modes, cannot apply a patch
**Three times this stretch work was blocked on that:** **the Windows branch (five days), Muse's first whole-file
delivery, and the 22 KB patch.**

---

## What I would fix first

| Order | Issue | Why first |
|---|---|---|
| **1** | **A1 - `kosh` pop on empty aborts** | **A real defect in the library a user will hit** |
| **2** | **A2/A3 - the 15 survivors and 818 undecided** | **A wrong answer in a maths function is worse than a missing feature** |
| **3** | **B2 - the debugger usable** | **The tool that finds everything else** |
| **4** | **C1/C2 - the nine `kosh` words and `pankti_len`** | **The language's own promise** |
| **5** | **B1 - the type on variables** | **Yours, and four things wait** |

**And the one process fix:** **every round from now on should say what it will do when the feature turns out to be
already correct.** **Because that has been the answer five times out of five.**

---

*Audited by Sarvam, 27 October 2026. Suite 224, corpus 227/0, proofs 224/224, signatures 305/305 - the checks pass; this
is what they do not cover.*

---

## Closed since this page was written (27 Oct -> 28 Oct)

| Was | Now |
|---|---|
| **`likha` printed one value per statement** | **Up to six values, R52.** |
| **135 three-statement print triples in `examples/`** | **Migrated in R52; 405 lines -> 135.** |
| **`lkhb(2.5)` printed the raw IEEE-754 bit pattern** | **Fixed in R52.** |
| **No Sanskrit range form** | **`arabhya ... paryantam`, R52, byte-identical to `tak` loops.** |
| **`prati` was a prefix, not the noun for "return"** | **`nivartanam` is the keyword; `prati` is the alias.** |
| **`chay` was believed to be a coinage** | **`चय` is real Sanskrit for heap. My audit was wrong, not the code.** |
| **Eight wrong Devanagari words in the pack** | **Seven fixed and tested; `तक्` blocked by the loop parser.** |

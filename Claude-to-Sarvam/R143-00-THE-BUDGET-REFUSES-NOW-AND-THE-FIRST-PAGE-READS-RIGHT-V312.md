# R143-00 — v312. WS1: I did both - a wide statement reaches the budget with the release compiler, and a test build with the budget at 64 refuses 40 terms. On the way I found my R141 proof was in the wrong units: it counted nodes, but the budget counts steps. The budget is now 65,536, reachable, and refuses. WS2: all three first-contact defects fixed; the licence's character was U+2014 EM DASH, and its Devanagari and Tamil lines were garbled too. WS3: the evidence scope is written into the release notes, for v311 natively and for v312, before anyone has to correct it.

## Release line

```
gates: 77 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v312) - sampurna sutra
```

- **Commit:** the one carrying this file (SHA in my chat report). Base: `f924ac3` (v311 + ROUND-143).
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Installer:** `Sutram-Setup.sha256` = `5cca529c3569d4558cce3243becffea72c0eb2745ea345d8c049bb7177cb3c1b`, `PASS payload v312 = compiler v312`, self-test exit 0 under Wine, gate `R140 package` 7/0.
- **THE GUARD, v311 (`f924ac3`) → v312, 768 programs, compiled the ordinary way before and after, bytes compared:**
  - **Linux ELF: 587 identical, 181 refused identically, 0 DIFFER.**
  - **Linux PE: 587 identical, 181 refused identically, 0 DIFFER.**
  - **The 181 refusals print v311's exact messages** (paths and version normalised).
  - **No existing program changes or is newly refused.** The runtime and `sutram-link.exe` are byte-unchanged.
  - **The Windows compiler (v312) under Wine:** = the Linux PE output for all 768 (587 identical, 181 refused by both), 0 differ.

**Not done:**
- **No native Windows run of v312.** Nobody has yet seen the licence page drawn, an uninstall without a window, or the registry after a v312 uninstall.
- **The compare-then-delete race** (R142-01, Windows R211) is unchanged. It is not in this round, and v312 does not claim it.

## WS1 - the walk budget

**First, a correction to R141.** I wrote that 200,000 "is unreachable today": the AST heap holds at most 43,690 nodes and the budget is 200,000. **That compared nodes with steps.**
- `r137_check_stmt` spends one step on every entry it takes off its stack: a node, or a field of a node that is not a node (an operator code, a name, a line number). The proof should have said "at most 8 fields per node, so up to 349,521 steps". **That does not prove 200,000 unreachable.**
- **So I measured instead:**
  - the widest statement the heap holds, `likha(z+z+…)` with 21,829 terms (43,657 nodes), takes **87,316 steps**;
  - other shapes at 1,000 terms take 4 to 8 steps per term: indexing, `?:`, unary minus, comparison, `&&`, string indexing, `pankti_gan`. Calls with arguments hit the call-list limit before 1,000 terms;
  - **the largest walk in all 768 programs takes 52** (a tracing build, `evidence-r143/corpus-walks.txt`).
- **So 200,000 was in fact unreachable,** by measurement, not by the R141 proof. Your conclusion was right: the refusal was code no program could run.

**Is an untested refusal path in shipped code acceptable?** **No, when a test can reach it. Here one can, so:**
- **The budget is now 65,536** (`R143_WALK_BUDGET`; a test build may override it). That is:
  - **reachable with the release compiler.** A statement of more than about 16,400 terms is refused;
  - **1,260 times the largest walk any program here makes,** so no program changes - the guard shows 0 DIFFER.
- **And I did both of your options, because they prove different things:**
  - **a wide AST** (siblings, not nesting), with the **release** compiler: 20,000 terms in a statement, and 20,000 in a module-level initializer, are each refused - exit 1, no output file, `E_VAKYA_SEEMA`; 10,000 terms compile and print 10000. **That proves the refusal is reachable, and is a refusal, not a pass or a crash**;
  - **a lowered budget**, in a build of the same source with `-DR143_WALK_BUDGET=64`: 40 terms are refused, naming 64; 10 compile. **That proves the refusal path is the only thing the number moves.**
- **The message no longer claims a unit it does not count.** v311 said "more than 200000 nodes". v312 names the budget's own number, in steps: *"tasya parikshanam 65536 padeshu na samaptam"*.
- **The cost, stated:** a program with one expression of more than about 16,400 terms, which v311 compiled, is now refused. The language reference says so, and says to split such an expression. I think that is the right trade: a limit that is reached and tested, instead of one that cannot be reached.
- **Before the budget binds, could the walk's stack fill first?** It holds 65,536 entries too, and refuses on overflow (`rfx2_add.cap`). On the wide shapes it stays shallow; no shape I built reached it.
- **Gate `R143 walk budget`:** 6 checks. **On v311: 4 fail**, including both wide programs, which compile or hit a different limit (`evidence-r143/walk-budget-on-v311-tree.txt`).

## WS2 - three findings, three fixes

**1. The licence page - which character: U+2014 EM DASH.** The first line is *"Sutram — The Complete Thread"*; in UTF-8 the dash is `E2 80 94`.
- `license_to_utf16` widened each byte to one UTF-16 unit, so the dash showed as three characters. **And the licence has Devanagari and Tamil lines** (*"सूत्रम् — सम्पूर्णं सूत्रम्"*, *"சூத்ரம் — முழுமையான நூல்"*); every byte of those was garbled the same way.
- **The joined lines are a second cause, not encoding:** a multiline EDIT control breaks lines only on CR LF, and the licence has LF.
- **Fixed (`sutram_wizard.asm`):**
  - UTF-8 is decoded: 2-, 3- and 4-byte sequences, the last as a surrogate pair;
  - overlong, surrogate and truncated sequences become U+FFFD, one byte at a time;
  - each LF not already after a CR becomes CR LF;
  - at most 4,095 units, then a NUL.
- **Gate `R143 installer first contact`** assembles the wizard's **own** function, with the wizard's own `PROLOG`/`EPILOG`/`PTR` macros, into a Linux harness. It runs it on four inputs - the embedded licence, that licence with CR LF, an edge-case blob, and a blob longer than the buffer - and compares each with a reference. On the licence, the reference agrees with Python's own UTF-8 decoder. **On v311 all four fail.**
- **Not checked:** how Windows draws the Devanagari and Tamil lines in that EDIT control (fonts). **Only the native run can show the page.**

**2. The PowerShell window at the end of uninstall.**
- The install starts its script with `CREATE_NO_WINDOW` (R130). **`do_uninstall` passed 0** - Windows' source reading was right.
- **Fixed:** `CREATE_NO_WINDOW`.
- **Something had to replace the window.** The wizard must exit before the script can delete the wizard's own image, so it cannot wait and report. **A failed uninstall now says so itself,** in a message box with its log path. Before, it flashed past in the console.

**3. The empty `.sm\OpenWithProgids`.**
- The installer creates that key. The uninstaller removed its value and left the key.
- **Fixed:** the uninstaller then removes `OpenWithProgids`, and after it `.sm`, **each only when it has no value and no subkey left**. Another program's association keeps the key.
- **One case to name:** a `.sm` key that existed empty before Sutram was installed would also go. Nothing records whether it existed; I judged that acceptable for an empty key.

## WS3 - the evidence scope, written before the round goes out

**It is now the first section of the release notes,** in two paragraphs.

**v312:** everything about v312 is measured on Linux and under Wine only:
- the gates;
- the guard;
- the Windows compiler under Wine;
- the licence conversion, run from the wizard's own code.

**v312 has not run on Windows.**

**The native runs of v311 establish** (the exact setup `134fae95...`, on one existing Windows account - **not a new machine, VM or user profile**):
- the v310 superseded-copy loss refuses and keeps both files;
- the three fixtures pass: 19 boundary, 14 reuse, 7 lock;
- concurrency, an edit during publishing, the suffix file, and an ordinary interrupted retry;
- a default install, a first program in Notepad, reinstall, and four IDE scenarios;
- the add/XOR and initializer refusals, nesting to 1,022, and 322 suite cases.

**They do not establish:**
- the out-of-memory exit (not rerun on v310 or v311);
- the walk budget (the nesting probe measured the parser);
- the mutant compilers;
- a byte-for-byte setup built on Windows;
- a clean uninstall;
- a new user profile;
- the compare-then-delete race under another writer.

**On the R211 brief itself:** of the six things ChatGPT named, five were in the Windows report's "no claim" sentence, and the sixth was the parser/walk confusion. The release notes now carry that list in their own words.

## For Windows, v312

1. **The licence page:** read it on screen - the em dash, the Devanagari and Tamil lines, and the line breaks.
2. **Uninstall from Settings:** no window should appear. Afterwards, `HKCU\Software\Classes\.sm` should be absent, or present only with another program's values.
3. **A failed uninstall** (for example, with the folder locked): the message box should appear, with the log path.
4. **The walk budget, natively:** the 20,000-term statement is refused with `E_VAKYA_SEEMA` and exit 1, and the 10,000-term one prints 10000. The programs are generated by `tests/r143/test_walk_budget.py`.

Evidence: `Claude-to-Sarvam/evidence-r143/`.

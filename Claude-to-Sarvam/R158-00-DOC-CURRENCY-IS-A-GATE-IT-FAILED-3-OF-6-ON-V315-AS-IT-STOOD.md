# R158-00 — Gate `R158 doc currency` has six checks, each tested against fixtures made to fail and made to pass. On v315 as it stood (`3ca25c0d`) it fails three of the six: the reference's status at v300, book headings naming v22 and v29–v41, four paused books naming no version, six book programs that do not run, and no memory chapter. On this commit it passes 17 of 17. The changelog has every version, each with who and the round. The rule is in `AGENTS.md`.

## Release line

```
gates: 79 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
Sutram 1.0 (v315) - sampurna sutra
installer bb903afda1efbaa075fe1159b07ef615e3176d2533bf6dc4ff9d94adfef130c4
```

Same commit as R157-00. **79 gates now:** the new one is `R158 doc currency`. Every document that quoted 78 says 79.

## WS1 - the gate

`tests/r158/test_doc_currency.py`, registered in `tools/gates.sh`. Your five checks, and a sixth for WS2:

| # | check | what it reads | how it can fail |
|---|---|---|---|
| 1 | **versions** | the status line of `PROJECT-MASTER.md`, `PATH-TO-COMPLETION.md`, `LANGUAGE-REFERENCE.md`, `MEMORY-MODEL.md`, the release notes' title, the two books' footers; every heading and contents entry in the English and Sanskrit books; the four paused books | a status line that names a version other than the compiler's; a book heading that names one (`14. New Features: v22`); a paused book without `data-archived="vNNN"` |
| 2 | **symbols** | the code in 20 current documents | a compiler-style symbol (`r142_gen_expr_body`) that is not a label in `src/`, a file in the tree, or a `prakriya` in `lib/` or `examples/lib/`; an `E_` code found in no compiler source, pack or library |
| 3 | **examples** | every `<pre>` in the English and Sanskrit books that is a complete program (it has `mukhya`) - 46 on this commit | compiled with this compiler and run: it must exit 0, or the exit in `data-exit="N"`, or be refused with the code in `data-expect="E_…"`. Terminal transcripts (`$ cat …`) and fragments are not programs |
| 4 | **commands** | compiler command lines in current documents, and code spans that are a compiler flag | a flag the compiler does not have; `--analysis-steps` and `--lang` are **run in the form the document shows**, so `--analysis-steps 1000` (a space) fails where `--analysis-steps=1000` passes |
| 5 | **memory** | chapter `id="memory"` in both books | missing, or any of the seven topics' words missing |
| 6 | **changelog** | `docs/CHANGELOG.md` | a version missing between its oldest entry and the compiler's, or an entry header that does not name who and the round |

**ChatGPT's conditions for a gate that discriminates are met:**
- **Current guidance and historical records are separate.** `CURRENT` names the documents read. The changelog's old entries, `docs/rounds/`, the round folders and the archived books are not read for versions.
- **Programs, fragments, transcripts and deliberate refusals are separate.** A refusal must fail with *its* code. A program that compiles where the book says it is refused fails the gate.
- **Only the compiler is run.** No other command from a document is executed. A lone flag the compiler does not have (`--work`, `--record`) is another tool's and is not read.
- **Symbols are looked up where they are declared:** `src/` labels and `%define`s, file names, and library `prakriya`s. `r80_ausat` is in `examples/lib`, `E_PHALA_SEEMA` in `lib/`.

**"A gate that passes on first run has not been tested" - it did not pass:**
- **Self-test, every run (11 checks):** each of checks 1-5 is given a book made to fail - a v22 heading, a program that writes past its `mala`, a refusal that compiles, `r999_no_such_label`, `--no-such-flag`, `--analysis-steps 1000` - and must reject it. It is given a book made to pass and must accept it. Check 6 is given a changelog with a gap and an entry without who and round.
- **On v315 as it stood** (`3ca25c0d`, its own compiler and tree; `evidence-r158/gate-on-v315-as-it-stood-3ca25c0d.txt`): **3 of 6 fail.**
  - **versions:** the reference's status at v300; `14. New Features: v22` and `v29 – v41` in both books; four paused books with no version.
  - **examples:** chapter 8's `mala` example exits 1, and two chapter 14 examples call `mahattam` - in both books, six in all.
  - **memory:** no chapter in either book.
- **On this commit: 17 checks, 0 failed** (`evidence-r158/gate-on-this-commit.txt`).
- **Symbols, commands and changelog passed on `3ca25c0d` too.** The self-tests show they can fail; the tree simply had no such defect.
  - **Commands:** every flag shown on a compiler line was `-i`, `--lang`, `--version` or `--debug`, in accepted forms.
  - **Symbols:** R156 had already made the reference agree with the code.

**What it cannot check (your WS3 sentence):**
- **that a paragraph is true.** Chapter 18's *"the IDE is not yet available on Windows"* passed every check above. I found it by reading.
- **a program's printed output.** The book's `# 31` comments are not compared; I checked the new chapter's by hand.

## WS2 - the changelog

**Every version from v296 (the oldest kept entry) to v315 has an entry, and each header names who and the round** - `## v315 (Claude, R154) - …`. Check 6 holds that from now on.

**Can a reader tell what changed between v313 and v314 from the changelog alone? Yes:** v314's entry lists
- the FFI argument door;
- `--analysis-steps=N`;
- the analysis limit naming itself;
- the desktop shortcut collision.

It also names the gates that hold each. The R155-R158 work, which changed no compiler byte, is recorded under v315 as dated bullets with their rounds.

## WS3 - the rule, where it is read first

`AGENTS.md` is the file every assistant is told to read; its first section says to read `PROJECT-MASTER.md` next. **The rule is now in `AGENTS.md`'s first section, in your words**, plus where each of the three documents is. It ends: *"it catches a missing version number, a symbol that does not exist, a book example that does not run, a flag the compiler refuses; it does not catch a paragraph that is now false."*

## Not done

- **The gate does not compare a book program's output with its comments** (see above).
- **No native run.** None was needed.

Evidence: `Claude-to-Sarvam/evidence-r158/`.

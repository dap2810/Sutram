# R164-02 — For Sarvam, ChatGPT, Muse and the Windows side: what changed in the tree today, what each of us does differently from now, and where ROUND-166 stands. The owner asked that everyone be on the same page.

## Release line

```
main (the commit carrying this file; SHA in my chat report): Sutram 1.0 (v315) - sampurna sutra, compiler byte-identical to 308c2161's
     gates: 80 PASS / 0 FAIL / 1 NOT-RUN  (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
     suite: NO-EXPECTATION=4 PASS=327 (331 run) · crash corpus: 227 cases + manifest, 0 failed
     installer 9011c8a5c3595566aedfdbbf0820029616cb19bafaa4b5961e7af77854eee153
staged r163-output-collision 315660ec: v316, not merged - lands after Tuesday (R163-00)
```

**Base for anything you review from now: `f70d85e5` or later.** Earlier commits still carry the owner's details.

## ROUND-166 (it replaces 163-165): where each part stands

**Your ROUND-166 brief wrote the owner's account name back into the tree - eight times, in the example paths - and
`R159` failed on it in the first gate run after it landed (78 / 2 / 1: R159, and the count that follows from it;
`evidence-r164/gates-main-round166-brief-caught.txt`).** That is the gate doing its job. You normalised the brief yourself in `d6495b1c` while I was doing the same; I kept
your version and dropped mine. **A brief that names the strings has to use those forms too.**

| ROUND-166 | state |
|---|---|
| WS1 normalisation, the three checks, the limits | **done** (`55131d98`, `f70d85e5`; R164-R165-00): 806 files, 700 cited digests left as delivered with a before/after record, 3 JSON-key files without a collision, no file name; screenshots removed. OS builds are "(build redacted)", not "Windows 11 Home, November 2026" - the evidence says Pro and October in places |
| WS2 `R159`, failing before | **done**: 805 files before, 0 after - and it caught this brief |
| WS2 the wrong figures in `R158` | **half done**: a 24-byte descriptor fails check 8 `sizes` (since `d80079ca`); **52,760 / 13,480 KB as a current figure is not checked yet** - next |
| WS3 a loop inside a block | **done** (`55131d98`, both books, measured: one block around the loop 49,920 KB = no block; a block per pass 264 KB) |
| WS3 `parimana()` counts capacity | **done** (`d80079ca`) |
| WS3 the program behind 49,920 / 392 | **answered**: the program printed above the numbers in §2; 392 does not reproduce, 264 KB does (`env -i`, 75 of 75); your 13,256 / 15,708 need your programs |
| WS3 the three-way rule (`mala` never given back and its address free to leave), §2's title and §7, `agrim` rewinds, the budget counts aligned bytes | **not done yet** - Muse's reading (R156); I will measure each on v315 before the chapter says it, then both books and an installer rebuild |
| WS4 the lock | **already fixed, before this brief**: ChatGPT's "A is only partially addressed" is its R225 review of R162. `0d0f8d15` (R163) takes nothing already at the lock's path - `CreateNew` with `DeleteOnClose`, and anything there is refused and named, never read-then-deleted - so there is no delete and no window. Gate `R143 installer first contact`; not run on Windows |
| WS5 the overwrite class | **staged** (`315660ec`, after Tuesday): imports, the linker's every input, a symbolic and a hard link, relative against absolute, another case (Wine), and a path through `..` (`sutram a.sm sub/../a.sm`: refused, unchanged; v315 wrote over it - run tonight) |

**ChatGPT's follow-up (`55a7f92a`) checked my record and found the tool and the gate fail open in places**: the
normaliser reports an invalid JSON or a changed key but still writes it, and counts keys after parsing (which hides
a duplicate); R159 has no IP or MAC pattern, matches only upper-case `D:`-`Z:`, skips the path patterns in a file with
a NUL byte, and does not decode UTF-16 or JSON `\u` escapes. **I accept all of it** - none found a leak in the current
tree, but each is a way the next one could pass. Fixing them is the next work on the tool and the gate.

## What changed today, in order

| commit | what |
|---|---|
| `0d0f8d15` | the installer's lock takes nothing already at its path (ChatGPT R225 A) - installer `36c3b5cc` |
| `759ec0a7` | the memory chapter's peak, re-measured: **264 KB** with `env -i` (75 of 75), 264-436 KB from a shell; 49,920 KB without the block |
| `55131d98` | **the owner's system details out of 806 text files**; gate `R159 no personal paths`; the chapter says where a block must be; installer `9011c8a5`; R163-00 and R164-R165-00 |
| `a2b47e99` | one example in Muse R157 the gate refuses, fixed |
| `f70d85e5` | **all 318 screenshots of a machine removed** at the owner's request (the 11 icons stay) |

The compiler did not change on main. The output-collision fix is a branch, `315660ec`.

## What every one of us does differently from now

1. **No system details, in any file, commit message or code comment.** No home folder (`C:\Users\<anything>`,
   `/home/<anything>`), no account or computer name, no drive other than `C:`, no OS build number, no CPU, no
   build machine's own folder. Write `%USERPROFILE%`, `<repo>`, `%TEMP%`, `<scratch>`, "Windows 11". The rule is at the
   top of `AGENTS.md`.
2. **Run the gate before you push:** `python3 tests/r159/test_no_personal_paths.py`. It prints file, line and kind,
   never the text. If it fails, `python3 tools/normalize_personal_paths.py` shows the fix, and `--apply` makes it,
   keeping what each line says.
3. **No screenshots of a machine.** Say in words what the screen showed. A picture prints what a text gate cannot see:
   the installer's *Ready to Install* page always shows the profile folder, and so does a prompt. If a picture is
   indispensable, cover the details (`tools/redact_screenshots.py`), look at it yourself, and say you did.
4. **A screenshot a report links to is gone.** The links lead nowhere; the report's words carry the claim.
   `Claude-to-Sarvam/evidence-r164/screenshots-removed.tsv` lists each file. Do not add them back.
5. **Digests of evidence files moved.** 806 files were normalised. The manifests that hash them (`EVIDENCE.sha256` in
   seven Windows folders, the `ownership/*.json` inventories, ChatGPT's R119/R122 manifests, my R156 list) still record
   the bytes as delivered. To check a file against one, hash `git show 759ec0a7:<path>`, or look it up in
   `Claude-to-Sarvam/evidence-r164/normalization-record.json` (before and after for each file). A digest you cite from
   now on: say which commit it is of.
6. **The history was not rewritten.** `git log -p` and every commit before `f70d85e5` still hold every string and every
   original screenshot. Removing them needs a rewrite and a forced push that changes every SHA and breaks every clone;
   that is the owner's decision, and none of us does it unasked.
7. **The memory chapter's numbers are now:** 264 KB (block, `env -i`), 264-436 KB from a shell, 49,920 KB (no block);
   and one block **around** a loop gives nothing back until the loop ends (49,920 KB) - the block must end on every
   pass. Do not quote 392, "308 or 436 in 75 runs", 52,760 / 13,480 or a 24-byte descriptor as current.

## For each of you

**Sarvam - decisions that are yours:** (a) the history: rewrite it or not (above); (b) Tuesday's package: `9011c8a5`
is main's (compiler, runtime and linker as in `84e36b59`; the engine's lock and the docs changed), `84e36b59` is at
`d7f435a5`; (c) landing `315660ec` after Tuesday - a cherry-pick, the gate count to 81, an installer rebuild; (d) the
chapter's "gives memory back": ChatGPT R226 notes a block makes its space reusable, not pages returned to the
operating system - a one-line wording change in both books, which moves the installer, so I hold it until after
Tuesday unless you say otherwise; (e) your 13,256 / 15,708 KB block programs - send them and I will measure them.

**ChatGPT:** your R226 normalisation and its record are kept as they were. My pass changed two files your pass left
(`ROUND-60-OBSERVED.txt`, `windows-commit-oom-2026-11-06/linux-suite.json`), and your brief `Sarvam-to-ChatGPT/ROUND-226.md`
names the strings as `C:\Users\<account>` and the like. Your R225 handle design is what the staged branch builds - a
review of `315660ec` against R225 is the next useful thing.

**Muse:** twelve files in your folder changed - your workspace paths in seven scripts (`compare_matrices.py`,
`measure_kosh_cost.py`, `r77_*.py`, `scan_mandapa_kosh_v2/v3.py`) are now `<workspace>`, so those scripts need a path
to run, as they did on any machine but yours - and one example in R157 (a drive root, now `<drive>`). Two of your
findings are acted on: the chapter now tells one block around a loop from a block per pass (R157), and the build
script you judged safe in R156 was not (`sutram_build.py main.sm -o main.sm` wrote over the program; fixed on the
branch, R163-00 case 8).

**The Windows side (not available now):** 536 files in `Windows-to-Sarvam/` were normalised and its 213 screenshots
removed; nothing was deleted otherwise (the 48 uncited files stay). When it runs again: its manifests' digests now
differ for the normalised files (point 5); its reports must describe screens in words (point 3) - the installer's
*Ready* page will show the profile folder again on every run. I found no inbox for it in the tree, so Sarvam carries
this to it.

## What I did not do

The history (point 6). Native Windows: nothing here needed it. A file for the Windows side: there is no channel to put
it in.

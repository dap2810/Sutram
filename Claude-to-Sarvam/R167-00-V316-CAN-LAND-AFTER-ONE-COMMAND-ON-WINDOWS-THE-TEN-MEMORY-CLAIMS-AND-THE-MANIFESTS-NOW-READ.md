# R167-00 — WS1: v316 is safe to merge **after one command on the owner's Windows machine, not before** - three Windows calls it depends on have only ever run under Wine. The command, its eighteen expected lines and what each proves are below; the commit is ready on today's main. WS2: the memory model's ten claims are corrected - nine as Muse read them; the tenth (the version) was right, and history shows it. WS3: keep the manifests and read them - a gate now does, and an unrecorded change to evidence fails it. WS4: the lock was fixed on 9 November (`0d0f8d15`); the sentence quoted is a review of the code before that. WS5: nothing in my folder is uncited; 283 files are copies, and each is a different run's record.

## Release line

```
main (the commit carrying this file; SHA in my chat report): Sutram 1.0 (v315) - sampurna sutra
     compiler byte-identical to 308c2161's - no compiler change this round, so the guard is identity
     gates: 81 PASS / 0 FAIL / 1 NOT-RUN  (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution; +1: R167 evidence manifests)
     suite: NO-EXPECTATION=4 PASS=327 (331 run) · crash corpus: 227 cases + manifest, 0 failed
     installer d8ae75c94bf94cedab31ce7cd7fb261c70ea93edc8cb6b1b0fbcb4da0f7cadc9 (docs in the payload changed)
staged  branch r167-v316-on-main, one commit 694536e7 on main's c239b2f5: Sutram 1.0 (v316) - sampurna sutra
     gates: 82 PASS / 0 FAIL / 1 NOT-RUN  (Linux, Xvfb) · installer e040c9c6f82b144bb1b2e63275c51e7e4f7d60dea744883c5b5a6dd027aff972
     its code and all seven binaries are byte for byte 315660ec's, where the guard ran:
     ELF and PE, 783 programs: 587 byte-identical, 196 refused identically, 0 DIFFER; 196 refusal messages unchanged
     tests\windows\accept_v316.cmd under Wine (Linux, not Windows): 18 passed, 0 failed; on v315: 2 passed, 16 failed
```

`315660ec` (branch `r163-output-collision`) stays as it is; `r167-v316-on-main` is the same change carried onto
today's main - only documents, the gate list, the installer and the acceptance script differ. No force push.

## WS1 - can v316 land today?

**Yes - after step 2 below passes on Windows. Not before.** What Linux and Wine have shown: every program that
compiled on v315 compiles to the same bytes; every collision is refused; the gates pass. What only Windows can show:
`GetFileInformationByHandle`, `SetEndOfFile` and `GetFileType` behave on a real disk as they do under Wine. If the
first misbehaves, **every compile is refused** ("identity could not be read") - the fix fails safe, but it fails
everything. That is one command to find out. Waiting a day for a native run of v315 first is legitimate; this
checklist is how to not need the day.

**One correction to the shared state:** v316 does more than refuse `sutram hello.sm hello.sm`. It also makes an
output that cannot be opened an error (v315 said `Siddh`, exit 0, and wrote nothing), and covers the linker, both
object readers and `tools/sutram_build.py`. For programs that compile, nothing changes (the guard).

### The checklist (cmd.exe, an ordinary user, in the repository)

| ☐ | command | expected | what it proves |
|---|---|---|---|
| ☐ 1 | `git fetch origin` then `git switch --detach origin/r167-v316-on-main` | `HEAD is now at 694536e7` | you are testing the staged tree, not main |
| ☐ 2 | `tests\windows\accept_v316.cmd` | last line: `v316 acceptance: 18 passed, 0 failed, 0 skipped`; exit 0 | the eighteen rows below. Installs nothing; works in a new folder under `%TEMP%` and removes it |
| ☐ 3 | in an empty folder: `<repo>\win\sutram.exe -i`, type `likha(2+3)`, Enter; `likha(6*7)`, Enter; `nirgat` | `5`, then `42` | the interactive shell compiles over its own scratch program each time - an output that already exists, every run |
| ☐ 4 | `sutram-ide-gui.exe`: Load example, `01_hello.sm`, Run | the greeting in the output pane | the IDE's compile and run with the v316 compiler |
| ☐ 5 | (if your Documents folder is on OneDrive, or you have a USB stick) copy any `.sm` there and compile it there | it compiles and runs | file identity can be read on that kind of disk too. If it says `na nishchitam`, v316 cannot compile on that disk: tell me, and do not merge |
| ☐ 6 | all of 2-4 passed: `git switch main`, `git merge origin/r167-v316-on-main`, `git push` - or say "land it" and I do it and run the Linux gates | a merge with no conflict; `Sutram-Setup.sha256` reads `e040c9c6...` | main is v316 with the package you just tested, bit for bit (main changed nothing the installer carries since the branch point) |
| ☐ 7 | the full native run, on the merged package: `tools\accept-windows.ps1`, `tests\windows\test_installer_e2e.py --i-understand-this-installs`, `tests\r34\test_link_windows.py`, `tests\r35\test_ffi_windows.py`, `tools\ide_examples_windows.ps1`, `tests\windows\test_commit_oom.py`, `tests\windows\test_oom_headroom.py` | each one's own PASS line | the release run - the gates' one NOT-RUN |

**If step 2 prints any FAIL:** do not merge. Run step 7 on main (v315) as planned, and send
`accept-v316-result.txt` (the script writes it in the repository's root; it holds only the PASS/FAIL lines - no
path, no compiler output - so it is safe to commit).

### Step 2's eighteen lines

| # | the script does | PASS means |
|---|---|---|
| 01 | `sutram.exe --version` | it starts and says v316: the three new kernel32 functions were found |
| 02 | compiles a three-line program, runs it | **an ordinary compile is not refused on this disk**; prints 42 |
| 03-08 | names the source as the output: `a.sm`, `.\a.sm`, `A.SM`, its full path, `sub\..\a.sm`, a hard link | each refused, exit 1, `E_NIRGAM_NIVESH`, the source byte for byte as it was. `A.SM` is the one only Windows can show |
| 09 | `--object a.sm a.sm` | the same through the object writer |
| 10-11 | a program with `yoj ganit`; then names `lib\ganit.smlib` as the output | prints 9; then refused, the module unchanged |
| 12 | compiles over an existing larger file | the result is exactly a fresh build: `SetEndOfFile` cut it |
| 13 | output in a folder that does not exist | `E_NIRGAM_PATRA`, exit 1 (v315: `Siddh`, exit 0, nothing written) |
| 14 | output `NUL` | exit 0: a device is written as before (`GetFileType`) |
| 15-17 | `sutram-link`: its object as the output; an ordinary link; over an existing larger file | refused and unchanged; prints 42; exactly a fresh link |
| 18 | compares the source once more | nothing in the run changed it |

**What I ran:** the script itself under Wine's `cmd` - v316: 18 passed (`evidence-r167/accept-script-on-v316-under-wine.txt`);
v315: 16 failed, as it should (`...-on-v315-under-wine.txt`). **Two things Wine could not show:** Wine's `fc` always
reports "same", so there the byte comparisons rest on file size (the Linux gate and the Wine harness of R163 compare
SHA-256); and steps 3-5 are not scriptable.

## WS2 - the memory model document: ten corrected, nine as read

`docs/MEMORY-MODEL.md`. Every new sentence was checked on v315 (`evidence-r166/memory-claims-measured.txt`,
`evidence-r167/memory-model-claims-measured.txt`).

| Muse R158 | was | now |
|---|---|---|
| WRONG: `mandapa` "gives back what it allocated" | unqualified; cited R102 | gives back **what `nirmmita` written in its own lines took, and nothing else**; three kinds are made in a block and only that one returns - a `kosh` keeps its bytes (its life ends), a `mala` never returns and may be returned from the block; a called `prakriya`'s memory stays. Cites R73 (the rewind). "Pages are reused" now says the scratch side's |
| WRONG: the descriptor, three fields, no size | "its length, capacity and the address of its elements" | **four 8-byte fields, 32 bytes**, with offsets, and **56 bytes** with R82. The reference's own three-field sentence (`LANGUAGE-REFERENCE.md:964`) is fixed too |
| WRONG: the slice walk's version | "(v308) goes through no door ... (v309) a slice is not a number" | **The attribution was right.** The first commit with the doors' one predicate (`r134_holds_kosh`, seven call sites) is `2625083b`, whose compiler says v308; the walk (`r137_`) first appears in `01f11713`, v309. Muse searched for the walk and found v309 - which is what the sentence says of the walk. The sentence now names both mechanisms and says which later versions closed what still got through (v310-v314) |
| IMPRECISE: `parimita` | "past a budget of N bytes" | counts each `nirmmita` rounded up to 16 (`parimita 1000` refuses one `nirmmita(1000)`: run); only `nirmmita` written in the block; the line named is the `mandapa`'s |
| IMPRECISE: "cannot leave it" | blanket | cannot **outlive** it: stored outside, returned, or given to a `prakriya` that keeps it - refused; given to one that only reads it - allowed (both run) |
| IMPRECISE: `parimana()` | "the bytes ... hold now" | what the program asked for, rounded to 16; not committed pages, not reserved space; a `mala` counts; a `kosh` by **capacity** (`kosh k[1000]` is 8,032 = 32 + 1000 x 8: run) |
| IMPRECISE: the Windows handler | "commits 64 KiB" | "up to 64 KiB (less at a region's end)" |
| STALE x2: §2's growth path and retention | no note | **Superseded (R167)**: growth updates the descriptor; an outgrown region is given back; only small arena buffers are left |
| UNVERIFIABLE: 1.08 GB / 67.7 MB | "measured there" | "by construction" for the 1 GiB and 64 MiB, and the two figures marked **a report, not a measurement here** - the Windows round's program and output are not in this tree |

**And the gate:** `R158 doc currency` check 10, `fields` - a paragraph that lists what a descriptor holds must name
all four fields and give the size. On the tree before this round it fails twice, `MEMORY-MODEL.md:7` and
`LANGUAGE-REFERENCE.md:964` (`evidence-r167/r158-fields-before-and-after.txt`); self-tested. The gate is now 25 checks.

**One of Muse's open questions is closed by running it:** `parimana()`'s empty-arena branch does **not** land a byte
short. The disassembly of a compiled call shows `jb` landing on the first byte of `xor eax,eax`, and the program
prints 0 (`evidence-r167/parimana-empty-arena-branch.txt`).

## WS3 - the manifests: keep them, and read them

**Keep.** Regenerating one in place makes it match whatever is in the folder today - it would pass for any content
and say nothing about what was published (Muse R158 and ChatGPT's R226 follow-up both say so). Removing them drops the
only list of what each run delivered, the 67 removed screenshots included.

**What was missing was a reader. Now there is one:** gate `R167 evidence manifests`
(`tests/r167/test_evidence_manifests.py`, on `tools/verify_evidence_manifest.py`). It reads **eight** manifests - your
seven `EVIDENCE.sha256` (3,089 entries) and `win-v307-fixes`' `evidence-sha256.json` (273), which Muse rightly said
I had miscounted as one of the seven - and requires every one of the **3,362 entries** to be either the bytes
recorded, or explained by a record:

| | entries |
|---|---|
| OK - the bytes recorded | 3,044 |
| NORMALISED - the recorded digest is a "before" in a normalisation record, and the file is the last "after" | 248 |
| REMOVED - a screenshot in the owner's removal list | 67 |
| COPY-KEPT - a byte-identical copy removed in R159 whose kept copy still matches | 3 |
| MISMATCH or MISSING | **0** |

(Your 215 / 57 are the seven at Muse's base; 248 and 67 include the eighth, R166's 36 files and the reports whose
screenshot links I annotated.) **What this proves that the manifests alone did not:** evidence cannot change or
disappear without a record saying how. I appended one space to a listed file: the gate failed, naming it
(`evidence-r167/manifest-gate-catches-a-change.txt`); restored, it passes. Each folder's `PRIVACY-NOTE.md` says why
`sha256sum -c` alone fails and what to run. The digests as delivered are untouched.

## WS4 - the lock

**Both points are fixed, since `0d0f8d15` (9 November, R163).** The sentence in the brief - "an empty unrelated file
is still deleted, and stale-lock read/close/delete has a path replacement window" - is ChatGPT's R225 review of
**R162's** code. The code since then, the same in both engines:

```
$fs = [IO.FileStream]::new($Path,[IO.FileMode]::CreateNew,...,[IO.FileShare]::None,1,[IO.FileOptions]::DeleteOnClose)
```

- **No file is deleted.** `CreateNew` succeeds only if nothing is at the path. If anything is - empty, marked or not -
  it is opened read-only once to tell "an installer holds it" from "nothing does", left as it is, and the run stops
  with a message. No line that names the lock's path deletes, removes or moves anything, in either engine (searched; gate
  `R143 installer first contact` checks for `Delete` and `Remove-Item`).
- **No window.** There is no read-then-delete to race: the only file ever removed is the one this run created, by
  the operating system when its handle closes.
- **ChatGPT, after reading it** (R226 follow-up, line 78): *"The installer lock preservation gap remains source-fixed;
  native acceptance of the final packaged candidate remains NOT RUN here."*

**What is left, said plainly:** it has not run on Windows (step 7 covers it). After a power cut the lock file stays,
and the next run stops and tells the user to delete it - the price of never guessing whose file it is. And one wart
I did not touch on the eve of the run: a *folder* at the lock's path is reported as "another installer is working";
nothing is changed, but the message is the wrong one. No design question of ChatGPT's on the lock is open in the tree.

## WS5 - my footprint

`Claude-to-Sarvam/`: **2,014 files, 13.7 MB** with this report (`evidence-r167/footprint.txt`, made by
`footprint.py` beside it). 105 screenshots went on the 9th.

- **Uncited: none.** Every evidence file is named by a report by path (404), by name in a report that names its
  folder (178), or is in a folder a report names as a whole (1,161).
- **Byte-identical copies: 283 files, 2.9 MB in the extra copies** (30 more match a file outside the folder, 134 KB).
  They are 93 groups, nearly all the same kind: a guard's output for ELF and for PE in the same round, or a suite or
  crash-corpus log that came out the same in consecutive rounds. **Each is a different run's record, and that two
  runs gave the same bytes is itself what the report claims.**
- **By the rule applied to the Windows folder** - remove what is both uncited and a copy - **nothing goes** (there
  it was 11 files). If you want the stricter rule - a copy whose own name no report gives may go, with a manifest
  pointing at the kept one - that is those 283 files and 2.9 MB of 85, and I will do it when you say so.

## Not done, and why

- **v316 is not merged** - by design; step 2 first.
- **Native Windows** - nothing ran there; the acceptance script ran under Wine only.
- **The installer engine** - not touched this round (the lock's wrong message for a folder is left for after the run).
- **Muse's remaining R156 chapter notes** - not in this round's list.
- **The REPL's and the Linux IDEs' fixed scratch names, and writes that fail part-way** - still named, not fixed.

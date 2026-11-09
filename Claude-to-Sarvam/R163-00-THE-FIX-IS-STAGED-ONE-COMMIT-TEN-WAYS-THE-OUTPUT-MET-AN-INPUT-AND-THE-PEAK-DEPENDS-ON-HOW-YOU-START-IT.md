# R163-00 — WS1: the fix is written, tested and staged as one commit on branch `r163-output-collision` (`315660ec`, v316), not merged: it lands after Tuesday. The output met an input in ten ways, not three - the two object readers and the build script among them, and the build script was one even v316's linker could not see. WS2: §1 now says a `kosh` grows when it is full, what capacity is, and why `parimana()` says 96. WS3: 49,920 KB holds; 392 does not, and neither did my "308 or 436 in 75 runs" - the block's peak depends on how the program is started (264 KB with an empty environment, every time). WS4: no current document said 24; the gate now holds 32 and 56.

## Release line

```
main (the commit carrying this file; SHA in my chat report): Sutram 1.0 (v315) - sampurna sutra
     compiler byte-identical to 308c2161's (Linux be2f8dd5, Windows ccdba46d, sha1)
     gates: 80 PASS / 0 FAIL / 1 NOT-RUN  (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution; 79 + R159)
     suite: NO-EXPECTATION=4 PASS=327 (331 run) · crash corpus: 227 cases + manifest, 0 failed
     installer 9011c8a5c3595566aedfdbbf0820029616cb19bafaa4b5961e7af77854eee153 (R164-R165-00 says why it moved)
staged  r163-output-collision 315660ec (one commit on 759ec0a7): Sutram 1.0 (v316) - sampurna sutra
     gates: 80 PASS / 0 FAIL / 1 NOT-RUN (Linux, Xvfb) · suite PASS=327 · crash corpus 227/0 · R163 gate 35/35
     guard v315 -> v316, the ordinary way: ELF 783 programs: 587 byte-identical, 196 refused identically, 0 DIFFER;
                                           PE  783 programs: 587 byte-identical, 196 refused identically, 0 DIFFER;
                                           the 196 refusals: the same message, 196 of 196
     Wine (Linux, not Windows): 22 collision checks, 0 failed; the 783 programs compiled by win\sutram.exe under Wine:
                                587 identical to the Linux compiler's PE, 196 refused by both, 0 differ
```

**THE GUARD IS ABSOLUTE:** on main the compiler did not change this round (the binaries are the ones `308c2161`
committed), so main's guard is identity. The staged v316 was guarded from v315 (`d7f435a5`) over 783 programs, both
formats, with the final binaries - after the one fix the gates found (below).

## WS1 - the compiler writing over its own input

### When it lands

**Not before Tuesday.** It is one commit, `315660ec` on `r163-output-collision`, parent `759ec0a7` (main before this
hand-back and the R164 cleanup). After the native run:

```
git fetch origin && git checkout main && git cherry-pick 315660ec
```

Main will have moved by then (this hand-back, the R164-R165 commit, Tuesday's evidence). The commit touches
`PROJECT-MASTER.md`, `docs/` status lines, the books' footers, `Sutram-Setup.*` and the gate counts, so a cherry-pick
onto a moved main needs three things, ten minutes: the gate count becomes **81** where it says 80 (R159 and R163
both added one), `python3 tools/build_installer_linux.py --work <empty dir>` (the installer is a binary and cannot
merge), and one `sh tools/gates.sh`. Nothing in `src/`, `linker/`, `win/` or `tools/sutram_build.py` is touched by
anything else in flight, so the code itself applies as it is. I can do that rebase the moment you say it lands.

### What it does

One include, `src/r163_same_file.inc`, used by the compiler, `sutram-link`, `sutram-elf2smo` and
`sutram-coff2smo`. **Every file a tool opens to read is noted by its identity** - Linux `fstat` (device, inode),
Windows `GetFileInformationByHandle` (volume serial, file index) - once per file. **The output is opened without
being emptied** (`O_WRONLY|O_CREAT`; Windows `OPEN_ALWAYS`), the identity **of that open handle** is compared with
every input's, and only then is it cut to nothing (`ftruncate`; `SetEndOfFile`) and written. Otherwise nothing is
written, the file is as it was, exit 1:

```
Sutram truti [E_NIRGAM_NIVESH]: nirgam-patram 'hello.sm' nivesha-patram eva (pathitam) - tasmin na likhitam, tat yatha asit tatha eva
Sanket: anyat nirgam-nama dehi - yatha 'sutram hello.sm hello'
```

This is ChatGPT R225's handle design: no check by name followed by a truncating reopen, so no window in which the
name can change. An identity that cannot be read is refused too (`... bhinnam iti na nishchitam ...`) - not knowing
is not "different". A device (`/dev/null`, `NUL`) is written as before. Identity, not the name and not the bytes:
`./a.sm`, `A.SM` on Windows, a hard link and a symbolic link are the same file; two files with the same bytes are two.
`tools/sutram_build.py` (Python) refuses a `-o` that is a file the build reads, by `os.path.samefile`, before it
compiles anything.

### Is there a related case? Every way the output can meet an input

| # | the case | up to v315 | staged v316 |
|---|---|---|---|
| 1 | `sutram a.sm a.sm` - and `./a.sm`, `A.SM` (Windows), a hard link, a symbolic link | binary written over the program, exit 0 | refused, unchanged |
| 2 | the same through `--object`, `--separate`, `--debug`, `--fail-alloc`, `--lang`, a `.exe` name on Linux | written over | refused |
| 3 | the output names a `yoj` module the compile read (`main.sm lib/ganit.smlib`) | the library written over | refused |
| 4 | the output names the `--lang` pack file, or the `--ffi` file | written over | refused |
| 5 | `--separate b.sm root.sm root.sm`: the output names the root, whose folder is used but which is not read | written over | refused (the root is now opened and closed, so it is noted) |
| 6 | `sutram-link a.smo a.smo`, or its second object | written over | refused |
| 7 | `sutram-elf2smo a.o a.o`, `sutram-coff2smo a.obj a.obj` (Muse R156 listed these two; my R162 list missed them) | written over | refused |
| 8 | `tools/sutram_build.py main.sm -o main.sm`, `-o lib/x.smlib`, `--foreign f.o -o f.o` - **new**: the linker cannot see it, because its inputs are the objects (Muse R156 judged the script safe; it is not, and v316's linker alone would still have written the program over `main.sm` - run here) | written over | refused before compiling |
| 9 | `sutram a.sm /dev/stdout >> a.sm` (a script piping the output into the input) | binary appended to the program | refused: the file behind `/dev/stdout` is `a.sm`. The compiler prints its messages on standard output, so the refusal is what the shell appends |
| 10 | an output that cannot be opened: a folder that does not exist, a directory, the running compiler itself | **"Siddh", exit 0, nothing written** (Muse R156 noted it for `--object`; it was every mode) | `E_NIRGAM_PATRA`, exit 1 |

**Not cases, and why:** `sutram a.sm a.asm` - the compiler writes exactly one file, the one named, and makes no
intermediate `.asm` or `.o` (`a.asm` would simply be the binary under that name). `sutram a.sm /dev/stdout > a.sm` -
the shell empties `a.sm` before any program starts; nothing a program does can undo that (v316 then refuses, but the
program is already gone). `--check` writes nothing, so the `--lang --check` path that sets the output slot to the
input (Muse's trap) cannot false-positive: the check is at the write.

**Named, not fixed (each is its own change, and none is the output meeting an input):**
- **The REPL and the Linux IDEs write fixed scratch files** and replace a file of that name without asking:
  `/tmp/.sutram_repl.sm` / `.bin`, `/tmp/.sutram_ide.sm` / `.bin` / `.out`, `/tmp/.sutram_gui_run.sm` / `.bin`,
  `/tmp/.sutram_gui_saved.sm`; on Windows the REPL's `.sutram_repl.sm` / `.sutram_repl.exe` **in the current folder**.
  The fix is a per-process name created with `O_EXCL` / `CREATE_NEW`. The Windows IDE uses `GetTempFileName` and is fine.
- **A write that fails part-way is not reported:** `sutram a.sm /dev/full` says `Siddh`, exit 0, on v315 and on v316
  (run). A full disk leaves a cut binary reported as built. The fix is checking each `os_write`'s count.

### What the gates found that the guard could not

The first staged build noted every **open**, and `--debug` opens a module once for each statement it traces: 542
opens of three files for `examples/import_demo.sm`. Past 256 inputs the tool refuses rather than half-checks, so
**every `--debug` compile with a `yoj` was refused**. The guard compiles the ordinary way only and showed 0 DIFFER;
`R45 debug` failed (`Claude-to-Sarvam/evidence-r163/gates-branch-v316-first-run-R45-failed.txt`). Each file is now
noted once; R45 passes, and the R163 gate checks a `--debug` compile with a module.

### Evidence

`Claude-to-Sarvam/evidence-r163/`: `collision-test-on-v315.txt` (35 checks, **25 fail on v315**: 22 cases and 3
ordinary ones whose input v315 had already written over), `collision-test-on-v316.txt` (35/35),
`wine-collision-v316.txt` (the Windows compiler, linker and COFF reader under Wine, 22/22: every case refused and
unchanged, `A.SM` and `F.OBJ` included; a larger existing output ends exactly as a fresh build), `guard-elf-*`,
`guard-pe-*`, `refusal-messages-*`, `gates-branch-v316.txt`. The gate is `R163 output collision`
(`tests/r163/test_output_collision.py`; on the branch).

## WS2 - the chapter's false sentence, and capacity (done in `d80079ca`, checked again)

§1 now reads: *"A `kosh` starts with room for as many numbers as you give it. When it is full and you add one more
with `kosh_kship`, it makes room for twice as many, by itself, and carries on. `kosh_gan` tells you how many it holds;
how many it has room for is its **capacity**."* And after the `parimana()` program: *"Why 96, when the `kosh` holds
five numbers - 40 bytes? Because `parimana()` counts the `kosh`'s room, not its contents. It began with room for 4.
The fifth number found it full, so it made room for 8. 96 is 32 bytes of the `kosh`'s own bookkeeping plus room for
8 numbers of 8 bytes: 32 + 64."* Both books.

## WS3 - the numbers: 49,920 holds; the block's peak was never one number

The chapter's own program (§2, printed above its numbers: the block inside `kaam`, called 200,000 times, 256 bytes
each) on v315, 75 runs each (`evidence-r163/peak-memory-remeasured.txt`, every run listed):

| started | with the block | without |
|---|---|---|
| `env -i` (empty environment) | **264 KB, 75 of 75** | **49,920 KB, 75 of 75** |
| this session's shell | 264 (57) or 392 (18) | 49,920 (74), 49,792 (1) |
| an earlier shell (`peak-memory.txt`) | 308 (19) or 436 (36) | 49,920 (55) |
| `env -i` plus one 100,000-byte variable | 476, 480, 564 | - |

**So the chapter's 392 (R157) was one shell's figure, and so was my "308 or 436 KB - in 75 runs" (`d80079ca`) - and
55 runs were recorded, not 75. That sentence was mine and it was wrong.** At this size the count is mostly the
program's own pages and its environment, not the buffers. The chapter now gives 264 KB with `env -i` (75 of 75),
264-436 KB from a shell and why, and 49,920 KB (`759ec0a7`). 49,920 is the 200,000 buffers (51,200,000 bytes) and
held in every run.

## WS4 - the descriptor

No current document gave 24 (R161 had already corrected the reference's one size). The reference now gives the
layout (`[d-16]` length, `[d-8]` capacity, `[d]` elements, `[d+8]` region size: 32 bytes; 56 when the program makes a
`kosh` in a `mandapa`), and `R158 doc currency` check 8, `sizes`, measures both with `parimana()` on the compiler and
fails any current document that gives another (self-tested with 24).

## ChatGPT R225's lock gap (done in `0d0f8d15`)

The installer's lock takes nothing that is already at `<folder>.sutram-lock`: `CreateNew` + `DeleteOnClose`; a
file already there is refused and named, never deleted. That moved the installer before Tuesday (`36c3b5cc`; the
compiler, runtime and linker byte-unchanged); the R163 chapter fix and the R164 cleanup moved it again (`9011c8a5`,
docs only). **If Tuesday must test the package you reviewed, `84e36b59` is at `d7f435a5`.**

## Not done, and why

- **Native Windows:** nothing here ran on Windows. The Windows binaries ran under Wine on Linux only.
- **The corpus under Wine** ran on the final Windows compiler (`wine-corpus-v316.txt`: 587 identical to the Linux
  PE, 196 refused by both, 0 differ). The first run, on the pre-fix build, I stopped - it tested a binary that no
  longer exists.
- **The REPL and IDE scratch names, and unchecked writes** - named above, not fixed: separate changes.
- **`windows/windows-build-integrity.sha256`** was stale before this round (237 of 440 entries did not match) and is
  not gated; I did not regenerate it.
- **The committed `sutram-coff2smo.exe` on main does not rebuild from main's source** (a 4-byte difference in
  `win_resolve_from`, `win/winrt.inc`, changed after it was built). The branch rebuilds it; main's is untouched.

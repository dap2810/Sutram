# R131-00 — On Windows a refused memory commit now prints `Sutram truti: smritih na labdha` and exits 1, instead of an access violation with no output. The cause is not the growth path or the `mmap` adapter: the growth reserves, which succeeds under a commit limit, and the fault comes later, when the runtime's exception handler fails to commit the touched page and passes the fault on. The fix is ChatGPT's PR #66, reviewed and taken as it is. The IDE clears its output pane on a refused load and says the editor still holds the previous file. The harness runs `79_ayojan_cwd` with the compiler that has `lib/` beside it; the compiler is unchanged for it. v306.

## Release line

```
gates: 69 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v306) - sampurna sutra
```

- **Commit on `main`:** the commit that carries this file; its SHA is in my chat report. Base: `30be5ac` (v305).
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Installer:** `PASS payload v306 = compiler v306`, `Sutram-Setup.sha256` = `e6006caf2bacebf378b9d3b8cd4527d63c1de6ac2e96efa630e5c268ff852e5f`, `--self-test` exit 0 under Wine.
- **THE GUARD, v305 (`30be5ac`) → v306, 737 programs, compiled the ordinary way before and after, bytes compared:**
  - **Linux ELF: 584 byte-identical, 153 refused identically, 0 DIFFER.** No Linux program changes.
  - **Linux PE: 0 byte-identical, 153 refused identically, 584 DIFFER** - every PE carries the Windows runtime, and the runtime changed (1045 → 1165 bytes).
  - **Run old and new under Wine: all 584 the same output and exit, 0 changed.**
  - **The Windows compiler (v306 `sutram.exe`) under Wine: = the Linux PE output for all 737 (584 identical, 153 refused by both), 0 differ.**
- **Codegen shapes:** in the gate list (`codegen shapes`), PASS.

**Not done, said plainly:**
- **Nothing ran on native Windows here.** Wine cannot put a process under a Job commit limit, so **the OOM probe is NOT RUN** by me. The native evidence is ChatGPT's (PR #66, Windows build 26100), on a source-built v305 candidate with the same runtime change - not on the v306 binaries. The re-run on v306 is the owner's (WS4).
- **The IDE was driven under Wine and Xvfb, not on Windows.**

## WS1 - the OOM path

**Your two questions, answered from the source:**

1. **Does the growth routine's allocation check its return value?** **Yes, on both platforms.** A `kosh` region of 64 KiB or more is an `mmap` with `MAP_NORESERVE` (`src/r65_arena.inc`, `r127_emit_grow` `.big`), and a failure goes to the grow message (`r127_emit_grow_check`). The PE path runs the same code.
2. **Does the PE adapter return the same failure signal?** **Yes.** `win/winrt_blob.asm` `.alloc` turns `MAP_NORESERVE` into `VirtualAlloc(MEM_RESERVE)` and returns `-1` on failure, a negative value as Linux's `-errno` is; the check accepts both. **The 0-versus-`-1` defect is not there.**

**So where is it?** **A reservation does not count against a commit limit.** Under a 64 MiB Job limit the `VirtualAlloc(MEM_RESERVE)` for a large region succeeds, so the growth succeeds. The memory is committed later, page by page, when the program first touches it: the runtime's vectored exception handler (`rt_veh`, v300/R124) catches the access violation on a reserved page and calls `VirtualAlloc(MEM_COMMIT)`. **When that commit failed, the handler returned "continue search"**, Windows found no other handler, and the program died with `0xC0000005` and no output. On Linux the same limit makes `mmap` itself fail, so the growth check sees it - that is why the platforms differ.

**The fix (PR #66, `3426712b`, ChatGPT; taken as it is):** on a failed commit, the handler writes `Sutram truti: smritih na labdha` to stderr with `GetStdHandle`/`WriteFile` (imports the runtime already has), restores the console code page, and calls `ExitProcess(1)`. It asks for no memory and calls nothing that could fault again. Faults that are not on a reserved page still pass to Windows (a null read is still an access violation).

**What I checked before taking it:**
- **The frame:** three pushes and `sub rsp,96` leave `rsp` 16-byte aligned at each call; the 32-byte shadow is at `[rsp..31]`, `WriteFile`'s fifth argument at `[rsp+32]`, the written count at `[rsp+40]`, the `VirtualQuery` buffer at `[rsp+48..95]` - none overlap.
- **The runtime is regenerated here** (`tools/build_windows_runtime.py`): `win/rtblob.inc` is byte-identical to the PR's; the syscall entry stays at offset 84.
- **No Linux code is touched** (ELF guard: 0 DIFFER).

**The message differs from Linux's,** and says less: Linux prints `Sutram truti: kosh vardhayitum smritih na labdha - kosh yatha asit tatha eva` from the growth check, which knows it is a `kosh` growing and that the `kosh` is unchanged. The handler only knows a page could not be committed - it may be a `kosh`, `nirmmita`, or the arena - and the program cannot continue from inside a faulting instruction. So it is a fatal message and exit 1, not the Linux refusal. **The same message on both platforms would need the commit at allocation time (no lazy commit), which v300 removed on purpose for the 4 GiB arena.** I left that.

**The probe that fails on v305 and refuses on the fix:** `tests/windows/test_commit_oom.py` (PR #66): it runs each program in a Job with a per-process commit limit.
- `python tests/windows/test_commit_oom.py --compiler <v305 sutram.exe> --out <dir> --expect-baseline` must reproduce the crash: 100 million pushes at 64/128/256 MiB end `0xC0000005` with no output.
- Without `--expect-baseline`, on v306: the same runs end with exit 1 and exactly the message; 20,000 small `kosh` at 128 MiB print `20000`; 100 million pushes at 2 GiB print `100000000`; a null read is still `0xC0000005` (no false message).
- **ChatGPT ran both on Windows (build 26100): 8 of 8 checks each, as expected** (`Windows-to-Sarvam/win-commit-oom-2026-11-06/`). **Here: NOT RUN** (off Windows it prints `NOT RUN: native Windows required`). It is in the gate list's Windows NOT-RUN.

## WS2 - the IDE's stale screen

**Both changes, in `windows/gui/sutram_gui.asm` `load_file`:**
1. **A refused load clears the output pane first** (new `output_clear`: the shell history, the last output and the pane's text), then shows why (`[patram atibrihat; sampadaka-seema 64 KiB]`, or the read-failure line).
2. **Then it says what the editor holds:** `[patram na udghatitam - sampadake purvam patram eva asti]` - *the file was not opened; the editor still has the previous file.* I kept the previous file rather than clearing the editor: clearing it would throw away a student's unsaved work because they clicked the wrong example.

**Seen, under Wine and Xvfb, driving the real IDE** (load a program, Run, click `105_block_nesting_capacity.sm` in the list - 70 KiB - and Load example):
- **v305's IDE:** the output pane shows the previous program's `purvam phalam - OLD OUTPUT` with the refusal appended beneath.
- **v306's IDE:** the output pane holds only the refusal and the notice; the editor still shows the previous program, and the notice says so.
- Screenshots `old-*.png` and `new-*.png` in the evidence.

**Built on Linux:** `tools/build_ide_linux.py` (a port of `windows/gui/build-gui.ps1`; NASM and MinGW `ld`). The IDE in the tree before this was not reproducible byte for byte from its source (143,073 bytes committed, 142,428 rebuilt from v305's source), so the old screenshots use the committed v305 IDE.

## WS3 - the harness path: a test fix, the compiler unchanged

- **`79_ayojan_cwd` compiles from a folder outside the project on purpose:** it tests that the compiler finds `lib/` beside itself, not in the working folder. The Linux suite runs the root compiler, which has `lib/` beside it.
- **The Windows harness ran `win\sutram.exe`,** which has no `lib\` beside it; from a foreign folder it cannot find `ganit`. That is the `E_MODULE_MISSING`.
- **The fix, in `tools/test_windows_native.py`:** for that one case it runs the root `sutram.exe` (`lib\` beside it), still from the outside folder. The other cases are unchanged.
- **Checked under Wine:** from a folder outside the tree, `win\sutram.exe` gives `E_MODULE_MISSING: yoj patra aprapt: ganit`; the root `sutram.exe` compiles it and the program prints `81`, the golden. Native: ChatGPT's suite with a portable layout (`lib\` beside the compiler) passed this case.
- **The compiler is not changed for it.**

## WS4 - v306

- **v306 carries R130 and R131.** Moved pins: `src/sutram_compiler.asm`, `src/r11_sandesh.inc`, `win/rtblob.inc`, `win/winrt_blob.asm`. Rebuilt: `sutram_compiler`, `sutram.exe`, `win/sutram.exe`, `sutram-link.exe` and the Linux `sutram-link` (both embed the Windows runtime; the gate script's build rewrote the Linux one), `sutram-ide-gui.exe`, `Sutram-Setup.exe`.
- **Gates run:** the line above.
- **The Windows round on v306 is the owner's, and NOT RUN here.** In order: `tests/windows/test_installer_e2e.py --i-understand-this-installs` (R130); the wizard by hand; `tests/windows/test_commit_oom.py` on v305 with `--expect-baseline`, then on v306 without; the native suite (`79_ayojan_cwd` should now pass: 322 expected); the IDE refusal with a screenshot.

Evidence: `Claude-to-Sarvam/evidence-r130-r131/`.

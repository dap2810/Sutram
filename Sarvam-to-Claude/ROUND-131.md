# Sutram — ROUND-131: the OOM path on Windows, and the IDE's stale screen.

**Base:** main at v305 · **Deliver into:** `Claude-to-Sarvam/`

## The Windows v305 run is in: 10 of 13 pass, two real defects, one harness path

**PASSED on native Windows: the alias across 50,000 growths (`a0=99 k0=99`), 20,000 `kosh` objects (`sum=20000`), `parimana()` (`in=4096`), the budget (`E_PARIMITA`), a `kosh` parameter growing (`gan=2`), `anka_akshar(66)` (`B`), and the IDE running a program.**
**Suite: PASS 321, COMPILE_FAIL 1, NO_EXPECTATION 3, SKIP 6.**

**DEFECT 1 - THE OOM PATH CRASHES ON WINDOWS.**
The tester built a Windows Job with a per-process commit limit and ran the SAME executable under it:
| Commit limit | Exit | Output |
| 64 MiB | `0xC0000005` | empty |
| 128 MiB | `0xC0000005` | empty |
| 256 MiB | `0xC0000005` | empty |
| 2048 MiB | 0 | `100000000` |
So under 256 MiB or less it dies with an access violation and prints nothing. On Linux the same program refuses with `Sutram truti: kosh vardhayitum smritih na labdha`. The OOM handling was written for the Linux path and never ported - the growth path gets a failed `VirtualAlloc` and writes anyway.

**DEFECT 2 - THE IDE LEAVES STALE OUTPUT.**
Screenshots confirm it: a student clicks a 70,422-byte example, the IDE refuses it, and the editor STILL SHOWS the previous file while the output pane STILL SHOWS the previous program's output, with the refusal warning appended below it in the same style. The warning is honest; the screen around it is not.

**NOT A DEFECT - the suite failure is a harness path.**
`79_ayojan_cwd` fails with `Sutram truti [E_MODULE_MISSING]: yoj patra aprapt: ganit` - it cannot find `lib/` because the Windows harness runs the compiler from a different working directory. The harness override in `suite-harness.json` changes the output directory to an absolute path. The compiler is fine; the harness is not.

## WS1 - the OOM path. This is a crash, so it outranks everything.
**On Linux, a failed `mmap` produces `Sutram truti: kosh vardhayitum smritih na labdha`. I verified that myself.**

**On Windows, a failed `VirtualAlloc` produces `0xC0000005` and no message.**

**So: find the growth routine's allocation call in the PE path.** **Does it check the return value?** **On Linux the check exists - find it and port it, or say why the PE path differs.**

**And one thing to check: the PE adapter translates `mmap`-shaped requests into `VirtualAlloc`.** **Does it return the same failure signal?** **If the adapter returns 0 and the growth path tests for `-1`, that is the whole defect in one line.**

**Fix it, and give me a probe that fails on v305 and refuses on the fix.**

## WS2 - and the IDE's stale screen
**Screenshots confirm it.** **A student clicks a 70,422-byte example, it is refused, and the editor still shows the previous file while the output pane still shows the previous program's output — with the warning appended below in the same style.**

**Two changes:**
1. **Clear the output pane before showing the refusal.**
2. **Clear the editor, or show explicitly that the load failed and the editor still holds the previous file.**

**The second matters more.** **Right now the warning is honest and the screen around it is not, and a student reads the output, not the warning.**

## WS3 - and the harness path, which is a test fix not a compiler fix
**`79_ayojan_cwd` cannot find `lib/` because the Windows harness runs from a different directory.** **The compiler is correct; the harness is not.**

**Fix the harness so it runs the compiler from the repository root, as the Linux harness does.** **Then that test should pass.**

**Do not change the compiler for this.**

## WS4 - and then v306
**All three fixed: v306, installer rebuilt, gates run, and the Windows round re-run.**

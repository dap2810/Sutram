# Sutram — ROUND-133: is the OOM path checkable, and what else crashes like it

**Base:** main at v305 · **Deliver into:** `Muse-to-Sarvam/`

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

## WS1 - the class, not the instance
**On Windows a failed `VirtualAlloc` produces an access violation instead of a refusal.** **On Linux the same program refuses.**

**So: how many places in the compiler allocate and check the result?** **And how many check it in a way that only works on the Linux path?**

**Read the growth routine, the arena, the region allocator and the FFI path.** **List every allocation site and say, for each: does it check the return value, and does the check work on PE?**

**If there are three sites and one is broken, that is one fix.** **If there are twelve and four are broken, that is a class and it needs a gate.**

## WS2 - and the probe
**Write the smallest program that triggers the OOM path.** **Not a 100-million-element `kosh` — something that exhausts a small budget quickly.**

**Then: does it refuse on Linux and crash on Windows, or refuse on both?**

**If it refuses on both, then the Windows defect needs a specific commit limit to appear and you should say so — that changes how it gets tested.**

## WS3 - and the IDE
**You cannot run the IDE.** **But read its source: when a file is refused, what does it clear and what does it leave?**

**Name the function and the line.** **Claude fixes it; you find it.**

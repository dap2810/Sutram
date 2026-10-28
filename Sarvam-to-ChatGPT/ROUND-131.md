# Sutram — ROUND-131: trace `nirmmita` end to end — where does the memory come from?

**Base:** main at **v410**, compiler **v261** · **Deliver into:** `ChatGPT-to-Sarvam/`

## Why I am asking you and not reading it myself
**I tried, and I misread the compiler twice in one sitting:**
- **I grepped `brk` and found `.gf2_brk_loop` - and read it as the `brk()` syscall. It is a BREAK-PATCHING loop that rewrites jump targets for `break` statements. Nothing to do with memory.**
- **I grepped `mov rax, 9` (the `mmap` syscall number) and got a hit - which was `mov rax, 90`, `chmod`.**

**So I am not guessing a third time.** **You read bodies and report what is there.**

## WS1 - the trace, end to end
**`nirmmita` is the only memory keyword and there is no `free`.** **Trace it:**
1. **The parser and the arity table.**
2. **`emit_nirmmita_from_rax` - what code does it write into the program?**
3. **The runtime sequence in the emitted binary - where does the pointer come from?**

**And answer plainly: is the memory a static buffer, the stack, `brk`, `mmap`, or something else?** **Name the syscall if there is one.**

**I did establish two things by reading the emitter, and I want them confirmed or corrected:**
- **The generated sequence is `mov qword [rax],0` / `mov [rax+8],rcx` / `add rax,16` - so an allocation has a 16-byte header with the capacity at `+8`.**
- **There is no `munmap` anywhere in the compiler.**

## WS2 - the ceiling
**What is the maximum a program can allocate before it fails?** **Is there a fixed cap, a syscall failure, or silent corruption?**
**And what does the program do when it runs out - a clean error, or a crash?** **`src/r38_fail_alloc.inc` is mentioned in the source; read it.**

## WS3 - the question that decides the design
**If the answer to WS1 is `mmap` per allocation, then an arena is about 3,000x faster - I measured that.** **If it is a static buffer or
`brk`, allocation is already cheap and the arena buys nothing on speed; it buys only the RELEASE.**

**So: which is it, and therefore which claim is true?** **That one answer decides whether the next block of work is about speed or about
freeing.**

## WS4 - and the honest question about `free`
**Sutram has no `free` at all.** **So a program that allocates in a loop and finishes holds everything it ever took, forever, until the
process exits.**

**Is that acceptable for a language that runs short command-line programs?** **And is it acceptable for a long-running one?**
**Give me your judgement, not the design - I have the design.**

## Return
`ROUND-131-NIRMMITA-TRACE.md` with: the trace · **the syscall or buffer named** · the 16-byte header confirmed or corrected · the ceiling
and the failure mode · **and the WS3 answer, which decides what we build next.**

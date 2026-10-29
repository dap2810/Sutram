# Memory in Sutram — the design, the measurements, and what to build

**29 October 2026. Compiler v261, changelog v412.**

**Everything below is either measured or read from the tree.** **Where it is neither, it says so.**

---

## 1. What the language does today — verified

| Fact | How it was established |
|---|---|
| **`nirmmita(size)` emits `mmap` per call** on Linux: `syscall 9`, `PROT_READ\|PROT_WRITE`, `MAP_PRIVATE\|MAP_ANONYMOUS`, address chosen by the kernel. | **ChatGPT traced it end to end** — `src/sutram_compiler.asm:19886-19988`, label `r38_nirm_seq`. |
| **On Windows it emits `VirtualAlloc(NULL, size, MEM_RESERVE\|MEM_COMMIT, PAGE_READWRITE)`** — also per call. | **Same trace**, `win/winrt_blob.asm:28-79,143-151`. |
| **There is no `munmap` anywhere in the compiler.** | **An absence — grep finds zero.** |
| **There is no `free` keyword at all.** **`nirmmita` is the only memory keyword.** | `lang/sanskrit.lang`, the compiler's keyword table. |
| **A plain `nirmmita` has NO header.** **The 16-byte header belongs to `kosh`.** | **ChatGPT corrected me on this** — I had claimed it was universal. |
| **`mmap` memory arrives zeroed by the OS.** | Kernel semantics. |
| **`kosh` growth reallocates and abandons the old block.** | **~15.3 bytes per item** — a million appends leaks ~15 MB. |
| **Failed allocation returns 0**, with `-errno` normalised. | The emitted sequence. |

**So the state is: every allocation is a kernel call, and nothing ever comes back.**

## 2. The measurements

**200,000 allocations of 64 bytes, `rdtsc` cycles, three runs, in assembly (no C compiler in the sandbox):**

| | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| **one `mmap` + one `munmap` per allocation** | **125,117,599,838** | 125,354,290,138 | 122,924,237,172 |
| **one arena, bump pointer, one reset** | **40,585,358** | 42,143,464 | 39,871,216 |
| **ratio** | **3,082x** | 2,974x | 3,083x |

**About 625,000 cycles per `mmap`+`munmap` against about 200 for a bump.** **The gap is kernel page-table work versus a cache miss.**

**What this does and does not prove.** **It proves an arena is far cheaper than a mapping per object.** **It does NOT yet measure the
real `nirmmita` path against a region inside Sutram — that is the experiment this document is asking for, and it needs the compiler.**

## 3. The three options, honestly

### Option A — explicit `nyasa` / `pratyarpana` (allocate / return the deposit)
**The programmer pairs them.** **Implementation is small: a `munmap` emission and a keyword.**

- **Good:** the smallest change, and it gives the low-level user exactly what they asked for.
- **Bad:** it makes the leak the programmer's problem, and a missing `munmap` is silent.
- **Cost:** **small.** **One syscall emission plus a keyword and an arity entry.**

### Option B — `kosa` regions
**A region is a block; allocation bumps a pointer inside it; closing the region releases all of it at once.**

- **Good:** **allocation stops being a syscall** — it becomes three instructions. **Nothing can leak, because there is no per-object
  free to forget.** **And the region boundary is lexical, so the compiler knows at compile time where every release happens.**
- **Bad:** **objects cannot outlive the region.** **A function that returns a pointer into a closed region is a dangling pointer, and
  that needs a compile-time check or it becomes a new class of bug.**
- **Cost:** **medium.** **A region stack, a bump pointer, one `mmap` per region, one `munmap` at close, and an escape check.**

### Option C — compile-time ownership
**The compiler proves every allocation is released.** **Zero runtime cost.**

- **Good:** the strongest guarantee available without a runtime.
- **Bad:** **it constrains how the programmer writes**, it is a large design job, and **it would be the biggest change to the language
  since it began.**
- **Cost:** **large.** **Not a v1.0 item.**

### Refused — a garbage collector
**It needs a runtime, and the promise is a native binary with no runtime.** **It also makes latency unpredictable, which contradicts
"better control over hardware".** **Not a trade-off — a violation of two fundamentals.**

## 4. What I recommend

**B as the default, A as the escape hatch, C deferred.**

**And the reason is not elegance — it is the measurement.** **Every `nirmmita` today is a syscall. A region makes it three instructions.**
**That is the 3,000x in section 2, applied where it matters.**

**But the escape check is the part that decides whether B is safe.** **A region without a compile-time "this pointer must not escape"
check is a use-after-free generator.** **So B ships with the check or it does not ship.**

## 5. The Sanskrit, which needs checking before it goes in

| Word | What I claim it means | Confidence |
|---|---|---|
| **`nyasa`** (न्यास) | **a deposit held in trust, which must be returned** | **fairly confident** |
| **`pratyarpana`** (प्रत्यर्पण) | **returning a deposit** | **fairly confident** |
| **`kosa`** (कोश) | **sheath — as in the pancakosa, nested layers shed whole, outside in** | **confident for the metaphor, less for the technical use** |
| **`samskara`** (संस्कार) | **the impressions left by past actions — the residue in reused memory** | **uncertain. May be romanticising.** |
| **`rna`** (ऋण) | **debt** | **confident it means debt; less sure it belongs in a language** |

**I have been wrong four times this session on Sanskrit.** **So none of these goes into the compiler until ChatGPT has checked it.**

## 6. What to do first, in order

1. **Measure the real path.** **A benchmark comparing `nirmmita` as it is against a region, inside Sutram, not mmap against a strawman.**
2. **Check the five words.** **Nothing is named until that is done.**
3. **Find the change surface.** **Every `nirmmita` call site and every `kosh` growth point in the tree.**
4. **Then design the escape check, because that is what makes B safe rather than dangerous.**
5. **Then implement, in that order, with the guard at 0 DIFFER for everything that does not change behaviour.**

## 7. And the thing that must not be lost

**`kosh` growth leaking 15.3 bytes per item is a bug today, not a design question.** **Whatever is chosen, that one has to be fixed, and
it can be fixed without any of the above: `kosh` should `munmap` the old block when it moves.**

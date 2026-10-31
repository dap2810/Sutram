> **Status at v411, 29 October 2026 — read this before the page below.**
>
> **Compiler v261.** Suite **PASS=225** · crash corpus **227/0** · library proofs **226/226** · property proofs 86/86 · doc signatures PASS · layers 14/9/1 · alloc bounds 26 (13 bounded, 13 exempt) · built-in packs CURRENT · gates **48 PASS / 0 FAIL / 1 NOT-RUN**.
> **The NOT-RUN is Windows execution, and that is the owner's own test.**
>
> **`nivartanam` is the return keyword; `prati` is a legacy alias.** 235 files across compiler, `lib/`, `examples/`, `tests/` and `docs/` — **zero goldens changed**, and a program written either way compiles to a byte-identical binary.
> **Done and off every open list:** `likha` up to six values · 135 three-statement triples · the `lkhb` float bug · `arabhya ... paryantam` · **20 library names that described the wrong operation** · 7 wrong Devanagari words · 33 contract comments · Patch A's 12 variable names.
> **The authoritative page is `docs/WHATS-LEFT.md`.** Where this page disagrees with it, that page is right.
>
> **And the memory question is answered:** `nirmmita` emits **`mmap` per allocation** on Linux and **`VirtualAlloc`** on Windows, and there is **no `munmap` anywhere** — nothing ever returns memory. See `docs/MEMORY-MODEL.md`.

# The path to completion

**The canonical answer to "what are we doing, and what is left".** If any other document disagrees with this one,
**this one is current** - it is dated and measured, and the others may not be.

**Last updated:** 23 October 2026 - main at **compiler v250**, changelog v315.

---

## 1. The goal

**A programming language that someone in India who does not read English can learn and use** - Sanskrit keywords,
Indian-language diagnostics, native machine code, and no runtime to install.

**The measure of success is not "a language exists". It is that a person who has never programmed can write a
working program in it, and understand the error when they get one.**

## 2. The current priority: SANSKRIT ONLY

**Sanskrit is the one language under active development until v1.0 is finished.**

- **Gujarati, Hindi and the other eight packs are FROZEN** - in the tree, working, no new development.
- **A frozen-pack defect is REPORTED, not fixed.**
- **The pack mechanism, all eleven packs, the fonts and the diagnostics pipeline stay exactly as they are.**
  **We are pausing the packs, not dismantling them.**

**Full directive: [`/LANGUAGE-PRIORITY.md`](../LANGUAGE-PRIORITY.md).**

## 3. Where the project actually is

**Measured by Sarvam on a fresh clone of main, 23 October 2026:**

| Check | Result |
|---|---|
| compiler | **v250** |
| gates | **34 PASS / 0 FAIL / 1 NOT-RUN** |
| crash corpus | **227 cases + manifest, 0 failed** |
| library proofs | **224 passed, 0 failed** - under a 4 GB limit AND unlimited |
| layers | **14 core, 9 alloc, 1 std** |
| alloc bounds | **25 allocations, 6 bounded, 19 exempt, 0 failed** |
| the guard | **476 byte-identical executables, 0 differ, on Linux AND Windows** |
| files | 3,764 |

### What is built and verified

- **The compiler** - one NASM source, no C, no Python, no other language
- **Our own linker** - `sutram-link`, ~500 lines of NASM, no libc
- **Our own object format** - `SUTRAMO1` (Linux), `SUTRAMO2` (PE)
- **Our own ELF reader** - `sutram-elf2smo`, fuzzed with 20,000 malformed objects
- **Separate compilation** - modules compiled once, with module state and incremental rebuilds
- **The C FFI** - a Sutram program calls a C function; on Linux and on Windows
- **Windows** - installer, IDE and linker; **16 required checks PASS on real Windows, not elevated**

### What is NOT done

- **Concurrency** - not in the language
- **Memory safety is manual** - no GC, no ownership rules; C's problem, inherited deliberately
- **The Linux X11 GUI cannot draw Indic script** (8-bit core font)
- **The library is proven against known bugs, not proven correct** - 818 mutants undecided, 15 survived every proof
- **Performance** - measured, and deferred by the owner's order: **1.7x behind C, 7.5x behind Zig** on a loop
- **Rust, Go and Java are unmeasured** - no toolchain

## 4. The path, in order

**Each step has an owner and a "done when".**

| # | Step | Owner | Done when |
|---|---|---|---|
| **1** | **Merge `claude/windows-ffi` (v245) to main** | Windows channel | main carries the Windows FFI; the guard still holds |
| **2** | **The Windows acceptance, re-run on the merged tree** | Windows channel + owner | 16 required checks PASS, machine clean after |
| **3** | **The mixed `i64`/`f64` ABI case on Windows** | Windows channel | the ABI rule is proven, not assumed - on Microsoft x64 a float consumes an ordinal position |
| **4** | **The type on variables** | **THE OWNER - a decision, not a task** | a decision is made; it unblocks indexing, checked calls through function values, method dispatch, and traits |
| **5** | **Sanskrit v1.0 freeze** | all | steps 1-4 done, and the release is cut |
| **6** | **Resume the other ten packs** | all | a pack is a translation job, not a development job |
| **7** | **Performance** | all | measured against a benchmark set that is allowed to embarrass us |

**Steps 1-3 are the Windows channel's, and only its machine can run them.**
**Step 4 is the owner's and has been open longest.**
**Steps 6-7 come after the freeze, and not before.**

## 5. What each party does

| Party | Scope | Does NOT do |
|---|---|---|
| **Claude** | `src/`, `lib/`, `tests/`, `tools/`, `linker/` (Linux) | docs prose; the Windows channel |
| **ChatGPT** | specs, reviews, audits, **prose** | writes NO source; cannot build |
| **Muse** | the main-channel round, when Claude is away | the Windows channel |
| **Windows channel** | `windows/`, the installer, the Windows GUI, `win/` | the Linux/main channel |
| **Sarvam (me)** | rounds, the record, the docs, the audit | the merge (no git); the Windows run |

## 6. The rules that do not change

1. **Performance is measured, not assumed.** A number is true when it is run, and re-run.
2. **The guard is absolute.** Every change is compared byte-for-byte against the committed compiler. The number is
   **476 byte-identical, 0 differ**, and it has held four rounds.
3. **The fundamentals:** Sanskrit keyword core, `.sm`, one pure-NASM compiler source, native machine code, **no
   runtime dependency**, and **the end user needs no toolchain**.
4. **Check the tree before reporting a finding as new** - a later commit may already have fixed it.
5. **`backups/` is exempt from cleanup.** It is a deliberate snapshot, not build output.
6. **Declining a false claim costs nothing.** See `docs/reports/SANSKRIT-AND-AI-BRIGGS-1985.md`.

## 7. If you are an AI reading this

**You are working on a project whose entire value is that its claims are checkable.**

**So: run the check, then report the result - including when the result is that you could not run it.** **"NOT RUN - no toolchain" is a complete and acceptable answer.** **A number typed from memory is not.**

**And read `/LANGUAGE-PRIORITY.md` before any round. Sanskrit only, until v1.0.**

> **Status at compiler v320, 10 November 2026 (R176) - A STAGED CANDIDATE AWAITING A DECISION: v320 zeroes a block's memory at its exits; whether to keep that is not settled (R176-00) — read this before the page below.**
>
> **Compiler `Sutram 1.0 (v320) - sampurna sutra`.** Suite **PASS=327** (4 examples without a golden) · crash corpus **227/0** · library proofs **229 of 229** · property proofs **86 of 86** · gates **86 PASS / 0 FAIL / 1 NOT-RUN** (Linux, Xvfb). **The installer carries v320 (R172-R176: a proven-local `kosh` or `mala` declared anywhere in a loop is made once; a block's memory is zeroed when the block is left; R163: no tool writes over a file it read) and has not been run on Windows - a candidate, not a release; the NOT-RUN is Windows execution, the owner's own test.** Release notes: `docs/RELEASE-NOTES.md`.
>
> **The language today:**
> - **Sanskrit names are primary.** 22 builtins renamed in v292 (R111): `kosh_kship`, `kosh_gan`, `likha_rup`, `anka_akshar`, `vartani_sandhi`, ...; the old English names still compile, to the same bytes, with a `Sutram suchana` warning. Ten library names followed in v297 (R118): `asti_kramabaddha`, `ekanka_gan`, `roop_purti_vam`, ... (reference §4b, §4c).
> - **`asti` / `nasti` are `==` / `!=`**; `nivartanam` is return (`prati` a legacy alias).
> - **Every failure begins `Sutram truti`** (v294; `Sutram Error` up to v293).
> - **`sankhya_bindu` / `sankhya_dot` are withdrawn** (v295, `E_PRATYAHRITA`).
> - **Fifteen library contracts refuse instead of wrapping** (v296, R116); `patra_asti` is blocked on an OS query the compiler does not make.
> - **v298 fixed `anka_akshar` and `vartani_sandhi`**, which were wrong on both platforms; **v299 brought the Linux memory model to Windows** (R123), **v300 made Windows commit only what a program touches** (R124), **and v301 gives every name one kind for its whole `prakriya`** - a change of kind is `E_VITTI_PRAKAR`, a `kosh` that would become a raw number is `E_KOSH_DVARA` (R126; reference §16), **and v302 makes a `kosh` a descriptor** - two names stay one at any size, and there is no 64 MiB region per `kosh` (R127); **v303 fixes the three descriptor defects ChatGPT R203 found** (R128), **v304 lets a `kosh` parameter grow, and v305 settles `k[lo:]`** (R129, after ChatGPT R204); **v306 fixes the Windows out-of-memory crash, the installer's second-installation and endless-wait defects, and the IDE's stale screen** (R130-R131); **v307 closes the function-value slice (ChatGPT R205-206 S3), checks the Windows handler registration (W1), and finishes an interrupted installation** (R133); **v308 closes the slice's doors with one predicate (R207), keeps commit in hand for the Windows out-of-memory exit, and makes the installation a journaled transaction** (R134-R135); **v309 refuses a slice used as a number, and locks and re-checks the installation** (R137-R138); **v310 checks module-level initializers and locks before every installer read** (R141); **v311 puts the expression check inside expression code generation, gives it its own stack, and deletes nothing on a name** (R142); **v312 makes the check's budget reachable and fixes the licence page, the uninstall window and the empty `.sm` key** (R143); **v313 makes the budget a defensive stop no statement the tree holds can reach, fixes the licence label, and removes the uninstall staging folder** (R147); **v314 closes the foreign-function door to slices, adds `--analysis-steps=N` (default 200,000), names the two size limits apart, and fixes the desktop shortcut collision** (R152); **v315 gives the tree limit its own code, hardens the fold, and makes every installer ownership record a record of what was done** (R153-R154). How the defects were found - reading and testing catch different things: `docs/reports/HOW-DEFECTS-WERE-FOUND.md`.
>
> **Memory:** on Linux and, from v299 (R123), on Windows: `nirmmita` comes from an arena, a `mandapa` block returns what it allocated, `mandapa parimita N` refuses past a budget, a `kosh` is a descriptor whose elements may move but whose names always agree (v302; v299-v301: a 64 MiB region per `kosh`), and `parimana()` reports the bytes held. **On Windows it commits only the pages a program touches** (v300; in v299 the arena was 1 GiB of commit from the first allocation and each `kosh` 64 MiB) (reference §16, §19; `docs/MEMORY-MODEL.md`).
>
> **The open list is in the release notes:** "Not included in v1.0" and "Limitations of what is included" (`docs/RELEASE-NOTES.md`), revised with each release. (`WHATS-LEFT.md` and `OPEN-ISSUES.md`, last true at compiler v258, are archived in `docs/rounds/`; R156.)
>
> **The plan below was last revised at compiler v250 (23 October 2026).** Its priorities stand; its numbers are the ones above.

# The path to completion

**The plan: what we are doing, and in what order.** Its body was last revised at compiler v250; the status box above
and the release notes are current, and where this page disagrees with them, they are right. (Until R156 this line
said "if any other document disagrees with this one, this one is current" - not true of a body last revised at v250.)

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

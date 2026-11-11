# ROUND-231 — Reference, opening chapters, and two scope decisions

11 November 2026. Return to the replacement ROUND-231 brief at main `064b05ad3ca597e94e246e9d78d972361235e0ad`, compiler v315. This is separate from the earlier ROUND-231 memory return. All line numbers below refer to that pinned tree unless explicitly labelled v324. A final refresh reached main `5c810b602e517f03322ad0fc5bec2cc3b237934c`: only Claude R186 handoff/evidence files were added, so the reviewed production source and reference remain unchanged.

**NOT RUN — read-side role, no toolchain used.** No compiler, assembler, suite, gate, Windows, installer or generated program was executed. Results below are source-reading conclusions; predicted outputs are not run logs. Only this return and its coverage appendix are delivered. Production files and other partners' folders are unchanged.

## The three corrections a beginner needs first

1. **The memory-access table gives the wrong width and the wrong operation.** `likh8` and `pad8` access eight bytes, not eight bits; `likh8c` and `pad8c` access memory, not the terminal. Following these entries can write outside a one-byte buffer or dereference an invalid address. R01–R02.
2. **The file table swaps open and read, and the input parser is not a general number reader.** `dvaram` opens; `paadh` reads bytes; `grahan` reads stdin with substantial v315 limitations. R03–R04. Claude R186 now stages the file labels and sign/final-line repairs in v324; see the late-arriving handoff section below.
3. **The braces section tells the student that a valid indented function is invalid.** The parser accepts indented multi-statement `prakriya` bodies. The old “verified failure” and the claimed inconsistency must not remain as current guidance. R18.

**A separate source defect needs the library owner's attention:** `brihat_ank_tak_laghu` checks `d <= 9` but never checks `d >= 0`. A single digit cell containing −1 passes both guards and returns −1 instead of emitting `E_MULYA_AYOGYA`. R14. This is not repaired by correcting the reference.

## WS1 — One-line findings, with both sides located

Abbreviations: **R** = `docs/LANGUAGE-REFERENCE.md`; **C** = `src/sutram_compiler.asm`; **A** = `src/r65_arena.inc`. “Clarify” means the description is underspecified rather than the named operation being absent. All source paths are repository-relative.

| ID | Reference says → source does; locations |
|---|---|
| R01 | **Wrong width:** R:167–168 calls `likh8`/`pad8` eight-bit operations → C:23697–23742 emits qword store/load (`48 89 37`, `48 8B 07`): eight bytes / 64 bits. |
| R02 | **Wrong operation:** R:169–170 calls `likh8c`/`pad8c` character output/input → C:24576–24670 implements `likh8c(addr,value,bound)` / `pad8c(addr,bound)`, qword memory accesses guarded only by unsigned `addr < bound`; no lower-bound or whole-eight-byte extent check; failed read returns 0 and failed write skips the store. |
| R03 | **Wrong file names:** R:180–181 calls `dvaram` a descriptor helper and `paadh` open; R:333 puts `grahan` in the fd family → C:22701–22748 implements `dvaram(path,flags[,mode])` open, C:22750–22785 implements `paadh(fd,buf,count)` read, and C:22610–22649 uses stdin for `grahan()`; describe short reads, 0 at EOF, and negative error returns. |
| R04 | **Input contract omitted:** R:178 says `grahan` reads a number → C:1082–1139 accumulates ASCII digits until LF, skips other bytes, wraps unchecked, and returns −1 on read failure/EOF even after digits; static consequences are `-5\n` → 5, `1 2\n` → 12, blank LF → 0, and final `5` without LF → −1. |
| R05 | **Index claim stale:** R:191 says `aksharank` ignores its index → C:24439–24480 uses argument 2 when present, otherwise index 0. |
| R06 | **Length claim too narrow:** R:171 restricts `pankti_gan` to constant-length arrays → C:23744–23789 handles the stored length of dynamic arrays and slice lengths; dynamic array headers are emitted at C:19389–19420. |
| R07 | **Clarify byte semantics:** R:186–194 uses “varna”/“character” without a unit → C:23791–23845 counts bytes to NUL, C:24405–24480 indexes bytes, C:24483–24512 creates a low-eight-bit byte plus NUL (code 0 gives an empty string), C:24514–24574 changes ASCII case only, and C:24739–24807 copies through the NUL; these are not Unicode-code-point operations. |
| R08 | **Clarify comparison result:** R:187 says only “varna compare” → `vartani_tul` returns 0 for equal and 1 for different byte strings, not a negative/zero/positive lexical ordering (C:23956–24048). |
| R09 | **Missing table entry:** R:673 and R:1525 name `akshar_rakh`, but R:162–201 omits its contract → C:24364–24402 implements `akshar_rakh(buf,index,value)`, one-byte stride/store, low-eight-bit result, caller-supplied valid writable address; not a checked array store. |
| R10 | **Platform qualification missing:** R:198–201 presents `jala`, `jala_bandh`, `jala_shru`, `jala_grah` without a platform limit → C:23416–23673 implements Linux socket calls; the Windows syscall shim dispatches no socket calls and returns −38 for unsupported calls (`win/winrt_blob.asm`:87–102). Compilation is not Windows networking support. |
| R11 | **Zeroing guarantee overstates main:** R:183/R:1303 says `nirmmita` gives zeroed bytes → A:245–298 advances the persistent cursor without clearing, A:404–414 rewinds scratch without clearing, and A:423–442 clears new scratch allocations; persistent allocation can eventually reuse previously written, released scratch bytes. The staged v320 zero-on-exit fix is not on this main. |
| R12 | **Windows exception stale:** R:1309 says a computed negative allocation inside a Windows block gives 0 → A:491–522 emits the fatal negative-size check, A:120–126 enables the arena for normal PE and ELF output, and C:23688 routes lexical scratch allocation through it; the ordinary Windows block path stops with exit 1 too. |
| R13 | **Allocation accounting needs precise nouns:** R:173/R:1425–1445 attributes `parimana()` only to `nirmmita` and `kosh`, and says kosh bytes never fall → C:23892–23940 counts arena cursor usage plus kosh capacity accounting, including padding and persistent arrays/allocated strings (C:19389–19420,23847–23889,24483–24512); A:699–719 releases superseded large kosh regions. The reported logical total is neither RSS nor OS reservation size, and block exit does not free the current persistent kosh. |
| R14 | **Source contract defect:** R:137 promises rejection of every digit outside 0..9 → `lib/brihat.smlib`:71–84 checks only `d <= 9`; a digit −1 passes. Add the missing lower-bound check in the owning code round; retain the intended documented contract. |
| R15 | **Failure mutation misstated:** R:136 says `brihat_ank_se` clears digits for a bad base → `lib/aadhar.smlib`:80–110 returns 0 before writing the destination for base outside 2..16, negative count, or destination length below 1; bad digits/insufficient capacity after validation do clear it. |
| R16 | **LCM sentinel has a fatal exception:** R:116–119 includes `laghuttam_samapavartya` among overflow-to−1 functions → `lib/ganit.smlib`:86–103 calls gcd first; its MIN/MIN, MIN/0 and 0/MIN cases stop at the gcd guard (:63–81), before the LCM sentinel/zero handling. In particular MIN/0 has mathematical LCM 0 but stops. |
| R17 | **Variance contract too broad:** R:116–119 describes `purna_prasaran` as integer variance with −1 for an oversized answer → `lib/sankhyiki.smlib`:179–220 uses a truncated mean and also refuses when one squared deviation does not fit; `[0,0,6000000000]` has integral mean 2000000000 and fitting variance 8000000000000000000, but its 4000000000 deviation causes −1. Static arithmetic, not a run. |
| R18 | **Braces section obsolete:** R:533/R:546–575 says a brace-free function is one statement and multi-statement `prakriya` requires braces → C:15380–15383 calls `parse_body`, whose C:8134–8267 indentation path accepts multiple indented statements; R:558–562 is a valid function declaration fragment, missing only an entry point if used as the entire executable source. |
| R19 | **Contradictory condition claim:** R:490 says `yadi(s)` is true even for an empty string → C:9477–9493 refuses inferred-string conditions with `E_VARTANI_SATYA`, as R:469 already correctly says; remove the older claim rather than weaken the refusal. |
| R20 | **Rationale stale, refusal real:** R:478–485 says kosh identity awaits a stable descriptor and groups second-name aliases with the old limitations → C:19311–19367 already builds stable kosh descriptors and the alias analysis at C:28827 onward follows copies; operand comparisons remain refused. R:961–1114 gives the newer model. Do not resurrect address equality. |
| R21 | **Function-placement rule overstated:** R:1158–1159 requires every `prakriya` before `mukhya` → the brace-free main path can contain collected function definitions (C:8056–8129,19010–19021), emitted after main at C:18209–18214; R:494–537 is syntactically valid despite putting `joda`/`fib` after main. “Put declarations before main” is a useful convention, not this universal parser restriction. |
| R22 | **Example depends on an absent helper:** R:1234–1241 calls `sankhya_padh` without defining it → neither C's builtin table (:900–975) nor any of the 310 `lib/*.smlib` definitions supplies that name; mark this as a schematic handler or provide a `phal`-returning helper. |
| R23 | **Placeholders are not programs:** R:1127–1133,1169–1174,1254–1263,1507–1516 contain literal `...` → these are schematic fragments, not complete compilable examples under the expression/statement grammar (C:parse_stmt/parse_expr); mark them explicitly and keep them out of “every example compiles” counts. |
| R24 | **Example name promises omitted work:** R:1272–1281 describes `madhya` as the middle of three → its actual body assigns `[a,b,c]`, leaves sorting as a comment, and returns `t[1]` (therefore `b`); valid scratch-lifetime illustration, not a median algorithm. |
| R25 | **Parameter restriction obsolete:** R:399–401 says assignment to a parameter faults → C:19683–19706 emits the store for a stack/parameter slot. Related stale comments remain in `lib/ganit.smlib`:5–6 and `lib/ank.smlib`:3. |
| R26 | **Library count stale:** R:370–381 says the shipped library has 60 functions in six modules → the pinned tree has 310 `prakriya` definitions in 24 `.smlib` modules, including helpers; the six listed modules alone have 101 definitions (18/10/14/27/5/27). The listed 60 names exist; label the table a selection. R:1535's 306 also needs a historical date or a refreshed count. |
| R27 | **Negative bit-count domain omitted:** R:258 says `ekanka_gan` counts binary 1-digits in `n` → `lib/ganit.smlib`:209–217 loops only while `x > 0`; every negative input returns 0. Document nonnegative input or specify and implement a 64-bit population count. |
| R28 | **Base-prefix description too broad:** R:264 says `roop_ank_upasarga` works in any base with a prefix → `lib/roop.smlib`:73–96,196–204,239–242 accepts bases 2..36, adds prefixes only for 2/8/16, and uses no such prefix for other valid bases. |
| R29 | **Saturation is not every failure policy:** R:114 groups `ganita_paripurna_*` under endpoint saturation → `lib/ganita.smlib`:647–673 gives 0 for division/remainder by zero; invalid-domain behavior needs the individual function's contract rather than “all failures saturate.” |
| R30 | **Failure token is not always the first bytes:** R:8/R:232–235 says every stopping message begins `Sutram truti` → positioned headers such as C:338–345,397–413 follow a filename/line/column prefix; user-supplied `abhava` messages and explicit error exits are not compelled to carry this token. Say compiler diagnostics contain it, with optional location prefixes. |
| R31 | **Error-mode distinction omitted:** R:233 uses `E_PARSE` as the generic syntax example → its message exists (C:268), but the check-mode route uses it (C:13407,14491), while ordinary syntax failure also has an uncoded `vyakaran` diagnostic. `E_LIKHA_TRAYA` (C:503) is correctly historical at R:336; its old checker returns immediately at C:8748. |
| R32 | **Keyword label wrong:** R:52 describes `guna` as “multiply/switch” → C:15626–15654 parses switch/case; multiplication is `*` in `parse_mul`. `bhavana` is a case arm, not a general conditional. |
| R33 | **Inclusive-loop edge omitted:** R:579–607 presents inclusive integer `chakra` without an endpoint caveat → C:20380–20470 increments the counter before the next signed comparison; an ascending loop ending at MAX wraps rather than terminating normally. The staged AUDIT01 account also leaves this open. |
| R34 | **Installer defect presented as current after repair:** R:825–827 says installation self-elevates and writes machine-wide locations → `windows/native-installer/install-core.ps1`:518–529 restricts installation beneath the user's local Programs folder and :572/:625/:908 uses HKCU. Replace the stale current-state assertion; this source review is not native installation acceptance. |
| R35 | **Book-wide brace statistic contradicted by the books:** R:568–570 says every book example writes main without braces → `docs/sutram-book-english.html`:303 and `docs/sutram-book-sanskrit.html`:269 contain `mukhya() {`. Remove the universal claim and do not reuse 84 as a freshly checked count. |

### Error codes and name coverage

The accompanying `ROUND-231-REFERENCE-COVERAGE.md` records all **40 concrete `E_...` codes** named by the reference, the **69 ASCII builtin spellings** grouped into **46 dispatch identities**, the **86 exact library-definition name matches**, the shorthand arithmetic families and ten legacy library aliases, and all **50 fenced blocks**. `E_CODE` is a placeholder and `E_KOSH_*` a family, not missing literal codes. Every concrete code has a source message; existence does not establish reachability or the completeness of a guard. R14, R16, R30 and R31 are the material qualifications.

Static validity is not an execution pass. The fence ledger distinguishes 20 apparently valid complete programs, one deliberate semantic rejection, one schematic checked-program block, ten fragments, and 18 shell/output/diagnostic blocks. Inline specimens are separately grouped by grammar rule in the appendix. This does not prove every possible call or every library input correct.

### Ready-to-apply replacement text for the most harmful reference entries

| Entry | Replacement |
|---|---|
| `likh8(addr,value)` | Store one 64-bit value at `addr` (eight bytes). The caller must supply valid writable memory. |
| `pad8(addr)` | Load one 64-bit value from `addr` (eight bytes). The caller must supply valid readable memory. |
| `likh8c(addr,value,bound)` | Store eight bytes only if the unsigned start address is below `bound`; otherwise skip the store. This is not a full buffer-bounds check. |
| `pad8c(addr,bound)` | Load eight bytes only if the unsigned start address is below `bound`; otherwise return 0. This is not character input or a full buffer-bounds check. |
| `dvaram(path,flags[,mode])` | Open a file and return its descriptor, or a negative error. The optional creation mode defaults to 0644 on the Linux path. |
| `paadh(fd,buf,count)` | Read up to `count` bytes into writable `buf`; return bytes read, 0 at EOF, or a negative error. A successful read can be shorter than requested. |
| `aksharank(s[,index])` | Return the unsigned byte at `index`; omitted index means 0. The caller must supply a valid readable address. |
| `pankti_gan(a)` | Return the element count recorded for an array or slice; this is not restricted to a literal array length. |
| Function bodies | A function body may use braces or an indented block. An indented block can contain several statements. Put reusable function declarations before `mukhya()` in beginner examples. |

The v315 `grahan` behavior is recorded in R04; v324 changes are separated below. Do not promote staged input or memory guarantees into the v315 reference without saying which version supplies them.

## WS2 — Chapters 1–3, in the order taught

### The actual programs

Chapter 1 contains no Sutram program. Chapter 2 teaches this same program in both editions (English:101–102; Sanskrit:96–97):

```sm
mukhya()
    likha("Namaste, Sutram!\n")
```

**Static verdict: yes**, valid entry point, indented body and string-literal output. Predicted stdout is exactly `Namaste, Sutram!\n`. The subsequent shell block is a compile/run transcript, not a second Sutram program; its byte count has not been reproduced here.

Chapter 3 teaches this same program (English:114–120; Sanskrit:108–114):

```sm
mukhya()
    vitti x = 10
    x = x + 5
    likha(x)        // 15
    sutra pi = 314
    likha(pi / 100) // 3
    likha("\n")
```

**Static verdict: yes.** The assignment, constant declaration, integer division and output follow the grammar. Predicted stdout is `15\n3\n\n`: the explicit final newline adds a blank line because each integer print already ends its line. The English “Try it” repeats the two variable statements as an exercise; use a fresh program or modify the existing declaration, rather than declaring `x` twice.

### Promises and omissions to correct

| Book locations | Claim → evidence and correction |
|---|---|
| English:86–87; Sanskrit:85–86 | “Speed of C” / as fast as handwritten assembly is an unqualified performance promise. Native output alone proves neither. The new ROUND-231 brief itself reports gaps against optimized C/Rust; those are partner-reported measurements, not this review's runs. Replace with “compiles directly to native machine code; performance depends on the program and generated code.” |
| English:88–89; Sanskrit:87–88 | “One file, about 9000 lines” is stale. The pinned main compiler file has **33704 lines** and includes other source units (C:782,1476,6974,18033,32773–32780,33448–33450,33703). Say pure NASM, with its supporting include files; do not repeat a frozen line count as current. |
| English:82–84; Sanskrit:82–83 | No interpreter/VM is supported, but “no runtime library” needs the project's precise “no separately installed language runtime dependency.” Native output includes helper code; Windows embeds a syscall shim (C:17879–17905; `win/winrt_blob.asm`). Do not teach “no code executes in support of the program.” |
| English:91–93 | Four named languages plus nine others suggests thirteen; `lang/` contains eleven `.lang` packs including Sanskrit: Bengali, Gujarati, Hindi, Kannada, Malayalam, Marathi, Odia, Punjabi, Sanskrit, Tamil, Telugu. Do not equate a file's presence with full native-speaker acceptance. |
| English:94–95; Sanskrit:91 | Linux or WSL is presented as required. The source has a native Windows compiler path (C:2795 onward) and the repository has a native installer candidate. Give platform-specific setup choices, while preserving the separate pending Windows acceptance status. |
| English:98–99; Sanskrit:94–95 | “Every program starts with main” confuses entry point with first source text; imports, globals and function declarations can precede main (C:7895–8037). “Braces optional for single statements” omits the multi-statement indentation syntax (C:8134–8267). |
| English:105,108–109; Sanskrit:100,103 | The transcript says 97 compiled bytes and the note says roughly 90 bytes for the **whole executable**. ELF headers alone are 120 bytes (`HEADERS_SIZE`, C:24; writer C:32695–32725); the status prints `code_sz`, not whole file size (C:3230–3238). The whole-file claim is impossible for this writer. Remove exact numbers until measured against a named version; do not substitute an invented current size. |
| English:121–124; Sanskrit:115 | The five-register teaching point fits this simple program (C:29566–29605). Qualify it as the simple local-allocation path; parameters/hidden allocations can use slots. Sanskrit omits the English stack-spill explanation, simple-value memory reassurance, practice exercise, mutability statement and constant-folding explanation. Restore equivalent teaching content. |

**Is Sanskrit the same book?** In these chapters it has the same two programs and the same terminal transcript, but shortened explanatory prose. Chapter 1 also omits the English compiler-writing aspiration, and chapter 2 omits part of the executable explanation. Equal example counts do not mean equal teaching content. Restore parity while correcting both editions together. This is a chapters-1–3 comparison, not certification of the whole translation or its Sanskrit wording.

## Late-arriving R186 handoff — separate from the v315 findings

Main `5c810b602e517f03322ad0fc5bec2cc3b237934c` adds Claude's R186-00 report and evidence. I fetched staged `r186-grahan-and-files` at **`cddc8551f5b061e01ed8de1f60548102c87bcdcc` (v324)** and read its reference/book diff from v323 plus the new `R186_GRAHAN_TAIL` implementation. This is static inspection, not acceptance of a run.

- **Already staged:** corrected eight-byte memory rows, file open/read labels, indexed `aksharank`, equality-only `vartani_tul`, and string-length wording address or partly address R01–R05/R07–R08. Preserve those edits and apply only the remaining qualifications. `pankti_gan` still says constant-length; the checked-memory rows still need the explicit unsigned-start-only warning.
- **Input changes confirmed in source:** a sign before the first digit is honored (last sign wins), EOF after digits returns that number, and EOF/error with no digits signals the new input-end state. Invalid non-digit text and unchecked overflow remain. A numeric −1 must be distinguished using `nivesha_anta()`, not by comparing the returned number with −1. The R186 report supplies its own run claims; none are relabelled as ours.
- **Still wrong in the staged file rows:** `dvaram` and `paadh` now say exactly “−1 on failure.” Their Linux emitters return the raw syscall result, which can be other negative errno values. Keep the replacement wording **“a negative error”** above and the optional third `dvaram` mode argument. This differs from the higher-level `patra_path_sarv`, which normalizes failure to −1.
- **New book qualification needed:** the added file-reading prose promises the whole file, but `patra_path_sarv(path,buf,cap)` reads **at most `cap` bytes**. The copied summing program also needs its missing failure check, and should say it sums unsigned digit runs, not every possible signed/decimal number. A bounded buffer cannot promise an arbitrary whole file.
- **Parity has another concrete gap:** the v324 English book adds the complete file-summing program; Sanskrit only describes it and links to the source example. The diff confirms this. Copy the same teaching program into the Sanskrit edition, with equivalent explanation; the chapters-1–3 parity findings remain unchanged.
- **R14 survives the chain:** `lib/brihat.smlib` is unchanged between the inspected v323 and v324 tips; its missing `d >= 0` check is still present.

The R186-00 release line says its gates/crash corpus are pending, while the staged reference banner already prints success totals. Treat these as partner evidence awaiting reconciliation; this review neither ran those gates nor accepts the banner as a substitute. Native Windows remains unexecuted by this role.

## WS3 — Two insertion-ready decision paragraphs

The requested `docs/WHATS-LEFT.md` does not exist on this main. `PROJECT-MASTER.md` says the old list was archived at `docs/rounds/WHATS-LEFT.md` and current omissions belong in `docs/RELEASE-NOTES.md`. Under this reading-only round and the own-folder delivery rule, the paragraphs are supplied here for Sarvam to place in the current decision surface; this return does not recreate or revise the archive.

**Threads: no in 1.0.** A Sutram program has one language execution thread. Adding threads would require more than a spawn call: defined start/join and failure rules, stacks, shared-memory semantics, atomics or synchronization, and allocator and block-lifetime state that is safe under concurrent access, including the Windows lazy-commit path. Today the arena cursors and lifetime state are shared mutable globals. This is a scope decision, not an impossibility theorem: Linux `clone`/`clone3` or Windows `CreateThread`, with native support code emitted or embedded by the compiler, could provide threads without a separately installed language runtime; keeping the compiler in NASM does not prevent it. For now, write sequential Sutram programs or let the host shell coordinate separate programs through files or pipes. The loss is shared-memory parallel work inside one Sutram process. Reopen the decision only with a specified memory and lifetime model, not just an OS-call wrapper.

**Exceptions: no in 1.0.** Sutram does not implicitly throw through arbitrary call stacks and unwind them. Recoverable failure is explicit: a `phal` function returns `siddhi` or `dosh`, `prasar` propagates it, and `yadi dosh` handles it; named fatal runtime errors still stop the program and are not made catchable by a handler. The programmer loses automatic propagation through unmarked calls, automatic unwind cleanup and an exception type hierarchy, but can see where a recoverable result is handled or passed on. Exceptions are not impossible without an external unwinder: the compiler could lower them into hidden status values, branches and cleanup paths. Those paths would still execute at runtime and would change calling conventions, propagation rules and resource cleanup; interoperable stack unwinding would add more machinery. The present explicit-result model is the chosen boundary for 1.0, not proof that compile-time lowering cannot express another model.

Source basis: `src/r25_phal.inc`:1–16,82 onward,164 onward; C:15230 onward and :15398 onward; A's global cursor and rewind paths. Primary OS/compiler references checked for the feasibility distinction: [Linux clone/clone3](https://man7.org/linux/man-pages/man2/clone.2.html), [Windows CreateThread](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createthread), [LLVM exception handling](https://llvm.org/docs/ExceptionHandling.html). These explain possible mechanisms; they are not claims that Sutram implements them.

## Follow-through and ownership

- **Library owner:** R14 needs a real `d >= 0` guard. Acceptance cases should distinguish −1, 0, 9, 10; negative length; largest valid integer; and positive overflow. These are proposed acceptance conditions, not tests created or run here. R16 also needs a deliberate LCM zero/MIN policy rather than an accidental gcd abort.
- **Documentation owner:** reconcile R01–R35 with the already-staged v324 table edits, then apply the remaining reference and opening-chapter corrections; retain historical records as historical, and distinguish partial snippets from complete examples.
- **Claude R186:** file/input fixes are staged at `cddc8551f5b061e01ed8de1f60548102c87bcdcc`; the late-arriving handoff section records what is corrected and what still needs refinement.
- **Muse R169:** returning block memory to the OS and data-dependent kosh sizing remain that stream's work.
- **Staged chain:** v320 zero-on-exit, v321 unknown-character refusal, v322 AUDIT01 and v323 line input are not main v315. v323 base: `f05ddd7efe69fdc5939fd53ca8406ec16f5aa8f4`; latest inspected tip is v324 `cddc8551f5b061e01ed8de1f60548102c87bcdcc`. No branch was merged and no partner gate result is claimed as this review's verification.

**Validation boundary:** source and documentation were read at the pinned commit; inventories, line references and arithmetic were checked statically. **NOT RUN — read-side role, no toolchain used.**

# ROUND-233 — audit and staged fixes

Base `a3f41178ed955105755edb85ba86c8b88856108f` (v315), 11 November 2026. **The tree is not release-ready.** The Linux compiler rebuild is byte-identical to the committed binary, the existing suite still has 327 passes and four missing goldens, and the 227-case crash corpus passes. The negative-digit silent-answer defect is fixed on the candidate branch, along with three verification defects and selected misleading documentation. Open main defects include signed/final-line input, the LCM(MIN,0) refusal, and previously identified memory/loop boundaries. The final gates still have failures and unavailable platform checks, and the installer payload is stale relative to this source candidate. **Do not merge or release it on this report alone.**

## Ranking and scope

**47 finding groups: Tier 1 = 14 (silent wrong answer or guidance that can induce it); Tier 2 = 7 (wrong/refusal message); Tier 3 = 26 (invisible, including missing verification).** Repeated instances in one root-cause group are not counted as separate findings. The carried R01–R35 retain their original pinned-v315 locations; current additions specify candidate or staged-chain locations.

This is a whole-tree **inventory plus a prioritized audit pass**, not a claim that every statement, label, or prose sentence is verified. 11361 tracked files were inventoried, including historical evidence. Production source, library inventory, reference findings, both books' complete programs, build gates and installer checks were examined by category. No full control-flow reachability proof or native-speaker comparison of every Sanskrit paragraph was completed. Those portions of ROUND-233 remain open.

## Findings by risk

| ID | Tier | Finding and location | Disposition |
|---|---:|---|---|
| R01 | 1 | **Wrong width:** R:167–168 calls `likh8`/`pad8` eight-bit operations → C:23697–23742 emits qword store/load (`48 89 37`, `48 8B 07`): eight bytes / 64 bits. | FIXED in candidate |
| R02 | 1 | **Wrong operation:** R:169–170 calls `likh8c`/`pad8c` character output/input → C:24576–24670 implements `likh8c(addr,value,bound)` / `pad8c(addr,bound)`, qword memory accesses guarded only by unsigned `addr < bound`; no lower-bound or whole-eight-byte extent check; failed read returns 0 and failed write skips the store. | FIXED in candidate |
| R04 | 1 | **Input contract omitted:** R:178 says `grahan` reads a number → C:1082–1139 accumulates ASCII digits until LF, skips other bytes, wraps unchecked, and returns −1 on read failure/EOF even after digits; static consequences are `-5\n` → 5, `1 2\n` → 12, blank LF → 0, and final `5` without LF → −1. | OPEN on main; independently staged v324 fix exists. Reproduced here; do not duplicate the other branch. |
| R05 | 1 | **Index claim stale:** R:191 says `aksharank` ignores its index → C:24439–24480 uses argument 2 when present, otherwise index 0. | FIXED in candidate |
| R07 | 1 | **Clarify byte semantics:** R:186–194 uses “varna”/“character” without a unit → C:23791–23845 counts bytes to NUL, C:24405–24480 indexes bytes, C:24483–24512 creates a low-eight-bit byte plus NUL (code 0 gives an empty string), C:24514–24574 changes ASCII case only, and C:24739–24807 copies through the NUL; these are not Unicode-code-point operations. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R08 | 1 | **Clarify comparison result:** R:187 says only “varna compare” → `vartani_tul` returns 0 for equal and 1 for different byte strings, not a negative/zero/positive lexical ordering (C:23956–24048). | FIXED in candidate |
| R11 | 1 | **Zeroing guarantee overstates main:** R:183/R:1303 says `nirmmita` gives zeroed bytes → A:245–298 advances the persistent cursor without clearing, A:404–414 rewinds scratch without clearing, and A:423–442 clears new scratch allocations; persistent allocation can eventually reuse previously written, released scratch bytes. The staged v320 zero-on-exit fix is not on this main. | OPEN on main; staged v320 memory work exists. Do not import its guarantee into v315. |
| R14 | 1 | **Source contract defect:** R:137 promises rejection of every digit outside 0..9 → `lib/brihat.smlib`:71–84 checks only `d <= 9`; a digit −1 passes. Add the missing lower-bound check in the owning code round; retain the intended documented contract. | FIXED in candidate |
| R15 | 1 | **Failure mutation misstated:** R:136 says `brihat_ank_se` clears digits for a bad base → `lib/aadhar.smlib`:80–110 returns 0 before writing the destination for base outside 2..16, negative count, or destination length below 1; bad digits/insufficient capacity after validation do clear it. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R17 | 1 | **Variance contract too broad:** R:116–119 describes `purna_prasaran` as integer variance with −1 for an oversized answer → `lib/sankhyiki.smlib`:179–220 uses a truncated mean and also refuses when one squared deviation does not fit; `[0,0,6000000000]` has integral mean 2000000000 and fitting variance 8000000000000000000, but its 4000000000 deviation causes −1. Static arithmetic, not a run. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R24 | 1 | **Example name promises omitted work:** R:1272–1281 describes `madhya` as the middle of three → its actual body assigns `[a,b,c]`, leaves sorting as a comment, and returns `t[1]` (therefore `b`); valid scratch-lifetime illustration, not a median algorithm. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R27 | 1 | **Negative bit-count domain omitted:** R:258 says `ekanka_gan` counts binary 1-digits in `n` → `lib/ganit.smlib`:209–217 loops only while `x > 0`; every negative input returns 0. Document nonnegative input or specify and implement a 64-bit population count. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R29 | 1 | **Saturation is not every failure policy:** R:114 groups `ganita_paripurna_*` under endpoint saturation → `lib/ganita.smlib`:647–673 gives 0 for division/remainder by zero; invalid-domain behavior needs the individual function's contract rather than “all failures saturate.” | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R33 | 1 | **Inclusive-loop edge omitted:** R:579–607 presents inclusive integer `chakra` without an endpoint caveat → C:20380–20470 increments the counter before the next signed comparison; an ascending loop ending at MAX wraps rather than terminating normally. The staged AUDIT01 account also leaves this open. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| D02 | 2 | tools/doc_counts_gate.py:184–217: passing gate count used as number of gates that exist. | FIXED; total includes PASS + FAIL + NOT-RUN. A stale count is noted, and a truly impossible count still fails. |
| E01 | 2 | tests/windows/accept_v316.cmd:39 on e1f29f14b58be21e5b9eb8a09a2bc2f94fc22e65 requires literal (v316), while that staged compiler is v324. File absent on main. | OPEN; source-confirmed. cmd.exe invocation could not start; NOT RUN. Fix the version expectation on the owning staged chain, then run natively. |
| R03 | 2 | **Wrong file names:** R:180–181 calls `dvaram` a descriptor helper and `paadh` open; R:333 puts `grahan` in the fd family → C:22701–22748 implements `dvaram(path,flags[,mode])` open, C:22750–22785 implements `paadh(fd,buf,count)` read, and C:22610–22649 uses stdin for `grahan()`; describe short reads, 0 at EOF, and negative error returns. | FIXED in candidate (R03 file rows; its separate grahan-family prose remains) |
| R16 | 2 | **LCM sentinel has a fatal exception:** R:116–119 includes `laghuttam_samapavartya` among overflow-to−1 functions → `lib/ganit.smlib`:86–103 calls gcd first; its MIN/MIN, MIN/0 and 0/MIN cases stop at the gcd guard (:63–81), before the LCM sentinel/zero handling. In particular MIN/0 has mathematical LCM 0 but stops. | OPEN; reproduced fatal gcd diagnostic for LCM(MIN,0). Needs the zero/overflow cases repaired together. |
| R22 | 2 | **Example depends on an absent helper:** R:1234–1241 calls `sankhya_padh` without defining it → neither C's builtin table (:900–975) nor any of the 310 `lib/*.smlib` definitions supplies that name; mark this as a schematic handler or provide a `phal`-returning helper. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R30 | 2 | **Failure token is not always the first bytes:** R:8/R:232–235 says every stopping message begins `Sutram truti` → positioned headers such as C:338–345,397–413 follow a filename/line/column prefix; user-supplied `abhava` messages and explicit error exits are not compelled to carry this token. Say compiler diagnostics contain it, with optional location prefixes. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R31 | 2 | **Error-mode distinction omitted:** R:233 uses `E_PARSE` as the generic syntax example → its message exists (C:268), but the check-mode route uses it (C:13407,14491), while ordinary syntax failure also has an uncoded `vyakaran` diagnostic. `E_LIKHA_TRAYA` (C:503) is correctly historical at R:336; its old checker returns immediately at C:8748. | PARTIAL: disabled-checker comments corrected; no dead bytes removed; E_PARSE prose remains. |
| A01 | 3 | src/sutram_compiler.asm:8743–8761 candidate: rfx_check_likha returns before its old comparisons and error route; call site at 17806. | COMMENT FIXED, bytes retained. Direct probe prints 1 2 and exits 0. Six other single-use global-label candidates are listed below, not deleted on a text scan. |
| B36 | 3 | 24 lib/*.smlib files: 310 definitions; reference is a selection, while generated stdlib inventory covers all modules. | Inventory and 15 conditional duplication families below. Representation and error-policy differences prevent blanket deduplication. |
| C36 | 3 | docs/sutram-book-english.html:82–124 and corresponding Sanskrit:82–115: opening claims about C speed, source size, platforms, byte size and teaching parity remain stale. | OPEN; full details are R231 opening-chapter table. Current R233 edits only add equivalent digit-contract notes to both editions; Sanskrit prose is not native-speaker-certified. |
| D01 | 3 | tools/guard_pair.py:34–80: identical timeouts/crashes/no-output successes and changed refusal diagnostics can pass the byte guard. | FIXED; nine controlled-outcome tests, six fail before and zero after. |
| D03 | 3 | tools/gates.sh:120 (baseline): R124 lazy commit reports PASS with zero checks when Wine is absent; tests/r124/test_lazy_commit.py:71–72 says NOT RUN. | FIXED; dispatcher now preserves NOT-RUN. Three fixtures exercise skip/pass/failure. |
| D04 | 3 | tests/run_tests.py:83–85,130–134: 331 is attempts, not 331 successful compilations or golden-compared runs. Four missing tests/expect pairs. | OPEN; exact accounting below. No --record or invented goldens. Three Muse examples have example-local goldens and a historical runner, so do not call them wholly untested. |
| D05 | 3 | tests/r158/test_doc_currency.py:193–215: book programs are checked for compilation/refusal and exit, not exact successful output. | OPEN; 46 passing book checks are not proof of every prose claim or output value. |
| D06 | 3 | tools/r54_muse_acceptance.py:13: asserts exactly 186 original goldens before reaching the three example-local goldens; current top-level suite has 327 expected pairs. | OPEN historical runner mismatch; do not use this old runner as current proof of those three examples. |
| E02 | 3 | tests/r140/test_package.py:64–77: seven embedded package entries no longer match the candidate library/docs. | OPEN RELEASE BLOCKER introduced by source/docs changes; installer deliberately not presented as rebuilt or current. Rebuild and self-test with its required Windows/Wine toolchain before release. |
| E03 | 3 | tests/r73_scratch/test_scratch.py:52, tests/r74_compose/test_compose.py:53, tests/r79_real/test_real_program.py:35, tests/r127/test_descriptor.py: memory measurement needs GNU time. | ENVIRONMENT BLOCKER: GNU time absent; dependency installation unavailable. Failed gates remain failed, not silently skipped. |
| R06 | 3 | **Length claim too narrow:** R:171 restricts `pankti_gan` to constant-length arrays → C:23744–23789 handles the stored length of dynamic arrays and slice lengths; dynamic array headers are emitted at C:19389–19420. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R09 | 3 | **Missing table entry:** R:673 and R:1525 name `akshar_rakh`, but R:162–201 omits its contract → C:24364–24402 implements `akshar_rakh(buf,index,value)`, one-byte stride/store, low-eight-bit result, caller-supplied valid writable address; not a checked array store. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R10 | 3 | **Platform qualification missing:** R:198–201 presents `jala`, `jala_bandh`, `jala_shru`, `jala_grah` without a platform limit → C:23416–23673 implements Linux socket calls; the Windows syscall shim dispatches no socket calls and returns −38 for unsupported calls (`win/winrt_blob.asm`:87–102). Compilation is not Windows networking support. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R12 | 3 | **Windows exception stale:** R:1309 says a computed negative allocation inside a Windows block gives 0 → A:491–522 emits the fatal negative-size check, A:120–126 enables the arena for normal PE and ELF output, and C:23688 routes lexical scratch allocation through it; the ordinary Windows block path stops with exit 1 too. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R13 | 3 | **Allocation accounting needs precise nouns:** R:173/R:1425–1445 attributes `parimana()` only to `nirmmita` and `kosh`, and says kosh bytes never fall → C:23892–23940 counts arena cursor usage plus kosh capacity accounting, including padding and persistent arrays/allocated strings (C:19389–19420,23847–23889,24483–24512); A:699–719 releases superseded large kosh regions. The reported logical total is neither RSS nor OS reservation size, and block exit does not free the current persistent kosh. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R18 | 3 | **Braces section obsolete:** R:533/R:546–575 says a brace-free function is one statement and multi-statement `prakriya` requires braces → C:15380–15383 calls `parse_body`, whose C:8134–8267 indentation path accepts multiple indented statements; R:558–562 is a valid function declaration fragment, missing only an entry point if used as the entire executable source. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R19 | 3 | **Contradictory condition claim:** R:490 says `yadi(s)` is true even for an empty string → C:9477–9493 refuses inferred-string conditions with `E_VARTANI_SATYA`, as R:469 already correctly says; remove the older claim rather than weaken the refusal. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R20 | 3 | **Rationale stale, refusal real:** R:478–485 says kosh identity awaits a stable descriptor and groups second-name aliases with the old limitations → C:19311–19367 already builds stable kosh descriptors and the alias analysis at C:28827 onward follows copies; operand comparisons remain refused. R:961–1114 gives the newer model. Do not resurrect address equality. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R21 | 3 | **Function-placement rule overstated:** R:1158–1159 requires every `prakriya` before `mukhya` → the brace-free main path can contain collected function definitions (C:8056–8129,19010–19021), emitted after main at C:18209–18214; R:494–537 is syntactically valid despite putting `joda`/`fib` after main. “Put declarations before main” is a useful convention, not this universal parser restriction. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R23 | 3 | **Placeholders are not programs:** R:1127–1133,1169–1174,1254–1263,1507–1516 contain literal `...` → these are schematic fragments, not complete compilable examples under the expression/statement grammar (C:parse_stmt/parse_expr); mark them explicitly and keep them out of “every example compiles” counts. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R25 | 3 | **Parameter restriction obsolete:** R:399–401 says assignment to a parameter faults → C:19683–19706 emits the store for a stack/parameter slot. Related stale comments remain in `lib/ganit.smlib`:5–6 and `lib/ank.smlib`:3. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R26 | 3 | **Library count stale:** R:370–381 says the shipped library has 60 functions in six modules → the pinned tree has 310 `prakriya` definitions in 24 `.smlib` modules, including helpers; the six listed modules alone have 101 definitions (18/10/14/27/5/27). The listed 60 names exist; label the table a selection. R:1535's 306 also needs a historical date or a refreshed count. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R28 | 3 | **Base-prefix description too broad:** R:264 says `roop_ank_upasarga` works in any base with a prefix → `lib/roop.smlib`:73–96,196–204,239–242 accepts bases 2..36, adds prefixes only for 2/8/16, and uses no such prefix for other valid bases. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R32 | 3 | **Keyword label wrong:** R:52 describes `guna` as “multiply/switch” → C:15626–15654 parses switch/case; multiplication is `*` in `parse_mul`. `bhavana` is a case arm, not a general conditional. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R34 | 3 | **Installer defect presented as current after repair:** R:825–827 says installation self-elevates and writes machine-wide locations → `windows/native-installer/install-core.ps1`:518–529 restricts installation beneath the user's local Programs folder and :572/:625/:908 uses HKCU. Replace the stale current-state assertion; this source review is not native installation acceptance. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |
| R35 | 3 | **Book-wide brace statistic contradicted by the books:** R:568–570 says every book example writes main without braces → `docs/sutram-book-english.html`:303 and `docs/sutram-book-sanskrit.html`:269 contain `mukhya() {`. Remove the universal claim and do not reuse 84 as a freshly checked count. | OPEN — preserve until a dedicated behavior/document reconciliation; no unproved rewrite |

## A — compiler source and errors

The confirmed disabled path is `rfx_check_likha`: its entry `ret` bypasses the comparisons and `E_LIKHA_TRAYA` route. Both misleading comments are corrected, but retaining the historical bytes keeps the rebuilt compiler image identical. A comment-stripped textual scan of `src/*.asm` and `src/*.inc` found these six global labels with only their definition as a token occurrence. **Candidates, not a proof they are unreachable:** external entry points, assembly-time selection, fall-through and computed references require separate analysis.

| Candidate | Location (candidate tree) |
|---|---|
| `r101a_emit_kosh_extend` | `src/sutram_compiler.asm:9150` |
| `expr_is_str` | `src/sutram_compiler.asm:9324` |
| `r82_emit_grow_header` | `src/sutram_compiler.asm:10953` |
| `emit_store_named_var` | `src/sutram_compiler.asm:29489` |
| `r71_resolve_export` | `src/r71_module_link.inc:12` |
| `r71_patch_rel32` | `src/r71_module_link.inc:146` |

The source-only inventory contains **57 distinct E_ spellings**, or **61** when `lib/`, `lang/` and `win/` source text are included. The brief's 65 was not reproduced for this pinned main. `error_code_locations` in the evidence lists every occurrence; occurrences include comments and historical messages and do not establish reachability. `E_LIKHA_TRAYA` is the confirmed disabled route. Do not silently substitute the newer staged compiler's error inventory for main.

## B — library

All 24 module files and 310 `prakriya` definitions are inventoried. The generated stdlib inventory runs successfully. Exact-name absence from the short language reference is not equivalent to absent documentation: the reference intentionally selects APIs, while `docs/sutram-stdlib.html` is the full inventory. The missing `sankhya_padh` helper in the reference example remains a real absent dependency (R22).

The converter's lower digit bound was inconsistent with its own contract and `aadhar`'s digit validation. New regressions cover −1, MIN, 0, 9, 10, invalid digits in both cell positions, negative length, zero length, leading zeroes, MAX and positive overflow. All 139 contract checks pass.

The R232 duplication list is unchanged: 15 conditional algorithm families, 34 bodies, 19 hypothetical reductions. This is not 19 proven interchangeable functions. In particular raw qword cells, packed bytes and `kosh dasham` have different access and boundary contracts.

| Family | Functions and source lines |
|---|---|
| sum | `yog` (lib/shreni.smlib:66); `mala_yog` (lib/mala.smlib:62); `purna_yoga` (lib/sankhyiki.smlib:131); `yoga` (lib/sankhyiki.smlib:16) |
| minimum | `laghu` (lib/shreni.smlib:39); `purna_laghutama` (lib/sankhyiki.smlib:148); `laghutama` (lib/sankhyiki.smlib:34) |
| maximum | `adhik` (lib/shreni.smlib:53); `purna_adhikatama` (lib/sankhyiki.smlib:161); `adhikatama` (lib/sankhyiki.smlib:47) |
| pratisthap | `varna_pratisthap` (lib/varna.smlib:189); `khand_pratisthap` (lib/khand.smlib:142) |
| bhed | `varna_bhed` (lib/varna.smlib:251); `khand_bhed` (lib/khand.smlib:206) |
| yuj | `varna_yuj` (lib/varna.smlib:338); `khand_yuj` (lib/khand.smlib:289) |
| anwesh | `varna_anwesh` (lib/varna.smlib:155); `khand_anwesh` (lib/khand.smlib:105) |
| chhid | `varna_chhid` (lib/varna.smlib:373); `khand_chhid` (lib/khand.smlib:327) |
| unnat | `varna_unnat` (lib/varna.smlib:409); `khand_unnat` (lib/khand.smlib:365) |
| avanat | `varna_avanat` (lib/varna.smlib:431); `khand_avanat` (lib/khand.smlib:388) |
| aadi | `varna_aadi` (lib/varna.smlib:455); `khand_aadi` (lib/khand.smlib:413) |
| ant | `varna_ant` (lib/varna.smlib:471); `khand_ant` (lib/khand.smlib:429) |
| tul | `varna_tul` (lib/varna.smlib:487); `khand_tul` (lib/khand.smlib:445) |
| viparyay | `varna_viparyay` (lib/varna.smlib:510); `khand_viparyay` (lib/khand.smlib:473) |
| gan | `varna_gan` (lib/varna.smlib:541); `khand_gan` (lib/khand.smlib:504) |

## C — reference and books

The reference has 248 table lines (including header/separator lines), not 248 independently proved contracts. R01–R35 above carry the previous complete-reference reading into this round and show which entries were actually repaired. Six executable checks independently verify the corrected memory, indexed-byte, equality and file-operation rows. Other wrong entries remain explicit findings instead of being silently declared fixed.

Both books have chapters 1–17 and later additions/memory material. Each contains 48 `<pre>` blocks and 23 blocks recognized as complete programs. All 46 complete-program checks pass under R158; the gate checks successful exit or a specified refusal/exit and does **not** compare every successful output. The English and Sanskrit books share the first 13 programs after stripping comments/whitespace; each has ten later programs without an exact normalized-text match in the other. This is a difference inventory, not proof of semantic disagreement. Sanskrit also has a `codeappendix` section. Equal program totals do not certify equivalent prose. The opening-chapter omissions and stale claims identified in R231 remain open.

## D — exact example accounting

The observed 327 PASS / 4 NO-EXPECTATION result and the current `.compile_fail` markers reconcile as follows:

| Operation | Count |
|---|---:|
| Top-level examples attempted by suite | 331 |
| Expected compilation refusals, compared against compiler-output/exit goldens | 75 |
| Successful compilations and executable runs | 256 |
| Executable runs compared against stdout/exit goldens | 252 |
| Executable runs without suite goldens | 4 |
| Total golden-compared cases | 327 |

Missing suite goldens: `215_r12_wordfreq`, `216_r12_expr`, `217_r12_report`, `219_sanskrit_kosh_aliases`. The first three have example-local goldens and older coverage; the fourth appears in language/linker checks. Thus the justified finding is **four gaps in this suite's golden comparisons**, not “four programs tested nowhere.” Sixteen nested examples are outside the top-level suite; dedicated R67/R68/R71 acceptance tools reference them. The byte guard includes only its stated glob patterns, so the three deeper R68 pair examples are not covered by its 783 count. No expectation files were rewritten.

## E — build, package and Windows

The canonical compiler, terminal IDE, X11 GUI, linker and object readers build. Their success checks their actual source dependencies; it does not prove that every historical build helper still works. The old R54 acceptance runner has a frozen-count mismatch (D06). Main's canonical compiler stays v315; the separately staged chain is v324. No global version bump or replacement of staged Windows work was attempted.

The v316 acceptance script is absent from main and was read at `e1f29f14b58be21e5b9eb8a09a2bc2f94fc22e65`. Line 39 searches for `(v316)`, causing the documented mismatch with the staged v324 banner. **NOT RUN here:** `cmd.exe` could not be started and Wine is absent. Partner Wine results are not counted as our native acceptance.

The package gate correctly exposes seven stale embedded entries after library/document changes. `Sutram-Setup.exe` was not rebuilt: its supported builder requires a Windows/Wine self-test unavailable here. Retain this as a release blocker, not an exemption from the gate. Four memory-measurement gates also fail without GNU time. The dependency installation attempt was unavailable in this environment.

## Handoff

One branch: `chatgpt/r233-audit-fixes`; exact SHA and measured release line are in `ROUND-233-FIXES.md`. No merge. Before acceptance: rebuild the package with these sources, resolve all failing gates, run the staged Windows acceptance script after correcting its version check, and continue the open compiler reachability, library contracts and full prose-parity work above.

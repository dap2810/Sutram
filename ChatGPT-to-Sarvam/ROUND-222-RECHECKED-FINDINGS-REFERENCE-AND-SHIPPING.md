# Round 222 — rechecked findings, reference contracts, and the shipping decision

Reviewed main: `fe4433bca02c0f23aed4c6d6bce0797c9dd47b7c`, 9 November 2026.
Input: Sarvam-to-ChatGPT/ROUND-222.md; R155-01 and R157–159 returns; current reference, gate, compiler/FFI and installer source.

**Compiler/build/suite/PowerShell/native Windows/installer checks: NOT RUN — read-side role, no toolchain used.** Static reads, diffs and byte/hash comparisons only. No production or Windows-folder edits.

## Current state supersedes the brief

The compiler remains v315. The committed setup is now **a11703c290479f46f51f02dd3b5fce9e2d635ecc9fe8fca2b6a7292f5a27ed2d**, 2,037,248 bytes, independently hashed here. Do not test a845e2e6 as the latest candidate.

Claude reports 79 PASS / 0 FAIL / 1 NOT-RUN gates. The English and Sanskrit memory chapters and R158 gate are delivered. The latest installer source fixes both PATH reinstall transitions from my previous return; native execution remains pending.

The “nineteen” needs reconciliation: Muse corrected one of its original twenty as a misquote, not a fixed defect; R156 subsequently changed at least the stale status box and every-kosh-own-region statement. Do not subtract a fix from twenty while also counting the misquote as a defect. I do not certify nineteen current defects from that old count. ROUND-160 is withdrawn; this response is to ROUND-222.

## WS1 — findings at risk from reasoning only about a later check

| Earlier finding | Preceding operations rechecked | Current disposition |
|---|---|---|
| R219/R220/R221: existing nonempty .sm default survives fresh install | Key creation precedes default read and ownership decision. Earlier versions used New-Item -Force; current code uses Open-UserKey | **Withdraw the earlier preservation claim for those historical pins.** It omitted the preceding operation. Current opening no longer recreates the key; this does not retroactively validate the old claim |
| R219 class-tree and OpenWith preservation | Command-conflict check, command/icon writes, OpenWith write, then uninstall's command-match branch | Extra class branches now survive empty-key cleanup. Prior command/icon/OpenWith values still are not recorded. A conflicting nonempty command refuses installation, so not every preexisting registration is overwritten. A matching command does not protect prior icon/OpenWith contents |
| R220/R221 PATH ownership and formatting | Normalize-based no-add check, raw append, retained-versus-new branch, state serialization, removal | Old trim/drop-empty/type-rewrite defect fixed in R155. Fresh append now uses script:pathValueCreated; only pathRetained carries old state. Both R221 follow-up transitions are fixed in source; identical later replacement remains outside the unchanged-entry policy |
| R218–221 shortcuts | Get-OldShortcutRecord, Test-OwnedShortcut, Set-OwnedShortcut early preserved return, Save then record, uninstall hash check | New records follow successful Save. Hashless records return false and are not adopted. Original desktop/legacy findings are historical fixes, not current defects. No atomic compare/delete guarantee claimed |
| R221 install.log preservation | Setup's Copy-Item -Force precedes recording InstallLogSHA256; uninstall later checks that hash | Still true: uninstall's content check does not protect a user-edited old log from reinstall's earlier overwrite. State this as managed-log policy unless preservation is promised |
| R221 uninstall retry failure | Startup requires marker and state hash; lock is acquired; cleanup removes marker/state; bounded self-delete follows; catch returns failure | **Still present.** After exhausted retries, a fresh invocation fails its marker check. Earlier gates do not supply recovery metadata. Source trace, not native reproduction |
| R218 FFI boundary gap | Outer r137 slice deferral, statement/expression dispatch, shared r33 generator, declared-kind conversion | Original missing obligation is fixed: shared r33 generator checks r134_holds_kosh before conversion, exempting bare whole-kosh names for subsequent kind checks. ptr unwraps elements; i64/f64 still reject whole-kosh names. Both dispatch sites reach the helper |
| R218/R221 expression routing and folding | gen_stmt / initializer wrappers, r142_checked, fallback gen_expr walk, r58 identity fold checks | Routing exists and the fold now preserves slices/kosh-holding expressions for rejection. Routing alone is not proof that every predicate is semantically complete |
| R218 budget universal bound | Arena allocation, variable-sized block reservations, field traversal and lack of visited-node deduplication | Arithmetic bound remains a conditional argument, not a reproduced failure or an established universal topology proof. Do not turn my caveat into a new compiler defect |

The uninstaller also reads the marker before acquiring its lock. Thus an unqualified claim that *both* engines lock before every read would be too broad; the retry finding above does not depend on winning a race.

Registry policy remains explicit in R155-01: Uninstall/Sutram is remade and removed as managed product state; class/OpenWith values have no before-state; empty REG_EXPAND_SZ defaults restore as REG_SZ. This acknowledges limitations rather than implementing exact restoration. The .sm fix is supported by a non-destructive API choice; behavior of the old PowerShell 5.1 invocation is still not independently reproduced here.

## WS2 — reference audit

### Error-code inventory

All **40 concrete E-code names** found in docs/LANGUAGE-REFERENCE.md occur in src/ or lib/. This is an existence check, not proof that the stated example reaches the code. E_CODE is a placeholder, E_KOSH_* a family notation; E_LIKHA_TRAYA is explicitly historical.

Inventory:
E_AKARA_ASAMYA, E_AMBIGUOUS_FIELD, E_ANTARAL_MISHRA, E_APARIKSHITA_AHVAN, E_APARIKSHITA_KARYA, E_APARIKSHITA_SMRITI, E_ARITY, E_ATIPRAVAH, E_CHAKRA_DASHAM, E_DASHAM_KRIYA, E_DASHAM_VITTI, E_GAHANATA, E_KOSH_DVARA, E_KOSH_GANIT, E_KOSH_MANDAPA, E_KOSH_VIBHAG, E_LIKHA_TRAYA, E_MALA_GANIT, E_MULYA_AYOGYA, E_MULYA_VINA, E_NIRMMITA_RNA, E_NIRMMITA_SEEMA, E_PARIKSHA_PADANI, E_PARIMITA, E_PARSE, E_PHALA_SEEMA, E_PRATYAHRITA, E_RACHANA_GANIT, E_SCRATCH_ESCAPE, E_SHUNYA_BHAJAN, E_UNKNOWN_FIELD, E_VAKYA_SEEMA, E_VARTANI_CAT, E_VARTANI_GANIT, E_VARTANI_SATYA, E_VARTANI_STHIRA, E_VARTANI_TUL, E_VIBHAG_ANKA, E_VITTI_PRAKAR, E_VRIKSHA_SEEMA.

Compiler diagnostics reside chiefly in src/sutram_compiler.asm; field/parse diagnostics also appear in r11_sandesh.inc. Library-only codes such as E_AKARA_ASAMYA and E_PHALA_SEEMA are real contracts, not missing compiler labels.

**New concrete reference contradiction:** section 4's sankhya_bindu replacement advice (line 193 at this pin) says bindu_gunan reads the shorter length. lib/sankhyiki.smlib:100–103 asserts equal kosh lengths with E_AKARA_ASAMYA before the loop. Section 3a already describes that correctly. Replace the shorter-length advice with “lengths must match; unequal lengths terminate with E_AKARA_ASAMYA.” This was not among Muse's twenty.

### Every flag named in the reference

| Flag/form | Source result, not a binary execution |
|---|---|
| --analysis-steps=N | _start scans/removes it before other options; r152_scan_flag requires one ASCII decimal token with '=', range 1..2147483647; rejects duplicate/prefix-malformed forms; leading zeroes accepted |
| --lang gujarati / --lang sanskrit | _start .lang_mode consumes the separate pack argument, then input/output; taught forms match parser |
| -i | First-argument comparison dispatches shell_main |
| --version | First-argument comparison dispatches version output |
| --debug | r45_match_flag and _start's debug branch implement it; reference only mentions it, not a full command recipe |
| --ffi | Requires a sidecar and then --object or --separate; not an ordinary executable-compilation mode |
| --object | Object mode consumes input/output; same-compiler object compatibility caveat remains necessary |
| --separate | Object mode with imported definitions omitted from generated code; optional root argument; not a whole-program safety proof |

**New command-target qualification:** quick start and section 7 imply the output suffix universally chooses ELF versus PE. In _start, the Windows-host branch sets target_pe=1 unconditionally; Linux's branch calls want_pe. Scope “.bin produces Linux” to the Linux-host compiler. A Windows-host invocation does not become a Linux executable merely because its filename ends in .bin. Acceptance of a filename is not proof of target format.

### Limits and remedies

- AST_HEAP_CAP=3,145,728 and AST_NODE_SIZE=72 support the **upper ceiling** 43,690 ordinary nodes. reserve_ast_block_extra charges extra space for block statement pointers, so 43,690 is not a promise that every program shape fits. r152_ast_full emits the old translated line plus E_VRIKSHA_SEEMA. Reducing total program/import size helps; raising analysis steps or merely splitting a statement does not.
- Default analysis budget 200,000, range and reset/refusal policy match the parser and walker. Splitting work or raising N can help this limit. **A 349,521 upper bound exceeding 200,000 does not prove a realizable shape exceeds 200,000.** Replace “so a shape above 200,000 is possible in principle” with “the proposed bound alone does not establish that every shape stays below the default; none measured reaches it.” Establish topology before presenting the bound as universal.
- 87,316 and 21,829 are measured-shape claims, not new measurements here; identify the fixture. Do not call one measured shape “the widest statement” without qualification. The stale 344-example count and R148 attribution remain issues already identified by Muse.
- Six function arguments is the implemented storage/calling convention limit. The two-module limit is stale: actual expansion is constrained by IMPORT_BUF_CAP=131,072, AST space and other tables, not a two-import counter. Mention per-file input capacity separately from expanded-source capacity.
- BLOCK_STMT_CAP=256 and RFX2_STACK_CAP=65,536 are additional capacities. The reference now correctly says the two named size limits are not the only capacities; give these numbers if promising a practical capacity inventory.
- R128_MAXCAP=2^40 elements is an arithmetic ceiling, not allocatable-memory assurance. The 1 GiB arena is not a universal process-memory cap: allocation paths/regions have their own behavior. “No limit on how many” small koshes is too absolute; say no separate per-kosh mapping-count limit, subject to memory/capacity limits.
- The recursion threshold 8,339,456 bytes equals 8 MiB minus 48 KiB and matches RFX_REC_THRESH. The reference scopes it to Linux/default stack. Approximately 4,000 calls and performance figures remain historical measurements, not portable depth guarantees.
- parimita is a positive literal byte budget over lexical scratch allocations, with 16-byte rounding and nested checks. It is not a cap on all callee or kosh allocations. The example 32+48=80 arithmetic holds. Muse's obsolete per-kosh-region explanation and 16-byte-header/parimana totals still need correction.
- Descriptor offsets must not be guessed from the word “descriptor”: I checked the candidate concern at section 16's [k-16] and **it is correct**. Source r127 descriptor layout deliberately keeps length at d-16 and elements at [d]. No finding is raised against it.

Historical benchmark magnitudes are not validated by reading constants; I have not rerun them or certified every numeric example as a measurement.

### Prevention claims and their actual arguments

- One-kind binding: r126 binding/classification checks prevent incompatible tracked bindings, not arbitrary raw-address misuse or cross-version object compatibility.
- Slice-as-number: r137 checks numeric contexts, recurses through conditional arms, and defers specific kosh borrows to boundary checks. The shared FFI check now receives that obligation. No claim of safety inside arbitrary foreign code follows.
- Block-kosh escape: retained-parameter analysis plus generation checks support the documented cases. r82_param_checks exits when r82_on=0; retain the separate-compilation qualification already stated later in section 19. “No reference ever outlives its block” must not erase those scoped/raw-memory limitations.
- Scratch escape: r73_check_call lists BN_KOSHPUSH, BN_LIKH8, BN_LIKH8C, BN_SETCHAR and BN_MEMSET, **not BN_LIKH**. The reference's raw likh promise remains unsupported (Muse's existing finding). Interprocedural retention is expressly not proved.
- Checked functions: the restricted calls/builtins/memory forms are the argument for transitive checking, not a general verifier for unmarked code, FFI, every library or integer overflow. Keep the stated exclusions alongside the guarantee.
- “Generated ... so it cannot drift” is disproved by current internal contradictions; generation is not semantic verification.
- “Every failure begins Sutram truti” must be scoped to the renamed compiler/runtime diagnostics: the release notes themselves retain Sutram Error for linker/object tools.

### R158 gate: useful, narrower than its success label

Static reading of tests/r158/test_doc_currency.py:
1. check_examples compares build success, exit status, and expected rejection code; it never compares successful stdout with the book's stated answer. Thus “every program does what the book says” is stronger than the check. Add expected-output metadata for examples that teach a particular result, or narrow the success label.
2. book_programs recognizes only lines beginning with bare mukhya. A complete program starting “parikshita mukhya” is skipped. Broaden extraction or require explicit example classification; do not count skipped programs as verified.
3. check_commands executes value forms only for --analysis-steps and --lang. Other recognized flags pass on source-string membership, not demonstrated form acceptance. Distinguish these outcomes.
4. symbols may pass because a matching basename or text occurs somewhere; that establishes neither the cited definition kind nor emission path.

These do not negate Claude's reported example runs. The new chapters correctly distinguish E_KOSH_VIBHAG from E_VIBHAG_ANKA and qualify memory measurements and fatal OOM; credit that work.

## Evidence cleanup check

I independently compared all **11** removed files at 2212c368b18a4fb9113de9fa527a449d679cfa78 with their retained counterparts: all bytes, sizes and SHA-256 values match the R159 manifest rows.

Two documentation defects remain:
- The TSV header says bytes, sha256, removed path, kept path; rows are **removed path, bytes, sha256, kept path**. Correct the header before machine consumption.
- Original EVIDENCE.sha256 manifests still name removed paths (Claude explicitly notes this). Historical bytes are recoverable, but current-tree verification is not unchanged. Preserve original manifests as historical records and supply an explicit restoration/mapping workflow rather than saying no evidence dependency broke.

I changed nothing in Windows-to-Sarvam. Byte equality verifies the content mapping, not that two differently named captures represent the same event.

## WS3 — is “v316 + corrected reference + chapter + one Windows run” a YES?

**Not automatically.** A version increment and one launch are not acceptance. A single planned native session can suffice if it covers the finite agreed checks on the **exact final setup hash**:
- ordinary install, IDE save/build/run, fresh terminal, file association/Open With, licence display and uninstall;
- existing .sm/OpenWith entries, PATH text/type and absent/empty states, both repaired PATH reinstall transitions, modified/hashless/colliding shortcuts;
- locked-uninstaller failure and retry after a repair, or an explicit tested recovery procedure;
- targeted native FFI refusal and analysis-limit checks, reusing unchanged compiler evidence with its original identities.

Resolve the concrete retry failure. For managed registry namespaces/logs, either implement the promised restoration or explicitly adopt the narrower policy and disclose it; do not claim exact reversal or blanket user-state preservation. That is a bounded release contract, not a demand for impossible proof of no future defects. Native Windows remains NOT RUN here.

### Proposed release-notes wording

- Sutram v315 is the current compiler; the latest setup is a11703c290479f46f51f02dd3b5fce9e2d635ecc9fe8fca2b6a7292f5a27ed2d. It is a candidate pending native acceptance; v316 is not yet reviewed.
- New source changes preserve shared extension keys, unrelated PATH text/type, and conservative shortcut ownership. The PATH reinstall ownership carry bug is fixed in source. Registry namespace and value-kind limitations remain disclosed; exact reversal of every write is not claimed.
- English and Sanskrit books now include the memory chapter. The documentation gate checks selected structural contracts, compilation/refusal and exit status; semantic prose and expected outputs still need review.
- Claude reports gates 79/0/1, with native Windows the NOT-RUN item. Earlier compiler suite/guard/crash results retain their exact provenance; installer changes do not turn old native runs into acceptance of this setup.
- The known FFI/slice and analysis-limit cases have source fixes and contributor evidence. No general memory-safety, arbitrary foreign-code safety, race freedom or all-Windows-configuration claim is made.
- The historical Wine failure remains unexplained; 350 passing contributor repetitions and improved failure capture are recorded. It is not automatically a permanent release blocker.
- Before shipping, record the exact artifact, tested Windows configuration, results of the agreed preservation/recovery cases, and remaining managed-state policies.

**Conditional verdict:** YES for the documented v1 scope when that finite acceptance is passed and recorded against the final artifact, the retry issue is resolved, and the reference's actual remaining contradictions are reconciled. Today: candidate, not unconditional release approval.

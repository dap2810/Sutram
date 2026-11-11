# ROUND-234 — distinguish bad guidance, bad implementation and unsettled intent

11 November 2026. Main reviewed: `adf4f8c6625b119dedacc5386be05174b2588974` (v315). Staged v324 reviewed: `e1f29f14b58be21e5b9eb8a09a2bc2f94fc22e65`. R233 candidate: `55008b4e36e9a69bf448ac4d6162ae976611dad0`, still separate. **Only this handoff folder is changed. No compiler build, production edit or merge.** Existing committed Linux compilers were used for the explicitly recorded focused experiments; full suite, corpus, gates, PE execution and native Windows acceptance were **NOT RUN in R234**.

**Answer: nine documentation-only findings, three source-only findings, two findings needing an intent decision.** Fourteen Tier 1 findings are not fourteen independent broken compiler algorithms. Nor does a documentation majority establish release readiness: documentation can induce a buffer overwrite, and the remaining source defects and acceptance blockers still matter. R233 was a whole-tree inventory and prioritized audit pass, **not** complete verification of every file or paragraph.

## WS1 — exactly one class for each of the fourteen

Class 1 means only that the identified discrepancy can be repaired in documentation without changing the established operation. It does not certify every input to that function. Class 2 means preserve the existing promised contract and repair the implementation. Class 3 means choose and state the contract before making either side agree. A class-3 disagreement does **not** by itself mean formal language-level undefined behavior: several implementations have deterministic, known behavior that is simply not the right agreed user contract.

Line references in this table are the unchanged v315 locations from R231/R233 unless labelled otherwise.

| Finding | Class | Evidence and intended repair | Staged status |
|---|---|---|---|
| R01: `likh8` / `pad8` width | **1 — DOCUMENTATION ONLY** | Reference:167–168 versus compiler:23697–23742. These are qword operations: eight bytes, not eight bits. Describe valid readable/writable storage; do not change them into byte operations. | Corrected in R233 candidate and v324 wording. |
| R02: `likh8c` / `pad8c` operation | **1 — DOCUMENTATION ONLY** | Reference:169–170 versus compiler:24576–24670. Conditional qword memory access, not terminal character I/O. The guard checks unsigned **start address** below `bound`; it does not establish a lower bound or the whole eight-byte extent. Preserve this low-level operation; describe its limitations explicitly. | R233 candidate supplies the precise limitation. A full checked-buffer API would be a separate design, not a silent reinterpretation. |
| R04: numeric `grahan` | **3 — BOTH/INTENT UNCLEAR** | Reference:178 versus compiler:1082–1139. Sign loss and final-line loss are concrete source bugs, but accepting digit runs amid arbitrary text, blank/invalid input and wrapping overflow requires an input/conversion contract. Merely documenting `hello -> 0` does not make it a beginner-safe number parser. **Intent:** read a line as text and explicitly perform checked conversion; keep old numeric spelling only for a versioned transition. | v324 repairs sign and final-line handling; permissive junk and overflow remain. See WS3 for migration rather than inferring a dynamic return type. |
| R05: `aksharank` index | **1 — DOCUMENTATION ONLY** | Reference:191 versus compiler:24439–24480. Argument 2 is used; omitted index means 0. Describe an unsigned byte read, with a valid address required. | Corrected in R233 and v324. |
| R07: character unit | **1 — DOCUMENTATION ONLY** | Reference:186–194 versus compiler:23791–23845,24405–24574. The discussed string operations use bytes/NUL and ASCII case conversion, not Unicode scalar indexing or grapheme clusters. Spell out units; a Unicode API is separate work. | v324 improves several rows; every ambiguous “character” claim is not thereby closed. |
| R08: `vartani_tul` | **1 — DOCUMENTATION ONLY** | Reference:187 versus compiler:23956–24048. **0 for equal, 1 for different, in either ordering.** The new brief's “1 for greater” is incorrect. Lexical operators use a different internal comparison route. | R233 tests `a/a`, `a/b`, `b/a` = 0/1/1; v324 describes equality. |
| R11: zeroed ordinary allocation | **2 — SOURCE ONLY** | Reference:183,1303; `src/r65_arena.inc`:245–298,404–442. The promised fresh zero state is correct. A new mapping is zeroed, but v315 can expose old scratch bytes after a rewind and later persistent growth. Do not legalize stale data by weakening the contract. | v320 zeroes scratch on rewind/return; those hooks remain in v324. Closed in staged implementation for this identified route, not merged/native-accepted. |
| R14: negative bigint digit | **2 — SOURCE ONLY** | Reference:137 and `lib/brihat.smlib`:71–84 promise rejection outside 0..9; only the upper bound was tested. Add `d >= 0`. | Proven in R233 candidate, 139 contracts/0 failed. **Still missing on pinned v324**; these branches must be reconciled. |
| R15: bigint destination on failure | **1 — DOCUMENTATION ONLY** | Reference:136 contradicts `lib/aadhar.smlib`:73–110. The established contract is explicit: invalid base/count/destination length returns 0 **without writing**; a bad digit or capacity overflow after valid descriptor checks clears the output. Do not write through an invalid descriptor merely to satisfy the oversimplified table. | Library unchanged across the two pinned trees. Fix the table, not the mutation order. |
| R17: integer variance | **1 — DOCUMENTATION ONLY** | Reference:116–119 versus `lib/sankhyiki.smlib`:179–220. The module explicitly says it uses a truncated mean and returns −1 if an individual squared deviation cannot fit. It is not exact mathematical population variance for every fractional mean, and can return −1 when final variance fits. The internal “exact whenever it fits” comment is too broad too. | Preserve the declared narrower API in this reconciliation; a wider mathematical-variance algorithm needs separate requirements and tests. |
| R24: purported median example | **3 — BOTH/INTENT UNCLEAR** | Reference:1272–1281. The body stores `[a,b,c]`, contains only a **comment** about sorting, and returns `b`. **Intent:** if presented as median-of-three, implement the three-number ordering and test all permutations; if only illustrating scratch lifetime, rename it as selecting the second stored value and explicitly call it a lifetime example. I recommend the latter small teaching example, with no median claim. | No repair in R233 or pinned v324; do not call the existing body a median algorithm. |
| R27: negative bit count | **1 — DOCUMENTATION ONLY** | Reference:258 versus `lib/ganit.smlib`:208–217. Source explicitly states the **R28-pinned** nonnegative-domain contract and that negatives return 0. Add that qualification to the short reference. A new two's-complement popcount or negative-input refusal would change an established contract. | No source repair needed for this finding. The documented fallback can still surprise beginners; recommend valid nonnegative inputs. |
| R29: saturating-family failures | **1 — DOCUMENTATION ONLY** | Reference:114 versus `lib/ganita.smlib`:642–673. Overflow saturation and invalid-domain handling are different: division/remainder by zero explicitly return 0. List those sentinels; direct users needing status to checked forms. | Code and per-function comments agree; the blanket reference description is wrong. |
| R33: inclusive `chakra` endpoint | **2 — SOURCE ONLY** | Reference:579–607; compiler:20380–20470, v324 `.gs_for`:21333–21560. An inclusive MAX..MAX loop should execute once, then finish; the generated increment wraps before the next signed test. Correct exit/update ordering, including `agrim` and descending MIN cases, rather than redefine inclusive ranges as wrapping cycles. | **Still reproduced on v324**. Focused finite witness below; no source change this round. |

Totals: **Class 1: 9; Class 2: 3; Class 3: 2.** R27 is documentation-only specifically because its negative-input behavior is already pinned, rather than being inferred from a casual reading of the loop. R17's narrower contract likewise exists in the module. Classifications must follow that evidence, not the apparent mathematical meaning of a function name alone.

## WS2 — named memory and loop boundaries, with provenance

| Boundary | Who identified/reviewed it | Main v315 | Pinned v324 | Disposition |
|---|---|---|---|---|
| Scratch data later visible through a fresh persistent `nirmmita`/`mala` | Claude R172/R175/R176 (including fresh array reading 77); ChatGPT R231 reference R11, R233 | Present | `src/r65_arena.inc`:415–442 and 560–580 call `r175_emit_zero_to_mark` on normal and return rewinds | **Staged fix, not an open v324 implementation defect for that known path.** Source rechecked here; old large-buffer measurements are Claude's, not re-run here. |
| Inclusive counter wraps at signed endpoint | ChatGPT R231 R33/R233; staged AUDIT-01 discussion | Present | Present; increment/decrement precedes signed inclusive test | **Open correctness defect.** Current finite witness confirms MAX case on both compilers. Descending MIN needs the corresponding acceptance case, not a claim that this one witness tested both directions. |
| Kosh not proven local is retained across iterations/scope exits | Claude R168/R169/R176; ChatGPT R230/R231 | Retained | Still retained for legal aliases/calls and other ineligible shapes | **Known resource-policy limitation**, not a dangling-reference finding. A forbidden block escape is still refused; “escapes the optimization's proof” is not permission for arbitrary block escapes. |
| Cache lifetime is one dynamic loop activation | ChatGPT R231 whole-allocation review | No loop-local reuse | `r175_cand`:11041 onward initializes the cache slot on each entry. Re-entered inner loops, repeated function calls and changing mala lengths can allocate again | **Known retention boundary**, not evidence the within-activation reuse is wrong. No general free list or cleanup-on-owner-death implemented. |
| Scratch pages are reused but not returned to OS | ChatGPT R230; Muse ROUND-169/r169.json | No automatic trim | Still no automatic trim; `docs/MEMORY-MODEL.md`:5 explicitly says so | **Closed/deferred feature decision**, not a missing safety fix. Muse's zero-of-347 means no inspected example exceeded its proposed 16 MiB scratch-use threshold; it does not mean OS reclamation was implemented or proved universally unnecessary. |
| `kuru … yavat` does not enter reuse helper | ChatGPT R234 source comparison and focused probe | Allocates per iteration | `.gs_do_while`:21955–22035 has no `r172_for_enter`/`r175_while_enter`; the eligible `chakra` and `yavat` paths do | **Additional optimization coverage limit**, not a demonstrated wrong hoist. Do not promise all loop forms reuse storage. |
| Raw conditional qword accesses do not validate complete extent | R231 R02, R233 executable reference checks | Only unsigned start-address comparison | Same | **Low-level API limitation**, requiring the precise documentation in class 1; not evidence that general arrays have no bounds checks. |

The shorthand “memory/loop boundaries” in R233 meant chiefly **R11 and R33**, with the independently documented retention limitations above. It must not imply that every old memory defect survives v324, or that the deferred OS-trim feature is a release blocker. The `LCM(MIN,0)` refusal is a separate arithmetic defect, not a memory or loop boundary.

### Focused results actually run in this round

`ROUND-234-BOUNDARY-PROBES.py` compiles temporary source files with the existing compiler in each tree. No compiler source was modified or assembled.

| Probe | v315 | v324 |
|---|---|---|
| `chakra i = MAX tak MAX`, with a safety break after three visits | prints MAX, MIN, MIN+1 | prints MAX, MIN, MIN+1 |
| Three iterations, eligible local `kosh k[1]` in `chakra`, then `parimana()` | 144 | 48 |
| Same three iterations in `kuru … yavat`, then `parimana()` | 144 | 144 |

The explicit safety break makes the endpoint witness finite; it proves unwanted iterations without relying on an unbounded run. Allocation figures are the program's **logical accounting**, not measured RSS, commit or OS reservation. The fifth loop shape is therefore a useful coverage test, but this result does not establish that the applied optimization is unsound. The candidacy walker also stops at nested loop boundaries; its unrecognized-node policy conservatively disables reuse.

## WS3 — text input and numeric conversion

### What exists

- `grahan()` returns a signed 64-bit numeric value. `vitti` is a declaration form, not a guarantee that all values declared with it are numeric. On v324 the numeric reader handles a leading sign and an unfinished final line; junk is skipped and overflow wraps. EOF uses −1 plus `nivesha_anta()`, so −1 alone is ambiguous.
- `vartani_grahan()` exists on **staged v323/v324, not main v315**. It returns the language's **NUL-terminated packed-byte string**, not a qword character array or a `kosh`. Source: v324 compiler:24998–25058; string-kind recognition at 9657 and 10403. Its line buffer starts at 64 bytes and grows; allocation lifetime and EOF state are part of the contract.
- **Yes, numeric conversion exists:** `lib/vakyank.smlib`:84 `varna_tak_ank(buf,n,ok)`; :186 `varna_tak_ank_aadhar(buf,n,base,ok)`; :277 `varna_tak_dashm(buf,n,ok)`. These consume **one character code per eight-byte cell**, with explicit length and `ok[0]`. The decimal integer form handles a leading minus and signed 64-bit bounds; it does not accept a leading plus or whitespace like Python's `int` does.
- **An adapter already exists too:** `lib/khand.smlib`:61 `khand_mukt(bytes,n,out)` expands packed bytes to qword cells and appends a zero cell. The destination needs **n+1 cells**, not n bytes. Thus a conversion pipeline is possible today on v324 without inventing two functions. `khand_bandh` goes in the opposite direction.

Do **not** call `varna_tak_ank(text,n,ok)` directly on the line reader's packed bytes. Do **not** call `grahan()` after reading a text line and claim it converts that string: it consumes the **next input line**. The v324 reference:411's “use grahan for that line instead” is an alternative read strategy, not a conversion operation.

### A bounded bridge was exercised, not proposed without a test

The evidence includes a small program importing `khand` and `vakyank`, reading a line, limiting its byte length to under 32, unpacking it into a 33-cell array, then calling `varna_tak_ank` and printing status/value. Results:

| Input | `ok[0]`, value |
|---|---|
| `42`, `-42`, `0` | 1, corresponding value |
| MIN / MAX | 1, corresponding endpoint |
| MAX+1 | 0, 0 |
| `hello`, `12 34`, empty line, `+42` | 0, 0 |
| bytes `12` + NUL + `x` + LF | **1, 12** |

The last result is an **additional silent-truncation hazard** in the proposed composition: `vartani_aayam` sees only bytes before NUL, although the line reader consumed the remainder. The integer parser is validating the supplied prefix, not the whole input line. A public strict-input API must reject embedded NUL before losing the length, or carry explicit byte length through the reader/parser boundary. The bounded bridge is proof that the existing components connect, **not** a production-ready general input API. Its small buffer limit is deliberate; do not copy it as an unlimited reader.

### How much breaks: count exposure separately from observed failures

The inventory strips strings and three comment forms, checks canonical `grahan` plus spellings from all 11 language packs, and uses the byte guard's exact glob set. No library module adds an indirect `grahan` dependency. It finds the same **8 programs / 18 direct call sites** on both trees:

- main: **331 top-level examples, 783 guard programs**;
- pinned v324: **335 top-level examples, 787 guard programs**;
- **6 of the top-level examples** contain calls, of which one already intentionally fails compilation;
- the other two callers are `tests/r79_real/report_blocks.sm` and `report_plain.sm`.

This is not “eight currently working programs all stop compiling.” To measure a concrete migration model, `ROUND-234-INPUT-MODEL.py` replaced just the calls in temporary copies with existing `vartani_grahan()`, compiled original and modified copies with v324, and ran accepted copies with fixed inputs and a five-second timeout.

| Source | Sites | Observed text-reader substitution |
|---|---:|---|
| `examples/23_grahan_input.sm` | 2 | Refused: `E_VARTANI_GANIT` at multiplication |
| `examples/24_guess_game.sm` | 1 | Compiles, then **times out** with the previously successful input `7`; mixed numeric/string variable use is not universally rejected |
| `examples/26_calculator.sm` | 2 | Refused: `E_VARTANI_TUL` at comparison with numeric sentinel |
| `examples/349_r126_kosh_in_one_branch.sm` | 1 | Already refused; diagnostic changes from `E_VITTI_PRAKAR` to `E_VARTANI_TUL` |
| `examples/46_language_reference.sm` | 1 | Compiles/runs with the same observed output/exit; input value is unused |
| `examples/59_windows_grahan_runtime.sm` | 1 | Compiles/runs; output changes from `42` plus LF to `42` without LF |
| `tests/r79_real/report_blocks.sm` | 5 | Refused: `E_VARTANI_GANIT` in allocation-size arithmetic |
| `tests/r79_real/report_plain.sm` | 5 | Refused: `E_VARTANI_GANIT` in allocation-size arithmetic |

**In this model: six previously compiling guard programs regress — four new compilation refusals, one timeout, one output change. Four of those are top-level examples.** One additional negative-test diagnostic changes; one unused-result example retains its observed output. Seven of the eight callers therefore need behavior/oracle migration in this experiment. This is a reproducible source-substitution model, **not an exact prediction of every possible future compiler implementation**. Builtin IDs, the `parikshita` allowlist, type inference, pointer-arithmetic rules and diagnostics must also be reconciled in a real return-type change. Generated programs embedded in Python tests and all book snippets are outside the 783/787 caller count and require a separate migration sweep.

### Recommendation

**Adopt one stable text-returning input operation plus explicit checked conversion as the eventual beginner model. Do not infer the return type from the user's input, and do not ship a silent return-type change as an ordinary v315 fix.**

For the current compatibility line, keep numeric `grahan()` and text `vartani_grahan()` working under their named contracts, teach the text reader plus status-checked conversion for new beginner examples, and provide a thin checked packed-string conversion wrapper (or a direct packed-byte parser). Reuse the existing converter/adapter machinery where appropriate; a library wrapper need not add a new compiler builtin. Once migration and compatibility policy are accepted for the next language version, `grahan()` can become the canonical text reader, with the old numeric operation given an explicit numeric name or kept behind a compatibility mode. Names are a project decision; none is implemented here.

The new conversion contract should require the **whole input** to match a defined grammar, reject overflow, distinguish valid zero from failure, define whitespace/plus/minus and ASCII/native digits, reject or represent NUL, and expose EOF/I/O failure distinctly from a valid empty line. Use the existing checked-status convention or an explicit `phal` result; do not return a numeric sentinel that collides with a valid number. Input failure handling, bounded growth and allocation lifetime mean this is **not zero-cost merely because a converter exists**.

For teaching, reading obtains text; conversion interprets it. A visible invalid-number branch is one extra concept but prevents `hello -> 0`, digit concatenation and overflow from masquerading as success. Two well-named, strict operations can be equally safe. The unsafe choice is **guessing number-versus-text or “parse whatever digits exist”**, regardless of how many functions the API has. Returning text alone is not sufficient: the measured guessing-game timeout and embedded-NUL example show why conversion and migration checks are essential.

Python's documented model is the comparison, not a claim of identical Sutram behavior: `input()` returns a line as text without its trailing newline and raises `EOFError` at EOF; `int()` is a separate conversion. Sutram's current EOF flag and explicit status/error mechanisms differ. Primary reference: https://docs.python.org/3/library/functions.html#input and https://docs.python.org/3/library/functions.html#int .

## WS4 — ten highest branch-density compiler blocks

“Most complex” needs a reproducible metric. `ROUND-234-INVENTORY.py` ranks **conditional jump instructions per non-local labelled source block**, tie-breaking by unconditional jumps and location. It scans `src/**/*.asm` and `src/**/*.inc`: 532 blocks with recognized instructions on main, 563 on v324. This is a source branch-density proxy, **not** a complete CFG, cyclomatic complexity, preprocessed build-specific count or count of branches in emitted programs. Macro expansion and call-graph complexity are not included; conditional-assembly alternatives can both contribute. The top ten names agree across the two trees.

All locations below are `src/sutram_compiler.asm`. “Every branch read” means the complete local block was read, including its branch destinations within that block; it does not certify every callee or prove reachability/test coverage.

| Rank | Routine/block | Main lines; conditional jumps | v324 lines; conditional jumps | Every local branch read? | Audit boundary |
|---:|---|---|---|---|---|
| 1 | `r142_gen_expr_body` | 21484–26701; 219 | 22564–27868; 221 | No | targeted builtin, input, string and allocation paths only; the large emitter remains the thinnest coverage. |
| 2 | `r142_gen_stmt_body` | 18924–21129; 170 | 19996–22209; 170 | No | loop, declaration, scratch and selected exit paths read; not every statement emission path. |
| 3 | `r45_parse_stmt_body` | 14836–16187; 164 | 15905–17258; 164 | No | selected declaration/body/loop parsing; not every syntax/diagnostic branch. |
| 4 | `lex` | 6976–7730; 107 | 7050–7823; 113 | No | targeted unknown-byte, token and string handling from earlier rounds; not a fresh complete branch read. |
| 5 | `expand_imports_pass` | 3619–4151; 84 | 3693–4225; 84 | No | includes/paths were inspected in earlier work, not every expansion/error branch here. |
| 6 | `parse_primary_inner` | 17075–17853; 75 | 18146–18924; 75 | No | selected calls/arguments and checks; not the complete expression-primary parser. |
| 7 | `_start` | 2745–3239; 56 | 2811–3313; 57 | No | selected version/options/platform initialization paths only. |
| 8 | `r81_walk` | 11296–11562; 51 | 12164–12430; 51 | Yes, both | dispatch, recursive child positions, declaration/index policy, builtin allowlist, likha special case, argument cap, user-call and refusal branches. Callees not fully audited. |
| 9 | `r137_check_stmt` | 28454–28752; 51 | 29621–29919; 51 | Yes, both | worklist/budget, node validation, all dispatches, numeric/slice and kosh distinctions, ternary arms, function parameters, generic children and error exits. Callees not fully audited. |
| 10 | `rfx_check_str_binop` | 9679–9922; 51 | 9785–10028; 51 | Yes, both | kosh/mala/rachana guards, boolean/arithmetic operations, string rewrites, mixed-kind cases, pointer-arithmetic exceptions and diagnostic paths. Callees not fully audited. |

The three fully read blocks are byte-for-byte equal as source slices between these pins; the current complete read therefore applies to both. The remaining seven are explicitly partial. No full reachability proof is attempted. The evidence includes the metric, counts and both top-ten inventories so the order can be reproduced rather than trusted as an impression.

## Coordination corrections and acceptance boundary

- The brief's `vartani_tul` ordering premise is corrected above.
- “Zero of 347” closed the proposed OS-trim work item for the studied examples; it did not implement memory return to the OS.
- `docs/WHATS-LEFT.md` was intentionally archived in R156; `PROJECT-MASTER.md`:18 and v324 `docs/RELEASE-NOTES.md`:337–338 point to the live release-notes list. Do not recreate the old path merely to satisfy an obsolete reference.
- Main is v315 and its changelog names v315. The pinned v324 changelog begins with **v324** and contains the intervening entries. The separate brief's claim that it is nine versions behind is not true of these inspected pins. Do not treat different main/staged versions as missing entries automatically.
- Production changes and application of the R233 branch belong to Claude's current implementation stream. This return changes only `ChatGPT-to-Sarvam/`. No Windows-to-Sarvam file, production file, golden, prior evidence or history is changed; personal system details must remain out of every follow-up.

Deliverables: this review; the three reproducible own-folder Python helpers; `ROUND-234-EVIDENCE.json` with inventories, temporary-program results, exact compiler hashes and verification scope. Focused observations are local Linux executions of the committed binaries; they do not renew R233's full-gate result, validate Windows, or accept the staged chain for release.

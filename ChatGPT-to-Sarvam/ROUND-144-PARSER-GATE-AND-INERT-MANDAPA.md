# Sutram ROUND 144 — four evidence blind spots, the body-ledger gate, and inert mandapa

**Date:** 30 October 2026. **Pinned main:** `8ad050b949eadfc30d19878982e00eb06f8a1e49`.
**Assignment:** `Sarvam-to-ChatGPT/ROUND-144.md`, blob `15f385d11a0f5be89181f6b0c63d2f0658c879b7`.
**Return:** `ChatGPT-to-Sarvam/ROUND-144-PARSER-GATE-AND-INERT-MANDAPA.md`.
**Observed source:** compiler v267; changelog v423. This is a read-side review and a proposed gate, NOT an implementation, execution report, or acceptance of a later concurrent commit. Sanskrit only; protected files remain unchanged by this return.

## Answers first

1. **Four useful evidence categories:** missing stimulus; checking the wrong or too-small property; a correlated/wrong oracle; and invalid configuration/result enforcement. The last category is the missing question: **did the claimed implementation actually run, and would its failure reach the final verdict?** These are evidence limitations, not a theorem that there are exactly four compiler bug classes. Missing source-to-tree verification is principally an independent-oracle/semantic-coverage gap.
2. **Price the literal body-accounting gate:** cover **eight existing body-owning construct families**, with **mandapa as a ninth, pending family**. Compare each body's **ordered statement identities and ownership**, with its count as a derived field, against an independent source-fixture manifest. Initial implementation estimate: **540–900 lines total**, including a test-only compiler exporter; initial native matrix: **46 cases per claimed applicable profile**. Comments and blank lines contribute zero, and a nested control contributes one statement to its parent plus separate child-body records. Details and limits are below. This is not a claim that 46 tests prove all parses correct.
3. **Inert first is a reasonable INTERNAL implementation stage, not a safe default user feature.** I would approve a disabled-by-default/test-only parser scaffold with strict equivalence and structure checks. I would request changes if the ordinary released compiler silently accepted `mandapa` as though reclamation or K0 protection existed. Develop parser, checker and lowering in separate reviewable commits; enable the public checked-block contract only when its checks, allocation routing and all exit cleanups are verified together.

## Evidence corrections before drawing conclusions

The brief and v423 heading say four silent drops, but the supplied list names **three concrete mechanisms**: old single-statement treatment of indented control bodies; unconsumed source after a braced `mukhya`; and the same-line second-statement policy. The fourth entry, “whatever the goldens then caught,” does not identify another defect. R71 specifically reports **two more** after the original R70 issue. Do not manufacture a fourth unique root cause or infer that every historical version was tested. [R1–R3]

Not all three were literal token deletion. R70 placed later statements outside the intended loop; the same-line case also executed the second statement outside the conditional under the old rule. R71 describes the new same-line rejection as a language-policy choice. Source after a braced `mukhya` was genuinely ignored. Those distinctions matter to the gate: **presence alone, and even per-body counts alone, are weaker than correct ownership and order.** [R2]

R71's 25-case matrix is especially informative: the old parser gives the expected total for a **true** three-statement `yadi`, but gives 2 instead of 0 for its **false** counterpart. With a true condition, one statement inside plus two outside can produce the same total as three inside. The oracle must distinguish meanings, not just tally outputs. These are partner-recorded runs, not reruns here. [R3]

I verified that R143's previous handoff remains present. It already priced a restricted behavioral model gate at 300–550 Python lines and optional direct structure checking at another 200–340 lines. Here I make the requested **per-source-body accounting scope** explicit, rather than silently treating the earlier cost as an implementation already delivered. [R6]

## WS1 — the SHAPE of what the four cited gates cannot establish

### The four categories, not a list of test programs

| Evidence category | What is missing | Correction to the brief's formulation |
|---|---|---|
| **1. Stimulus/composition coverage** | The source form, input, branch, nesting, failure condition or interaction that exposes the defect never reaches the gate. | A construct absent from all tested inputs is untested. A construct present only in one context is not tested in every composition. A census can reveal absence but does not prove correctness of present forms. |
| **2. Property/observation coverage** | The observed property does not distinguish the bad execution from a correct one. Examples: memory remains mapped; output totals agree although ownership/order differs; termination or side effects are not observed. | A bounds mechanism is not a semantic checker. However, the surrounding runner may also compare outputs: classify the actual checks, not just the gate's name. A silent omission can be detected by an independently correct output/effect/progress oracle. |
| **3. Oracle independence and correctness** | The expected result shares the implementation's mistake, derives from an erroneous baseline, or encodes an unsettled language policy. Two wrong implementations can agree byte-for-byte. | Consistent output is not necessarily correct output. A reviewed source-to-tree model supplies an additional independent obligation; a dump compared only to another dump from the same faulty parser does not. A wrongly assumed exclusive `chakra` endpoint would also be an oracle error. |
| **4. Configuration and verdict integrity** | The suspect implementation/path was replaced, the claimed target was not run, a case was skipped/refused rather than executed, or errors/timeouts/missing records were lost in aggregation. | Ask both **what actually executed** and **whether a failing observation makes the gate fail**. A replacement allocator cannot qualify the disabled production path; a displayed PASS count cannot compensate for ignored process status. |

Category 4 has two distinguishable subproblems—configuration fidelity and fail-closed reporting. It is grouped here to answer the requested four-category framing, not to declare a universal taxonomy. R141/R142 previously documented examples in this project; this round has not freshly audited the current wrapper's full error propagation. Do not mark those earlier concerns fixed or still reproduced from this review alone.

The bullet “nothing checks that the parse tree matches the source” is not evidence of another discovered bug. It names an absent **specification-to-implementation relation**, mainly category 3, with category 2 deciding what part of that relation is observed. Such a relation must be defined by the agreed grammar, not by visual intuition or another language's rules.

### Why “none of the four gates could see any of them” is too strong

A correct golden and a timeout would detect the original infinite loop. R70/R71's retained new examples and matrix do precisely that on the affected old compilers, according to their reports. Thus the output-test machinery is capable of detecting the family; the original inputs/oracles/configurations did not establish the needed property. [R2,R3]

Conversely, identical binaries are strong evidence of unchanged generated bytes for the compared input, but not evidence that those bytes implement its intended meaning. A guard-page run is valuable for its protected executed boundaries, but not a proof of syntax, binding, ordering, termination or all memory safety. There is no single additional aggregate count that turns these conditional observations into universal correctness.

**The compact answer:** the missing shape is **an accepted source interpretation that is wrong but observationally indistinguishable under the selected, possibly correlated checks**. Add independent meaning/structure observations, and verify that the actual candidate and all outcomes reach those observations.

## WS2 — exact scope and price of a source-body counting gate

### A. Eight existing construct families, plus the pending ninth

This is an explicit grouping for the proposed gate, not a count of `parse_body` call instructions. R71 reports 11 callers; several belong to arms of the same source construct and some bodies use other parser paths. [R2]

| Family | Body ownership the gate must represent |
|---|---|
| 1. `mukhya` | Entry body, its end, and the disposition of every subsequent top-level token. Distinguish braced main from the current unbraced-to-EOF policy. |
| 2. `prakriya` | Function body, parameters/declarations and following function/entry declarations; no accidental absorption or omission. |
| 3. `yadi` / `anya` / `anya yadi` | Then/else ownership and chain attachment, including taken and untaken paths. Chaining is a variant, not a ninth independent family. |
| 4. `yavat` | Condition, ordered loop body and following siblings. |
| 5. `chakra` | Loop body and following siblings; both `tak` and `arabhya … paryantam` are variants. Preserve the documented inclusive endpoint. |
| 6. `kuru … yavat` | Post-test loop body and its trailing condition; do not count the tail as a second loop body. |
| 7. `guna` / `bhavana` | Selection and individual case-body roles under the accepted grammar. The selector still requires braces in the inspected evidence; indentation may be used for case bodies, not silently substituted for required selector braces. |
| 8. `yadi dosh (…) … anya …` | Failure/success arm ownership; do not conflate this with an ordinary Boolean branch merely because words overlap. |
| **9. `mandapa`, pending** | Its source wrapper, ordered contents, nested ownership, and outside continuation. No working implementation or K0 acceptance is claimed here. |

Also inventory the program root, ordinary sequence containers and statement leaves, but do not inflate those implementation records into extra language-construct families. Leaf coverage initially includes scalar declaration, assignment, call/expression statement, return, break/continue and the relevant error-form statements in their legal contexts. Data-member lists and enum entries are **not executable bodies**. The minimum gate's supported expression subset is small, explicit and independently specified; unsupported constructs are UNCHECKED/failing coverage, not invisibly discarded.

### B. Counting rule: direct source statements, not physical lines or all AST nodes

Define a body ledger record as:

```text
(body_identity, owner_statement, role, ordered_direct_statement_ids)
```

The count is `len(ordered_direct_statement_ids)`. Record each statement's kind, relevant operands and source token/span identity separately. A synthetic AST wrapper must not acquire a fictional source statement identity.

| Source situation | Legitimate accounting |
|---|---|
| Blank line or comment-only line | Zero statements; no body transition merely because a blank/comment line has different indentation. Follow the frozen lexical policy. |
| Trailing comment | No extra statement. A comment marker inside a string is string content, not a comment. |
| One expression/statement over several lines | One statement, using the grammar's token continuation rules, not line count. |
| Two permitted statements separated on one line | Two statements. In v267, a second statement on a **single-statement header-body line** is instead refused; do not normalize a rejected input into two accepted statements. |
| Nested `yadi` inside `yavat` | One control statement in the loop's direct list; distinct lists for its then/else bodies. The nested children are not double-counted as direct loop siblings. |
| `anya` / case label / post-test tail | Structural role or delimiter as specified, not an extra executable leaf merely because it occupies a line. |
| Braces, indentation and dedentation | Body boundaries, not executable statements. A data-layout brace list is not automatically a statement block. |
| Declaration with initializer | One source statement; initializer expression nodes are not additional direct statements. |
| Parser-generated lowering/wrappers | Compare through an explicit source-origin mapping. Never compare source-statement counts to every low-level AST node. |
| Unreachable but syntactically present statements | Present in the pre-optimization structural ledger even when the expected runtime trace omits their execution. |
| Invalid or unsupported grammar | Expected diagnostic, or UNCHECKED for the proposed tool; never a silently reduced denominator. |

A scanner that strips `#`, counts newlines, or counts semicolons without recognizing strings and continuations is not this gate. Tabs must follow Sutram's specified rule, not a Python/editor tab-stop assumption. Imports/rewritten sources need file and expansion identity in any later whole-repository version.

**The count can legitimately differ between source lines and a tree; it must not differ between the same defined source statements and their normalized direct-child records.** Comments and whitespace disappear under normalization by definition. Unexplained differences fail; there is no blanket “nested constructs cause different counts” exemption.

### C. Why retain identities, parents and order in addition to counts?

Consider these abstract ledgers:

```text
intended loop: [print_A, increment]     wrong loop: [print_A, print_B]
intended after: [print_B, finish]       wrong after: [increment, finish]
```

Both bodies have two statements, and every statement identity appears exactly once globally. **Even independent per-body counts pass**, while the counter increment moved outside the loop. Swapping two distinct statements within one body also preserves every count. An ordered identity/owner comparison is a small addition that detects both shapes; it is not an excuse to build a full formal verifier first.

A local abstract Python check confirmed those equal counts and unequal ownership/order. It was not a Sutram parse or native execution.

### D. The smallest direct gate I would implement

1. **Independent expectation:** create reviewed fixture models and explicit source files/sidecars defining statement identities, ownership and expected trace/state. For generated fixtures, render from the intended tree and retain the source-span map produced by that renderer. Do not generate the expected ownership from the production parser or formatter.
2. **Observe the actual retained representation:** add a test-only traversal/export before optimization/code generation. It must walk the final reachable parse representation and registered functions—not merely log that `parse_stmt` was called. A node can be parsed and then dropped. When parsing already lowers a construct, preserve an origin/owner side table or report a precisely documented source-level projection. Do not assume the existing AST already has all this metadata.
3. **Compare the complete records:** exact identities, owners, roles, order and direct counts, plus the small supported expression structure. Assert full input disposition and no successful executable after a parse error. A token reaching EOF is necessary but insufficient: wrong-body assignment can consume every token.
4. **Execute independent semantics as well:** both legal brace and indentation renderings must match the intended model's trace/final state and termination. Matching each other alone is not the oracle. Preserve the real historical failures as calibration.
5. **Fail closed:** fresh output path per case, exact compiler/source hashes, bounded output and timeout, child status retained, manifest cases reconciled. Unknown nodes, missing roots or missing cases cannot become PASS.

This is source-to-structure checking for a **defined fixture subset**. It is not an automated proof over every arbitrary source file. Handwritten fixed sources can use independently reviewed expected ledgers. Applying the same system to unknown existing programs requires a separately specified independent lexical/layout recognizer or manually authored manifests; a regular expression is not a substitute for either.

### E. Price, with the scope stated

| Work item | Planning estimate, NOT implemented |
|---|---:|
| Eight-family fixture model, legal renderers, source-span/identity manifests and lexical variants | 160–260 Python/fixture lines |
| Test-only compiler traversal/export and missing source-owner metadata for that subset | 180–300 NASM lines |
| Independent ledger normalization/comparison, counts and ownership/order checks | 100–160 Python lines |
| Bounded runner, semantic observations, mutation controls and structured outcomes | 100–180 Python lines |
| **Minimum direct body-ledger gate** | **540–900 total lines** |

These are estimates for the bounded scope above, not measurements or a guaranteed ceiling. Existing AST lowering or provenance plumbing may require more. A simpler **behavior-only** model gate can start with R143's 300–550 Python-line budget and no compiler edits; it detects the historical wrong meaning but does not directly inspect parse-tree counts.

For **arbitrary-file discovery** beyond the fixture subset, separately budget approximately **600–1,200 additional test-side lines** for an independent token/layout/body recognizer and its grammar controls. This is an estimate for explicitly supported forms, not a promise of a complete second Sutram frontend; unsupported syntax must remain UNCHECKED. Rich imports, full expression grammar and full binding verification are outside the small first gate. Keep that larger census distinct from the smallest detector that would have caught these reported cases.

### F. Concrete initial denominator: 46 present-language cases

- Eight existing families × two intended structural scenarios × two legal surface renderings = **32 positive renderings**. One scenario emphasizes a multi-statement body/continuation; the other distinguishes nested or alternative-arm ownership. For `guna`, preserve its required outer braces in both variants and vary the allowed case-body form.
- **Eight negative cases:** ambiguous intermediate dedent; executable source after braced `mukhya`; a function after braced `mukhya`; the forbidden second statement on a single-statement header-body line; orphan `anya`; unmatched brace; missing assignment expression; unfinished parenthesized header. Freeze exact source and expected diagnostics first.
- **Six additional lexical/layout variants:** comment-only lines; blank lines at boundaries; comment/delimiter-looking text inside a string; a continued expression; multiple permitted statements inside an indented body line; and a declared tab/CRLF spelling variant under the actual lexical policy.

**32 + 8 + 6 = 46**, per claimed applicable build profile. These are proposed source executions, not completed tests, and not all possible combinations. Both range spellings, every case/error alternative, nesting limits, import provenance, over-indentation policy and further expression forms need additional named rows before broader coverage is claimed. Publish the expanded denominator rather than hiding unsupported variants under one family count.

For the later experimental `mandapa` scaffold, add **four explicit wrapper/erasure pairs**—straight-line, nested, inside a branch/loop, and scalar early exit—giving eight additional compilations/executions once legal syntax exists. Do not count today's unknown-keyword refusal as a passed wrapper test. Compare each pair's structure as well as bytes/output under the scope rules in WS3.

Calibrate the ledger with delete, duplicate, swap and cross-body-move mutations, including changes preserving all per-body counts. Run known v264/v265/v266 counterexamples at their applicable historical commits. Missing case, wrong oracle, failed child and timeout must each fail the top-level gate. Passing only the fixed candidate is not calibration.

## WS3 — review of the proposed inert mandapa stage

### My commit-review decision

**Approve the staged engineering idea; request changes before default public enablement.** Introducing syntax separately makes parser changes reviewable without conflating them with allocation, cleanup and escape checking. Requiring unchanged normal code generation is a useful isolation condition. It is not enough to make an unchecked, non-reclaiming block a released safety feature.

The source I inspected still identifies itself as **v267**. I reviewed its body helper and R71 evidence, not a completed inert-mandapa diff. The following is a prospective acceptance checklist, not approval of code that has not been inspected. [R4]

### “Inert” needs an exact meaning

For this stage, inert should mean **no scratch routing, no cursor mark/rewind, no automatic free, no new runtime safety guarantee and no K0 certification**. Existing `nirmmita` remains the persistent allocation operation on that path. The parser should retain the wrapper identity and source extent for structural checking; the test-stage lowering may explicitly erase it. Parsing and immediately forgetting the wrapper everywhere would make the new syntax harder to validate.

**Choose binding semantics explicitly.** A transparent annotation that is erased before name binding can be compared with the same sequence simply unwrapped. A new lexical scope can change declaration visibility, shadowing, rejection behavior and variable placement. The existing indentation helper calls `r7_close_block`, so normal block processing already has scope consequences. [R4]

Therefore the universal statement “with the block and without it are identical” is underspecified. Either:

- the experimental wrapper is truly transparent, and the erasure transformation removes only that wrapper while preserving all surrounding structure; or
- it deliberately introduces a scope, and equivalence is checked against the same ordinary lexical scope, or on explicitly scope-insensitive programs.

Do not erase a real scope, change which binding a use denotes, and then demand identical bytes. Do not normalize away changed ownership merely to make the comparison pass. A `kosh` example accepted in an inert developer build is likewise **not K0 acceptance**: the eventual checked function's collection prohibition remains separate.

### Two different equivalence gates

| Comparison | Required result for the stated stage |
|---|---|
| Same existing source, no `mandapa`: pre-scaffold compiler versus scaffold-disabled/default compiler | Zero unexplained acceptance, output or ordinary emitted-byte change against the same allocator baseline. Account separately for intentional keyword-reservation compatibility effects. |
| Experimental wrapper source versus its independently specified safe erasure/control | Same intended statement ownership after erasing only the wrapper; same results/effects/termination; same ordinary generated bytes where the binding and build-mode contract promises this. |

A debug build may encode source locations changed by adding an opener/indentation; byte equality for that mode needs its own explicit policy. State the target/options and compare normal output first rather than making a universal claim over every diagnostic or source-location mode. Pointer addresses or source-derived diagnostics must not be silently used as an equality oracle without defining their status.

New reserved words can invalidate an existing identifier even with zero emitted instructions. Require a collision/compatibility check for the chosen keyword and native spelling; a passing finite no-block corpus does not prove there are no external users of that identifier. No whole-repository collision census was performed in this round.

### Conditions I would attach to an internal scaffold merge

1. **Disabled by default or available only through an explicit developer/test compiler option.** Normal v1 users must not mistake an inert block for a checked/reclaiming block. An opt-in experimental build must state that neither guarantee exists; an informational warning is not itself a safety check.
2. **Parser ownership independently checked.** Preserve late body statements, nested exits, branch attachment and continuation; reject malformed layout according to the agreed grammar. Add the proposed body-ledger/meaning cases rather than relying only on output equality of one happy path.
3. **No hidden semantic work.** Do not partly turn on rewind/routing while the checker is absent. Even a syntactically tiny wrapper can become dangerous if cleanup starts invalidating pointers that were never escape-checked.
4. **No-block compatibility against the same baseline.** Record compiler hashes, target modes and the exact changed-source list. Do not compare against a different allocator version and attribute every byte change to the scaffold.
5. **Failure paths report honestly.** No stale executable after syntax failure, no dropped tail, no uncounted failed or skipped fixture. Preserve actual child status through the gate.
6. **Stable public activation is a later, coordinated gate.** Require K0's whole-function restrictions, allocation/null/extent rules, correct scratch routing, all normal/early/failure exits and backend preservation before enabling the user-facing guarantee. The implementation commits can remain separate; the release contract cannot be half-enabled.

If the owner explicitly intends a permanently harmless grouping construct rather than a memory/safety construct, that is a different public language decision. It must not simultaneously be documented as reclaiming scratch. I do not silently make that decision in a reviewer handoff.

### K0 remains the same limited feature

The future checked feature is fixed-size numeric scratch, not arbitrary vectors or pointer graphs; unsupported `kosh` remains prohibited throughout its containing checked function. The source-to-tree parser gate is a prerequisite, not a replacement for those checks or for native cleanup tests. Conversely, an internal inert scaffold does not need to pretend it has already enforced K0. Label its acceptance results as **parser/scaffold tests only**.

**Public wording during staging:** “Experimental syntax only: this build recognizes `mandapa` but does not reclaim its allocations or enforce K0 safety.” In a default release that is not intended to expose such an experiment, reject the keyword until activation instead. Do not use the future beginner sentence about reclaimed space without its implementation-status notice.

## Disposition and evidence ledger

**R144 recommendation:** keep the useful existing gates; add the independent body ledger/meaning gate; permit experimental inert-first development; withhold the stable checked-block promise until the full accepted K0 contract is implemented and qualified. This is not a claim that the parser defect family is exhaustively closed, nor a recommendation to undo the measured allocator improvement.

The brief's latest heading and R71's detailed report differ on benchmark wording: v423 summarizes used allocations as 6–8 ns, while R71's written-allocation table reports about 31 ns on its host and 1.7 ns for untouched allocation after loop subtraction. This round did not investigate those harnesses. Do not use an unresolved summary as evidence that the parser or inert block is correct. Benchmark reconciliation remains separate from WS1–WS3. [R2,R5]

Pinned repository sources:

- **R1:** `Sarvam-to-ChatGPT/ROUND-144.md`, `15f385d11a0f5be89181f6b0c63d2f0658c879b7`: three workstreams and the proposed inert stage.
- **R2:** `Claude-to-Sarvam/R71-00-PARSER-CLASS.md`, `8d66db980139a3d1ea37caeb69d94a66a28a2825`: v266/v267 diagnoses and policy changes, named parser paths, recorded outcomes and native-testing limitations.
- **R3:** `Claude-to-Sarvam/evidence-r71/bodies-matrix.md`, `0fba9fb649baf623eb65ddd31eed4c9a8b46f6da`: 25 partner-reported scenarios; the true/false-branch contrast and expected refusals.
- **R4:** `src/sutram_compiler.asm`, `88bbf91e8e4ada1336ad1f3c59438faecc7b64c3`, read at 80–245 and 7220–7510: v267/AST definitions, retained indentation helper, `r71_after_single`, statement list construction and scope closing. This is not a complete parser audit. The earlier same-versus-deeper indentation prose/branch discrepancy remains visible; no new native reproduction is claimed.
- **R5:** `docs/CHANGELOG.md:1-110`, `ca219c31c50bc939e6cf48f25d1df17fea2f4eee`: v423 framing and attributed census/benchmark claims. The 2,189-site census was not independently rerun here.
- **R6:** `ChatGPT-to-Sarvam/ROUND-143-PARSER-SEMANTIC-GATE.md:1-25`, `447a4033c4080ab04dc3d35732af84690fd39822`: prior verified return, existing price and scope; the remaining report is available in the conversation history.
- **R7:** `LANGUAGE-PRIORITY.md:1-65`, `64682919a70fa1b79e415bc879aee9cad07582ad`; `AGENTS.md`, `795d1181272a8ab24848b84753bc46a2eb386d40`: Sanskrit-only active work, documentation-only handoff and no unapproved automatic workflow.

**Outside methodological context, distinct from Sutram evidence:** LLVM's official Testing Infrastructure Guide (https://llvm.org/docs/TestingGuide.html, consulted 30 October 2026) describes focused regressions and checking textual intermediate results. Clang's own AST documentation describes AST inspection (https://llvm.googlesource.com/llvm-project/clang/+/03a30c50893e7b629b90d875c4fb3435adf2f8b3/docs/IntroductionToTheClangAST.md). These support the general testing technique; they do not supply Sutram's grammar, validate this implementation, or determine the proposed costs/counts. No LLVM dependency is requested.

**Performed here:** connected pinned reads; a small local abstract-tree ownership/count check; integer arithmetic for the eight-family/46-case proposal and 540–900-line budget. No repository compiler or test tool was executed.

**NOT RUN — no native toolchain invoked:** current/historical parser executions, AST/body-ledger gate, inert wrapper equivalence, v267 qualification, compiler builds, Linux/PE/Windows/Wine tests, benchmarks, full-tree census or new CI. Partner totals remain attributed. No mandapa implementation, cleanup or K0 checker was inspected as completed work.

**NOT APPLIED:** compiler, library, tests, tools, canonical docs, packs, workflows, Windows or backup changes. Add only this Markdown handoff to `ChatGPT-to-Sarvam/`, verify full readback and single-file commit scope, then stop after Round 144.

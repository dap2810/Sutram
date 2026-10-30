# Sutram ROUND 143 — source-to-tree fidelity, the smallest useful parser gate, and K0

**Date:** 30 October 2026. **Pinned main:** `c32999ea82804c1fe6bca84da7651e3d1c6fdfec`.
**Assignment:** `Sarvam-to-ChatGPT/ROUND-143.md`, blob `b4ebc2aa26621d310d131e2060aa414323e0ea0f`.
**Return:** `ChatGPT-to-Sarvam/ROUND-143-PARSER-SEMANTIC-GATE.md`.
**Observed source:** v265 parser change; changelog v421. **Role:** read-side evidence/design review, not implementation or native validation. R70/Sarvam execution results remain attributed to their authors.

## The three answers, plainly

1. **The blind family is silent semantic misinterpretation with a shared wrong oracle:** the compiler accepts source but gives it the wrong structure or meaning, and the available observations either preserve that same mistake or do not test the intended behavior. In this case it is **wrong statement-to-body membership**, not a demonstrated allocation clobber. There is no justified finite count of all undiscovered manifestations. Output tests CAN detect it when their expected result is independently correct; the existing four gate labels did not supply that obligation for this input.
2. **Do not use a statement count as the parser gate.** The smallest useful new gate is an independently specified, bounded statement-tree model, rendered both with braces and with indentation, with each rendering checked against the model's expected execution trace. Initial budget: **300–550 test-side Python lines**, **30 primary cases per claimed profile**. No new language feature or compiler implementation is required for that first layer. For direct source-to-tree assertions, add a small test-only AST dump/comparator, estimated **200–340 additional lines**. Both prices are estimates, not completed work or full-language verification.
3. **The bug does not refute K0's abstract lifetime rules, but it is NOT orthogonal to an end-to-end K0 guarantee.** A correct checker over a wrong tree does not establish that the user's source was understood correctly. Parser fidelity is a prerequisite alongside checker and backend correctness. Do not permanently ban loops or `nirmmita` to compensate; qualify the parser and keep K0's existing limited scope.

## What changed since R142 — separate diagnosis from measurement

R142 deliberately did not identify a corrupted register. Its report explicitly listed a parsing/lowering mistake among alternatives and required baseline comparisons. The new evidence resolves the reported symptom differently: R70 says the v264 loop contained only `likha`; allocation and increment appeared **after** it. Its four-compiler transcript reports repeated `i=0` on v261/v263/v264 and `i=0 i=1 i=2 done` on v265. That supports the correction to the allocator hypothesis. I have not independently executed those binaries. [R2,R3,R9]

It is important not to replace one inaccurate diagnosis with another: **this example does not establish that statement tokens disappeared entirely.** They were assigned to the wrong enclosing sequence. The allocation was never reached while the loop ran. The same source-node count can therefore coexist with the wrong loop semantics.

R70 calls the indentation implementation a language change adopting the intended documented rule. Its passing old corpus shows preservation of those tested programs; it is not proof that every external program using the old single-statement convention is unchanged. R70's claim that none of the old corpus used the triggering multi-statement indentation is partner-reported, not a fresh whole-tree census by this review. Likewise the reproduced old versions do not by themselves establish the behavior of all 264 historical versions. [R2,R3]

I read the live `parse_body` / `r70_indent_body` implementation and the two new examples. The new helper is genuinely present in source; that source inspection is not a rerun of the reported regression or a complete correctness audit of the fix. [R4-R6]

## WS1 — the shape that the four gates missed

### A shared interpretation can be consistently wrong

Let S be the source, P the parser, and O the observable result of executing the generated program. The missing obligation is not merely:

```text
O(old_compiler(S)) == O(new_compiler(S))
```

It is that the accepted source is assigned the **specified structure and behavior**. Two compiler versions can share an erroneous P. Their binaries can match exactly, their outputs can match on the exercised inputs, and neither can touch a protected page, while both implement the wrong source program.

| Gate cited in the question | What its evidence can establish | Why this family can escape |
|---|---|---|
| Old/new output guard | Agreement on observed outputs/exits for selected inputs | Both versions share the parser mistake, the triggering composition is absent, or the selected observation does not distinguish meanings. |
| Guard pages | Executed accesses that reach successfully protected boundaries fault | Wrong control flow, omitted actions or wrong binding can remain entirely within mapped memory. Instrumentation may also replace production paths. |
| Regression suite | The cases satisfy their recorded expectations | A missing case provides no coverage; an expectation recorded from the same mistaken implementation is not an independent meaning oracle. A correct golden plus timeout WOULD detect this loop. |
| Byte comparison | Selected outputs have identical machine bytes or expected refusal behavior | Identical wrong binaries remain identical. No source-language meaning is established by equality alone. |

Thus **“none could ever catch it” is too strong**. R70's own new positive example fails on v264 by timeout and reportedly passes on v265. That is the existing regression mechanism successfully observing the right counterexample. What was missing was the source-meaning obligation and its stimulus, not an inherently powerless test runner. [R2,R5]

The same family includes losing a statement, duplicating it, placing it in the wrong branch, attaching `anya` to the wrong header, changing evaluation order, or binding a name/operator incorrectly. These are examples of a failure shape, not a claim that each is currently broken. Some can be memory-safe and still wrong; some can later cause unsafe behavior. A universal severity ranking of “parser bug versus memory bug” is not useful: this demonstrated nontermination is already sufficient to block qualification of the affected source form.

### Why counting statements is not enough

For the reported source, the intended and mistaken structures are:

```text
INTENDED                             OLD INTERPRETATION (R70 report)
Declare i = 0                        Declare i = 0
While i < 3                          While i < 3
  print i                              print i
  Declare p = nirmmita(64)            Declare p = nirmmita(64)
  i = i + 1                          i = i + 1
print done                           print done
```

Every leaf statement can still be present exactly once. A global count passes. A count per body, if independently specified, catches this particular 3-versus-1 body error, but still misses swapped statements, equal-sized wrong branches, wrong operands, and wrong bindings. Counting source lines is worse: a line can hold several statements, a statement can span lines, and comments/blank lines are not statements.

The structural obligation is **identity + owning body/branch + order + relevant expression/binding meaning**, under the accepted grammar. A small local illustrative tree check confirmed equal leaf sets/counts but different parent paths for allocation and increment. That calculation is not a Sutram parse or execution.

### Do not choose another correlated oracle

R70 reports that `tools/sutram_fmt.py` previously implemented the same one-statement body assumption, and was changed with the parser. Therefore “format it, compile it again, compare bytes” can preserve the same wrong interpretation. The formatter remains useful for its declared round-trip checks; it must not define the independent expected meaning for the new parser gate. [R2]

## WS2 — the smallest gate I would build now

### A. Freeze the grammar policy first

Use the explicit R70 policy as the starting contract, with owner confirmation where it is incomplete:

- A brace opener selects a brace block.
- A later-line body indented deeper than its header selects indentation-block handling.
- A body on the header's own line remains a single statement.
- R70 retains the legacy one-statement case for a following line not deeper than the header; do not silently test that as if v265 promised a rejection.
- A dedent between the recorded header and body levels is rejected, as example 259 specifies.
- Spaces and tabs each count one position in R70, not an assumed tab-stop width from another language.

**Concrete policy discrepancy found while reading:** the helper's prose says following statements start at the **same indentation**, but its loop uses `cmp rax,r15` followed by `jae .stmt`, explicitly accepting **at or deeper** indentation. The instruction is source-confirmed; no native counterexample was run. Decide whether an extra-indented ordinary statement without a new header is allowed or rejected, then make documentation and expected trees agree. Do not manufacture a PASS by deriving the policy from whichever behavior the current parser happens to emit. [R4]

The helper measures the preceding token's line to find the header indentation. If multiline headers are admitted by the intended grammar, include a case where the final header token is on a continuation line; do not assume it has the opener's indentation. This is a test requirement, not a newly established defect. Similarly freeze comment/blank-line handling, mixed brace/indent boundaries and branch attachment. Unsupported grammar must be explicit rather than guessed into an oracle.

### B. Build trees first, not expected output from the compiler

The test manifest describes a tiny independent model: sequences, scalar assignments, integer conditions, bounded loops, branches, direct scalar returns and uniquely identifiable marker events. Construct the intended tree FIRST. Render it in two separately specified surface forms:

```text
reviewed model tree T
    -> brace renderer -> S_brace
    -> indentation renderer -> S_indent
    -> tiny bounded evaluator -> expected event trace and final scalar state
```

Compile and execute each rendering with the production candidate. Require **each** to match the independent trace/state/termination oracle. Also compare the two results as supporting evidence. A pair that agrees with each other but disagrees with the model must fail.

The evaluator implements this restricted fixture model, not a second complete Sutram parser. Restrict integers to non-overflowing small values, loops to fixed small bounds, and effects to controlled observations. Do not add pointers or allocation to the minimal shape detector: R70 already demonstrates the same bug without allocation. Preserve the exact allocating reproducer separately as an end-to-end regression.

A simple positive model repeats two distinct markers three times and then prints a final marker, with the counter update between the repeated markers. Moving the update or second marker outside the loop changes its trace or termination. Markers must have distinct identities; observing only a total sum permits cancellations and reordered execution to disappear.

Run both an event-trace version and, where useful, a delayed scalar-state observation when expanding coverage. Observer calls can affect backend behavior, so a marker-only test is not the entire compiler-preservation argument. This gate primarily targets source structure; R142's independent backend/effect obligation remains separate.

### C. A small, explicitly bounded first matrix

**Twelve positive model scenarios, each rendered in two forms, plus six negative source cases: 12 × 2 + 6 = 30 primary cases per claimed build profile.** This is a proposed initial batch, not a magic sufficient total or tests already implemented.

| Model | Distinguishing structure |
|---|---|
| P01 | Three-iteration loop with three body statements and an after-loop marker. |
| P02 | Zero-iteration loop: body effects absent, after-loop effect present. |
| P03 | One-iteration loop with distinct first/last body effects. |
| P04 | Taken `yadi` with multiple statements followed by an outside sibling. |
| P05 | Untaken `yadi` with multi-statement `anya`, followed by an outside sibling. |
| P06 | `yadi`/`anya` nested inside a bounded loop, with a loop-tail increment. |
| P07 | Two nested bounded loops with distinct inner/outer tail effects. |
| P08 | Dedent through two scopes followed by an outer sibling; ownership matters. |
| P09 | Scalar early return inside a branch: later effects must not execute. |
| P10 | A scalar helper body with several statements and a caller continuation. |
| P11 | Comments and blank lines between body statements and before dedent. |
| P12 | Multiple statements on a line within a body; line count must not define node count. |

The six proposed negative cases are: example 259's between-level dedent; an unfinished parenthesized header; an unmatched brace; a missing assignment expression inside a body; an orphan `anya`; and malformed trailing source after an otherwise complete program. Freeze the exact strings and intended rejections against the agreed grammar before implementation. No unsupported optional syntax should be mislabeled as malformed merely to increase the count.

This batch does not exhaust `chakra`, `kuru`, switch/case, short-circuit expressions, failure propagation, import rewriting, same-line legacy bodies, newline encodings or the over-indentation policy question. Add separate named rows for those supported forms; publish the expanded denominator. Include all selected true/false and iteration scenarios explicitly rather than claiming that one arbitrary branch input covers both arms.

The original examples 258/259 stay in the existing suite. Their presence does not make the additional matrix already run, and duplicating one as a new row is not independent evidence. No proposed initial case requires `mandapa`.

### D. A direct AST check is better for structural localization

For a stronger frontend gate, export a **test-only normalized parse tree before code generation/optimization**. Compare it with T for each rendering, not with another dump generated by the same mistaken parser. Record node kind, body/branch role, ordered children, fixture statement identity, and relevant operands/operators/names. Track source spans or source-token identity where the current representation supports it; adding missing metadata has a cost and must not be assumed free.

Normalize only explicitly irrelevant representation details, such as arena addresses and approved synthetic wrappers. Do not normalize away statement ownership or order. A per-body count logged by the same parser is useful debugging information, but is not a substitute for traversing the produced tree and comparing it to the independent manifest.

An unrecognized node or incomplete input must be UNCHECKED/FAIL for that gate, never silently omitted. Assert full input consumption, no unexpected leftover tokens, no parse-error recovery producing a successful executable, and no reuse of a stale output file after compilation fails. These invariants supplement structural equality; reaching EOF alone does not catch the reparenting above.

This export hook is a proposed developer/test capability, not a new public Sanskrit keyword or a shipped feature. Ordinary builds must remain byte-identical to the same candidate with the hook disabled. A test-only build must also be paired with normal production execution, so instrumentation does not become the only configuration validated.

### E. Price, implementation boundary and calibration

| Component | Planning estimate, not completed work |
|---|---:|
| Restricted tree model and the two renderers | 120–220 Python lines |
| Independent trace/state evaluator and fixture manifests | 80–150 Python lines |
| Bounded child runner, exact comparison, negative calibration and structured reporting | 100–180 Python lines |
| **Smallest useful behavior gate subtotal** | **300–550 Python lines; no compiler edits required** |
| Optional normalized AST exporter for this restricted node set | **140–240 NASM lines** |
| AST normalization/comparison and completeness checks | **60–100 Python lines** |
| **With direct structure checks** | **500–890 lines total** |

These are approximate engineering budgets for an authorized implementer, not time promises. Rich source-span plumbing, all grammar forms, import provenance and a full independent parser are outside this minimum. Reusing existing runners can reduce new code; incomplete error propagation must not be reused as an unexamined shortcut. No tool or source patch is delivered by this review.

Calibrate against the actual v264 counterexample and the corrected v265 result, with compiler hashes pinned. A deliberately wrong expected trace, a timeout and a failed child must make the top-level gate fail. For AST comparison, mutations that delete, duplicate, swap or reparent a distinct node must be rejected, including mutations preserving all node counts. This is calibration of the checker/oracle, not permission to modify the production compiler in this round.

Capture source/model/expected-result hashes, compiler hash, target/mode, compile result, native exit/signal, bounded output and timeout. Use fresh per-case output paths and an output cap: a program printing forever must not consume the runner's memory. Expected compile refusals are distinct from native passes; missing records and unexpected skips fail closed.

Start on the production Linux profile. Claim object/separate, Wine or real-Windows coverage only from their own results. Positive parser-shape cases should not depend on the guard-page allocator, and a parser dump on one host is not a native target execution.

**Acceptance for this first gate:** every agreed scenario has its independent expected outcome, the known bad interpretation is detected, no cases vanish from aggregation, and the direct-tree extension (when enabled) matches identity/parent/order rather than only counts. Passing 30 cases does not prove all parses correct. It closes a named, repeatable coverage obligation and can grow from a small trusted model.

## WS3 — what this means for K0

**Plain answer: not a logical refutation of the K0 design; a direct dependency and blocker for an unqualified implementation guarantee.** Calling it simply “orthogonal” conceals the dependency.

The assurance chain must include the frontend:

```text
source text is interpreted according to the agreed lexical/layout grammar
    -> the complete intended AST, scopes and bindings
    -> K0 checks that entire function under its stated restrictions
    -> code generation preserves the checked meaning and cleanup
    -> the claimed target/link/runtime assumptions hold
    -> the explicitly scoped guarantee
```

If checker and emitter consume the same wrong AST, the executable might still satisfy a **narrow memory property of that AST** while doing the wrong calculation or looping forever. The observed parser bug does not by itself prove a K0 use-after-free or unsoundness theorem. Conversely, checking the wrong scopes cannot establish correct implementation of the user's intended region/escape semantics. Both distinctions must remain visible.

For the future block, body membership decides which allocation is scratch, which exit rewinds it, and which assignment/call is inside the checked boundary. Therefore test the source-to-AST boundary before accepting a scoped-lifetime claim. An illustrative future fixture would place an outward pointer assignment late in an indented region body: dropping or reparenting it must not let the source be falsely accepted under an intended checked-block guarantee. That is a future K0 acceptance case, NOT something v265 can test merely by rejecting an unknown `mandapa` keyword.

Retain the current K0 policy: opt-in fixed-size numeric scratch; no unsupported `kosh` in the containing checked function. Do not permanently forbid `nirmmita` in loops, weaken escape rules, or rewrite the language around this parser defect. Also do not claim the 519-case builtin gate proposed in R142 is the smallest way to establish this parser repair; it addresses a separate, broader preservation obligation.

Once K0 is implemented, checker and lowering must use the same fully parsed representation, with consistent source/import identity. Parsing failures must not emit a partially checked program. Test accepted and rejected indentation/brace forms against an independent structural expectation, then test native cleanup paths. A prose scope rule cannot compensate for an unvalidated parser.

**Disposition for this round:** credit R70's specific repair and its reported baseline/fixed controls. Do not retain “allocator register clobber” as the established cause. The pinned review does not independently certify v265 or a K0 implementation; the block is still a future step. The new gate specification is additive to, not a replacement for, the previously identified access, retention, alias and result-propagation obligations.

## A note on the 6 ns claim — preserve the evidence boundary

The brief/changelog report 1,000,000 allocations in 6.4 ms. Dividing gives **6.4 ns per reported iteration/allocation**, rounded to 6, but that arithmetic is not an independent measurement of isolated allocator latency. R70's separate retained log reports **75–94 cycles per allocation** for its million-iteration measurements and **0.03 s wall / 62,464 KB RSS** for an indentation-form workload that writes each allocation. These are different reported observations; the inspected evidence does not establish identical harnesses, touch policy, clocks or timing windows. [R1,R2,R7,R8]

Do not silently replace either record with the other or infer a C `malloc` ranking from them. Keep source, actual completed operation count, touch pattern, timing method, baseline and environment together. With a preceding parser error, verifying the loop's count and effects is especially important before assigning a denominator. One million requests of 64 bytes represent 64,000,000 requested bytes; requested storage, touched pages and peak RSS are different measurements. No new benchmark was run here.

## Evidence ledger and status

All live repository reads below used the pinned SHA unless a historical commit is named.

- **R1:** `Sarvam-to-ChatGPT/ROUND-143.md`, `b4ebc2aa26621d310d131e2060aa414323e0ea0f` — three questions, corrected diagnosis and reported timing.
- **R2:** `Claude-to-Sarvam/R70-00-LOOP-FIXED.md`, `1ee1b19ce7dd501a1d9505232164083e4491b2ce` — reported disassembly interpretation, baseline comparisons, syntax/formatter change, tests and limits.
- **R3:** `Claude-to-Sarvam/evidence-r70/repro-four-compilers.txt`, `d8a40e34004bdd40b988ca62712a2f935bc73026` — partner's bounded first-lines record on v261/v263/v264/v265; not executions by this review.
- **R4:** `src/sutram_compiler.asm:7220-7410`, `da24e91db92cfa00d6cff1836627879858e1448d` — `parse_body`, `r70_indent_body`, `r70_line_indent`, parent/body indentation and comparison branch. Parser commit inspected: `f947ce92ab7a378b57f2afd45de7ce9e6194d030`.
- **R5:** `examples/258_r70_loop_indent.sm`, `3e794341451b0e9d629d11762cf63b2b69ca2c55` — exact repro and allocation/branch/control variations.
- **R6:** `examples/259_r70_indent_ambiguous.sm`, `36f9cf92902abe5afa08b3c3b19c53c2344ee142` — ambiguous-dedent negative source.
- **R7:** `Claude-to-Sarvam/evidence-r70/per-allocation-cost-v265.txt`, `2d878a6de8079f450799d5c44d61a73035c72ccb` — distinct reported cycle and written-allocation wall/RSS results.
- **R8:** `docs/CHANGELOG.md:1-85`, `d9e3d06b59187b5700c080f3fdb4741ac015574a` — v421 interpretation and timing; historical prose is not a new execution record.
- **R9:** `ChatGPT-to-Sarvam/ROUND-142-VARIABLE-PRESERVATION-GATE.md:1-26`, `25378daf2d001f0e349bb5e17428f57c8820b493` — previous return verified present; original uncertainty about root cause and separate backend gate.

**Outside context, not repository evidence:** LLVM's official Testing Infrastructure Guide (https://llvm.org/docs/TestingGuide.html, consulted 30 October 2026) distinguishes focused regression tests from whole-program tests and describes checking textual intermediate results. It supports a layered testing approach; it does not prescribe this Sutram model, the 30-case count, the line estimates or a safety certification. Those are this review's engineering proposals. No LLVM dependency or automated workflow change is requested.

**Performed here:** connected pinned-source/report reads; a small local Python illustration comparing equal-sized trees with different parent paths; arithmetic for the 30-case matrix, line-budget sums, requested byte count and reported time division. These are not native parser/compiler tests.

**NOT RUN — no native toolchain invoked:** historical/fixed reproducer, new gate, AST exporter, formatter verification, full-tree syntax census, compiler builds, Linux/PE/Wine/Windows execution, allocation benchmark, regression/proof suites or release qualification. No fresh code defect beyond the identified prose/branch policy discrepancy is claimed as an executed result.

**NOT APPLIED:** compiler, formatter, library, tests, tools, canonical documentation, language packs, workflows, Windows or backup changes. Add only this Markdown handoff under `ChatGPT-to-Sarvam/`; verify complete readback and single-file commit scope, then stop after Round 143.

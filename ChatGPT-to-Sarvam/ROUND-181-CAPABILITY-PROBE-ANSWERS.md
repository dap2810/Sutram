# R181 — capability probe answers

Base: `ea97309518b61e46a9454d50a01f2e7e22bd3598` (v291), 2026-11-03. This answers the probe only. No project implementation or merge.

## Task 1 — library function count

**306 prakriya definitions in the 24 immediate lib/*.smlib files.** Includes helpers/private functions; counts definitions, not distinct exported APIs, builtin aliases or recursive imports.

| Module | Definitions |
|---|---:|
| lib/aadhar.smlib | 2 |
| lib/ank.smlib | 10 |
| lib/anukram.smlib | 5 |
| lib/brihat.smlib | 13 |
| lib/chandas.smlib | 6 |
| lib/ganit.smlib | 18 |
| lib/ganita.smlib | 23 |
| lib/gudh.smlib | 2 |
| lib/kalana.smlib | 6 |
| lib/khand.smlib | 22 |
| lib/madhava.smlib | 5 |
| lib/mala.smlib | 8 |
| lib/nighantu.smlib | 17 |
| lib/patra.smlib | 3 |
| lib/phal.smlib | 14 |
| lib/roop.smlib | 23 |
| lib/sadhan.smlib | 7 |
| lib/samanvaya.smlib | 11 |
| lib/sangrah.smlib | 14 |
| lib/sankhyiki.smlib | 16 |
| lib/shreni.smlib | 14 |
| lib/suchi.smlib | 34 |
| lib/vakyank.smlib | 6 |
| lib/varna.smlib | 27 |
| **Total** | **306** |

Method: retrieved all 24 files at the pinned commit. Counted declaration lines; independently scanned tokens after removing Sutram # comments and quoted strings. Both methods returned the same names in the same order for each module. This is an executed text audit, not compilation.

Confidence: **high for this pinned set**; a different revision, recursive directory scope, or definition syntax missed by both scans could change the answer.

## Task 2 — constants and line numbers

In `src/sutram_compiler.asm`:

- **Line 8756:** `R101A_REGION equ 0x04000000` = **67,108,864 bytes (64 MiB)**.
- **Line 8757:** `R101A_MAXCAP equ (R101A_REGION - 40) / 8` = (67,108,864 − 40) / 8 = **8,388,603 elements**.

These are one-based lines in the pinned source, blob `029d8ea513f4f4d3dbd46007024d92fd35411e55`.

Confidence: **high**; line numbers change with source revisions, and this does not certify every allocator use of the constants.

## Task 3 — one-line unified patch

The separate file [R181-probe.patch](R181-probe.patch) contains only the unified diff below. Its only addition is the heading; the changelog itself has not been changed.

```diff
diff --git a/docs/CHANGELOG.md b/docs/CHANGELOG.md
--- a/docs/CHANGELOG.md
+++ b/docs/CHANGELOG.md
@@ -1,3 +1,4 @@
+## probe
 > **The 20 newest entries.** Older ones, from "v432" back to the first, are in [rounds/CHANGELOG-ARCHIVE.md](rounds/CHANGELOG-ARCHIVE.md) (split in R88).
 
 ## v291 (Claude, R109) - the outlives rule follows a second name and a chain of any length; the installer gate names the payload; the suite's summary is its last line
```

Executed `git apply --check` against a local copy of the pinned changelog: **exit 0, no output**. This was a patch applicability check, not an application to the repository.

Confidence: **high at the pinned base**; an intervening change to the initial context can prevent application.

## Task 4 — doubling arithmetic, worked without execution

**8 growth events; 1,020 existing elements copied.**

Initial capacity is already 4. Growth capacities:
4 → 8 → 16 → 32 → 64 → 128 → 256 → 512 → 1,024.

There are eight arrows. The final capacity is the first one at least 1,000. At each full-capacity growth, copy the old contents:

4 + 8 + 16 + 32 + 64 + 128 + 256 + 512
= 4 × (2^8 − 1)
= 4 × 255
= **1,020**.

The original allocation is not a growth event; inserting the 1,000 new elements is not copying old elements. There are nine allocated capacity stages if the initial allocation is included.

Confidence: **high under the question's model**; a zero-capacity start, reserve operation, in-place extension or a different copying policy changes the interpretation. No code/calculator was run for this task.

## Task 5 — one body/name mismatch

**File:** `lib/patra.smlib`. **Function:** `patra_asti(path)`, lines 81–86.

Its body opens the path read-only with `dvaram(path, 0)`; if the descriptor is negative, it returns 0; otherwise it closes the descriptor and returns 1.

The name suggests **“file exists.”** The actual predicate is **“this path successfully opens read-only under current conditions.”** Permission denial, descriptor exhaustion or another open failure returns false even when the file exists. Success does not establish that the target is a regular file. The nearby comments already acknowledge the open-versus-existence distinction.

This is a real API naming/contract mismatch, **not a newly discovered undocumented memory bug**. I would name/document it as an openability predicate or implement a separately specified existence query. No change was made.

Confidence: **high for the body-level distinction**; precise platform-specific open behavior requires execution, and an intentionally documented project definition of asti as openability would make this a usability issue rather than a specification violation. Native probe: **NOT RUN — no toolchain**.

## Task 6 — limits, and a claim I could not verify

- I cannot build/run the Sutram native compiler and suite in the current read-side workflow: **NOT RUN — no toolchain**. This turn's executable lookup found no NASM on PATH. That lookup alone is not a search of every installed file.
- I **can** execute available shell/Python/JavaScript tools and git checks. Saying “I cannot execute anything” would be false; the count and patch check above were executed.
- I cannot independently certify reported suite/guard results, timing, RSS, allocator behavior or crash absence by reading another agent's report. I can attribute them and inspect supporting artifacts.
- I cannot establish Windows installer, IDE, shell or native executable acceptance without the actual Windows run and evidence. ELF/PE structure or a matching hash is insufficient.
- I cannot claim to have seen a rendered page or desktop from source/Markdown alone. No rendered Sutram page or UI was inspected in this round. Browser/image tools may support a future requested inspection; that does not create evidence retroactively.
- I cannot verify a source claim when the relevant source/version is unavailable. Prior context and a report title are not substitutes for the bytes.
- I cannot certify Sanskrit compounds as a native-speaker review, or turn an English gloss into proof of grammatical correctness.
- Finite probes and static inspection do not prove all-program memory safety. Unknown paths and incomplete provenance remain possible.
- My authorized project role does not permit source/lib/tests/tools edits, Windows-to-Sarvam changes, frozen-pack edits, merge decisions or unsolicited CI/monitoring. These are scope limits, distinct from technical inability.

**Specific unverified claim in the last twenty rounds:** in R179 I treated `to` as a working old spelling that must be kept operational because it appeared in `r4_old_kw`. I had not established acceptance by following the retirement path or executing it. Claude R110 reported a syntax error on v291; R180 corrected my statement. The table showed a diagnostic/migration mapping, not proof of an accepted alias.

Confidence: **high about the actions performed and the R179 correction**; available tools and authorization can change, so these are current limits rather than permanent claims about the product.

## Task 7 — my specific errors

1. **Shipped error, R179:** inferred that `to` remained accepted from its presence in the old-keyword table. Correct answer: retired `to`, loop-bound `tak`, return alias `prati`. I should have traced the table's consumer before stating compatibility behavior. Corrected in R180.
2. **Caught before delivery, this probe:** my first text counter returned **240**, because I used a comment/string stripping pattern that did not handle Sutram's # comments. Apostrophes/quotes inside comments swallowed real declarations. Reading the module output exposed missing functions. I discarded the result and obtained 306 with declaration-line counting plus a #/string-aware scanner, agreeing per file. I should have used the language's actual lexical rules first.
3. **Communication weakness, R179:** I supplied a target operator table without putting current behavior in each cell. I did label it as proposed, but it did not directly answer “what each does today.” R180 corrected that presentation by showing current → target, including refusals and raw-address fallback. This was an answer-fit problem, not a measured compiler failure.

I have **one independently corroborated shipped factual error in this immediate review record**, plus the caught counting error and the answer-fit problem above. I will not invent additional incidents or claim this is an exhaustive audit of twenty rounds. The repeated request for a table is evidence that my presentation did not resolve the maintainer's question; it is not evidence that no table had been delivered.

Confidence: **high for the named examples, limited for completeness**; a systematic review of all twenty reports and their source bases could reveal more errors.

## Task 8 — who should do which job

**Claude: implementation and reproducible native verification.** Give Claude accepted, narrow contracts; require an exact tested revision, native commands, outputs, regression deltas and separate reporting of failures. In the evidence reviewed, Claude reproduced alias/long-chain escapes, measured the old arena's wrong answer, and distinguished the frozen-pack/scanner failures from a static name search. That is useful execution work. Do not let Claude self-approve a merge or equate passing existing tests with a proved lifetime rule.

**Muse: independent adversarial testing and user-facing semantic review.** Give Muse the exact candidate and contract, with authority to find counterexamples rather than defend implementation. Require boundary tests derived from the algorithm: 31/32/33+ propagation rounds, retained aliases, actual memory reuse, scanner whitespace and error-path behavior. Muse's earlier attack covered useful cases but missed a retaining chain and explicitly did not attack R178. A headline such as “held” must stay scoped to the actual tests. Sanskrit recommendations still need native-speaker acceptance.

**ChatGPT/me: read-side specification, source/evidence reconciliation and review preparation.** Use me to trace paths, compare report claims with actual commits, identify unchecked assumptions, write tables/invariants, enumerate attack obligations and prepare small review artifacts whose applicability I can test. R178's analysis-limit concerns led to independently reproduced defects, and R179 identified the prati collision; those are evidence for this role, not proof that I can replace execution.

My weaknesses are concrete: I can overinfer from a symbol/table name; use a familiar but wrong lexical pattern; give a target design when a current-state answer is wanted; and become verbose enough that a decision is obscured. I also lack native execution evidence in this role and native-speaker authority. Countermeasures: trace consumers, pin revisions, label executed versus inferred versus attributed results, make the requested table explicit, and lead each handoff with a short decision.

**The owner remains the decision-maker.** Intended semantics, vocabulary policy, compatibility exceptions and merges belong to the owner after independent evidence. For an implementation change: accepted contract → Claude candidate and measurements → Muse independent attack → my reconciliation of contract/source/evidence → owner decision. This is a review sequence, not a claim that every small documentation edit needs all three agents.

No agent should be the sole designer, implementer, tester and acceptance authority for the same memory-safety change. Windows UI/installer acceptance needs a person or agent actually operating the Windows environment. Final Sanskrit acceptance needs a qualified reviewer.

Confidence: **moderate**; this allocation follows the specific reports and capabilities visible here, not a controlled comparative benchmark of the three models. Revise it if measured performance or tool access changes.

## Delivery boundary

Only this answer and the requested unapplied patch are delivered. No source or changelog modification, no native suite, no CI, no arena merge, no project development.

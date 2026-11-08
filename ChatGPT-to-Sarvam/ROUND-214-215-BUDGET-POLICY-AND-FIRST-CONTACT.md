# R214–R215 — explicit budget policy and bounded release acceptance

Reviewed main: `108301e2155b7c48e3e6d88103910148662fd191`. Responds jointly to ROUND-214 and ROUND-215.
Read-side review; compiler/build/native Windows execution **NOT RUN — no toolchain used**. New native observations are credited to `WINDOWS-V312-FIRST-CONTACT-2026-11-08.md`.

## 1. Decision: a configurable step budget with a generous default

Of the proposed options I choose **a compiler flag controlling the analysis-step budget, with a generous default and a documented testing override**. This is a compiler resource limit, not a promise that every source expression has a predictable number of terms.

The rule that produces a default is:
- preserve previously supported valid inputs unless measured time/memory costs justify a compatibility change;
- bound actual work in the validator's own units;
- measure representative generated/adversarial inputs against the supported compiler resource envelope;
- publish the chosen default and its compatibility impact. Corpus headroom is supporting evidence, not the rule.

For this code, **200,000 remains my recommended default** absent new resource-cost evidence. The measured 52-step/12-term corpus maximum does not justify rejecting formerly accepted generated expressions merely to exercise a branch. The controlled-build test already exercises it. I do not propose an unlimited mode: increasing this budget must still obey AST, stack and integer limits and must never turn an incomplete validation into success.

Illustrative interface (proposal, **not implemented**): `--analysis-steps=N`. On exhaustion the compiler exits nonzero, emits no executable, names the limit and source location where available, and suggests splitting the expression or deliberately raising the limit. The diagnostic should explain that parsing/AST capacity limits may bind separately. Do not claim a fixed conversion such as “16,400 terms” for all shapes.

Tests:
1. Parse a valid override; reject malformed, negative, overflowing or unsupported values explicitly.
2. Use the same source at low and sufficient budgets: low refuses with E_VAKYA_SEEMA/no output, sufficient produces the expected result. Include local and global expressions.
3. Run a controlled build to exercise the failure path without shrinking the production default.
4. Retain compatibility probes for previously accepted generated expressions, plus existing refusals and scalar controls.
5. Record actual traversal steps, memory/stack use and compile time, not just term counts.

This is my recommended design direction, **not a newly imposed release blocker**. The project can deliberately ship 65,536 as a documented v1 implementation limit after accepting its compatibility cost. That resolves the disagreement as a policy decision rather than pretending 1,260x corpus headroom proves no user impact. A new flag need not delay otherwise accepted fixes.

## 2. Native rendering now has evidence

Credit the new native run: the actual licence control renders Sanskrit and Hindi as Devanagari, the em dash is correct, CRLF text matches the source, and the licence body wraps. Do not continue listing that rendering as wholly unverified.

Say **“verified on the recorded Windows configuration.”** Do not generalize to every Windows font configuration. A Wine font limitation belongs in test-environment notes unless Wine is a supported user deployment target. “Renders on Windows, not under Wine” is too universal: it reports an environment-dependent observation as a platform law. Correct decoded text alone never proves glyph coverage.

The remaining observed UI failure is the separate instruction label clipping “the terms to continue.” Native uninstall also leaves a new temporary script/log directory. Canonical files, association keys and PATH were removed; that functional success is distinct from the requested cleanup criterion.

## 3. Other first-contact checks worth prioritizing

These are **candidate checks, not discovered defects or a new unlimited release gate**. Existing evidence does not justify claiming that nobody ever tested them.

| Priority | Check | Why it follows from current evidence |
|---|---|---|
| High | All wizard page labels and buttons at the supported DPI/text-size settings, keyboard Tab order, Enter/Escape and accept/decline state | The clipped fixed-layout instruction shows that correct control text is not enough to prove usable layout. |
| High | Cancellation and failure before/after extraction, followed by retry | Temporary uninstall residue raises the same lifecycle question for unsuccessful and cancelled setup paths. |
| High | A genuinely new profile with Unicode/spaces in its account/install paths, and a refused unwritable destination | Existing-account acceptance does not establish first-run path and permission behavior. Preserve unrelated data on refusal. |
| Targeted | Another application's .sm association, followed by install/uninstall | Empty-key removal must not damage shared association state. |
| Targeted | Failure messages and log location remain accessible after cleanup | Deleting temporary scripts/logs can accidentally erase the only failure evidence. Clean successful temporary payloads; define intentional failure-log retention separately. |
| Later compatibility | Smaller display/high contrast/screen reader, long paths, security-product/download warnings | These require a declared support scope and cannot all be inferred from one account's screenshots. |

For the two active repairs, inspect the entire instruction at the intended supported scale and prove successful cleanup removes only this invocation's temporary files. Do not recursively remove a guessed TEMP prefix or delete preserved user backups. If a diagnostic log is intentionally retained, name its stable location and narrow the “nothing left” promise accordingly.

## 4. Corrections to R215's shared state

Please retain the following distinctions in the project record:
- “The ten tested escape shapes are refused” is supported; “a slice cannot escape” is broader than the tests and ignores the already disclosed trusted-context/raw-code limitations.
- The original v303 stall at file 132 is not proven to have the same cause as later v306/v307 Acronis suspensions. CRLF byte drift was measured; **CRLF as the security product's causal trigger was not established**.
- The 9.47/21.20/8.65-second figures belong to the v307 repair candidate, not this v312 package.
- Native v312 tested setup **5cca529c3569d4558cce3243becffea72c0eb2745ea345d8c049bb7177cb3c1b**. The shared state names rebuilt setup **2356014d…**. Do not label that rebuilt artifact natively tested without an identity/diff-based transfer or its own run.
- Windows/Linux equality of a reported PR #68 payload/manifest is not automatically full-installer reproducibility for every later main package.
- The native suite recorded 23.128 seconds versus an 18.6-second reference. One sample is not proof of a compiler slowdown or its cause; keep the observation, not an inferred regression.

## 5. The sentence that would support YES

**“YES for the documented v1 scope: this exact package passes the agreed acceptance checks, the clipped instruction and uninstall residue are resolved or explicitly accepted under a defined cleanup policy, the analysis limit and compatibility effect are documented, and transferred evidence names the unchanged components it covers.”**

That sentence is a condition for acceptance, **not today's verdict**. Current status is still pending the two observed acceptance findings and final-artifact reconciliation. Native rendering and walk-budget behavior now count as demonstrated; do not keep them open as though no evidence arrived. No additional speculative first-contact check above automatically reopens the agreed finite checklist.

No product source, tests, binaries, Windows evidence or workflows were changed; no CI or native tests were run.

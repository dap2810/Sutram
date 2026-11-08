# R213 — budget policy and the remaining native acceptance scope

Reviewed main: `06324cefc5c50a3c50fb68b6a2a43f50b800d339` (v312). Read-side review; compiler/build/native Windows/installer execution **NOT RUN — no toolchain used**.

## WS1 — a corpus maximum informs policy; it does not settle compatibility

My recommendation remains: **retain the prior 200,000-step production budget unless a measured resource cost or an explicit language-limit decision justifies reducing it. Test exhaustion with the supported low-budget build.** The new controlled-build evidence addresses the original testing request; lowering the shipped limit was not necessary to obtain it.

A 10x rule is a capacity-planning heuristic, not a safety or compatibility rule. Even 1,000x the largest checked-in example can reject a legitimate generated expression. Conversely, a much smaller margin may be acceptable if it is an intentional, documented language limit with predictable resource use.

Use this order:
1. Count the actual units consumed: popped traversal entries/steps, not source terms, bytes or distinct AST nodes.
2. Measure compiler time, peak work-stack usage and memory versus steps on representative and adversarial shapes, including generated code.
3. Choose an explicit supported resource envelope and check backward compatibility against previously accepted inputs.
4. Use a corpus maximum and headroom ratio as monitoring data; flag approaching the limit. Do not call a chosen multiplier a proof.

The proposed 331-example/library measurement is useful, but report the actual largest statement and its step count, source location, compiler configuration and coverage. “52” from the earlier reported corpus is not interchangeable with “200 terms” or a future measurement of every library body.

A valid 20,000-term expression accepted before and rejected now is a compatibility change even if no checked-in example uses it. The old guard's 0 DIFFER describes its 768 programs, not all valid programs. That change may be an acceptable v1 design choice; it should be decided as such, not justified only by wanting the failure branch to execute.

I will not require rollback of 65,536 as an automatic release blocker if the project consciously adopts and documents that limit. But the release notes must identify the stricter limit and avoid a universal “no existing program changes” claim. Likewise, the largest tested shape taking 87,316 steps does not prove all possible accepted shapes stay below 200,000. Say “not reached in these measurements,” unless a traversal bound proves more.

## WS2 — current v312 evidence and untested items

Claude R143 reports release-build wide-expression refusals and positive controls, a 64-step controlled build, Linux conversion-harness checks, package integrity checks, 77 passing gates, and the guard. The later Wine check reports Windows-compiler parity for 768 programs. These constitute meaningful implementation and regression evidence.

**No native v312 Windows report is present at this pin.** In particular, none establishes:
- the actual licence page displaying correct em dash, Devanagari/Sanskrit and Tamil glyphs, paragraph boundaries, complete final text and scrolling;
- Settings uninstall without a console flash, or a forced-failure notification with a usable log path;
- removal of empty association keys while preserving another application's values/subkeys;
- native behavior of the new production-budget boundary and its positive control.

The UTF-8 decoder harness tests converted units, not Windows font coverage, shaping, clipping or control rendering. The cause was addressed; the rendered result remains unverified.

Broader limitations remain as previously scoped, not new gates: no clean-machine/profile acceptance, no suspended-process timeout result, no atomic guarantee against arbitrary external writers, no formal memory-safety proof, and no automatic whole-setup reproducibility claim. Native v311 results and PR #68 payload comparisons retain their exact artifact identities. Unchanged-component evidence may transfer when identified; a v312/v313 label alone cannot transfer it.

The current release notes disclose the lack of native v312 execution. Keep that caveat adjacent to outcome wording: before the native run, “the decoder now produces UTF-16 with CRLF” is established more directly than “the page shows the licence correctly.”

## WS3 — acceptance decision

**A v313 release can be YES after the final artifact satisfies the already-agreed checks; it is not YES merely because someone launches the v312 installer.** If v313 adds product changes, validate those changes and document what evidence transfers from v312.

The short remaining sequence:
1. Record the budget-policy decision and its compatibility effect. Credit the controlled and release-build budget results; a native boundary/control check is appropriate for the final Windows compiler.
2. Inspect the final native licence page and exercise the repaired uninstall success/failure/registry paths, preserving another application's association.
3. Pin the setup/compiler/engine hashes, verify installed/embedded identity, and reconcile applicable earlier OOM/IDE/package evidence by component identity and scope. Do not rerun unrelated tests without a reason.

**Does Sanskrit rendering alone block?** For the full release acceptance requested here, yes: it is the outstanding verification of a known visibly broken first-contact screen, and a small direct native check can close it. This does not call an unseen result a failure. It also does not prohibit an explicitly labelled preview build. Inspect legibility and correct content, not cosmetic perfection; an unrelated aesthetic preference is not grounds to keep moving the release threshold.

Suggested notes after successful verification:
“On the named Windows configuration, this exact package displays the licence correctly and passes the listed install/uninstall checks. The compiler enforces the documented per-expression analysis limit; larger previously accepted expressions may need splitting. Prior evidence is reused only for the identified unchanged components. Untested environments and the stated raw-pointer, foreign-code, concurrent-writer and timeout limitations remain outside these results.”

**Current verdict: acceptance pending, not yet YES.** No new product defect is alleged by this response. No source edits, native tests, CI launches or merges were performed.

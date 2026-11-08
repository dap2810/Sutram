# R216 — exact boundaries, first-contact checks and artifact-ready briefs

Reviewed main: `a70b4321bf66a161b6a4df0d4760179e356fd637`. Read-side only; compiler/build/native Windows/installer execution **NOT RUN — no toolchain used**. Evidence cited below belongs to the committed Windows preflight.

## WS1 — what the ratio settles

**Yes: the existing diagnostic gives a concrete remedy, and the measured local-assignment boundary is deterministic for that program shape. No: it does not establish a universal four-steps-per-term language rule.**

The actual Windows BUDGET.md explicitly says:
- 16,384 terms compile/run and 16,385 refuse for local `vitti s = x+x+...`;
- steps are analysis visits, not source terms;
- global initializers and direct print expressions may differ;
- no cross-platform reproduction was performed in that round.

The earlier measured shapes also have different visit counts. R216's “exact boundary on both platforms” and “a programmer can predict it: four steps per term” therefore exceed the supplied evidence.

The remaining property is **an explicit compatibility/resource policy**, not another chosen number: does v1 intentionally refuse some previously accepted generated expressions, and is the limit documented as implementation work rather than a uniform source-term allowance? An actionable diagnostic resolves usability in part; it does not make that compatibility change disappear.

I accept 65,536 as a possible documented v1 policy choice. This is **not an independent release blocker and does not require a new flag before release**. My preference remains a generous configurable limit, but release can proceed with the present limit if the project adopts it consciously and describes it accurately. Do not keep the design discussion open merely to obtain unanimous preference.

Recommended documentation: “Each expression validation has a 65,536-step analysis limit. The number of source terms that fits depends on expression structure. If E_VAKYA_SEEMA occurs, split the expression into smaller assignments and combine the intermediate values.” Include a short worked example. The message is actionable for someone who understands its wording; the report does not claim novice usability testing.

## WS2 — the first-contact question was answered

The R214–R215 response has a priority table under “Other first-contact checks worth prioritizing.” To make it easy to assign:

1. **Layout and navigation:** inspect every wizard page at supported display scaling/text settings, including full instruction/error text, keyboard Tab order, accept/decline and Enter/Escape. The current wizard is fixed-size; do not request two user-resized widths. Change the test environment or use a deliberate test build if another layout size is needed.
2. **Cancellation/failure lifecycle:** cancel before and after extraction; fail setup/uninstall deliberately; verify unrelated files survive, retries work, temporary scripts are cleaned appropriately, and useful failure logs remain accessible under a declared policy.
3. **Genuinely new profile/path cases:** Unicode/spaces in username and destination, missing parent directories, and an unwritable destination. Existing-account tests do not establish these outcomes.
4. **Shared associations:** install/uninstall with another application's .sm values present; preserve those values and their keys.
5. **Accessibility/support scope:** smaller display, high contrast and assistive navigation where supported. These are targeted coverage candidates, not automatically new release conditions.

I cannot truthfully say these are defects “nobody has looked at.” They are plausible unverified cases in the evidence reviewed, not observed failures. The two established remaining findings are still the clipped instruction and this uninstall's temporary script/log residue. Do not turn this candidate list into an ever-growing release gate.

## WS3 — the smallest honest YES sentence

**“YES for the documented v1 scope: the exact final package passes the agreed checks, resolves the clipped instruction and temporary-file cleanup findings, documents its analysis limit, and identifies the tested configuration and any reused unchanged-component evidence.”**

That is the acceptance condition, not today's approval. The current candidate remains v312. A v313 installer has not been supplied in the reviewed tree. Credit existing successes; run the targeted changed workflows and reconcile exact identities once the final artifact exists. If logs are intentionally retained, define the location and cleanup promise explicitly rather than quietly treating accidental residue as success.

## WS4 — artifact-ready brief rule

**A test-ready brief must identify an existing immutable artifact, verify its embedded identity, and state what to do on mismatch before authorizing installation.**

Required fields:
- source commit and repository path/download location;
- full setup hash, embedded compiler hash and expected version;
- engine/payload identity where relevant;
- applicable baseline evidence and whether component identity permits reuse;
- exact checks, expected results, allowed machine changes, preservation requirements and NOT-RUN/blocked reporting rules.

Before issuing an executable acceptance brief:
1. Confirm the artifact exists at the pinned commit.
2. Hash it, extract/verify its manifest and embedded compiler identity without installing.
3. Where execution is available, verify --version natively; otherwise label that check as the tester's mandatory preflight, not as already done.
4. Require the tester to repeat identity preflight on the received bytes. On mismatch, stop product testing and report expected/actual identities; do not substitute “latest” or relabel an older result.

A planned brief may be written before a build exists, but its status must be **DRAFT — blocked on artifact publication**, without invented hashes or claims that the requested version is available. Any rebuilt byte change requires a new identity and a scoped evidence-transfer decision.

The Windows preflight did exactly the right thing: setup `2356014d...` embedded v312, so it recorded useful v312 baseline observations without installing or claiming a v313 result.

No product edits, CI launches, merges or native tests were performed in this response.

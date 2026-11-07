# R210 — validation placement, deletion races, and exact-candidate acceptance

Reviewed main: `e7eb31db73c847183f6ec3142ecfe9f9ab5b4b6a` (v310).
Read-side: compiler/build/suite/Wine/native Windows/installer/GUI **NOT RUN — no toolchain used**. This response answers design questions using source and committed evidence; it introduces no claimed new executed reproduction.

## WS1 — make validation unavoidable, not merely counted

Prefer a semantic validation boundary enforced by the generator interface over a grep that counts two known calls. But **do not simply insert the entire r137_check_stmt subtree walk into every recursive gen_expr invocation**.

For a tree with N nodes, walking each node's whole remaining subtree can take O(N²) work on a chain, rather than one O(N) traversal. It repeats checks many times, not just twice. On today's code, gen_expr performs r58_fold_tree near its entry; validation must precede any transformation that can erase the forbidden form. Revalidating later also observes a different AST or updated symbol state.

Duplicate checks are not guaranteed harmless to diagnostics. Traversal order, existing door checks, register/name classification and intervening transformations can change which error is first and whether an established E_KOSH_VIBHAG or E_KOSH_GANIT diagnostic wins. A repeated validator must also preserve registers, budgets and scratch state; do not assume the shared analysis stack is reentrant. The separate traversal-stack work described in PR #68 is relevant comparison material.

A practical design:
- Keep statement/context validation for non-expression conditions such as destination ownership and lifetime.
- Give every expression reaching numeric lowering a local kind/use check, including temporary results, with origin established before folding.
- Alternatively, validate a complete expression once through a mandatory checked entry and give the recursive emitter an explicitly internal interface. A cached validated mark must be tied to AST and semantic context and invalidated when either changes; a global “already checking” Boolean is not a proof.
- Enumerate all routes to the internal emitter, including globals, generated expressions and alternate compile modes. A new caller must be classified. A structural gate is useful here as an inventory assertion, not a substitute for the invariant.
- Preserve refusal order deliberately: test the exact existing diagnostics and positive controls, not just nonzero exits. Validate generated replacements or establish that they preserve the original checked kind.

This is not an instruction to add a costly whole-program type-system rewrite before release. A small common entry plus explicit internal-emitter discipline can be reviewable. The current two-call count still misses a third unchecked entry. Demonstrate the replacement gate with a deliberately added unchecked entry that causes the gate to fail; restore the source afterward.

**Additional precision:** unique AST nodes and traversal visits are not automatically the same number. The 43,690-node heap bound alone does not prove the 200,000-visit budget unreachable unless the walk's repetition/graph properties are established. The fail-closed branch is the useful guarantee; test it by forced exhaustion rather than needing a naturally gigantic input.

## WS2 — full hash fixes equality; it does not make the operation atomic

Under stable files, compare the full SHA-256 of the superseded copy against the full hash of the current target before treating them as identical. A 12-hex filename prefix and Test-Path prove neither equality nor integrity. A differing copy must cause preservation of both or a safe refusal.

With concurrent writers, even a full hash check can race:
1. Hash target and superseded copy: equal.
2. Another process changes either file or replaces its pathname.
3. Delete target: the comparison no longer describes the files affected.

The installer lock only excludes cooperating installers/uninstallers. An atomic rename prevents a half-renamed directory entry; it does **not** make the earlier hash and the later delete one indivisible operation or prevent writes through existing handles.

**Recommended bounded implementation:** avoid this deduplication deletion altogether. Move the current installer-owned target to a fresh unique backup name, record intent, and keep both copies until the transaction has safely committed. If moving fails because a writer holds an incompatible handle, refuse without deleting the source. If identical-copy deletion is retained, use stable handles/identity and sharing restrictions appropriate to Windows through comparison and deletion, and handle already-open writers explicitly; this needs native tests. Do not promise arbitrary-writer safety from Get-FileHash followed by File.Delete.

Check unequal existing superseded content, matching content, mutation between check and publication, locked-file failure, and interrupted retry. Record hashes of every preserved original. A post-commit backup-cleanup policy must not silently discard a newly discovered user edit.

This is narrower than the brief's phrase “deletes the only copy”: source shows a potentially unverified duplicate, but actual only-copy loss has not been reproduced by this reviewer. Keep the finding precise.

## New Windows evidence: useful, separately pinned

I acknowledge the published final repair handoff and PR #68 at `7ab8c439075b91278dd0e96bf000140a0ed26cf5`. It reports:
- 42/42 expanded entry-path cases, forced exhaustion, separate traversal stack;
- real two-process ownership fixtures, publication/reuse safeguards;
- Windows/Linux equality of 657 payload files plus manifest;
- native arithmetic, OOM, suite, recovery and selected IDE workflows.

The installed repair setup is `ffed7a486b0b3eab86c5a76afea32bc606e6b8b24feca4d8bc546cac99c9f0d7`; compiler `bcb33e6dbb58c1e8556d29057c2f20128cc00f54e48cf860c7ea5496c0972532`. The handoff explicitly says this is a **v309 repair branch**, not upstream v310; review/selectively integrate remaining differences rather than blindly merging superseded work. Payload equality is established for its reported Windows/Linux builds, not automatically for every main package. Whole-setup reproducibility is a separate claim.

R210 again combines 9.47/21.20/8.65-second v307 repair timings with v309 identity. Use the separately pinned Windows reports instead. The newer repair evidence adds real coverage and should be credited without relabeling it.

## WS3 — conditional YES, not automatic on a version label

**Yes, a v311 candidate can be accepted once its fixes and the finite R209 acceptance checks pass on that exact integrated artifact.** “Windows runs it” must mean the relevant checks, not only a successful launch.

Required evidence:
1. Global/local and expression regressions, safe controls, forced exhaustion, and a gate that actually rejects an unvalidated-entry mutation; diagnostic compatibility and the relevant compiler guard.
2. Superseded-copy preservation plus the named ownership/concurrency/publication/interruption tests. Reuse applicable PR #68 tests, but run them against the integrated engine.
3. Final setup/compiler/engine hashes; embedded manifest verification; native install, upgrade, late recovery, edited-file preservation, PATH and required IDE/uninstall checks; arithmetic/OOM controls tied to the final compiler. Evidence may transfer for genuinely identical components when that identity and test scope are documented.

**Present verdict on v310: not yet YES.** Native upstream v310 acceptance is absent and the two follow-up conditions remain open.

Release notes must distinguish:
- tested expression/lifetime rules from a formal memory-safety guarantee; raw pointers, inline assembly and foreign-code obligations;
- measured OOM cases from all possible allocation failures, startup-reserve failure and general teardown;
- recoverable file-by-file installation from atomic rollback of files/registry/PATH, and tested concurrency from arbitrary-writer safety;
- payload/manifest equality from whole-ZIP/setup reproducibility;
- selected IDE workflows from full IDE/uninstall acceptance;
- observed security-product behavior from a proved cause or future immunity.

Keep existing v1 feature exclusions and frozen non-Sanskrit-pack status. Name exact tested candidate hashes and any outstanding checks; do not waive a known destructive defect by documenting it. No source changes, merges, native execution or CI launches were performed in this review.

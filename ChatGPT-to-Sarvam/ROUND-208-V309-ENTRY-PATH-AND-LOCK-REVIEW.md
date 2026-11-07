# R208 follow-up — v309 native progress and two remaining coverage gaps

Reviewed main: `1a93b3ffff53a03544a048c95b03c55c53bb976d`. Latest ChatGPT assignment is still R208. This follows its expression-coverage and ownership questions against the new implementation; it does not invent a new round.

**Read-side:** compiler/build/suite/Wine/native Windows/installer/GUI execution **NOT RUN — no toolchain used by this reviewer**. Native observations below belong to the committed Windows report. Proposed programs and races are **NOT RUN**.

## What can now be credited

The Windows handoff `ChatGPT-to-Sarvam/WINDOWS-V309-2026-11-07.md` pins tested upstream `7c92bc02ff6f81b4903a20c14712ad3fd566b0c4`, compiler SHA-256 `05b23d56d40aaa4b71c6d67d13996d75da6e4d2e2b2ac47fbf4960a1a52fb481`, and setup SHA-256 `9d046b4e1b3d95222523e78304e48cb5bc10a69f951b33822a2673f0dc3bb533`.

- The original add/XOR 7/99 programs are both refused natively with E_VIBHAG_ANKA, exit 1 and no executable. Four broader refusals pass; the length control prints 2.
- The requested 32 memory-limit cases exit 1 with the expected stderr and no stack-overflow status or timeout.
- The installed v309 payload matches all 657 manifest entries. The native suite reports 322 PASS, three examples without expectations, six deliberate skips and no failures.
- Initial upgrade and two interruption retries complete. The edited-file case preserves the exact changed bytes and refuses; the observer error is disclosed rather than hidden.
- Source fixes preserve ambiguous legacy partials, put the transaction lock outside its cleanup directory, share that lock with uninstall, and recheck changed destination hashes before replacement.

These are meaningful improvements. The old v308 add/XOR finding is addressed for the tested v309 programs. It should not remain described as an observed v309 failure.

## C1 — global initialization bypasses the new statement validation (source gap; proposed reproduction NOT RUN)

The new `r137_check_stmt` is called by `gen_stmt` before statement dispatch. It walks expressions in ordinary statements; it is **not limited to named destinations**. For example, gen_stmt's default expression branch calls gen_expr only after that validation. The problem is a separate entry path:

1. The parser's `.pf_top_global` parses a scalar AST_DECL and registers it through `r56_register_global`.
2. `r56_gen_global_initializers` (src/sutram_compiler.asm, around 18311) loads each declaration's initializer from +16, calls `gen_expr` directly, then `r56_emit_global_store`.
3. It does not call `gen_stmt`, `r137_check_stmt`, or the assignment-door check.
4. The older binop check `rfx_is_kosh_operand` sees a bare AST_VAR, not a kosh-valued function call. The new R137 rule was precisely what caught the latter inside ordinary statements.

A narrow proposed reproduction:

```sutram
vitti zero = 0
vitti leaked = make_kosh() + zero

prakriya make_kosh() {
    kosh k[1]
    kosh_kship(k, 7)
    nivartanam k
}

mukhya() {
    likha(leaked)
}
```

**Prediction, NOT RUN:** the global initializer can still perform arithmetic on the returned kosh descriptor and store its numeric address. A matching local declaration inside mukhya should be refused by v309's new rule. This is a coverage/type-erasure candidate, **not a demonstrated new stale-slice read**. Verify both forms and the exact diagnostic; another check may reject the proposed program before emission. The allowed global function-call syntax is established by `tests/r56_check/initializer_calls.sm`; module-level array declarations are not required.

Fix direction: validate global initializer expressions at their actual entry point with the proper global context, and enumerate all callers that can reach expression generation outside gen_stmt. Add paired global/local negative cases and a valid scalar global-call control. `tests/r137/test_slice_number.py` generates its expression cases inside mukhya; its operator enumeration would not detect this missing entry path.

A separate hardening observation: r137_check_stmt decrements a 200000-node budget and exits normally on exhaustion. It does not explicitly refuse an incomplete analysis. **Reachability of exhaustion on a valid input has not been established here.** Either prove the bound for every accepted AST/traversal or reject on exhaustion; a safety check should not silently become incomplete.

## I2 follow-up — the lock still follows some ownership reads (static finding)

The journal read now occurs under the lock, but the claim “before any state is read” is too broad:

- `$oldState = Read-State $statePath` is at line 422.
- `$pending = Test-Path ...` is at line 426.
- The exclusive FileStream lock is acquired later, around line 437.
- `$oldState` is not reloaded under the lock. It is subsequently used for uninstaller ownership checks, PATH ownership, shortcut ownership and association ownership.

A possible interleaving is run B reading state while A owns the lock, A finishing and releasing it, and B then acquiring it using the old snapshot. A failed simultaneous acquisition correctly refuses; that does not cover the case where acquisition succeeds just after A completes. **This interleaving has NOT RUN here.** Depending on the stale values, it can yield a false ownership refusal or stale integration-ownership decisions. No observed user-file loss is claimed.

The static transaction gate compares the lock's position only against `Read-Journal`, while its description says “before any state is read.” That gate can pass this ordering. Move or refresh oldState/pending under the lock before decisions use them, and make the gate check those actual reads. The uninstaller already takes its lock before its Read-State call.

The edited-file native case establishes preservation for an edit made **before retry**. It does not test two concurrent installers or a write during publication. Those narrower limitations should stay visible.

## Payload and recovery evidence

`Windows-to-Sarvam/win-v309-2026-11-07/PAYLOAD.md` directly confirms the R208 newline prediction: README.md and docs/LANGUAGE-REFERENCE.md in the Windows checkout are CRLF and differ from the package; replacing CRLF with LF makes them identical. The language pack already matches. All 657 embedded entries verify against the package's own manifest. **The package is internally valid; cross-checkout/build determinism is still unverified and the Markdown rule is still missing.** The tested package was checked in, not a newly built Windows package.

`RECOVERY.md` distinguishes successful recovery from an optimization requirement: the late retry recreates all 657 staging copies, then recognizes matching target hashes and avoids per-file replacement. It completes; this is not data corruption or a failed recovery. A no-restaging shortcut remains an unmet requested behavior. The stop occurred after the last PUBLISHED record, not during a torn journal write. D1 stopped before any transaction existed. Backup/publish, finalization, COMMITTED/cleanup, torn-record and concurrency boundaries remain separate coverage questions.

## Updated release disposition

**NO to final release acceptance on this pinned main**, with narrower reasons than v308:

1. Reproduce/resolve C1 and ensure every expression entry path is validated; retain the passing native add/XOR and positive controls. Do not call the old programs still broken.
2. Finish ownership snapshot ordering and verify the outstanding transaction/concurrency boundaries with user-file preservation.
3. Complete the payload text policy and compare actual Windows/Linux staged manifests and embedded ZIP bytes for the final candidate.
4. Tie the required native installation/IDE/uninstall and failure-path acceptance to that final package. The new report explicitly adds no IDE acceptance claim.

Sarvam-to-Claude R140 already assigns packaging, documentation and lowering-path coverage. This follow-up supplies a concrete entry path and the remaining lock-order detail for that work. No source edits, test execution, CI launches, merges or Windows-to-Sarvam writes were performed.

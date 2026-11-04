# R204 — v303 fix review and release verdict

**Verdict: NO to general v1.0 release with only the native Windows run remaining.** v303 closes the three original R203 reproduction paths, but a directly passed kosh slice can still become stale during another argument's evaluation. The omitted-upper-bound slice path also retains the old upper endpoint. The first is a source-traced memory-safety blocker; the second needs an explicit semantic decision and regression. The installer payload is current, but the zero-configuration installation blocker and inaccurate release claims are not removed by a green version check.

**Pinned review:** `8154fdea7606b0e4febfb3b5e8fb9fafdfa44722`, compiler v303. The fix commit is `47c3791221d0f245dee8139b07d86d3fb61bec5e`; subsequent commits through the pinned head add the round briefs, not further source fixes. Read-side review only. The new probe outcomes below are source predictions, **NOT RUN**. Claude's Linux/Wine results remain Claude's observations; my independent observations are source inspection and the static file checks in `ROUND-204-STATIC-IDENTITY.json`.

## WS1 — what the three fixes actually close

| R203 finding | Review of v303 | Verdict within the stated scope |
|---|---|---|
| F1: index evaluation can move/shrink the collection after data/length were saved | `r128_emit_kosh_base` retains the descriptor when `r128_has_call` finds a call. After the index, `r128_emit_kosh_refresh` reloads length/data without replacing the computed index. Both read and assignment paths use it. Explicit slice bounds similarly refresh the backing after evaluating the bounds. | **The reported direct-index, assignment and explicit-bound reproductions are addressed at the cause. The broader stale-view class is not closed; see S1 and S2.** |
| F2: `(capacity + header_words) * 8` wraps into a small allocation | `r128_emit_cap_check` rejects a normalized declared capacity above `2^40` before the header addition and multiply. At or below that bound, both the 32-byte and 56-byte layouts and their alignment fit comfortably in the size arithmetic. The original positive `2^61` capacity is refused before allocation/stores. | **Original construction-overflow path closed by an explicit input bound.** This is not a proof that every later growth calculation is checked. |
| F3: region accounting reads syscall-clobbered r11 | `r127_emit_grow` now emits `mov rcx,[rsp]` before shifting/counting, using the saved new capacity. At this point the generated runtime stack's top is that saved capacity; the other saves and failure check remain intact. The compiler's own pushes while emitting code do not change this runtime-stack fact. | **Original register-clobber cause closed.** It does not certify all accounting paths or platforms. |

Source locations: `src/sutram_compiler.asm` at `r128_emit_kosh_base`, `r128_emit_kosh_refresh`, `r128_has_call`, `r128_emit_cap_check`, the indexed read/store paths; `src/r23_capabilities.inc:r23_gen_slice`; and `src/r65_arena.inc:r127_emit_grow`.

The conditional refresh is reasonable for the current checked expression forms: direct builtins, direct/indirect function calls and `prasar` are treated as potentially mutating, nested expression fields are searched, and depth 64 takes the conservative refresh path. It is not merely a check for the spelling `kosh_kship`. Keeping the no-call fast path to preserve existing code-generation ceilings does not itself weaken those cases. This is not a proof about arbitrary unchecked pointer/assembly effects or future AST forms.

**F2 qualification:** `R128_MAXCAP` is checked at declaration, not on every growth. `.ge_call_koshpush` still doubles capacity with a shift; `r127_emit_grow` shifts capacity into bytes and doubles the region request. “One push at a time” is not an arithmetic invariant. Enforce a stated maximum on growth too, or supply a precise supported-target argument showing why a prior allocation must fail before any unchecked transformation can wrap. I am not claiming an executable v303 growth-overflow reproduction: ordinary x86-64 address limits would intervene far earlier. This is a remaining invariant/defensive-check obligation, separate from the concrete S1 blocker.

The new R127 evidence is useful: Claude records all six added cases failing on v302 and passing on v303. The complete gate has **16 ELF checks and 8 PE-under-Wine checks = 24**, not 24 checks on each platform. The region-release index case, shrink case and large parimana case have `as_pe=False`; those particular new cases were not run as PE by this gate. Do not turn the aggregate into native Windows acceptance.

## S1 — direct slice arguments still survive a relocation without protection

**Source finding, execution NOT RUN.** This was a named gap in R203; the current fix has not closed it.

1. `r23_gen_slice` constructs a two-word slice containing a **raw element address and length**. It does not retain the collection descriptor as the source of subsequent accesses.
2. `gen_typed_call_arg` accepts a direct kosh slice, and accepts a whole integer kosh as an implicit `k[:]` for a `vibhag` parameter.
3. `.ge_funcall` evaluates expression-call arguments left to right and pushes each completed result. A later argument may call `kosh_kship` on the same collection or an alias.
4. Growth updates the collection descriptor and may release its old region. Nothing refreshes or pins the slice already produced for the earlier argument.
5. `r23_index_slice` in the callee uses the saved raw address and the slice's saved length. The bounds check cannot establish that this backing allocation still exists.

A direct reproduction for the implementation owner:

```sutram
prakriya pratham(vibhag s, ignored) {
    nivartanam s[0]
}
mukhya() {
    kosh k[1]
    vitti obstacle = nirmmita(8)
    chakra i = 1 tak 8388608 {
        kosh_kship(k, i)
    }
    likha(pratham(k[0:1], kosh_kship(k, 9)))
}
```

The first argument captures the old region. The second triggers the move beyond capacity 8,388,608; the old region is released. Source tracing predicts a read through that released address in `pratham`, potentially SIGSEGV. No foreign function, stored local slice, nested collection, thread or growth through a kosh parameter is involved. The release note's advice to “pass it on directly” permits exactly this form.

A small, cheaper probe exposes the same issue without requiring an unmapped page:

```sutram
prakriya badal(vibhag s, ignored) {
    s[0] = 99
    nivartanam 0
}
mukhya() {
    kosh k[1]
    kosh_kship(k, 7)
    vitti obstacle = nirmmita(16)
    likha(badal(k[0:1], kosh_kship(k, 8)))
    likha(k[0])
}
```

Source prediction: `0` then `7`, because the write reaches a retained old buffer. A supported live view of the collection must write its current first element, giving `0` then `99`, or the conflicting borrow/growth must be deliberately refused. Merely retaining old storage to avoid a crash leaves the silent stale-write problem.

**Order qualification:** `docs/SPECIFICATION.md` explicitly leaves a universal argument order unspecified, and statement-call generation currently evaluates arguments in the opposite order. That is why these probes deliberately use expression calls and why both call forms need coverage. Unspecified order does not authorize a checked slice to become a dangling pointer. Do not “fix” this by changing argument order: another ordering of the same two operations, or mutation during the callee's body, recreates the problem.

**Required resolution:** either represent a kosh view by stable descriptor identity plus offset/extent and revalidate it at use, or enforce a no-relocation borrow for the entire lifetime of the view. For a narrow v1 fix, conservatively refusing unsupported kosh-slice/call combinations is acceptable if the refusal is enforced and documented. A complete borrow must cover remaining argument evaluation, the callee and nested calls, and growth through every alias. Refusing only `vitti s = k[...]` does not do this. Do not silently turn a view into a copy; writes through a slice are documented to affect the original collection.

The separately issued Claude R129 proposal to enable parameter growth must include this boundary. The stable descriptor makes parameter growth feasible, but does not by itself make a simultaneous raw slice valid.

## S2 — an omitted upper slice bound is still the pre-mutation length

**Source finding and semantic gap, execution NOT RUN.** In `r23_gen_slice`, `.hi_len` loads the saved original length into rax for an omitted upper bound. `.hi_done` then refreshes the stack's length and data address, but **does not replace rax**, which remains the old upper endpoint.

```sutram
prakriya pratham(vibhag s) {
    nivartanam s[0]
}
mukhya() {
    kosh k[1]
    kosh_kship(k, 7)
    vitti obstacle = nirmmita(16)
    likha(pratham(k[kosh_kship(k, 8) - 1:]))
}
```

The lower expression appends 8 and evaluates to 1. Under the new post-bound collection-state rule and the reference's “to the end” description, the slice should be `[1:2]` and return **8**. The emitted omitted-upper path instead uses upper 1, builds an empty `[1:1]` view, and predicts a bounds refusal inside `pratham`. The added R127 slice test uses an explicit upper bound of 2, so it cannot distinguish this case.

This is not a claimed new crash, nor a claim that the old specification already settled every side-effect order. Choose and document when an omitted endpoint is evaluated. The consistent extension of the v303 fix is to obtain omitted `hi` from the refreshed length after evaluating `lo`, while leaving an explicit `hi` as its once-evaluated value. Add growth, shrink and clear cases for omitted `hi`, alongside the explicit-bound control. Do not describe the entire slice-bound class as closed until that rule is pinned.

## WS2 — release conditions, checked against R197

**NO: a successful native Windows run alone would not make this exact v303 tree shippable as the promised general v1.0.** It can remain a clearly labelled testing candidate. A future corrected candidate can be assessed on its own exact commit and payload; this review does not pre-approve it.

| R197 requirement | Current evidence | Remaining acceptance |
|---|---|---|
| Reconcile string contracts | v298 behavior and the current release notes distinguish in-place append, literal refusal and allocating string `+`. | Keep the existing R54/R121 regressions in final native acceptance. No reason to reopen the settled implementation choice here. |
| Resolve eager Windows commit | v300 lazy commitment is present; current linker was rebuilt to include that runtime. | Native commit/failure observations on the final Windows candidate remain required. Wine evidence is not native acceptance. |
| Attack the integrated candidate on both platforms | R128 gives discriminating v302/v303 cases and Linux/Wine evidence. Muse R129 attacked **v302**, not v303, and did not cover the R203 paths. | Resolve S1 and settle S2; verify the fixes on the candidate. The new Muse R130 request is an assignment, not completed acceptance. |
| Build installer from accepted commit and verify it | Static inspection confirms the payload's compiler, linker and IDE bytes match the pinned tree, and the manifest/hash checks below pass. | Clean native install/run/uninstall, Unicode paths and console, IDE behavior and installation-policy compatibility are not established by payload identity. |
| Publish accurate capability/cost reference and release notes | `docs/RELEASE-NOTES.md` now exists and includes the useful R197 exception/debugger/library-contract corrections. | The memory headlines still overclaim; see the corrections below. The general reference also retains stale memory text identified in R203. |

### Installer evidence I independently checked without executing it

The companion JSON records these actual static observations:

- Setup SHA-256 is `0a278682f8333419fcdb874674910c5201e85df741b7835f77fe061845b669e0`, matching `Sutram-Setup.sha256`.
- The embedded ZIP has 657 files, including its manifest. All **656 manifest entries** match their embedded bytes, with **0 missing, 0 mismatched and 0 unmanifested payload files**.
- Both embedded compiler copies are byte-identical to `win/sutram.exe`; their embedded version string is v303. The embedded linker and GUI are byte-identical to the corresponding pinned tree binaries.
- All **25 source-lock blob pins** match the checkout.

This verifies file identity and internal integrity, **not execution, publisher authenticity or reproducible build provenance**. I did not run the installer, compiler, linker or scripts.

The evidence chain for “68/0/1” also needs precise attribution: the checked-in full `gates.txt` ends **66 PASS / 2 FAIL / 1 NOT-RUN**. Claude then rebuilt the installer and reports passing reruns of installer-version, doc-counts and the R93 installer gate. The resulting **68/0/1 is the reconciled latest-result aggregate**, not a second all-green full-run log. This is a reasonable account of focused reruns; do not erase the original failures or imply a different log exists. Any later source/binary change requires acceptance of that changed candidate.

### The installer limitation is still a release condition

`windows/native-installer/README.md` explicitly calls unsigned-script blocking under Restricted/AllSigned an **unresolved release blocker for the zero-configuration promise**. R128 repeats that it was not resolved. A successful install on one permissive test machine does not remove that supported-environment restriction. Resolve the delivery/policy compatibility or explicitly revise the supported-installation promise; do not ask the learner to bypass security policy. The owner still needs to accept install and uninstall on the supported native configuration.

The IDE's retained previous output after rejecting a large file is also still disclosed, not fixed. Native acceptance must show that the failure is unmistakable and old output cannot reasonably be mistaken for a new successful run; otherwise it remains a classroom-release correctness issue. Partial English menus and lack of a full interactive debugger can be honestly scoped limitations without being confused with this stale-result problem.

### Corrections still required in the release notes/reference

The useful explicit-result, debugger, library-status/saturation and non-formal-proof wording should stay. Correct these remaining claims before publication:

- **“No limit on how many”** is false. Say the fixed 64 MiB reservation for every *small* kosh is gone. Finite allocation limits remain, and large-growth backings still reserve at least 64 MiB. v303 also now imposes a declared-capacity bound.
- **“A mandapa gives its memory back”** needs its actual scope: lexically allocated scratch nirmmita, with pages retained for reuse. It does not reclaim a block's kosh storage or ordinary helper allocations. `mandapa parimita` is not a whole-program/kosh budget.
- **“parimana reports bytes held”** needs the accounting scope and exclusions: occupied arena storage, retained arena buffers and regional logical capacity; not RSS/commit/virtual reservation, and ordinary fallback mappings are excluded.
- **“Running out of memory is a message, not a crash”** should cover the checked allocation-return and capacity-refusal paths actually tested. It is not evidence about every later first-touch commitment failure, process kill or arbitrary raw-pointer error.
- **“Pass [a kosh slice] on directly”** is not a complete safety condition while S1 exists. Fix or refuse the conflicting use before recommending it as safe.
- The v303 change list should say **declared capacities above `2^40` are now refused**, not that every capacity above `2^40` previously wrapped. The old `2^61` reproduction wraps; `2^40 + 1` does not overflow a 64-bit byte-size calculation.
- Distinguish **no user-visible general free** from the allocator releasing an outgrown private kosh region. Retaining the initial payload beside a stable descriptor can retain much more than 64 KiB when the declaration started large.
- The sentence that the v298 builtin defects were ones “Linux never showed” conflicts with R121's reported Linux reproductions. Say Windows testing exposed the bugs; a passing earlier Linux sample was not proof of correctness. Do not rewrite that history as Windows-only implementation defects.
- Muse R129's **24-byte header** and suggestion that parameter passing copies a descriptor are inaccurate implementation explanations. The layout is 32 bytes, or 56 with the extra lifetime metadata, before alignment; a typed parameter receives the descriptor address. Its growth refusal is a retained language restriction, not descriptor-by-value semantics.

The same-version-only object rule is now stated in the notes, which is progress. The linker still does not enforce it. Treat legacy/mixed objects as explicitly unsupported, require a clean rebuild for the representation change, and do not claim that every incompatible input is automatically refused. A version check remains the stronger future enforcement.

## WS3 — is the memory model finished?

**No.** The relevant remaining class is **a raw view surviving mutation of the collection it views**, including cross-argument evaluation, borrowed views passed down calls and future growth through parameters. S1 gives a source-level instance in the currently accepted language. Stable collection identity does not make a captured element address stable.

This is not a request to add generics, nested koshes, reclamation or threads before v1.0. Those can remain refused/deferred or explicitly scoped. The release obligation is that the accepted checked operations either obey their stated contracts or reject unsupported combinations before an invalid access. Repeated block-kosh retention, uncounted fallback allocations, raw/foreign pointers and mixed-version objects remain limits to state precisely; a finite attack set cannot certify their absence.

## Narrow next acceptance, then stop expanding this round

1. Reproduce S1 with both a small stale-write case and an actual region move; fix or refuse the conflict. Cover expression/statement calls, whole-kosh-to-vibhag conversion and growth through another alias. If parameter growth is enabled, include mutation inside the callee while a view is live.
2. Settle omitted-bound semantics and add S2 plus explicit-bound controls. Preserve the three original R203 regressions; do not change their expected results to fit a faulty implementation.
3. State/enforce the growth-size invariant. Correct the release claims and settle the installer support condition. Rebuild and hash the payload if its source or shipped contents change.
4. Accept the exact final compiler/installer on Linux and real Windows, recording output, exits, refusals, skips and native install/IDE/uninstall evidence separately. Reuse the established gates; no automatic CI trigger or background watcher is requested.

**Work performed here:** source/diff/test/evidence reading; static ZIP, hash and source-lock inspection; this handoff and its JSON evidence only. **Compiler build, Linux/PE execution, new reproduction probes, native Windows, Wine, GUI/install/uninstall and CI: NOT RUN — read-side role, no toolchain used.** No source, library, tests, tools, reference, packs or Windows-folder changes; no merge. Only documentation in `ChatGPT-to-Sarvam/` is delivered, pending independent implementation and acceptance.

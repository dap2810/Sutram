# R212 — bounded evidence, budget testing and acceptance repairs

Reviewed main: `f924ac3c643f7d606492e7500472a6ee08f366dd` (v311). Read-side; compiler/build/native Windows/installer execution **NOT RUN — no toolchain used**. Native claims below come from WINDOWS-V311-ACCEPTANCE-2026-11-07.md and its separately pinned earlier reports.

## WS1 — smallest honest evidence sentence

**“The pinned v311 package passed the reported Windows installation, compiler, IDE and recovery checks on one existing user account; uninstall worked functionally but left three recorded acceptance findings, and untested guarantees remain unclaimed.”**

The three findings collectively concern uninstall and licence display, not three uninstall failures. For detail: default install, Notepad's first program, reinstall, four IDE workflows and 322 suite passes are observed. The account's prior state was preserved and moved aside; this was not a new OS/VM/profile. Uninstall removed canonical files, shortcuts, PATH and Sutram registry values, but left an empty association key. Its exit code and console duration were not captured because observation started after completion.

Do not replace the earlier caveats with “verified end to end” without naming this scope.

## WS2 — keep a generous production budget; test exhaustion separately

**Do not lower the release budget merely to make a suite hit it.** That would create unnecessary refusals of legitimate large programs. A defensive failure branch can appropriately be unreachable under present input limits and still protect against future limits, transformations or violated assumptions.

But “43,690 unique nodes < 200,000 visits” is not a complete unreachability proof. The validator's budget counts traversal visits; shared nodes, repeated edges or unexpected graph structure can make visits differ from unique allocations. Prove the traversal bound if claiming unreachable. Otherwise simply say the branch is a defensive limit.

Use a controlled build with the same validator and failure path, replacing only the initial budget with a small test value. Test local and global expressions:
- a case below the limit compiles and has correct output;
- a case exhausting it returns nonzero, E_VAKYA_SEEMA and no executable;
- no crash/hang, and no silent partial validation;
- the ordinary release build accepts the same otherwise-valid case.

Record source commit, test define/diff, commands and statuses. Keep the production limit unchanged. This tests fail-closed behavior without confusing it with the independently verified parser-depth limit. The test build is not the shipped compiler; label it accordingly.

## WS3 — licence display: a concrete encoding mismatch

In `windows/native-installer/sutram_wizard.asm`, `license_to_utf16` does:
```asm
movzx eax, byte [rsi]
mov [rdi], ax
inc rsi
add rdi, 2
```
That is byte widening, **not UTF-8 decoding**. LICENSE.txt begins “Sutram — The Complete Thread”; its em dash is multibyte UTF-8. Widening each byte yields multiple wrong characters. The function even labels its input “ASCII,” but the file is not ASCII.

It also copies newlines unchanged. The normalized licence is LF-only; the destination is a standard Unicode EDIT control created with ES_MULTILINE. Convert its display copy to the expected CRLF newlines, rather than changing canonical licence/package bytes. These two independent conversions explain the corrupted dash and joined lines.

Recommended repair:
1. Decode the bounded licence byte span as UTF-8 into UTF-16, with checked conversion and buffer sizing. Do not silently truncate a multibyte sequence.
2. Normalize display newlines to CRLF without doubling existing CRLF; preserve paragraphs and all licence text.
3. Render and inspect the actual page, including its final paragraph. Check scrolling, accept/decline behavior and Unicode text.
4. Preserve the canonical UTF-8/LF file and package hashing convention.

For the other findings:
- Remove the Sutram OpenWithProgids value, then remove its container only if it is empty and safe to remove. Preserve other applications' values/subkeys and pre-existing ownership assumptions; never recursively delete the shared .sm tree.
- Audit the uninstall launch path and any cleanup descendants for console creation. The normal install child already requests CREATE_NO_WINDOW, while another CreateProcessW call in the wizard sets creation flags to zero. Trace the actual uninstall call before assigning blame. Observe the process tree and completion/error behavior after a hidden-launch change; hiding a window is not permission to hide failure.

## WS4 — conditional YES for v312, not approval before evidence

**Yes, v312 can meet the existing release conditions with the budget demonstration, repaired acceptance findings and honest evidence scope.** The version number alone is insufficient. Review the actual diff and pin the rebuilt package; recheck the changed licence/uninstall/registry workflows on Windows, including preservation of another application's association. Reuse unchanged compiler/IDE evidence when component identity and test scope support it; do not gratuitously rerun everything.

Also finish the already-requested evidence reconciliation: attach the applicable OOM and payload/build results to the final component hashes or run the targeted missing check. This is not a new product requirement. Payload integrity, cross-platform payload equality and whole-setup reproducibility are separate claims.

**Current v311 verdict remains NO for final acceptance**, because the controlled budget result and the three repairs are not yet provided. Credit the IDE workflow and functional uninstall as executed; do not keep calling them wholly untested.

Release-note wording to retain:
- Tested on the recorded Windows account/configuration, not a clean machine/profile.
- Named compiler/borrow cases are checked; this is not formal memory-safety proof or a guarantee for raw pointers/foreign code.
- OOM claims apply to the recorded tests and component identities, not every allocation failure or teardown path.
- Recovery is file-by-file at the tested boundaries, not atomic system-wide rollback; full-hash-then-delete is not atomic against arbitrary external writers.
- State precisely which installer, IDE and uninstall workflows passed, and which remain untested (including the suspended-process timeout).
- Distinguish package manifest integrity, payload equality and whole-installer reproducibility. Do not infer security-product causality.
- Retain existing v1 feature exclusions and frozen-pack status.

No source edits, tests, CI launches or merges were performed in this response.

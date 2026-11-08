# R218 follow-up — v314 review: compiler progress, shortcut ownership still unsafe

Reviewed main: `a05b058049d6fcb5a11c0af266f2c5cb84e5d272`, 8 November 2026 (America/Toronto). No new Sarvam-to-ChatGPT brief since R218. This responds to the newly published Claude R152 implementation/report and its Wine follow-up.

**Compiler/build/suite/native Windows/installer execution: NOT RUN — read-side role, no toolchain used.** Findings below are static source traces; reported test results belong to Claude. No product source changes.

## 1. A concrete shortcut ownership defect remains

**Do not accept the desktop-preservation claim yet.** The new desktop logic and its existing helper disagree about ownership. This is a sequential path, not the previously discussed concurrent-writer race.

### A. An existing user shortcut can be adopted and later deleted

Sources: `windows/native-installer/install-core.ps1:New-Shortcut` (367 onward), desktop selection block (714–735), state serialization; `windows/native-installer/uninstall-core.ps1` desktop deletion block (164 onward).

Trace:
1. No previous installer ownership exists. The user already has a desktop `Sutram IDE.lnk` targeting the intended `$guiInstalled` path, possibly with custom arguments/icon. A shortcut can predate the installation or be a user's manually created link.
2. `$isOurs` returns true solely because TargetPath matches. The selection logic does not choose the alternative name.
3. The caller invokes `New-Shortcut`. That helper sees an existing path absent from oldState.OwnedShortcuts, logs preservation and returns **without creating it or adding it to the new ownedShortcuts list**.
4. The caller nevertheless unconditionally sets `$desktopOwned = $true`. It writes DesktopOwned=1 and DesktopLink=Sutram IDE.lnk.
5. Uninstall trusts DesktopOwned and the matching TargetPath, independently of OwnedShortcuts, and removes the user's preserved link.

Thus the helper's preservation is undone by state serialization and the later uninstall. **A matching target is not evidence that this installer created a file.**

### B. A previously owned but user-retargeted link can be overwritten

On a later installation, previousDesktopOwned=true and the old encoded path remains in OwnedShortcuts. If the user has changed that link to Notepad:
- the new preservation condition includes `-and -not $previousDesktopOwned`, so it does not preserve this case;
- New-Shortcut authorizes replacement from historical OwnedShortcuts membership;
- it rewrites TargetPath and other supplied fields and saves the link.

This is not a newly introduced guarantee: some historical behavior was already unsafe. It remains a concrete counterexample to the current broad preservation claim. Uninstall's target check does not protect the earlier setup overwrite.

### Required correction and focused validation

Make shortcut creation return an explicit result: created/updated-owned/preserved/failed. Derive DesktopOwned and OwnedShortcuts consistently from that result. Do not adopt ownership merely from target equality, and do not treat historical path membership as permission to overwrite a user-modified link. Record identity of a created shortcut and preserve changes, or use a fresh unoccupied name without replacing the changed file.

If both canonical and alternate names are occupied, preserve both and show a visible route to the Start-menu IDE; current code only logs that no desktop shortcut was made. Avoid claiming the requested desktop icon always exists.

Requested native cases, **NOT RUN here**:
- fresh install with an unowned same-target custom shortcut; install/uninstall preserve its bytes;
- reinstall after retargeting the previously owned shortcut; preserve changed bytes;
- both desktop names occupied; preserve both and explain the outcome visibly;
- ordinary empty desktop and original Notepad collision; create/remove only the installer-owned shortcut.

The R143 first-contact gate currently checks text patterns and presence of the alternate name/state fields. It does not exercise these branches. Its pass does not refute the traces above.

## 2. FFI correction is at the right shared boundary

The added check in `src/r32_ffi.inc:r33_gen_foreign_funcall` runs before kind conversion/emission. A bare whole-kosh name remains subject to the existing kind handling (ptr allowed; scalar rejected); other arguments go through r134_holds_kosh.

Static reading supports rejection of the original direct kosh-slice argument, named slices including mala-backed names, and conditional slice values classified as mixed by r126_value_kind. Direct mala slices remain rejected by the enclosing walk. This closes the specific missing-check path discussed in R218 for the normal statement and expression routes, because both use this foreign generator.

Claude supplies actual v313/v314 evidence: the old direct ptr slice produced a descriptor-derived result and the old i64 count slice crashed; v314 rejects those inputs. The dedicated Wine check uses a valid msabi FFI sidecar and observes exit 1/no object for the new shape. Credit this evidence.

Scope corrections:
- The committed fifteenth fixture is an **expression call** through likha. The dedicated evidence shows ptr and i64 literal cases, not the entire statement/expression × ptr/i64/f64 × named/conditional matrix requested in R218.
- The broad 783-program Wine comparison runs the FFI fixture **without --ffi**, so its unknown-name rejection is not evidence of the FFI fix. Use the separate FFI evidence for that claim.
- The FFI rejection routes through r126_fail_door, which names the value/callee but does not print a source line. “With the line” in the report title is not supported by that path.
- The old statement-call branch still bypasses r129_check_call; the new shared boundary now rejects slices before generation. Do not rewrite the old trace as if all foreign call forms took .unknown.

No new runtime escape is claimed here. Add the targeted missing variants to the evidence rather than inferring universal boundary completeness from fifteen shapes.

## 3. The budget flag now exists; “to the letter” is too strong

The source now defaults to **200000**, scans the flag before ordinary argument processing, rejects duplicate/malformed/out-of-range values, and resets each walk from r152_steps. The checked accumulation avoids overflow. Claude reports 40 flag checks, plus the exact 87315-refuses / 87316-succeeds boundary for its measured expression and override of the low-budget test build.

This resolves the principal R218 mismatch: v314 actually has the flag, unlike v313.

Remaining differences from R217:
- malformed flag code is E_PARIKSHA_PADANI rather than the proposed E_PARIKSHANA_VIKALPA; exact text differs;
- analysis exhaustion prints function context or a top-level description, not the requested location/fallback line;
- AST exhaustion still has no distinct stable E_VRIKSHA_SEEMA code; its hint mentions E_VAKYA_SEEMA only to say this is another limit;
- the AST hint suggests splitting long expressions. This may increase total AST storage and is not a reliable remedy for arena exhaustion;
- the 40-check test helper deletes the output before each case, so it does not establish preservation of a pre-existing output. That property needs its own focused check.

Wording differences alone need not block release if explicitly adopted. A practical small correction is a distinct AST code plus “reduce the compilation unit / imports,” while preserving the legacy translated first line if necessary. When no location is available, state that honestly; R217 already allowed unavailable locations and did not require enlarging every AST node before release.

The language reference's “a program meets two limits” is still not exhaustive: block/nesting/work-stack and other capacities remain. Say “these two limits” instead. The static arithmetic gate does not establish the no-revisited-nodes premise behind the universal 349521 bound; the current configurable-limit policy does not require that unproved universal claim.

## 4. Evidence and release decision

Claude reports:
- Linux/Xvfb: 78 PASS / 0 FAIL / 1 NOT-RUN; suite 327 PASS plus 4 without expectations; crash corpus 227/0.
- v313 → v314 comparison: 587 identical outputs + 195 identical refusals + 1 new fixture = 783 programs, zero differences among existing cases.
- Windows compiler under Wine: 587 matching PE outputs and 196 refusals, with the FFI qualification above.
- candidate setup SHA-256: `a0e786e44d26780ef5f20f4103eaefdd7b33474762ebd41611499144cc4e03eb`; contributor payload/version check and Wine self-test pass.
- **Native v314 install/IDE/uninstall acceptance: NOT RUN.**

**Verdict: v314 remains a candidate.** The compiler changes make substantial progress, but the deterministic shortcut ownership/deletion path must be corrected before endorsing preservation, and the final package needs the agreed native acceptance. The licence-label and staging-cleanup changes still need that native observation.

Do not automatically turn every item in Claude's twelve-row remaining-work list into a new release gate. Distinguish concrete defects, the agreed final-package verification, and explicitly documented coverage gaps. The shortcut findings above are concrete traces in a workflow just changed, not an expanding wish list.

No production edits, test runs, CI launches or merges performed. Documentation follow-up only.

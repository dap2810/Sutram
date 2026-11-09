# R220 follow-up — v315: AST diagnostic complete, ownership repairs partial

Reviewed main: `308c21611c149b11531e324678fc2bf2c1eee1b2`, 8 November 2026 (America/Toronto). No new Sarvam-to-ChatGPT round; this reviews Claude R154 and its changes since the R220 response.

**Compiler/build/suite/PowerShell/native Windows/installer execution: NOT RUN — read-side role, no toolchain used.** Source traces are not runtime reproductions. Execution evidence below is Claude's.

## Completed improvements

1. **AST exhaustion has its own stable code.** src/sutram_compiler.asm now emits E_VRIKSHA_SEEMA after the preserved translated line, and explains that splitting statements does not shrink the AST. The analysis hint references the distinct AST code. Claude's analysis-steps log reports 42 checks, including AST refusal with exit 1/no output. This closes the previously missing-code and misleading-AST-remedy findings.
2. **User-added class descendants are no longer recursively deleted.** The Sutram.Source cleanup removes matching default values and then only empty keys. In particular, an added shell/edit verb should survive this source path. This addresses R219's specific whole-class-deletion trace; native verification is still pending.
3. **PATH removal is narrower.** PathAdded replaces the uninstall boolean as the selector, and removal stops after one matching entry. It no longer expands variables while selecting that entry or deletes every equivalent entry.
4. The folder comparison and compiler logs identify v315, with 587 identical outputs and 196 identical refusals across the 783-program comparison, zero differences. The supplied R137 log explicitly reports plain-build identity for ELF and both PE compiler copies. Do not confuse the broad comparison's FFI unknown-name refusal with the dedicated --ffi boundary check.

Candidate setup SHA-256: `06eba09b1b0064e854625542d1503e554b688df2b52d8760d0c370bfd50b8021`. This replaces the R153 package. Claude reports 78 PASS / 0 FAIL / 1 NOT-RUN, suite 327 PASS plus 4 without expectations, crash corpus 227/0, and Wine compiler/package checks. **Native v315 acceptance remains NOT RUN.**

## 1. Legacy shortcut migration is unchanged

R220's concrete counterexample still applies. Test-OwnedShortcut calls Test-ShortcutSays for hashless legacy records; that compares only target, arguments, working directory and icon.

A legacy link changed only in Description, Hotkey or WindowStyle is still accepted as unchanged. It can be removed during an unchecked reinstall or adopted with a new hash and later deleted. The R153 fixture still expects legacy-template adoption and does not test a change only in an unexamined property.

This is not a demand for a more complicated hash: the original bytes were never recorded. Preserve hashless legacy links without claiming ownership from a partial field match. Use a fresh name if a new desktop link is requested. The current source does not support “all four comply now” under the claimed modified-link preservation contract.

## 2. Registry cleanup is less destructive but still lacks before-state

Sources: install-core.ps1 class/default/icon/OpenWith registration and AssociationSet block; uninstall-core.ps1 expectedCommand branch.

The class command and icon values are compared to reconstructed expected values on uninstall, but **there is no record that those particular values were absent before this install or what their previous values/types were**.

Remaining sequential cases:
- A pre-existing class with the same expected open command is accepted. Setup writes the icon and uninstall deletes the matching command/icon defaults. “Matches the value we would write” still does not establish that removal restores the user's prior state.
- A pre-existing .sm/OpenWithProgids/Sutram.Source value is still overwritten during setup and removed unconditionally within the matching-command branch. No ownership/before-value record protects it.
- An explicitly empty .sm default is treated as absent, set to Sutram.Source, then deleted on uninstall. Its original present-empty value/type is not restored.
- The separate Uninstall/Sutram product registry tree still uses recursive deletion based on matching InstallLocation. User-added values there are not protected by the class-tree fix.

AssociationSet records the **after-value**, not the complete reversible mutation. It improves clarity and drops stale ownership when a different default is observed, but merely replacing a boolean with the constant string does not solve absent-versus-empty, pre-existing-equal, or recreated-value ambiguity.

Required narrow correction: for values the installer changes, record existence, old value/type, and installed value/type; restore/delete only when the current value still matches the installed state. Preserve pre-existing equal values without newly claiming them. Remove keys only when empty. Keep class cleanup and OpenWith/default cleanup independently governed by their own records; one matching class command is not proof of ownership of all related values.

## 3. PATH: remove-once helps, but “exact text; every other entry unchanged” is false

Both copies of Remove-UserPathEntryOnce:
- compare item.Trim() using OrdinalIgnoreCase;
- skip all whitespace-only/empty entries;
- add every remaining item.Trim() to a rebuilt list;
- write the whole value as RegistryValueKind.ExpandString.

Thus they do **not** perform byte-exact selection or preserve all untouched text/type. Example, as a static string trace:

Before: ` <drive>\Keep ;;<drive>\Sutram\bin;<drive>\Keep `
Recorded PathAdded: `<drive>\Sutram\bin`
After removal: `<drive>\Keep;<drive>\Keep`

The selected occurrence is removed, but whitespace and the empty segment elsewhere also change. A prior REG_SZ is rewritten as REG_EXPAND_SZ. The same trimming/type behavior also exists in the insertion helper. This is a concrete mismatch with the preservation promise; no particular application failure is claimed.

Choose precise wording and behavior:
- if the contract is exact textual reversal, remove one identified span and separator while preserving all other spans and the registry value kind;
- if case-insensitive/trimmed matching is deliberate, document it as such, but still avoid rewriting unrelated entries;
- handle later duplicate/recreated entries under the explicit ambiguity policy from R220. Removing one leaves another when two equal strings exist; it does not establish who authored the removed occurrence or restore the historical pre-install PATH in every sequence.

Also correct two report claims:
- **No duplicate append is not deduplication.** Existing equivalent duplicates remain; setup does not collapse them.
- **Legacy flags are still read during reinstall.** install-core.ps1 reads PathOwned to infer previousAdded, AssociationOwned to infer AssociationSet, and DesktopOwned/legacy DesktopShortcut to select a prior desktop name. Uninstall no longer using those booleans is a narrower, accurate claim. The PATH flag can still authorize a remove-once operation during legacy migration.

These are chiefly contract/implementation alignment issues; do not claim a wholly new arbitrary PATH deletion or that the initial pre-existing-equivalent case appends a duplicate.

## 4. Structural tests do not establish the preservation cases

The R143 additions assert source spellings and branch fragments. They are useful tripwires but do not exercise pre-existing-equal values, empty defaults, legacy properties or raw PATH/type preservation.

The report says a PATH/association fixture would have to modify the real HKCU Environment/Classes keys. That is not required. A safe design can:
- isolate PATH transformation into a pure function over raw text, value kind and ownership record;
- make registry operations accept an injected root/adapter;
- exercise a temporary test subtree or an in-memory adapter for create/update/restore decisions.

That allows focused behavior checks without modifying live user configuration. It does not replace the final native test, but it is a practical way to validate these branches before handing off the candidate. No such fixture was created or run by me.

## Disposition and bounded next work

**Accept the distinct AST diagnostic and the source-level fix for preserving extra Sutram.Source descendants. Keep installer ownership acceptance open.**

Before calling the ownership changes complete:
1. Preserve hashless legacy shortcuts and cover metadata-only changes.
2. Record before/after state for class/default/icon/OpenWith values; preserve user additions in the product registration tree.
3. Make PATH reversal preserve unrelated text/type, or narrow and explicitly adopt its policy without claiming exact reversal.
4. Verify these targeted cases, rebuild once, then run the agreed native acceptance on the exact final setup.

No fresh round number is invented here. This is a follow-up to R220 on the new v315 candidate, not release approval.

No production edits, compiler/test execution, CI launches or merges performed.

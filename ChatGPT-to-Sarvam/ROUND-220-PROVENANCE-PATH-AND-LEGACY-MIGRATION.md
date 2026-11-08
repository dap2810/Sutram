# R220 — provenance versus content, PATH equivalence, and association ownership

Reviewed main: `21267969ded51240b1b6ecd132c06ca9463f9e7b`, 8 November 2026 (America/Toronto). Read ROUND-220, R153 source changes/report and the new Windows shortcut fixture. Compiler remains v314; setup is a new artifact, SHA-256 `573e5feb236313576f0081eb750e1684a5ea101d14cc611df69bdabd068a9959`.

**Compiler/build/suite/PowerShell/native Windows/installer execution: NOT RUN — read-side role, no toolchain used.** Static findings below are not native reproductions. Claude explicitly reports the new Windows fixture NOT RUN.

## WS1 — content equality is necessary for this policy, but is not provenance

**A content hash alone does not establish ownership.** The R153 new-record design is stronger than that slogan: it requires a recorded path from an installer operation **and** a matching current hash. That distinction matters.

- A user-created or copied link at an **unrecorded path**, even byte-identical to an installer link, must remain unowned. Get-OldShortcutRecord returns null, so the new path does preserve this case.
- A matching hash at a recorded path establishes equal bytes, not an uninterrupted history of the same filesystem object. If a user deletes the link and replaces it with an identical copy, path+hash cannot detect that intent.
- Define the practical contract as: “remove the unchanged bytes at paths this installation recorded as created/updated.” Do not say the hash proves who created the current object or that nobody has changed it.
- If the product promises to preserve even byte-identical replacements, it needs additional object/generation identity (and conservative behavior when it cannot be established), not more hashing. That stronger promise is not needed to correct the original unrecorded-user-link bug.

The record must be tied to the actual successful write, specific installation/path and expected post-write content; migration must not invent that provenance. Hash checks also do not make a later deletion atomic against an independent writer. Keep that separate limitation explicit.

### Remaining concrete hole: hashless legacy adoption

In install-core.ps1:
- Get-OldShortcutRecord returns an empty string for an old path-only record.
- Test-OwnedShortcut then calls Test-ShortcutSays.
- Test-ShortcutSays compares only TargetPath, Arguments, WorkingDirectory and IconLocation.
- Set-OwnedShortcut can then update the link and record a new hash; Remove-OwnedShortcut can immediately delete it when the desktop option is unchecked.

A sequential counterexample:
1. A legacy installation recorded a shortcut's path but no hash.
2. The user changes only its Description, Hotkey or WindowStyle, leaving those four compared fields unchanged.
3. Reinstall accepts the four-field match as “unchanged.”
4. If the shortcut remains selected, the helper adopts its current bytes into a new ownership record and later uninstall can delete it. If unchecked, Remove-OwnedShortcut can delete it during reinstall.

No race or hash collision is required. Even if Save preserves the customized property, the later ownership/deletion decision is still wrong under the stated “changed shortcuts are kept” promise.

**Small safe fix:** treat hashless legacy records as insufficient for destructive action: preserve them, do not adopt them into hash ownership merely from a partial field match, and use a fresh desktop name where needed. Retaining a legacy shortcut is preferable to claiming knowledge of its original bytes that was never recorded. The current fixture's legacy test explicitly expects adoption and tests changed Arguments only; add a changed-only Description/Hotkey case and change the migration expectation.

For current hashed records, the original unrecorded-user-link and ordinary retargeting paths are addressed in source. Native verification remains pending. Do not call the whole preservation contract closed while the legacy exception remains.

## WS2 — PATH: the brief's initial sequence is not what the code does

Source: install-core.ps1 Normalize-PathEntry / Set-UserPathEntry and the PATH caller; uninstall-core.ps1 Remove-UserPathEntry.

**Setup does not add a second entry when an equivalent one already exists in the user PATH. It also does not deduplicate existing duplicates.**

Normalization trims whitespace, surrounding quotes and trailing backslashes, expands environment variables, and compares case-insensitively. The target is the installation's bin directory, derived from InstallDir; uninstall is not removing an arbitrary PATH entry just because the flag is true.

| Sequence | Actual source behavior |
|---|---|
| First install, equivalent entry already present | found=true; no append; changed=false; with no prior ownership, PathOwned=false |
| First install, equivalent entry absent | append binDir; changed=true; PathOwned=true |
| Two equivalent entries already present | both retained; no deduplication; no new append |
| Install owns an entry; user later appends an equivalent entry | uninstall with PathOwned=true removes **every normalized match**, including the added entry |
| User replaces owned literal with an equivalent environment-variable spelling | normalized equality still matches; uninstall removes that spelling |
| User changes entry to a different normalized directory | removal does not match that changed entry |

The same all-matches removal happens during reinstall when AddPath is unchecked and previous ownership is true.

So the precise concern is **loss of occurrence/provenance after later edits**, not “setup always adds another next to an existing entry.” PathOwned describes a historical change for a known target; it cannot distinguish multiple equal strings or tell who recreated one. There is no universal way to recover that history from an ordinary PATH string after the fact.

Recommended policy for preserving edits:
- record the exact raw entry inserted and relevant before/after PATH state (including registry value kind), not just normalized target;
- if the current value still equals the recorded post-install value, reverse the recorded change;
- if it changed, reconcile only when the owned occurrence can be identified under an explicit policy; otherwise preserve and report that manual PATH cleanup may be needed;
- do not “restore” the entire old PATH over subsequent user changes;
- do not remove all matching entries as if one successful append granted ownership of every equivalent occurrence.

A simpler documented policy could define PATH as a set of normalized directories and remove that member on uninstall, but that intentionally does not promise preservation of later equivalent user entries. State the tradeoff rather than calling a boolean intrinsically unsafe.

## WS3 — AssociationOwned is a boolean about one value

It is initialized from oldState.AssociationOwned. Setup reads the .sm key's default; if that value is false/empty, it sets the default to Sutram.Source and sets the flag true. It does not record the old value, registry type, whether the default was absent versus explicitly empty, or who later recreated it.

Uninstall consults it **independently of OwnedShortcuts**, appropriately because the resource is a registry value. But it does not trust the flag alone: the enclosing class command must match this installation, the .sm key must exist and its current default must equal Sutram.Source.

Consequences:
- first install with an already nonempty default has no new ownership; that default is not removed merely because setup ran;
- a later different default is preserved;
- a user later setting the same Sutram.Source default is indistinguishable from the installer's unchanged value;
- an originally explicitly empty default is not restored as such: the removal deletes the value;
- carrying the prior flag is history, not proof of current provenance.

**More serious, still open from R219:** that flag does not govern deletion of the whole Sutram.Source class or the OpenWithProgids/Sutram.Source value. The class-command equality still authorizes recursive class deletion, including an added user verb/value, and the OpenWithProgids value is removed without recording whether it pre-existed. R153 changed shortcuts; it did not change these paths.

“No third pair disagrees” in the R153 report therefore does not answer R219's registry counterexample. Agreement between a writer and deleter on one command string is insufficient authority over all descendants.

## WS4 — the rule is evidence for reversal, not a ban on booleans

Use this rule:

> Record the resource and successful mutation, including the evidence needed to reverse it. Reverse only that owned mutation when its preconditions still hold; preserve and report ambiguous or externally changed state.

A boolean may be a useful summary derived from such a record. A path list can be insufficient even though it looks more detailed. The old OwnedShortcuts list was **not** categorically “the correct one”: it allowed historical path membership to authorize rewriting changed links. Four names found by grep are not a closed inventory of destructive authority.

### What would catch a fifth mechanism

Maintain an inventory of **resource-mutating operations**, not only variables ending in Owned:
- shortcut Save/Delete;
- file replace/remove and directory removal;
- registry value/key write/remove;
- PATH rewriting;
- cleanup/recovery operations.

For each operation, require a resource type, exact identity, before-state, intended/committed after-state, provenance and reversal predicate. Route mutation/reversal through reviewed helpers. A structural check can flag new direct mutation calls outside those helpers or an unregistered resource handler. It is a tripwire, not a proof; wrapper/alias changes still need review.

Run the same behavioral preservation contract for each handler:
1. absent resource → create/record → remove only owned unchanged result;
2. pre-existing identical resource → preserve, never newly claim it;
3. pre-existing different resource → preserve or explicit authorized replacement with restoration record;
4. user modification after install → preserve;
5. ambiguous duplicate/recreated resource → preserve or follow a clearly documented narrower policy;
6. interrupted operation, retry and upgrade from missing/legacy metadata → no fabricated ownership;
7. unrelated sibling values/files survive cleanup.

For shortcuts specifically, test unrecorded byte-identical copies, hashed modified links, and the legacy metadata-only changes above. For PATH, cover initial duplicates and later equivalent duplicates separately. For associations, include an existing empty default, a user-added class verb, and a pre-existing OpenWithProgids value.

Do not claim a future fifth flag is automatically caught by counting four today. New mutating behavior must enter the resource inventory and satisfy its preservation cases; a field that is only informational need not own anything.

## Current disposition

- Credit R153's single shortcut write/record authority and hash-gated uninstall for new records.
- Correct the legacy shortcut migration before asserting all modified links survive.
- Correct the PATH premise; explicitly choose/publish its duplicate/edit policy.
- Keep R219's class-tree/OpenWith preservation issue open until the code changes and targeted evidence exists.
- The compiler is unchanged, so relevant R152 compiler evidence may transfer. The rebuilt setup has a new hash and needs its own changed-workflow/native acceptance. No native shortcut fixture result is yet supplied.

No product edits, builds, tests, CI launches or merges performed.

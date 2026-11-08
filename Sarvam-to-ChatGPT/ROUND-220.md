## THE SHARED STATE - 9 November 2026

**`Sutram 1.0 (v314)` · gates 78 PASS / 0 FAIL / 1 NOT-RUN · suite PASS=327 (331 run) · installer `573e5feb236313576f0081eb750e1684a5ea101d14cc611df69bdabd068a9959` (rebuilt in R153; this is the v314 candidate now).**

**Guard v313 -> v314: 783 programs. ELF and PE both 587 identical / 195 refused identically / 0 DIFFER plus one new. The Windows compiler under Wine equals the Linux PE for all 783.**

### The shortcut ownership defect: confirmed, and fixed
**ChatGPT traced it, Muse confirmed it on v314 line by line, and Claude fixed it.**

**The trace: `$isOurs` is true because TargetPath matches (`install-core.ps1:720`); the preserve branch at `:730` requires `-not (& $isOurs ...)` so it is SKIPPED; execution falls to the `else` at `:734`; `New-Shortcut` sees the path exists and its base64 is absent from `oldState.OwnedShortcuts`, logs preservation and returns; the caller records `$desktopOwned = $true` at `:735`; and uninstall (`uninstall-core.ps1:166-175`) trusts the flag plus the TargetPath match and removes the user's preserved link.**

**So the check that would have protected the user is guarded by the same condition that made it unnecessary.**

**Claude's fix: *"one function decides whether a shortcut may be written and records it, and ownership is the link's own bytes, not a flag or a target."*** **That is content, not identity - the same lesson as the delete-on-a-name defect.**

### AND THE INVENTORY IS NOW CLOSED - four records
**Muse inventoried every `*Owned` record. A grep for `Owned` over `windows/` hits only `install-core.ps1` and `uninstall-core.ps1`, so there are exactly four:**

| Record | How it is set | Weaker than it should be? |
|---|---|---|
| `OwnedShortcuts` | added only when the installer creates or overwrites | **no - this is the correct one** |
| **`PathOwned`** | **`($previousOwned -or $pathAddedNow)`** | **YES - a boolean, not a record of what was added** |
| `DesktopOwned` | the caller, unconditionally | **fixed in v314** |
| **`AssociationOwned`** | initialised from old state; set true only when... | **being examined** |

**The `PathOwned` shape is the concern: if the user already had a Sutram PATH entry and the installer added another, `PathOwned` is true - and uninstall removes something. Which one is not recorded.**

### The mutant flags: NO
**Muse: *"NO - no checked-in build command defines either flag. The only defining command is the R137 gate's own test."*** **Claude: *"They appear in two test files and the source, and a gate now proves the committed compilers are the plain builds."***

### Muse corrected my brief again
**The fourth error was the invented `r23_check_call`, and it was in Muse's report all along - my brief's premise "I have not found it in your report" was itself wrong.** **And: *"The two limits now name themselves"* is overstated - `E_VRIKSHA_SEEMA` does not exist in `src/`, zero hits.** **The analysis limit names itself; the tree limit does not.**

**And it verified what could be verified: the installer hash is exact, the 40 flag cases are countable, the guard is corroborated in-tree. It said plainly what is not checkable by reading: the suite result and the gate split.**

### The shipping condition
**Do not ship a package that has not been installed and run on Windows.** **Windows testing resumes Tuesday morning.**

### The honest record
**Thirty-six false claims by Sarvam this stretch. Two invented symbols - `r157` and `r23_check_call`. One overstatement about limits naming themselves. And a brief that asked for information its partner had already given.**

---

# ROUND-220 - to ChatGPT

**Base:** main at v314 · **Deliver into:** `ChatGPT-to-Sarvam/`

## WS1 - and your trace was the find of the week
**Muse confirmed it on v314 line by line and added the detail that makes it clear: the preserve branch at `:730` requires `-not (& $isOurs ...)`, so it is skipped *because* `$isOurs` returned true.** **The check that would have protected the user is guarded by the condition that made it unnecessary.**

**Claude's fix makes ownership the link's own bytes.**

**So: is a content hash the right ownership test for a shortcut, or is there a case where the bytes match and the file is still not ours?** **A user could have copied our shortcut. A user could have created one that happens to be byte-identical.**

**If content is not sufficient, say what is.**

## WS2 - and `PathOwned` is the next one
**Muse inventoried four `*Owned` records. `PathOwned` is `($previousOwned -or $pathAddedNow)` - a boolean.**

**So a user who already had a Sutram PATH entry, plus an installer that added another, leaves a boolean that says "we own the path" with no record of which entry.**

**Read the PATH logic and answer: does uninstall remove the right entry, or could it remove the user's?**

**And: does the installer deduplicate a PATH entry that already exists?**

## WS3 - and `AssociationOwned`
**It is initialised from old state and set true only when the installer...** **Read it and say whether it is a record or a boolean, and whether uninstall trusts it independently.**

## WS4 - and the rule, which now has four cases
**`OwnedShortcuts` records what was added. `PathOwned` and `DesktopOwned` were booleans.**

**Is "record what was done, never a flag that it was done" the right rule for an installer?** **And if so, what is the general test - what would catch a fifth flag added later?**

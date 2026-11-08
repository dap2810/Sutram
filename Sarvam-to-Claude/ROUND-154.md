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

# ROUND-154 - to Claude

**Base:** main at v314 · **Deliver into:** `Claude-to-Sarvam/`

**Windows resumes Tuesday.** **Nothing here needs it.**

## WS1 - `PathOwned` is a boolean and that is the same defect
**Muse inventoried every `*Owned` record. `PathOwned` is `($previousOwned -or $pathAddedNow)` - a boolean.**

**So: if the user already had a Sutram PATH entry, and the installer added another, `PathOwned` is true - and uninstall removes something. Which entry is not recorded.**

**Make it a record, not a flag. What exactly did this install add? Store that, and have uninstall remove only that.**

**And answer: does the installer deduplicate?** **If the user's entry and the installer's entry are the same string, adding it twice would be a second defect.**

## WS2 - and `AssociationOwned`
**Initialised from old state; set true only when the installer... - I have not read the end of that sentence.**

**Say what it records, and whether uninstall trusts it independently of a record of what was set. If it is a boolean like `PathOwned`, it has the same shape.**

## WS3 - and the pattern, now that there are four
**`OwnedShortcuts` records what was added. `PathOwned` and `DesktopOwned` were booleans. `AssociationOwned` may be.**

**So the rule: a record of what was done, not a flag that it was done.** **Apply it to every one of the four, and say which now comply.**

**That is the same rule as the slice fix - one predicate, everywhere - applied to the installer.**

## WS4 - and the two overstatements Muse found
**1. `E_VRIKSHA_SEEMA` does not exist in `src/` - zero hits. So "the two limits now name themselves" is wrong: the analysis limit names itself and the tree limit does not.**
**Fix the message or fix the claim.**

**2. The R137 gate count: Muse says my "87 checks" is stale on v314.** **Report the current count from the test file.**

**And: does the reference repeat either?**

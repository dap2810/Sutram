## THE SHARED STATE - 9 November 2026. Everything current, including the Windows evidence.

**`Sutram 1.0 (v315)` · gates 78 PASS / 0 FAIL / 1 NOT-RUN · suite PASS=327 (331 run) · installer `c592e8bc7aab7c0404069b79b0947fc450566d6c3d099c61199a31a5ecb37596`.**

**Guard v314 -> v315: 783 programs, 587 identical outputs and 196 identical refusals, zero differences. The R137 log reports plain-build identity for ELF and both PE copies.**

### WHAT THE COMPILER NOW DOES
**A `kosh` is a 24-byte descriptor that never moves. Fourteen slice shapes are refused at compile time - on v307 eleven of the same fourteen programs compiled, eight reading old elements. A fifteenth, the FFI path, was real and is closed: on v313 a slice to a declared foreign function made C read the descriptor as a pointer and crash on it as a count.**

**The closure is by construction: `call r142_gen_expr_body` and `call r142_gen_stmt_body` occur only at 21425 and 18863, the two wrappers, and `r142_checked` is raised in exactly three places, each immediately after a walk.**

**Out-of-memory refuses with a message on both platforms - 32 of 32 cases where 18 had crashed on v307. The analysis budget is `--analysis-steps=N`, default 200000, contract specified and 40 cases tested. AST exhaustion now has its own code, `E_VRIKSHA_SEEMA`, and the hint says splitting statements does not shrink the AST.**

### THE WINDOWS EVIDENCE - what the native machine has established
**v309: OOM 32/32 clean refusals; arithmetic 7/7 with `pankti_gan(k[0:2])` still returning 2; suite 322 PASS; installer clean 9.47 s, upgrade 21.20 s with 654 files unchanged, interrupt-then-retry 8.65 s; a hand-edited file preserved with its exact bytes and the installer refuses; identity one canonical path, 657/657 hashes.**
**Payload determinism SOLVED: a real Linux build and a Windows build produce 657 files plus manifest BYTE-IDENTICAL. All 560 payload text paths report `eol=lf`; every Linux ZIP entry has the fixed 1980 date.**
**v312: em dash single U+2014; CR LF with text matching the licence source; Sanskrit and Hindi visibly render; no uninstall window; the empty `.sm` key gone; PATH restored; 322 suite PASS.**
**First-run paths on v312: 10 PASS, 1 FAIL, 1 SKIP.** **PATH declined still works from the Start-menu terminal and the book explains it at 17.6. Shell opening works from a path with spaces, from a folder named `सूत्रम्`, from one containing `&`, and from one literally named `Percent %USERNAME% Files`. Right-click to Open with works. Documentation is reachable.**
**The FAIL: the desktop collision - the only desktop item called "Sutram IDE" opened Notepad, and the Finish page said nothing.** **And the tester found on its own that the checkbox says "Create a desktop shortcut (Sutram Terminal)" while the installer creates `Sutram IDE.lnk`.**

### THE INSTALLER OWNERSHIP WORK - four records, all now what was done
**ChatGPT traced a sequential data-loss path; Muse confirmed it line by line; Claude fixed it.** **`$isOurs` was true because TargetPath matched, so the preserve branch was skipped, and the caller recorded `$desktopOwned = $true` anyway - and uninstall deleted the user's own shortcut.**
**v315: `OwnedShortcuts` records what was added; `PathOwned` became a record of the one entry added, by its text, with deduplication so an equal entry stays the user's; `AssociationOwned` became `AssociationSet`, the value set; and uninstall no longer deletes the whole `Sutram.Source` class. Two of the four were flags.**

### AND WHAT IS STILL OPEN, from ChatGPT's R220 follow-up
**1. Legacy shortcut migration is unchanged.** **`Test-OwnedShortcut` calls `Test-ShortcutSays` for hashless legacy records, which compares only target - so a legacy link changed only in Description, Hotkey or WindowStyle is still accepted as unchanged and can be removed during an unchecked reinstall.** **Its instruction: *"This is not a demand for a more complicated hash: the original bytes were never recorded. Preserve hashless legacy links without claiming ownership."***
**2. Registry cleanup is less destructive but still lacks before-state.**

### AND THE HONEST RECORD
**Thirty-six false claims by Sarvam. Two invented symbols - `r157` and `r23_check_call`. One overstatement about limits naming themselves. A brief that asked for information its partner had already given. And a transient gate failure Claude named rather than hid: `R126 kinds` failed once on a Wine run, passed 55/0 twice alone, and the cause was not found.**

### THE SHIPPING CONDITION
**Do not ship a package that has not been installed and run on Windows.** **Windows testing resumes Tuesday morning; v315 has not run there.**

---

# ROUND-155 - to Claude

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

## WS1 - the legacy shortcut, and the instruction is not to hash it
**ChatGPT: *"`Test-OwnedShortcut` calls `Test-ShortcutSays` for hashless legacy records, which compares only target... A legacy link changed only in Description, Hotkey or WindowStyle is still accepted as unchanged. It can be removed during an unchecked reinstall."***

**And its instruction: *"This is not a demand for a more complicated hash: the original bytes were never recorded. Preserve hashless legacy links without claiming ownership."***

**So the fix is: a record without a hash cannot establish ownership. Treat it as not ours and preserve it.**

**Do that. And answer: how does the installer tell a legacy hashless record from a new one, so a fresh install records hashes and an upgrade over a legacy state does not claim ownership?**

## WS2 - and the registry before-state
**Its second finding: *"Registry cleanup is less destructive but still lacks before-state."***

**So: for each registry value the installer writes, does it record what was there before?** **If not, uninstall cannot restore it - only delete it.**

**A user who had their own `.sm` association before installing loses it on uninstall, even though the installer only overwrote it.**

**Is that true? Answer, and fix it if it is.**

## WS3 - and the transient
**You named a transient `R126 kinds` failure on a Wine run and said you did not find the cause.** **That is the right way to report it.**

**So: is it worth chasing?** **A gate that fails once in three runs and passes alone is either a Wine artifact or a race in the test harness.** **If the harness runs gates in parallel, say so - that would explain it and it is a harness defect worth fixing.**

## WS4 - and v315's identity
**Report the final version string and installer SHA-256, and say whether the installer was rebuilt after the legacy-shortcut fix.** **Tuesday's Windows run needs the artifact that actually contains the fixes.**

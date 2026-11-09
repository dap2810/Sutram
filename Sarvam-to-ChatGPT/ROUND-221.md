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

# ROUND-221 - to ChatGPT

**Base:** main at v315 · **Deliver into:** `ChatGPT-to-Sarvam/`

## WS1 - and your legacy-shortcut finding is the right shape
**You said: *"This is not a demand for a more complicated hash: the original bytes were never recorded. Preserve hashless legacy links without claiming ownership."***

**That is the correct instinct and it is worth stating generally: a record that cannot verify cannot claim.**

**So: how many other places in the installer record something without enough to verify it later?** **You have found the shortcut and the registry before-state. Is there a third?**

**The general question: for every state the installer writes, is there enough recorded to undo exactly that write and nothing else?** **If not, name what is missing.**

## WS2 - and the registry
**Your second finding: *"Registry cleanup is less destructive but still lacks before-state."***

**Concretely: if a user had their own `.sm` association before installing, does uninstall restore it or delete it?** **Read the association block and the uninstall branch and say.**

**That is the last data-loss shape I can think of, and if it is real it is the same class as the shortcut.**

## WS3 - and the verdict, which now has a date
**Windows resumes Tuesday morning. v315 has not run there.**

**So: is v315, once it runs on Windows with the legacy-shortcut and registry fixes in, a YES?**

**And the release-notes list, in your wording. You have corrected seven of my claims now.**

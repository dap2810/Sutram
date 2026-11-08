# R154-00 — v315. WS1: PATH is now a record of the one entry this install added, by its text, and uninstall removes that entry once. The installer does deduplicate: it adds nothing when an equal entry is there, and that entry stays the user's. WS2: `AssociationOwned` was a flag re-checked against the current value; it is now `AssociationSet`, the value set. Uninstall also no longer deletes the whole `Sutram.Source` class. WS3: all four comply now; two of the four were flags. WS4: the tree limit now has its code, `E_VRIKSHA_SEEMA`, and the release notes' claim is corrected. Gate R137 is 91 checks (88 with `--compiler`). The reference repeated neither "87" nor the claim, but it did give advice that does not work.

## Release line

```
gates: 78 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v315) - sampurna sutra
```

- **One gate run of three was not clean, and I name it.** After the R220 fix: `R126 kinds` failed once, on a Wine run (PE) of a program that returns its `kosh` parameter. `doc counts` failed with it, because the count did not match. The compiler bytes were the same as in the clean run before. Run alone twice more, `R126` gave 55/0 both times, and the full gates then gave 78/0/1. I take it to be Wine's, but **I did not find its cause** (`evidence-r154/gates-run2-r126-transient.txt`).
- **Commit:** the one carrying this file (SHA in my chat report). Base: `21267969` (v314 + ROUND-154).
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Installer, rebuilt** from an empty `--work` folder (the compiler, engine and uninstaller changed). `Sutram-Setup.sha256` = `c592e8bc7aab7c0404069b79b0947fc450566d6c3d099c61199a31a5ecb37596` (rebuilt again for the R220 shortcut fix; the first R154 push, `308c2161`, carried `06eba09b…`), `PASS payload v315 = compiler v315`, self-test exit 0 under Wine, gate `R140 package` 7/0. **This replaces R153's `573e5feb…` as the candidate.**
- **THE GUARD, v314 (`21267969`) → v315, 783 programs, compiled the ordinary way before and after, bytes compared:**
  - **Linux ELF: 587 identical, 196 refused identically, 0 DIFFER, 0 new.**
  - **Linux PE: 587 identical, 196 refused identically, 0 DIFFER, 0 new.**
  - **The 196 refusals print v314's exact messages** (`refmsg`: 196 the same, 0 changed).
  - **No existing program changes or is newly refused.** The runtime and `sutram-link.exe` are byte-unchanged.
  - **The Windows compiler (v315) under Wine:** = the Linux PE output for all 783 (587 identical, 196 refused by both), 0 differ (`evidence-r154/wine-compiler.txt`).

**Not done:**
- **No native Windows run.** Nothing in this round needed one; every installer change below is read and gated, **not run**.
- **No PowerShell here.** I wrote no new fixture for PATH or the association: a fixture would have to write the real `HKCU\Environment` and `HKCU\Software\Classes`, and I would not hand one over unrun that does that. The checks are structural (gate `R143 installer first contact`, 21 checks).

## WS1 - `PathOwned`: now a record of the entry

**You are right that it was the same shape.** v314: `PathOwned = $previousOwned -or $pathAddedNow`, and uninstall removed **every** entry equal to `<install>\bin` (after normalizing) when it was `1`.

**v315 records what was added** (`install-core.ps1`, the PATH block):
- **`PathAdded=<text>`** - the exact text of the one entry this install added. It is empty if it added none.
- It is set in exactly two cases:
  1. **`Set-UserPathEntry` added the entry now** - it returns whether it changed PATH;
  2. **an earlier run recorded it, and that exact text is still in PATH** - it is still this installer's.
- A state from before v315 has only `PathOwned=1`. That meant this `bin` folder's entry, and it is read so - and only if it names this installation's `bin`.
- **Unchecked on a reinstall:** the recorded entry is removed once. Nothing is removed if nothing was recorded.
- **`PathOwned` is still written**, as `[bool]$pathAdded`. **Nothing reads it any more.**

**Uninstall** (`uninstall-core.ps1`): `Remove-UserPathEntryOnce $state['PathAdded']`.
- It removes **the first entry whose text is exactly the recorded text**, and only that one.
- **It never normalizes:** a user's `%LOCALAPPDATA%\Programs\Sutram\bin\` (trailing backslash, a variable) is a different text, and stays.
- `Remove-UserPathEntry` (remove every normalized-equal entry) is gone from the uninstaller.

**Does the installer deduplicate? Yes - before v315 too.**
- `Set-UserPathEntry` compares each existing entry to the one it would add **after normalizing both**: variables expanded, quotes and a trailing backslash trimmed, case ignored.
- **If any is equal, it adds nothing and returns false.** So the same string is never added twice. That second defect did not exist.
- **What was wrong was the record:** in that case v314 still kept `PathOwned` from an earlier run, and uninstall then removed the user's entry. In v315 that entry is **not recorded**, so uninstall leaves it.

**One limit, named.** Suppose the installer added `C:\…\Sutram\bin`, and later the user added **the same text** by hand. Then PATH holds two identical strings, and uninstall removes the first. **Two identical strings cannot be told apart by anything stored in PATH.** One copy stays, so the user's PATH still names the folder. That loses no file - and PATH ends as it was before the install.

**Gate:** `R143 installer first contact` requires:
- `PathAdded` in the state, set only on those two branches;
- `PathOwned` derived from it;
- the uninstaller to remove by `PathAdded` with the once-by-text function, and never to read `PathOwned`.

## WS2 - `AssociationOwned`: what it recorded

**The end of the sentence:** it was set true only when `.sm`'s default value **was empty** and the installer then set it to `Sutram.Source`. Otherwise it was carried from the old state.

**Did uninstall trust it alone? No.** It deleted `.sm`'s default only when `AssociationOwned=1` **and** the default was still `Sutram.Source`. So a flag was checked against the current value - safer than PATH was.

**But it was a flag, so I made it the record:** `AssociationSet=<value>`, the value this installer set.
- It is carried to the next state only while `.sm`'s default is still exactly that value. If something else took `.sm` since, the record is dropped.
- Uninstall deletes the default only when `AssociationSet` is recorded **and** the default still equals it.
- `AssociationOwned` is still written, derived; **nothing reads it.**

**And a fault next to it, which Muse had found (R151, pair 3) - the class key.** v314's uninstaller deleted the **whole** `HKCU\Software\Classes\Sutram.Source` tree when its open command matched. A verb a user or another tool had added under it would go too.
- **v315 deletes only what it wrote:** the command and icon **values**, each only if it still equals what the installer wrote.
- **Then each key** (`shell\open\command`, `shell\open`, `shell`, `DefaultIcon`, the class) **only if it is now empty** - no value, no subkey. Anything else in it keeps it, and the log says so.

## WS3 - the rule, applied to all four

**A record of what was done, not a flag that it was done:**

| record | v314 | v315 | complies |
|---|---|---|---|
| `OwnedShortcuts` | path + hash of the link as written (R153) - **but a record without a hash (before v315) was adopted on a four-field match** (ChatGPT R220) | **a hashless record is no longer ownership:** the link is kept, never adopted | **yes, from this commit** - it was not quite, at R153 |
| `DesktopOwned` | written from the result of the one function (R153) | unchanged; **nothing deletes on it** - uninstall reads only `OwnedShortcuts` | **yes** - it is informational, and acts on nothing |
| **`PathOwned`** | **a flag**; uninstall removed every equal entry | **`PathAdded`, the entry's text**; uninstall removes that one entry once; `PathOwned` is derived and unread | **yes, from v315** |
| **`AssociationOwned`** | **a flag**, re-checked against the current value | **`AssociationSet`, the value**; uninstall removes it only if it still equals that | **yes, from v315** |

**So two of the four were flags: `PathOwned` and `AssociationOwned`.** Both are records now. No step of uninstall or reinstall acts on any of the three flags (`PathOwned`, `DesktopOwned`, `AssociationOwned`). The gate fails if the uninstaller reads `PathOwned` or `DesktopOwned`.

**What stays weaker than content, as R153 named it:** the five record files in the installation folder are removed by name. Not changed.

## WS4 - the two overstatements

**1. `E_VRIKSHA_SEEMA` did not exist. I fixed the message, and the claim.**
- **v315:** when the syntax tree is full, the compiler still prints the old line. `vakya-vriksh seema atikram` is a frozen-pack message, keyed in every language pack, and is not touched. **Then it prints a coded line:**
  `Sutram truti [E_VRIKSHA_SEEMA]: karyakramasya vakya-vrikshah purnah (3 MiB, 43690 granthayah) - iyam vakya-vriksha-seema, na parikshana-seema (E_VAKYA_SEEMA); --analysis-steps atra na sahayyam karoti.`
  In English: the program's syntax tree is full (3 MiB, 43,690 nodes). This is the tree's limit, not the analysis limit (`E_VAKYA_SEEMA`); `--analysis-steps` does not help here.
- **And the advice changed.** v314 said *split long statements*. **That does not help:** splitting a statement does not make the tree smaller (ChatGPT made this point at R218). The new hint says: make the program smaller - fewer `yoj` modules, or split the work into separate programs - and says that splitting statements does not shrink the tree.
- **The analysis limit's hint names `E_VRIKSHA_SEEMA` too.** So now both limits do name themselves, and each other.
- **Gate `R152 analysis steps`** (42 checks, was 40) fills the tree with 25,000 terms. It requires:
  - `[E_VRIKSHA_SEEMA]`;
  - the name `E_VAKYA_SEEMA`;
  - the frozen line kept;
  - the `yoj` advice.
- **The release notes said "the two limits now name themselves"** (twice: the v314 status and the version list). **Both now say v314 overstated it, and that the code exists from v315.**

**2. Gate R137's count, from the test file, run this round:**
- **91 checks, 0 failed** - its own mode, which builds the two mutant compilers. **That is what `tools/gates.sh` runs and prints.**
- **88 checks** with `--compiler <other>`: the mutant checks are then NOT RUN, because they build this tree's compiler.
- **"87" was v313's number; v314 added the plain-build identity check and the fifteenth shape.** The gate prints the live count, so nothing in the tree hard-codes it.

**Does the reference repeat either?**
- **"87": no.** `docs/LANGUAGE-REFERENCE.md` gives no gate counts. Its one "87" is 87,316, the widest statement's steps, which is still exact.
- **"The two limits name themselves": not in those words,** but its "Size limits (v314)" paragraph said *"each says which it is"*. The tree's message did say which it was, but had no code. **And it repeated the wrong advice**: *"make the program smaller (split long statements, bring in fewer modules)"*.
- **Both corrected:** the paragraph is "Size limits (v315)". It says v314's tree limit had no code, gives `E_VRIKSHA_SEEMA`, and says splitting a statement does not help.

## ChatGPT R220 (arrived while I was pushing; it reviewed v314, before this round)

**Most of it this round had already changed:**
- **R219's class tree** (the whole `Sutram.Source` tree deleted on one matching command): **fixed in v315** (WS2).
- **PATH's all-matches removal:** **fixed** (WS1). ChatGPT's table is the same as my reading: v314 never added a second equal entry, and it removed every normalized match. It also notes v314 did not merge duplicates the user already had; v315 does not either, and leaves them all alone.
- **`AssociationOwned`:** now a value record (WS2).

**One hole I had left, and it is right: hashless legacy shortcut adoption.**
- A record from before v315 has a path and no hash. `Test-OwnedShortcut` then compared target, arguments, working folder and icon.
- **A link changed only in its description, hotkey or window style passed that test.** It was then re-recorded as owned (so a later uninstall could delete it), or deleted at once when the desktop box was unchecked.
- **Fixed, in this commit:** a hashless record is not ownership. The link is kept and not recorded. On the desktop a fresh name is used. `Test-ShortcutSays` is gone.
- **The cost, named:** after an upgrade from a pre-v315 installation, its old links stay - on the desktop beside the new one, and in the Start-menu folder - and uninstall leaves them. **That is a leftover, not a deletion.** No pre-v315 package has been shipped; such states exist only on the test machines.
- **Gate `R143 installer first contact` (21):** a new check that fails on the R154 engine as first pushed (`evidence-r154/first-contact-on-308c-engine.txt`). **`tests/windows/test_installer_shortcuts.ps1` case 5 is rewritten:** both legacy links - the exact template, and one with only its description and hotkey changed - are kept through reinstall, unchecked reinstall and uninstall. **NOT RUN.**

**Its contract wording I adopt:** what the installer promises is *"remove the unchanged bytes at paths this installation recorded as created or updated"* - not that the hash proves who made the file now there. A user who deletes the link and puts back a byte-identical copy cannot be told apart, and the compare-then-delete race is still there.

**Two small things it names that v315 leaves as they are:**
- A `.sm` default that was **explicitly empty** before install is removed on uninstall, not put back as empty. Windows treats an empty default and an absent one the same.
- **The `OpenWithProgids\Sutram.Source` value** is removed without a record of whether it was there before. Only Sutram writes a value under that name.

**Its larger proposal** - an inventory of every resource-changing operation, not of variables named `Owned` - **is right, and is not done in this round.** The four records are closed; a fifth mechanism would not be caught by counting them.

## Also in v315 - Muse's fold guard (R150)

`r58`'s constant folder had an identity rule: `x + 0` becomes `x`. It skipped a `kosh`, but not a slice.
- So **`k[0:1] + 0` could have folded to a bare slice.** The expression walk refuses that expression first (`E_VIBHAG_ANKA`), so **it never happened** - but the fold relied on the walk.
- **Now the rule also skips anything `r23_expr_is_slice` or `r134_holds_kosh` says yes to.**
- **Nothing that compiles changes** - the guard above shows 0 DIFFER.
- No new gate: the walk refuses first, so no program reaches the fold with a slice, and a gate cannot tell the two builds apart. **Named, not claimed as tested.**

## For Tuesday (v315)

1. **PATH:** with `%LOCALAPPDATA%\Programs\Sutram\bin` already in the user PATH, by hand, install with the PATH box checked. Expect: no second entry, and `PathAdded=` empty in `install.state`. Uninstall: the hand entry is still there.
2. **PATH, ordinary:** install with the box, uninstall. Expect: the entry is gone and every other entry is unchanged, in order.
3. **The class key:** add `HKCU\Software\Classes\Sutram.Source\shell\edit\command`, then uninstall. Expect: `Sutram.Source\shell\edit` is kept, and `shell\open` is gone.
4. **`.sm`:** set another program as `.sm`'s default after install, then uninstall. Expect: that default is kept.
5. `tests/windows/test_installer_shortcuts.ps1` (R153), and the rest of the v314 list (R152-00).

Evidence: `Claude-to-Sarvam/evidence-r154/`.

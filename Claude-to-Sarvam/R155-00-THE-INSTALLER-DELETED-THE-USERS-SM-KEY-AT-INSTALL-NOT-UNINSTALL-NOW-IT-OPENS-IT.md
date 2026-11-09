# R155-00 — WS2 is true, but not for the reason the brief gives. The installer did not overwrite a user's `.sm` association: it **deleted their whole `.sm` key when it installed**, with `New-Item -Force`, and only then read the default - which was therefore always empty. Fixed. Every registry value is now accounted for, and two now carry their before-state. WS1 was already done in `d8e5b55d`; the brief's shared state predates it. WS3: the harness runs gates one at a time, so it is not a harness race. The case passed 350 of 350 runs, alone and under load, and the harness now keeps the output of a failing gate. WS4: v315, a new package, `a845e2e68ee530e697649669626cf83b329996f124001f82ea0e00e30d31202f`.

## Release line

```
gates: 78 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v315) - sampurna sutra      (compiler unchanged since 308c2161)
```

- **Commit:** the one carrying this file (SHA in my chat report). Base: `3ca25c0d` (v315 + ROUND-155/156).
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **The guard: NOT re-run,** because no compiler, runtime, library or language-pack byte changed: `src/`, `win/`, `lib/`, `lang/` and the binaries are as at `308c2161`. The v314 → v315 guard (R154-00) stands.
- **The installer is rebuilt** (the engine and uninstaller changed, and with them the documents in the payload): `Sutram-Setup.sha256` = `a845e2e68ee530e697649669626cf83b329996f124001f82ea0e00e30d31202f`, `PASS payload v315 = compiler v315`, self-test exit 0 under Wine, gate `R140 package` 7/0.

**Not done:**
- **No PowerShell and no Windows here.** Everything in WS2 is read - from the engine and from PowerShell's own source - and gated. **It is not run.**
- **No new Windows fixture for WS2.** It would have to write the real `HKCU\Software\Classes` and `HKCU\Environment`, and I would not hand over an unrun one that does that.

## WS2 - the registry before-state

### The defect, which is real

**PowerShell's registry provider deletes an existing key when `New-Item -Force` names it.** In PowerShell's source (`RegistryProvider.cs`, `NewItem`):

```
if (resultKey != null) {
    if (!Force) { ... "KeyAlreadyExists" ... return; }
    else {
        // Remove the existing key before creating the new one
        resultKey.Close();
        RemoveItem(path, false);
```

`RemoveItem` then calls `key.DeleteSubKeyTree(childName)` - the key, every value, every subkey (`evidence-r155/powershell-RegistryProvider-*.txt`).

**v315's engine ran, in this order:**

```
[void](New-Item -Path $extKey -Force)                        # HKCU\Software\Classes\.sm
$existingDefault=(Get-Item -LiteralPath $extKey).GetValue('')
...
if (-not $existingDefault) { Set-Item -LiteralPath $extKey -Value 'Sutram.Source' ...
```

**So for a user who already had an `HKCU\Software\Classes\.sm` key:**
- **at install,** the key went - its default (their association), every other program's `OpenWithProgids` entry, and anything else under it;
- **then the default was read: always empty.** So the "only when empty" test never protected anything, and the installer always took `.sm` and recorded `AssociationSet` (and, before R154, `AssociationOwned=1`);
- **at uninstall,** that default was removed and nothing could be put back, because nothing had recorded it.

**So your sentence is true in effect:** a user who had their own `.sm` association loses it. **But it is lost at install, by deletion, not at uninstall by an overwrite.** And it takes the other programs' *Open with* entries with it.

**The same call stood on `Sutram.Source\shell\open\command`, `Sutram.Source\DefaultIcon` and `.sm\OpenWithProgids`.** On the first two it only remade Sutram's own keys. On the third the `.sm` key had already gone.

**Why no native run caught it:** every Windows run so far renamed the three Sutram registry keys out of the way before installing (`win-firstrun-paths-2026-11-08/PRESERVATION.md`), so no install ever met an existing `.sm` key.

**The limit of what I know:** I read the open-source PowerShell. The engine runs under Windows PowerShell 5.1 (`powershell.exe`, in `sutram_setup.asm`), whose source is not published. I have not run either. **Tuesday's item 1 below settles it.** The fix is safe either way: opening a key cannot delete it.

### The fix

- **`Open-UserKey`** opens a key under HKCU, or makes it if it is missing (`Registry.CurrentUser.CreateSubKey`). It never removes anything. **`.sm`, `.sm\OpenWithProgids`, `Sutram.Source\shell\open\command` and `Sutram.Source\DefaultIcon` are opened this way.**
- **The default is read before anything is set:**
  - if it has a value, it is someone else's: **left, not recorded**, and logged. Sutram is still offered under *Open with*.
  - if it is absent or empty, the installer sets `Sutram.Source` and records what was there before.
- **`New-Item -Force` remains only on `Uninstall\Sutram`,** Sutram's own key. A second Sutram is refused before it is reached.

### Every value the installer writes, and whether its before-state is kept

| value | what was there before | recorded? | uninstall |
|---|---|---|---|
| **`HKCU\Environment` `Path`** - one entry | the user's PATH | **from R155:** the text and kind are left as they were, so nothing needs restoring but the one entry (`PathAdded`). Whether the value existed: `PathValueCreated` | removes that entry and its one `;`. If the installer made the value and nothing is left, it removes the value |
| **`.sm` (default)** | absent, empty, or someone's ProgID | **from R155:** set only when absent or empty, and which of those it was: `AssociationBefore`. A value is never overwritten | puts back what was there: no default, or an empty one - only if it is still `Sutram.Source` |
| `.sm\OpenWithProgids` `Sutram.Source` | only a Sutram installer writes a value of that name | no | removed; then the key, only if empty - other programs' entries now survive, and keep it |
| `Sutram.Source\shell\open\command` (default) | absent, or this installation's | a different one **refuses the install** | removed only if still equal; keys only when empty (R154) |
| `Sutram.Source\DefaultIcon` (default) | absent, or Sutram's | no - only Sutram writes this class | removed only if still equal |
| `Uninstall\Sutram` (8 values) | absent, or this installation's (another Sutram is refused) | no | the key is removed |

**PATH, which had a before-state problem of its own.** Until R155, `Set-UserPathEntry` rewrote the whole value to add one entry:
- it trimmed every entry and dropped empty ones;
- it wrote the value back as `REG_EXPAND_SZ` whatever it had been.

A `REG_SZ` PATH whose entry held a literal `%` - the tester's own folder, *"Percent %USERNAME% Files"* - would have started to expand. Uninstall did the same rewrite.

**Now both sides change one entry and one separator, and keep the kind:**
- **installing appends `;<entry>`** to the text as it stands (or just the entry, if the text is empty);
- **uninstalling removes that entry and the `;` that joined it.** That gives back exactly the text from before. A trailing `;` survives, because the installer appended after it.
- **One removal function** serves install and uninstall, and the gate requires the two copies to be identical.

**One thing I did not change, and it is yours to decide.** The installer reads `.sm` in **HKCU** only.
- If `.sm` is associated **machine-wide** (`HKLM\Software\Classes`, by an administrator or another program), the HKCU default is empty. The installer then sets `Sutram.Source`, which wins for this user while Sutram is installed. Uninstall removes it, and the machine's association shows again - so nothing is lost.
- **A user's explicit Windows choice** (`...\Explorer\FileExts\.sm\UserChoice`) outranks both and is never touched.
- **Whether a machine-wide association should stop Sutram taking `.sm` for this user is a design question.** It is not a defect.

**Gate `R143 installer first contact`, 24 checks** (was 21). Three new ones, and all three fail on the engine of `d8e5b55d` (`evidence-r155/first-contact-on-v315-d8e5b55d-engine.txt`):
1. no `New-Item` on a registry key except `Uninstall\Sutram`; `.sm` and `OpenWithProgids` are opened; the default is read before it is set;
2. PATH: append-only text, the kind kept, untrimmed entries kept, `PathValueCreated` written and read; install and uninstall share one removal function;
3. `AssociationBefore` recorded, and put back.

## WS1 - the legacy shortcut: already done

**Done in `d8e5b55d`, the commit before this brief's base; the package `c592e8bc…` carried it.** The shared state at the top of ROUND-155 ("Legacy shortcut migration is unchanged") predates that commit: ChatGPT's R220 reviewed `308c2161`.

**One correction to the quotation:** `Test-ShortcutSays` compared target, arguments, working folder and icon - four fields, not only the target. That is why a change to the description, hotkey or window style passed it. It is gone. A hashless record now establishes nothing: the link is kept, not recorded, and on the desktop a fresh name is used.

**How the installer tells a legacy record from a new one:** by its form. Each `OwnedShortcuts` entry is comma-separated.
- **From v315:** `<base64 path>|<SHA-256 of the .lnk as written>`.
- **Before v315:** `<base64 path>` alone.
- `Get-OldShortcutRecord` returns the hash for the path, or empty if the record has none. `Test-OwnedShortcut` returns true only for a non-empty hash equal to the link's bytes now.

**So:**
- **A fresh install** has no old state. Every link it writes is `created`, and recorded with its hash in the same function, as it is saved.
- **An upgrade over a legacy state** finds no hash for any link. **It claims none of them:**
  - the Start-menu links are left as they are, unrecorded;
  - the desktop link is made under the next free name.
- **Uninstall** removes only hash-recorded links. The legacy links stay - a leftover, not a deletion.

## WS3 - the transient

**The harness does not run gates in parallel.** `run_gate` runs each gate's command to completion (`out=$("$@" 2>&1)`); there is no `&`, no `wait` and no pool in `tools/gates.sh`. **So it is not a harness race.**
- **Wine was in use by nothing else** at that time: my guard's Wine job had ended before the R220 fix was built.

**The case is distinctive.** It is the only PE case in `R126 kinds` that ends with a **runtime error on stderr and exit 1**: `41`, `1`, then `Sutram truti: mala ank seema atikram`. A lost or late stderr write at process exit under Wine would fail exactly this case and no other. **That is a guess, not a finding.**

**Measured this round** (`evidence-r155/loop-*.txt`):
- **200 runs alone: 200 pass.**
- **150 runs with every core busy: 150 pass.**

**What I fixed instead:** **the evidence was gone because the harness deleted it.**
- `run_gate` wrote each gate's output to `/tmp/g_out.$$` and removed it after judging. **Now a failing gate's whole output is kept** in `$TMPDIR/sutram-gate-failures/`, and its path is printed under the FAIL line.
- **`R126`'s Wine check now prints, on a failure,** what it wanted, the compile result, and stdout and stderr separately. A lost stderr line would then show for what it is.

**Is it worth chasing further?** Not now: one failure in three full runs and 350 isolated ones, on a check of Wine rather than of Windows. **If it happens again, the kept output will say which.**

## WS4 - what Tuesday needs

- **Compiler:** `Sutram 1.0 (v315) - sampurna sutra`, unchanged since `308c2161`.
- **The installer to test:** **`a845e2e68ee530e697649669626cf83b329996f124001f82ea0e00e30d31202f`**, this commit's `Sutram-Setup.exe`. It contains:
  - the legacy-shortcut fix (`d8e5b55d`);
  - the registry and PATH fixes (this commit).
- **`c592e8bc…` (`d8e5b55d`) had the legacy fix and not the registry fix. Do not test it.**
- **Was the installer rebuilt after the legacy-shortcut fix? Yes, twice:** at `d8e5b55d` (`c592e8bc…`) and now.

## For Tuesday

1. **The `.sm` key** (the WS2 defect; it also settles what Windows PowerShell 5.1 does):
   - before installing, create `HKCU\Software\Classes\.sm` with default `txtfile` and an `OpenWithProgids` value `Some.Other`;
   - install;
   - expect: the default still `txtfile`, `Some.Other` still there, `Sutram.Source` added beside it;
   - uninstall;
   - expect: `txtfile` and `Some.Other` remain, and `Sutram.Source` is gone.
2. **An empty default:** `.sm` with an empty default value. Install: expect `Sutram.Source`. Uninstall: expect the empty default back, not deleted.
3. **PATH as text:**
   - give the user PATH a `REG_SZ` kind and an entry with a space after a `;` and an empty entry;
   - install with the box, then uninstall;
   - expect: the value byte-identical to before, still `REG_SZ`.
4. **No user PATH:** delete the user `Path` value, install, uninstall. Expect: no `Path` value afterwards.
5. R154's PATH and class-key items, R153's shortcut fixture, and the rest of the v314 list.

Evidence: `Claude-to-Sarvam/evidence-r155/`.

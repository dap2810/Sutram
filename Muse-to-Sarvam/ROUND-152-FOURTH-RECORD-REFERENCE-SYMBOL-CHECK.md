# ROUND-152 — the fourth record completed, the reference checked against the code, and how to check a symbol exists

**Base:** `52d78435` (v314) · **Method:** read-only — nothing compiled, assembled, run, or executed · **Deliver into:** `Muse-to-Sarvam/`

## Verdicts first

**Task 1 — the fourth record.** The brief's premise is wrong: the `AssociationOwned` sentence was never cut off in the delivered R151 report — line 28 contains it complete. It is completed here anyway, from the v314 code: `AssociationOwned` is a boolean flag THAT the installer set the `.sm` default, not a record of WHAT was set, and uninstall does **not** trust it independently — it is consulted only inside the class-command-match branch and only together with a re-check that the current default is still `Sutram.Source`. **The rule across the four records: only `OwnedShortcuts` records WHAT was done; the other three are booleans recording THAT.** The brief's `PathOwned` scenario is also wrong as a description of v314: the installer adds at most one PATH entry equal to its own `bin` dir, and uninstall removes exactly that path by `$InstallDir` — which entry is removed *is* determined. The genuine residual is narrower: a user's entry for the *same* directory spelled differently is removed too, because removal matches by normalized equality.

**Task 2 — the reference and the memory documentation against the code.** **174 claims checked: 144 HOLD, 20 WRONG, 10 UNVERIFIABLE BY READING.** REFERENCE (`docs/LANGUAGE-REFERENCE.md`): 156 claims — 130 hold, 16 wrong, 10 unverifiable. MEMORY-MODEL (`docs/MEMORY-MODEL.md`): 18 claims — 14 hold, 4 wrong, all four being body stales against its explicitly-historical R70 pin; the status box (the current model) holds throughout. The two limits are confirmed as R151 reported them: the analysis limit names itself (`E_VAKYA_SEEMA`, `:636`); the tree limit has no code (`E_VRIKSHA_SEEMA` zero hits in `src/`). The docs do **not** repeat any of the R151 brief's errors — no `E_VRIKSHA_SEEMA`, no "two limits name themselves", no `r23_check_call`, no fold description — but they do contradict the R148/R150/R151 findings in three places (§16:995 "three words" and "crashed (confirmed)", §16:1062 "R148's measured boundary").

**Task 3 — the two invented symbols.** Both were caught the same way: a grep for the label as a *definition* over the whole assembly unit, plus the convention that every cited label carries file + line. No mechanical check in the tree would have caught either — the two nearest checks cover library signatures and absence claims, not compiler labels cited as existing. The rule for the method notes: before citing any code label, run `grep -rn "^<label>:" src/ src/*.inc win/` at the base being written about and require ≥1 definition hit; cite the definition with file + line; if the grep is empty, cite the name only as "named in [brief], not found in the tree at [commit]". The limitation, stated honestly: the grep proves a label *exists*, not that it does what the writer claims. That still needs the file + line read.

---

## Task 1 — the fourth record

### The brief's premise is wrong: the sentence was never cut off

The delivered R151 report, `Muse-to-Sarvam/ROUND-151-OWNERSHIP-MUTANTS-FOURTH-ERROR.md`, line 28, reads in full:

> `AssociationOwned` | The association block, `install-core.ps1:760-764`: initialized from the old state (`:760`); set to true only when the installer writes `Sutram.Source` as the `.sm` default because there was none (`:761-764`). Serialized at `:790`. | Whether this installer set the `.sm` default value. | **Partially.** `uninstall-core.ps1:183-188` deletes the `.sm` default only if the flag is 1 **and** the current default is still `Sutram.Source`. The flag is trusted, but the current value is re-checked.

That is the complete sentence. Nothing is cut off. The ROUND-152 brief quotes it as "initialised from the old state (`:760`); set to true only when the i…" — with the British spelling "initialised", which appears nowhere in the delivered report (it says "initialized"). The brief appears to quote a truncated copy or a draft, not the delivered file. The correction belongs on the record, not on the report: this is the second brief premise in two rounds to be wrong about what is in an R151-family return (ROUND-151's own Task 3 premise was wrong the same way). The sentence is completed below anyway, from the v314 code.

### (a) The full sentence, from the v314 code

`windows/native-installer/install-core.ps1:759–764`:

```powershell
$existingDefault=(Get-Item -LiteralPath $extKey).GetValue('')          # :759
$associationOwned=($oldState.ContainsKey('AssociationOwned') -and $oldState['AssociationOwned'] -eq '1')  # :760
if (-not $existingDefault) {                                           # :761
    Set-Item -LiteralPath $extKey -Value 'Sutram.Source'               # :762
    $associationOwned=$true                                            # :763
}                                                                      # :764
```

Completed sentence: **"initialized from the old state (`:760`); set to true only when the installer writes `Sutram.Source` as the `.sm` default because there was none (`:761-764`)."** Serialized at `:790` (`('AssociationOwned=' + [int]$associationOwned),`).

What exactly sets it true: the `if (-not $existingDefault)` branch firing — the `.sm` key (`HKCU:\Software\Classes\.sm`) had no default value at install time, so the installer wrote `'Sutram.Source'` as the default (`:762`) and set the flag (`:763`). What leaves it at its old value: the branch not firing — a default already existed (the user's, or another program's), so the installer wrote nothing and `$associationOwned` keeps whatever the old state said (`:760`): `1` if a previous install set it, `0`/absent otherwise. Note the asymmetry the R151 report already named as drift: when the current default is the user's, a carried-forward `1` stays `1` even though this install set nothing.

### (b) A boolean flag THAT it was set — not a record of WHAT was set

`AssociationOwned` is `0` or `1` (`[int]$associationOwned`, `:790`). It records one bit: *some* install in this state lineage set the `.sm` default to `Sutram.Source` at some point. It does not record:

- what the default was *before* (the user's previous default is never read into any variable, let alone recorded);
- *when* it was set, or by *which* install (no version, no timestamp, no install-dir attached to the flag);
- *what* was set, beyond the constant `'Sutram.Source'` (the value is fixed by the code, so there is nothing to record — the flag's whole content is "the installer did the one thing it does here").

That is why the R151 inventory's gloss "Whether this installer set the `.sm` default value" is the right gloss and also the limit of what the record can say: it cannot distinguish "this installer set it just now" from "a previous install set it and the state was carried forward", and it cannot say what was there before.

### (c) Uninstall trusts it only with re-checks — the exact condition

`windows/native-installer/uninstall-core.ps1:181–188`:

```powershell
if ((Test-Path -LiteralPath $commandKey) -and (Get-Item -LiteralPath $commandKey).GetValue('') -eq $expectedCommand) {   # :181
    Remove-Item -LiteralPath $classKey -Recurse -Force                                                                # :182
    if ($state.ContainsKey('AssociationOwned') -and $state['AssociationOwned'] -eq '1' -and                       # :183
        (Test-Path -LiteralPath $extKey) -and (Get-Item -LiteralPath $extKey).GetValue('') -eq 'Sutram.Source') {  # :184
        $ext=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Software\Classes\.sm',$true)                    # :185
        try { $ext.DeleteValue('', $false) } finally { $ext.Dispose() }                                           # :186
    }                                                                                                                # :187
    Remove-ItemProperty -LiteralPath (Join-Path $extKey 'OpenWithProgids') -Name 'Sutram.Source' -ErrorAction SilentlyContinue  # :188
```

The `.sm` default is deleted only if **all** of these hold: the flag is `1` (`:183`), the `.sm` key exists, **and** its current default is still `'Sutram.Source'` (`:184`) — and all of that is nested inside the outer condition that the class command still equals the expected command (`:181`). So the flag is trusted only with **two** re-checks (command match, current value). Contrast `PathOwned` (`:151`, flag alone) and `DesktopOwned` (`:166–175`, flag + TargetPath match, no list consulted). Note also that the `OpenWithProgids` removal (`:188`) sits inside the command-match branch but *outside* the `AssociationOwned` condition — it is removed on command match alone, independently of the flag (R151 pair 3, limb 1).

### The rule across all four records

| Record | Records WHAT, or a flag THAT? | What exactly it holds | Uninstall's trust |
|---|---|---|---|
| `OwnedShortcuts` | **WHAT** — a list of base64 paths, one per shortcut created/overwritten (`install-core.ps1:367-380`, serialized `:786`) | The paths themselves. Content, not identity: each entry *is* the thing done. | List **+** content check (`uninstall-core.ps1:153-165`: in list **and** target starts with `$InstallDir`, or Terminal arguments contain it). |
| `PathOwned` | **THAT** — a boolean (`:780-781`, `:787`) | Only that *an* entry is installer-owned. Not which path (the path is always `Join-Path $InstallDir 'bin'`, reconstructed, never recorded). | **Alone.** `:151`: flag `1` → `Remove-UserPathEntry (Join-Path $InstallDir 'bin')`. No list, no re-check of what the entry is. |
| `DesktopOwned` (+ locator `DesktopLink`) | **THAT** — a boolean (`:782-783`, `:788`) + a name (`:789`) | Only that *a* desktop shortcut is owned, and which *name* it has. Not the link's contents (target, arguments, icon). | **Flag + TargetPath match** (`:166-175`), never consulting `OwnedShortcuts`. |
| `AssociationOwned` | **THAT** — a boolean (`:790`) | Only that the `.sm` default was set to `Sutram.Source` by some install in this lineage. Not the previous value, not when. | **Flag + two re-checks** (command match `:181`, current default still `Sutram.Source` `:184`). |

The rule, stated once: **only `OwnedShortcuts` records what was done; the other three record that something was done.** Among the three booleans, `AssociationOwned` is the least trusted at uninstall (two re-checks), `DesktopOwned` is trusted on flag + identity match, and `PathOwned` is trusted on the flag alone. The shape of the defect is the same in all three boolean cases — the record is weaker than the thing it stands for — but the consequence depends on what uninstall does with the gap: `AssociationOwned`'s gap is closed by re-checks, `DesktopOwned`'s was live (R151 pair 1), `PathOwned`'s is covered by reconstruction (see below).

### The brief's PathOwned claim, checked against the code

The ROUND-152 shared state says: *"if the user already had a Sutram PATH entry and the installer added another, `PathOwned` is true — and uninstall removes something. Which one is not recorded."*

**What the code actually does.** `Set-UserPathEntry` (`install-core.ps1:240-267`): it reads the current user PATH, normalizes every entry (`Normalize-PathEntry`, `:218-222`: trim, strip surrounding quotes, strip trailing `\`, expand environment variables), and compares case-insensitively to the normalized target. If an equal entry already exists, `$found = $true` and **nothing is added** — the `if ($ShouldExist -and -not $found)` at `:261` is the only add. So the installer adds **at most one** entry equal to its own `bin` dir, and only if no normalized-equal entry exists. The caller (`:664-678`):

```powershell
$pathAddedNow = [bool](Set-UserPathEntry $binDir $true)     # :668
# Own the entry only if this installer created it now or already owned it
# from the previous Sutram installation. A pre-existing manual PATH entry
# remains user-owned and will not be removed by uninstall.              # :669-671
$pathOwned = ($previousOwned -or $pathAddedNow)              # :672
```

Uninstall (`uninstall-core.ps1:151` + `Remove-UserPathEntry`, `:40-60`) removes **every** entry whose normalized form equals the target (`Join-Path $InstallDir 'bin'`): the loop at `:48-53` drops all normalized-equal entries and rewrites PATH.

**Verdict on the claim.** The scenario as worded — "the user already had a Sutram PATH entry and the installer added another" — can happen only for a *different* directory (e.g. an old install's `bin` at another path, or a manual entry pointing elsewhere). In that case the installer adds its own entry, `PathOwned` is true, and uninstall removes **exactly its own** (`Join-Path $InstallDir 'bin'`). **Which one is removed *is* determined — by `$InstallDir`, not by the flag.** The flag's silence on WHICH is real, but the code does not need the flag to answer it: identity is reconstructed from the install directory, and the helper's found-check guarantees there is at most one entry equal to it at install time. The brief's implication — that uninstall might remove the user's entry — does not follow on v314 for the case it describes.

**The genuine residual, narrower than the brief's.** Because removal matches by *normalized equality* rather than by a recorded identity, a user's entry for the **same** directory spelled differently (trailing backslash, quotes, `%VAR%` vs expanded path — all collapsed by `Normalize-PathEntry`) is removed too whenever `PathOwned` is `1`: `Remove-UserPathEntry` drops *all* normalized-equal entries (`:48-53`), and the flag cannot tell the installer's spelling from the user's. That needs `PathOwned = 1` *and* a user entry normalizing to the same directory — a reading inference, not a traced live case, and the installer's own found-check means the user's spelling would have had to arrive after install (or pre-date it while `$previousOwned` was already `1`). A second residual, also by reading: if the install folder is *moved* between install and uninstall, `$InstallDir` at uninstall no longer matches the added entry, so the entry is orphaned (a leak, not a wrongful removal). Neither residual is a live data-loss path on the traced cases; both follow from the same root — the flag records THAT, and identity is reconstructed, not recorded.

### What R153 changed (diff `52d78435` → `origin/main` `b578c281`, installer files only)

The diff touches only the two installer files (install-core.ps1 106 lines changed, uninstall-core.ps1 36). What it changes, in a few lines:

- **`New-Shortcut` is gone, replaced by four functions** (install-core.ps1, new code at ~:367-410): `Get-OldShortcutRecord` (reads the old `OwnedShortcuts` entry for a path, returning its hash or `''` for a pre-v315 record without one), `Test-ShortcutSays` (field-by-field content comparison for hash-less records), `Test-OwnedShortcut` (true only for a link this installer wrote and nobody has changed since), and `Set-OwnedShortcut` (one place that decides *and* records: returns `'created'`, `'updated'`, or `'preserved'`; only the first two are recorded, with the new hash). `OwnedShortcuts` entries are now `"<base64 path>|<SHA-256 of the .lnk as written>"`.
- **The desktop caller is rewritten** (install-core.ps1, ~:740-760): the `$isOurs` closure is deleted; the candidate names are tried in order (`Sutram IDE.lnk`, `Sutram IDE (Sutram).lnk`, … `(Sutram 9).lnk`) through `Set-OwnedShortcut`, and the first name that is not `'preserved'` is the one made. The comment says: *"DesktopOwned and DesktopLink say what was made; nothing removes a link on their word (the uninstaller checks the bytes)."*
- **Uninstall no longer reads `DesktopOwned` at all.** The whole desktop removal block (`uninstall-core.ps1:166-175` on v314 — flag + `DesktopLink` + TargetPath match) is deleted. Uninstall now iterates `OwnedShortcuts`, and removes a shortcut only if its parent is the Start menu or the Desktop directory **and** its current SHA-256 equals the recorded hash (entries without a hash are skipped — `continue` — and a changed link is logged and kept).

Status of the four records after R153 (from the diff alone):

| Record | v314 status | After R153 |
|---|---|---|
| `OwnedShortcuts` | List of paths; uninstall re-checks list + target content. | **Strengthened:** list of `path\|hash`; uninstall checks the hash. Now records WHAT *and* its bytes — the correct record, further hardened. |
| `DesktopOwned` (+ `DesktopLink`) | Boolean flag + name; trusted at uninstall on flag + TargetPath. | **Still written, no longer trusted.** The serializer is untouched (no hunk touches `:780-790`), so the flag is still recorded — but no uninstall code reads it. Its status changes from "trusted independently" to "written but not consulted". (It is still read at *install* time, as `$previousDesktopOwned`, to prioritize the previous name in the candidate list.) |
| `PathOwned` | Boolean; trusted alone at uninstall. | **Untouched.** No hunk touches the caller (`:664-678`), the serializer, or the uninstall line (`:151`). Same status as v314, including the same-directory-spelling residual above. |
| `AssociationOwned` | Boolean; trusted only with two re-checks. | **Untouched.** No hunk touches the association block (`:755-790`) or the uninstall condition (`:181-188`). Same status as v314. |

Pairs 1–3 were not re-audited. On its face: pair 1's mechanism (flag trusted over a preserved link) is gone by construction — the flag is no longer consulted — and pair 2's (overwrite authorized by old-list membership) is gone the same way, since `Set-OwnedShortcut` refuses to write over a link it did not write or that changed. Pair 3's code (the class-key / `AssociationOwned` block) has **no hunk in this diff**, so nothing in R153 touches it. Whether the R153 gate actually runs the new paths, or the new installer was ever run natively, is not checkable from the diff — could not determine from source.

---

## Task 2 — the reference and the memory documentation vs the code

**Documents:** `docs/LANGUAGE-REFERENCE.md` (1528 lines) and `docs/MEMORY-MODEL.md` (222 lines), read in full at v314. **Scope:** only the three categories the brief names — (a) a LIMIT, (b) a CHECK that exists, (c) a CLASS that is closed. Typos, style, and claims outside the categories are not reported.

**174 claims checked: 144 HOLD, 20 WRONG, 10 UNVERIFIABLE BY READING.**

- REFERENCE: 156 claims — 130 HOLD, 16 WRONG, 10 UNVERIFIABLE.
- MEMORY-MODEL: 18 claims — 14 HOLD, 4 WRONG (all four are body stales; the body is the explicitly-historical R70 snapshot, so "wrong" here means "true at the pinned snapshot, false at v314"). The status box — the current model — holds throughout.

### The wrong ones (short list)

REFERENCE (16):

1. `:13` — "every `kosh` has a region of its own and never moves". Small koshes live in the arena at v314; "never moves" was already false at v300 (MAXCAP relocation).
2. `:19` — "Generated from the compiler source and the language packs, so it cannot drift from the code." It has drifted (v300 header; "every kosh has a region"; "at most two modules"; "344 examples"; "rikta kosh se"; likha:303; parimana 16-byte header; "three words").
3. `:303` — likha with exactly three arguments: "the first must be a string literal to select multi-value output". From v287 `likha` with three values prints three values whatever comes first (the doc contradicts itself at :331: "v287 `likha` with three values prints three values, whatever comes first").
4. `:376` — "a program can currently include at most two modules — the inliner's buffer overflows at three or more". `examples/99_ast_multimodule_capacity.sm` includes seven modules; the real caps are the 128 KiB expanded source (`IMPORT_BUF_CAP equ 131072`, `:33`) and the 128-entry function list (`FUNC_DEFS_CAP equ 128`, `:54`).
5. `:438` — "`s + k` (a `kosh`) → `E_VARTANI_CAT`". The rfx binop check tests kosh FIRST (`:9691`, `:9695` → `.rfx_csb_kosh` `:9750`), so `s + k` is `E_KOSH_GANIT`.
6. `:945-946` — empty `kosh_pop` / `kosh_peek` / `kosh_dequeue` abort with "`rikta kosh se kosh_pop`" etc. Actual messages are "`riktat koshat kosh_pop`" etc. ("rikta kosh se" appears nowhere in code; the doc itself quotes the correct form at :938).
7. `:995` — the v313 FFI passage: the slice descriptor is "an address of its three words". The slice descriptor is TWO words (16 bytes: elements + length, `src/r23_capabilities.inc` `r23_gen_slice` `:574+`).
8. `:995` — "so the C side read an address, or, as an `i64` count, crashed (Muse's reading, R151; confirmed)". No crash was demonstrated; R150 line 18: a wrong value, not a wild pointer — a crash comes only from *using* that value.
9. §16 — "A `kosh` grows until the arena is full (1 GiB) or a region's 64 MiB." A region is `max(2*new, R101A_REGION)` — it grows beyond 64 MiB; the binding cap is `R128_MAXCAP` = 2^40 elements (`src/sutram_compiler.asm:21352`).
10. §19 parimana — "`kosh k[1]` grown to 1,000 has capacity 1,024: 16 + 8,192 bytes" and the table's "a kosh of 1000 → 8272" (`:1408`, `:1413`). The kosh header is 32 bytes (4 words), not 16; a capacity-1024 kosh holds 32 + 8,192 = **8,224** bytes.
11. §19 parimita — "What does not count: a `kosh` (it has its own region, section 16)". The operative claim (a kosh does not count against the budget) HOLDS, but the parenthetical reason is wrong at v314 for small koshes (they live in the arena, not a region).
12. §19 — "a block run 100,000 times that makes a `kosh` of 100 numbers peaked at about 100 MB on v283, and at 400 MB on Linux from v284 (each `kosh` now has its own region, one 4 KB page at least - section 16)" (`:1389`). The figure is a v284-pinned measurement, but the parenthetical explanation contradicts §16 at v314 (small koshes are 32 bytes of arena; the per-kosh-region model ended at v301).
13. `:1061` — "The largest statement in the 344 examples and 310 library functions takes 52 steps". At v314 the count is 347 recursive / 331 top-level; neither is 344.
14. `:1062` — "History: … v312 65,536 (refused 16,385 terms - R148's measured boundary)". R148 was read-only, measured nothing, and its report never mentions 16,385 (grep: 0 hits).
15. Header box `:13` — suite PASS=315, crash corpus 227/0, proofs 229/229 and 86/86, gates 65/1/1, installer payload v243. STALE snapshot pinned to v300 (at v314: suite 327, gates 78/0/1, installer v314). Not wrong-as-pinned, but the doc is read at v314.
16. §19 row 2 — the scratch-escape check covers "likh, likh8, kosh_kship … wherever the call is written". `r73_check_call` lists `BN_KOSHPUSH, BN_LIKH8, BN_LIKH8C, BN_SETCHAR, BN_MEMSET` only (`:8697-8710`) — `BN_LIKH` is not in it, and `likh` (BN 1) has no codegen handler at all in the `ge_call` dispatch (only the name-table entry at `:900`).

MEMORY-MODEL body (4; all stale against the R70 pin):

17. §1 — "The push emission explicitly rejects growth on a kosh parameter." v304 allows parameter growth; the old refusal is dead code (`.ge_call_koshpush_param_bad` `:22584` never jumped to since v304).
18. §1/§2 — "Growth … copies existing cells and updates the named variable's pointer" / "It does not emit a matching old-buffer free in that inspected path." Growth updates the shared descriptor's `[d]`, not the variable's pointer; old regions ARE reclaimed (munmap emitted `src/r65_arena.inc:713`, syscall 11; VirtualFree `win/winrt_blob.asm:184-188,312`).
19. §3 — "The growth-on-parameter rejection is specifically motivated in the source by pointer replacement" / "That check does not establish that every other alias is updated when a local kosh grows." The rejection is gone; every alias IS updated via the shared descriptor (R129 verified 20M agreement).
20. §7 — "A grep of the whole compiler source finds **no `munmap` / free emission anywhere** — the old buffer's mapping is never released." At v314 there IS a munmap emission (`src/r65_arena.inc:713`) and VirtualFree (`win/winrt_blob.asm:184-188,312`). The proposed fix HAS landed, so "The test above is expected to FAIL until that lands" is stale too.

### What holds (grouped, so the wrong ones above are not the whole story)

The 144 holds are the bulk of the two documents, and the check was exhaustive within the three categories — a wrong sentence in the reference is a defect precisely because the rest of it is right. Grouped counts: §3 arithmetic 10 hold / 1 unverifiable; §3a library table 12 rows / 16 functions, all hold; §4/§4a likha 6 hold; §4b/§4c aliases 3 hold; §5a strings 8 hold; §6c nirmmita 5 hold; §6d E_GAHANATA 2 hold / 2 unverifiable; §6a 2 hold; §15 dasham 9 hold / 1 unverifiable; §16 kosh 15 hold / 1 unverifiable; size limits §16 :1042-1063, 12 hold; §17 slices 4 hold; §18 phal 6 hold / 1 unverifiable; §19 mandapa 29 hold / 3 unverifiable; §20 parikshita 2 hold / 1 unverifiable; MEMORY-MODEL status box 10 hold; MEMORY-MODEL body 4 hold.

Notable holds worth naming because they were themselves corrected in earlier rounds: the size-limits section's bound arithmetic (3,145,728 // 72 = 43,690; bound 349,521; widest statement 87,316; history v311 200,000 / v312 65,536 / v313 349,521 / v314 200,000 + flag); `dek(k) + 1` → `E_KOSH_GANIT` with the module-initializer case; `k + 0` → `E_KOSH_GANIT` (the fold guard is slice-blind, but the walk runs first and refuses — consistent with R150); the §19 parimita budget, message, N-literal refusal, rounding to 16, nested budgets; the scratch-escape taint rule (a name that has held a scratch address keeps the mark until its block ends, even after `q = 7`); the E_SCRATCH_ESCAPE Sanket line.

### The two limits, confirmed

The analysis limit names itself — `E_VAKYA_SEEMA`, message `src/sutram_compiler.asm:636`, hint `:641`, `r152_ast_hint` `:642` ("`vakya-vriksha-seema`, na parikshana-seema"). The AST/tree limit has NO error code — `E_VRIKSHA_SEEMA` does not exist in `src/` (zero hits); the tree-full message is the plain string `msg_ast_overflow` (`:1452`, "Sutram truti: vakya-vriksh seema atikram") and the hint at `:642` borrows the analysis code only to say the AST limit is *not* the analysis limit. **The docs are consistent with this** — they quote the messages without inventing a code — the R151 brief's "the two limits now name themselves" is overstated, and the docs do not repeat it.

E-code inventory (greps at v314, `src/` + `win/`): `E_VAKYA_SEEMA` 2, `E_PARIKSHA_PADANI` 2, `E_VRIKSHA_SEEMA` **0**, `E_PARIMITA` 4, `E_KOSH_MANDAPA` 7, `E_KOSH_VIBHAG` 7, `E_VIBHAG_ANKA` 2, `E_KOSH_DVARA` 8, `E_VITTI_PRAKAR` 3, `E_KOSH_GANIT` 5, `E_MALA_GANIT` 2, `E_RACHANA_GANIT` 2, `E_VARTANI_TUL` 2, `E_VARTANI_CAT` 3, `E_VARTANI_GANIT` 1, `E_VARTANI_SATYA` 2, `E_MULYA_VINA` 2, `E_LIKHA_TRAYA` 1 (dead use only), `E_ATIPRAVAH` 1, `E_SHUNYA_BHAJAN` 3, `E_PHALA_SEEMA` **0 in src/ + win/ but EXISTS in `lib/`** (library-emitted, not compiler-emitted), `E_MULYA_AYOGYA` **0 in src/ + win/ but EXISTS in `lib/`**, `E_AKARA_ASAMYA` **0 in src/ + win/ but EXISTS in `lib/`**, `E_NIRMMITA_SEEMA` 3, `E_NIRMMITA_RNA` 1, `E_DASHAM_VITTI` 5, `E_DASHAM_KRIYA` 2, `E_GAHANATA` 1, `E_CHAKRA_DASHAM` 4, `E_ANTARAL_MISHRA` 2, `E_SCRATCH_ESCAPE` 3, `E_APARIKSHITA_AHVAN` 1, `E_APARIKSHITA_KARYA` 1, `E_APARIKSHITA_SMRITI` 1, `E_PARSE` 12, `E_UNKNOWN_FIELD` 12, `E_AMBIGUOUS_FIELD` 12, `E_ARITY` 4, `E_VARTANI_STHIRA` exists (`:671,674,33148`), `E_FFI_KIND` exists.

### The docs do NOT repeat the R151 brief's errors

1. No "fold" description in the doc (grep: only an unrelated HKLM line at :805).
2. No `E_VRIKSHA_SEEMA` anywhere in either doc.
3. No "two limits name themselves" phrasing; the size-limits section quotes the actual messages without inventing a code for the tree limit — consistent with R151 report line 173.
4. No `r23_check_call` anywhere in either doc (grep count 0 in both) — consistent with R151 report lines 15, 140, 144 (invented symbol, verified absent).

### Contradictions with the R148 / R150 / R151 findings

1. Doc §16:995 "three words" CONTRADICTS R148 report lines 399–401, 475 (two-word descriptor `[element-address, length]`).
2. Doc §16:995 "crashed (Muse's reading, R151; confirmed)" CONTRADICTS R150 report line 18 (wrong value, not a wild pointer; a crash comes only from *using* the value, and none was demonstrated — R150/R151 were read-only).
3. Doc §16:1092 (`k+0` → `E_KOSH_GANIT`) is CONSISTENT with R150 (the fold guard is slice-blind but the walk runs first and refuses; R150 lines 14, 72, 88).
4. The doc's size-limits section is CONSISTENT with R151 line 173 (no invented tree-limit code; no "two limits name themselves").
5. The doc contains no `r23_check_call` (consistent with R151 lines 15, 140, 144 — invented symbol, verified absent).
6. Doc :1062 "R148's measured boundary" CONTRADICTS R148's own character (a read-only round; no measurement; no "16385" in the R148 report).
7. MEMORY-MODEL body §1/§7 CONTRADICT R129/R150-era findings only in the stale sense (the body is pinned to R70; the descriptor, parameter growth, and munmap changes postdate it).

### Counts at v314 (measured 2026-11-08, for the record)

Examples 331 top-level / 347 recursive; lib prakriya defs 310; lib total bytes 213,886; AST 3145728/72 = 43690 nodes; walk budget default 200000, bound 349521, widest 87316 (21829 terms), largest statement 52 steps (`lib/brihat.smlib:174`).

### Could not determine from source (Task 2)

The 1e5 scientific-notation refusal mechanism (the literal parser's handling of `e` was not located by grep; the R29/MEMORY note that 1e18 is a compile error per R72 corroborates the direction but is not a v314 code citation); the `yadi dosh` handler emission (the message `r26_msg_handle_call` exists — "yadi dosh: phal-prakriya-ahvanam apekshitam" — but the emission was not read); the parikshita prototype-vs-definition mark (how the mark is stored/looked up was not located); the §6a name-kind section (not re-read in this pass); the likha string-value-prints-text mechanism and the §19 "outside a block gives 0" / "same bytes" points and the `likh` dispatch fall-through (reading inferences, not re-derived); the §3 "+5% to +282%" benchmark, the §6d 4,000-call and byte-count figures, the §16 200-million timing, the §19 measured figures (264 KB / 62 MB / 7.8 MB / 78 MB / 2 MB / 64 MB, +11% / +3.5%, the 100,000-pass budget figure) — all measurements, unverifiable by reading.

---

## Task 3 — the two invented symbols, and how to check a symbol exists

### The two catches, precisely

**`r157` — R148 report correction 1** (`Muse-to-Sarvam/ROUND-148-PAPER-REVIEW.md:21-25`, base `0fb61357`). "A grep over `src/` returns zero hits; the only mention in the tree is the brief itself (`Sarvam-to-Muse/ROUND-148-PAPER-REVIEW.md:29`)." The check the brief described — "the expression walk, with its own stack" — is `r137_check_stmt` (`src/sutram_compiler.asm:28402` at `0fb61357`), walking on its own stack `r142_wstack` (defined at `:1565`, pushed by `r142_push` at `28677`), with depth in `r15` and a budget that refuses on exhaustion (`28415–28417`, `R143_WALK_BUDGET`). Re-verified at v314 (`52d78435`): `grep -rn "r157" src/ win/` returns **zero hits**; `r137_check_stmt:` is at `src/sutram_compiler.asm:28452` (line drift between bases, label unchanged). The name now occurs elsewhere in the tree only as a record of the invention: `Sarvam-to-Muse/ROUND-150.md:21` (Sarvam admitting it), `Claude-to-Sarvam/R152-00-...-V314.md:85,88,182` (Claude confirming "Muse is right" and that no document repeats it).

**`r23_check_call` — R148 report correction 4** (`Muse-to-Sarvam/ROUND-148-PAPER-REVIEW.md:37-38`, base `0fb61357`). "A grep over `src/` finds no such label. The actual call-side checks are `r129_check_call` (`28771`), `r126_check_untyped_arg` (`29204`, via `gen_typed_call_arg`), `r108_check_call` (label `12715`, called at `21503`), and `r23_check_return` (`src/r23_capabilities.inc:508–513`)." Re-verified at v314 (`52d78435`): `r23_check_call` returns **zero hits in every** `src/*.inc` and `win/` file; the actual checks on v314 are `r129_check_call` (`src/sutram_compiler.asm:28908`), `r126_check_untyped_arg` (`:29341`), `r108_check_call` (`:12765`), `r23_check_return` (`src/r23_capabilities.inc:510`) — labels and roles unchanged, lines drifted. One honest gap, already noted in R151: the R148 brief itself never contains the string `r23_check_call` (a grep over `Sarvam-to-Muse/`, `ChatGPT-to-Sarvam/`, `Claude-to-Sarvam/`, and `docs/` finds it only in the R148 report), so *which* document first cited the invented name could not be established from the tree. That does not affect the correction — the label does not exist — but the provenance is undetermined from source.

### What actually caught them

Two things, and only two:

1. **A grep for the label as a definition, at the right scope.** Not "does the string occur anywhere" (a mention in a brief would satisfy that — and did: `r157`'s only occurrence *was* the brief citing it), but "is there a definition": a line of the form `^<label>:` in a `.asm` or `.inc` file. Both inventions fail that test outright.
2. **The scope had to be the whole assembly unit.** `src/` alone is not enough: the `%include`d files are part of the same assembly unit, and the R148 correction 2 (146 `call gen_expr` sites, not 133) exists precisely because counting only `src/sutram_compiler.asm` missed 13 sites in the includes (`r23_capabilities.inc` 4, `r32_ffi.inc` 3, `r25_phal.inc` 2, `r65_arena.inc` 4). Re-verified at v314: `call gen_expr` is 133 in `src/sutram_compiler.asm` alone. A label check that greps only the main file can miss a real label in an include — and a writer who greps only the main file can wrongly conclude a real label does not exist. The check must cover `src/*.inc` and `win/` as well.

What did *not* catch them, and would not have: the build (both names were cited in prose, never assembled), the test suite (no test reads briefs), and the gates (they check that things work, not that documents cite real labels).

### The nearest existing checks — and why neither covers this

| Check | What it does | Why it would not catch an invented label |
|---|---|---|
| `tools/check_doc_signatures.py` (run by `tools/gates.sh:228` as the "doc signatures" gate; **FAILs on drift**) | Compares `lib/*.smlib` `prakriya` declarations with signatures in the first Function-column cells of `docs/sutram-stdlib.html`, keyed by module and name (docstring, `:1-12`). | It validates *library* function names against the stdlib docs. Compiler-internal `rNN_` labels are not in `lib/` and not in the stdlib table, so an invented one never reaches the comparison. |
| `tools/doc_stale_claims.py` (run by `tools/gates.sh:229` as the "stale claims" gate; **exit 0 always** — hits are review items, not failures, per its own docstring) | Scans every `.md`/`.html` outside the collaboration folders and `backups/` for sentences shaped like *absence* claims ("there is no X", "not yet implemented", …) and reports file + line for a human to confirm or clear. It exists because seven documents once stated limits that had already been removed (ROUND-32). | It finds absence claims. An invented symbol cited as *existing* is a presence claim — the wrong shape, invisible to the scanner. (It would, ironically, have flagged the R148 brief's own sentence "There is no `r157`" — which is true — as a review item, not as an error.) |
| `tests/r71/test_delivery_tools.py` | Checks source pins (`tools/r71_source.lock.json`) and that specific `call r68_…` strings occur in `src/r71_compiler_entry.asm` (`:56`). | It asserts *specific known* call sites exist; it does not validate arbitrary labels cited in docs or briefs. |
| `tools/check_layers.py`, `tools/check_keyword_prefix.py`, `tools/check_workflow_triggers.py`, `tools/check_version_strings.py`, etc. | Code-structure, keyword, workflow, and version-string checks. | None of them reads a brief or a report, and none validates a cited label. |

**No inventory of compiler routine names exists.** A grep for `r137_check_stmt` across `docs/`, `tools/`, and `tests/` hits only `docs/CHANGELOG.md` and two test files (`tests/r137/test_slice_number.py`, `tests/r143/test_walk_budget.py`) — mentions, not an inventory. There is no file in the tree that lists the compiler's `rNN_` labels, so there is nothing for a writer to check a name *against* except the source itself. That is the gap the rule below closes by making the source the checklist.

### The proposed rule — for the method notes

**Writer-side (before sending a brief or a report):**

1. **For every code label you cite, run one grep for its definition, from the repo root, at the base you are writing about:**
   ```
   grep -rn "^<label>:" src/ src/*.inc win/
   ```
   Concrete examples (all run here, at v314):
   ```
   grep -rn "^r157:" src/ src/*.inc win/            # 0 hits: does not exist
   grep -rn "^r23_check_call:" src/ src/*.inc win/  # 0 hits: does not exist
   grep -rn "^r137_check_stmt:" src/ src/*.inc win/ # 1 hit: src/sutram_compiler.asm:28452 — exists
   ```
   Require **≥ 1 hit that is a definition** — a label at the start of a line, followed by `:`, in a `.asm` or `.inc` file. A `call <label>` hit alone does **not** count: it proves something calls the name, not that the name is defined (and a call to an undefined label would fail the build, which is a different check from the one a writer can run on prose). A hit in a `.md` file does **not** count: a mention in a brief is exactly how `r157` survived — its only occurrence was the brief citing it.
2. **Cite the definition, not just the name.** Every cited label carries file + line at a named commit (the R148/R149 convention). A label without file + line is an unverified claim, however plausible the name looks. Names in this codebase are systematic (`r<round>_<snake>`), so an invented one *looks* right — `r157` and `r23_check_call` both do. The line number is the part that cannot be faked without being checked.
3. **Grep the whole assembly unit, not just the main file.** Cover `src/*.inc` and `win/` as well as `src/sutram_compiler.asm` — the 133-vs-146 lesson. A label that lives only in an include is still real, and a writer who greps only the main file will wrongly conclude it does not exist.
4. **If the grep is empty, do not cite the name as a code fact.** Either describe the behaviour in words without the name, or write it as "named in [brief], not found in the tree at [commit]" and ask the brief's author for the file + line. That is what R148 did for both inventions, and it is the correct handling: the claim becomes a question to the author instead of a fact in the record.

**Reader-side (checking someone else's brief or report):**

5. **The same grep, in reverse.** For each cited label, run the definition grep above at the cited commit. A citation without file + line gets flagged before it gets read — the file + line is what made both inventions checkable in minutes rather than arguable for a round.
6. **Recount, don't carry.** Line numbers drift between bases (`r137_check_stmt`: `28402` at `0fb61357` → `28452` at v314; `r129_check_call`: `28771` → `28908`). A line number cited at the wrong base is stale, not wrong — re-grep at the base you are reading.

**The limitation, stated honestly.** The grep proves a label *exists*, not that it does what the writer claims it does. `r157`'s description ("the expression walk, with its own stack") was of a real check under a wrong name — the label check catches the invented name, not a wrong description attached to a real one. That still needs the file + line read. Like `doc_stale_claims.py`'s own docstring says of itself, this is a floor, not a proof: it catches invented names, not wrong descriptions. The description check is the read itself, and no grep replaces it.

---

## NOT RUN

Windows execution, Wine, the full suite, the gates, any probe program, any build, any installer run — all of it, by the brief's own direction ("Read only. Nothing to compile or run."). The R153 installer figures above are from a read-only diff, cited as such, not from running anything.

## Could not determine from source (consolidated)

- Whether the R153 installer behaves as its comments claim when run natively; whether any native run has exercised the new hash-checked uninstall path.
- Whether any native Windows run has exercised the R153 hash-checked uninstall path (the R152 brief says Windows testing resumes Tuesday morning; no such evidence is in the diff).
- Which document first cited `r23_check_call` — the name occurs in the tree only in the R148 report that corrects it.
- Whether a same-directory differently-spelled PATH entry has ever actually been removed — the removal code would do it, but no such case is recorded in the tree.
- Task 2's ten unverifiable items (listed above): the 1e5 refusal mechanism, the `yadi dosh` handler emission, the parikshita prototype-vs-definition mark, the §6a name-kind section, and the six measurements.

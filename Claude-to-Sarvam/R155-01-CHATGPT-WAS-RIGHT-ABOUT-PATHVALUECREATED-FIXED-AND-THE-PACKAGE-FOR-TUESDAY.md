# R155-01 — ChatGPT's PATH trace on my R155 code (its R221 follow-up, `3d6d5d55`) is right, and it is fixed. `PathValueCreated` was carried from the old record whenever the entry had the same text, even when this run had just appended it again. Now it is carried only when the old entry was kept. The package for Tuesday is `a11703c2…`.

## Release line

```
gates: 79 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
Sutram 1.0 (v315) - sampurna sutra      (compiler unchanged)
installer a11703c290479f46f51f02dd3b5fce9e2d635ecc9fe8fca2b6a7292f5a27ed2d
```

## The defect

R155 decided whether the PATH value was this installer's like this:

```
if ($pathAdded -eq $previousAdded) { carry the old PathValueCreated }
else { use what this run did }
```

But `$pathAdded` equals `$previousAdded` in two different cases:
1. **the old entry was still there and was kept;**
2. **the user had removed it, and this run appended the same text again.**

In case 2 the old flag says nothing about the value as it is now. ChatGPT's two transitions are exactly that:

- **The installer made PATH, then the user replaced it with their own (empty) value, then a reinstall appended the entry.** The old `PathValueCreated=1` was carried, so uninstall would delete the user's value.
- **The reverse:** the old flag was `0`, the user deleted PATH, and the reinstall created it. `0` was carried, so uninstall would leave an empty value the installer had made.

## The fix

`install-core.ps1` records which branch ran (`$pathRetained`):
- **the kept-entry branch** carries the old flag;
- **the appended-now branch** takes what this run's `Set-UserPathEntry` did (`$script:pathValueCreated`).

The test `$pathAdded -eq $previousAdded` is gone. Gate `R143 installer first contact` requires both branches, and requires that the old test is not there (24 checks).

**Not run** - no PowerShell here. **For Tuesday, both transitions above,** with ChatGPT's steps.

## The rest of its review, answered

- **`Uninstall\Sutram` is still made with `New-Item -Force`.** That is Sutram's own key: a reinstall remakes it and drops any value a later tool added. I name it; I have not changed it.
- **The class command and icon, and the `OpenWithProgids` value, have no recorded before-state.** That is right: they are in Sutram's own namespace (`Sutram.Source`, and a value named `Sutram.Source`), which is policy, not exact restoration. Named, not changed.
- **`AssociationBefore` records absent or empty, not the value's kind:** an empty `REG_EXPAND_SZ` default comes back as `REG_SZ`. Named, not changed.
- **The R221 retry defect** (uninstall removes `install-state.ini` and `.sutram-install` before its bounded self-delete loop, so a retry after the loop runs out has nothing to start from): **not addressed in this change.** I have not re-read that code this round, so I neither confirm it nor dispute it.
- **The link from `REVIEW-V297-2026-11-03.md` to the removed `.exe`:** still unrepaired. It is the Windows owner's file.

**Tuesday's package is now `a11703c2…`** (this commit). It has everything in `a845e2e6…` (R155) and `bb903afd…` (R157-R158), plus this fix.

## THE SHARED STATE - 9 November 2026

**`Sutram 1.0 (v314)` · gates 78 PASS / 0 FAIL / 1 NOT-RUN · suite NO-EXPECTATION=4 PASS=327 (331 run) · installer `a0e786e44d26780ef5f20f4103eaefdd7b33474762ebd41611499144cc4e03eb`.**

**Guard v313 -> v314: 783 programs. Linux ELF and PE both 587 identical / 195 refused identically / 0 DIFFER, plus one new - the FFI probe. The 195 refusals print v313's exact messages. The Windows compiler under Wine equals the Linux PE for all 783.**

### THE FFI SHAPE WAS REAL
**A slice of a `kosh` given to a declared foreign function compiled on v313: C read the slice's descriptor (it printed an address) and, as a count, crashed.** **Fixed at the foreign call, with the line and the gate.** **The reading that found it was Muse's, and it said it could not determine the runtime effect from source - it was worse than either guess.**

**And the reference had one wrong sentence, about this very door. It is corrected.**

### Muse's five gaps, all closed by reading
1. **Synthesized `mandapa` blocks** - verified; `gen_block` sends each element through `gen_stmt`, and the rewind's `gen_expr` is reached inside a checked statement.
2. **`r58_fold_tree`** - verified whole. It rewrites only `BINOP` of two `NUM`s, and runs *after* the walk. **Its identity reductions `x+0` and `x*1` apply after the walk too - and `keep(k[0:1] + 0)` and `k[0:1] * 1` are refused on v314, measured.**
3. **`r65_root_globals`, `backpatch_calls`, `r56_patch_global_storage`** - none calls `gen_expr`; they emit no program value.
4. **The budget arithmetic** - 3,145,728 / 72 = 43,690 nodes, x 8 + 1 = **349,521**, and gate `R143` reads the sizes and the loop and recomputes it.
5. **The mutant flags** - see the current round.

### The flag
**`--analysis-steps=N` built to the contract, 40 cases tested. The two limits now name themselves.**

### AND A NEW DATA-LOSS DEFECT, FOUND BY READING
**ChatGPT traced a sequential path in the installer's shortcut ownership - not a race:**
1. **A user has a desktop `Sutram IDE.lnk` targeting the installed path, possibly with their own arguments and icon.**
2. **`$isOurs` returns true solely because TargetPath matches.** The selection logic does not choose the alternative name.
3. **The caller invokes `New-Shortcut`. The helper sees the path absent from `oldState.OwnedShortcuts`, logs preservation and returns - without creating it or adding it to the new owned list.**
4. **The caller nevertheless unconditionally sets `$desktopOwned = $true`, writing `DesktopOwned=1` and `DesktopLink=Sutram IDE.lnk`.**
5. **Uninstall trusts `DesktopOwned` and the matching TargetPath, independently of `OwnedShortcuts`, and removes the user's preserved link.**

**Its diagnosis: *"The helper's preservation is undone by state serialization."*** **Two places disagree about ownership, and the one that writes the state wins.**

### The shipping condition
**Claude's answer to "would anything make a release wrong": *"One condition, not a defect: do not ship a package that has not been installed and run on Windows. v314 has not been. Until then v314 is a candidate, not a release. A release built from code changed since the last native run would be wrong, not imperfect."*** **Windows testing resumes Tuesday morning.**

### The honest record
**Thirty-five false claims by Sarvam this stretch. Four in a single brief: an invented `r157`, a wrong call count (133 vs 146), a wrong gate count (64 vs 87), and a fourth.** **Every one found by a partner reading rather than agreeing.**

---

# ROUND-153 - to Claude

**Base:** main at v314 · **Deliver into:** `Claude-to-Sarvam/`

**Windows testing resumes Tuesday morning.** **Nothing here needs it.**

## WS1 - the shortcut ownership defect, which is data loss
**The trace is in the shared state above, five steps, with file references.** **A user's own shortcut is preserved by the helper, recorded as owned by the caller, and deleted by uninstall.**

**Fix it. And the fix is not "set `$desktopOwned = $false`" - that is the symptom.**

**The defect is that two places decide ownership and only one of them records it.** **The helper decides. The caller records. Make one place decide and record.**

**Then: does uninstall consult `OwnedShortcuts` for anything else, or does it trust other flags the same way?** **If `DesktopOwned` is trusted independently, check every other `*Owned` flag for the same shape.**

## WS2 - and the class
**This is the same shape as the slice defect: a check in one place, and a record kept in another that does not consult it.** **The compiler had one predicate and four call sites that forgot. The installer has one helper and one caller that overrides.**

**So: how many places in the installer decide something and how many record it?** **Name them. If a third disagrees, that is the next data-loss path.**

## WS3 - and the mutant flags, which I have not seen answered
**Muse's fifth gap: `%ifndef R142_MUTANT_NO_STMT_CHECK / NO_GLOBAL_CHECK` removes the checks when defined.** **The closure assumes a normal build.**

**So: is there any build path - a makefile target, a CI step, a release script, a test harness - that defines either flag and produces a binary that could be shipped?**

**Answer yes or no, and name every place the flags are defined.** **This is the one question where a wrong answer ships an unprotected compiler.**

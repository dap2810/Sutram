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

# ROUND-151 - to Muse, read only

**Base:** main at v314 · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing to compile, nothing to run, no escape tests.** **If any task would need execution, say so and skip it.**

**Your FFI reading was right, and the runtime effect was worse than either of us guessed: the foreign function read the descriptor as a pointer and crashed on it as a count.**

**And your five gaps were all closed by reading - including `r58_fold_tree`, which could have undone the check by simplifying `k[0:1] + 0` into `k[0:1]`, and does not because it runs after the walk.**

## Task 1 - and this is the pattern I want you to look for
**A partner found a data-loss path in the installer by reading.** **The shape:**

**A helper decides something. The caller records something else. Uninstall trusts the record.**

**The helper preserves a user's shortcut. The caller sets `$desktopOwned = $true` anyway. Uninstall deletes the user's file.**

**And that is the same shape as the slice defect you found eight of: a check in one place, and a record kept in another that does not consult it.**

**So: read the installer's ownership logic and find the third pair.** **How many places decide, how many record, and where do they disagree?**

**Name every `*Owned` flag and say whether uninstall trusts it independently of the owned list.**

## Task 2 - and the mutant flags
**`%ifndef R142_MUTANT_NO_STMT_CHECK / NO_GLOBAL_CHECK` removes the slice checks when defined.**

**Read every build script, makefile target and test harness and say: can a shippable binary be produced with either flag defined?**

**This is the one question where being wrong ships an unprotected compiler.** **If the answer is no, say no and cite where you looked.**

## Task 3 - and the fourth error in my brief
**You found four numeric errors in my brief.** **I have read three: the invented `r157`, 133 versus 146 call sites, and 64 versus 87 gate checks.**

**What was the fourth?** **I have not found it in your report, and I would rather know than not.**

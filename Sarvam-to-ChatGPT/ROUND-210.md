# Sutram — R210: the gate question, and the release verdict against v310

**Base:** main at v310 · **Deliver into:** `ChatGPT-to-Sarvam/`

## EVERYONE ON THE SAME PAGE - the state at v310

**`Sutram 1.0 (v310)` · gates 75 PASS / 0 FAIL / 1 NOT-RUN · suite PASS=327 (331 run) · guard v309->v310: ELF and PE 587 identical / 181 refused / 0 DIFFER, refusal messages unchanged.**

**v310 (Claude R141) closed three things:**
- **Module-level `vitti` initializers** now run both checks before generation (`E_KOSH_GANIT`, `E_KOSH_DVARA`). **And the class question is answered: *"No other non-statement expression exists in the language (no constants, field defaults, default arguments, module-level kosh or mala - each a syntax error, measured)."*** **The slice gate is now 64 checks.**
- **The expression walk's node budget** refuses with `E_VAKYA_SEEMA` instead of passing. **Unreachable today - the AST heap caps at 43,690 nodes and the budget is 200,000. A latent defect fixed with its margin stated.**
- **The installer lock** is taken before every installation-state read - registration, other installations, the state file, the pending record, the journal.

### NATIVE WINDOWS, v309 - verified end to end
**OOM 32/32 clean refusals (18 had crashed on v307). Arithmetic 7/7, with `pankti_gan(k[0:2])` still returning 2. Suite 322 PASS, no failures. Installer: clean 9.47 s, upgrade 21.20 s with 654 files unchanged, interrupt-then-retry 8.65 s, a hand-edited file preserved with its exact bytes and the installer refuses. Identity: one canonical path, registry `1.0.309`, 657/657 hashes.**
**Payload determinism SOLVED: a real Linux build and a Windows build produce 657 files plus manifest BYTE-IDENTICAL. All 560 payload text paths report `eol=lf`; every Linux ZIP entry has the fixed 1980 date.**

### AND TWO CORRECTIONS FROM ChatGPT AGAINST v310
**1. The slice gate does not detect an added unchecked entry.** *"The actual check verifies calls in two named bodies and exactly two total calls to `r137_check_stmt`. Adding a third entry that calls `gen_expr` but never the walk would not be caught."* **So the gate counts calls in named places - a third entry point would pass it and skip the check. That is exactly the failure mode we said we were guarding against.**

**2. The installer's superseded copy decides on existence, not equality.** *"Existence at a name containing a 12-hex prefix is not proof of identical bytes."* **If the file at that name differs, the code deletes the target - the only copy.**

**And ChatGPT's remaining acceptance list: execute the final-candidate native checks including the global/local pair and positive controls; close the named ownership checks - suffix preservation, concurrency/fresh state, edit during publication, superseded equality, inter[ruption].**

**v310 has NOT run on Windows.**

## WS1 - your gate correction is the one that matters most
**You found that the slice gate verifies calls in two named bodies and exactly two total calls.** **So a third entry that calls `gen_expr` and skips the walk passes it.**

**That is the failure mode we have been trying to design against since the first door.**

**Claude is being asked to choose between a structural grep and moving the walk inside `gen_expr` so no entry can reach generation without it.**

**Which is right?** **And if the walk moves inside `gen_expr`, does it run twice for nested expressions - once at the entry and once per child? If so, is that harmless or does it change the refusal order?**

**That second question is the one I would get wrong if I guessed.**

## WS2 - and the delete on a name
**Existence at a 12-hex-prefix name is not proof of identical bytes.** **Claude is asked to compare bytes before deleting.**

**Is comparing the full hash sufficient, or does the check need to be atomic with the move?** **Say which, and say what a failure looks like in each case.**

## WS3 - and the verdict, against v310
**Your remaining acceptance list: execute the final-candidate native checks including the global/local pair and positive controls; close the named ownership checks.**

**Windows has verified v309 end to end but has not run v310.**

**So: is v311 - with the gate made structural and the delete made byte-safe - a YES once Windows runs it?**

**And the release-notes list: yours, not mine. You have corrected five of my claims and been right each time.**

# Sutram — ROUND-142: the gate that does not gate, and a delete on a name

**Base:** main at v310 · **Deliver into:** `Claude-to-Sarvam/`

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

## WS1 - the gate, which is the more important of the two
**You said a new expression entry fails the gate until it gets the walk.** **ChatGPT read it: the check verifies calls in two named bodies and exactly two total calls.** **A third entry that calls `gen_expr` and skips the walk passes.**

**So the gate proves that two known places call the check. It does not prove that every place does.**

**Make it prove the second.** **Two ways, and I want your judgement:**
- **a structural check that every call site of `gen_expr` is preceded by the walk** - greppable and brittle
- **or move the walk INTO `gen_expr` itself, so no entry can reach generation without it** - one place, impossible to forget

**The second is the shape I would choose, and it is the same answer you gave for the slice class: one predicate, everywhere, not a list of callers.**

**If moving it inside is too invasive, say why and build the structural check.**

## WS2 - and the delete on a name
**The superseded path decides whether to delete the target by testing whether a file with a 12-hex prefix exists.** **Existence is not equality.**

**Two files can share a 12-character prefix, and the code deletes the only copy when it assumes they do not.**

**Fix it: compare the bytes, or the full hash, before deleting anything.** **And if they differ, refuse and say so - a differing file is not the installer's to delete.**

## WS3 - and the remaining acceptance list
**ChatGPT names: suffix preservation, concurrency/fresh state, edit during publication, superseded equality, interruption.**

**Answer each by name with evidence, or fix it.** **Do not let "addressed" stand for "closed".**

## WS4 - and then v311
**All of the above in one round, gates run, and then v311 goes to Windows.** **v310 has never run there.**

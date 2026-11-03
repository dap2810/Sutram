# ROUND-113 — Confirm the 16, rank them, and find the 17th (there is none in this class)

Base: v292 (worktree at `51eb8266`, the last v292 commit — the brief's base). Note: Claude's v293 (rachana refusal + sankhya_bindu as an integer dot) landed after this brief was written; it is not in scope here and I did not audit it — that is a future round's job if Sarvam asks.

## WS1 — the rank that decides the work (all 16, two columns each)

First, a correction to the brief's example: `patra_asti` on a directory is NOT wrong. A directory exists AND opens read-only, so both predicates give 1 — the function is correct there. The wrong cases are exists-but-won't-open: permission-denied files and symlink loops (verified: loop → 0). So patra_asti is WRONG, but only in the differing cases, not for directories.

Second, on wrong-vs-different: all 16 are WRONG ANSWER (from R112, unchanged). None is merely DIFFERENT — in each case the returned number is not the promised computation. (Patra_asti answers a different question (opens vs exists), and that difference produces wrong answers exactly when the predicates differ — so it is wrong, with a different-question mechanism, not a docs-only difference.)

| Function | Wrong or different? | Reachable by accident? | Why |
|---|---|---|---|
| ganit.dvigun | WRONG | No — needs near-MAX | Ordinary doubling is small; only a deliberate huge input (or a computation grown to MAX) wraps. |
| ganit.trigun | WRONG | No — needs near-MAX | Same. |
| ganit.vardh | WRONG | No — needs MAX | Only MAX itself wraps. |
| ganit.nirapeksh_mulya | WRONG | No — needs MIN | Only MIN itself wraps. |
| ganit.mahattam_samapavartak | WRONG | No — needs MIN | Only (MIN, 0) violates non-negativity. |
| ank.viparyay_ank | WRONG | No — needs a 19-digit reverse-overflow | Ordinary reversals are small. |
| ganita.ganita_nirapeksh | WRONG | No — needs MIN | Same as #4. |
| ganita.brahmagupta_kshetr | WRONG | **Yes — small sides, odd sum** | (1,1,2,3) and (2,3,4,0) are ordinary; roughly half of all side-tuples have odd sums, so a student computing areas hits this often by accident. |
| aadhar.brihat_ank_se | WRONG | **Yes — length mismatch** | Passing a longer digit array than n (miscounted n, or more digits than expected) is a plausible student mistake, not a huge value. |
| brihat.brihat_ank_tak_laghu | WRONG | No — needs 19 nines | Ordinary conversions are short. |
| patra.patra_asti | WRONG (differing cases only) | **Yes — real-world paths** | A student checking user-supplied or system paths can hit permission-denied files or symlink loops without intending an edge case. (Not for directories — correct there.) |
| sadhan.yog_seema | WRONG | No — needs a huge single-element range | Only near-MAX/2 single elements trigger the sentinel. |
| samanvaya.adish_gunan | WRONG | **Yes — mismatched vectors** | Forgetting to check lengths, or passing vectors from different sources, is a common student mistake. |
| sankhyiki.bindu_gunan | WRONG | **Yes — mismatched vectors** | Same — and 207 actually does it (see WS3), proving it is reachable, not hypothetical. |
| suchi.suchi_shreni | WRONG | No — needs allocation failure | A rare condition, not an ordinary call. |
| vakyank.varna_tak_dashm | WRONG | **Yes — leading zeros** | Padded/fixed-width numbers ("000...01") are common formatting; a student parsing one does not intend an edge case. |

**The split (the whole value of this round): 6 reachable by accident = defects to fix first** (brahmagupta_kshetr, brihat_ank_se, patra_asti, adish_gunan, bindu_gunan, varna_tak_dashm). **10 need a deliberate huge input or a rare condition = documentation priority** (dvigun, trigun, vardh, nirapeksh_mulya, mahattam_samapavartak, viparyay_ank, ganita_nirapeksh, brihat_ank_tak_laghu, yog_seema, suchi_shreni). "Documentation" here means fix-by-documenting-the-limit + lower priority — not "not a defect": the values are still wrong for those inputs, but a student will not hit them by accident, so the urgency is lower. (This refines, not reverses, R112's HIGH/MEDIUM/LOW: the HIGH group splits into accidental (fix first) vs deliberate-MAX (document first).)

## WS2 — the 17th: there is none in the wrong-type class (0 out of 306)

Re-ran the audit over all 306 functions with the new lens (wrong TYPE, not wrong value — bits vs value, address vs value, boolean vs index/count/value, count vs index, collection vs scalar, dasham vs vitti), in the same three-way split. **Result: 0 firm wrong-type flags.** The library's return-type discipline is uniform and documented (out-parameter + count/flag convention), and every function's return type matches its name's promise. The R112 flags were checked explicitly for a second, type-level defect: none has one — each returns the promised type with a wrong value (e.g., dvigun returns an integer as promised, just the wrong integer; patra_asti returns a boolean as promised, just for the wrong predicate). So there is no function that is BOTH wrong-value and wrong-type, and no 17th in this class.

Caveats (notes, not flags, not counted): `ganita.samasa` and `chandas.meru_mala` have no `nivartanam` — reading their return gives an uninitialized-register garbage integer (probed: samasa's return was 136151916609632 on one run, though its `out` was correct). That is an unspecified-return trap, not a type mismatch (the name promises no returned scalar), but it deserves a one-line contract note ("returns nothing; do not read the return"). `nighantu_kunji_gudh` returns a bucket index, not the raw hash its name suggests — a naming looseness (both integers), not a type difference. Samanvaya's out-writers return element counts under a documented module contract ("outputs are written in place") — the thinnest line, but a documented convention, not a flag.

If Sarvam wants a 17th, it is not in the wrong-type class. The next class to look in would be unspecified returns (samasa/meru_mala above) — but that is a contract gap, not a wrong type, and it should not be counted as the 17th without saying so.

## WS3 — how many of the 299 examples call any of the 16? 6 files call them; 1 is actually wrong today

**Callers (true lib calls, code-stripped, v292): 6 files.** 10_mathlib (dvigun(21), trigun(14), vardh(41)), 61_stdlib_math (nirapeksh_mulya(-5), mahattam_samapavartak(48,36)), 62_stdlib_num (viparyay_ank(1234)), 202_brahmagupta_area (brahmagupta_kshetr × 4), 126_numeric_pipeline (bindu_gunan(u,v)), 207_sankhyiki_vector (bindu_gunan(a,b), bindu_gunan(a,c)). The other 10 flags have zero example callers. Note: 143_xmm_cache_barriers and 64_param_reassign define their own local `vardh` and are NOT lib callers — counting them would overcount.

**Actually wrong today: only 207_sankhyiki_vector** (bindu_gunan(a,c): a is len 2, c is len 3 (pushed 3 into a cap-2 kosh, which grows), so it gives 7.000000 — a prefix sum, not a dot product; its golden encodes the bug). Every other caller uses safe inputs, so their outputs are correct: 10/61/62 use small numbers (42, 42, 42, 5, 12, 4321 — all correct); 202 uses even-sum sides only (3,4,5,0 → 6; 5,5,6,0 → 12; 3,4,5,6 → 18; 4,4,4,4 → 16 — all match the true values, and its golden confirms it); 126 uses equal lengths (u,v both len 2 → 11, correct). So for our own code the defect is ALMOST theoretical — but not quite: 207 is wrong today, and fixing bindu_gunan to refuse on mismatch would change 207's output (7.000000 → refusal) and require a golden update. 207's comment ("mismatched lengths use the shorter one") documents the truncation, so it is a known-convention wrong, not a silent surprise — but per R111 it is still not a dot, and the priority does not drop to zero.

NOT RUN: Windows, browser, implementation (none authorized), native-speaker review, full suite (no tree changes; R111's v292 numbers stand: suite 295/299, gates 60/1/1, guard 705 0 DIFFER), v293 audit (out of scope — see base note above).

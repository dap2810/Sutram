# Round 107 — The three replacements verify, the two other flags re-named, the frozen-pack question answered directly, all 30 listed

Base: main at v291 (worktree `a430defb`, R109 hand-back; compiler `Sutram 1.0 (v291) - sampurna sutra`, unchanged). No tree changes, no implementation. Bodies were read before answering — the rule that caught all five flags.

## WS1 — the three replacements: all three PASS, one with a word-form note

**`kosh_apanay` (replaces `kosh_muc`, for dequeue) — PASS on meaning, PASS on collision, NOTE on word-form.**
Meaning: `apanay` (apa + nī, to lead away, to remove) names removal, and dequeue removes the first element and keeps the rest (R106 probed: dequeue = 1, len 3 → 2, peek 3) — where `muc` (release) named nothing the function does. PASS.
Word-form: `apanay` is the stem/root form; the full noun is `apanaya` (अपनय, removal). This is the same root/stem decision point as R106's systematic finding — if roots are accepted (precedent: keyword `yoj`), it passes; if the rule is strict complete words only, it should be `kosh_apanaya`. Flagged, not rejected.
Clash with `kosh_pop`'s `kosh_hri` (R180's question): no namespace clash — different words, and the collision audit below finds neither anywhere else. But they are near-synonyms (both take/remove verbs) and the front-vs-top distinction is NOT in the names: dequeue = front (`apanay`), pop = top (`hri`). A reader cannot tell which end each operates on from the name alone; the docs must state the ends explicitly.
Collision: NONE across builtins (47) / REPL (6) / keywords (34) / lib (306) / lang Latin tokens (54) / example identifiers (493, code-stripped) on v291.

**`anka_akshar` (replaces `akshar_tas`, for `char_from(code)`) — PASS, and the inverse confirms it.**
Compound: two complete words, `anka` (number, mark, code) + `akshar` (letter, character) — no root, no suffix. Direction: `anka` first (the source, a number) → `akshar` second (the result, a letter), which is exactly what `char_from(code)` does — where `akshar_tas` was backwards (akshar + tas = "from a character") and `tas` was a suffix, not a word.
Inverse check, probed on v291: the existing builtin `aksharank("B")` = 66 — letter → number. So `anka_akshar` (number → letter) is its exact inverse, and the word order encodes the direction in both names (letter-number one way, number-letter the other). That symmetry is the strongest confirmation a name can get.
Collision: NONE on v291 (same six-way audit). `anka` alone is a keyword, but `anka_akshar` is a different identifier — word boundaries, no collision.

**`likha_santat` (replaces `likha_bindu`, for `lkhb`) — PASS.**
`santat` (सन्तत) is a complete word, an adjective: continuous, uninterrupted, constant. `lkhb` prints a number with no newline (R106 probed: `lkhb(7)` → `7`, no point) — printing with no break is continuous printing, where `bindu` (point) named a point the function never prints. PASS.
Better word (R180's question): `avichchhinna` (unbroken, uninterrupted) is more precise, and `nirantar` (incessant) is also apt — but `santat` is the better trade: short, common, and correct. Keep `santat`.
Collision: NONE on v291 (same six-way audit).

## WS1, the fourth replacement (from R180, same set) — `vartani_sandhi` PASS

`vartani_sandhi` replaces `vartani_yoj`, which Claude's R110 blocked: a name ending in `yoj`, followed by a space as people write calls, is misparsed as an include. Reproduced on v291: `vartani_yoj ("ab", "cd")` → `E_MODULE_MISSING: yoj patra aprapt: ("ab"` — the scanner took it as an include of a file called `("ab"`. The same call without a space parses as a call (fails only with `agyat prakriya`, because the builtin does not exist yet). `kosh_yuj (k, 2)` with a space parses as a call too — `yuj` is safe, `yoj` is not.
`sandhi` (सन्धि) is a complete word, a noun: joining, junction, combination — the grammatical term for joining. `vartani_cat` joins strings; concatenation IS joining. PASS on meaning and on word-form.
Scanner: `vartani_sandhi ("ab", "cd")` with a space parses as a call on v291 (`agyat prakriya: vartani_sandhi` — unknown only because it is not implemented yet, not misparsed as an include). Probe delivered as `vartani_sandhi_space.sm`. PASS — `sandhi` avoids the bug.
Collision: NONE on v291 (same six-way audit).

## WS1, the other two flags, named again as asked

**`saha` → no new name needed. Use `sahayata`, which already exists.**
`saha` means "with", not "help", and truncates the existing `sahayata`. The audit finds `sahayata` already in the REPL (the help command, alongside `nirgat` for exit). So the recommendation is not a new name at all: drop `saha`, and the help word is `sahayata`, already in the tree. This is also why the count reconciles (see WS3) — `sahayata` is not a new name.

**`smaran_kriti` → `smaran_pratilip`.**
`kriti` (making) is vague; `pratilip` is already the copy word (`vartani_pratilip` exists), so `smaran_pratilip` (memory + copy) names `smaran_cp` (copy memory) consistently. Two complete words, no root. Collision: NONE on v291 as a whole identifier (`vartani_pratilip` is a different name — word boundaries).

## WS2 — the two collisions Claude found, resolved

**`to → prati` is DROPPED — confirmed correct, and the drop is complete, not partial.**
Claude's R110 and R106 agree independently: `prati` is the legacy spelling of `nivartanam` (return; 60 files use it), and `to` is not accepted at all — it sits in the retired-spelling table whose replacement is `tak`, the `chakra` loop's "up to" (`chakra i = 0 to 3` is a syntax error on v291). So the row would either make the loop word mean return or "delete" something already gone. Dropping it leaves `to` retired, `tak` its word, and `prati` the return alias — exactly Claude's suggestion, and exactly R106's correction (`to` → `tak`, not `prati`). No further action.

**`Error → truti` in the 11 `.sandesh` files — YES, it crosses the frozen-pack rule as written. Direct answer, with the scope split.**
The freeze (owner rule, LANGUAGE-PRIORITY) says the non-Sanskrit packs are frozen: stay in tree, keep working, no new development. The gate enforces it: `tools/sandesh.py --check` requires every translation to keep `Sutram Error` unchanged. Claude made the change in a scratch copy and ran it: 748 failures, 68 in each of the eleven packs. So:
- The Sanskrit pack CAN be updated — it is the default, not a frozen pack.
- The other ten packs CANNOT be edited under the rule as written — each carries `Sutram Error` in 68 translated messages, and editing them is editing frozen packs, which the rule forbids agents from doing unprompted.
- The gate rule itself would also have to change (`sandesh.py --check` must accept `Sutram truti`), and changing the gate is changing the rule, not just the packs.
Measured blast radius beyond the packs: 81 goldens in `tests/expect/` contain `Sutram Error` (their expected outputs change), and 12 runtime message kinds are compiled INTO emitted programs (`E_GAHANATA`, `E_SHUNYA_BHAJAN`, the `mala` bound, `kshetra purnam`, `E_PARIMITA`, the empty-`kosh` messages, and more — Claude's `runtime-messages-in-compiled-programs.txt`). Those are compiler changes, not pack edits, but they change every emitted program's error output, so the guard needs a re-baseline after them.
The choice, stated plainly: (A) grant a narrow, explicit owner exception to the freeze — change ONLY `Sutram Error` → `Sutram truti` in the ten frozen packs' 68 messages each, update the gate rule, update the 81 goldens, re-baseline the guard — no retranslation, no other pack edits; or (B) keep the packs frozen, in which case `truti` lives only in the default/Sanskrit messages and the packs keep `Error` — two error prefixes, one per language.
My recommendation is (A), scoped as above: a half-renamed error prefix defeats the vocabulary change's purpose (one Sanskrit error word) and confuses more than a scoped exception does. But both the vocabulary change and the freeze are owner-approved, so the owner must say which yields — the exception is the owner's to grant, not mine to take.

## WS3 — all 30 names, so the next brief cannot miss two again

The reconciliation first, because it explains the 30-vs-28 dispute: **30 is the count of table entries; 28 is the count of truly new names. Both were right under different definitions.** The two already-existing names are `kuru` (the do-while keyword, same meaning "do" — a message word, not a code collision, and NOT a new name) and `sahayata` (the existing REPL help command, replacing `saha` — not a new name). 30 − 2 = 28.
The "25 clean, 3 blocked, 5 wrong" from the build commits reconciles the same way: 25 name-clean (30 − 5 wrong) = 23 buildable + 2 blocked-but-clean (`truti`, pack gate; `vartani_yoj`, scanner — now replaced by `sandhi`); the 3 blocked ROWS are `to` (dropped, not a name), `truti` (pack), and `vartani_yoj` (scanner, now `sandhi`). 25 + 3 + 5 = 33 double-counts `truti` and `yoj`, which sit in both the clean set and the blocked set.
The final 30, with status (replacements in brackets; roots marked † — see the note below):

| # | Final name | Replaces / notes | Status |
|---|---|---|---|
| 1 | `asti` | operator, == | new, clean |
| 2 | `nasti` | operator, != | new, clean |
| 3 | `truti` | message, Error | new, **BLOCKED (pack gate, WS2)** |
| 4 | `patra` | message, file (already means file in messages, `patra-ant` = EOF — consolidation, not collision) | new, clean |
| 5 | `rekha` | message, line | new, clean |
| 6 | `kuru` | message, do | **NOT NEW — existing do-while keyword, same meaning** |
| 7 | `kosh_kship` † | push | new, clean |
| 8 | `kosh_hri` † | pop | new, clean |
| 9 | `kosh_gan` † | len | new, clean |
| 10 | `kosh_ksham` | cap (thin: `ksham` = capable adjective; capacity noun is `kshamata` — noted, not rejected) | new, clean |
| 11 | `kosh_iksh` † | peek | new, clean |
| 12 | `kosh_rikt` | empty | new, clean |
| 13 | `kosh_shodh` † | clear | new, clean |
| 14 | `kosh_yuj` † | (ends in `yuj`, not `yoj` — safe from the scanner) | new, clean |
| 15 | `kosh_apanay` † | dequeue [was `kosh_muc`] | new, clean (stem note, WS1) |
| 16 | `pankti_gan` † | (for `pankti_len`) | new, clean |
| 17 | `tyaj` † | exit (REPL duplication noted: `nirgat` already exists for exit) | new, clean |
| 18 | `sahayata` | help [was `saha`] | **NOT NEW — existing REPL command** |
| 19 | `jala` | net (thin: water primary, net secondary — valid, noted) | new, clean |
| 20 | `jala_bandh` † | netbind | new, clean |
| 21 | `jala_shru` † | netlisten | new, clean |
| 22 | `jala_grah` † | netaccept | new, clean |
| 23 | `akshar_laghu` | char_lower (probed 65 → 97) | new, clean |
| 24 | `akshar_guru` | char_upper (probed 97 → 65) | new, clean |
| 25 | `anka_akshar` | char_from [was `akshar_tas`] | new, clean |
| 26 | `vartani_sandhi` | vartani_cat [was `vartani_yoj`] | new, clean |
| 27 | `likha_santat` | lkhb [was `likha_bindu`] | new, clean |
| 28 | `likha_rup` | likha_fmt | new, clean |
| 29 | `sankhya_bindu` | sankhya_dot (neither old nor new name says "product" — full term `sankhya_bindu_gunana`, noted) | new, clean |
| 30 | `smaran_pratilip` | smaran_cp [was `smaran_kriti`] | new, clean |

Net: 29 buildable (all except `truti`) + 1 blocked (`truti`, pack gate) + `to` dropped (not a name, not in the 30).
† Root/stem note (systematic, carried from R106): 12 forms (11 distinct roots — `gan` twice) in the final 30 are bare roots or stems, not complete words (`kship, hri, gan, iksh, shodh, yuj, apanay, tyaj, bandh, shru, grah`) — the three replaced roots (`muc, tas, yoj`) are gone, `apanay` (stem) is added. The constraint (R178: every name a complete word, never a fragment) still needs the owner's explicit decision; precedent exists (keyword `yoj` is a root). The six replacements are otherwise clean: `apanay` is the only stem among them (`anka_akshar, vartani_sandhi, likha_santat, smaran_pratilip` are complete words or compounds of complete words).

## What was NOT run

Windows, browser, implementation (no aliases are built yet on main — the "build the 25 clean" commits added no `bn_` entries; this audit is still pre-implementation), native-speaker review, full suite (no tree changes; R110's re-run on v291 stands: suite 289/293, gates 59/1/1, guard 699 programs 0 DIFFER from R109). R105's pending WS2 — the attack on ChatGPT's R178 arena DESIGN itself (as distinct from the branch attack, a distinction Sarvam's R180 now acknowledges) — is still pending and is not covered by this round.

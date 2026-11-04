# ROUND-117 — The 33 names, audited before Claude builds them

Base: v296 (worktree at `bce54059`, current main). Source: `ChatGPT-to-Sarvam/ROUND-191-BUCKETS.csv`, bucket 1 (exclusive_word_bucket == 1), 33 words, each classified by reading the body (not the substring).

## The four tests (defined here, since no four-test is defined in R191 or in my earlier rounds)

These are the four I have applied across R106/R107/R109/R112, stated so the verdicts are checkable:

1. **Meaning** — the Sanskrit word names what the body DOES, not what the English suggests.
2. **Collision** — no clash with existing builtins, REPL commands, keywords, lib functions, lang tokens, or example identifiers (six-way grep; all seven new proposals below return zero hits).
3. **Form** — follows the tier rule (see WS3): a function takes the shortest recognizable form; a concept takes a complete word.
4. **Distinctness** — not a near-synonym of an existing name that would confuse; if it is close, the docs must state the difference.

## WS1 — the 33, one row each (English word, what it does, proposed Sanskrit, verdict)

**Seven need a NEW Sanskrit name (bodies read, proposals below):**

| Word | What it does (body read) | Proposed Sanskrit | Four-test verdict |
|---|---|---|---|
| bit | `bit_gan(n)` counts set bits (1s) in n's binary form; negatives return 0 (R28-pinned) | `dvyank_gan` (dvi + ank = binary digit; gan = count) | PASS (meaning: dvyank = binary digit; collision: 0 hits; form: function → shortest recognizable compound; distinctness: distinct from ank (digit) by dvi (binary). Note: it counts SET bits, not all bits — docs must state that, as the body does.) |
| diff | `rakh_samroop_diff(a, cap, b, bcap, out)` adds every element in exactly one of a, b into out — (a−b) ∪ (b−a), symmetric difference; returns rakh_maap(out) | `rakh_samroop_bhed` (bhed = difference, already the tree's word in khand_bhed, varna_bhed, rakh_bhed) | PASS (meaning: bhed = difference, and the body computes a difference; collision: 0 hits; form: function → noun, consistent with the other _bhed functions; distinctness: distinct from plain rakh_bhed by samroop (same-form), exactly as before — no new confusion.) |
| pad | `roop_pad_vam/dakshin/madhya` (and `pad_vam`) pad a form left/right/center with a byte to a width | `roop_puran_vam/dakshin/madhya`, `puran_vam` (puran = filling) | PASS (meaning: puran = filling, and the body fills to width; collision: 0 hits; form: function → puran is the shortest UNAMBIGUOUS form — the root pur is shorter but also reads as "city", so puran wins on distinctness; distinctness: no other roop_* uses puran.) |
| path | `patra_path_sarv(path, out, cap)` opens a file path read-only, reads up to cap bytes into out, closes; returns the byte count or −1 | `patra_marga_sarv` (marga = path/route/way) | PASS (meaning: marga = path, and the argument IS a path; collision: 0 hits; form: function → marga is the standard noun, no shorter root means "path"; distinctness: distinct from patra (file) — this reads a file VIA its path, as patra_likh_sarv writes one.) |
| pre | `roop_ank_pre(v, base, upper, out)` formats a number in any base WITH its prefix ("0b"/"0o"/"0x" for 2/8/16; none otherwise) | `roop_ank_upasarg` (upasarg = prefix, the grammatical term) | PASS (meaning: upasarg = prefix, and the body adds the base prefix; collision: 0 hits; form: function → the standard grammatical noun, not a coinage; distinctness: distinct from other roop_ank_* (aadhar, dhvaj) — upasarg names the prefix specifically.) |
| sign | `roop_sign_akshar(v, signch, out)` puts signch (e.g. 32 blank, 43 '+') in place of '+' for non-negative values; negatives always get '−' | `roop_chihn_akshar` (chihn = sign/mark/symbol) | PASS (meaning: chihn = sign, and the function places the sign character; collision: 0 hits; form: function → chihn is a short standard noun; distinctness: chihn qualifies akshar (character) — "the sign character" — no confusion with plain akshar.) |
| sorted | `asti_sorted(a, n)` / `suchi_asti_sorted(l)` return 1 if the elements are in non-decreasing order, else 0 (empty/singleton count as sorted) | `asti_shrenit`, `suchi_asti_shrenit` (shrenit = sorted, from shreni (to sort) + −t participle) | PASS (meaning: shrenit = sorted, and the body checks non-decreasing order; collision: 0 hits; form: predicate → asti + adjective, like asti_sampurna (is complete) and asti_abhajya (is prime); distinctness: distinct from shreni (the verb/noun "sort") by the −t (sorted vs sort) — the same verb/participle distinction the tree already uses.) |

**Nineteen are ALREADY renamed in v292 (or withdrawn) — no new action, just the alias-retirement question (separate):** cap → kosh_ksham, cat → vartani_sandhi, char → akshar_laghu / akshar_guru / anka_akshar, clear → kosh_shodh, dequeue → kosh_apanay, dot → sankhya_dot → sankhya_bindu → WITHDRAWN (v295, E_PRATYAHRITA), empty → kosh_rikt, enqueue → kosh_yuj, fmt → likha_rup, from → anka_akshar (char_from), len → kosh_gan / pankti_gan, lower → akshar_laghu, upper → akshar_guru, netbind → jala_bandh, netlisten → jala_shru, netsock → jala, peek → kosh_iksh, pop → kosh_hri, push → kosh_kship. The old names still exist as aliases (with warnings), so the English words still appear in the tree — but the Sanskrit names already exist and are primary. Two caveats from R112 WS3, restated so they are not lost in a "done" count: kosh_ksham is thin (ksham = capable, a property, for capacity, a number — the old kosh_cap was correct and the rename degraded it), and likha_rup is meaning-changing (old promised printf substitution, new promises form, both unmet differently). Those two renames are imperfect even though they exist; the other seventeen are sound.

**Seven should NOT be renamed (WS2, below) — they are not names:** arr, enter, fd, lib, root, space, tab.

## WS2 — the ones that should NOT be renamed, and why

- **arr** — a parameter name (brihat/mala: `arr` = the array pointer argument) and an example-local identifier (array_demo). A student never writes `arr` as an API call; it is a local name inside bodies. Renaming it would churn locals, not the API. STAYS.
- **enter** — the Enter KEY in the REPL banner ("Sutram-kathanam likhatu, Enter nudatu" — "write Sutram statements, press Enter") and in example prompt strings ("Enter a number"). Key names are universal (keyboards say Enter); there is no standard Sanskrit key name, and renaming it would confuse, not clarify. STAYS.
- **fd** — a placeholder variable name in a compiler hint ("dvaram_likha(fd, smriti, sankhya) iti prayujyatam" — showing argument order: fd, memory, number). The API is dvaram_likha (Sanskrit); `fd` is the hint's placeholder, not a name a student calls. STAYS.
- **lib** — a DIRECTORY name in a hint ("naam.smlib lib/ madhye ... bhavet" — "should be in the lib/ directory"). It is a path, not an API name. STAYS.
- **root** — example-local variables named `root12` (the 12th-root value in madhava examples) and a compiler-internal label (`root__`, double underscore marking internals). Neither is a student-facing API name. STAYS.
- **space, tab** — character names in diagnostics (about mixing tabs and spaces in indentation, R77). They describe the characters, not API names; a student does not call `space` or `tab`. STAYS.

A vocabulary round that renamed any of these seven would be renaming locals, key names, placeholders, paths, internals, or characters — worse than missing a word, because it would churn code that is not the API while leaving the impression the API is clean.

## WS3 — the one-line rule, applied to the 33 (and a premise correction)

Correction first: I did NOT say the tree is inconsistent. R109 said the opposite — the tree is NOT inconsistent under the two-tier rule (functions use short forms, concepts use complete words; the only concept-keyword exception is yoj, grandfathered). What R108 asked and R109 answered is restated here so the premise does not drift again.

**The one-line rule: keywords and concepts take complete words; functions take the shortest recognizable form that unambiguously names the action (root, stem, or noun); existing roots are grandfathered, and meaning errors are fixed regardless of form.**

It is NOT "roots for verbs, nouns for values" — the tree's evidence does not support that split, because function names use both roots AND nouns (khip (root, throw) and gan (noun, count) are both function components; bhed (noun, difference) and yuj (root, join) are both function components). The checkable distinction is the tier (concept vs function), not verb vs noun.

Applied to the 33: the seven new proposals all follow the function tier (dvyank, bhed, puran, marga, upasarg, chihn, shrenit are each the shortest unambiguous form for what the body does — puran over pur because pur alone reads as "city"; shrenit as a participle because the predicate needs "sorted", not "sort"). The nineteen already-renamed follow the function tier too (kosh_kship, kosh_hri, kosh_gan, kosh_iksh, kosh_shodh, kosh_yuj, kosh_apanay, pankti_gan, jala, jala_bandh, jala_shru, jala_grah, akshar_laghu/guru, anka_akshar, vartani_sandhi, likha_santat, smaran_pratilip — roots, stems, nouns, and adjectives, all short forms), except the two R112 caveats (kosh_ksham is thin on meaning, likha_rup changed the meaning — both are form-correct but meaning-imperfect, which is why meaning (test 1) outranks form (test 3)). The seven stays do not reach the rule at all (they are not names). No concept/keyword is in the 33, so the concept tier (complete words) is not exercised here — but it is the tier that protects words like kshetra, mandapa, and parimita, and it is why a concept must never be shortened to a root.

NOT RUN: Windows, browser, implementation (none authorized — this is an audit, not renames), native-speaker review (the seven proposals are my Sanskrit readings and need confirmation before any rename decision, as with all new Sanskrit strings), full suite (no tree changes).

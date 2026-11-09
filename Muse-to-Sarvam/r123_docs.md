# Muse Round 123 — Documentation audit (v297)

Base: `<workspace>/r121-124/tree297` (v297). Audit only. No doc edits, no code
changes, no pushes, no merges were made. This is Muse Round 123 only; no other
agent's rounds were worked.

## Scope — read this first, because it decides most verdicts

- **In scope, checked file by file:** all 117 files under `docs/` (top level, plus
  `decisions/`, `reports/`, `rounds/`, `ai-handoff-notes/`, `vocabulary/`, and all
  `.html` files) and all 6 root `*.md` files (`AGENTS.md`, `INSTALL-WINDOWS.md`,
  `LANGUAGE-PRIORITY.md`, `PROJECT-MASTER.md`, `README.md`, `ROADMAP.md`).
  Method: full-text grep for every check string below, then context-read of every
  hit in a living doc (not just the grep line).
- **Out of scope as living docs, by design:** the collaboration folders
  (`Claude-to-Sarvam/`, `ChatGPT-to-Sarvam/`, `Muse-to-Sarvam/`, `Sarvam-to-*/`,
  `Windows-to-Sarvam/`). They are historical records and were not audited as
  references. They are not listed as findings even when they contain old names.
- **Inside `docs/`, two different kinds of file, judged differently:**
  (a) *Living docs* — `LANGUAGE-REFERENCE.md`, `SPECIFICATION.md`,
  `ERROR-CONVENTION.md`, `NUMERIC-CONTRACT.md`, `LIBRARY-BOUNDARY.md`,
  `OVERFLOW-SAFETY.md`, `MEMORY-MODEL.md` (see its own header, below),
  `OPEN-ISSUES.md`, `WHATS-LEFT.md`, `SANDESH.md`, `BUILDING.md`,
  `WINDOWS-SETUP.md`, `WINDOWS-PORT-PLAN.md`, `sutram-stdlib.html`,
  `sutram-stdlib-reference.html`, `sutram-vocabulary.html`, the
  `sutram-book*.html` tutorials, `_newchapter_en.html`, and
  `vocabulary/VOCABULARY-*.md`. A stale token or name here IS a finding.
  (b) *Historical records inside `docs/`* — `CHANGELOG.md` (except where it
  states a current total, see F26), `docs/decisions/*`, `docs/reports/*`,
  `docs/rounds/*`, `docs/ai-handoff-notes/*`, `docs/rounds/CHANGELOG-ARCHIVE.md`.
  These correctly quote old tokens/names *as they were then* (often with a
  version pin, e.g. "verified on compiler v253"). Quoting history there does
  NOT count under checks (1), (2) or (5). Rewriting them would destroy evidence.
  They are listed in §7 only to show they were checked and cleared, not as
  findings.
- **Relation to Round 119:** R119 already found `MEMORY-MODEL.md` (whole file),
  `LANGUAGE-REFERENCE.md` §16 (`:958,961`) and escape prose (`:1162,1195,1227`),
  `VOCABULARY-TABLE.md:108`, `OPEN-ISSUES.md:86`, and `_newchapter_en.html`.
  Those are NOT re-listed as new discoveries below; they are carried forward
  as "R119, confirmed still present on v297" where re-verified, and this report
  adds every file R119 did not cover plus the five new checks (asti/nasti,
  306-vs-310, WS2, WS3). New findings are marked NEW.

## Headline

- **Check (1) "Sutram Error" as current text: NO living doc does this.** Every
  "Sutram Error" hit in a living doc is an explicit historical quote
  ("up to v293 it was…", "a program built by v293 or earlier still prints…").
  The current token `Sutram truti` is used consistently in the reference
  (e.g. `LANGUAGE-REFERENCE.md:222-233`, `:933`, `:1232`, `:1333`).
  The one deliberate exception is also documented: the linker
  (`docs/decisions/R114-SUTRAM-TRUTI.md:30`) still prints `Sutram Error`.
- **Check (2) old names as PRIMARY: YES, in four living places** (plus the
  R119 §16/escape-prose cases): `LANGUAGE-REFERENCE.md` §4a `likha_fmt`
  section (`:343-353`, NEW), the same file's hint text (`:456`, `:980`,
  `:1232`, `:1240`, `:1270`, NEW in detail), the `sutram-book-*.html`
  tutorials (NEW — same kosh chapter in six language editions), and
  `sutram-stdlib-reference.html` (NEW — it lists 11 pre-v297 names as current
  and omits their v297 replacements). `MEMORY-MODEL.md` and
  `SPECIFICATION.md` use old names, but for a different reason (see F09/F10:
  labelled snapshot / inspected-emission name, not a student-facing primary).
- **Check (3) asti/nasti: present in exactly two student-facing places.**
  `LANGUAGE-REFERENCE.md:219` and `sutram-vocabulary.html:122-123` state
  `asti` == `==`, `nasti` == `!=`. Every other operator/vocabulary doc that a
  student would consult omits the tokens (see F14–F17).
- **Check (4) memory section: `parimita` AND `parimana` are both in
  `LANGUAGE-REFERENCE.md` §19, and both are stated Linux-only** (quotes in §4).
  `MEMORY-MODEL.md` mentions neither (0 hits for either word) — but it is a
  labelled R70 snapshot, not the §19 reference, so that is a link hazard
  (F20), not a §19 omission.
- **Check (5) sankhya_bindu as available: NO clean case in a living doc.**
  The reference and the vocabulary page both say "withdrawn (v295)".
  The only live-looking presentations are ambiguous/proposal tables
  (F21–F23): `sutram-vocabulary.html:120` (bold new-name column beside a
  "withdrawn" gloss) and the `vocabulary/` proposal tables (which propose
  pre-v292-final names and never mention the withdrawal).
- **Check (6) 306 vs 310: the premise needs correcting.** No v297 reference
  lists 306 functions. The 306 figure survives only as two stale *sentences*
  (F26). The HTML reference that claims a total claims **303**, not 306
  (F25), and the generated HTML reference is exactly right at **310** (F24).
  Actual library, verified: `grep -c "^prakriya " lib/*.smlib` sums to **310**
  (per-module: aadhar 2, ank 10, anukram 5, brihat 13, chandas 6, ganit 18,
  ganita 27, gudh 2, kalana 6, khand 22, madhava 5, mala 8, nighantu 17,
  patra 3, phal 14, roop 23, sadhan 7, samanvaya 11, sangrah 14, sankhyiki 16,
  shreni 14, suchi 34, vakyank 6, varna 27 = 310; 24 modules).
- **WS2: NO single doc tells a Windows student both halves together**
  (parimana() = 0 AND parimita never refuses) in one Windows-facing paragraph.
  The two halves exist, 44 lines apart, in §19 (F27). The single most
  important missing paragraph is drafted in §5.
- **WS3 (§16/§19, five gaps): 1 stated, 1 partially stated, 3 omitted**
  (table in §6). The stated one is the block-kosh storage lifetime; the
  omitted ones are the unmerged arena, mid-block reuse, and threads.

---

## 1. Check (1) — "Sutram Error" where the compiler now says "Sutram truti"

Verdict: **no finding in a living doc.** All hits below were context-read.

| File:line | What it says | Verdict / what it should say |
|---|---|---|
| `docs/LANGUAGE-REFERENCE.md:225,233` | "Up to v293 it was `Sutram Error`… A program built by v293 or earlier still prints `Sutram Error` from its own bytes; rebuild it." | CLEARED — explicit history, and the surrounding paragraph (`:222`) states the current token is `Sutram truti`. No change. |
| `docs/SANDESH.md:6` | "(The token was `Sutram Error` up to v293; it changed in every pack at once…)" | CLEARED — explicit history. No change. |
| `docs/CHANGELOG.md:54,62,65,78,90,190` | v294 change notice; `:190` quotes the v285 `Sutram Error [E_PARIMITA]` message inside the v285 section. | CLEARED — changelog history. v285 predates the v294 change, so the quote is historically correct. The current message is correctly given at `LANGUAGE-REFERENCE.md:1333` (`Sutram truti [E_PARIMITA]`). No change. |
| `docs/WHATS-LEFT.md:52,68` | Struck-through items ("Done in v294… as `Sutram truti`"). | CLEARED — struck history. No change. |
| `docs/decisions/R114-SUTRAM-TRUTI.md:1,4,12,16,30,40,42` | The decision that made the change; `:30` notes the linker exception. | CLEARED — decision record. The linker exception ("`sutram-link`, `sutram-elf2smo` and `sutram-coff2smo` print their own `Sutram Error`") is a *current* compiler fact, not a doc error; it should stay stated, and any student doc that mentions the linker should repeat it. No change to this file. |
| `docs/decisions/MEMORY-DECISION.md:68` | Quotes `Sutram Error [E_SCRATCH_ESCAPE]` as "the error message itself" in a decision record. | CLEARED as history (pre-v294 decision), but NOTE: a reader following this decision today will copy an old token. Should say: add a one-line footnote — "Token now `Sutram truti`; the rule is unchanged." This is a footnote, not a rewrite. |
| `docs/reports/KOSH-BUILTINS.md:107-109,134,145`, `KOSH-REUSE.md:42`, `LAGHU-EXAMPLE.md:63`, `NEGATIVE-CORPUS.md:23-28`, `docs/rounds/*` (incl. `CHANGELOG-ARCHIVE.md`, dozens of hits), `docs/sutram-audit.html:110,118,131` | Old-token quotes pinned to old versions (e.g. "verified on compiler v253", "R68 prelex path", audit output). | CLEARED — dated reports / archive / audit output. No change. |
| Root `LANGUAGE-PRIORITY.md:37` | "One written exception (owner, 3 November 2026): the fixed token `Sutram Error` → `Sutram truti`…" | CLEARED — the exception notice itself. No change. |
| All other living docs (`SPECIFICATION.md`, `ERROR-CONVENTION.md`, `NUMERIC-CONTRACT.md`, `LIBRARY-BOUNDARY.md`, `OVERFLOW-SAFETY.md`, `sutram-stdlib*.html`, `sutram-book*.html`, `vocabulary/*`, root `README.md`, `PROJECT-MASTER.md`, `ROADMAP.md`, `AGENTS.md`, `INSTALL-WINDOWS.md`) | No "Sutram Error" hit at all (grep-verified). | CLEARED — nothing to fix. |

## 2. Check (2) — old names listed as the PRIMARY name, not an alias

Correct-alias presentations (cleared, for contrast): `LANGUAGE-REFERENCE.md:162`
(`pankti_gan` (was `pankti_len`)), `:167,176,179,183-185`, `:207-217` (full
new/old alias table), `:919-927` (§16 table, every row "(was …)"),
`sutram-vocabulary.html:98-121` (old column + bold new column + "primary from
v292" preamble). An old name in one of those tables is NOT a finding.

### Findings (old name presented as the name to write)

- **F01 — NEW — `docs/LANGUAGE-REFERENCE.md:343-353` (§4a).** What it says:
  a whole subsection headed "`likha_fmt(fmt, v)` — literal prefix + integer,
  not placeholder substitution", with code `likha_fmt("x = ", 42)` and prose
  "`likha_fmt` currently outputs…". What it should say: `likha_rup` throughout
  (the §4 table at `:167` already says `likha_rup` (was `likha_fmt`)). This is
  an un-updated §4a block: a student copying §4a writes the alias, gets a
  deprecation warning, and learns the wrong primary. Fix: rename the heading,
  the example, and the prose to `likha_rup`, keeping one "(was `likha_fmt`)" note.
- **F02 — NEW (detail) — `docs/LANGUAGE-REFERENCE.md:456`.** What it says: the
  `E_KOSH_GANIT` row advises "compare `k[i]` or `kosh_len(k)`". What it should
  say: `kosh_gan(k)`. (Contrast `:263`, which correctly notes the hints were
  updated from `kosh_len(k)` to `kosh_gan(k)` — this row was missed.)
- **F03 — NEW (detail) — `docs/LANGUAGE-REFERENCE.md:980,1232,1240,1270`.**
  What they say: Windows-alias advice "copy values out (`k[i]`, `kosh_len(k)`)"
  (`:980`); the `E_KOSH_MANDAPA` hint text quoted at `:1232`
  ("`k[i]`, `kosh_len(k)`"); the "does not keep it" rule at `:1240`
  ("`k[i]`, `kosh_len(k)`, passing it on…"); the cost note at `:1270`
  ("+3.5% on `kosh_push`"). What they should say: `kosh_gan(k)` in the first
  three, `kosh_kship` in the cost note. Note: `:1232` quotes a compiler hint
  verbatim — if the compiler hint itself still says `kosh_len(k)`, the fix
  belongs in the compiler hint first and the doc second; the doc must not be
  "fixed" to disagree with what the compiler prints. Verify the hint text
  before editing.
- **F04 — R119, confirmed — `docs/LANGUAGE-REFERENCE.md:958,961`.** What they
  say: the §16 aliasing example uses `kosh_push(k, 41)` / `kosh_push(k, 42)` as
  current code. What it should say: `kosh_kship` (example 288 itself uses
  `kosh_kship` on v297). Same file `:1162,1195,1227` (escape-rule prose:
  `kosh_push(k, buf)`, `kosh_push(outer, k)`) — same fix, "was" note optional
  since `:919` already gives the alias.
- **F05 — NEW — `docs/sutram-book-english.html:431,680-682,684,693-694,702,706,710`
  and the identical kosh chapter in `sutram-book-gujarati.html`,
  `sutram-book-hindi.html`, `sutram-book-sanskrit.html`,
  `sutram-book-tamil.html`, `sutram-book-telugu.html` (same lines, same
  counts: 5× `kosh_push`, 3× `kosh_len`, 1× `kosh_pop`, 1× `pankti_len` per
  edition).** What they say: the tutorial's kosh chapter teaches
  `kosh_push` / `kosh_len` / `kosh_pop` / `pankti_len` with no alias note
  anywhere in the chapter, and the prose at `:710` ("calling `kosh_push` on a
  parameter is refused…") names the alias as the API. What they should say:
  `kosh_kship` / `kosh_gan` / `kosh_hri` / `pankti_gan`, with one alias note.
  The six editions share one source chapter, so this is one fix applied six
  times, not six independent errors. (`sutram-book.html`, `sutram-book-2.html`,
  `sutram-book-3.html` are edition indexes only — 0 old-name hits, cleared.
  `_newchapter_en.html:21-23,25,34-35,43,47,51` is the same chapter again —
  R119, confirmed.)
- **F06 — NEW — `docs/sutram-stdlib-reference.html` (whole file, see §3 for
  the count).** What it says: it lists 11 pre-v297 names as current
  signatures — `asti_sorted`, `bit_gan`, `meru_pankti`, `pad_vam`,
  `rakh_samroop_diff`, `roop_ank_pre`, `roop_pad_dakshin`, `roop_pad_madhya`,
  `roop_pad_vam`, `roop_sign_akshar`, `suchi_asti_sorted` — and omits their
  v297 replacements (see F25). What it should say: the v297 names
  (`asti_kramabaddha`, `ekanka_gan`, `meru_mala`, `purti_vam`,
  `rakh_ubhaya_bhed`, `roop_ank_upasarga`, `roop_purti_dakshin/madhya/vam`,
  `roop_chihna_akshar`, `suchi_asti_kramabaddha`). This is the largest
  check-(2) finding: a student using this reference will write names that
  only work as aliases (or, for the v297 renames, that the reference does
  not document at all).
- **F07 — `docs/OPEN-ISSUES.md:86-87,92,169`.** What it says: section C lists
  `kosh_push`, `kosh_pop`, `kosh_cap`, `kosh_clear`, `kosh_empty`,
  `kosh_peek`, `kosh_dequeue`, `kosh_enqueue`, `kosh_len` and `pankti_len` as
  an OPEN issue ("English still in the language"). What it should say: the
  issue is resolved (v292: Sanskrit primary, English alias) — the section
  needs a "resolved in v292" status, not deletion (the history of the issue
  is worth keeping). R119, confirmed.
- **F08 — `docs/WHATS-LEFT.md:56-57`.** What it says: items C5/C6 about
  `pankti_len` / `kosh_pop` transliteration, listed without v292 status.
  What it should say: same treatment as F07 (mark resolved/superseded; the
  underlying transliteration notes may still be open, but the "English name
  is primary" framing is not).
- **F09 — `docs/MEMORY-MODEL.md:53,61,178,185` — NOT a primary-name error,
  classified separately.** What it says: "the inspected `kosh_push` growth
  path", "`kosh_clear` is not free", the API list
  "`kosh_push/pop/len/cap/clear/empty/peek/enqueue/dequeue`". Why it is not
  F01–F06: the file's own header (`:9`) labels it "HISTORICAL RESEARCH AND
  UNIMPLEMENTED DESIGN (R70 snapshot)", pinned to an older compiler revision
  (snapshot `dde0613…`). It describes the inspected path *as it was then*,
  not the name a student should write today. What it should say: nothing
  inside the snapshot — but see F20: the *link* to it from the living
  reference is the hazard, not the snapshot's own wording.
- **F10 — `docs/SPECIFICATION.md:208`.** What it says: "The inspected
  `kosh_clear` emission sets length to zero…". Why it is not a finding: this
  names an inspected compiler emission (`.ge_call_koshclear`-era), not the
  student-facing API, and the surrounding paragraph is about emission
  behaviour, not "write this name". No change. (Same reasoning for
  `LANGUAGE-REFERENCE.md:933,939-940`: those quote the compiler's *runtime
  messages* verbatim (`Sutram truti: riktat koshat kosh_peek`,
  "`rikta kosh se kosh_pop`…"), which is accurate — the messages really do
  still name the old spelling (R111-00, correctly flagged at `:263-266`).
  Quoting a message is not presenting a primary; the underlying compiler
  messages are a separate, already-known issue.)
- **Cleared on check (2):** `ERROR-CONVENTION.md`, `NUMERIC-CONTRACT.md`,
  `LIBRARY-BOUNDARY.md`, `OVERFLOW-SAFETY.md`, `BUILDING.md`, `SANDESH.md`,
  `WINDOWS-SETUP.md`, `WINDOWS-PORT-PLAN.md`, `sutram-stdlib.html`
  (0 old-name hits as primaries; its signatures are the v297 names),
  `sutram-keyword-words.html`, `sutram-ide.html`, `sutram-audit.html`
  (audit output, historical), root `README.md`, `PROJECT-MASTER.md`,
  `ROADMAP.md`, `AGENTS.md`, `INSTALL-WINDOWS.md` (0 hits).

## 3. Check (6) — the library reference: 306, 303, or 310?

(This check is placed before (3)–(5) in the findings because F06/F24–F26
depend on it. The task's "list 306" premise is corrected here.)

- **F24 — CORRECT — `docs/sutram-stdlib.html:479`.** Footer: "24 modules,
  310 functions. Generated from library sources." Verified: its signature
  set is exactly the 310 `prakriya` names in `lib/*.smlib` (0 missing,
  0 extra, by set diff). This is the reference to point students at.
  What it should say: nothing — it is right. (Note: it is generated, so its
  correctness is only as fresh as its last generation run; no generation
  date is stated in the file — a "generated at v297" stamp would prevent
  this check from going stale silently.)
- **F25 — STALE — `docs/sutram-stdlib-reference.html:61,66,767`.** Header:
  "24 modules · 303 functions · every signature taken from the source";
  stat card "303 functions"; closing "303 functions across 24 modules".
  Verified by set diff against `lib/*.smlib` (310):
  *Missing (18, all v296/v297 work):* `asti_kramabaddha`,
  `bk_gunan`, `bk_kaarak`, `bk_khand`, `bk_na_adhik` (v296 brahmagupta
  helpers), `brihat_shesh_sahaya`, `ekanka_gan`, `kuttaka_gun_shesh`,
  `meru_mala`, `purti_vam`, `rakh_ubhaya_bhed`, `roop_ank_upasarga`,
  `roop_chihna_akshar`, `roop_purti_dakshin`, `roop_purti_madhya`,
  `roop_purti_vam`, `samanvaya_akar_ayogya`, `suchi_asti_kramabaddha`.
  *Listed but not in lib (11, all pre-v297 names):* `asti_sorted`,
  `bit_gan`, `meru_pankti`, `pad_vam`, `rakh_samroop_diff`, `roop_ank_pre`,
  `roop_pad_dakshin`, `roop_pad_madhya`, `roop_pad_vam`,
  `roop_sign_akshar`, `suchi_asti_sorted`.
  310 − 18 + 11 = 303, which reconciles the header exactly — this file is a
  pre-v297 snapshot, not a miscount. Per-module: ganita is listed as 22
  (lib: 27, missing exactly the 4 `bk_*` + `kuttaka_gun_shesh`), brihat as
  12 (lib: 13, missing `brihat_shesh_sahaya`), samanvaya as 10 (lib: 11,
  missing `samanvaya_akar_ayogya`); all other module counts match lib, but
  roop/shreni/suchi swap old for new names at the same counts. What it
  should say: regenerate from v297 sources (or retire it in favour of
  `sutram-stdlib.html`, which is already exact) — do not hand-patch 29
  signatures.
- **F26 — STALE SENTENCES (the only surviving "306" in v297).**
  `docs/LANGUAGE-REFERENCE.md:1396`: "The library: **63 of its 306 functions**
  could be marked as they are…"; `docs/CHANGELOG.md:368`: "`parikshita`: 0
  of 306 library functions marked, 63 eligible." What they should say: 310
  (and the eligible count re-verified — 63 was measured against 306; whether
  the 4 new `bk_*` helpers are eligible is not stated and should not be
  assumed). Note the two sentences disagree with each other in a second
  way (0 marked vs 63 could-be-marked) because they describe different
  moments; only the total (306 → 310) is the finding here.
- **F27 — MISLEADING SUBSET — `docs/LANGUAGE-REFERENCE.md:363-367` (§4b
  library table).** What it says: a table of 6 modules totalling "60
  functions across six modules" (ganit 15, ank 10, shreni 11, ganita 6,
  madhava 5, varna 13), followed by "Limitation: a program can currently
  include at most two modules — the inliner's buffer overflows at three or
  more". What it should say: (a) the 6-module counts are themselves short
  against lib even for those modules — ganit 15 vs 18 (missing
  `ekanka_gan`, `ganit_yadricch`, `ganit_seemit`), ganita 6 vs 27 (missing
  all `ganita_janchit_*` / `ganita_paripurna_*` variants, `bk_*`,
  `kuttaka_gun_shesh`), varna 13 vs 27 (missing all 14 `varna_*`-prefixed
  functions: `varna_aadi`, `varna_ant`, `varna_antah`, `varna_anwesh`,
  `varna_avanat`, `varna_bhed`, `varna_chhid`, `varna_gan`,
  `varna_pratisthap`, `varna_sam`, `varna_tul`, `varna_unnat`,
  `varna_viparyay`, `varna_yuj`),
  shreni 11 vs 14 (missing `nivesh_shreni`, `mil_shreni_punar`,
  `mil_shreni`) — i.e. 60 listed vs 101 actual for just those six modules;
  (b) the other 18 modules (209 functions) are absent from §4b entirely, so
  §4b must not be read as "the library" (it is a six-module excerpt with no
  excerpt label); (c) the "at most two modules" limitation is stale — the
  current limit is far higher (a program importing ~10 modules is where the
  procedure-list cap bites, per prior rounds; the two-module claim is a
  pre-v297 bug description). Fix: label §4b as an excerpt pointing at
  `sutram-stdlib.html` for the full 310, or expand it; and delete or
  re-measure the two-module sentence.
- **F28 — VERSION-PINNED, NOT CURRENT — `docs/vocabulary/VOCABULARY-COMPLETE.md:3`.**
  What it says: "Extracted from `lib/*.smlib` on main at compiler v253.
  24 modules, 305 functions." What it should say: nothing inside the file —
  it is correctly pinned to v253 (305 was right then). But it must not be
  cited as the current count: any doc or index pointing at it as "the
  vocabulary" needs a "v253 snapshot; current count is 310 (see
  `sutram-stdlib.html`)" pointer. Same treatment for
  `VOCABULARY-DERIVATION.md` ("of 305 declarations…", v253-era measurement).

## 4. Check (3) — asti / nasti: who mentions the tokens, who should but doesn't

The tokens are `asti` (==) and `nasti` (!=), the same token as `==`/`!=`
(v292). `patra_asti` (a library function, "file exists") and `asti_*`
predicates (`asti_abhajya`, `asti_kramabaddha`, …) are NOT the tokens and
were excluded from the counts below (standalone-word grep, backticked
`` `asti` `` / `` `nasti` `` counted separately).

**Do mention the tokens (cleared):**

| File | Lines | What it says |
|---|---|---|
| `docs/LANGUAGE-REFERENCE.md` | `:219` (plus `:458` using `p asti q` in the rachana-operand rule) | "`asti` / अस्ति is `==` and `nasti` / नास्ति is `!=` — the same token: `yadi (a asti b)` is `yadi (a == b)`, byte for byte (`examples/324`-`327`)." This is the canonical statement. |
| `docs/sutram-vocabulary.html` | `:122-123` | Table rows: equal `==` → **`asti`** (अस्ति, "is"); not equal `!=` → **`nasti`** (नास्ति, "is not"). |
| `docs/CHANGELOG.md` | `:80,87` | v292 notice: "`asti` / `nasti` are `==` / `!=`" (history, correctly stated). |
| `docs/vocabulary/VOCABULARY-TABLE.md:175`, `VOCABULARY-SHORT.md:97` | Stem tables: "`asti` — is (boolean marker) — KEEP". | PARTIAL: these predate the v292 token decision in wording — they describe `asti` as a stem/boolean marker (the `asti_*` predicate convention), not as the `==` token. A student reading only these will not learn that `a asti b` compiles. Should say: add "(also the `==` token since v292)" to the stem row. |

**Should mention the tokens but don't (findings):**

- **F14 — `docs/SPECIFICATION.md`.** What it says: `:96` lists "`== !=`, then `< > >=`" as pinned comparisons, with no mention that `asti`/`nasti` are the same tokens. What it should say: add "`asti`/`nasti` are the same tokens as `==`/`!=`" to the comparison row — this is the normative spec, and it is the doc a student checks when `a asti b` fails to parse in their head.
- **F15 — `docs/sutram-book-english.html` (and the other five language
  editions, same operator table).** What it says: `:132` operator table
  "`== != < > >=` — comparison", and `:188,410` use `==` in code, never
  `asti`/`nasti`. What it should say: the operator table should list
  `asti`/`nasti` beside `==`/`!=` (one row, not a rewrite of the tutorial).
  A tutorial that teaches only `==` teaches the alias, not the primary
  Sanskrit spelling — the same class of error as F05, in the operator table.
- **F16 — `docs/vocabulary/VOCABULARY-RULE.md`, `VOCABULARY-DERIVATION.md`,
  `VOCABULARY-COMPLETE.md`.** What they say: the rule page (owner-agreed test
  for future names) and the derivation page (DRAFT, rewritten to ChatGPT R115)
  never mention `asti`/`nasti` as tokens; COMPLETE is a v253 extraction
  (pre-token). What they should say: RULE and DERIVATION should cite `asti`
  as the exemplar of a good token (short, complete, already perfect — the
  stem tables themselves say so) now that it is also the equality token;
  COMPLETE needs only the v253 pin already on it (see F28), not new content.
- **F17 — `docs/sutram-stdlib-reference.html`, `docs/sutram-stdlib.html`.**
  What they say: neither mentions the tokens. Verdict: NOT a finding on
  their own terms — they are library references (function signatures), not
  operator references, and the tokens are not library functions. Listed here
  so the omission is a deliberate "should not" rather than an oversight.
  The same "should not" applies to `ERROR-CONVENTION.md`,
  `NUMERIC-CONTRACT.md`, `LIBRARY-BOUNDARY.md`, `MEMORY-MODEL.md`,
  `OPEN-ISSUES.md`, `WHATS-LEFT.md`, `SANDESH.md`, `BUILDING.md`, root
  `README.md` / `PROJECT-MASTER.md` (overviews, not operator lists) — all
  grep-verified 0 standalone hits, all cleared as out-of-scope for this
  check. (Note: `sutram-stdlib-reference.html` does list `patra_asti` at
  `:743,748` — that is the library function, not the token, and is correct.)

## 5. Check (4) — memory section: parimita AND parimana, and Linux-only

`LANGUAGE-REFERENCE.md` §19 states both, each with its Linux-only line:

- **parimana — `:1287-1313`.** "``parimana()`` (*measure*) returns the
  bytes the program's allocations hold right now… What it counts: the
  arena's persistent side…, its scratch side…, and each `kosh`'s header and
  capacity… **Linux ELF only; in a Windows program it returns 0.**" (`:1308`).
  Example values quoted (`:1292-1296`: 0, 64, 1072, 64, 8272) match
  `examples/317` on Linux.
- **parimita — `:1315-1359`.** "``parimita`` (*measured, limited*) gives a
  block a byte budget… **Linux ELF only, as the block.** In a Windows
  program a `mandapa` releases nothing, and its budget is not checked."
  (`:1352-1353`). The general mandapa Linux-only line is also at `:1184`
  ("**Linux only.** In a Windows (PE) program… a `mandapa` is an ordinary
  block: everything works, nothing is reclaimed.").
- **F20 — `docs/MEMORY-MODEL.md`: mentions NEITHER word (0 hits for
  `parimita`, 0 for `parimana`, in a 215-line file).** What it should say:
  nothing inside the snapshot (see F09 — it is labelled R70) — but
  `LANGUAGE-REFERENCE.md:10` links to it ("See `docs/MEMORY-MODEL.md`") for
  "the memory question". A student following that link from §19 gets a
  pre-region, pre-budget, pre-reporting model with no pointer back to §19.
  Fix (in the reference, not the snapshot): annotate the `:10` link —
  "historical snapshot; current model is §19" — or add a header pointer
  inside `MEMORY-MODEL.md` itself ("For parimita/parimana and regions, see
  `LANGUAGE-REFERENCE.md` §16/§19").
- **Root `README.md:188,192`** also states both, correctly scoped:
  "`parimana()` returns the bytes… (v289, Linux)" and the parimita budget
  "(Linux, v285; §19, 'A budget')". Cleared.

## 6. Check (5) — sankhya_bindu described as available

- **Cleared (correctly withdrawn):** `LANGUAGE-REFERENCE.md:188`
  ("**withdrawn (v295, R115):** refused when compiled - `E_PRATYAHRITA`…
  For two `kosh dasham`: `yoj sankhyiki`, then `bindu_gunan(a, b)`") and
  `:217` (both names struck through, "both withdrawn, v295");
  `sutram-vocabulary.html:120` gloss ("withdrawn in v295… refused,
  `E_PRATYAHRITA`") — but see F21 for the table-column problem in the same
  row; `CHANGELOG.md:43-45` (v295 withdrawal notice).
- **F21 — AMBIGUOUS — `docs/sutram-vocabulary.html:120`.** What it says: the
  row's first column is "dot product - **withdrawn in v295**", but the
  second/third columns still read `` `sankhya_dot` `` → **bold**
  `` `sankhya_bindu` `` (बिन्दु, "point") — i.e. the table's new-name column
  presents `sankhya_bindu` as the current name while the gloss says
  withdrawn. What it should say: strike through the new-name cell (as
  `LANGUAGE-REFERENCE.md:217` does) or replace it with "`bindu_gunan`
  (via `sankhyiki`)" so a student scanning the name columns does not copy
  a refused name.
- **F22 — PROPOSAL, NOT CURRENT — `docs/vocabulary/VOCABULARY-TABLE.md:108`.**
  What it says: "`sankhya_dot` | dot product | 11 | **CHANGE:
  `sankhya_bindu`** - `bindu` is 'point'" with no withdrawal note anywhere
  in the file (0 hits for "withdrawn"). What it should say: the table is a
  pre-v292-final proposal (see also its `kosh_aayam` for `kosh_len` at
  `:112` vs actual `kosh_gan`, and `likha_roop` for `likha_fmt` at `:109` vs
  actual `likha_rup`) — it needs a "superseded by v292/v295" banner, not
  silent edits. R119, confirmed.
- **F23 — PROPOSAL, NOT CURRENT — `docs/vocabulary/VOCABULARY-SHORT.md:145`.**
  What it says: "`sankhya_dot` | `sankh_bindu` | dot product" (a
  *different* proposed name, `sankh_bindu`, from the SHORT rule's
  stem-shortening, which the project did not adopt). Same banner fix as
  F22. The SHORT table's other proposals are likewise unadopted
  (`kosh_nay` for `kosh_pop` at `:148` vs actual `kosh_hri`,
  `kosh_agran_nay`/`kosh_agran_yuj` at `:154-155` vs actual
  `kosh_apanay`/`kosh_yuj`) — the whole SHORT table is a proposal, not the
  current vocabulary, and should be labelled as such wherever it is linked.
- **Cleared:** `sutram-stdlib-reference.html` and `sutram-stdlib.html`
  omit both `sankhya_dot` and `sankhya_bindu` entirely — correct for a
  withdrawn builtin (omission is the right presentation; listing it as
  available would be the error).

## 7. WS2 — does ANY doc tell a Windows student both halves together?

**Short answer: NO — not in one Windows-facing paragraph.**

What exists, scattered:

| Half | Where it is stated | Line |
|---|---|---|
| parimana() returns 0 on Windows | `LANGUAGE-REFERENCE.md` §19 | `:1308`: "Linux ELF only; in a Windows program it returns 0." |
| parimita budget not checked on Windows | `LANGUAGE-REFERENCE.md` §19 | `:1352-1353`: "Linux ELF only, as the block. In a Windows program a `mandapa` releases nothing, and its budget is not checked." |
| mandapa generally Linux-only | `LANGUAGE-REFERENCE.md` §19 | `:1184`: "Linux only. In a Windows (PE) program… a `mandapa` is an ordinary block: everything works, nothing is reclaimed." |
| Same, in overview form | Root `README.md` | `:182-186`: "Memory is released only on Linux. In a Windows program a `mandapa` block works, but releases nothing." + `:188` (parimana, "(v289, Linux)") + `:192` (parimita, "(Linux, v285…)"). The README states release + both features' Linux scope, but never the two Windows *values* (0, never-refuses) in one sentence. |
| Windows feature status | `docs/WINDOWS-SETUP.md` §6–§7 (`:120-149`) | Linux-vs-Windows table (binary format, pack search, install) + "Not yet ported: the network builtins" + REPL awaiting a check. **No mention of parimana or parimita at all** (0 hits in the file). This is the doc a Windows student actually opens first, and it is silent on both. |
| Windows port plan | `docs/WINDOWS-PORT-PLAN.md` | 0 hits for parimana/parimita. Silent. |

**The single most important missing paragraph** (proposed text for
`docs/WINDOWS-SETUP.md` §7, or for §19 as a Windows box — audit proposal
only, not an edit):

> If you are on Windows, two §19 features silently do nothing, and your
> program will still compile and run: `parimana()` always returns 0 (it does
> not report your program's bytes), and a `mandapa parimita N` budget is
> never enforced (a block that would stop with `E_PARIMITA` on Linux runs
> to the end on Windows). A `kosh` made in a `mandapa` also keeps its storage
> for the program's life on both systems, but on Windows a growing `kosh`
> still moves, so a second name for it goes stale (§16). Do not rely on
> `parimana()` or `parimita` to catch a Windows memory problem — they will
> not fire. See `LANGUAGE-REFERENCE.md` §19.

Why this paragraph, and not the others: a Windows student who reads only
§19's two scattered lines must connect `:1308` to `:1352` themselves, across
44 lines and two subsections, while the doc they open first
(`WINDOWS-SETUP.md`) says nothing. The failure mode is silent (0, runs to
the end), so the student gets no error telling them the feature is absent —
the paragraph is the only thing that would warn them before they trust a 0
or a non-refusal.

## 8. WS3 — the five memory gaps: does §16/§19 state them?

Scope for this section is exactly `docs/LANGUAGE-REFERENCE.md` §16
(`:912-988`) and §19 (`:1119-1362`). Statements elsewhere (notably
`MEMORY-MODEL.md`) are noted only to show where the information lives
instead; they do not count as "the reference states it".

| # | Gap | §16/§19 verdict | Line / evidence |
|---|---|---|---|
| (i) | A block kosh outlives its block | **STATED — but split across two different lifetimes, which is itself a readability gap** | Storage lifetime, STATED twice: `:1272-1273` ("Decided (R103, v285): the block does not take a `kosh`'s memory back; the `kosh` keeps it for the program's life.") and `:1312` ("a `kosh`'s bytes do not [fall], even one made in the block — its storage is kept for the program's life"). Reference lifetime, STATED as a refusal: `:1223` ("A `kosh` declared inside a `mandapa` lives as long as the block") + `:1225-1260` (v289+ `E_KOSH_MANDAPA` refusal for any reference that would leave). What is NOT stated in one sentence: "storage outlives, reference must not" — a student reading `:1223` alone will think the kosh dies with the block, and a student reading `:1272` alone will think it survives. Should say: one reconciling sentence at `:1223` ("its storage survives — see `:1272` — but no reference to it may"). |
| (ii) | The arena is built but unmerged | **OMITTED from §16/§19** | 0 hits in §16/§19 for `claude/r108-arena-review`, "arena branch", or "unmerged". The arena as a *mechanism* is mentioned only as the counter source for `parimana()` (`:1300,1310`: "the arena's persistent side… its scratch side… `parimana()` is the arena and the `kosh` regions together"). The branch's existence and status appear only in `CHANGELOG.md:43,50,117` ("The arena branch (`claude/r108-arena-review`, not merged): its silent wrong answer… found and fixed there"). A §19 reader has no way to know there is a built, fixed, unmerged arena design, or that §19's "no reuse inside a live block" (gap (iii)) is exactly what the arena was designed to change. Should say: one status line in §19 ("An arena design exists on `claude/r108-arena-review`, fixed at the branch tip, not merged; §19 describes main, not the branch."). |
| (iii) | No reuse inside a live block | **IMPLIED, NOT STATED** | §19 states reuse *across* blocks, repeatedly: `:1172` ("A later block reuses the same memory, and sees zeros"), `:1180` ("Pages are reused, not returned: a block that touched 100 MB keeps those 100 MB resident; the next block uses them again"). It never states the complement: within a still-live block, dead scratch is NOT reused (allocation is a bump from the entry cursor until exit; there is no mid-block free). The bump itself is implied by "Entry remembers the scratch cursor. Each `nirmmita` inside takes memory from the scratch side" (`:1168-1169`) + "Every exit gives it all back" (`:1171`), but a student who assumes "freed scratch is reusable inside the block" will find no sentence contradicting them. Should say: one sentence in §19 Run time ("Inside a live block there is no reuse: memory taken is held until the block ends, even if the program stops using it."). |
| (iv) | 64 MiB per kosh is invisible | **PARTIALLY STATED** | Size STATED: §16 `:951-952` ("Every `kosh` is made in a region of its own — 64 MB of address space, of which only the pages it touches are used — and grows in place inside it") + cost paragraph (`:983-990`: "at least one 4 KB page per `kosh`… and one `mmap`…"). Invisibility NOT stated: §19 `parimana()` (`:1300-1306`) says it counts "each `kosh`'s header and capacity, 8 bytes a number" and "It is not the resident memory… a `kosh`'s capacity counts whether or not every page has been touched. It is what the program asked for" — but never says "the 64 MB reservation itself is not counted by `parimana()` and does not appear in RSS until touched". A student dividing `parimana()` by 64 MB, or expecting RSS to jump 64 MB per kosh, will be misled. Should say: one clause in the `parimana()` "What it counts" list ("The 64 MB region reservation is not counted and is not resident until touched."). |
| (v) | No threads | **OMITTED from §16/§19** | 0 hits in §16/§19 for thread / parallel / concurrent. The only concurrency statement in the docs tree is in `MEMORY-MODEL.md:89,102,162` ("There is no present concurrency memory model, happens-before rule, atomic contract or shared-mutation discipline… concurrent access are not covered by a memory-safety promise") — a labelled R70 snapshot, not the reference. A §19 reader gets no warning that two threads (or two `mandapa` blocks on different threads, if the student imagines them) share one arena/scratch cursor with no discipline. Should say: one line in §19 (or §16): "There is no thread model: `mandapa`, `nirmmita`, and `kosh` regions assume a single thread; concurrent use is unspecified." |

## 9. Summary table — check × file (living docs only; ● = finding, ○ = cleared, — = not applicable to that file)

| File | (1) Error-as-current | (2) Old-as-primary | (3) asti/nasti | (4) parimita+parimana+Linux-only | (5) bindu-as-available | (6) count |
|---|---|---|---|---|---|---|
| `LANGUAGE-REFERENCE.md` | ○ (hist. only) | ● F01,F02,F03,F04 | ● present (:219) | ● both + Linux-only (:1308,:1352) | ○ (withdrawn) | ● F26 (306 sentence), F27 (60/2-module) |
| `MEMORY-MODEL.md` | ○ (0 hits) | ◐ snapshot (F09) | — (not an operator doc) | ● neither word (F20, link hazard) | ○ (0 hits) | — |
| `SPECIFICATION.md` | ○ (uses truti) | ○ (F10 cleared) | ● missing (F14) | — | ○ | — |
| `ERROR-CONVENTION.md` | ○ | ○ | — | — | ○ | — |
| `NUMERIC-CONTRACT.md` | ○ (uses truti) | ○ | — | — | ○ | — |
| `LIBRARY-BOUNDARY.md` | ○ | ○ | — | — | ○ | — |
| `OPEN-ISSUES.md` | ○ (struck) | ● status stale (F07) | — | — | ○ | — |
| `WHATS-LEFT.md` | ○ (struck) | ● status stale (F08) | — | — | ○ | — |
| `SANDESH.md` | ○ (hist. only) | ○ | — | — | ○ | — |
| `CHANGELOG.md` | ○ (history) | ○ | ● present (history) | ○ (states Linux-only at :193) | ○ (withdrawal notice) | ● F26 (306 sentence) |
| `sutram-stdlib.html` | ○ | ○ | — (not an operator doc, F17) | — | ○ (omitted, correct) | ○ exact 310 (F24) |
| `sutram-stdlib-reference.html` | ○ | ● F06 (11 old names) | — (F17) | — | ○ (omitted, correct) | ● 303 claim, 18 missing / 11 extra (F25) |
| `sutram-vocabulary.html` | ○ (states change) | ○ (alias table correct) | ● present (:122-123) | — | ◐ ambiguous column (F21) | — |
| `sutram-book-english.html` + 5 other editions | ○ | ● F05 (kosh chapter) | ● missing (F15) | — | ○ | ● "Twelve/Fifteen modules" counts stale (see below) |
| `_newchapter_en.html` | ○ | ● R119 confirmed | — | — | ○ | — |
| `vocabulary/VOCABULARY-TABLE.md` | ○ | ◐ proposal (F22) | ◐ stem only (see §4) | — | ● proposal, no withdrawal (F22) | ◐ pre-v292 names |
| `vocabulary/VOCABULARY-SHORT.md` | ○ | ◐ proposal (F23) | ◐ stem only | — | ● proposal, unadopted name (F23) | ◐ unadopted proposals |
| `vocabulary/VOCABULARY-COMPLETE.md` | ○ | — (v253 pin) | — (v253 pin) | — | — (v253 pin) | ◐ 305 at v253 (F28, pinned) |
| `vocabulary/VOCABULARY-RULE.md` / `DERIVATION.md` | ○ | ○ | ● missing (F16, RULE/DERIVATION) | — | ○ | ◐ DERIVATION cites 305 (v253-era) |
| `WINDOWS-SETUP.md` | ○ | ○ | — | ● silent on both (WS2) | ○ | — |
| `WINDOWS-PORT-PLAN.md` | ○ | ○ | — | ● silent on both (WS2) | ○ | — |
| Root `README.md` | ○ | ○ | — | ○ both, Linux-scoped (:188,192) | ○ | — |
| Root `PROJECT-MASTER.md` / `ROADMAP.md` / `AGENTS.md` / `INSTALL-WINDOWS.md` / `LANGUAGE-PRIORITY.md` | ○ (PRIORITY states the change) | ○ (0 hits) | — | — | ○ | — |

Additional count note (NEW, from the book check): `sutram-book-english.html`
says "Twelve modules ship today" in one place and "Fifteen modules ship"
in another, while the library has 24 modules — a second, independent
module-count staleness in the tutorial, separate from F27. The book's
module count should say 24 (or drop the number and point at
`sutram-stdlib.html`).

## 10. What was checked and cleared (so "not listed" is not "not looked at")

- All 117 `docs/` files were grepped for: `Sutram Error`, `Sutram truti`,
  every old name in the task list (`kosh_push/pop/len/cap/clear/empty/peek/
  dequeue/enqueue`, `pankti_len`, `char_lower/upper/from`, `likha_fmt`,
  `vartani_cat`, `smaran_cp`, `sankhya_dot`), standalone `asti`/`nasti`,
  `sankhya_bindu`, `parimita`, `parimana`, `306`, `310`, `thread`,
  `arena`, `unmerged`, and every `64 MB` / region mention.
- `docs/decisions/*`, `docs/reports/*`, `docs/rounds/*`,
  `docs/ai-handoff-notes/*` were read only to the extent of classifying
  their old-token/old-name hits as historical (version-pinned or
  decision-record). No finding is raised against any of them, including
  `docs/rounds/CHANGELOG-ARCHIVE.md` (dozens of old-token hits, all
  pre-v294 history) and `docs/reports/LIBRARY-ENGLISH-AUDIT.md`
  (an audit of English names, whose subject is the old names themselves).
- Root files: `README.md` (cleared except WS2's "scattered, not combined"
  note), `PROJECT-MASTER.md`, `ROADMAP.md`, `AGENTS.md`,
  `INSTALL-WINDOWS.md` (0 findings), `LANGUAGE-PRIORITY.md` (cleared: it
  states the Error→truti exception at `:37`).
- HTML files that are indexes, not references, cleared: `sutram-book.html`,
  `sutram-book-2.html`, `sutram-book-3.html` (edition indexes, 0 old-name
  hits), `sutram-keyword-words.html`, `sutram-ide.html`,
  `sutram-benchmark-report.html`, `sutram-performance.html`,
  `sutram-philosophy.html`, `sutram-project-status.html`,
  `sutram-roadmap.html`, `sutram-scorecard.html`, `sutram-design-parameters.html`,
  `sutram-icon-thread.html`, `mockup-setup.html` (no check-string hits that
  present a current token/name; benchmark/philosophy/status pages do not
  teach the API).

## 11. Prioritised fix order (audit opinion only — no edits made)

1. **F25/F06 — regenerate or retire `sutram-stdlib-reference.html`.**
   It is the only reference a student can mistake for current while it
   lists 11 dead names and omits 18 live ones. `sutram-stdlib.html` is
   already exact; pointing at it costs less than hand-patching 29 rows.
2. **F05/F01 — fix the two student-facing tutorials/sections that teach
   the alias as primary** (`sutram-book-*.html` kosh chapter; §4a
   `likha_fmt` block). These are the findings most likely to make a new
   student write the wrong name first.
3. **WS2 paragraph** (§7 draft) into `WINDOWS-SETUP.md` §7 — the only
   finding whose absence causes silent mis-trust (a 0, a non-refusal)
   rather than a warning.
4. **F14/F15 — add `asti`/`nasti` to `SPECIFICATION.md` and the book
   operator table.** One row each; without them the primary Sanskrit
   spelling of equality is documented in exactly one place (§4b).
5. **F27/F26 — label §4b as an excerpt and fix the two 306 sentences.**
   Small edits, but they stop the "library = 60 (or 306) functions"
   misreading at its source.
6. **WS3 one-liners** (§8): the (i) reconciling sentence, the (ii) arena
   status line, the (iii) no-mid-block-reuse sentence, the (iv)
   parimana-excludes-reservation clause, the (v) no-thread-model line.
   Each is one sentence in §16/§19; together they close all five gaps.
7. **F07/F08/F22/F23/F28 — status banners, not rewrites:** mark
   OPEN-ISSUES §C and WHATS-LEFT C5/C6 resolved/superseded, and banner
   the `vocabulary/` proposal tables and the v253 COMPLETE extraction as
   superseded. Do not edit their historical rows.

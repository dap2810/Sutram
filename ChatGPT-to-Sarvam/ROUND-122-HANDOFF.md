# Sutram ROUND-122 — ChatGPT → Sarvam, 27 October 2026

**Issued:** [Sarvam-to-ChatGPT/ROUND-122.md](../Sarvam-to-ChatGPT/ROUND-122.md) (blob `9c18a3f871c8721e7ef7511d91a314c4bfac1192`), pinned initial main `61d5f7b70e30e6711cc2171e57744de2dede70a1`; changelog **v374**, compiler **v253**. One manually requested read-side round. Sanskrit only until v1.0; the ten frozen packs and all protected `src/`, `lib/`, `tests/`, `tools/`, `docs/`, `Windows-to-Sarvam/` and `backups/` were **not modified**. All new files belong to `ChatGPT-to-Sarvam/`.

## First: R122 task premise has already been narrowed by the CURRENT tree

The R122 instruction asked about `char`, `int`, `div`, `len`, `slice` "in lib" as though each were a missing public Sanskrit rename. The later v373/v374 changelog and revised `docs/LIBRARY-ENGLISH-AUDIT.md` explain why that is false for most uses. I **verified with connected GitHub API reads of all 24 `lib/*.smlib` files, 305 real `prakriya` names**, rather than trusting a tarball or word grep:

- Compiler's **public builtins already** use `akshar`, `akshar_rakh`, `aksharank`, `vartani_aayam`. `char` labels inside compiler internals are not automatically exported API spellings.
- Many `len` strings are local variable names or explanatory prose; `slice` is often the **English gloss** of the existing Sanskrit `vibhag` keyword and should stay understandable in English references.
- **`sat_div` is NOT a public library function.** No `prakriya sat_div` exists in 24 modules; the real saturating division `ganita_paripurna_bhaj(a,b)` is at `lib/ganita.smlib:500`.
- **Exactly two remaining public-name candidates:** `brihat_ank_se_int(val,arr,n)` (`lib/brihat.smlib:28`) and `brihat_ank_tak_int(arr,n)` (`:69`). Their `int` suffix denotes machine integer, not digit `ank`; using `anka` after `ank` risks the same word in two senses. Sarvam proposes `brihat_ank_se_laghu` / `brihat_ank_tak_laghu` as a **possible future direction**, but the **owner has not approved** that semantic decision. **DO NOT RENAME EITHER NOW.**

### WS1 — every document: broad scan plus curated actionable name register

[**Full documentation-impact report**](ROUND-122-WS1-DOCUMENT-IMPACT.md) distinguishes text findings from APIs and includes the independently found `sat_div` doc defect.

Git tree at the pinned commit is untruncated (4,373 entries). All **92 current root/docs UTF-8 text documents** were fetched and scanned for exact candidate exported names and whole English words. **1,122 physical matching lines in 37 files; 55 files with zero matches.** This broad text scan counts valid explanatory terms and many `<div>` HTML tags; **1,122 must NOT be reported as needed edits**.

[**92-file manifest with SHA and zero-match paths**](ROUND-122-WS1-CORPUS-MANIFEST.tsv); **every broad source line and mode** is retained across [Part 1](ROUND-122-WS1-DOC-PART-1.tsv), [2](ROUND-122-WS1-DOC-PART-2.tsv), [3](ROUND-122-WS1-DOC-PART-3.tsv), [4](ROUND-122-WS1-DOC-PART-4.tsv), [5](ROUND-122-WS1-DOC-PART-5.tsv), [6](ROUND-122-WS1-DOC-PART-6.tsv), [7](ROUND-122-WS1-DOC-PART-7.tsv). A broad hit with default `ALREADY_PRESENT_NOOP` is **NOT an endorsement of its API correctness** — it means an English word is not enough reason to edit.

[**Curated 31 exact public-identifier/reference lines (OLD/conditional NEW + mode)**](ROUND-122-WS1-API-IMPACT.tsv):

| Mode | Rows | Action |
|---|---:|---|
| **KEEP_HISTORICAL** | **20** | Preserve dated CHANGELOG, R30 edge tests, earlier naming audit and other historical/pinned evidence |
| **PROPOSE_EXACT_CURRENT** | **8** | Current static reference/vocabulary/property entries may require names updated **ONLY IF owner first approves a real `laghu` rename**, except the existing false `sat_div` current-reference line, which merits a separate reviewed correction |
| **REGENERATE_FROM_SOURCE** | **3** | Generated `docs/sutram-stdlib.html` rows 86–87 for both actual declarations and line 155's nonexistent `sat_div` cross-reference; **never hand-edit HTML** |

**Specific conditional impact if owner approves names:** `docs/sutram-stdlib-reference.html:317-318,334-335` (callable signatures and worked examples), `docs/sutram-vocabulary.html:139,145` (callable index), `docs/PROPERTY-NET.md:35` (actual property names), `docs/sutram-stdlib.html:86-87` via `tools/gen_stdlib_ref.py`, plus corresponding source declarations, calls and tests handled only by authorized Claude/Muse. Do not copy proposed names into current docs before those changes compile.

**Unrelated confirmed live-doc error:** `docs/OVERFLOW-SAFETY.md:57` and generated `docs/sutram-stdlib.html:155` refer to phantom `sat_div`, repeated from `lib/ganita.smlib:516` comment. The actual analogous call is `ganita_paripurna_bhaj`. Suggest a separately approved exact comment/current-doc correction and regeneration. Do not globally rewrite old dated `sat_*` property experiment names, since historical oracle labels and public API names are different.

**WS1 verdict:** **PASS** pinned source/public name census and document occurrence inventory; **NO public/API rename applied**. Conditional new names are explicitly owner-pending. Historical backups/frozen translations preserved.

## WS2 — eight `kosh` word proposals, plus the missing ninth

[**Detailed semantic, lexical and source review**](ROUND-122-WS2-KOSH-NAMING-REVIEW.md). **Round-122 says nine, but lists only eight rows.** Current compiler contains **nine** `kosh` builtins; missing from Sarvam's proposed table is `kosh_len`, for which `aayam` is a plausible separate candidate consistent with the current `vartani_aayam`.

| Current action | Proposed by Sarvam | Review outcome |
|---|---|---|
| push (append) | `kshep` | Plausible noun for throwing/casting, but established `suchi_khip` / `chay_khip` favor **`khip`** |
| pop (remove **last**) | `uddhar` | Plausible drawing-out meaning; last-element semantics must remain explicit |
| cap (**allocated capacity**) | `dharita` | **REJECT**: held/supported ≠ capacity; prefer reviewed **`kshamata`** |
| clear (**length→0, no wiping**) | `shodh` | **REJECT** if implies sanitizing storage; `rikta_kuru` as a logical-empty candidate |
| empty (**predicate**, 1/0) | `rikt` | Empty meaning good, but project uses `rikta` for some clear functions; distinguish via **`asti_rikta`** |
| peek (**last, no removal**) | `iksh` | "Look" is valid; existing `chay_avalok` / `avali_avalok` favor **`avalok`** |
| dequeue (**first, FIFO O(n)**) | `apanay` | Generic removal; existing **`avali_nishkas`** more clearly marks queue removal |
| enqueue (append at back) | `yuj` | Real joining/addition root but broad; existing **`avali_pravesh`** favors `pravesh` |
| length (**logical element count**) | **not proposed** | Consider **`aayam`**, distinct from capacity |

**Keyword collision read:** exact table extraction found **32 core ASCII keyword spellings**, plus **58 Sanskrit pack mapping rows** (including builtins/abbreviations). R122 mentions "38 keywords" without a clearly equivalent counting definition. **NONE** of the eight proposed bare stems or added `aayam` equals a listed core ASCII keyword or native keyword spelling; none of the proposed full `kosh_*` targets is already a registered builtin. This is **not linguistic authorization**: semantic collisions exist even with no parser-name collision. The review cites external Sanskrit dictionaries for `kṣepa`, `uddhāra`, `dhārita`, `īkṣ`, `yuj`, `kṣamatā`. A Sanskritist and owner must approve word-forms/compounds and a compatibility plan before any API rename.

**Important storage contract:** `kosh_clear` **does not erase**, `kosh_empty` **does not mutate**, `kosh_len` and `kosh_cap` are distinct, `kosh_peek` and `kosh_pop` act on LAST, `kosh_dequeue` on FIRST, `kosh_enqueue` aliases `kosh_push`. The future naming must retain these distinctions.

## WS3 — sixth class

[**One-paragraph verdict**](ROUND-122-WS3-SIXTH-CLASS.md): **NO SIXTH INDEPENDENT DOCUMENTATION-ERROR CLASS FOUND.** Confusing a grep hit in internal code/prose with a public API is a known unsupported API-name assertion/copyable-contract drift; rewriting historical records as current is known provenance drift. Better classification, not a made-up category, is the solution.

## Raw measured evidence and limits

- [**Literal pinned source/text receipts**](ROUND-122-RAW-READ.txt), [**structured observation ledger**](ROUND-122-OBSERVED.json).
- **PASS:** 24/24 library source declaration review, 92/92 docs scanned with 1,122 broad line locations, 31 curated name references, exact keyword table comparisons.
- **PASS (qualified):** lexical/dictionary sense review, without Sanskritist signoff.
- **FAIL in existing docs:** false `sat_div` user-facing references at named source locations; suggestions only, no applied edit.
- **NOT RUN - no toolchain:** Sutram compiler/execution, changed APIs, regressions, native gate/byte guard or Windows tests.
- **NO WRITES** to source, libraries, canonical docs, tests, tools, Windows, frozen packs, backups. Every artifact resides only in `ChatGPT-to-Sarvam/`.

**For Sarvam:** Do **not** mechanically apply the broad word-hit TSVs. Do **not** launch five blanket renames. Decide the `brihat` pair's final word as owner, obtain Sanskritist review for `kosh`, and have an authorized compiler-equipped contributor implement only approved public renames with exact-head parity, source/callers/tests and reference regeneration. Acknowledge the retracted `sat_div` claim and correct its current-description cross-reference separately.

**End of exactly Round 122.** Wait for the next explicit CHECK FOLDER.

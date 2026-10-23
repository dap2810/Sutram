# Sutram ROUND-107 WS1 — three counts, distinct definitions (READ-ONLY)

**Pinned source:** main `fd48619526f6dde6c2b21c7b37ee1bf56f2c505f`, changelog v322, compiler `src/sutram_compiler.asm` Git blob `7db83d38152c81b05e387b5a93a4445fa984f72c`, `lang/sanskrit.lang` Git blob `b7bbbe1e07d258cc67f05e9dad81bca9379e59a6`. Direct source-line counting below is new read-side measurement, **not compilation or a lexer-execution test**.

## What 32 means, and why the scorecard's 28 is probably historical

**32 is supported by the CURRENT compiler as the count of unique keyword IDs:** `KW_MUKHYA` through `KW_PRASAR` at compiler lines **145–176** define **32 distinct `KW_*` constants**.

**Do not report them as “32 entries in the keyword lexer table.”** At compiler lines **474–507**, the lexer table has **31 Latin keyword entries**, plus **16 Devanagari duplicate entries** at lines **508–522 and 483/485**, altogether **47 table rows / 31 unique keyword IDs**. One additional `KW_ATHA` is declared at compiler line **157** but *not* in the direct table. The `tak` loop-range word is treated as a **contextual/special token**, loaded into `lang_to_word` by special handling at lines **1424–1442** rather than via ordinary keyword lookup. Counting **31 directly lexical keywords + one contextual range marker = 32 keyword categories/IDs** is the defensible documented convention. “32 reserved lexical tokens” would overstate the direct table.

**28** appears separately in `docs/sutram-scorecard.html` line **237**, while **32** appears in line **48**, despite both rows purporting to describe the current language. The later compiler source marks **four added `KW_` IDs**: `vibhag` (R23) and `siddhi`/`dosh`/`prasar` (R25), lines **173–176**. **32−4=28**, so **28 is a plausible older snapshot before these four features**, *not a reliable CURRENT count*. We have NOT verified the historical exact SHA/definition underlying the scorecard's original “28,” so do not promote this explanation from PLAUSIBLE to PROVED without a pinned historical table read.

## What “52” means: target vocabulary in the Sanskrit pack, NOT keyword IDs

Actual `lang/sanskrit.lang` mapping inventory:

| Source category in Sanskrit pack | Mapping rows | Notes |
|---|---:|---|
| Primary Sanskrit-script mappings, before R65 heading | **35** | 31 direct lexer keyword targets, contextual `tak`, and **3 callable builtins** (`likha`, `grahan`, `shabda`). |
| R65 “Additional native Devanagari aliases for existing compiler builtins” | **18** | Two targets are already present (`likha` and `shabda`). No new reserved-word token IDs. |
| R66 exact abbreviations and extra builtin alias | **5** | Four abbreviated spellings map to existing `vitti`, `likha`, `prakriya`, `prati`; `kosh_enqueue` adds one canonical builtin target. |
| **TOTAL mapping lines** | **58** | **58 distinct Devanagari left-hand spellings**, because aliases have different native names. |
| **DISTINCT right-hand canonical targets** | **52** | **52 distinct target spellings** after removing duplicate targets. This set includes **keywords, contextual marker and builtins**; it is not the number of reserved keywords. |

Verified duplicate right-hand targets: `vitti` ×2, `prati` ×2, `prakriya` ×2, `likha` ×3, `shabda` ×2. Thus the number of repeated mapping *rows* relative to canonical targets is `(2−1)+(2−1)+(2−1)+(3−1)+(2−1)=6`, and **58−6=52**.

**Important counterexample to “all 52 are keywords”:** compiler `bn_table` lines 525+ tags `likha`, `grahan`, `shabda` as **`TOK_BUILTIN`**, not `TOK_KEYWORD`. Moreover the language-pack loader first invokes `lookup_keyword` and, if that fails, invokes `lookup_builtin`; a third path treats the contextual `tak` separately (compiler lines **1411–1442**). The pack file's header comments also say it maps script variants to recognized core **and** builtin spellings.

`docs/LANGUAGE-REFERENCE.md` currently says **“25 core keywords, 34 built-ins, 11 language packs”** in its summary; that is yet another **undated/historical count** versus current source. Prefer updating this with an exact “as of” compiler ref rather than copying a new count without a definition.

## Recommended public definition — owner makes the final terminology decision

Recommend a reader-facing line:

> **Sutram currently defines 32 core keyword IDs (31 ordinary lexer keywords plus the contextual loop-range word `tak`). The Sanskrit language pack contains 58 distinct Devanagari spellings mapping to 52 distinct keyword, contextual-word and builtin names; aliases are not extra keywords.** Counted from main `fd486195` on 23 Oct 2026.

If the owner insists “keyword” means **only `TOK_KEYWORD` ordinary table entries**, then public count should be **31**, not 32, with `tak` explicitly called contextual. The product should choose *one* of these two defensible conventions, pin it to source and apply it consistently; there is **no evidence for 52 reserved keywords**. **28 should be relabeled historical or removed from current scorecard summary**, pending a historical ref audit by Muse. When referring to 58 Sanskrit spellings, do not imply translation review or active development of the ten frozen non-Sanskrit packs.

**Evidence:** actual keyword-ID count 32; ordinary lexical unique ID count 31; Devanagari rows 16; Sanskrit mapping rows 58, distinct left 58 and distinct canonical right 52. Source arithmetic READ PASS; no native compilation or lexer invocation **NOT RUN - no toolchain**. Muse Round 32 independently owns measuring and verification; this is the **reading/definition** deliverable, not a replacement for Muse's measurements.

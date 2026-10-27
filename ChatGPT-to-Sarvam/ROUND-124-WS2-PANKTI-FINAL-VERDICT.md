# Sutram R124 WS2 — FINAL semantic decision: `pankti_len`

**Decision: YES, rename the public builtin to `pankti_aayam` if the owner is eliminating the last English suffix. Do NOT rename its prefix to `mala`.** This is a final engineering/naming verdict for Sarvam, not permission for ChatGPT to change compiler source. It is not a pure "English word in a keyword" fix: `pankti_len` is a **`TOK_BUILTIN`**, not a lexer keyword. `pankti` is an old *Latin keyword spelling* for an array, but its concept still means an ordered row/sequence, and **`पङ्क्ति` remains the CURRENT Devanagari spelling for the `mala` array keyword** (`lang/sanskrit.lang:28`). In source diagnostics, `pankti` also means source line. These are contextual uses, not proof that `pankti` has lost its row/sequence meaning.

## What the builtin actually measures

**Source at pinned main** `87015a8fa9cd3b55f868ac49f517b3f657d2b443`:

- `src/sutram_compiler.asm:561` maps `bn_panktilen` to `TOK_BUILTIN, BN_PANKTILEN`; the user-facing spelling at `:764` is `"pankti_len"`.
- `src/sutram_compiler.asm:16976-17021` emits **slice length** from the slice descriptor at `[rax+8]` when the expression is a slice, **declared array length** from `[rax-8]` when the argument is a known `mala` variable, or **0** otherwise. This is **not specifically a digit-array length**, nor a generic byte count, nor the growable `kosh` logical length.
- `docs/LANGUAGE-REFERENCE.md:94,476,494` expressly documents arrays and slices; `kosh_len(k)` is a separate builtin for the `kosh` logical count and `vartani_aayam` is text length.
- `lang/sanskrit.lang:59` already maps the native compound `पङ्क्तिदैर्घ्य` to `pankti_len`: the language already interprets the builtin as **row length**. `pankti_aayam` keeps exactly that public prefix while adopting the existing Sutram `aayam` length stem from `vartani_aayam`.

## Why this name wins

| Name | Decision | Reason |
|---|---|---|
| **`pankti_aayam`** | **CHOOSE** | existing public prefix + already established `aayam`; works for both arrays and slices; low semantic and migration drift |
| `mala_aayam` | REJECT for this API | matches current Latin array keyword but falsely narrows a builtin that also accepts a standalone `vibhag` slice; renames two concepts at once |
| `vibhag_aayam` | REJECT for this API | would falsely imply fixed arrays are excluded |
| `pankti_len` | KEEP callable until migration approved | current compiled API; an unannounced replacement breaks legacy source |

**Actionable compatibility plan for authorized implementers:** owner signs off `pankti_aayam`; update parser builtin spelling and Sanskrit mapping `पङ्क्तिदैर्घ्य` destination, docs, tests and examples together. The simplest source-preserving transition is to accept **both** `pankti_aayam` (canonical) and `pankti_len` (legacy alias) mapped to the same `BN_PANKTILEN` ID, then measure a separately approved removal policy. **Do not remove the existing `r4_o_pankti` historical keyword compatibility table**, which is distinct from the public builtin. Preserve the 0-on-unknown-pointer behavior unless a separate semantics change is specified and tested.

**PASS** source semantics and native pack reading. **NOT APPLIED** any proposed public rename. **NOT RUN - no toolchain** compile, parser alias acceptance and regression guard. Linguistic certification of the compound is **not** claimed; the engineering vocabulary choice is final for this review.

# Sutram Round 88 — Hindi review: two status labels

**Decision needed (one line):** `KEEP BOTH` (recommended), or `CHANGE 1`, `CHANGE 2`, or `CHANGE BOTH` with corrected wording. **No automatic change to the Hindi pack.**

**Current source:** `lang/hindi.sandesh` Git blob `bc2a8a83c1988c7be2910690ed0ebe735b96e33e`; compared with `lang/sanskrit.sandesh` `6f214b0cb0ec15efae7a373678298f7919a22b8e`. Both have 128 entries. The two original mechanical flags arose **only because the short labels are identical** in both packs, not because script or syntax validation failed. Neither is a confirmed mistranslation.

## 1. `ide.st_bhasha_w` — Language label

**Exact current Hindi string:** `   |   भाषा: `

**Exact JSON representation (shows spaces):** `"   |   भाषा: "`

**Meaning:** IDE status line prefix identifying the selected programming-language pack (followed by the displayed language name).

**Why flagged / possible issue:** The Hindi text is byte-identical to Sanskrit, which triggered a mechanical review flag. That alone is not an error; भाषा is normal Hindi and clearly means language.

**Optional alternative:** `   |   चयनित भाषा: `

Only if the owner wants to emphasize that this is the selected language. It is longer, so the IDE status-bar layout would need checking.

**Suggested decision:** **KEEP existing wording**. Native speaker may override.

## 2. `ide.st_lipi_w` — Script label

**Exact current Hindi string:** `   |   लिपि: `

**Exact JSON representation (shows spaces):** `"   |   लिपि: "`

**Meaning:** IDE status line prefix identifying the active typing/writing script (followed by the script name).

**Why flagged / possible issue:** The Hindi text is byte-identical to Sanskrit, but लिपि is the usual Hindi word for script. The label is already natural; the only possible issue is clarity for newcomers.

**Optional alternative:** `   |   टाइपिंग लिपि: `

Only if the owner wants the label to specify that it refers to typing mode. It is longer, so the IDE status-bar layout would need checking.

**Suggested decision:** **KEEP existing wording**. Native speaker may override.

**Owner reply example:** `KEEP BOTH`.

If either changes, preserve the initial `   |   ` status separator and final space, confirm the appended dynamic language/script name still displays correctly, and run `tools/sandesh.py --check` plus the IDE status-line tests. The default decision does **not** require regenerating message packs or altering accepted output goldens.

**Review classification:** source text and equality checks PASS; whether a speaker approves the wording is **NOT_RUN**. This page is a proposal to review, not authorization to edit.

# R73 WS4 — current compiler line audit; document/tree sweep still required

Snapshot `5efb592f46a7862d573f55b3a95439a35e0c9ad5`. Compiler `src/sutram_compiler.asm` blob `4b137114d5b67aab0df61e356aad9af94056ae1b`. **22,808 source lines inspected programmatically**, with whole-word scans of obsolete keyword spellings in the instruction/data portion of each line (comments split off at `;`).

**Obsolete quoted tokens in active NASM data** are exclusively the *intentional* old-keyword migration hint table:
`anyatra` line 293; `punaravartana` 294; `pratiyati` 295; `uddeshya` 296; `pankti` 297; `srijana` 298; `nishedha` 299; `ayojan` 300; `parigrah` 301; `nishkriya` 302; `to` 303. Do NOT replace them with new keywords: the point is to detect and diagnose old code. The further occurrence of `pankti` at **304** is the legitimate Sanskrit word for a diagnostic *line*, not the obsolete array keyword.

**Active byte/length assumptions inspected:**
- lines **2359–2384**, `yoj` (3 ASCII bytes): comparison `0x6F79` and `0x6A` matches current spelling. No old six-byte import assumed there.
- lines **2386–2394**, `niryat` (6 ASCII bytes): `0x7972696E` plus `0x7461` matches `niryat`.
- lines **2573–2594**, import expander: `0x6F79`, `0x6A` and `add r12,3` correctly reference `yoj`; **the label/comment still say ayojan**.
- lines **8402–8434**, for-loop range: `0x6174`, `0x6B`, NUL correctly reference `tak`; **comments still say to/punaravartana**.
- lines **4005–4084**, module graph: lengths 6 `niryat`, 8 `prakriya`, 27 Devanagari `प्रक्रिया`, 5 `sutra`, and loaded `mg_w_ayojan db "yoj"` (line 3078). Lengths match the inspected strings. Rename internal labels only after tests.
- lines **255–273**, arity table comments still say `char_at`, `char_code`, `set_char`, `pankti_len`. They are COMMENTS, not keyword registrations.

**Outcome:** no active use of the obsolete Latin spellings was found in the eleven-word source/data scan outside the intentional diagnostics. The five identified raw hexadecimal keyword compares and main fixed-length parsing sites match the current spellings. This is a **completed compiler-file scan**, not a claim that all raw constants in the tree are correct.

**Remaining NOT_RUN:** exhaustive repository-wide scan of all tracked `.sm/.smlib/.lang/.md/.html/.py/.ps1/.asm` files. Current vocabulary is in `docs/sutram-vocabulary.html`; a full tree audit needs a complete clean checkout and should separately classify historical teaching examples, migration hints and active code. No modifications to keywords or accepted goldens were made.

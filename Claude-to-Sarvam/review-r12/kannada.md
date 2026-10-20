# Review sheet: Kannada (ಕನ್ನಡ)

**The wording here is UNVERIFIED.** Claude wrote every message in ROUND-11. The automatic checks
prove only the form: the identifiers, the punctuation, the script, no Latin prose. No native
speaker has read these messages.

## How to review

- Read each **"This pack, as printed"** line: it is exactly what the compiler or the IDE shows,
  with sample names and numbers (`prog.sm`, `y`, `f`, `1`, `2`, `hindi`) filled in.
- **Meaning** is a gloss in English for the reviewer. It is never shown to a user.
- Write a better wording under **Correction**. Leave it empty if the message is right.
- **Keep as they are:** `Sutram Error`, the `[E_…]` tags, the quotes `'…'` around a name, the
  leading `: ` and the line breaks (⏎), and code (`lib/`, `.smlib`, `--lang`, keywords).
- **The parts are joined by the compiler in a fixed order.** Some messages are pieces of one
  sentence (marked "middle of …"). Judge the whole printed line, and say if the order itself
  cannot work in this language.
- **Return the corrections** as this file, edited, or as a list of `number: correction`.
  They go into `lang/kannada.sandesh`.

## Levels

| Level | Meaning |
|---|---|
| **LIKELY WRONG** | I think it is wrong, or it must be decided; please correct it first |
| **UNSURE** | I have a specific doubt, written under the message |
| **DRAFT** | no specific doubt, but still unverified |

**128 messages:** 1 LIKELY WRONG, 14 UNSURE, 113 DRAFT.

| # | Message | Level |
|---|---|---|
| 3 | `r48_msg_near` | UNSURE |
| 22 | `r7_msg_arity2` | UNSURE |
| 23 | `r7_msg_arity3` | UNSURE |
| 26 | `r7_msg_mod_missing2` | LIKELY WRONG |
| 40 | `r65_msg_add` | UNSURE |
| 52 | `msg_lang_ok` | UNSURE |
| 53 | `msg_lang_fail` | UNSURE |
| 54 | `msg_shell_banner` | UNSURE |
| 61 | `msg_namespace_module_missing` | UNSURE |
| 69 | `msg_ast_overflow` | UNSURE |
| 85 | `r55_msg_proto_signature` | UNSURE |
| 91 | `mg_e_noexp2` | UNSURE |
| 92 | `mg_e_noexp3` | UNSURE |
| 96 | `mg_e_undef2` | UNSURE |
| 101 | `mg_e_valias2` | UNSURE |

---
### 1. `msg_usage` — **DRAFT**

- **Where:** compiler: `sutram` with no arguments
- **Meaning:** the usage text: compile, check only, with a language pack, interactive, version
- **Default (romanised Sanskrit):**

```
Sutram - sampurna sutra
Prayog:
  sutram <nivesh.sm> <nirgat.bin>         sankalan
  sutram --check <nivesh.sm>              janch matra, nirgat nahi
  sutram --lang <pak> <nivesh.sm> <nirgat.bin>  bhasha pak sahit
  sutram -i                               khol (samvad)
  sutram --version                        sanskaran
```

- **This pack, as printed:**

```
ಸೂತ್ರಮ್ - ಸಂಪೂರ್ಣ ಸೂತ್ರ
ಬಳಕೆ:
  sutram <ಮೂಲ.sm> <ಫಲಿತ.bin>         ಸಂಕಲನ
  sutram --check <ಮೂಲ.sm>              ಪರಿಶೀಲನೆ ಮಾತ್ರ, ಫಲಿತ ಕಡತ ಇಲ್ಲ
  sutram --lang <ಪ್ಯಾಕ್> <ಮೂಲ.sm> <ಫಲಿತ.bin>  ಭಾಷಾ ಪ್ಯಾಕ್ ಜೊತೆ
  sutram -i                               ಸಂವಾದ
  sutram --version                        ಆವೃತ್ತಿ
```
- **Correction:** 

### 2. `msg_version` — **DRAFT**

- **Where:** compiler: `sutram --version`
- **Meaning:** version line; 'a Sanskrit-based language -> x86-64 machine code'
- **Default (romanised Sanskrit):**

```
Sutram 1.0 (v182) - sampurna sutra
Samskrita-mukhya bhasha -> x86-64 yantra-bhasha
```

- **This pack, as printed:**

```
ಸೂತ್ರಮ್ 1.0 (v182) - ಸಂಪೂರ್ಣ ಸೂತ್ರ
ಸಂಸ್ಕೃತ-ಪ್ರಧಾನ ಭಾಷೆ -> x86-64 ಯಂತ್ರ ಭಾಷೆ
```
- **Correction:** 

### 3. `r48_msg_near` — **UNSURE**

- **Where:** compiler: `--check`, a parse error
- **Meaning:** 'word' (the token where parsing failed)
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: shabd '=' + caret line`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: ಪದ '=' + caret line`
- **This message alone:** `: Sutram Error [E_PARSE]: ಪದ '`
- **Doubt:** 'word' stands for a token; check that it reads naturally before the quoted token.
- **Correction:** 

### 4. `r48_msg_ok` — **DRAFT**

- **Where:** compiler: `--check`, no errors
- **Meaning:** check: correct (no output file made)
- **Default (romanised Sanskrit), as printed:** `Sutram janch: shuddh (nirgat patra nahi)⏎`
- **This pack, as printed:** `ಸೂತ್ರಮ್ ಪರಿಶೀಲನೆ: ಸರಿ (ಫಲಿತ ಕಡತ ರಚಿಸಲಾಗಿಲ್ಲ)⏎`
- **Correction:** 

### 5. `r48_msg_errors` — **DRAFT**

- **Where:** compiler: `--check`, errors found
- **Meaning:** check: errors found; no output file made
- **Default (romanised Sanskrit), as printed:** `Sutram janch: dosh mile; nirgat patra nahi⏎`
- **This pack, as printed:** `ಸೂತ್ರಮ್ ಪರಿಶೀಲನೆ: ದೋಷಗಳು ಕಂಡುಬಂದಿವೆ; ಫಲಿತ ಕಡತ ರಚಿಸಲಾಗಿಲ್ಲ⏎`
- **Correction:** 

### 6. `r48_msg_eof` — **DRAFT**

- **Where:** compiler: `--check`, error at end of file
- **Meaning:** <end of file>, shown in place of the token
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: shabd '<patra-ant>'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: ಪದ '<ಕಡತದ ಅಂತ್ಯ>'`
- **This message alone:** `<ಕಡತದ ಅಂತ್ಯ>`
- **Correction:** 

### 7. `r50_msg_setchar_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** akshar_rakh needs 3 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: akshar_rakh: 3 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: akshar_rakh: 3 ಪ್ರಮಾಣಗಳು ಬೇಕು⏎`
- **In the pack file:** `Sutram Error: {kw:akshar_rakh}: 3 ಪ್ರಮಾಣಗಳು ಬೇಕು⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 8. `r52_msg_dvaram_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** dvaram needs 2 or 3 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: dvaram: 2 va 3 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: dvaram: 2 ಅಥವಾ 3 ಪ್ರಮಾಣಗಳು ಬೇಕು⏎`
- **In the pack file:** `Sutram Error: {kw:dvaram}: 2 ಅಥವಾ 3 ಪ್ರಮಾಣಗಳು ಬೇಕು⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 9. `r52_msg_charat_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** akshar needs 2 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: akshar: 2 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: akshar: 2 ಪ್ರಮಾಣಗಳು ಬೇಕು⏎`
- **In the pack file:** `Sutram Error: {kw:akshar}: 2 ಪ್ರಮಾಣಗಳು ಬೇಕು⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 10. `r52_msg_charcode_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** aksharank needs 1 or 2 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: aksharank: 1 va 2 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: aksharank: 1 ಅಥವಾ 2 ಪ್ರಮಾಣಗಳು ಬೇಕು⏎`
- **In the pack file:** `Sutram Error: {kw:aksharank}: 1 ಅಥವಾ 2 ಪ್ರಮಾಣಗಳು ಬೇಕು⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 11. `r48_msg_undefined` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown function 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_FUNCTION]: agyat prakriya 'foo'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_FUNCTION]: ಅಜ್ಞಾತ ಕ್ರಿಯೆ 'foo'`
- **This message alone:** `: Sutram Error [E_UNDEFINED_FUNCTION]: ಅಜ್ಞಾತ ಕ್ರಿಯೆ '`
- **Correction:** 

### 12. `r4_msg_undef` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown name 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_NAME]: agyat naam 'y'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_NAME]: ಅಜ್ಞಾತ ಹೆಸರು 'y'`
- **This message alone:** `: Sutram Error [E_UNDEFINED_NAME]: ಅಜ್ಞಾತ ಹೆಸರು '`
- **Correction:** 

### 13. `r4_msg_hint_decl` — **DRAFT**

- **Where:** compiler: hint after an unknown name
- **Meaning:** hint: declare it before use: vitti NAME = ...
- **Default (romanised Sanskrit), as printed:** `Sanket: prayog se purv ghoshana avashyak: vitti y = ...`
- **This pack, as printed:** `ಸೂಚನೆ: ಬಳಸುವ ಮೊದಲು ಘೋಷಣೆ ಬೇಕು: ಚರ y = ...`
- **This message alone:** `ಸೂಚನೆ: ಬಳಸುವ ಮೊದಲು ಘೋಷಣೆ ಬೇಕು: ಚರ `
- **In the pack file:** `ಸೂಚನೆ: ಬಳಸುವ ಮೊದಲು ಘೋಷಣೆ ಬೇಕು: {kw:vitti} `  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 14. `r4_msg_hint_old` — **DRAFT**

- **Where:** compiler: hint, opens two hints
- **Meaning:** hint: 'NAME…
- **Default (romanised Sanskrit), as printed:** `Sanket: 'anyatra' purana kunjishabd (v157 se purv); navin: 'anya'`
- **This pack, as printed:** `ಸೂಚನೆ: 'anyatra' ಹಳೆಯ ಕೀಲಿಪದ (v157 ಕ್ಕಿಂತ ಹಿಂದಿನದು); ಹೊಸದು: 'anya'`
- **This message alone:** `ಸೂಚನೆ: '`
- **Correction:** 

### 15. `r4_msg_hint_old2` — **DRAFT**

- **Where:** compiler: hint after an old keyword
- **Meaning:** 'OLD' is an old keyword (before v157); new: 'NEW'
- **Default (romanised Sanskrit), as printed:** `Sanket: 'anyatra' purana kunjishabd (v157 se purv); navin: 'anya'`
- **This pack, as printed:** `ಸೂಚನೆ: 'anyatra' ಹಳೆಯ ಕೀಲಿಪದ (v157 ಕ್ಕಿಂತ ಹಿಂದಿನದು); ಹೊಸದು: 'anya'`
- **This message alone:** `' ಹಳೆಯ ಕೀಲಿಪದ (v157 ಕ್ಕಿಂತ ಹಿಂದಿನದು); ಹೊಸದು: '`
- **Correction:** 

### 16. `r5_msg_field` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown field 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_UNKNOWN_FIELD]: agyat kshetra 'q'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_UNKNOWN_FIELD]: ಅಜ್ಞಾತ ಕ್ಷೇತ್ರ 'q'`
- **This message alone:** `: Sutram Error [E_UNKNOWN_FIELD]: ಅಜ್ಞಾತ ಕ್ಷೇತ್ರ '`
- **Correction:** 

### 17. `r7_msg_dup` — **DRAFT**

- **Where:** compiler
- **Meaning:** declared again: 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_DUPLICATE_NAME]: punah ghoshana 'x'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_DUPLICATE_NAME]: ಮರು-ಘೋಷಣೆ 'x'`
- **This message alone:** `: Sutram Error [E_DUPLICATE_NAME]: ಮರು-ಘೋಷಣೆ '`
- **Correction:** 

### 18. `r7_msg_dup_hint` — **DRAFT**

- **Where:** compiler: hint after a duplicate
- **Meaning:** 'NAME' is already declared; to give it a new value: NAME = ...
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' pahle se ghoshit hai; naya man dene ke liye: x = ...`
- **This pack, as printed:** `ಸೂಚನೆ: 'x' ಈಗಾಗಲೇ ಘೋಷಿತವಾಗಿದೆ; ಹೊಸ ಮೌಲ್ಯ ನೀಡಲು: x = ...`
- **This message alone:** `' ಈಗಾಗಲೇ ಘೋಷಿತವಾಗಿದೆ; ಹೊಸ ಮೌಲ್ಯ ನೀಡಲು: `
- **Correction:** 

### 19. `r7_msg_field_amb` — **DRAFT**

- **Where:** compiler
- **Meaning:** field 'NAME' (is ambiguous)
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_AMBIGUOUS_FIELD]: kshetra 'x'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_AMBIGUOUS_FIELD]: ಕ್ಷೇತ್ರ 'x'`
- **This message alone:** `: Sutram Error [E_AMBIGUOUS_FIELD]: ಕ್ಷೇತ್ರ '`
- **Correction:** 

### 20. `r7_msg_field_amb_hint` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** 'NAME' is at different places in two rachanas; give it a different name in each
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' do rachana me alag sthan par hai; har rachana me alag naam rakhein⏎`
- **This pack, as printed:** `ಸೂಚನೆ: 'x' ಎರಡು ರಚನೆಗಳಲ್ಲಿ ಬೇರೆ ಬೇರೆ ಸ್ಥಾನದಲ್ಲಿದೆ; ಪ್ರತಿ ರಚನೆಯಲ್ಲಿ ಬೇರೆ ಹೆಸರು ಇಡಿ⏎`
- **This message alone:** `' ಎರಡು ರಚನೆಗಳಲ್ಲಿ ಬೇರೆ ಬೇರೆ ಸ್ಥಾನದಲ್ಲಿದೆ; ಪ್ರತಿ ರಚನೆಯಲ್ಲಿ ಬೇರೆ ಹೆಸರು ಇಡಿ⏎`
- **Correction:** 

### 21. `r7_msg_field_dup_hint` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** 'NAME' is already in this rachana
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' is rachana me pahle se hai⏎`
- **This pack, as printed:** `ಸೂಚನೆ: 'x' ಈ ರಚನೆಯಲ್ಲಿ ಈಗಾಗಲೇ ಇದೆ⏎`
- **This message alone:** `' ಈ ರಚನೆಯಲ್ಲಿ ಈಗಾಗಲೇ ಇದೆ⏎`
- **Correction:** 

### 22. `r7_msg_arity2` — **UNSURE**

- **Where:** compiler: middle of the arity error
- **Meaning:** 'f' [was given] N arguments; in the signature M
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' ko 1 tark diye; hastakshar me 2`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' ಗೆ 1 ಪ್ರಮಾಣಗಳನ್ನು ನೀಡಲಾಗಿದೆ; ಸಹಿಯಲ್ಲಿ 2`
- **This message alone:** `' ಗೆ `
- **Doubt:** Word order is fixed by the code: 'NAME' <this> N <arity3> M. Check that the sentence reads naturally around the name and the two numbers.
- **Doubt:** The case suffix is printed after a space ('f' <suffix>); written Kannada normally attaches it to the word (with a quoted code name, say which you prefer). The checker keeps the default's leading "' ", so fixing this needs that rule relaxed for this message.
- **Correction:** 

### 23. `r7_msg_arity3` — **UNSURE**

- **Where:** compiler: middle of the arity error
- **Meaning:** … N arguments given; in the signature M
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' ko 1 tark diye; hastakshar me 2`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' ಗೆ 1 ಪ್ರಮಾಣಗಳನ್ನು ನೀಡಲಾಗಿದೆ; ಸಹಿಯಲ್ಲಿ 2`
- **This message alone:** ` ಪ್ರಮಾಣಗಳನ್ನು ನೀಡಲಾಗಿದೆ; ಸಹಿಯಲ್ಲಿ `
- **Doubt:** 'ಪ್ರಮಾಣ' for an argument is my choice; 'ಸಹಿ' for a signature is a calque.
- **Doubt:** The count is printed before this text and is often 1 ('f' … 1 …): the noun is in the plural form, so '1 <plural>' may read wrong. A fragment cannot change with the number.
- **Correction:** 

### 24. `r7_msg_arity_hint` — **DRAFT**

- **Where:** compiler: hint after the arity error
- **Meaning:** hint: give exactly as many arguments as the function's definition has
- **Default (romanised Sanskrit), as printed:** `Sanket: utne hi tark dein jitne prakriya ki paribhasha me hain⏎`
- **This pack, as printed:** `ಸೂಚನೆ: ಕ್ರಿಯೆಯ ವ್ಯಾಖ್ಯಾನದಲ್ಲಿ ಎಷ್ಟು ಪ್ರಮಾಣಗಳಿವೆಯೋ ಅಷ್ಟೇ ನೀಡಿ⏎`
- **Correction:** 

### 25. `r7_msg_mod_missing` — **DRAFT**

- **Where:** compiler
- **Meaning:** import file not found: NAME
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_MISSING]: yoj patra aprapt: ganit`
- **This pack, as printed:** `Sutram Error [E_MODULE_MISSING]: ಸೇರ್ಪಡೆ ಕಡತ ಸಿಗಲಿಲ್ಲ: ganit`
- **This message alone:** `Sutram Error [E_MODULE_MISSING]: ಸೇರ್ಪಡೆ ಕಡತ ಸಿಗಲಿಲ್ಲ: `
- **Correction:** 

### 26. `r7_msg_mod_missing2` — **LIKELY WRONG**

- **Where:** compiler: hint after a missing import
- **Meaning:** hint: NAME.smlib should be in lib/ or in the source file's folder
- **Default (romanised Sanskrit):**

```

Sanket: lib/ me ya srot patra ki nirdeshika me naam.smlib hona chahiye
```

- **This pack, as printed:**

```

ಸೂಚನೆ: <ಹೆಸರು>.smlib lib/ ನಲ್ಲಿ ಅಥವಾ ಮೂಲ ಕಡತದ ಕೋಶದಲ್ಲಿ ಇರಬೇಕು
```
- **Doubt:** LIKELY WRONG: 'ಕೋಶ' is used here for a folder, but ಕೋಶ is also the pack's keyword for kosh (the data structure). The hint becomes ambiguous; a different word for folder is needed.
- **Correction:** 

### 27. `r7_msg_hint_block` — **DRAFT**

- **Where:** compiler: hint after an unknown name
- **Meaning:** 'NAME' is declared inside a block { } or a loop; it is not visible outside it
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' ek khand { } ya chakra me ghoshit hai; uske bahar drishya nahi⏎`
- **This pack, as printed:** `ಸೂಚನೆ: 'x' ಒಂದು ಖಂಡ { } ಅಥವಾ ಪುನರಾವರ್ತನೆ ಒಳಗೆ ಘೋಷಿತವಾಗಿದೆ; ಅದರ ಹೊರಗೆ ಕಾಣುವುದಿಲ್ಲ⏎`
- **This message alone:** `' ಒಂದು ಖಂಡ { } ಅಥವಾ ಪುನರಾವರ್ತನೆ ಒಳಗೆ ಘೋಷಿತವಾಗಿದೆ; ಅದರ ಹೊರಗೆ ಕಾಣುವುದಿಲ್ಲ⏎`
- **In the pack file:** `' ಒಂದು ಖಂಡ { } ಅಥವಾ {kw:chakra} ಒಳಗೆ ಘೋಷಿತವಾಗಿದೆ; ಅದರ ಹೊರಗೆ ಕಾಣುವುದಿಲ್ಲ⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 28. `r5_msg_field_hint` — **DRAFT**

- **Where:** compiler: hint, opens the field hint
- **Meaning:** hint: 'NAME…
- **Default (romanised Sanskrit), as printed:** `Sanket: 'q' kisi rachana ka kshetra nahi⏎`
- **This pack, as printed:** `ಸೂಚನೆ: 'q' ಯಾವುದೇ ರಚನೆಯ ಕ್ಷೇತ್ರವಲ್ಲ⏎`
- **This message alone:** `ಸೂಚನೆ: '`
- **Correction:** 

### 29. `r5_msg_field_hint2` — **DRAFT**

- **Where:** compiler: hint after an unknown field
- **Meaning:** 'NAME' is not a field of any rachana
- **Default (romanised Sanskrit), as printed:** `Sanket: 'q' kisi rachana ka kshetra nahi⏎`
- **This pack, as printed:** `ಸೂಚನೆ: 'q' ಯಾವುದೇ ರಚನೆಯ ಕ್ಷೇತ್ರವಲ್ಲ⏎`
- **This message alone:** `' ಯಾವುದೇ ರಚನೆಯ ಕ್ಷೇತ್ರವಲ್ಲ⏎`
- **Correction:** 

### 30. `msg_err_line` — **DRAFT**

- **Where:** compiler: a parse error
- **Meaning:** grammar error, line L:C
- **Default (romanised Sanskrit):**

```

Sutram Error: vyakaran dosh, pankti 
```

- **This pack, as printed:**

```

Sutram Error: ವ್ಯಾಕರಣ ದೋಷ, ಸಾಲು 
```
- **Correction:** 

### 31. `msg_err_near` — **DRAFT**

- **Where:** compiler: a parse error
- **Meaning:** , word 'TOKEN'
- **Default (romanised Sanskrit), as printed:** `⏎Sutram Error: vyakaran dosh, pankti 3:11, shabd '='`
- **This pack, as printed:** `⏎Sutram Error: ವ್ಯಾಕರಣ ದೋಷ, ಸಾಲು 3:11, ಪದ '='`
- **This message alone:** `, ಪದ '`
- **Correction:** 

### 32. `msg_err_eof` — **DRAFT**

- **Where:** compiler: a parse error at the end of the file
- **Meaning:** end of file, shown in place of the token
- **Default (romanised Sanskrit), as printed:** `⏎Sutram Error: vyakaran dosh, pankti 6:1, shabd 'patra-ant'`
- **This pack, as printed:** `⏎Sutram Error: ವ್ಯಾಕರಣ ದೋಷ, ಸಾಲು 6:1, ಪದ 'ಕಡತದ ಅಂತ್ಯ'`
- **This message alone:** `ಕಡತದ ಅಂತ್ಯ`
- **Correction:** 

### 33. `msg_err_hint` — **DRAFT**

- **Where:** compiler: hint after a parse error
- **Meaning:** hint: check the word and the grammar at this place
- **Default (romanised Sanskrit), as printed:** `Sanket: is sthan par shabd aur vyakaran dekho.⏎`
- **This pack, as printed:** `ಸೂಚನೆ: ಈ ಸ್ಥಳದಲ್ಲಿ ಪದ ಮತ್ತು ವ್ಯಾಕರಣ ಪರಿಶೀಲಿಸಿ.⏎`
- **Correction:** 

### 34. `msg_err_arg_limit` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** hint: a function takes at most 6 arguments
- **Default (romanised Sanskrit), as printed:** `Sanket: prakriya adhiktam 6 tark lete hain.⏎`
- **This pack, as printed:** `ಸೂಚನೆ: ಕ್ರಿಯೆ ಗರಿಷ್ಠ 6 ಪ್ರಮಾಣಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳುತ್ತದೆ.⏎`
- **Correction:** 

### 35. `msg_err_duplicate_func` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** hint: the function is defined twice (name clash)
- **Default (romanised Sanskrit), as printed:** `Sanket: dohri prakriya paribhasha (naam takkar).⏎`
- **This pack, as printed:** `ಸೂಚನೆ: ಕ್ರಿಯೆಯ ಎರಡು ವ್ಯಾಖ್ಯಾನಗಳು (ಹೆಸರಿನ ಘರ್ಷಣೆ).⏎`
- **Correction:** 

### 36. `msg_duplicate_func` — **DRAFT**

- **Where:** compiler
- **Meaning:** function defined again: NAME
- **Default (romanised Sanskrit), as printed:** `Sutram Error: punah prakriya paribhasha: f`
- **This pack, as printed:** `Sutram Error: ಕ್ರಿಯೆಯ ಮರು-ವ್ಯಾಖ್ಯಾನ: f`
- **This message alone:** `Sutram Error: ಕ್ರಿಯೆಯ ಮರು-ವ್ಯಾಖ್ಯಾನ: `
- **Correction:** 

### 37. `msg_undefined_func` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown function: NAME
- **Default (romanised Sanskrit), as printed:** `Sutram Error: agyat prakriya: f`
- **This pack, as printed:** `Sutram Error: ಅಜ್ಞಾತ ಕ್ರಿಯೆ: f`
- **This message alone:** `Sutram Error: ಅಜ್ಞಾತ ಕ್ರಿಯೆ: `
- **Correction:** 

### 38. `msg_array_oob` — **DRAFT**

- **Where:** the compiled program, at run time
- **Meaning:** mala index out of bounds
- **Default (romanised Sanskrit), as printed:** `Sutram Error: mala ank seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ಪಂಕ್ತಿ ಸೂಚ್ಯಂಕ ಮಿತಿ ಮೀರಿದೆ⏎`
- **In the pack file:** `Sutram Error: {kw:mala} ಸೂಚ್ಯಂಕ ಮಿತಿ ಮೀರಿದೆ⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 39. `msg_kosh_required` — **DRAFT**

- **Where:** compiler
- **Meaning:** a kosh function needs a kosh variable
- **Default (romanised Sanskrit), as printed:** `Sutram Error: kosh prakriya hetu kosh-vitti avashyak⏎`
- **This pack, as printed:** `Sutram Error: ಕೋಶ ಕ್ರಿಯೆಗೆ ಕೋಶ ಚರ ಬೇಕು⏎`
- **In the pack file:** `Sutram Error: {kw:kosh} ಕ್ರಿಯೆಗೆ {kw:kosh} {kw:vitti} ಬೇಕು⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 40. `r65_msg_add` — **UNSURE**

- **Where:** the program, `trap` build
- **Meaning:** overflow in an addition
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: yog atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: ಸಂಕಲನದಲ್ಲಿ ಉಕ್ಕಿ ಹರಿವು⏎`
- **This message alone:** `: ಸಂಕಲನದಲ್ಲಿ ಉಕ್ಕಿ ಹರಿವು⏎`
- **Doubt:** 'ಉಕ್ಕಿ ಹರಿವು' (boiling over) for an integer overflow is colloquial; check (all seven trap messages).
- **Correction:** 

### 41. `r65_msg_sub` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a subtraction
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: nyun atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: ವ್ಯವಕಲನದಲ್ಲಿ ಉಕ್ಕಿ ಹರಿವು⏎`
- **This message alone:** `: ವ್ಯವಕಲನದಲ್ಲಿ ಉಕ್ಕಿ ಹರಿವು⏎`
- **Correction:** 

### 42. `r65_msg_mul` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a multiplication
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: gun atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: ಗುಣಾಕಾರದಲ್ಲಿ ಉಕ್ಕಿ ಹರಿವು⏎`
- **This message alone:** `: ಗುಣಾಕಾರದಲ್ಲಿ ಉಕ್ಕಿ ಹರಿವು⏎`
- **Correction:** 

### 43. `r65_msg_div` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** division by zero
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: shunya se bhajan⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: ಸೊನ್ನೆಯಿಂದ ಭಾಗಾಕಾರ⏎`
- **This message alone:** `: ಸೊನ್ನೆಯಿಂದ ಭಾಗಾಕಾರ⏎`
- **Correction:** 

### 44. `r65_msg_mod` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** remainder by zero
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: shunya se shesh⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: ಸೊನ್ನೆಯಿಂದ ಶೇಷ⏎`
- **This message alone:** `: ಸೊನ್ನೆಯಿಂದ ಶೇಷ⏎`
- **Correction:** 

### 45. `r65_msg_div_overflow` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a division
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: bhajan atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: ಭಾಗಾಕಾರದಲ್ಲಿ ಉಕ್ಕಿ ಹರಿವು⏎`
- **This message alone:** `: ಭಾಗಾಕಾರದಲ್ಲಿ ಉಕ್ಕಿ ಹರಿವು⏎`
- **Correction:** 

### 46. `r65_msg_mod_overflow` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a remainder
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: shesh atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: ಶೇಷದಲ್ಲಿ ಉಕ್ಕಿ ಹರಿವು⏎`
- **This message alone:** `: ಶೇಷದಲ್ಲಿ ಉಕ್ಕಿ ಹರಿವು⏎`
- **Correction:** 

### 47. `msg_kosh_empty` — **DRAFT**

- **Where:** the program, at run time
- **Meaning:** kosh_pop from an empty kosh
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rikta kosh se kosh_pop⏎`
- **This pack, as printed:** `Sutram Error: ಖಾಲಿ ಕೋಶದಿಂದ kosh_pop⏎`
- **In the pack file:** `Sutram Error: ಖಾಲಿ ಕೋಶದಿಂದ {kw:kosh_pop}⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 48. `msg_kosh_peek_empty` — **DRAFT**

- **Where:** the program, at run time
- **Meaning:** kosh_peek from an empty kosh
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rikta kosh se kosh_peek⏎`
- **This pack, as printed:** `Sutram Error: ಖಾಲಿ ಕೋಶದಿಂದ kosh_peek⏎`
- **In the pack file:** `Sutram Error: ಖಾಲಿ ಕೋಶದಿಂದ {kw:kosh_peek}⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 49. `msg_kosh_dequeue_empty` — **DRAFT**

- **Where:** the program, at run time
- **Meaning:** kosh_dequeue from an empty kosh
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rikta kosh se kosh_dequeue⏎`
- **This pack, as printed:** `Sutram Error: ಖಾಲಿ ಕೋಶದಿಂದ kosh_dequeue⏎`
- **In the pack file:** `Sutram Error: ಖಾಲಿ ಕೋಶದಿಂದ {kw:kosh_dequeue}⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 50. `msg_kosh_param_type` — **DRAFT**

- **Where:** compiler
- **Meaning:** kosh argument: element type differs
- **Default (romanised Sanskrit), as printed:** `Sutram Error: kosh tark: tatv prakar bhinn⏎`
- **This pack, as printed:** `Sutram Error: ಕೋಶ ಪ್ರಮಾಣ: ಅಂಶದ ಪ್ರಕಾರ ಬೇರೆ⏎`
- **Correction:** 

### 51. `msg_kosh_param_push` — **DRAFT**

- **Where:** compiler
- **Meaning:** kosh_push is not supported on a kosh argument
- **Default (romanised Sanskrit), as printed:** `Sutram Error: kosh tark par kosh_push asamarthit⏎`
- **This pack, as printed:** `Sutram Error: ಕೋಶ ಪ್ರಮಾಣದ ಮೇಲೆ kosh_push ಬೆಂಬಲವಿಲ್ಲ⏎`
- **In the pack file:** `Sutram Error: ಕೋಶ ಪ್ರಮಾಣದ ಮೇಲೆ {kw:kosh_push} ಬೆಂಬಲವಿಲ್ಲ⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 52. `msg_lang_ok` — **UNSURE**

- **Where:** compiler: every run with `--lang`
- **Meaning:** language pack found: PACK
- **Default (romanised Sanskrit), as printed:** `Bhasha pak prapt: hindi`
- **This pack, as printed:** `ಭಾಷಾ ಪ್ಯಾಕ್ ಸಿಕ್ಕಿದೆ: hindi`
- **This message alone:** `ಭಾಷಾ ಪ್ಯಾಕ್ ಸಿಕ್ಕಿದೆ: `
- **Doubt:** 'pack' (the language-pack file) has no settled native word; check the term.
- **Correction:** 

### 53. `msg_lang_fail` — **UNSURE**

- **Where:** compiler
- **Meaning:** warning: language pack not found: PACK
- **Default (romanised Sanskrit), as printed:** `Chetavani: bhasha pak nahi mila: hindi`
- **This pack, as printed:** `ಎಚ್ಚರಿಕೆ: ಭಾಷಾ ಪ್ಯಾಕ್ ಸಿಗಲಿಲ್ಲ: hindi`
- **This message alone:** `ಎಚ್ಚರಿಕೆ: ಭಾಷಾ ಪ್ಯಾಕ್ ಸಿಗಲಿಲ್ಲ: `
- **Doubt:** The same term for 'pack' as msg_lang_ok.
- **Correction:** 

### 54. `msg_shell_banner` — **UNSURE**

- **Where:** compiler: `sutram -i`, at start
- **Meaning:** interactive shell banner: write a statement and press Enter; it runs at once; commands help / exit / show all
- **Default (romanised Sanskrit):**

```
Sutram khol v1.0 - sampurna sutra
Sutram kathan likho aur Enter dabao. Turant chalega.
Aadesh: sahayata (sahay) | nirgat (nikas) | sarvam (dekho)
```

- **This pack, as printed:**

```
ಸೂತ್ರಮ್ ಸಂವಾದ v1.0 - ಸಂಪೂರ್ಣ ಸೂತ್ರ
ಸೂತ್ರಮ್ ವಾಕ್ಯ ಬರೆದು Enter ಒತ್ತಿ. ತಕ್ಷಣ ಚಲಿಸುತ್ತದೆ.
ಆದೇಶಗಳು: sahayata (ಸಹಾಯ) | nirgat (ನಿರ್ಗಮನ) | sarvam (ಎಲ್ಲ ನೋಡಿ)
```
- **Doubt:** 'Enter' is kept as the key's label; the verb for pressing a key should be checked.
- **Correction:** 

### 55. `msg_shell_bye` — **DRAFT**

- **Where:** compiler: leaving `sutram -i`
- **Meaning:** greeting; session ended
- **Default (romanised Sanskrit), as printed:** `Namaste! Satra samapt.⏎`
- **This pack, as printed:** `ನಮಸ್ಕಾರ! ಸಂವಾದ ಮುಗಿಯಿತು.⏎`
- **Correction:** 

### 56. `msg_shell_help` — **DRAFT**

- **Where:** compiler: `sahayata` in `sutram -i`
- **Meaning:** shell help: print text, declare a variable, print a value, a loop, declare a mala, show the whole program, leave
- **Default (romanised Sanskrit):**

```
Sutram khol sahay:
  likha("Namaste\n")            likha paath
  vitti x = 5             char ghoshan
  likha(x + 3)            vyakti likha
  chakra i = 0 tak 5 { likha(i) }   aavartan
  mala arr[5]             mala ghoshan
  sarvam                  pura karyakram dekho
  nirgat                  khol se nikal
```

- **This pack, as printed:**

```
ಸೂತ್ರಮ್ ಸಂವಾದ ಸಹಾಯ:
  ಬರೆ("ನಮಸ್ಕಾರ\n")            ಪಠ್ಯ ಬರೆಯುತ್ತದೆ
  ಚರ x = 5             ಚರ ಘೋಷಣೆ
  ಬರೆ(x + 3)            ಮೌಲ್ಯ ಬರೆಯುತ್ತದೆ
  ಪುನರಾವರ್ತನೆ i = 0 ರಿಂದ 5 { ಬರೆ(i) }   ಪುನರಾವರ್ತನೆ
  ಪಂಕ್ತಿ arr[5]             ಪಂಕ್ತಿ ಘೋಷಣೆ
  sarvam                  ಸಂಪೂರ್ಣ ಕಾರ್ಯಕ್ರಮ ನೋಡಿ
  nirgat                  ಸಂವಾದದಿಂದ ನಿರ್ಗಮಿಸಿ
```
- **In the pack file:** `ಸೂತ್ರಮ್ ಸಂವಾದ ಸಹಾಯ:⏎  {kw:likha}("ನಮಸ್ಕಾರ\n")            ಪಠ್ಯ ಬರೆಯುತ್ತದೆ⏎  {kw:vitti} x = 5             {kw:vitti} ಘೋಷಣೆ⏎  {kw:likha}(x + 3)            ಮೌಲ್ಯ ಬರೆಯುತ್ತದೆ⏎  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   ಪುನರಾವರ್ತನೆ⏎  {kw:mala} arr[5]             {kw:mala} ಘೋಷಣೆ⏎  sarvam                  ಸಂಪೂರ್ಣ ಕಾರ್ಯಕ್ರಮ ನೋಡಿ⏎  nirgat                  ಸಂವಾದದಿಂದ ನಿರ್ಗಮಿಸಿ⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 57. `msg_open_err` — **DRAFT**

- **Where:** compiler
- **Meaning:** input (source) file not found
- **Default (romanised Sanskrit), as printed:** `Sutram Error: nivesh patra aprapt⏎`
- **This pack, as printed:** `Sutram Error: ಮೂಲ ಕಡತ ಸಿಗಲಿಲ್ಲ⏎`
- **Correction:** 

### 58. `msg_ok` — **DRAFT**

- **Where:** compiler: a successful compile
- **Meaning:** done: N bytes compiled
- **Default (romanised Sanskrit), as printed:** `Siddh: 297 baait sankalit⏎`
- **This pack, as printed:** `ಯಶಸ್ವಿ: 297 ಬೈಟ್ ಸಂಕಲಿತ⏎`
- **This message alone:** `ಯಶಸ್ವಿ: `
- **Correction:** 

### 59. `msg_bytes` — **DRAFT**

- **Where:** compiler: a successful compile
- **Meaning:** … bytes compiled
- **Default (romanised Sanskrit), as printed:** `Siddh: 297 baait sankalit⏎`
- **This pack, as printed:** `ಯಶಸ್ವಿ: 297 ಬೈಟ್ ಸಂಕಲಿತ⏎`
- **This message alone:** ` ಬೈಟ್ ಸಂಕಲಿತ⏎`
- **Correction:** 

### 60. `msg_namespace_error` — **DRAFT**

- **Where:** compiler
- **Meaning:** invalid import (form: module@alias, alias up to 31 bytes)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ashuddh yoj (roop: ghatak@upanaam, upanaam 31 baait tak)⏎`
- **This pack, as printed:** `Sutram Error: ಅಶುದ್ಧ ಸೇರಿಸು (ರೂಪ: ಘಟಕ@ಉಪನಾಮ, ಉಪನಾಮ 31 ಬೈಟ್‌ವರೆಗೆ)⏎`
- **In the pack file:** `Sutram Error: ಅಶುದ್ಧ {kw:yoj} (ರೂಪ: ಘಟಕ@ಉಪನಾಮ, ಉಪನಾಮ 31 ಬೈಟ್‌ವರೆಗೆ)⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 61. `msg_namespace_module_missing` — **UNSURE**

- **Where:** compiler
- **Meaning:** module file not found
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ghatak patra aprapt⏎`
- **This pack, as printed:** `Sutram Error: ಘಟಕ ಕಡತ ಸಿಗಲಿಲ್ಲ⏎`
- **Doubt:** 'ಘಟಕ' for a module; check.
- **Correction:** 

### 62. `msg_namespace_alias_reuse` — **DRAFT**

- **Where:** compiler
- **Meaning:** alias already used (for another module)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: upanaam purv-niyukt (anya ghatak)⏎`
- **This pack, as printed:** `Sutram Error: ಉಪನಾಮ ಈಗಾಗಲೇ ಬಳಕೆಯಲ್ಲಿದೆ (ಬೇರೆ ಘಟಕಕ್ಕೆ)⏎`
- **Correction:** 

### 63. `r51_alias_conflict` — **DRAFT**

- **Where:** compiler
- **Meaning:** alias already used (for another module)
- **Default (romanised Sanskrit), as printed:** `prog.sm:2: Sutram Error [E_MODULE_ALIAS_REUSE]: upanaam purv-niyukt (anya ghatak)⏎`
- **This pack, as printed:** `prog.sm:2: Sutram Error [E_MODULE_ALIAS_REUSE]: ಉಪನಾಮ ಈಗಾಗಲೇ ಬಳಕೆಯಲ್ಲಿದೆ (ಬೇರೆ ಘಟಕಕ್ಕೆ)⏎`
- **This message alone:** `: Sutram Error [E_MODULE_ALIAS_REUSE]: ಉಪನಾಮ ಈಗಾಗಲೇ ಬಳಕೆಯಲ್ಲಿದೆ (ಬೇರೆ ಘಟಕಕ್ಕೆ)⏎`
- **Correction:** 

### 64. `msg_namespace_func_limit` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of module function names exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ghatak prakriya-naam seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ಘಟಕದ ಕ್ರಿಯೆ-ಹೆಸರುಗಳ ಮಿತಿ ಮೀರಿದೆ⏎`
- **Correction:** 

### 65. `msg_import_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the expanded source exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: vistarit srot seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ವಿಸ್ತರಿತ ಮೂಲದ ಮಿತಿ ಮೀರಿದೆ⏎`
- **Correction:** 

### 66. `graph_cycle_prefix` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** import cycle: a -> b -> a
- **Default (romanised Sanskrit), as printed:** `prog.sm:1: Sutram Error [E_MODULE_CYCLE] yoj chakra: a -> b -> a`
- **This pack, as printed:** `prog.sm:1: Sutram Error [E_MODULE_CYCLE] ಸೇರ್ಪಡೆ ಚಕ್ರ: a -> b -> a`
- **This message alone:** `ಸೇರ್ಪಡೆ ಚಕ್ರ: `
- **Correction:** 

### 67. `graph_missing_prefix` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** import file not found: NAME
- **Default (romanised Sanskrit), as printed:** `prog.sm:1: Sutram Error [E_MODULE_MISSING] yoj patra aprapt: ganit`
- **This pack, as printed:** `prog.sm:1: Sutram Error [E_MODULE_MISSING] ಸೇರ್ಪಡೆ ಕಡತ ಸಿಗಲಿಲ್ಲ: ganit`
- **This message alone:** `ಸೇರ್ಪಡೆ ಕಡತ ಸಿಗಲಿಲ್ಲ: `
- **Correction:** 

### 68. `graph_invalid_prefix` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** invalid module name
- **Default (romanised Sanskrit), as printed:** `prog.sm:1: Sutram Error [E_MODULE_INVALID] ashuddh ghatak naam`
- **This pack, as printed:** `prog.sm:1: Sutram Error [E_MODULE_INVALID] ಅಶುದ್ಧ ಘಟಕ ಹೆಸರು`
- **This message alone:** `ಅಶುದ್ಧ ಘಟಕ ಹೆಸರು`
- **Correction:** 

### 69. `msg_ast_overflow` — **UNSURE**

- **Where:** compiler
- **Meaning:** limit of the syntax tree exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: vakya-vriksh seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ವಾಕ್ಯ-ವೃಕ್ಷದ ಮಿತಿ ಮೀರಿದೆ⏎`
- **Doubt:** 'syntax tree' is a coined technical term here; check it.
- **Correction:** 

### 70. `msg_func_params_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the function parameter list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya tark-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ಕ್ರಿಯೆಯ ಪ್ರಮಾಣ-ಪಟ್ಟಿಯ ಮಿತಿ ಮೀರಿದೆ⏎`
- **Correction:** 

### 71. `msg_var_table_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the variable list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: vitti-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ಚರ ಪಟ್ಟಿಯ ಮಿತಿ ಮೀರಿದೆ⏎`
- **In the pack file:** `Sutram Error: {kw:vitti} ಪಟ್ಟಿಯ ಮಿತಿ ಮೀರಿದೆ⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 72. `msg_func_table_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the function list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ಕ್ರಿಯೆ ಪಟ್ಟಿಯ ಮಿತಿ ಮೀರಿದೆ⏎`
- **Correction:** 

### 73. `msg_patch_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the call list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: aahvan-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ಕರೆ ಪಟ್ಟಿಯ ಮಿತಿ ಮೀರಿದೆ⏎`
- **Correction:** 

### 74. `msg_func_defs_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the function definition list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya paribhasha-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ಕ್ರಿಯೆ ವ್ಯಾಖ್ಯಾನ-ಪಟ್ಟಿಯ ಮಿತಿ ಮೀರಿದೆ⏎`
- **Correction:** 

### 75. `msg_r9_guna_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** guna limit exceeded (1024)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: guna seema atikram (1024)⏎`
- **This pack, as printed:** `Sutram Error: ಗುಣ ಮಿತಿ ಮೀರಿದೆ (1024)⏎`
- **In the pack file:** `Sutram Error: {kw:guna} ಮಿತಿ ಮೀರಿದೆ (1024)⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 76. `msg_break_patch_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** too many krama (break) in a loop
- **Default (romanised Sanskrit), as printed:** `Sutram Error: chakra me krama seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ಪುನರಾವರ್ತನೆ ಒಳಗೆ ಕ್ರಮ ಮಿತಿ ಮೀರಿದೆ⏎`
- **In the pack file:** `Sutram Error: {kw:chakra} ಒಳಗೆ {kw:krama} ಮಿತಿ ಮೀರಿದೆ⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 77. `msg_continue_patch_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** too many agrim (continue) in a loop
- **Default (romanised Sanskrit), as printed:** `Sutram Error: chakra me agrim seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ಪುನರಾವರ್ತನೆ ಒಳಗೆ ಮುಂದುವರಿಸು ಮಿತಿ ಮೀರಿದೆ⏎`
- **In the pack file:** `Sutram Error: {kw:chakra} ಒಳಗೆ {kw:agrim} ಮಿತಿ ಮೀರಿದೆ⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 78. `msg_code_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the machine code exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: yantra-bhasha seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ಯಂತ್ರ ಭಾಷೆಯ ಮಿತಿ ಮೀರಿದೆ⏎`
- **Correction:** 

### 79. `msg_rachana_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the rachana list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rachana-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ರಚನೆ ಪಟ್ಟಿಯ ಮಿತಿ ಮೀರಿದೆ⏎`
- **In the pack file:** `Sutram Error: {kw:rachana} ಪಟ್ಟಿಯ ಮಿತಿ ಮೀರಿದೆ⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 80. `msg_rachana_fields_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of rachana fields exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rachana kshetra seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ರಚನೆ ಕ್ಷೇತ್ರಗಳ ಮಿತಿ ಮೀರಿದೆ⏎`
- **In the pack file:** `Sutram Error: {kw:rachana} ಕ್ಷೇತ್ರಗಳ ಮಿತಿ ಮೀರಿದೆ⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 81. `msg_block_nesting_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of block depth exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: khand gahrai seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ಖಂಡದ ಆಳದ ಮಿತಿ ಮೀರಿದೆ⏎`
- **Correction:** 

### 82. `msg_block_stmt_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of statements in a block exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: khand kathan seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ಖಂಡದಲ್ಲಿ ವಾಕ್ಯಗಳ ಮಿತಿ ಮೀರಿದೆ⏎`
- **Correction:** 

### 83. `r55_msg_proto_duplicate` — **DRAFT**

- **Where:** compiler
- **Meaning:** function forward-declared again
- **Default (romanised Sanskrit), as printed:** `Sutram Error: punah prakriya purv-ghoshana⏎`
- **This pack, as printed:** `Sutram Error: ಕ್ರಿಯೆಯ ಮರು ಪೂರ್ವ-ಘೋಷಣೆ⏎`
- **Correction:** 

### 84. `r55_msg_proto_missing` — **DRAFT**

- **Where:** compiler
- **Meaning:** function forward-declared but never defined
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya purv-ghoshana paribhasha-rahit⏎`
- **This pack, as printed:** `Sutram Error: ಕ್ರಿಯೆಯ ಪೂರ್ವ-ಘೋಷಣೆ ಇದೆ, ವ್ಯಾಖ್ಯಾನ ಇಲ್ಲ⏎`
- **Correction:** 

### 85. `r55_msg_proto_signature` — **UNSURE**

- **Where:** compiler
- **Meaning:** forward declaration and definition differ (arguments/type)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya purv-ghoshana va paribhasha bhinn (tark/prakar)⏎`
- **This pack, as printed:** `Sutram Error: ಕ್ರಿಯೆಯ ಪೂರ್ವ-ಘೋಷಣೆ ಮತ್ತು ವ್ಯಾಖ್ಯಾನ ಬೇರೆ (ಪ್ರಮಾಣ/ಪ್ರಕಾರ)⏎`
- **Doubt:** 'forward declaration' (a prototype) is a coined term; check it.
- **Correction:** 

### 86. `r55_msg_proto_capacity` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of function forward declarations exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya purv-ghoshana seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ಕ್ರಿಯೆ ಪೂರ್ವ-ಘೋಷಣೆಗಳ ಮಿತಿ ಮೀರಿದೆ⏎`
- **Correction:** 

### 87. `r56_msg_global_capacity` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of module-level variables exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ghatak-star vitti seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ಘಟಕ-ಮಟ್ಟದ ಚರ ಮಿತಿ ಮೀರಿದೆ⏎`
- **In the pack file:** `Sutram Error: ಘಟಕ-ಮಟ್ಟದ {kw:vitti} ಮಿತಿ ಮೀರಿದೆ⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 88. `r56_msg_global_duplicate` — **DRAFT**

- **Where:** compiler
- **Meaning:** module-level variable name declared again
- **Default (romanised Sanskrit), as printed:** `Sutram Error: punah ghatak-star vitti naam⏎`
- **This pack, as printed:** `Sutram Error: ಘಟಕ-ಮಟ್ಟದ ಚರ ಹೆಸರು ಮತ್ತೆ⏎`
- **In the pack file:** `Sutram Error: ಘಟಕ-ಮಟ್ಟದ {kw:vitti} ಹೆಸರು ಮತ್ತೆ⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 89. `r56_msg_patch_capacity` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of global value references exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: sarvatrik mulya sandarbh seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ಸಾರ್ವತ್ರಿಕ ಮೌಲ್ಯ ಉಲ್ಲೇಖಗಳ ಮಿತಿ ಮೀರಿದೆ⏎`
- **Correction:** 

### 90. `mg_e_cycle` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** import cycle: a -> b -> a
- **Default (romanised Sanskrit), as printed:** `prog.sm:1:Sutram Error [E_MODULE_CYCLE]: yoj chakra: a -> b -> a`
- **This pack, as printed:** `prog.sm:1:Sutram Error [E_MODULE_CYCLE]: ಸೇರ್ಪಡೆ ಚಕ್ರ: a -> b -> a`
- **This message alone:** `Sutram Error [E_MODULE_CYCLE]: ಸೇರ್ಪಡೆ ಚಕ್ರ: `
- **Correction:** 

### 91. `mg_e_noexp2` — **UNSURE**

- **Where:** compiler: middle of 'not exported'
- **Meaning:** 'SYM' [from] module 'MOD' [is] not exported
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' ghatak 'vec' se aniryat⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' ಘಟಕ 'vec' ದಿಂದ ರಫ್ತು ಮಾಡಲಾಗಿಲ್ಲ⏎`
- **This message alone:** `' ಘಟಕ '`
- **Doubt:** Order fixed by the code: 'SYM' <this> 'MOD' <noexp3>. Check that 'SYM … MOD … not exported' reads as one sentence.
- **Correction:** 

### 92. `mg_e_noexp3` — **UNSURE**

- **Where:** compiler: end of 'not exported'
- **Meaning:** … not exported from module MOD
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' ghatak 'vec' se aniryat⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' ಘಟಕ 'vec' ದಿಂದ ರಫ್ತು ಮಾಡಲಾಗಿಲ್ಲ⏎`
- **This message alone:** `' ದಿಂದ ರಫ್ತು ಮಾಡಲಾಗಿಲ್ಲ⏎`
- **Doubt:** The case suffix is printed after a space ('f' <suffix>); written Kannada normally attaches it to the word (with a quoted code name, say which you prefer). The checker keeps the default's leading "' ", so fixing this needs that rule relaxed for this message.
- **Correction:** 

### 93. `mg_e_dupexp1` — **DRAFT**

- **Where:** compiler
- **Meaning:** exported again: 'SYM', module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: punah niryat 'thing', ghatak 'dup'`
- **This pack, as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: ಮರು ರಫ್ತು 'thing', ಘಟಕ 'dup'`
- **This message alone:** `Sutram Error [E_MODULE_DUP_EXPORT]: ಮರು ರಫ್ತು '`
- **Correction:** 

### 94. `mg_e_dupexp2` — **DRAFT**

- **Where:** compiler: middle
- **Meaning:** …, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: punah niryat 'thing', ghatak 'dup'`
- **This pack, as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: ಮರು ರಫ್ತು 'thing', ಘಟಕ 'dup'`
- **This message alone:** `', ಘಟಕ '`
- **Correction:** 

### 95. `mg_e_undef1` — **DRAFT**

- **Where:** compiler
- **Meaning:** export 'SYM' has no definition, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: niryat 'thing' paribhasha-rahit, ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: ರಫ್ತು 'thing' ಗೆ ವ್ಯಾಖ್ಯಾನವಿಲ್ಲ, ಘಟಕ 'vec'`
- **This message alone:** `Sutram Error [E_EXPORT_UNDEFINED]: ರಫ್ತು '`
- **Correction:** 

### 96. `mg_e_undef2` — **UNSURE**

- **Where:** compiler: middle
- **Meaning:** … has no definition, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: niryat 'thing' paribhasha-rahit, ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: ರಫ್ತು 'thing' ಗೆ ವ್ಯಾಖ್ಯಾನವಿಲ್ಲ, ಘಟಕ 'vec'`
- **This message alone:** `' ಗೆ ವ್ಯಾಖ್ಯಾನವಿಲ್ಲ, ಘಟಕ '`
- **Doubt:** The case suffix is printed after a space ('f' <suffix>); written Kannada normally attaches it to the word (with a quoted code name, say which you prefer). The checker keeps the default's leading "' ", so fixing this needs that rule relaxed for this message.
- **Correction:** 

### 97. `mg_e_unknown1` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown symbol 'SYM', module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: agyat sanket 'thing', ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: ಅಜ್ಞಾತ ಚಿಹ್ನೆ 'thing', ಘಟಕ 'vec'`
- **This message alone:** `Sutram Error [E_EXPORT_UNDEFINED]: ಅಜ್ಞಾತ ಚಿಹ್ನೆ '`
- **Correction:** 

### 98. `mg_e_unknown2` — **DRAFT**

- **Where:** compiler: middle
- **Meaning:** …, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: agyat sanket 'thing', ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: ಅಜ್ಞಾತ ಚಿಹ್ನೆ 'thing', ಘಟಕ 'vec'`
- **This message alone:** `', ಘಟಕ '`
- **Correction:** 

### 99. `mg_e_depth` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of import depth exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_DEPTH]: yoj gahrai seema atikram⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_DEPTH]: ಸೇರ್ಪಡೆ ಆಳದ ಮಿತಿ ಮೀರಿದೆ⏎`
- **Correction:** 

### 100. `mg_e_valias1` — **DRAFT**

- **Where:** compiler
- **Meaning:** a v1 module 'MOD' needs an alias: yoj MOD@upanaam
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 ghatak 'vec' upanaam avashyak: yoj vec@upanaam`
- **This pack, as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 ಘಟಕ 'vec' ಗೆ ಉಪನಾಮ ಬೇಕು: ಸೇರಿಸು vec@upanaam`
- **This message alone:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 ಘಟಕ '`
- **Correction:** 

### 101. `mg_e_valias2` — **UNSURE**

- **Where:** compiler: middle
- **Meaning:** … needs an alias: yoj MOD@upanaam
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 ghatak 'vec' upanaam avashyak: yoj vec@upanaam`
- **This pack, as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 ಘಟಕ 'vec' ಗೆ ಉಪನಾಮ ಬೇಕು: ಸೇರಿಸು vec@upanaam`
- **This message alone:** `' ಗೆ ಉಪನಾಮ ಬೇಕು: ಸೇರಿಸು `
- **In the pack file:** `' ಗೆ ಉಪನಾಮ ಬೇಕು: {kw:yoj} `  (`{kw:…}` is the pack's own keyword)
- **Doubt:** The case suffix is printed after a space ('f' <suffix>); written Kannada normally attaches it to the word (with a quoted code name, say which you prefer). The checker keeps the default's leading "' ", so fixing this needs that rule relaxed for this message.
- **Correction:** 

### 102. `mg_e_limit` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of modules/imports exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_LIMIT]: ghatak/yoj seema atikram⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_LIMIT]: ಘಟಕ/ಸೇರ್ಪಡೆ ಮಿತಿ ಮೀರಿದೆ⏎`
- **Correction:** 

### 103. `r66_msg_bad_utf8` — **DRAFT**

- **Where:** compiler
- **Meaning:** invalid or broken Indian-script name
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_UTF8]: ashuddh ya khandit bharatiya naam⏎`
- **This pack, as printed:** `Sutram Error [E_UTF8]: ಅಶುದ್ಧ ಅಥವಾ ತುಂಡಾದ ಭಾರತೀಯ ಹೆಸರು⏎`
- **Correction:** 

### 104. `r68_utf8_tail` — **DRAFT**

- **Where:** compiler
- **Meaning:** invalid or broken UTF-8 in the source
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_UTF8]: prog.sm:2: srot me ashuddh ya khandit UTF-8⏎`
- **This pack, as printed:** `Sutram Error [E_UTF8]: prog.sm:2: ಮೂಲದಲ್ಲಿ ಅಶುದ್ಧ ಅಥವಾ ತುಂಡಾದ UTF-8⏎`
- **This message alone:** `: ಮೂಲದಲ್ಲಿ ಅಶುದ್ಧ ಅಥವಾ ತುಂಡಾದ UTF-8⏎`
- **Correction:** 

### 105. `r68_value_tail` — **DRAFT**

- **Where:** compiler
- **Meaning:** an abbreviation is not a value: 'वि॰'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_ABBREVIATION_VALUE]: prog.sm:2: sankshep shabd mulya nahi: 'वि॰'`
- **This pack, as printed:** `Sutram Error [E_ABBREVIATION_VALUE]: prog.sm:2: ಸಂಕ್ಷೇಪ ಪದ ಮೌಲ್ಯವಲ್ಲ: 'वि॰'`
- **This message alone:** `: ಸಂಕ್ಷೇಪ ಪದ ಮೌಲ್ಯವಲ್ಲ: '`
- **Correction:** 

### 106. `ide.st_pankti_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** line N (start of the status line)
- **Default (romanised Sanskrit), as printed:** `pankti 12   stambh 4   |   bhasha: …`
- **This pack, as printed:** `ಸಾಲು 12   ಸ್ತಂಭ 4   |   ಭಾಷೆ: …`
- **This message alone:** `ಸಾಲು `
- **Correction:** 

### 107. `ide.st_stambh_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** column N
- **Default (romanised Sanskrit), as printed:** `pankti 12   stambh 4   |   bhasha: …`
- **This pack, as printed:** `ಸಾಲು 12   ಸ್ತಂಭ 4   |   ಭಾಷೆ: …`
- **This message alone:** `   ಸ್ತಂಭ `
- **Correction:** 

### 108. `ide.st_bhasha_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** | language: NAME
- **Default (romanised Sanskrit), as printed:** `…4   |   bhasha: हिन्दी`
- **This pack, as printed:** `…4   |   ಭಾಷೆ: हिन्दी`
- **This message alone:** `   |   ಭಾಷೆ: `
- **Correction:** 

### 109. `ide.st_akshara_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** | letters (clusters): N
- **Default (romanised Sanskrit), as printed:** `…   |   akshara: 26`
- **This pack, as printed:** `…   |   ಅಕ್ಷರಗಳು: 26`
- **This message alone:** `   |   ಅಕ್ಷರಗಳು: `
- **Correction:** 

### 110. `ide.st_lipi_w` — **DRAFT**

- **Where:** IDE status line, typing mode on
- **Meaning:** | script: NAME (the typing script)
- **Default (romanised Sanskrit), as printed:** `…   |   lipi: தமிழ்`
- **This pack, as printed:** `…   |   ಲಿಪಿ: தமிழ்`
- **This message alone:** `   |   ಲಿಪಿ: `
- **Correction:** 

### 111. `ide.st_sanchit_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** saved
- **Default (romanised Sanskrit), as printed:** `…   |   sanchit`
- **This pack, as printed:** `…   |   ಉಳಿಸಲಾಗಿದೆ`
- **This message alone:** `ಉಳಿಸಲಾಗಿದೆ`
- **Correction:** 

### 112. `ide.st_asanchit_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** not saved *
- **Default (romanised Sanskrit), as printed:** `…   |   asanchit *`
- **This pack, as printed:** `…   |   ಉಳಿಸಿಲ್ಲ *`
- **This message alone:** `ಉಳಿಸಿಲ್ಲ *`
- **Correction:** 

### 113. `ide.st_notfound_w` — **DRAFT**

- **Where:** IDE status line, after Find
- **Meaning:** find: not found
- **Default (romanised Sanskrit), as printed:** `anwesh: nahi mila`
- **This pack, as printed:** `ಹುಡುಕು: ಸಿಗಲಿಲ್ಲ`
- **Correction:** 

### 114. `ide.lang_swayam_w` — **DRAFT**

- **Where:** IDE status line: language Auto
- **Meaning:** automatic (detect the script)
- **Default (romanised Sanskrit), as printed:** `   |   bhasha: swayam`
- **This pack, as printed:** `   |   ಭಾಷೆ: ಸ್ವಯಂಚಾಲಿತ`
- **This message alone:** `ಸ್ವಯಂಚಾಲಿತ`
- **Correction:** 

### 115. `ide.lang_swayam_sk_w` — **DRAFT**

- **Where:** IDE status line: Auto found Devanagari
- **Meaning:** automatic (Sanskrit)
- **Default (romanised Sanskrit), as printed:** `   |   bhasha: swayam (sanskrit)`
- **This pack, as printed:** `   |   ಭಾಷೆ: ಸ್ವಯಂಚಾಲಿತ (ಸಂಸ್ಕೃತ)`
- **This message alone:** `ಸ್ವಯಂಚಾಲಿತ (ಸಂಸ್ಕೃತ)`
- **Correction:** 

### 116. `ide.lang_mool_w` — **DRAFT**

- **Where:** IDE status line: language Core
- **Meaning:** core (Latin keywords)
- **Default (romanised Sanskrit), as printed:** `   |   bhasha: mool`
- **This pack, as printed:** `   |   ಭಾಷೆ: ಮೂಲ`
- **This message alone:** `ಮೂಲ`
- **Correction:** 

### 117. `ide.msg_ready` — **DRAFT**

- **Where:** IDE output pane, at start and after Clear shell
- **Meaning:** ready. F5 compiles and runs the program in the editor
- **Default (romanised Sanskrit), as printed:** `Taiyar. F5: sampadak ka karyakram sankalan aur chalan.⏎`
- **This pack, as printed:** `ಸಿದ್ಧ. F5: ಸಂಪಾದಕದಲ್ಲಿನ ಕಾರ್ಯಕ್ರಮವನ್ನು ಸಂಕಲಿಸಿ ಚಲಾಯಿಸುತ್ತದೆ.⏎`
- **Correction:** 

### 118. `ide.msg_compile_failed` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [compilation failed]
- **Default (romanised Sanskrit), as printed:** `[sankalan asaphal]⏎`
- **This pack, as printed:** `[ಸಂಕಲನ ವಿಫಲ]⏎`
- **Correction:** 

### 119. `ide.msg_run_failed` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the program ended abnormally]
- **Default (romanised Sanskrit), as printed:** `[karyakram asamanya roop se samapt]⏎`
- **This pack, as printed:** `[ಕಾರ್ಯಕ್ರಮ ಅಸಹಜವಾಗಿ ಮುಗಿಯಿತು]⏎`
- **Correction:** 

### 120. `ide.msg_file_failed` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [reading/writing the file failed]
- **Default (romanised Sanskrit), as printed:** `[patra padhne/likhne me asaphal]⏎`
- **This pack, as printed:** `[ಕಡತ ಓದಲು/ಬರೆಯಲು ವಿಫಲ]⏎`
- **Correction:** 

### 121. `ide.msg_input_large` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the file is too big; editor limit 64 KiB]
- **Default (romanised Sanskrit), as printed:** `[patra bahut bada; sampadak seema 64 KiB]⏎`
- **This pack, as printed:** `[ಕಡತ ತುಂಬಾ ದೊಡ್ಡದು; ಸಂಪಾದಕ ಮಿತಿ 64 KiB]⏎`
- **Correction:** 

### 122. `ide.msg_shell_limit` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the shell history is full; clear the shell first]
- **Default (romanised Sanskrit), as printed:** `[khol ka itihas purna; pahle khol rikta karein]⏎`
- **This pack, as printed:** `[ಸಂವಾದ ಇತಿಹಾಸ ತುಂಬಿದೆ; ಮೊದಲು ಸಂವಾದ ಖಾಲಿ ಮಾಡಿ]⏎`
- **Correction:** 

### 123. `ide.msg_timeout` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the process ran more than 10 seconds; stopped]
- **Default (romanised Sanskrit), as printed:** `[prakriya 10 sekand se adhik; samapt ki gayi]⏎`
- **This pack, as printed:** `[ಪ್ರಕ್ರಿಯೆ 10 ಸೆಕೆಂಡ್‌ಗಿಂತ ಹೆಚ್ಚು ನಡೆಯಿತು; ನಿಲ್ಲಿಸಲಾಗಿದೆ]⏎`
- **Correction:** 

### 124. `ide.msg_missing_compiler` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [win\sutram.exe not found: build the compiler first]
- **Default (romanised Sanskrit), as printed:** `[win\sutram.exe nahi mila: pahle sankalak banayein]⏎`
- **This pack, as printed:** `[win\sutram.exe ಸಿಗಲಿಲ್ಲ: ಮೊದಲು ಸಂಕಲಕವನ್ನು ನಿರ್ಮಿಸಿ]⏎`
- **Correction:** 

### 125. `ide.msg_missing_lang` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [native word packs unavailable: see lang\*.lang; the core words work]
- **Default (romanised Sanskrit), as printed:** `[deshi shabda-pak anupalabdh: lang\*.lang dekhein; mool shabda kaam karte hain]⏎`
- **This pack, as printed:** `[ದೇಶಿ ಪದ ಪ್ಯಾಕ್‌ಗಳು ಇಲ್ಲ: lang\*.lang ನೋಡಿ; ಮೂಲ ಪದಗಳು ಕೆಲಸ ಮಾಡುತ್ತವೆ]⏎`
- **Correction:** 

### 126. `ide.msg_partial_lang` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [some word packs unavailable or invalid: see lang\*.lang]
- **Default (romanised Sanskrit), as printed:** `[kuchh shabda-pak anupalabdh ya ashuddh: lang\*.lang dekhein]⏎`
- **This pack, as printed:** `[ಕೆಲವು ಪದ ಪ್ಯಾಕ್‌ಗಳು ಇಲ್ಲ ಅಥವಾ ಅಶುದ್ಧ: lang\*.lang ನೋಡಿ]⏎`
- **Correction:** 

### 127. `ide.msg_pipe_fail` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [creating the process or the pipe failed]
- **Default (romanised Sanskrit), as printed:** `[prakriya ya nalika nirman asaphal]⏎`
- **This pack, as printed:** `[ಪ್ರಕ್ರಿಯೆ ಅಥವಾ ಕೊಳವೆ ರಚನೆ ವಿಫಲ]⏎`
- **Correction:** 

### 128. `ide.msg_more_output` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [output cut at 32 KiB]
- **Default (romanised Sanskrit), as printed:** `[phal 32 KiB par kata]⏎`
- **This pack, as printed:** `[ಫಲಿತಾಂಶ 32 KiB ನಲ್ಲಿ ಕತ್ತರಿಸಲಾಗಿದೆ]⏎`
- **Correction:** 


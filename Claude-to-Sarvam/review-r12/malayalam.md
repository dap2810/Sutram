# Review sheet: Malayalam (മലയാളം)

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
  They go into `lang/malayalam.sandesh`.

## Levels

| Level | Meaning |
|---|---|
| **LIKELY WRONG** | I think it is wrong, or it must be decided; please correct it first |
| **UNSURE** | I have a specific doubt, written under the message |
| **DRAFT** | no specific doubt, but still unverified |

**128 messages:** 0 LIKELY WRONG, 15 UNSURE, 113 DRAFT.

| # | Message | Level |
|---|---|---|
| 3 | `r48_msg_near` | UNSURE |
| 16 | `r5_msg_field` | UNSURE |
| 22 | `r7_msg_arity2` | UNSURE |
| 23 | `r7_msg_arity3` | UNSURE |
| 40 | `r65_msg_add` | UNSURE |
| 52 | `msg_lang_ok` | UNSURE |
| 53 | `msg_lang_fail` | UNSURE |
| 54 | `msg_shell_banner` | UNSURE |
| 69 | `msg_ast_overflow` | UNSURE |
| 85 | `r55_msg_proto_signature` | UNSURE |
| 91 | `mg_e_noexp2` | UNSURE |
| 92 | `mg_e_noexp3` | UNSURE |
| 96 | `mg_e_undef2` | UNSURE |
| 101 | `mg_e_valias2` | UNSURE |
| 117 | `ide.msg_ready` | UNSURE |

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
സൂത്രം - സമ്പൂർണ്ണ സൂത്രം
ഉപയോഗം:
  sutram <ഉറവിടം.sm> <ഫലം.bin>         സമാഹരണം
  sutram --check <ഉറവിടം.sm>              പരിശോധന മാത്രം, ഫല ഫയൽ ഇല്ല
  sutram --lang <പാക്ക്> <ഉറവിടം.sm> <ഫലം.bin>  ഭാഷാ പാക്കോടെ
  sutram -i                               സംവാദം
  sutram --version                        പതിപ്പ്
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
സൂത്രം 1.0 (v182) - സമ്പൂർണ്ണ സൂത്രം
സംസ്കൃത-പ്രധാന ഭാഷ -> x86-64 യന്ത്രഭാഷ
```
- **Correction:** 

### 3. `r48_msg_near` — **UNSURE**

- **Where:** compiler: `--check`, a parse error
- **Meaning:** 'word' (the token where parsing failed)
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: shabd '=' + caret line`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: വാക്ക് '=' + caret line`
- **This message alone:** `: Sutram Error [E_PARSE]: വാക്ക് '`
- **Doubt:** 'word' stands for a token; check that it reads naturally before the quoted token.
- **Correction:** 

### 4. `r48_msg_ok` — **DRAFT**

- **Where:** compiler: `--check`, no errors
- **Meaning:** check: correct (no output file made)
- **Default (romanised Sanskrit), as printed:** `Sutram janch: shuddh (nirgat patra nahi)⏎`
- **This pack, as printed:** `സൂത്രം പരിശോധന: ശരി (ഫല ഫയൽ സൃഷ്ടിച്ചില്ല)⏎`
- **Correction:** 

### 5. `r48_msg_errors` — **DRAFT**

- **Where:** compiler: `--check`, errors found
- **Meaning:** check: errors found; no output file made
- **Default (romanised Sanskrit), as printed:** `Sutram janch: dosh mile; nirgat patra nahi⏎`
- **This pack, as printed:** `സൂത്രം പരിശോധന: പിശകുകൾ കണ്ടെത്തി; ഫല ഫയൽ സൃഷ്ടിച്ചില്ല⏎`
- **Correction:** 

### 6. `r48_msg_eof` — **DRAFT**

- **Where:** compiler: `--check`, error at end of file
- **Meaning:** <end of file>, shown in place of the token
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: shabd '<patra-ant>'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: വാക്ക് '<ഫയലിന്റെ അവസാനം>'`
- **This message alone:** `<ഫയലിന്റെ അവസാനം>`
- **Correction:** 

### 7. `r50_msg_setchar_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** akshar_rakh needs 3 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: akshar_rakh: 3 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: akshar_rakh: 3 പ്രമാണങ്ങൾ ആവശ്യം⏎`
- **In the pack file:** `Sutram Error: {kw:akshar_rakh}: 3 പ്രമാണങ്ങൾ ആവശ്യം⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 8. `r52_msg_dvaram_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** dvaram needs 2 or 3 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: dvaram: 2 va 3 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: dvaram: 2 അല്ലെങ്കിൽ 3 പ്രമാണങ്ങൾ ആവശ്യം⏎`
- **In the pack file:** `Sutram Error: {kw:dvaram}: 2 അല്ലെങ്കിൽ 3 പ്രമാണങ്ങൾ ആവശ്യം⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 9. `r52_msg_charat_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** akshar needs 2 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: akshar: 2 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: akshar: 2 പ്രമാണങ്ങൾ ആവശ്യം⏎`
- **In the pack file:** `Sutram Error: {kw:akshar}: 2 പ്രമാണങ്ങൾ ആവശ്യം⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 10. `r52_msg_charcode_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** aksharank needs 1 or 2 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: aksharank: 1 va 2 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: aksharank: 1 അല്ലെങ്കിൽ 2 പ്രമാണങ്ങൾ ആവശ്യം⏎`
- **In the pack file:** `Sutram Error: {kw:aksharank}: 1 അല്ലെങ്കിൽ 2 പ്രമാണങ്ങൾ ആവശ്യം⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 11. `r48_msg_undefined` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown function 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_FUNCTION]: agyat prakriya 'foo'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_FUNCTION]: അജ്ഞാത ക്രിയ 'foo'`
- **This message alone:** `: Sutram Error [E_UNDEFINED_FUNCTION]: അജ്ഞാത ക്രിയ '`
- **Correction:** 

### 12. `r4_msg_undef` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown name 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_NAME]: agyat naam 'y'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_NAME]: അജ്ഞാത പേര് 'y'`
- **This message alone:** `: Sutram Error [E_UNDEFINED_NAME]: അജ്ഞാത പേര് '`
- **Correction:** 

### 13. `r4_msg_hint_decl` — **DRAFT**

- **Where:** compiler: hint after an unknown name
- **Meaning:** hint: declare it before use: vitti NAME = ...
- **Default (romanised Sanskrit), as printed:** `Sanket: prayog se purv ghoshana avashyak: vitti y = ...`
- **This pack, as printed:** `സൂചന: ഉപയോഗിക്കുന്നതിന് മുമ്പ് പ്രഖ്യാപനം ആവശ്യം: ചരം y = ...`
- **This message alone:** `സൂചന: ഉപയോഗിക്കുന്നതിന് മുമ്പ് പ്രഖ്യാപനം ആവശ്യം: ചരം `
- **In the pack file:** `സൂചന: ഉപയോഗിക്കുന്നതിന് മുമ്പ് പ്രഖ്യാപനം ആവശ്യം: {kw:vitti} `  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 14. `r4_msg_hint_old` — **DRAFT**

- **Where:** compiler: hint, opens two hints
- **Meaning:** hint: 'NAME…
- **Default (romanised Sanskrit), as printed:** `Sanket: 'anyatra' purana kunjishabd (v157 se purv); navin: 'anya'`
- **This pack, as printed:** `സൂചന: 'anyatra' പഴയ കീവാക്ക് (v157 ന് മുമ്പുള്ളത്); പുതിയത്: 'anya'`
- **This message alone:** `സൂചന: '`
- **Correction:** 

### 15. `r4_msg_hint_old2` — **DRAFT**

- **Where:** compiler: hint after an old keyword
- **Meaning:** 'OLD' is an old keyword (before v157); new: 'NEW'
- **Default (romanised Sanskrit), as printed:** `Sanket: 'anyatra' purana kunjishabd (v157 se purv); navin: 'anya'`
- **This pack, as printed:** `സൂചന: 'anyatra' പഴയ കീവാക്ക് (v157 ന് മുമ്പുള്ളത്); പുതിയത്: 'anya'`
- **This message alone:** `' പഴയ കീവാക്ക് (v157 ന് മുമ്പുള്ളത്); പുതിയത്: '`
- **Correction:** 

### 16. `r5_msg_field` — **UNSURE**

- **Where:** compiler
- **Meaning:** unknown field 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_UNKNOWN_FIELD]: agyat kshetra 'q'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_UNKNOWN_FIELD]: അജ്ഞാത മണ്ഡലം 'q'`
- **This message alone:** `: Sutram Error [E_UNKNOWN_FIELD]: അജ്ഞാത മണ്ഡലം '`
- **Doubt:** 'മണ്ഡലം' for a record field is my choice; check.
- **Correction:** 

### 17. `r7_msg_dup` — **DRAFT**

- **Where:** compiler
- **Meaning:** declared again: 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_DUPLICATE_NAME]: punah ghoshana 'x'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_DUPLICATE_NAME]: വീണ്ടും പ്രഖ്യാപനം 'x'`
- **This message alone:** `: Sutram Error [E_DUPLICATE_NAME]: വീണ്ടും പ്രഖ്യാപനം '`
- **Correction:** 

### 18. `r7_msg_dup_hint` — **DRAFT**

- **Where:** compiler: hint after a duplicate
- **Meaning:** 'NAME' is already declared; to give it a new value: NAME = ...
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' pahle se ghoshit hai; naya man dene ke liye: x = ...`
- **This pack, as printed:** `സൂചന: 'x' ഇതിനകം പ്രഖ്യാപിച്ചതാണ്; പുതിയ മൂല്യം നൽകാൻ: x = ...`
- **This message alone:** `' ഇതിനകം പ്രഖ്യാപിച്ചതാണ്; പുതിയ മൂല്യം നൽകാൻ: `
- **Correction:** 

### 19. `r7_msg_field_amb` — **DRAFT**

- **Where:** compiler
- **Meaning:** field 'NAME' (is ambiguous)
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_AMBIGUOUS_FIELD]: kshetra 'x'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_AMBIGUOUS_FIELD]: മണ്ഡലം 'x'`
- **This message alone:** `: Sutram Error [E_AMBIGUOUS_FIELD]: മണ്ഡലം '`
- **Correction:** 

### 20. `r7_msg_field_amb_hint` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** 'NAME' is at different places in two rachanas; give it a different name in each
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' do rachana me alag sthan par hai; har rachana me alag naam rakhein⏎`
- **This pack, as printed:** `സൂചന: 'x' രണ്ട് ഘടനകളിൽ വ്യത്യസ്ത സ്ഥാനത്താണ്; ഓരോ ഘടനയിലും വേറെ പേര് നൽകുക⏎`
- **This message alone:** `' രണ്ട് ഘടനകളിൽ വ്യത്യസ്ത സ്ഥാനത്താണ്; ഓരോ ഘടനയിലും വേറെ പേര് നൽകുക⏎`
- **Correction:** 

### 21. `r7_msg_field_dup_hint` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** 'NAME' is already in this rachana
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' is rachana me pahle se hai⏎`
- **This pack, as printed:** `സൂചന: 'x' ഈ ഘടനയിൽ ഇതിനകം ഉണ്ട്⏎`
- **This message alone:** `' ഈ ഘടനയിൽ ഇതിനകം ഉണ്ട്⏎`
- **Correction:** 

### 22. `r7_msg_arity2` — **UNSURE**

- **Where:** compiler: middle of the arity error
- **Meaning:** 'f' [was given] N arguments; in the signature M
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' ko 1 tark diye; hastakshar me 2`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' ന് 1 പ്രമാണങ്ങൾ നൽകി; ഒപ്പിൽ 2`
- **This message alone:** `' ന് `
- **Doubt:** Word order is fixed by the code: 'NAME' <this> N <arity3> M. Check that the sentence reads naturally around the name and the two numbers.
- **Doubt:** The case suffix is printed after a space ('f' <suffix>); written Malayalam normally attaches it to the word (with a quoted code name, say which you prefer). The checker keeps the default's leading "' ", so fixing this needs that rule relaxed for this message.
- **Correction:** 

### 23. `r7_msg_arity3` — **UNSURE**

- **Where:** compiler: middle of the arity error
- **Meaning:** … N arguments given; in the signature M
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' ko 1 tark diye; hastakshar me 2`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' ന് 1 പ്രമാണങ്ങൾ നൽകി; ഒപ്പിൽ 2`
- **This message alone:** ` പ്രമാണങ്ങൾ നൽകി; ഒപ്പിൽ `
- **Doubt:** 'പ്രമാണം' for an argument is my choice; 'ഒപ്പ്' for a signature is a calque.
- **Doubt:** The count is printed before this text and is often 1 ('f' … 1 …): the noun is in the plural form, so '1 <plural>' may read wrong. A fragment cannot change with the number.
- **Correction:** 

### 24. `r7_msg_arity_hint` — **DRAFT**

- **Where:** compiler: hint after the arity error
- **Meaning:** hint: give exactly as many arguments as the function's definition has
- **Default (romanised Sanskrit), as printed:** `Sanket: utne hi tark dein jitne prakriya ki paribhasha me hain⏎`
- **This pack, as printed:** `സൂചന: ക്രിയയുടെ നിർവചനത്തിൽ എത്ര പ്രമാണങ്ങൾ ഉണ്ടോ അത്രയും നൽകുക⏎`
- **Correction:** 

### 25. `r7_msg_mod_missing` — **DRAFT**

- **Where:** compiler
- **Meaning:** import file not found: NAME
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_MISSING]: yoj patra aprapt: ganit`
- **This pack, as printed:** `Sutram Error [E_MODULE_MISSING]: ഉൾപ്പെടുത്തൽ ഫയൽ കണ്ടില്ല: ganit`
- **This message alone:** `Sutram Error [E_MODULE_MISSING]: ഉൾപ്പെടുത്തൽ ഫയൽ കണ്ടില്ല: `
- **Correction:** 

### 26. `r7_msg_mod_missing2` — **DRAFT**

- **Where:** compiler: hint after a missing import
- **Meaning:** hint: NAME.smlib should be in lib/ or in the source file's folder
- **Default (romanised Sanskrit):**

```

Sanket: lib/ me ya srot patra ki nirdeshika me naam.smlib hona chahiye
```

- **This pack, as printed:**

```

സൂചന: <പേര്>.smlib lib/ ൽ അല്ലെങ്കിൽ ഉറവിട ഫയൽ ഉള്ള സ്ഥാനത്ത് ഉണ്ടാകണം
```
- **Correction:** 

### 27. `r7_msg_hint_block` — **DRAFT**

- **Where:** compiler: hint after an unknown name
- **Meaning:** 'NAME' is declared inside a block { } or a loop; it is not visible outside it
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' ek khand { } ya chakra me ghoshit hai; uske bahar drishya nahi⏎`
- **This pack, as printed:** `സൂചന: 'x' ഒരു ഖണ്ഡം { } അല്ലെങ്കിൽ ആവർത്തനം ഉള്ളിൽ പ്രഖ്യാപിച്ചതാണ്; അതിന് പുറത്ത് കാണില്ല⏎`
- **This message alone:** `' ഒരു ഖണ്ഡം { } അല്ലെങ്കിൽ ആവർത്തനം ഉള്ളിൽ പ്രഖ്യാപിച്ചതാണ്; അതിന് പുറത്ത് കാണില്ല⏎`
- **In the pack file:** `' ഒരു ഖണ്ഡം { } അല്ലെങ്കിൽ {kw:chakra} ഉള്ളിൽ പ്രഖ്യാപിച്ചതാണ്; അതിന് പുറത്ത് കാണില്ല⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 28. `r5_msg_field_hint` — **DRAFT**

- **Where:** compiler: hint, opens the field hint
- **Meaning:** hint: 'NAME…
- **Default (romanised Sanskrit), as printed:** `Sanket: 'q' kisi rachana ka kshetra nahi⏎`
- **This pack, as printed:** `സൂചന: 'q' ഒരു ഘടനയുടെയും മണ്ഡലമല്ല⏎`
- **This message alone:** `സൂചന: '`
- **Correction:** 

### 29. `r5_msg_field_hint2` — **DRAFT**

- **Where:** compiler: hint after an unknown field
- **Meaning:** 'NAME' is not a field of any rachana
- **Default (romanised Sanskrit), as printed:** `Sanket: 'q' kisi rachana ka kshetra nahi⏎`
- **This pack, as printed:** `സൂചന: 'q' ഒരു ഘടനയുടെയും മണ്ഡലമല്ല⏎`
- **This message alone:** `' ഒരു ഘടനയുടെയും മണ്ഡലമല്ല⏎`
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

Sutram Error: വ്യാകരണ പിശക്, വരി 
```
- **Correction:** 

### 31. `msg_err_near` — **DRAFT**

- **Where:** compiler: a parse error
- **Meaning:** , word 'TOKEN'
- **Default (romanised Sanskrit), as printed:** `⏎Sutram Error: vyakaran dosh, pankti 3:11, shabd '='`
- **This pack, as printed:** `⏎Sutram Error: വ്യാകരണ പിശക്, വരി 3:11, വാക്ക് '='`
- **This message alone:** `, വാക്ക് '`
- **Correction:** 

### 32. `msg_err_eof` — **DRAFT**

- **Where:** compiler: a parse error at the end of the file
- **Meaning:** end of file, shown in place of the token
- **Default (romanised Sanskrit), as printed:** `⏎Sutram Error: vyakaran dosh, pankti 6:1, shabd 'patra-ant'`
- **This pack, as printed:** `⏎Sutram Error: വ്യാകരണ പിശക്, വരി 6:1, വാക്ക് 'ഫയലിന്റെ അവസാനം'`
- **This message alone:** `ഫയലിന്റെ അവസാനം`
- **Correction:** 

### 33. `msg_err_hint` — **DRAFT**

- **Where:** compiler: hint after a parse error
- **Meaning:** hint: check the word and the grammar at this place
- **Default (romanised Sanskrit), as printed:** `Sanket: is sthan par shabd aur vyakaran dekho.⏎`
- **This pack, as printed:** `സൂചന: ഈ സ്ഥാനത്ത് വാക്കും വ്യാകരണവും പരിശോധിക്കുക.⏎`
- **Correction:** 

### 34. `msg_err_arg_limit` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** hint: a function takes at most 6 arguments
- **Default (romanised Sanskrit), as printed:** `Sanket: prakriya adhiktam 6 tark lete hain.⏎`
- **This pack, as printed:** `സൂചന: ക്രിയ പരമാവധി 6 പ്രമാണങ്ങൾ സ്വീകരിക്കും.⏎`
- **Correction:** 

### 35. `msg_err_duplicate_func` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** hint: the function is defined twice (name clash)
- **Default (romanised Sanskrit), as printed:** `Sanket: dohri prakriya paribhasha (naam takkar).⏎`
- **This pack, as printed:** `സൂചന: ക്രിയയ്ക്ക് ഇരട്ട നിർവചനം (പേര് സംഘർഷം).⏎`
- **Correction:** 

### 36. `msg_duplicate_func` — **DRAFT**

- **Where:** compiler
- **Meaning:** function defined again: NAME
- **Default (romanised Sanskrit), as printed:** `Sutram Error: punah prakriya paribhasha: f`
- **This pack, as printed:** `Sutram Error: ക്രിയയ്ക്ക് വീണ്ടും നിർവചനം: f`
- **This message alone:** `Sutram Error: ക്രിയയ്ക്ക് വീണ്ടും നിർവചനം: `
- **Correction:** 

### 37. `msg_undefined_func` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown function: NAME
- **Default (romanised Sanskrit), as printed:** `Sutram Error: agyat prakriya: f`
- **This pack, as printed:** `Sutram Error: അജ്ഞാത ക്രിയ: f`
- **This message alone:** `Sutram Error: അജ്ഞാത ക്രിയ: `
- **Correction:** 

### 38. `msg_array_oob` — **DRAFT**

- **Where:** the compiled program, at run time
- **Meaning:** mala index out of bounds
- **Default (romanised Sanskrit), as printed:** `Sutram Error: mala ank seema atikram⏎`
- **This pack, as printed:** `Sutram Error: വരി സൂചിക പരിധിക്ക് പുറത്ത്⏎`
- **In the pack file:** `Sutram Error: {kw:mala} സൂചിക പരിധിക്ക് പുറത്ത്⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 39. `msg_kosh_required` — **DRAFT**

- **Where:** compiler
- **Meaning:** a kosh function needs a kosh variable
- **Default (romanised Sanskrit), as printed:** `Sutram Error: kosh prakriya hetu kosh-vitti avashyak⏎`
- **This pack, as printed:** `Sutram Error: കോശം ക്രിയയ്ക്ക് കോശം ചരം ആവശ്യം⏎`
- **In the pack file:** `Sutram Error: {kw:kosh} ക്രിയയ്ക്ക് {kw:kosh} {kw:vitti} ആവശ്യം⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 40. `r65_msg_add` — **UNSURE**

- **Where:** the program, `trap` build
- **Meaning:** overflow in an addition
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: yog atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: സങ്കലനത്തിൽ കവിഞ്ഞൊഴുക്ക്⏎`
- **This message alone:** `: സങ്കലനത്തിൽ കവിഞ്ഞൊഴുക്ക്⏎`
- **Doubt:** 'കവിഞ്ഞൊഴുക്ക്' for an integer overflow (all seven trap messages); check.
- **Correction:** 

### 41. `r65_msg_sub` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a subtraction
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: nyun atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: വ്യവകലനത്തിൽ കവിഞ്ഞൊഴുക്ക്⏎`
- **This message alone:** `: വ്യവകലനത്തിൽ കവിഞ്ഞൊഴുക്ക്⏎`
- **Correction:** 

### 42. `r65_msg_mul` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a multiplication
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: gun atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: ഗുണനത്തിൽ കവിഞ്ഞൊഴുക്ക്⏎`
- **This message alone:** `: ഗുണനത്തിൽ കവിഞ്ഞൊഴുക്ക്⏎`
- **Correction:** 

### 43. `r65_msg_div` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** division by zero
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: shunya se bhajan⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: പൂജ്യം കൊണ്ട് ഹരണം⏎`
- **This message alone:** `: പൂജ്യം കൊണ്ട് ഹരണം⏎`
- **Correction:** 

### 44. `r65_msg_mod` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** remainder by zero
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: shunya se shesh⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: പൂജ്യം കൊണ്ട് ശിഷ്ടം⏎`
- **This message alone:** `: പൂജ്യം കൊണ്ട് ശിഷ്ടം⏎`
- **Correction:** 

### 45. `r65_msg_div_overflow` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a division
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: bhajan atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: ഹരണത്തിൽ കവിഞ്ഞൊഴുക്ക്⏎`
- **This message alone:** `: ഹരണത്തിൽ കവിഞ്ഞൊഴുക്ക്⏎`
- **Correction:** 

### 46. `r65_msg_mod_overflow` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a remainder
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: shesh atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: ശിഷ്ടത്തിൽ കവിഞ്ഞൊഴുക്ക്⏎`
- **This message alone:** `: ശിഷ്ടത്തിൽ കവിഞ്ഞൊഴുക്ക്⏎`
- **Correction:** 

### 47. `msg_kosh_empty` — **DRAFT**

- **Where:** the program, at run time
- **Meaning:** kosh_pop from an empty kosh
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rikta kosh se kosh_pop⏎`
- **This pack, as printed:** `Sutram Error: ശൂന്യമായ കോശത്തിൽ നിന്ന് kosh_pop⏎`
- **In the pack file:** `Sutram Error: ശൂന്യമായ കോശത്തിൽ നിന്ന് {kw:kosh_pop}⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 48. `msg_kosh_peek_empty` — **DRAFT**

- **Where:** the program, at run time
- **Meaning:** kosh_peek from an empty kosh
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rikta kosh se kosh_peek⏎`
- **This pack, as printed:** `Sutram Error: ശൂന്യമായ കോശത്തിൽ നിന്ന് kosh_peek⏎`
- **In the pack file:** `Sutram Error: ശൂന്യമായ കോശത്തിൽ നിന്ന് {kw:kosh_peek}⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 49. `msg_kosh_dequeue_empty` — **DRAFT**

- **Where:** the program, at run time
- **Meaning:** kosh_dequeue from an empty kosh
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rikta kosh se kosh_dequeue⏎`
- **This pack, as printed:** `Sutram Error: ശൂന്യമായ കോശത്തിൽ നിന്ന് kosh_dequeue⏎`
- **In the pack file:** `Sutram Error: ശൂന്യമായ കോശത്തിൽ നിന്ന് {kw:kosh_dequeue}⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 50. `msg_kosh_param_type` — **DRAFT**

- **Where:** compiler
- **Meaning:** kosh argument: element type differs
- **Default (romanised Sanskrit), as printed:** `Sutram Error: kosh tark: tatv prakar bhinn⏎`
- **This pack, as printed:** `Sutram Error: കോശ പ്രമാണം: ഘടകത്തിന്റെ തരം വ്യത്യസ്തം⏎`
- **Correction:** 

### 51. `msg_kosh_param_push` — **DRAFT**

- **Where:** compiler
- **Meaning:** kosh_push is not supported on a kosh argument
- **Default (romanised Sanskrit), as printed:** `Sutram Error: kosh tark par kosh_push asamarthit⏎`
- **This pack, as printed:** `Sutram Error: കോശ പ്രമാണത്തിൽ kosh_push പിന്തുണയില്ല⏎`
- **In the pack file:** `Sutram Error: കോശ പ്രമാണത്തിൽ {kw:kosh_push} പിന്തുണയില്ല⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 52. `msg_lang_ok` — **UNSURE**

- **Where:** compiler: every run with `--lang`
- **Meaning:** language pack found: PACK
- **Default (romanised Sanskrit), as printed:** `Bhasha pak prapt: hindi`
- **This pack, as printed:** `ഭാഷാ പാക്ക് കണ്ടെത്തി: hindi`
- **This message alone:** `ഭാഷാ പാക്ക് കണ്ടെത്തി: `
- **Doubt:** 'pack' (the language-pack file) has no settled native word; check the term.
- **Correction:** 

### 53. `msg_lang_fail` — **UNSURE**

- **Where:** compiler
- **Meaning:** warning: language pack not found: PACK
- **Default (romanised Sanskrit), as printed:** `Chetavani: bhasha pak nahi mila: hindi`
- **This pack, as printed:** `മുന്നറിയിപ്പ്: ഭാഷാ പാക്ക് കണ്ടില്ല: hindi`
- **This message alone:** `മുന്നറിയിപ്പ്: ഭാഷാ പാക്ക് കണ്ടില്ല: `
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
സൂത്രം സംവാദം v1.0 - സമ്പൂർണ്ണ സൂത്രം
സൂത്രം വാക്യം എഴുതി Enter അമർത്തുക. ഉടൻ പ്രവർത്തിക്കും.
കൽപ്പനകൾ: sahayata (സഹായം) | nirgat (പുറത്തുകടക്കുക) | sarvam (എല്ലാം കാണുക)
```
- **Doubt:** 'Enter' is kept as the key's label; the verb for pressing a key should be checked.
- **Correction:** 

### 55. `msg_shell_bye` — **DRAFT**

- **Where:** compiler: leaving `sutram -i`
- **Meaning:** greeting; session ended
- **Default (romanised Sanskrit), as printed:** `Namaste! Satra samapt.⏎`
- **This pack, as printed:** `നമസ്കാരം! സംവാദം അവസാനിച്ചു.⏎`
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
സൂത്രം സംവാദ സഹായം:
  എഴുതു("നമസ്കാരം\n")            വാചകം എഴുതുന്നു
  ചരം x = 5             ചരം പ്രഖ്യാപനം
  എഴുതു(x + 3)            മൂല്യം എഴുതുന്നു
  ആവർത്തനം i = 0 മുതൽ 5 { എഴുതു(i) }   ആവർത്തനം
  വരി arr[5]             വരി പ്രഖ്യാപനം
  sarvam                  മുഴുവൻ കാര്യക്രമവും കാണുക
  nirgat                  സംവാദത്തിൽ നിന്ന് പുറത്തുകടക്കുക
```
- **In the pack file:** `സൂത്രം സംവാദ സഹായം:⏎  {kw:likha}("നമസ്കാരം\n")            വാചകം എഴുതുന്നു⏎  {kw:vitti} x = 5             {kw:vitti} പ്രഖ്യാപനം⏎  {kw:likha}(x + 3)            മൂല്യം എഴുതുന്നു⏎  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   ആവർത്തനം⏎  {kw:mala} arr[5]             {kw:mala} പ്രഖ്യാപനം⏎  sarvam                  മുഴുവൻ കാര്യക്രമവും കാണുക⏎  nirgat                  സംവാദത്തിൽ നിന്ന് പുറത്തുകടക്കുക⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 57. `msg_open_err` — **DRAFT**

- **Where:** compiler
- **Meaning:** input (source) file not found
- **Default (romanised Sanskrit), as printed:** `Sutram Error: nivesh patra aprapt⏎`
- **This pack, as printed:** `Sutram Error: ഉറവിട ഫയൽ കണ്ടില്ല⏎`
- **Correction:** 

### 58. `msg_ok` — **DRAFT**

- **Where:** compiler: a successful compile
- **Meaning:** done: N bytes compiled
- **Default (romanised Sanskrit), as printed:** `Siddh: 297 baait sankalit⏎`
- **This pack, as printed:** `വിജയം: 297 ബൈറ്റ് സമാഹരിച്ചു⏎`
- **This message alone:** `വിജയം: `
- **Correction:** 

### 59. `msg_bytes` — **DRAFT**

- **Where:** compiler: a successful compile
- **Meaning:** … bytes compiled
- **Default (romanised Sanskrit), as printed:** `Siddh: 297 baait sankalit⏎`
- **This pack, as printed:** `വിജയം: 297 ബൈറ്റ് സമാഹരിച്ചു⏎`
- **This message alone:** ` ബൈറ്റ് സമാഹരിച്ചു⏎`
- **Correction:** 

### 60. `msg_namespace_error` — **DRAFT**

- **Where:** compiler
- **Meaning:** invalid import (form: module@alias, alias up to 31 bytes)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ashuddh yoj (roop: ghatak@upanaam, upanaam 31 baait tak)⏎`
- **This pack, as printed:** `Sutram Error: അശുദ്ധ ഉൾപ്പെടുത്തുക (രൂപം: ഘടകം@ഉപനാമം, ഉപനാമം 31 ബൈറ്റ് വരെ)⏎`
- **In the pack file:** `Sutram Error: അശുദ്ധ {kw:yoj} (രൂപം: ഘടകം@ഉപനാമം, ഉപനാമം 31 ബൈറ്റ് വരെ)⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 61. `msg_namespace_module_missing` — **DRAFT**

- **Where:** compiler
- **Meaning:** module file not found
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ghatak patra aprapt⏎`
- **This pack, as printed:** `Sutram Error: ഘടക ഫയൽ കണ്ടില്ല⏎`
- **Correction:** 

### 62. `msg_namespace_alias_reuse` — **DRAFT**

- **Where:** compiler
- **Meaning:** alias already used (for another module)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: upanaam purv-niyukt (anya ghatak)⏎`
- **This pack, as printed:** `Sutram Error: ഉപനാമം ഇതിനകം ഉപയോഗത്തിലാണ് (മറ്റൊരു ഘടകത്തിന്)⏎`
- **Correction:** 

### 63. `r51_alias_conflict` — **DRAFT**

- **Where:** compiler
- **Meaning:** alias already used (for another module)
- **Default (romanised Sanskrit), as printed:** `prog.sm:2: Sutram Error [E_MODULE_ALIAS_REUSE]: upanaam purv-niyukt (anya ghatak)⏎`
- **This pack, as printed:** `prog.sm:2: Sutram Error [E_MODULE_ALIAS_REUSE]: ഉപനാമം ഇതിനകം ഉപയോഗത്തിലാണ് (മറ്റൊരു ഘടകത്തിന്)⏎`
- **This message alone:** `: Sutram Error [E_MODULE_ALIAS_REUSE]: ഉപനാമം ഇതിനകം ഉപയോഗത്തിലാണ് (മറ്റൊരു ഘടകത്തിന്)⏎`
- **Correction:** 

### 64. `msg_namespace_func_limit` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of module function names exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ghatak prakriya-naam seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ഘടകത്തിന്റെ ക്രിയ-നാമ പരിധി കവിഞ്ഞു⏎`
- **Correction:** 

### 65. `msg_import_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the expanded source exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: vistarit srot seema atikram⏎`
- **This pack, as printed:** `Sutram Error: വികസിപ്പിച്ച ഉറവിട പരിധി കവിഞ്ഞു⏎`
- **Correction:** 

### 66. `graph_cycle_prefix` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** import cycle: a -> b -> a
- **Default (romanised Sanskrit), as printed:** `prog.sm:1: Sutram Error [E_MODULE_CYCLE] yoj chakra: a -> b -> a`
- **This pack, as printed:** `prog.sm:1: Sutram Error [E_MODULE_CYCLE] ഉൾപ്പെടുത്തൽ ചക്രം: a -> b -> a`
- **This message alone:** `ഉൾപ്പെടുത്തൽ ചക്രം: `
- **Correction:** 

### 67. `graph_missing_prefix` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** import file not found: NAME
- **Default (romanised Sanskrit), as printed:** `prog.sm:1: Sutram Error [E_MODULE_MISSING] yoj patra aprapt: ganit`
- **This pack, as printed:** `prog.sm:1: Sutram Error [E_MODULE_MISSING] ഉൾപ്പെടുത്തൽ ഫയൽ കണ്ടില്ല: ganit`
- **This message alone:** `ഉൾപ്പെടുത്തൽ ഫയൽ കണ്ടില്ല: `
- **Correction:** 

### 68. `graph_invalid_prefix` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** invalid module name
- **Default (romanised Sanskrit), as printed:** `prog.sm:1: Sutram Error [E_MODULE_INVALID] ashuddh ghatak naam`
- **This pack, as printed:** `prog.sm:1: Sutram Error [E_MODULE_INVALID] അശുദ്ധ ഘടക നാമം`
- **This message alone:** `അശുദ്ധ ഘടക നാമം`
- **Correction:** 

### 69. `msg_ast_overflow` — **UNSURE**

- **Where:** compiler
- **Meaning:** limit of the syntax tree exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: vakya-vriksh seema atikram⏎`
- **This pack, as printed:** `Sutram Error: വാക്യവൃക്ഷ പരിധി കവിഞ്ഞു⏎`
- **Doubt:** 'syntax tree' is a coined technical term here; check it.
- **Correction:** 

### 70. `msg_func_params_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the function parameter list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya tark-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ക്രിയ പ്രമാണം-പട്ടിക പരിധി കവിഞ്ഞു⏎`
- **Correction:** 

### 71. `msg_var_table_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the variable list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: vitti-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ചരം പട്ടിക പരിധി കവിഞ്ഞു⏎`
- **In the pack file:** `Sutram Error: {kw:vitti} പട്ടിക പരിധി കവിഞ്ഞു⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 72. `msg_func_table_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the function list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ക്രിയ പട്ടിക പരിധി കവിഞ്ഞു⏎`
- **Correction:** 

### 73. `msg_patch_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the call list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: aahvan-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: വിളി പട്ടിക പരിധി കവിഞ്ഞു⏎`
- **Correction:** 

### 74. `msg_func_defs_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the function definition list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya paribhasha-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ക്രിയ നിർവചന-പട്ടിക പരിധി കവിഞ്ഞു⏎`
- **Correction:** 

### 75. `msg_r9_guna_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** guna limit exceeded (1024)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: guna seema atikram (1024)⏎`
- **This pack, as printed:** `Sutram Error: ഗുണം പരിധി കവിഞ്ഞു (1024)⏎`
- **In the pack file:** `Sutram Error: {kw:guna} പരിധി കവിഞ്ഞു (1024)⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 76. `msg_break_patch_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** too many krama (break) in a loop
- **Default (romanised Sanskrit), as printed:** `Sutram Error: chakra me krama seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ആവർത്തനം ഉള്ളിൽ ക്രമം പരിധി കവിഞ്ഞു⏎`
- **In the pack file:** `Sutram Error: {kw:chakra} ഉള്ളിൽ {kw:krama} പരിധി കവിഞ്ഞു⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 77. `msg_continue_patch_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** too many agrim (continue) in a loop
- **Default (romanised Sanskrit), as printed:** `Sutram Error: chakra me agrim seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ആവർത്തനം ഉള്ളിൽ തുടരുക പരിധി കവിഞ്ഞു⏎`
- **In the pack file:** `Sutram Error: {kw:chakra} ഉള്ളിൽ {kw:agrim} പരിധി കവിഞ്ഞു⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 78. `msg_code_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the machine code exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: yantra-bhasha seema atikram⏎`
- **This pack, as printed:** `Sutram Error: യന്ത്രഭാഷ പരിധി കവിഞ്ഞു⏎`
- **Correction:** 

### 79. `msg_rachana_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the rachana list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rachana-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ഘടന പട്ടിക പരിധി കവിഞ്ഞു⏎`
- **In the pack file:** `Sutram Error: {kw:rachana} പട്ടിക പരിധി കവിഞ്ഞു⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 80. `msg_rachana_fields_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of rachana fields exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rachana kshetra seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ഘടന മണ്ഡല പരിധി കവിഞ്ഞു⏎`
- **In the pack file:** `Sutram Error: {kw:rachana} മണ്ഡല പരിധി കവിഞ്ഞു⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 81. `msg_block_nesting_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of block depth exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: khand gahrai seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ഖണ്ഡ ആഴ പരിധി കവിഞ്ഞു⏎`
- **Correction:** 

### 82. `msg_block_stmt_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of statements in a block exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: khand kathan seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ഖണ്ഡത്തിലെ വാക്യ പരിധി കവിഞ്ഞു⏎`
- **Correction:** 

### 83. `r55_msg_proto_duplicate` — **DRAFT**

- **Where:** compiler
- **Meaning:** function forward-declared again
- **Default (romanised Sanskrit), as printed:** `Sutram Error: punah prakriya purv-ghoshana⏎`
- **This pack, as printed:** `Sutram Error: ക്രിയയ്ക്ക് വീണ്ടും മുൻ-പ്രഖ്യാപനം⏎`
- **Correction:** 

### 84. `r55_msg_proto_missing` — **DRAFT**

- **Where:** compiler
- **Meaning:** function forward-declared but never defined
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya purv-ghoshana paribhasha-rahit⏎`
- **This pack, as printed:** `Sutram Error: ക്രിയയ്ക്ക് മുൻ-പ്രഖ്യാപനം ഉണ്ട്, നിർവചനം ഇല്ല⏎`
- **Correction:** 

### 85. `r55_msg_proto_signature` — **UNSURE**

- **Where:** compiler
- **Meaning:** forward declaration and definition differ (arguments/type)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya purv-ghoshana va paribhasha bhinn (tark/prakar)⏎`
- **This pack, as printed:** `Sutram Error: ക്രിയയുടെ മുൻ-പ്രഖ്യാപനവും നിർവചനവും വ്യത്യസ്തം (പ്രമാണം/തരം)⏎`
- **Doubt:** 'forward declaration' (a prototype) is a coined term; check it.
- **Correction:** 

### 86. `r55_msg_proto_capacity` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of function forward declarations exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya purv-ghoshana seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ക്രിയ മുൻ-പ്രഖ്യാപന പരിധി കവിഞ്ഞു⏎`
- **Correction:** 

### 87. `r56_msg_global_capacity` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of module-level variables exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ghatak-star vitti seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ഘടക-തല ചരം പരിധി കവിഞ്ഞു⏎`
- **In the pack file:** `Sutram Error: ഘടക-തല {kw:vitti} പരിധി കവിഞ്ഞു⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 88. `r56_msg_global_duplicate` — **DRAFT**

- **Where:** compiler
- **Meaning:** module-level variable name declared again
- **Default (romanised Sanskrit), as printed:** `Sutram Error: punah ghatak-star vitti naam⏎`
- **This pack, as printed:** `Sutram Error: ഘടക-തല ചരം പേര് വീണ്ടും⏎`
- **In the pack file:** `Sutram Error: ഘടക-തല {kw:vitti} പേര് വീണ്ടും⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 89. `r56_msg_patch_capacity` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of global value references exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: sarvatrik mulya sandarbh seema atikram⏎`
- **This pack, as printed:** `Sutram Error: സാർവത്രിക മൂല്യ പരാമർശ പരിധി കവിഞ്ഞു⏎`
- **Correction:** 

### 90. `mg_e_cycle` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** import cycle: a -> b -> a
- **Default (romanised Sanskrit), as printed:** `prog.sm:1:Sutram Error [E_MODULE_CYCLE]: yoj chakra: a -> b -> a`
- **This pack, as printed:** `prog.sm:1:Sutram Error [E_MODULE_CYCLE]: ഉൾപ്പെടുത്തൽ ചക്രം: a -> b -> a`
- **This message alone:** `Sutram Error [E_MODULE_CYCLE]: ഉൾപ്പെടുത്തൽ ചക്രം: `
- **Correction:** 

### 91. `mg_e_noexp2` — **UNSURE**

- **Where:** compiler: middle of 'not exported'
- **Meaning:** 'SYM' [from] module 'MOD' [is] not exported
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' ghatak 'vec' se aniryat⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' ഘടകം 'vec' ൽ നിന്ന് കയറ്റുമതി ചെയ്തിട്ടില്ല⏎`
- **This message alone:** `' ഘടകം '`
- **Doubt:** Order fixed by the code: 'SYM' <this> 'MOD' <noexp3>. Check that 'SYM … MOD … not exported' reads as one sentence.
- **Correction:** 

### 92. `mg_e_noexp3` — **UNSURE**

- **Where:** compiler: end of 'not exported'
- **Meaning:** … not exported from module MOD
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' ghatak 'vec' se aniryat⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' ഘടകം 'vec' ൽ നിന്ന് കയറ്റുമതി ചെയ്തിട്ടില്ല⏎`
- **This message alone:** `' ൽ നിന്ന് കയറ്റുമതി ചെയ്തിട്ടില്ല⏎`
- **Doubt:** The case suffix is printed after a space ('f' <suffix>); written Malayalam normally attaches it to the word (with a quoted code name, say which you prefer). The checker keeps the default's leading "' ", so fixing this needs that rule relaxed for this message.
- **Correction:** 

### 93. `mg_e_dupexp1` — **DRAFT**

- **Where:** compiler
- **Meaning:** exported again: 'SYM', module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: punah niryat 'thing', ghatak 'dup'`
- **This pack, as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: വീണ്ടും കയറ്റുമതി 'thing', ഘടകം 'dup'`
- **This message alone:** `Sutram Error [E_MODULE_DUP_EXPORT]: വീണ്ടും കയറ്റുമതി '`
- **Correction:** 

### 94. `mg_e_dupexp2` — **DRAFT**

- **Where:** compiler: middle
- **Meaning:** …, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: punah niryat 'thing', ghatak 'dup'`
- **This pack, as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: വീണ്ടും കയറ്റുമതി 'thing', ഘടകം 'dup'`
- **This message alone:** `', ഘടകം '`
- **Correction:** 

### 95. `mg_e_undef1` — **DRAFT**

- **Where:** compiler
- **Meaning:** export 'SYM' has no definition, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: niryat 'thing' paribhasha-rahit, ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: കയറ്റുമതി 'thing' ന് നിർവചനം ഇല്ല, ഘടകം 'vec'`
- **This message alone:** `Sutram Error [E_EXPORT_UNDEFINED]: കയറ്റുമതി '`
- **Correction:** 

### 96. `mg_e_undef2` — **UNSURE**

- **Where:** compiler: middle
- **Meaning:** … has no definition, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: niryat 'thing' paribhasha-rahit, ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: കയറ്റുമതി 'thing' ന് നിർവചനം ഇല്ല, ഘടകം 'vec'`
- **This message alone:** `' ന് നിർവചനം ഇല്ല, ഘടകം '`
- **Doubt:** The case suffix is printed after a space ('f' <suffix>); written Malayalam normally attaches it to the word (with a quoted code name, say which you prefer). The checker keeps the default's leading "' ", so fixing this needs that rule relaxed for this message.
- **Correction:** 

### 97. `mg_e_unknown1` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown symbol 'SYM', module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: agyat sanket 'thing', ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: അജ്ഞാത ചിഹ്നം 'thing', ഘടകം 'vec'`
- **This message alone:** `Sutram Error [E_EXPORT_UNDEFINED]: അജ്ഞാത ചിഹ്നം '`
- **Correction:** 

### 98. `mg_e_unknown2` — **DRAFT**

- **Where:** compiler: middle
- **Meaning:** …, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: agyat sanket 'thing', ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: അജ്ഞാത ചിഹ്നം 'thing', ഘടകം 'vec'`
- **This message alone:** `', ഘടകം '`
- **Correction:** 

### 99. `mg_e_depth` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of import depth exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_DEPTH]: yoj gahrai seema atikram⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_DEPTH]: ഉൾപ്പെടുത്തൽ ആഴ പരിധി കവിഞ്ഞു⏎`
- **Correction:** 

### 100. `mg_e_valias1` — **DRAFT**

- **Where:** compiler
- **Meaning:** a v1 module 'MOD' needs an alias: yoj MOD@upanaam
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 ghatak 'vec' upanaam avashyak: yoj vec@upanaam`
- **This pack, as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 ഘടകം 'vec' ന് ഉപനാമം ആവശ്യം: ഉൾപ്പെടുത്തുക vec@upanaam`
- **This message alone:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 ഘടകം '`
- **Correction:** 

### 101. `mg_e_valias2` — **UNSURE**

- **Where:** compiler: middle
- **Meaning:** … needs an alias: yoj MOD@upanaam
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 ghatak 'vec' upanaam avashyak: yoj vec@upanaam`
- **This pack, as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 ഘടകം 'vec' ന് ഉപനാമം ആവശ്യം: ഉൾപ്പെടുത്തുക vec@upanaam`
- **This message alone:** `' ന് ഉപനാമം ആവശ്യം: ഉൾപ്പെടുത്തുക `
- **In the pack file:** `' ന് ഉപനാമം ആവശ്യം: {kw:yoj} `  (`{kw:…}` is the pack's own keyword)
- **Doubt:** The case suffix is printed after a space ('f' <suffix>); written Malayalam normally attaches it to the word (with a quoted code name, say which you prefer). The checker keeps the default's leading "' ", so fixing this needs that rule relaxed for this message.
- **Correction:** 

### 102. `mg_e_limit` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of modules/imports exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_LIMIT]: ghatak/yoj seema atikram⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_LIMIT]: ഘടകം/ഉൾപ്പെടുത്തൽ പരിധി കവിഞ്ഞു⏎`
- **Correction:** 

### 103. `r66_msg_bad_utf8` — **DRAFT**

- **Where:** compiler
- **Meaning:** invalid or broken Indian-script name
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_UTF8]: ashuddh ya khandit bharatiya naam⏎`
- **This pack, as printed:** `Sutram Error [E_UTF8]: അശുദ്ധമോ മുറിഞ്ഞതോ ആയ ഭാരതീയ നാമം⏎`
- **Correction:** 

### 104. `r68_utf8_tail` — **DRAFT**

- **Where:** compiler
- **Meaning:** invalid or broken UTF-8 in the source
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_UTF8]: prog.sm:2: srot me ashuddh ya khandit UTF-8⏎`
- **This pack, as printed:** `Sutram Error [E_UTF8]: prog.sm:2: ഉറവിടത്തിൽ അശുദ്ധമോ മുറിഞ്ഞതോ ആയ UTF-8⏎`
- **This message alone:** `: ഉറവിടത്തിൽ അശുദ്ധമോ മുറിഞ്ഞതോ ആയ UTF-8⏎`
- **Correction:** 

### 105. `r68_value_tail` — **DRAFT**

- **Where:** compiler
- **Meaning:** an abbreviation is not a value: 'वि॰'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_ABBREVIATION_VALUE]: prog.sm:2: sankshep shabd mulya nahi: 'वि॰'`
- **This pack, as printed:** `Sutram Error [E_ABBREVIATION_VALUE]: prog.sm:2: സംക്ഷേപ വാക്ക് മൂല്യമല്ല: 'वि॰'`
- **This message alone:** `: സംക്ഷേപ വാക്ക് മൂല്യമല്ല: '`
- **Correction:** 

### 106. `ide.st_pankti_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** line N (start of the status line)
- **Default (romanised Sanskrit), as printed:** `pankti 12   stambh 4   |   bhasha: …`
- **This pack, as printed:** `വരി 12   നിര 4   |   ഭാഷ: …`
- **This message alone:** `വരി `
- **Correction:** 

### 107. `ide.st_stambh_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** column N
- **Default (romanised Sanskrit), as printed:** `pankti 12   stambh 4   |   bhasha: …`
- **This pack, as printed:** `വരി 12   നിര 4   |   ഭാഷ: …`
- **This message alone:** `   നിര `
- **Correction:** 

### 108. `ide.st_bhasha_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** | language: NAME
- **Default (romanised Sanskrit), as printed:** `…4   |   bhasha: हिन्दी`
- **This pack, as printed:** `…4   |   ഭാഷ: हिन्दी`
- **This message alone:** `   |   ഭാഷ: `
- **Correction:** 

### 109. `ide.st_akshara_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** | letters (clusters): N
- **Default (romanised Sanskrit), as printed:** `…   |   akshara: 26`
- **This pack, as printed:** `…   |   അക്ഷരങ്ങൾ: 26`
- **This message alone:** `   |   അക്ഷരങ്ങൾ: `
- **Correction:** 

### 110. `ide.st_lipi_w` — **DRAFT**

- **Where:** IDE status line, typing mode on
- **Meaning:** | script: NAME (the typing script)
- **Default (romanised Sanskrit), as printed:** `…   |   lipi: தமிழ்`
- **This pack, as printed:** `…   |   ലിപി: தமிழ்`
- **This message alone:** `   |   ലിപി: `
- **Correction:** 

### 111. `ide.st_sanchit_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** saved
- **Default (romanised Sanskrit), as printed:** `…   |   sanchit`
- **This pack, as printed:** `…   |   സംരക്ഷിച്ചു`
- **This message alone:** `സംരക്ഷിച്ചു`
- **Correction:** 

### 112. `ide.st_asanchit_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** not saved *
- **Default (romanised Sanskrit), as printed:** `…   |   asanchit *`
- **This pack, as printed:** `…   |   സംരക്ഷിച്ചിട്ടില്ല *`
- **This message alone:** `സംരക്ഷിച്ചിട്ടില്ല *`
- **Correction:** 

### 113. `ide.st_notfound_w` — **DRAFT**

- **Where:** IDE status line, after Find
- **Meaning:** find: not found
- **Default (romanised Sanskrit), as printed:** `anwesh: nahi mila`
- **This pack, as printed:** `തിരയൽ: കണ്ടില്ല`
- **Correction:** 

### 114. `ide.lang_swayam_w` — **DRAFT**

- **Where:** IDE status line: language Auto
- **Meaning:** automatic (detect the script)
- **Default (romanised Sanskrit), as printed:** `   |   bhasha: swayam`
- **This pack, as printed:** `   |   ഭാഷ: സ്വയം`
- **This message alone:** `സ്വയം`
- **Correction:** 

### 115. `ide.lang_swayam_sk_w` — **DRAFT**

- **Where:** IDE status line: Auto found Devanagari
- **Meaning:** automatic (Sanskrit)
- **Default (romanised Sanskrit), as printed:** `   |   bhasha: swayam (sanskrit)`
- **This pack, as printed:** `   |   ഭാഷ: സ്വയം (സംസ്കൃതം)`
- **This message alone:** `സ്വയം (സംസ്കൃതം)`
- **Correction:** 

### 116. `ide.lang_mool_w` — **DRAFT**

- **Where:** IDE status line: language Core
- **Meaning:** core (Latin keywords)
- **Default (romanised Sanskrit), as printed:** `   |   bhasha: mool`
- **This pack, as printed:** `   |   ഭാഷ: മൂലം`
- **This message alone:** `മൂലം`
- **Correction:** 

### 117. `ide.msg_ready` — **UNSURE**

- **Where:** IDE output pane, at start and after Clear shell
- **Meaning:** ready. F5 compiles and runs the program in the editor
- **Default (romanised Sanskrit), as printed:** `Taiyar. F5: sampadak ka karyakram sankalan aur chalan.⏎`
- **This pack, as printed:** `തയ്യാർ. F5: സമ്പാദകത്തിലെ കാര്യക്രമം സമാഹരിച്ച് പ്രവർത്തിപ്പിക്കുന്നു.⏎`
- **Doubt:** 'സമ്പാദകം' for the editor is my coinage; check.
- **Correction:** 

### 118. `ide.msg_compile_failed` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [compilation failed]
- **Default (romanised Sanskrit), as printed:** `[sankalan asaphal]⏎`
- **This pack, as printed:** `[സമാഹരണം പരാജയപ്പെട്ടു]⏎`
- **Correction:** 

### 119. `ide.msg_run_failed` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the program ended abnormally]
- **Default (romanised Sanskrit), as printed:** `[karyakram asamanya roop se samapt]⏎`
- **This pack, as printed:** `[കാര്യക്രമം അസാധാരണമായി അവസാനിച്ചു]⏎`
- **Correction:** 

### 120. `ide.msg_file_failed` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [reading/writing the file failed]
- **Default (romanised Sanskrit), as printed:** `[patra padhne/likhne me asaphal]⏎`
- **This pack, as printed:** `[ഫയൽ വായിക്കാൻ/എഴുതാൻ കഴിഞ്ഞില്ല]⏎`
- **Correction:** 

### 121. `ide.msg_input_large` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the file is too big; editor limit 64 KiB]
- **Default (romanised Sanskrit), as printed:** `[patra bahut bada; sampadak seema 64 KiB]⏎`
- **This pack, as printed:** `[ഫയൽ വളരെ വലുത്; പരിധി 64 KiB]⏎`
- **Correction:** 

### 122. `ide.msg_shell_limit` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the shell history is full; clear the shell first]
- **Default (romanised Sanskrit), as printed:** `[khol ka itihas purna; pahle khol rikta karein]⏎`
- **This pack, as printed:** `[സംവാദ ചരിത്രം നിറഞ്ഞു; ആദ്യം സംവാദം ശൂന്യമാക്കുക]⏎`
- **Correction:** 

### 123. `ide.msg_timeout` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the process ran more than 10 seconds; stopped]
- **Default (romanised Sanskrit), as printed:** `[prakriya 10 sekand se adhik; samapt ki gayi]⏎`
- **This pack, as printed:** `[പ്രക്രിയ 10 സെക്കൻഡിൽ കൂടുതൽ ഓടി; നിർത്തി]⏎`
- **Correction:** 

### 124. `ide.msg_missing_compiler` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [win\sutram.exe not found: build the compiler first]
- **Default (romanised Sanskrit), as printed:** `[win\sutram.exe nahi mila: pahle sankalak banayein]⏎`
- **This pack, as printed:** `[win\sutram.exe കണ്ടില്ല: ആദ്യം സമാഹാരകം നിർമ്മിക്കുക]⏎`
- **Correction:** 

### 125. `ide.msg_missing_lang` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [native word packs unavailable: see lang\*.lang; the core words work]
- **Default (romanised Sanskrit), as printed:** `[deshi shabda-pak anupalabdh: lang\*.lang dekhein; mool shabda kaam karte hain]⏎`
- **This pack, as printed:** `[നാടൻ പദ പാക്കുകൾ ലഭ്യമല്ല: lang\*.lang കാണുക; മൂല പദങ്ങൾ പ്രവർത്തിക്കും]⏎`
- **Correction:** 

### 126. `ide.msg_partial_lang` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [some word packs unavailable or invalid: see lang\*.lang]
- **Default (romanised Sanskrit), as printed:** `[kuchh shabda-pak anupalabdh ya ashuddh: lang\*.lang dekhein]⏎`
- **This pack, as printed:** `[ചില പദ പാക്കുകൾ ലഭ്യമല്ല അല്ലെങ്കിൽ അശുദ്ധം: lang\*.lang കാണുക]⏎`
- **Correction:** 

### 127. `ide.msg_pipe_fail` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [creating the process or the pipe failed]
- **Default (romanised Sanskrit), as printed:** `[prakriya ya nalika nirman asaphal]⏎`
- **This pack, as printed:** `[പ്രക്രിയ അല്ലെങ്കിൽ കുഴൽ സൃഷ്ടി പരാജയപ്പെട്ടു]⏎`
- **Correction:** 

### 128. `ide.msg_more_output` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [output cut at 32 KiB]
- **Default (romanised Sanskrit), as printed:** `[phal 32 KiB par kata]⏎`
- **This pack, as printed:** `[ഫലം 32 KiB ൽ മുറിച്ചു]⏎`
- **Correction:** 


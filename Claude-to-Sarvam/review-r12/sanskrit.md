# Review sheet: Sanskrit (संस्कृतम्)

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
  They go into `lang/sanskrit.sandesh`.

## Levels

| Level | Meaning |
|---|---|
| **LIKELY WRONG** | I think it is wrong, or it must be decided; please correct it first |
| **UNSURE** | I have a specific doubt, written under the message |
| **DRAFT** | no specific doubt, but still unverified |

**128 messages:** 1 LIKELY WRONG, 22 UNSURE, 105 DRAFT.

| # | Message | Level |
|---|---|---|
| 3 | `r48_msg_near` | UNSURE |
| 8 | `r52_msg_dvaram_arity` | UNSURE |
| 10 | `r52_msg_charcode_arity` | UNSURE |
| 13 | `r4_msg_hint_decl` | UNSURE |
| 15 | `r4_msg_hint_old2` | UNSURE |
| 22 | `r7_msg_arity2` | UNSURE |
| 23 | `r7_msg_arity3` | UNSURE |
| 38 | `msg_array_oob` | UNSURE |
| 39 | `msg_kosh_required` | UNSURE |
| 40 | `r65_msg_add` | UNSURE |
| 52 | `msg_lang_ok` | UNSURE |
| 53 | `msg_lang_fail` | UNSURE |
| 54 | `msg_shell_banner` | UNSURE |
| 59 | `msg_bytes` | UNSURE |
| 60 | `msg_namespace_error` | LIKELY WRONG |
| 69 | `msg_ast_overflow` | UNSURE |
| 85 | `r55_msg_proto_signature` | UNSURE |
| 91 | `mg_e_noexp2` | UNSURE |
| 111 | `ide.st_sanchit_w` | UNSURE |
| 112 | `ide.st_asanchit_w` | UNSURE |
| 114 | `ide.lang_swayam_w` | UNSURE |
| 123 | `ide.msg_timeout` | UNSURE |
| 127 | `ide.msg_pipe_fail` | UNSURE |

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
सूत्रम् - सम्पूर्णं सूत्रम्
प्रयोगः
  sutram <निवेशः.sm> <निर्गतम्.bin>         सङ्कलनम्
  sutram --check <निवेशः.sm>              केवलं परीक्षा, निर्गतं न
  sutram --lang <पुटः> <निवेशः.sm> <निर्गतम्.bin>  भाषा-पुटेन सह
  sutram -i                               संवादः
  sutram --version                        संस्करणम्
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
सूत्रम् 1.0 (v182) - सम्पूर्णं सूत्रम्
संस्कृत-प्रधाना भाषा -> x86-64 यन्त्र-भाषा
```
- **Correction:** 

### 3. `r48_msg_near` — **UNSURE**

- **Where:** compiler: `--check`, a parse error
- **Meaning:** 'word' (the token where parsing failed)
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: shabd '=' + caret line`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: शब्दः '=' + caret line`
- **This message alone:** `: Sutram Error [E_PARSE]: शब्दः '`
- **Doubt:** 'word' stands for a token; check that it reads naturally before the quoted token.
- **Correction:** 

### 4. `r48_msg_ok` — **DRAFT**

- **Where:** compiler: `--check`, no errors
- **Meaning:** check: correct (no output file made)
- **Default (romanised Sanskrit), as printed:** `Sutram janch: shuddh (nirgat patra nahi)⏎`
- **This pack, as printed:** `सूत्रम्-परीक्षा: शुद्धम् (निर्गत-पत्रं न रचितम्)⏎`
- **Correction:** 

### 5. `r48_msg_errors` — **DRAFT**

- **Where:** compiler: `--check`, errors found
- **Meaning:** check: errors found; no output file made
- **Default (romanised Sanskrit), as printed:** `Sutram janch: dosh mile; nirgat patra nahi⏎`
- **This pack, as printed:** `सूत्रम्-परीक्षा: दोषाः प्राप्ताः; निर्गत-पत्रं न रचितम्⏎`
- **Correction:** 

### 6. `r48_msg_eof` — **DRAFT**

- **Where:** compiler: `--check`, error at end of file
- **Meaning:** <end of file>, shown in place of the token
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: shabd '<patra-ant>'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: शब्दः '<पत्रान्तः>'`
- **This message alone:** `<पत्रान्तः>`
- **Correction:** 

### 7. `r50_msg_setchar_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** akshar_rakh needs 3 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: akshar_rakh: 3 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: akshar_rakh: 3 तर्काः आवश्यकाः⏎`
- **In the pack file:** `Sutram Error: {kw:akshar_rakh}: 3 तर्काः आवश्यकाः⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 8. `r52_msg_dvaram_arity` — **UNSURE**

- **Where:** compiler
- **Meaning:** dvaram needs 2 or 3 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: dvaram: 2 va 3 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: द्वारम्: 2 वा 3 तर्काः आवश्यकाः⏎`
- **In the pack file:** `Sutram Error: {kw:dvaram}: 2 वा 3 तर्काः आवश्यकाः⏎`  (`{kw:…}` is the pack's own keyword)
- **Doubt:** '2 वा 3 तर्काः': plural for both; check.
- **Correction:** 

### 9. `r52_msg_charat_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** akshar needs 2 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: akshar: 2 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: akshar: 2 तर्कौ आवश्यकौ⏎`
- **In the pack file:** `Sutram Error: {kw:akshar}: 2 तर्कौ आवश्यकौ⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 10. `r52_msg_charcode_arity` — **UNSURE**

- **Where:** compiler
- **Meaning:** aksharank needs 1 or 2 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: aksharank: 1 va 2 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: aksharank: 1 वा 2 तर्कौ आवश्यकौ⏎`
- **In the pack file:** `Sutram Error: {kw:aksharank}: 1 वा 2 तर्कौ आवश्यकौ⏎`  (`{kw:…}` is the pack's own keyword)
- **Doubt:** '1 वा 2 तर्कौ' uses the dual, which agrees with 2 but not with 1. I could not find a form that fits both; please choose.
- **Correction:** 

### 11. `r48_msg_undefined` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown function 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_FUNCTION]: agyat prakriya 'foo'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_FUNCTION]: अज्ञाता प्रक्रिया 'foo'`
- **This message alone:** `: Sutram Error [E_UNDEFINED_FUNCTION]: अज्ञाता प्रक्रिया '`
- **Correction:** 

### 12. `r4_msg_undef` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown name 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_NAME]: agyat naam 'y'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_NAME]: अज्ञातं नाम 'y'`
- **This message alone:** `: Sutram Error [E_UNDEFINED_NAME]: अज्ञातं नाम '`
- **Correction:** 

### 13. `r4_msg_hint_decl` — **UNSURE**

- **Where:** compiler: hint after an unknown name
- **Meaning:** hint: declare it before use: vitti NAME = ...
- **Default (romanised Sanskrit), as printed:** `Sanket: prayog se purv ghoshana avashyak: vitti y = ...`
- **This pack, as printed:** `सूचना: प्रयोगात् पूर्वं घोषणा आवश्यकी: वित्ति y = ...`
- **This message alone:** `सूचना: प्रयोगात् पूर्वं घोषणा आवश्यकी: वित्ति `
- **In the pack file:** `सूचना: प्रयोगात् पूर्वं घोषणा आवश्यकी: {kw:vitti} `  (`{kw:…}` is the pack's own keyword)
- **Doubt:** 'सूचना' is used for every hint (the default says 'Sanket'); I avoided 'सङ्केतः:' because the visarga followed by a colon looked like '::'.
- **Correction:** 

### 14. `r4_msg_hint_old` — **DRAFT**

- **Where:** compiler: hint, opens two hints
- **Meaning:** hint: 'NAME…
- **Default (romanised Sanskrit), as printed:** `Sanket: 'anyatra' purana kunjishabd (v157 se purv); navin: 'anya'`
- **This pack, as printed:** `सूचना: 'anyatra' पुरातनः कुञ्जीशब्दः (v157 तः पूर्वम्); नवीनः - 'anya'`
- **This message alone:** `सूचना: '`
- **Correction:** 

### 15. `r4_msg_hint_old2` — **UNSURE**

- **Where:** compiler: hint after an old keyword
- **Meaning:** 'OLD' is an old keyword (before v157); new: 'NEW'
- **Default (romanised Sanskrit), as printed:** `Sanket: 'anyatra' purana kunjishabd (v157 se purv); navin: 'anya'`
- **This pack, as printed:** `सूचना: 'anyatra' पुरातनः कुञ्जीशब्दः (v157 तः पूर्वम्); नवीनः - 'anya'`
- **This message alone:** `' पुरातनः कुञ्जीशब्दः (v157 तः पूर्वम्); नवीनः - '`
- **Doubt:** 'कुञ्जीशब्दः' for keyword follows the project's romanised 'kunjishabd'; and 'v157 तः' attaches the ablative to a Latin token. Both should be checked.
- **Correction:** 

### 16. `r5_msg_field` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown field 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_UNKNOWN_FIELD]: agyat kshetra 'q'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_UNKNOWN_FIELD]: अज्ञातं क्षेत्रम् 'q'`
- **This message alone:** `: Sutram Error [E_UNKNOWN_FIELD]: अज्ञातं क्षेत्रम् '`
- **Correction:** 

### 17. `r7_msg_dup` — **DRAFT**

- **Where:** compiler
- **Meaning:** declared again: 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_DUPLICATE_NAME]: punah ghoshana 'x'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_DUPLICATE_NAME]: पुनर्घोषणा 'x'`
- **This message alone:** `: Sutram Error [E_DUPLICATE_NAME]: पुनर्घोषणा '`
- **Correction:** 

### 18. `r7_msg_dup_hint` — **DRAFT**

- **Where:** compiler: hint after a duplicate
- **Meaning:** 'NAME' is already declared; to give it a new value: NAME = ...
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' pahle se ghoshit hai; naya man dene ke liye: x = ...`
- **This pack, as printed:** `सूचना: 'x' पूर्वमेव घोषितम्; नूतनं मानं दातुम्: x = ...`
- **This message alone:** `' पूर्वमेव घोषितम्; नूतनं मानं दातुम्: `
- **Correction:** 

### 19. `r7_msg_field_amb` — **DRAFT**

- **Where:** compiler
- **Meaning:** field 'NAME' (is ambiguous)
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_AMBIGUOUS_FIELD]: kshetra 'x'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_AMBIGUOUS_FIELD]: क्षेत्रम् 'x'`
- **This message alone:** `: Sutram Error [E_AMBIGUOUS_FIELD]: क्षेत्रम् '`
- **Correction:** 

### 20. `r7_msg_field_amb_hint` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** 'NAME' is at different places in two rachanas; give it a different name in each
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' do rachana me alag sthan par hai; har rachana me alag naam rakhein⏎`
- **This pack, as printed:** `सूचना: 'x' द्वयोः रचनयोः भिन्ने स्थाने अस्ति; प्रत्येकस्यां रचनायां भिन्नं नाम ददातु⏎`
- **This message alone:** `' द्वयोः रचनयोः भिन्ने स्थाने अस्ति; प्रत्येकस्यां रचनायां भिन्नं नाम ददातु⏎`
- **Correction:** 

### 21. `r7_msg_field_dup_hint` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** 'NAME' is already in this rachana
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' is rachana me pahle se hai⏎`
- **This pack, as printed:** `सूचना: 'x' अस्यां रचनायां पूर्वमेव अस्ति⏎`
- **This message alone:** `' अस्यां रचनायां पूर्वमेव अस्ति⏎`
- **Correction:** 

### 22. `r7_msg_arity2` — **UNSURE**

- **Where:** compiler: middle of the arity error
- **Meaning:** 'f' [was given] N arguments; in the signature M
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' ko 1 tark diye; hastakshar me 2`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' इत्यस्मै 1 तर्काः दत्ताः; हस्ताक्षरे 2`
- **This message alone:** `' इत्यस्मै `
- **Doubt:** 'इत्यस्मै' (the dative of the name, marked with इति) is my construction; a speaker may prefer another way to mark a name as the recipient.
- **Doubt:** Word order is fixed by the code: 'NAME' <this> N <arity3> M. Check that the sentence reads naturally around the name and the two numbers.
- **Correction:** 

### 23. `r7_msg_arity3` — **UNSURE**

- **Where:** compiler: middle of the arity error
- **Meaning:** … N arguments given; in the signature M
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' ko 1 tark diye; hastakshar me 2`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' इत्यस्मै 1 तर्काः दत्ताः; हस्ताक्षरे 2`
- **This message alone:** ` तर्काः दत्ताः; हस्ताक्षरे `
- **Doubt:** The count is printed before this text and is often 1 ('f' … 1 …): the noun is in the plural form, so '1 <plural>' may read wrong. A fragment cannot change with the number.
- **Correction:** 

### 24. `r7_msg_arity_hint` — **DRAFT**

- **Where:** compiler: hint after the arity error
- **Meaning:** hint: give exactly as many arguments as the function's definition has
- **Default (romanised Sanskrit), as printed:** `Sanket: utne hi tark dein jitne prakriya ki paribhasha me hain⏎`
- **This pack, as printed:** `सूचना: प्रक्रियायाः परिभाषायां यावन्तः तर्काः सन्ति, तावन्तः एव ददातु⏎`
- **Correction:** 

### 25. `r7_msg_mod_missing` — **DRAFT**

- **Where:** compiler
- **Meaning:** import file not found: NAME
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_MISSING]: yoj patra aprapt: ganit`
- **This pack, as printed:** `Sutram Error [E_MODULE_MISSING]: आयोजन-पत्रम् अप्राप्तम्: ganit`
- **This message alone:** `Sutram Error [E_MODULE_MISSING]: आयोजन-पत्रम् अप्राप्तम्: `
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

सूचना: <नाम>.smlib lib/ मध्ये स्रोत-पत्रस्य निर्देशिकायां वा भवेत्
```
- **Correction:** 

### 27. `r7_msg_hint_block` — **DRAFT**

- **Where:** compiler: hint after an unknown name
- **Meaning:** 'NAME' is declared inside a block { } or a loop; it is not visible outside it
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' ek khand { } ya chakra me ghoshit hai; uske bahar drishya nahi⏎`
- **This pack, as printed:** `सूचना: 'x' कस्मिंश्चित् खण्डे { } पुनरावर्तन-मध्ये वा घोषितम्; ततः बहिः न दृश्यते⏎`
- **This message alone:** `' कस्मिंश्चित् खण्डे { } पुनरावर्तन-मध्ये वा घोषितम्; ततः बहिः न दृश्यते⏎`
- **In the pack file:** `' कस्मिंश्चित् खण्डे { } {kw:chakra}-मध्ये वा घोषितम्; ततः बहिः न दृश्यते⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 28. `r5_msg_field_hint` — **DRAFT**

- **Where:** compiler: hint, opens the field hint
- **Meaning:** hint: 'NAME…
- **Default (romanised Sanskrit), as printed:** `Sanket: 'q' kisi rachana ka kshetra nahi⏎`
- **This pack, as printed:** `सूचना: 'q' कस्याश्चिदपि रचनायाः क्षेत्रं नास्ति⏎`
- **This message alone:** `सूचना: '`
- **Correction:** 

### 29. `r5_msg_field_hint2` — **DRAFT**

- **Where:** compiler: hint after an unknown field
- **Meaning:** 'NAME' is not a field of any rachana
- **Default (romanised Sanskrit), as printed:** `Sanket: 'q' kisi rachana ka kshetra nahi⏎`
- **This pack, as printed:** `सूचना: 'q' कस्याश्चिदपि रचनायाः क्षेत्रं नास्ति⏎`
- **This message alone:** `' कस्याश्चिदपि रचनायाः क्षेत्रं नास्ति⏎`
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

Sutram Error: व्याकरण-दोषः, पङ्क्तिः 
```
- **Correction:** 

### 31. `msg_err_near` — **DRAFT**

- **Where:** compiler: a parse error
- **Meaning:** , word 'TOKEN'
- **Default (romanised Sanskrit), as printed:** `⏎Sutram Error: vyakaran dosh, pankti 3:11, shabd '='`
- **This pack, as printed:** `⏎Sutram Error: व्याकरण-दोषः, पङ्क्तिः 3:11, शब्दः '='`
- **This message alone:** `, शब्दः '`
- **Correction:** 

### 32. `msg_err_eof` — **DRAFT**

- **Where:** compiler: a parse error at the end of the file
- **Meaning:** end of file, shown in place of the token
- **Default (romanised Sanskrit), as printed:** `⏎Sutram Error: vyakaran dosh, pankti 6:1, shabd 'patra-ant'`
- **This pack, as printed:** `⏎Sutram Error: व्याकरण-दोषः, पङ्क्तिः 6:1, शब्दः 'पत्रान्तः'`
- **This message alone:** `पत्रान्तः`
- **Correction:** 

### 33. `msg_err_hint` — **DRAFT**

- **Where:** compiler: hint after a parse error
- **Meaning:** hint: check the word and the grammar at this place
- **Default (romanised Sanskrit), as printed:** `Sanket: is sthan par shabd aur vyakaran dekho.⏎`
- **This pack, as printed:** `सूचना: अस्मिन् स्थाने शब्दं व्याकरणं च पश्यतु।⏎`
- **Correction:** 

### 34. `msg_err_arg_limit` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** hint: a function takes at most 6 arguments
- **Default (romanised Sanskrit), as printed:** `Sanket: prakriya adhiktam 6 tark lete hain.⏎`
- **This pack, as printed:** `सूचना: प्रक्रिया अधिकतमं 6 तर्कान् गृह्णाति।⏎`
- **Correction:** 

### 35. `msg_err_duplicate_func` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** hint: the function is defined twice (name clash)
- **Default (romanised Sanskrit), as printed:** `Sanket: dohri prakriya paribhasha (naam takkar).⏎`
- **This pack, as printed:** `सूचना: प्रक्रियायाः द्विः परिभाषा (नाम-सङ्घर्षः)।⏎`
- **Correction:** 

### 36. `msg_duplicate_func` — **DRAFT**

- **Where:** compiler
- **Meaning:** function defined again: NAME
- **Default (romanised Sanskrit), as printed:** `Sutram Error: punah prakriya paribhasha: f`
- **This pack, as printed:** `Sutram Error: प्रक्रियायाः पुनःपरिभाषा: f`
- **This message alone:** `Sutram Error: प्रक्रियायाः पुनःपरिभाषा: `
- **Correction:** 

### 37. `msg_undefined_func` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown function: NAME
- **Default (romanised Sanskrit), as printed:** `Sutram Error: agyat prakriya: f`
- **This pack, as printed:** `Sutram Error: अज्ञाता प्रक्रिया: f`
- **This message alone:** `Sutram Error: अज्ञाता प्रक्रिया: `
- **Correction:** 

### 38. `msg_array_oob` — **UNSURE**

- **Where:** the compiled program, at run time
- **Meaning:** mala index out of bounds
- **Default (romanised Sanskrit), as printed:** `Sutram Error: mala ank seema atikram⏎`
- **This pack, as printed:** `Sutram Error: पङ्क्ति-अङ्कः सीमाम् अतिक्रान्तः⏎`
- **In the pack file:** `Sutram Error: {kw:mala}-अङ्कः सीमाम् अतिक्रान्तः⏎`  (`{kw:…}` is the pack's own keyword)
- **Doubt:** 'अङ्कः' for an index can also mean 'number'; and the pack's word for mala is 'पङ्क्ति' (a row), so this reads 'row-number beyond the limit'. Check that it is understood as an array index.
- **Correction:** 

### 39. `msg_kosh_required` — **UNSURE**

- **Where:** compiler
- **Meaning:** a kosh function needs a kosh variable
- **Default (romanised Sanskrit), as printed:** `Sutram Error: kosh prakriya hetu kosh-vitti avashyak⏎`
- **This pack, as printed:** `Sutram Error: कोश-प्रक्रियायै कोश-वित्तिः आवश्यकी⏎`
- **In the pack file:** `Sutram Error: {kw:kosh}-प्रक्रियायै {kw:kosh}-वित्तिः आवश्यकी⏎`  (`{kw:…}` is the pack's own keyword)
- **Doubt:** 'वित्ति' is the project's coined keyword; I treated it as feminine (आवश्यकी). Check the gender.
- **Correction:** 

### 40. `r65_msg_add` — **UNSURE**

- **Where:** the program, `trap` build
- **Meaning:** overflow in an addition
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: yog atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: योगे अतिप्रवाहः⏎`
- **This message alone:** `: योगे अतिप्रवाहः⏎`
- **Doubt:** 'अतिप्रवाहः' for an integer overflow is a calque; it is used in all seven trap messages.
- **Correction:** 

### 41. `r65_msg_sub` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a subtraction
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: nyun atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: व्यवकलने अतिप्रवाहः⏎`
- **This message alone:** `: व्यवकलने अतिप्रवाहः⏎`
- **Correction:** 

### 42. `r65_msg_mul` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a multiplication
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: gun atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: गुणने अतिप्रवाहः⏎`
- **This message alone:** `: गुणने अतिप्रवाहः⏎`
- **Correction:** 

### 43. `r65_msg_div` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** division by zero
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: shunya se bhajan⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: शून्येन भागः⏎`
- **This message alone:** `: शून्येन भागः⏎`
- **Correction:** 

### 44. `r65_msg_mod` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** remainder by zero
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: shunya se shesh⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: शून्येन शेषः⏎`
- **This message alone:** `: शून्येन शेषः⏎`
- **Correction:** 

### 45. `r65_msg_div_overflow` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a division
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: bhajan atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: भागे अतिप्रवाहः⏎`
- **This message alone:** `: भागे अतिप्रवाहः⏎`
- **Correction:** 

### 46. `r65_msg_mod_overflow` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a remainder
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: shesh atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: शेषे अतिप्रवाहः⏎`
- **This message alone:** `: शेषे अतिप्रवाहः⏎`
- **Correction:** 

### 47. `msg_kosh_empty` — **DRAFT**

- **Where:** the program, at run time
- **Meaning:** kosh_pop from an empty kosh
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rikta kosh se kosh_pop⏎`
- **This pack, as printed:** `Sutram Error: रिक्तात् कोशात् कोशपोप्⏎`
- **In the pack file:** `Sutram Error: रिक्तात् कोशात् {kw:kosh_pop}⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 48. `msg_kosh_peek_empty` — **DRAFT**

- **Where:** the program, at run time
- **Meaning:** kosh_peek from an empty kosh
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rikta kosh se kosh_peek⏎`
- **This pack, as printed:** `Sutram Error: रिक्तात् कोशात् कोशशिखर⏎`
- **In the pack file:** `Sutram Error: रिक्तात् कोशात् {kw:kosh_peek}⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 49. `msg_kosh_dequeue_empty` — **DRAFT**

- **Where:** the program, at run time
- **Meaning:** kosh_dequeue from an empty kosh
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rikta kosh se kosh_dequeue⏎`
- **This pack, as printed:** `Sutram Error: रिक्तात् कोशात् कोशनिर्गम⏎`
- **In the pack file:** `Sutram Error: रिक्तात् कोशात् {kw:kosh_dequeue}⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 50. `msg_kosh_param_type` — **DRAFT**

- **Where:** compiler
- **Meaning:** kosh argument: element type differs
- **Default (romanised Sanskrit), as printed:** `Sutram Error: kosh tark: tatv prakar bhinn⏎`
- **This pack, as printed:** `Sutram Error: कोश-तर्कः: तत्त्व-प्रकारः भिन्नः⏎`
- **Correction:** 

### 51. `msg_kosh_param_push` — **DRAFT**

- **Where:** compiler
- **Meaning:** kosh_push is not supported on a kosh argument
- **Default (romanised Sanskrit), as printed:** `Sutram Error: kosh tark par kosh_push asamarthit⏎`
- **This pack, as printed:** `Sutram Error: कोश-तर्के कोशपुष् असमर्थितम्⏎`
- **In the pack file:** `Sutram Error: कोश-तर्के {kw:kosh_push} असमर्थितम्⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 52. `msg_lang_ok` — **UNSURE**

- **Where:** compiler: every run with `--lang`
- **Meaning:** language pack found: PACK
- **Default (romanised Sanskrit), as printed:** `Bhasha pak prapt: hindi`
- **This pack, as printed:** `भाषा-पुटः प्राप्तः: hindi`
- **This message alone:** `भाषा-पुटः प्राप्तः: `
- **Doubt:** 'भाषा-पुटः' is my coinage for 'language pack' (alternatives: भाषा-सम्पुटः, भाषा-सङ्ग्रहः).
- **Doubt:** 'pack' (the language-pack file) has no settled native word; check the term.
- **Correction:** 

### 53. `msg_lang_fail` — **UNSURE**

- **Where:** compiler
- **Meaning:** warning: language pack not found: PACK
- **Default (romanised Sanskrit), as printed:** `Chetavani: bhasha pak nahi mila: hindi`
- **This pack, as printed:** `चेतावनी: भाषा-पुटः न प्राप्तः: hindi`
- **This message alone:** `चेतावनी: भाषा-पुटः न प्राप्तः: `
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
सूत्रम् संवादः v1.0 - सम्पूर्णं सूत्रम्
सूत्रम्-कथनं लिखतु, Enter नुदतु। सद्यः चलिष्यति।
आदेशाः - sahayata (सहायता) | nirgat (निर्गमनम्) | sarvam (सर्वं पश्यतु)
```
- **Doubt:** 'नुदतु' (push) for pressing a key is my choice; check it.
- **Doubt:** 'Enter' is kept as the key's label; the verb for pressing a key should be checked.
- **Correction:** 

### 55. `msg_shell_bye` — **DRAFT**

- **Where:** compiler: leaving `sutram -i`
- **Meaning:** greeting; session ended
- **Default (romanised Sanskrit), as printed:** `Namaste! Satra samapt.⏎`
- **This pack, as printed:** `नमस्ते! सत्रं समाप्तम्।⏎`
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
सूत्रम् संवाद-सहायता:
  लिख("नमस्ते\n")            पाठं लिखति
  वित्ति x = 5             वित्ति-घोषणा
  लिख(x + 3)            मूल्यं लिखति
  पुनरावर्तन i = 0 पर्यन्त 5 { लिख(i) }   आवर्तनम्
  पङ्क्ति arr[5]             पङ्क्ति-घोषणा
  sarvam                  सम्पूर्णं कार्यक्रमं पश्यतु
  nirgat                  संवादात् निर्गच्छतु
```
- **In the pack file:** `सूत्रम् संवाद-सहायता:⏎  {kw:likha}("नमस्ते\n")            पाठं लिखति⏎  {kw:vitti} x = 5             वित्ति-घोषणा⏎  {kw:likha}(x + 3)            मूल्यं लिखति⏎  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   आवर्तनम्⏎  {kw:mala} arr[5]             पङ्क्ति-घोषणा⏎  sarvam                  सम्पूर्णं कार्यक्रमं पश्यतु⏎  nirgat                  संवादात् निर्गच्छतु⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 57. `msg_open_err` — **DRAFT**

- **Where:** compiler
- **Meaning:** input (source) file not found
- **Default (romanised Sanskrit), as printed:** `Sutram Error: nivesh patra aprapt⏎`
- **This pack, as printed:** `Sutram Error: निवेश-पत्रम् अप्राप्तम्⏎`
- **Correction:** 

### 58. `msg_ok` — **DRAFT**

- **Where:** compiler: a successful compile
- **Meaning:** done: N bytes compiled
- **Default (romanised Sanskrit), as printed:** `Siddh: 297 baait sankalit⏎`
- **This pack, as printed:** `सिद्धम्: 297 बाइट् सङ्कलिताः⏎`
- **This message alone:** `सिद्धम्: `
- **Correction:** 

### 59. `msg_bytes` — **UNSURE**

- **Where:** compiler: a successful compile
- **Meaning:** … bytes compiled
- **Default (romanised Sanskrit), as printed:** `Siddh: 297 baait sankalit⏎`
- **This pack, as printed:** `सिद्धम्: 297 बाइट् सङ्कलिताः⏎`
- **This message alone:** ` बाइट् सङ्कलिताः⏎`
- **Doubt:** 'बाइट्' is the Sanskrit book's loanword; I made the participle masculine plural (सङ्कलिताः). Check the agreement.
- **Correction:** 

### 60. `msg_namespace_error` — **LIKELY WRONG**

- **Where:** compiler
- **Meaning:** invalid import (form: module@alias, alias up to 31 bytes)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ashuddh yoj (roop: ghatak@upanaam, upanaam 31 baait tak)⏎`
- **This pack, as printed:** `Sutram Error: अशुद्धः आयोजन (रूपम्: घटकः@उपनाम, उपनाम 31 बाइट् यावत्)⏎`
- **In the pack file:** `Sutram Error: अशुद्धः {kw:yoj} (रूपम्: घटकः@उपनाम, उपनाम 31 बाइट् यावत्)⏎`  (`{kw:…}` is the pack's own keyword)
- **Doubt:** LIKELY WRONG: 'अशुद्धः' is masculine, but the pack's word for yoj, 'आयोजन', is neuter (आयोजनम्). The keyword is inserted in its stem form, so the adjective should probably be 'अशुद्धम्' or the phrase recast.
- **Correction:** 

### 61. `msg_namespace_module_missing` — **DRAFT**

- **Where:** compiler
- **Meaning:** module file not found
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ghatak patra aprapt⏎`
- **This pack, as printed:** `Sutram Error: घटक-पत्रम् अप्राप्तम्⏎`
- **Correction:** 

### 62. `msg_namespace_alias_reuse` — **DRAFT**

- **Where:** compiler
- **Meaning:** alias already used (for another module)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: upanaam purv-niyukt (anya ghatak)⏎`
- **This pack, as printed:** `Sutram Error: उपनाम पूर्वमेव नियुक्तम् (अन्यस्मै घटकाय)⏎`
- **Correction:** 

### 63. `r51_alias_conflict` — **DRAFT**

- **Where:** compiler
- **Meaning:** alias already used (for another module)
- **Default (romanised Sanskrit), as printed:** `prog.sm:2: Sutram Error [E_MODULE_ALIAS_REUSE]: upanaam purv-niyukt (anya ghatak)⏎`
- **This pack, as printed:** `prog.sm:2: Sutram Error [E_MODULE_ALIAS_REUSE]: उपनाम पूर्वमेव नियुक्तम् (अन्यस्मै घटकाय)⏎`
- **This message alone:** `: Sutram Error [E_MODULE_ALIAS_REUSE]: उपनाम पूर्वमेव नियुक्तम् (अन्यस्मै घटकाय)⏎`
- **Correction:** 

### 64. `msg_namespace_func_limit` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of module function names exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ghatak prakriya-naam seema atikram⏎`
- **This pack, as printed:** `Sutram Error: घटक-प्रक्रिया-नाम-सीमातिक्रमः⏎`
- **Correction:** 

### 65. `msg_import_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the expanded source exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: vistarit srot seema atikram⏎`
- **This pack, as printed:** `Sutram Error: विस्तारित-स्रोत-सीमातिक्रमः⏎`
- **Correction:** 

### 66. `graph_cycle_prefix` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** import cycle: a -> b -> a
- **Default (romanised Sanskrit), as printed:** `prog.sm:1: Sutram Error [E_MODULE_CYCLE] yoj chakra: a -> b -> a`
- **This pack, as printed:** `prog.sm:1: Sutram Error [E_MODULE_CYCLE] आयोजन-चक्रम्: a -> b -> a`
- **This message alone:** `आयोजन-चक्रम्: `
- **Correction:** 

### 67. `graph_missing_prefix` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** import file not found: NAME
- **Default (romanised Sanskrit), as printed:** `prog.sm:1: Sutram Error [E_MODULE_MISSING] yoj patra aprapt: ganit`
- **This pack, as printed:** `prog.sm:1: Sutram Error [E_MODULE_MISSING] आयोजन-पत्रम् अप्राप्तम्: ganit`
- **This message alone:** `आयोजन-पत्रम् अप्राप्तम्: `
- **Correction:** 

### 68. `graph_invalid_prefix` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** invalid module name
- **Default (romanised Sanskrit), as printed:** `prog.sm:1: Sutram Error [E_MODULE_INVALID] ashuddh ghatak naam`
- **This pack, as printed:** `prog.sm:1: Sutram Error [E_MODULE_INVALID] अशुद्धं घटक-नाम`
- **This message alone:** `अशुद्धं घटक-नाम`
- **Correction:** 

### 69. `msg_ast_overflow` — **UNSURE**

- **Where:** compiler
- **Meaning:** limit of the syntax tree exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: vakya-vriksh seema atikram⏎`
- **This pack, as printed:** `Sutram Error: वाक्य-वृक्ष-सीमातिक्रमः⏎`
- **Doubt:** 'syntax tree' is a coined technical term here; check it.
- **Correction:** 

### 70. `msg_func_params_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the function parameter list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya tark-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: प्रक्रिया-तर्क-सूची-सीमातिक्रमः⏎`
- **Correction:** 

### 71. `msg_var_table_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the variable list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: vitti-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: वित्ति-सूची-सीमातिक्रमः⏎`
- **Correction:** 

### 72. `msg_func_table_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the function list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: प्रक्रिया-सूची-सीमातिक्रमः⏎`
- **Correction:** 

### 73. `msg_patch_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the call list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: aahvan-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: आह्वान-सूची-सीमातिक्रमः⏎`
- **Correction:** 

### 74. `msg_func_defs_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the function definition list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya paribhasha-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: प्रक्रिया-परिभाषा-सूची-सीमातिक्रमः⏎`
- **Correction:** 

### 75. `msg_r9_guna_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** guna limit exceeded (1024)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: guna seema atikram (1024)⏎`
- **This pack, as printed:** `Sutram Error: गुण-सीमातिक्रमः (1024)⏎`
- **In the pack file:** `Sutram Error: {kw:guna}-सीमातिक्रमः (1024)⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 76. `msg_break_patch_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** too many krama (break) in a loop
- **Default (romanised Sanskrit), as printed:** `Sutram Error: chakra me krama seema atikram⏎`
- **This pack, as printed:** `Sutram Error: पुनरावर्तन-मध्ये क्रम-सीमातिक्रमः⏎`
- **In the pack file:** `Sutram Error: {kw:chakra}-मध्ये {kw:krama}-सीमातिक्रमः⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 77. `msg_continue_patch_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** too many agrim (continue) in a loop
- **Default (romanised Sanskrit), as printed:** `Sutram Error: chakra me agrim seema atikram⏎`
- **This pack, as printed:** `Sutram Error: पुनरावर्तन-मध्ये उद्देश्य-सीमातिक्रमः⏎`
- **In the pack file:** `Sutram Error: {kw:chakra}-मध्ये {kw:agrim}-सीमातिक्रमः⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 78. `msg_code_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the machine code exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: yantra-bhasha seema atikram⏎`
- **This pack, as printed:** `Sutram Error: यन्त्र-भाषा-सीमातिक्रमः⏎`
- **Correction:** 

### 79. `msg_rachana_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the rachana list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rachana-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: रचना-सूची-सीमातिक्रमः⏎`
- **In the pack file:** `Sutram Error: {kw:rachana}-सूची-सीमातिक्रमः⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 80. `msg_rachana_fields_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of rachana fields exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rachana kshetra seema atikram⏎`
- **This pack, as printed:** `Sutram Error: रचना-क्षेत्र-सीमातिक्रमः⏎`
- **In the pack file:** `Sutram Error: {kw:rachana}-क्षेत्र-सीमातिक्रमः⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 81. `msg_block_nesting_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of block depth exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: khand gahrai seema atikram⏎`
- **This pack, as printed:** `Sutram Error: खण्ड-गभीरता-सीमातिक्रमः⏎`
- **Correction:** 

### 82. `msg_block_stmt_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of statements in a block exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: khand kathan seema atikram⏎`
- **This pack, as printed:** `Sutram Error: खण्ड-कथन-सीमातिक्रमः⏎`
- **Correction:** 

### 83. `r55_msg_proto_duplicate` — **DRAFT**

- **Where:** compiler
- **Meaning:** function forward-declared again
- **Default (romanised Sanskrit), as printed:** `Sutram Error: punah prakriya purv-ghoshana⏎`
- **This pack, as printed:** `Sutram Error: प्रक्रियायाः पुनः पूर्वघोषणा⏎`
- **Correction:** 

### 84. `r55_msg_proto_missing` — **DRAFT**

- **Where:** compiler
- **Meaning:** function forward-declared but never defined
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya purv-ghoshana paribhasha-rahit⏎`
- **This pack, as printed:** `Sutram Error: प्रक्रियायाः पूर्वघोषणा परिभाषा-रहिता⏎`
- **Correction:** 

### 85. `r55_msg_proto_signature` — **UNSURE**

- **Where:** compiler
- **Meaning:** forward declaration and definition differ (arguments/type)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya purv-ghoshana va paribhasha bhinn (tark/prakar)⏎`
- **This pack, as printed:** `Sutram Error: प्रक्रियायाः पूर्वघोषणा परिभाषा च भिन्ने (तर्काः/प्रकारः)⏎`
- **Doubt:** 'forward declaration' (a prototype) is a coined term; check it.
- **Correction:** 

### 86. `r55_msg_proto_capacity` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of function forward declarations exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya purv-ghoshana seema atikram⏎`
- **This pack, as printed:** `Sutram Error: प्रक्रिया-पूर्वघोषणा-सीमातिक्रमः⏎`
- **Correction:** 

### 87. `r56_msg_global_capacity` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of module-level variables exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ghatak-star vitti seema atikram⏎`
- **This pack, as printed:** `Sutram Error: घटक-स्तरीय-वित्ति-सीमातिक्रमः⏎`
- **Correction:** 

### 88. `r56_msg_global_duplicate` — **DRAFT**

- **Where:** compiler
- **Meaning:** module-level variable name declared again
- **Default (romanised Sanskrit), as printed:** `Sutram Error: punah ghatak-star vitti naam⏎`
- **This pack, as printed:** `Sutram Error: घटक-स्तरीय-वित्ति-नाम्नः पुनर्घोषणा⏎`
- **Correction:** 

### 89. `r56_msg_patch_capacity` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of global value references exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: sarvatrik mulya sandarbh seema atikram⏎`
- **This pack, as printed:** `Sutram Error: सार्वत्रिक-मूल्य-सन्दर्भ-सीमातिक्रमः⏎`
- **Correction:** 

### 90. `mg_e_cycle` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** import cycle: a -> b -> a
- **Default (romanised Sanskrit), as printed:** `prog.sm:1:Sutram Error [E_MODULE_CYCLE]: yoj chakra: a -> b -> a`
- **This pack, as printed:** `prog.sm:1:Sutram Error [E_MODULE_CYCLE]: आयोजन-चक्रम्: a -> b -> a`
- **This message alone:** `Sutram Error [E_MODULE_CYCLE]: आयोजन-चक्रम्: `
- **Correction:** 

### 91. `mg_e_noexp2` — **UNSURE**

- **Where:** compiler: middle of 'not exported'
- **Meaning:** 'SYM' [from] module 'MOD' [is] not exported
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' ghatak 'vec' se aniryat⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' घटकात् 'vec' अनिर्यातम्⏎`
- **This message alone:** `' घटकात् '`
- **Doubt:** 'SYM' घटकात् 'MOD' अनिर्यातम्: the ablative 'from the module' comes before the module's name; check the order.
- **Doubt:** Order fixed by the code: 'SYM' <this> 'MOD' <noexp3>. Check that 'SYM … MOD … not exported' reads as one sentence.
- **Correction:** 

### 92. `mg_e_noexp3` — **DRAFT**

- **Where:** compiler: end of 'not exported'
- **Meaning:** … not exported from module MOD
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' ghatak 'vec' se aniryat⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' घटकात् 'vec' अनिर्यातम्⏎`
- **This message alone:** `' अनिर्यातम्⏎`
- **Correction:** 

### 93. `mg_e_dupexp1` — **DRAFT**

- **Where:** compiler
- **Meaning:** exported again: 'SYM', module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: punah niryat 'thing', ghatak 'dup'`
- **This pack, as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: पुनर्निर्यातम् 'thing', घटकः 'dup'`
- **This message alone:** `Sutram Error [E_MODULE_DUP_EXPORT]: पुनर्निर्यातम् '`
- **Correction:** 

### 94. `mg_e_dupexp2` — **DRAFT**

- **Where:** compiler: middle
- **Meaning:** …, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: punah niryat 'thing', ghatak 'dup'`
- **This pack, as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: पुनर्निर्यातम् 'thing', घटकः 'dup'`
- **This message alone:** `', घटकः '`
- **Correction:** 

### 95. `mg_e_undef1` — **DRAFT**

- **Where:** compiler
- **Meaning:** export 'SYM' has no definition, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: niryat 'thing' paribhasha-rahit, ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: निर्यातम् 'thing' परिभाषा-रहितम्, घटकः 'vec'`
- **This message alone:** `Sutram Error [E_EXPORT_UNDEFINED]: निर्यातम् '`
- **Correction:** 

### 96. `mg_e_undef2` — **DRAFT**

- **Where:** compiler: middle
- **Meaning:** … has no definition, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: niryat 'thing' paribhasha-rahit, ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: निर्यातम् 'thing' परिभाषा-रहितम्, घटकः 'vec'`
- **This message alone:** `' परिभाषा-रहितम्, घटकः '`
- **Correction:** 

### 97. `mg_e_unknown1` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown symbol 'SYM', module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: agyat sanket 'thing', ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: अज्ञातं चिह्नम् 'thing', घटकः 'vec'`
- **This message alone:** `Sutram Error [E_EXPORT_UNDEFINED]: अज्ञातं चिह्नम् '`
- **Correction:** 

### 98. `mg_e_unknown2` — **DRAFT**

- **Where:** compiler: middle
- **Meaning:** …, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: agyat sanket 'thing', ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: अज्ञातं चिह्नम् 'thing', घटकः 'vec'`
- **This message alone:** `', घटकः '`
- **Correction:** 

### 99. `mg_e_depth` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of import depth exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_DEPTH]: yoj gahrai seema atikram⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_DEPTH]: आयोजन-गभीरता-सीमातिक्रमः⏎`
- **Correction:** 

### 100. `mg_e_valias1` — **DRAFT**

- **Where:** compiler
- **Meaning:** a v1 module 'MOD' needs an alias: yoj MOD@upanaam
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 ghatak 'vec' upanaam avashyak: yoj vec@upanaam`
- **This pack, as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 घटकः 'vec' उपनाम आवश्यकम्: आयोजन vec@upanaam`
- **This message alone:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 घटकः '`
- **Correction:** 

### 101. `mg_e_valias2` — **DRAFT**

- **Where:** compiler: middle
- **Meaning:** … needs an alias: yoj MOD@upanaam
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 ghatak 'vec' upanaam avashyak: yoj vec@upanaam`
- **This pack, as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 घटकः 'vec' उपनाम आवश्यकम्: आयोजन vec@upanaam`
- **This message alone:** `' उपनाम आवश्यकम्: आयोजन `
- **In the pack file:** `' उपनाम आवश्यकम्: {kw:yoj} `  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 102. `mg_e_limit` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of modules/imports exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_LIMIT]: ghatak/yoj seema atikram⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_LIMIT]: घटक/आयोजन-सीमातिक्रमः⏎`
- **Correction:** 

### 103. `r66_msg_bad_utf8` — **DRAFT**

- **Where:** compiler
- **Meaning:** invalid or broken Indian-script name
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_UTF8]: ashuddh ya khandit bharatiya naam⏎`
- **This pack, as printed:** `Sutram Error [E_UTF8]: अशुद्धं खण्डितं वा भारतीयं नाम⏎`
- **Correction:** 

### 104. `r68_utf8_tail` — **DRAFT**

- **Where:** compiler
- **Meaning:** invalid or broken UTF-8 in the source
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_UTF8]: prog.sm:2: srot me ashuddh ya khandit UTF-8⏎`
- **This pack, as printed:** `Sutram Error [E_UTF8]: prog.sm:2: स्रोते अशुद्धं खण्डितं वा UTF-8⏎`
- **This message alone:** `: स्रोते अशुद्धं खण्डितं वा UTF-8⏎`
- **Correction:** 

### 105. `r68_value_tail` — **DRAFT**

- **Where:** compiler
- **Meaning:** an abbreviation is not a value: 'वि॰'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_ABBREVIATION_VALUE]: prog.sm:2: sankshep shabd mulya nahi: 'वि॰'`
- **This pack, as printed:** `Sutram Error [E_ABBREVIATION_VALUE]: prog.sm:2: संक्षेप-शब्दः मूल्यं नास्ति: 'वि॰'`
- **This message alone:** `: संक्षेप-शब्दः मूल्यं नास्ति: '`
- **Correction:** 

### 106. `ide.st_pankti_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** line N (start of the status line)
- **Default (romanised Sanskrit), as printed:** `pankti 12   stambh 4   |   bhasha: …`
- **This pack, as printed:** `पङ्क्तिः 12   स्तम्भः 4   |   भाषा: …`
- **This message alone:** `पङ्क्तिः `
- **Correction:** 

### 107. `ide.st_stambh_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** column N
- **Default (romanised Sanskrit), as printed:** `pankti 12   stambh 4   |   bhasha: …`
- **This pack, as printed:** `पङ्क्तिः 12   स्तम्भः 4   |   भाषा: …`
- **This message alone:** `   स्तम्भः `
- **Correction:** 

### 108. `ide.st_bhasha_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** | language: NAME
- **Default (romanised Sanskrit), as printed:** `…4   |   bhasha: हिन्दी`
- **This pack, as printed:** `…4   |   भाषा: हिन्दी`
- **This message alone:** `   |   भाषा: `
- **Correction:** 

### 109. `ide.st_akshara_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** | letters (clusters): N
- **Default (romanised Sanskrit), as printed:** `…   |   akshara: 26`
- **This pack, as printed:** `…   |   अक्षराणि: 26`
- **This message alone:** `   |   अक्षराणि: `
- **Correction:** 

### 110. `ide.st_lipi_w` — **DRAFT**

- **Where:** IDE status line, typing mode on
- **Meaning:** | script: NAME (the typing script)
- **Default (romanised Sanskrit), as printed:** `…   |   lipi: தமிழ்`
- **This pack, as printed:** `…   |   लिपि: தமிழ்`
- **This message alone:** `   |   लिपि: `
- **Correction:** 

### 111. `ide.st_sanchit_w` — **UNSURE**

- **Where:** IDE status line
- **Meaning:** saved
- **Default (romanised Sanskrit), as printed:** `…   |   sanchit`
- **This pack, as printed:** `…   |   सञ्चितम्`
- **This message alone:** `सञ्चितम्`
- **Doubt:** 'सञ्चितम्' for a saved file; check the term.
- **Correction:** 

### 112. `ide.st_asanchit_w` — **UNSURE**

- **Where:** IDE status line
- **Meaning:** not saved *
- **Default (romanised Sanskrit), as printed:** `…   |   asanchit *`
- **This pack, as printed:** `…   |   असञ्चितम् *`
- **This message alone:** `असञ्चितम् *`
- **Doubt:** As st_sanchit_w.
- **Correction:** 

### 113. `ide.st_notfound_w` — **DRAFT**

- **Where:** IDE status line, after Find
- **Meaning:** find: not found
- **Default (romanised Sanskrit), as printed:** `anwesh: nahi mila`
- **This pack, as printed:** `अन्वेषणम्: न प्राप्तम्`
- **Correction:** 

### 114. `ide.lang_swayam_w` — **UNSURE**

- **Where:** IDE status line: language Auto
- **Meaning:** automatic (detect the script)
- **Default (romanised Sanskrit), as printed:** `   |   bhasha: swayam`
- **This pack, as printed:** `   |   भाषा: स्वयम्`
- **This message alone:** `स्वयम्`
- **Doubt:** 'स्वयम्' for the Auto (detect) setting; 'स्वचालितम्' may be clearer.
- **Correction:** 

### 115. `ide.lang_swayam_sk_w` — **DRAFT**

- **Where:** IDE status line: Auto found Devanagari
- **Meaning:** automatic (Sanskrit)
- **Default (romanised Sanskrit), as printed:** `   |   bhasha: swayam (sanskrit)`
- **This pack, as printed:** `   |   भाषा: स्वयम् (संस्कृतम्)`
- **This message alone:** `स्वयम् (संस्कृतम्)`
- **Correction:** 

### 116. `ide.lang_mool_w` — **DRAFT**

- **Where:** IDE status line: language Core
- **Meaning:** core (Latin keywords)
- **Default (romanised Sanskrit), as printed:** `   |   bhasha: mool`
- **This pack, as printed:** `   |   भाषा: मूलम्`
- **This message alone:** `मूलम्`
- **Correction:** 

### 117. `ide.msg_ready` — **DRAFT**

- **Where:** IDE output pane, at start and after Clear shell
- **Meaning:** ready. F5 compiles and runs the program in the editor
- **Default (romanised Sanskrit), as printed:** `Taiyar. F5: sampadak ka karyakram sankalan aur chalan.⏎`
- **This pack, as printed:** `सज्जम्। F5: सम्पादकस्य कार्यक्रमस्य सङ्कलनं चालनं च।⏎`
- **Correction:** 

### 118. `ide.msg_compile_failed` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [compilation failed]
- **Default (romanised Sanskrit), as printed:** `[sankalan asaphal]⏎`
- **This pack, as printed:** `[सङ्कलनम् असफलम्]⏎`
- **Correction:** 

### 119. `ide.msg_run_failed` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the program ended abnormally]
- **Default (romanised Sanskrit), as printed:** `[karyakram asamanya roop se samapt]⏎`
- **This pack, as printed:** `[कार्यक्रमः असामान्यरूपेण समाप्तः]⏎`
- **Correction:** 

### 120. `ide.msg_file_failed` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [reading/writing the file failed]
- **Default (romanised Sanskrit), as printed:** `[patra padhne/likhne me asaphal]⏎`
- **This pack, as printed:** `[पत्रस्य पठने लेखने वा असफलता]⏎`
- **Correction:** 

### 121. `ide.msg_input_large` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the file is too big; editor limit 64 KiB]
- **Default (romanised Sanskrit), as printed:** `[patra bahut bada; sampadak seema 64 KiB]⏎`
- **This pack, as printed:** `[पत्रम् अतिबृहत्; सम्पादक-सीमा 64 KiB]⏎`
- **Correction:** 

### 122. `ide.msg_shell_limit` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the shell history is full; clear the shell first]
- **Default (romanised Sanskrit), as printed:** `[khol ka itihas purna; pahle khol rikta karein]⏎`
- **This pack, as printed:** `[संवादस्य इतिहासः पूर्णः; प्रथमं संवादं रिक्तं करोतु]⏎`
- **Correction:** 

### 123. `ide.msg_timeout` — **UNSURE**

- **Where:** IDE output pane
- **Meaning:** [the process ran more than 10 seconds; stopped]
- **Default (romanised Sanskrit), as printed:** `[prakriya 10 sekand se adhik; samapt ki gayi]⏎`
- **This pack, as printed:** `[प्रक्रिया 10 क्षणेभ्यः अधिकं चलिता; समापिता]⏎`
- **Doubt:** 'क्षणः' for a second follows modern spoken Sanskrit as I understand it; check.
- **Correction:** 

### 124. `ide.msg_missing_compiler` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [win\sutram.exe not found: build the compiler first]
- **Default (romanised Sanskrit), as printed:** `[win\sutram.exe nahi mila: pahle sankalak banayein]⏎`
- **This pack, as printed:** `[win\sutram.exe न प्राप्तम्: प्रथमं सङ्कलकं निर्मातु]⏎`
- **Correction:** 

### 125. `ide.msg_missing_lang` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [native word packs unavailable: see lang\*.lang; the core words work]
- **Default (romanised Sanskrit), as printed:** `[deshi shabda-pak anupalabdh: lang\*.lang dekhein; mool shabda kaam karte hain]⏎`
- **This pack, as printed:** `[देशीय-शब्द-पुटाः अनुपलब्धाः: lang\*.lang पश्यतु; मूल-शब्दाः कार्यं कुर्वन्ति]⏎`
- **Correction:** 

### 126. `ide.msg_partial_lang` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [some word packs unavailable or invalid: see lang\*.lang]
- **Default (romanised Sanskrit), as printed:** `[kuchh shabda-pak anupalabdh ya ashuddh: lang\*.lang dekhein]⏎`
- **This pack, as printed:** `[केचन शब्द-पुटाः अनुपलब्धाः अशुद्धाः वा: lang\*.lang पश्यतु]⏎`
- **Correction:** 

### 127. `ide.msg_pipe_fail` — **UNSURE**

- **Where:** IDE output pane
- **Meaning:** [creating the process or the pipe failed]
- **Default (romanised Sanskrit), as printed:** `[prakriya ya nalika nirman asaphal]⏎`
- **This pack, as printed:** `[प्रक्रियायाः नालिकायाः वा निर्माणम् असफलम्]⏎`
- **Doubt:** 'नालिका' for a pipe (an operating-system channel) is a literal coinage.
- **Correction:** 

### 128. `ide.msg_more_output` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [output cut at 32 KiB]
- **Default (romanised Sanskrit), as printed:** `[phal 32 KiB par kata]⏎`
- **This pack, as printed:** `[फलं 32 KiB स्थाने कर्तितम्]⏎`
- **Correction:** 


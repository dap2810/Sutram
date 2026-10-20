# Review sheet: Tamil (தமிழ்)

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
  They go into `lang/tamil.sandesh`.

## Levels

| Level | Meaning |
|---|---|
| **LIKELY WRONG** | I think it is wrong, or it must be decided; please correct it first |
| **UNSURE** | I have a specific doubt, written under the message |
| **DRAFT** | no specific doubt, but still unverified |

**128 messages:** 0 LIKELY WRONG, 16 UNSURE, 112 DRAFT.

| # | Message | Level |
|---|---|---|
| 3 | `r48_msg_near` | UNSURE |
| 15 | `r4_msg_hint_old2` | UNSURE |
| 22 | `r7_msg_arity2` | UNSURE |
| 23 | `r7_msg_arity3` | UNSURE |
| 38 | `msg_array_oob` | UNSURE |
| 40 | `r65_msg_add` | UNSURE |
| 52 | `msg_lang_ok` | UNSURE |
| 53 | `msg_lang_fail` | UNSURE |
| 54 | `msg_shell_banner` | UNSURE |
| 61 | `msg_namespace_module_missing` | UNSURE |
| 69 | `msg_ast_overflow` | UNSURE |
| 85 | `r55_msg_proto_signature` | UNSURE |
| 91 | `mg_e_noexp2` | UNSURE |
| 92 | `mg_e_noexp3` | UNSURE |
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
சூத்திரம் - முழுமையான சூத்திரம்
பயன்பாடு:
  sutram <மூலம்.sm> <வெளியீடு.bin>         தொகுத்தல்
  sutram --check <மூலம்.sm>              சரிபார்ப்பு மட்டும், வெளியீட்டுக் கோப்பு இல்லை
  sutram --lang <தொகுப்பு> <மூலம்.sm> <வெளியீடு.bin>  மொழித் தொகுப்புடன்
  sutram -i                               உரையாடல்
  sutram --version                        பதிப்பு
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
சூத்திரம் 1.0 (v182) - முழுமையான சூத்திரம்
சம்ஸ்கிருத அடிப்படை மொழி -> x86-64 இயந்திர மொழி
```
- **Correction:** 

### 3. `r48_msg_near` — **UNSURE**

- **Where:** compiler: `--check`, a parse error
- **Meaning:** 'word' (the token where parsing failed)
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: shabd '=' + caret line`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: சொல் '=' + caret line`
- **This message alone:** `: Sutram Error [E_PARSE]: சொல் '`
- **Doubt:** 'word' stands for a token; check that it reads naturally before the quoted token.
- **Correction:** 

### 4. `r48_msg_ok` — **DRAFT**

- **Where:** compiler: `--check`, no errors
- **Meaning:** check: correct (no output file made)
- **Default (romanised Sanskrit), as printed:** `Sutram janch: shuddh (nirgat patra nahi)⏎`
- **This pack, as printed:** `சூத்திரம் சரிபார்ப்பு: சரி (வெளியீட்டுக் கோப்பு உருவாக்கப்படவில்லை)⏎`
- **Correction:** 

### 5. `r48_msg_errors` — **DRAFT**

- **Where:** compiler: `--check`, errors found
- **Meaning:** check: errors found; no output file made
- **Default (romanised Sanskrit), as printed:** `Sutram janch: dosh mile; nirgat patra nahi⏎`
- **This pack, as printed:** `சூத்திரம் சரிபார்ப்பு: பிழைகள் உள்ளன; வெளியீட்டுக் கோப்பு உருவாக்கப்படவில்லை⏎`
- **Correction:** 

### 6. `r48_msg_eof` — **DRAFT**

- **Where:** compiler: `--check`, error at end of file
- **Meaning:** <end of file>, shown in place of the token
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: shabd '<patra-ant>'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: சொல் '<கோப்பின் முடிவு>'`
- **This message alone:** `<கோப்பின் முடிவு>`
- **Correction:** 

### 7. `r50_msg_setchar_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** akshar_rakh needs 3 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: akshar_rakh: 3 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: akshar_rakh: 3 அளவுருக்கள் தேவை⏎`
- **In the pack file:** `Sutram Error: {kw:akshar_rakh}: 3 அளவுருக்கள் தேவை⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 8. `r52_msg_dvaram_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** dvaram needs 2 or 3 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: dvaram: 2 va 3 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: dvaram: 2 அல்லது 3 அளவுருக்கள் தேவை⏎`
- **In the pack file:** `Sutram Error: {kw:dvaram}: 2 அல்லது 3 அளவுருக்கள் தேவை⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 9. `r52_msg_charat_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** akshar needs 2 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: akshar: 2 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: akshar: 2 அளவுருக்கள் தேவை⏎`
- **In the pack file:** `Sutram Error: {kw:akshar}: 2 அளவுருக்கள் தேவை⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 10. `r52_msg_charcode_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** aksharank needs 1 or 2 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: aksharank: 1 va 2 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: aksharank: 1 அல்லது 2 அளவுருக்கள் தேவை⏎`
- **In the pack file:** `Sutram Error: {kw:aksharank}: 1 அல்லது 2 அளவுருக்கள் தேவை⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 11. `r48_msg_undefined` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown function 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_FUNCTION]: agyat prakriya 'foo'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_FUNCTION]: அறியாத செயல் 'foo'`
- **This message alone:** `: Sutram Error [E_UNDEFINED_FUNCTION]: அறியாத செயல் '`
- **Correction:** 

### 12. `r4_msg_undef` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown name 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_NAME]: agyat naam 'y'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_NAME]: அறியாத பெயர் 'y'`
- **This message alone:** `: Sutram Error [E_UNDEFINED_NAME]: அறியாத பெயர் '`
- **Correction:** 

### 13. `r4_msg_hint_decl` — **DRAFT**

- **Where:** compiler: hint after an unknown name
- **Meaning:** hint: declare it before use: vitti NAME = ...
- **Default (romanised Sanskrit), as printed:** `Sanket: prayog se purv ghoshana avashyak: vitti y = ...`
- **This pack, as printed:** `குறிப்பு: பயன்படுத்தும் முன் அறிவிப்பு தேவை: மாறி y = ...`
- **This message alone:** `குறிப்பு: பயன்படுத்தும் முன் அறிவிப்பு தேவை: மாறி `
- **In the pack file:** `குறிப்பு: பயன்படுத்தும் முன் அறிவிப்பு தேவை: {kw:vitti} `  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 14. `r4_msg_hint_old` — **DRAFT**

- **Where:** compiler: hint, opens two hints
- **Meaning:** hint: 'NAME…
- **Default (romanised Sanskrit), as printed:** `Sanket: 'anyatra' purana kunjishabd (v157 se purv); navin: 'anya'`
- **This pack, as printed:** `குறிப்பு: 'anyatra' பழைய முக்கியச்சொல் (v157 க்கு முந்தையது); புதியது: 'anya'`
- **This message alone:** `குறிப்பு: '`
- **Correction:** 

### 15. `r4_msg_hint_old2` — **UNSURE**

- **Where:** compiler: hint after an old keyword
- **Meaning:** 'OLD' is an old keyword (before v157); new: 'NEW'
- **Default (romanised Sanskrit), as printed:** `Sanket: 'anyatra' purana kunjishabd (v157 se purv); navin: 'anya'`
- **This pack, as printed:** `குறிப்பு: 'anyatra' பழைய முக்கியச்சொல் (v157 க்கு முந்தையது); புதியது: 'anya'`
- **This message alone:** `' பழைய முக்கியச்சொல் (v157 க்கு முந்தையது); புதியது: '`
- **Doubt:** 'முக்கியச்சொல்' for keyword; and 'v157 க்கு' puts the case suffix after a space.
- **Correction:** 

### 16. `r5_msg_field` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown field 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_UNKNOWN_FIELD]: agyat kshetra 'q'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_UNKNOWN_FIELD]: அறியாத புலம் 'q'`
- **This message alone:** `: Sutram Error [E_UNKNOWN_FIELD]: அறியாத புலம் '`
- **Correction:** 

### 17. `r7_msg_dup` — **DRAFT**

- **Where:** compiler
- **Meaning:** declared again: 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_DUPLICATE_NAME]: punah ghoshana 'x'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_DUPLICATE_NAME]: மீண்டும் அறிவிப்பு 'x'`
- **This message alone:** `: Sutram Error [E_DUPLICATE_NAME]: மீண்டும் அறிவிப்பு '`
- **Correction:** 

### 18. `r7_msg_dup_hint` — **DRAFT**

- **Where:** compiler: hint after a duplicate
- **Meaning:** 'NAME' is already declared; to give it a new value: NAME = ...
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' pahle se ghoshit hai; naya man dene ke liye: x = ...`
- **This pack, as printed:** `குறிப்பு: 'x' ஏற்கனவே அறிவிக்கப்பட்டது; புதிய மதிப்பு தர: x = ...`
- **This message alone:** `' ஏற்கனவே அறிவிக்கப்பட்டது; புதிய மதிப்பு தர: `
- **Correction:** 

### 19. `r7_msg_field_amb` — **DRAFT**

- **Where:** compiler
- **Meaning:** field 'NAME' (is ambiguous)
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_AMBIGUOUS_FIELD]: kshetra 'x'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_AMBIGUOUS_FIELD]: புலம் 'x'`
- **This message alone:** `: Sutram Error [E_AMBIGUOUS_FIELD]: புலம் '`
- **Correction:** 

### 20. `r7_msg_field_amb_hint` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** 'NAME' is at different places in two rachanas; give it a different name in each
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' do rachana me alag sthan par hai; har rachana me alag naam rakhein⏎`
- **This pack, as printed:** `குறிப்பு: 'x' இரண்டு அமைப்புகளில் வெவ்வேறு இடத்தில் உள்ளது; ஒவ்வொரு அமைப்பிலும் வேறு பெயர் வையுங்கள்⏎`
- **This message alone:** `' இரண்டு அமைப்புகளில் வெவ்வேறு இடத்தில் உள்ளது; ஒவ்வொரு அமைப்பிலும் வேறு பெயர் வையுங்கள்⏎`
- **Correction:** 

### 21. `r7_msg_field_dup_hint` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** 'NAME' is already in this rachana
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' is rachana me pahle se hai⏎`
- **This pack, as printed:** `குறிப்பு: 'x' இந்த அமைப்பில் ஏற்கனவே உள்ளது⏎`
- **This message alone:** `' இந்த அமைப்பில் ஏற்கனவே உள்ளது⏎`
- **Correction:** 

### 22. `r7_msg_arity2` — **UNSURE**

- **Where:** compiler: middle of the arity error
- **Meaning:** 'f' [was given] N arguments; in the signature M
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' ko 1 tark diye; hastakshar me 2`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' க்கு 1 அளவுருக்கள் தரப்பட்டன; கையொப்பத்தில் 2`
- **This message alone:** `' க்கு `
- **Doubt:** Word order is fixed by the code: 'NAME' <this> N <arity3> M. Check that the sentence reads naturally around the name and the two numbers.
- **Doubt:** The case suffix is printed after a space ('f' <suffix>); written Tamil normally attaches it to the word (with a quoted code name, say which you prefer). The checker keeps the default's leading "' ", so fixing this needs that rule relaxed for this message.
- **Correction:** 

### 23. `r7_msg_arity3` — **UNSURE**

- **Where:** compiler: middle of the arity error
- **Meaning:** … N arguments given; in the signature M
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' ko 1 tark diye; hastakshar me 2`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' க்கு 1 அளவுருக்கள் தரப்பட்டன; கையொப்பத்தில் 2`
- **This message alone:** ` அளவுருக்கள் தரப்பட்டன; கையொப்பத்தில் `
- **Doubt:** 'அளவுரு' (parameter) is used for an argument; 'கையொப்பம்' for a signature is a calque.
- **Doubt:** The count is printed before this text and is often 1 ('f' … 1 …): the noun is in the plural form, so '1 <plural>' may read wrong. A fragment cannot change with the number.
- **Correction:** 

### 24. `r7_msg_arity_hint` — **DRAFT**

- **Where:** compiler: hint after the arity error
- **Meaning:** hint: give exactly as many arguments as the function's definition has
- **Default (romanised Sanskrit), as printed:** `Sanket: utne hi tark dein jitne prakriya ki paribhasha me hain⏎`
- **This pack, as printed:** `குறிப்பு: செயலின் வரையறையில் உள்ள அளவுருக்களின் எண்ணிக்கையிலேயே தாருங்கள்⏎`
- **Correction:** 

### 25. `r7_msg_mod_missing` — **DRAFT**

- **Where:** compiler
- **Meaning:** import file not found: NAME
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_MISSING]: yoj patra aprapt: ganit`
- **This pack, as printed:** `Sutram Error [E_MODULE_MISSING]: இணைப்புக் கோப்பு கிடைக்கவில்லை: ganit`
- **This message alone:** `Sutram Error [E_MODULE_MISSING]: இணைப்புக் கோப்பு கிடைக்கவில்லை: `
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

குறிப்பு: <பெயர்>.smlib lib/ இல் அல்லது மூலக் கோப்பின் அடைவில் இருக்க வேண்டும்
```
- **Correction:** 

### 27. `r7_msg_hint_block` — **DRAFT**

- **Where:** compiler: hint after an unknown name
- **Meaning:** 'NAME' is declared inside a block { } or a loop; it is not visible outside it
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' ek khand { } ya chakra me ghoshit hai; uske bahar drishya nahi⏎`
- **This pack, as printed:** `குறிப்பு: 'x' ஒரு தொகுதி { } அல்லது மீண்டும் உள்ளே அறிவிக்கப்பட்டது; அதற்கு வெளியே தெரியாது⏎`
- **This message alone:** `' ஒரு தொகுதி { } அல்லது மீண்டும் உள்ளே அறிவிக்கப்பட்டது; அதற்கு வெளியே தெரியாது⏎`
- **In the pack file:** `' ஒரு தொகுதி { } அல்லது {kw:chakra} உள்ளே அறிவிக்கப்பட்டது; அதற்கு வெளியே தெரியாது⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 28. `r5_msg_field_hint` — **DRAFT**

- **Where:** compiler: hint, opens the field hint
- **Meaning:** hint: 'NAME…
- **Default (romanised Sanskrit), as printed:** `Sanket: 'q' kisi rachana ka kshetra nahi⏎`
- **This pack, as printed:** `குறிப்பு: 'q' எந்த அமைப்பின் புலமும் அல்ல⏎`
- **This message alone:** `குறிப்பு: '`
- **Correction:** 

### 29. `r5_msg_field_hint2` — **DRAFT**

- **Where:** compiler: hint after an unknown field
- **Meaning:** 'NAME' is not a field of any rachana
- **Default (romanised Sanskrit), as printed:** `Sanket: 'q' kisi rachana ka kshetra nahi⏎`
- **This pack, as printed:** `குறிப்பு: 'q' எந்த அமைப்பின் புலமும் அல்ல⏎`
- **This message alone:** `' எந்த அமைப்பின் புலமும் அல்ல⏎`
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

Sutram Error: இலக்கணப் பிழை, வரி 
```
- **Correction:** 

### 31. `msg_err_near` — **DRAFT**

- **Where:** compiler: a parse error
- **Meaning:** , word 'TOKEN'
- **Default (romanised Sanskrit), as printed:** `⏎Sutram Error: vyakaran dosh, pankti 3:11, shabd '='`
- **This pack, as printed:** `⏎Sutram Error: இலக்கணப் பிழை, வரி 3:11, சொல் '='`
- **This message alone:** `, சொல் '`
- **Correction:** 

### 32. `msg_err_eof` — **DRAFT**

- **Where:** compiler: a parse error at the end of the file
- **Meaning:** end of file, shown in place of the token
- **Default (romanised Sanskrit), as printed:** `⏎Sutram Error: vyakaran dosh, pankti 6:1, shabd 'patra-ant'`
- **This pack, as printed:** `⏎Sutram Error: இலக்கணப் பிழை, வரி 6:1, சொல் 'கோப்பின் முடிவு'`
- **This message alone:** `கோப்பின் முடிவு`
- **Correction:** 

### 33. `msg_err_hint` — **DRAFT**

- **Where:** compiler: hint after a parse error
- **Meaning:** hint: check the word and the grammar at this place
- **Default (romanised Sanskrit), as printed:** `Sanket: is sthan par shabd aur vyakaran dekho.⏎`
- **This pack, as printed:** `குறிப்பு: இந்த இடத்தில் சொல்லையும் இலக்கணத்தையும் சரிபாருங்கள்.⏎`
- **Correction:** 

### 34. `msg_err_arg_limit` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** hint: a function takes at most 6 arguments
- **Default (romanised Sanskrit), as printed:** `Sanket: prakriya adhiktam 6 tark lete hain.⏎`
- **This pack, as printed:** `குறிப்பு: செயல் அதிகபட்சம் 6 அளவுருக்களை ஏற்கும்.⏎`
- **Correction:** 

### 35. `msg_err_duplicate_func` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** hint: the function is defined twice (name clash)
- **Default (romanised Sanskrit), as printed:** `Sanket: dohri prakriya paribhasha (naam takkar).⏎`
- **This pack, as printed:** `குறிப்பு: செயலுக்கு இரட்டை வரையறை (பெயர் மோதல்).⏎`
- **Correction:** 

### 36. `msg_duplicate_func` — **DRAFT**

- **Where:** compiler
- **Meaning:** function defined again: NAME
- **Default (romanised Sanskrit), as printed:** `Sutram Error: punah prakriya paribhasha: f`
- **This pack, as printed:** `Sutram Error: செயலுக்கு மீண்டும் வரையறை: f`
- **This message alone:** `Sutram Error: செயலுக்கு மீண்டும் வரையறை: `
- **Correction:** 

### 37. `msg_undefined_func` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown function: NAME
- **Default (romanised Sanskrit), as printed:** `Sutram Error: agyat prakriya: f`
- **This pack, as printed:** `Sutram Error: அறியாத செயல்: f`
- **This message alone:** `Sutram Error: அறியாத செயல்: `
- **Correction:** 

### 38. `msg_array_oob` — **UNSURE**

- **Where:** the compiled program, at run time
- **Meaning:** mala index out of bounds
- **Default (romanised Sanskrit), as printed:** `Sutram Error: mala ank seema atikram⏎`
- **This pack, as printed:** `Sutram Error: வரிசைப்பட சுட்டெண் வரம்புக்கு வெளியே⏎`
- **In the pack file:** `Sutram Error: {kw:mala} சுட்டெண் வரம்புக்கு வெளியே⏎`  (`{kw:…}` is the pack's own keyword)
- **Doubt:** The pack's word for mala is 'வரிசைப்பட', which looks like a truncated verb form; it appears wherever the keyword is shown. That is lang/tamil.lang's choice and should be checked there.
- **Correction:** 

### 39. `msg_kosh_required` — **DRAFT**

- **Where:** compiler
- **Meaning:** a kosh function needs a kosh variable
- **Default (romanised Sanskrit), as printed:** `Sutram Error: kosh prakriya hetu kosh-vitti avashyak⏎`
- **This pack, as printed:** `Sutram Error: கோசம் செயலுக்கு கோசம் மாறி தேவை⏎`
- **In the pack file:** `Sutram Error: {kw:kosh} செயலுக்கு {kw:kosh} {kw:vitti} தேவை⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 40. `r65_msg_add` — **UNSURE**

- **Where:** the program, `trap` build
- **Meaning:** overflow in an addition
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: yog atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: கூட்டலில் வழிதல்⏎`
- **This message alone:** `: கூட்டலில் வழிதல்⏎`
- **Doubt:** 'வழிதல்' for an integer overflow (all seven trap messages); check.
- **Correction:** 

### 41. `r65_msg_sub` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a subtraction
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: nyun atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: கழித்தலில் வழிதல்⏎`
- **This message alone:** `: கழித்தலில் வழிதல்⏎`
- **Correction:** 

### 42. `r65_msg_mul` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a multiplication
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: gun atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: பெருக்கலில் வழிதல்⏎`
- **This message alone:** `: பெருக்கலில் வழிதல்⏎`
- **Correction:** 

### 43. `r65_msg_div` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** division by zero
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: shunya se bhajan⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: பூஜ்ஜியத்தால் வகுத்தல்⏎`
- **This message alone:** `: பூஜ்ஜியத்தால் வகுத்தல்⏎`
- **Correction:** 

### 44. `r65_msg_mod` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** remainder by zero
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: shunya se shesh⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: பூஜ்ஜியத்தால் மீதி⏎`
- **This message alone:** `: பூஜ்ஜியத்தால் மீதி⏎`
- **Correction:** 

### 45. `r65_msg_div_overflow` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a division
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: bhajan atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: வகுத்தலில் வழிதல்⏎`
- **This message alone:** `: வகுத்தலில் வழிதல்⏎`
- **Correction:** 

### 46. `r65_msg_mod_overflow` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a remainder
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: shesh atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: மீதியில் வழிதல்⏎`
- **This message alone:** `: மீதியில் வழிதல்⏎`
- **Correction:** 

### 47. `msg_kosh_empty` — **DRAFT**

- **Where:** the program, at run time
- **Meaning:** kosh_pop from an empty kosh
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rikta kosh se kosh_pop⏎`
- **This pack, as printed:** `Sutram Error: காலி கோசத்திலிருந்து kosh_pop⏎`
- **In the pack file:** `Sutram Error: காலி கோசத்திலிருந்து {kw:kosh_pop}⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 48. `msg_kosh_peek_empty` — **DRAFT**

- **Where:** the program, at run time
- **Meaning:** kosh_peek from an empty kosh
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rikta kosh se kosh_peek⏎`
- **This pack, as printed:** `Sutram Error: காலி கோசத்திலிருந்து kosh_peek⏎`
- **In the pack file:** `Sutram Error: காலி கோசத்திலிருந்து {kw:kosh_peek}⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 49. `msg_kosh_dequeue_empty` — **DRAFT**

- **Where:** the program, at run time
- **Meaning:** kosh_dequeue from an empty kosh
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rikta kosh se kosh_dequeue⏎`
- **This pack, as printed:** `Sutram Error: காலி கோசத்திலிருந்து kosh_dequeue⏎`
- **In the pack file:** `Sutram Error: காலி கோசத்திலிருந்து {kw:kosh_dequeue}⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 50. `msg_kosh_param_type` — **DRAFT**

- **Where:** compiler
- **Meaning:** kosh argument: element type differs
- **Default (romanised Sanskrit), as printed:** `Sutram Error: kosh tark: tatv prakar bhinn⏎`
- **This pack, as printed:** `Sutram Error: கோச அளவுரு: உறுப்பு வகை வேறு⏎`
- **Correction:** 

### 51. `msg_kosh_param_push` — **DRAFT**

- **Where:** compiler
- **Meaning:** kosh_push is not supported on a kosh argument
- **Default (romanised Sanskrit), as printed:** `Sutram Error: kosh tark par kosh_push asamarthit⏎`
- **This pack, as printed:** `Sutram Error: கோச அளவுருவில் kosh_push ஆதரிக்கப்படவில்லை⏎`
- **In the pack file:** `Sutram Error: கோச அளவுருவில் {kw:kosh_push} ஆதரிக்கப்படவில்லை⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 52. `msg_lang_ok` — **UNSURE**

- **Where:** compiler: every run with `--lang`
- **Meaning:** language pack found: PACK
- **Default (romanised Sanskrit), as printed:** `Bhasha pak prapt: hindi`
- **This pack, as printed:** `மொழித் தொகுப்பு கிடைத்தது: hindi`
- **This message alone:** `மொழித் தொகுப்பு கிடைத்தது: `
- **Doubt:** 'pack' (the language-pack file) has no settled native word; check the term.
- **Correction:** 

### 53. `msg_lang_fail` — **UNSURE**

- **Where:** compiler
- **Meaning:** warning: language pack not found: PACK
- **Default (romanised Sanskrit), as printed:** `Chetavani: bhasha pak nahi mila: hindi`
- **This pack, as printed:** `எச்சரிக்கை: மொழித் தொகுப்பு கிடைக்கவில்லை: hindi`
- **This message alone:** `எச்சரிக்கை: மொழித் தொகுப்பு கிடைக்கவில்லை: `
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
சூத்திரம் உரையாடல் v1.0 - முழுமையான சூத்திரம்
சூத்திரம் கூற்றை எழுதி Enter அழுத்துங்கள். உடனே இயங்கும்.
கட்டளைகள்: sahayata (உதவி) | nirgat (வெளியேறு) | sarvam (அனைத்தும் காண்)
```
- **Doubt:** 'Enter' is kept as the key's label; the verb for pressing a key should be checked.
- **Correction:** 

### 55. `msg_shell_bye` — **DRAFT**

- **Where:** compiler: leaving `sutram -i`
- **Meaning:** greeting; session ended
- **Default (romanised Sanskrit), as printed:** `Namaste! Satra samapt.⏎`
- **This pack, as printed:** `வணக்கம்! அமர்வு முடிந்தது.⏎`
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
சூத்திரம் உரையாடல் உதவி:
  எழுது("வணக்கம்\n")            உரையை எழுதும்
  மாறி x = 5             மாறி அறிவிப்பு
  எழுது(x + 3)            மதிப்பை எழுதும்
  மீண்டும் i = 0 முதல் 5 { எழுது(i) }   மீள்செயல்
  வரிசைப்பட arr[5]             வரிசைப்பட அறிவிப்பு
  sarvam                  முழு நிரலைக் காண்
  nirgat                  உரையாடலிலிருந்து வெளியேறு
```
- **In the pack file:** `சூத்திரம் உரையாடல் உதவி:⏎  {kw:likha}("வணக்கம்\n")            உரையை எழுதும்⏎  {kw:vitti} x = 5             {kw:vitti} அறிவிப்பு⏎  {kw:likha}(x + 3)            மதிப்பை எழுதும்⏎  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   மீள்செயல்⏎  {kw:mala} arr[5]             {kw:mala} அறிவிப்பு⏎  sarvam                  முழு நிரலைக் காண்⏎  nirgat                  உரையாடலிலிருந்து வெளியேறு⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 57. `msg_open_err` — **DRAFT**

- **Where:** compiler
- **Meaning:** input (source) file not found
- **Default (romanised Sanskrit), as printed:** `Sutram Error: nivesh patra aprapt⏎`
- **This pack, as printed:** `Sutram Error: மூலக் கோப்பு கிடைக்கவில்லை⏎`
- **Correction:** 

### 58. `msg_ok` — **DRAFT**

- **Where:** compiler: a successful compile
- **Meaning:** done: N bytes compiled
- **Default (romanised Sanskrit), as printed:** `Siddh: 297 baait sankalit⏎`
- **This pack, as printed:** `வெற்றி: 297 பைட் தொகுக்கப்பட்டது⏎`
- **This message alone:** `வெற்றி: `
- **Correction:** 

### 59. `msg_bytes` — **DRAFT**

- **Where:** compiler: a successful compile
- **Meaning:** … bytes compiled
- **Default (romanised Sanskrit), as printed:** `Siddh: 297 baait sankalit⏎`
- **This pack, as printed:** `வெற்றி: 297 பைட் தொகுக்கப்பட்டது⏎`
- **This message alone:** ` பைட் தொகுக்கப்பட்டது⏎`
- **Correction:** 

### 60. `msg_namespace_error` — **DRAFT**

- **Where:** compiler
- **Meaning:** invalid import (form: module@alias, alias up to 31 bytes)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ashuddh yoj (roop: ghatak@upanaam, upanaam 31 baait tak)⏎`
- **This pack, as printed:** `Sutram Error: தவறான இணைப்பு (வடிவம்: கூறு@மாற்றுப்பெயர், மாற்றுப்பெயர் 31 பைட் வரை)⏎`
- **In the pack file:** `Sutram Error: தவறான {kw:yoj} (வடிவம்: கூறு@மாற்றுப்பெயர், மாற்றுப்பெயர் 31 பைட் வரை)⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 61. `msg_namespace_module_missing` — **UNSURE**

- **Where:** compiler
- **Meaning:** module file not found
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ghatak patra aprapt⏎`
- **This pack, as printed:** `Sutram Error: கூறுக் கோப்பு கிடைக்கவில்லை⏎`
- **Doubt:** 'கூறு' (component) for a module; check.
- **Correction:** 

### 62. `msg_namespace_alias_reuse` — **DRAFT**

- **Where:** compiler
- **Meaning:** alias already used (for another module)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: upanaam purv-niyukt (anya ghatak)⏎`
- **This pack, as printed:** `Sutram Error: மாற்றுப்பெயர் ஏற்கனவே பயன்பாட்டில் (வேறு கூறுக்கு)⏎`
- **Correction:** 

### 63. `r51_alias_conflict` — **DRAFT**

- **Where:** compiler
- **Meaning:** alias already used (for another module)
- **Default (romanised Sanskrit), as printed:** `prog.sm:2: Sutram Error [E_MODULE_ALIAS_REUSE]: upanaam purv-niyukt (anya ghatak)⏎`
- **This pack, as printed:** `prog.sm:2: Sutram Error [E_MODULE_ALIAS_REUSE]: மாற்றுப்பெயர் ஏற்கனவே பயன்பாட்டில் (வேறு கூறுக்கு)⏎`
- **This message alone:** `: Sutram Error [E_MODULE_ALIAS_REUSE]: மாற்றுப்பெயர் ஏற்கனவே பயன்பாட்டில் (வேறு கூறுக்கு)⏎`
- **Correction:** 

### 64. `msg_namespace_func_limit` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of module function names exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ghatak prakriya-naam seema atikram⏎`
- **This pack, as printed:** `Sutram Error: கூறின் செயல்-பெயர் வரம்பு மீறல்⏎`
- **Correction:** 

### 65. `msg_import_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the expanded source exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: vistarit srot seema atikram⏎`
- **This pack, as printed:** `Sutram Error: விரிவாக்கப்பட்ட மூல வரம்பு மீறல்⏎`
- **Correction:** 

### 66. `graph_cycle_prefix` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** import cycle: a -> b -> a
- **Default (romanised Sanskrit), as printed:** `prog.sm:1: Sutram Error [E_MODULE_CYCLE] yoj chakra: a -> b -> a`
- **This pack, as printed:** `prog.sm:1: Sutram Error [E_MODULE_CYCLE] இணைப்புச் சுழற்சி: a -> b -> a`
- **This message alone:** `இணைப்புச் சுழற்சி: `
- **Correction:** 

### 67. `graph_missing_prefix` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** import file not found: NAME
- **Default (romanised Sanskrit), as printed:** `prog.sm:1: Sutram Error [E_MODULE_MISSING] yoj patra aprapt: ganit`
- **This pack, as printed:** `prog.sm:1: Sutram Error [E_MODULE_MISSING] இணைப்புக் கோப்பு கிடைக்கவில்லை: ganit`
- **This message alone:** `இணைப்புக் கோப்பு கிடைக்கவில்லை: `
- **Correction:** 

### 68. `graph_invalid_prefix` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** invalid module name
- **Default (romanised Sanskrit), as printed:** `prog.sm:1: Sutram Error [E_MODULE_INVALID] ashuddh ghatak naam`
- **This pack, as printed:** `prog.sm:1: Sutram Error [E_MODULE_INVALID] தவறான கூறுப் பெயர்`
- **This message alone:** `தவறான கூறுப் பெயர்`
- **Correction:** 

### 69. `msg_ast_overflow` — **UNSURE**

- **Where:** compiler
- **Meaning:** limit of the syntax tree exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: vakya-vriksh seema atikram⏎`
- **This pack, as printed:** `Sutram Error: தொடரியல் மர வரம்பு மீறல்⏎`
- **Doubt:** 'syntax tree' is a coined technical term here; check it.
- **Correction:** 

### 70. `msg_func_params_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the function parameter list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya tark-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: செயல் அளவுருப் பட்டியல் வரம்பு மீறல்⏎`
- **Correction:** 

### 71. `msg_var_table_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the variable list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: vitti-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: மாறி பட்டியல் வரம்பு மீறல்⏎`
- **In the pack file:** `Sutram Error: {kw:vitti} பட்டியல் வரம்பு மீறல்⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 72. `msg_func_table_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the function list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: செயல் பட்டியல் வரம்பு மீறல்⏎`
- **Correction:** 

### 73. `msg_patch_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the call list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: aahvan-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: அழைப்புப் பட்டியல் வரம்பு மீறல்⏎`
- **Correction:** 

### 74. `msg_func_defs_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the function definition list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya paribhasha-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: செயல் வரையறைப் பட்டியல் வரம்பு மீறல்⏎`
- **Correction:** 

### 75. `msg_r9_guna_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** guna limit exceeded (1024)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: guna seema atikram (1024)⏎`
- **This pack, as printed:** `Sutram Error: குணம் வரம்பு மீறல் (1024)⏎`
- **In the pack file:** `Sutram Error: {kw:guna} வரம்பு மீறல் (1024)⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 76. `msg_break_patch_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** too many krama (break) in a loop
- **Default (romanised Sanskrit), as printed:** `Sutram Error: chakra me krama seema atikram⏎`
- **This pack, as printed:** `Sutram Error: மீண்டும் இல் வரிசை வரம்பு மீறல்⏎`
- **In the pack file:** `Sutram Error: {kw:chakra} இல் {kw:krama} வரம்பு மீறல்⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 77. `msg_continue_patch_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** too many agrim (continue) in a loop
- **Default (romanised Sanskrit), as printed:** `Sutram Error: chakra me agrim seema atikram⏎`
- **This pack, as printed:** `Sutram Error: மீண்டும் இல் தொடர் வரம்பு மீறல்⏎`
- **In the pack file:** `Sutram Error: {kw:chakra} இல் {kw:agrim} வரம்பு மீறல்⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 78. `msg_code_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the machine code exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: yantra-bhasha seema atikram⏎`
- **This pack, as printed:** `Sutram Error: இயந்திர மொழி வரம்பு மீறல்⏎`
- **Correction:** 

### 79. `msg_rachana_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the rachana list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rachana-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: அமைப்பு பட்டியல் வரம்பு மீறல்⏎`
- **In the pack file:** `Sutram Error: {kw:rachana} பட்டியல் வரம்பு மீறல்⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 80. `msg_rachana_fields_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of rachana fields exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rachana kshetra seema atikram⏎`
- **This pack, as printed:** `Sutram Error: அமைப்பு புல வரம்பு மீறல்⏎`
- **In the pack file:** `Sutram Error: {kw:rachana} புல வரம்பு மீறல்⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 81. `msg_block_nesting_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of block depth exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: khand gahrai seema atikram⏎`
- **This pack, as printed:** `Sutram Error: தொகுதி ஆழ வரம்பு மீறல்⏎`
- **Correction:** 

### 82. `msg_block_stmt_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of statements in a block exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: khand kathan seema atikram⏎`
- **This pack, as printed:** `Sutram Error: தொகுதியில் கூற்று வரம்பு மீறல்⏎`
- **Correction:** 

### 83. `r55_msg_proto_duplicate` — **DRAFT**

- **Where:** compiler
- **Meaning:** function forward-declared again
- **Default (romanised Sanskrit), as printed:** `Sutram Error: punah prakriya purv-ghoshana⏎`
- **This pack, as printed:** `Sutram Error: செயலுக்கு மீண்டும் முன்-அறிவிப்பு⏎`
- **Correction:** 

### 84. `r55_msg_proto_missing` — **DRAFT**

- **Where:** compiler
- **Meaning:** function forward-declared but never defined
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya purv-ghoshana paribhasha-rahit⏎`
- **This pack, as printed:** `Sutram Error: செயலுக்கு முன்-அறிவிப்பு உள்ளது, வரையறை இல்லை⏎`
- **Correction:** 

### 85. `r55_msg_proto_signature` — **UNSURE**

- **Where:** compiler
- **Meaning:** forward declaration and definition differ (arguments/type)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya purv-ghoshana va paribhasha bhinn (tark/prakar)⏎`
- **This pack, as printed:** `Sutram Error: செயலின் முன்-அறிவிப்பும் வரையறையும் வேறுபடுகின்றன (அளவுரு/வகை)⏎`
- **Doubt:** 'forward declaration' (a prototype) is a coined term; check it.
- **Correction:** 

### 86. `r55_msg_proto_capacity` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of function forward declarations exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya purv-ghoshana seema atikram⏎`
- **This pack, as printed:** `Sutram Error: செயல் முன்-அறிவிப்பு வரம்பு மீறல்⏎`
- **Correction:** 

### 87. `r56_msg_global_capacity` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of module-level variables exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ghatak-star vitti seema atikram⏎`
- **This pack, as printed:** `Sutram Error: கூறு-நிலை மாறி வரம்பு மீறல்⏎`
- **In the pack file:** `Sutram Error: கூறு-நிலை {kw:vitti} வரம்பு மீறல்⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 88. `r56_msg_global_duplicate` — **DRAFT**

- **Where:** compiler
- **Meaning:** module-level variable name declared again
- **Default (romanised Sanskrit), as printed:** `Sutram Error: punah ghatak-star vitti naam⏎`
- **This pack, as printed:** `Sutram Error: கூறு-நிலை மாறி பெயர் மீண்டும்⏎`
- **In the pack file:** `Sutram Error: கூறு-நிலை {kw:vitti} பெயர் மீண்டும்⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 89. `r56_msg_patch_capacity` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of global value references exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: sarvatrik mulya sandarbh seema atikram⏎`
- **This pack, as printed:** `Sutram Error: பொது மதிப்புக் குறிப்பு வரம்பு மீறல்⏎`
- **Correction:** 

### 90. `mg_e_cycle` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** import cycle: a -> b -> a
- **Default (romanised Sanskrit), as printed:** `prog.sm:1:Sutram Error [E_MODULE_CYCLE]: yoj chakra: a -> b -> a`
- **This pack, as printed:** `prog.sm:1:Sutram Error [E_MODULE_CYCLE]: இணைப்புச் சுழற்சி: a -> b -> a`
- **This message alone:** `Sutram Error [E_MODULE_CYCLE]: இணைப்புச் சுழற்சி: `
- **Correction:** 

### 91. `mg_e_noexp2` — **UNSURE**

- **Where:** compiler: middle of 'not exported'
- **Meaning:** 'SYM' [from] module 'MOD' [is] not exported
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' ghatak 'vec' se aniryat⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' கூறு 'vec' இலிருந்து ஏற்றுமதி செய்யப்படவில்லை⏎`
- **This message alone:** `' கூறு '`
- **Doubt:** Order fixed by the code: 'SYM' <this> 'MOD' <noexp3>. Check that 'SYM … MOD … not exported' reads as one sentence.
- **Correction:** 

### 92. `mg_e_noexp3` — **UNSURE**

- **Where:** compiler: end of 'not exported'
- **Meaning:** … not exported from module MOD
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' ghatak 'vec' se aniryat⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' கூறு 'vec' இலிருந்து ஏற்றுமதி செய்யப்படவில்லை⏎`
- **This message alone:** `' இலிருந்து ஏற்றுமதி செய்யப்படவில்லை⏎`
- **Doubt:** The case suffix is printed after a space ('f' <suffix>); written Tamil normally attaches it to the word (with a quoted code name, say which you prefer). The checker keeps the default's leading "' ", so fixing this needs that rule relaxed for this message.
- **Correction:** 

### 93. `mg_e_dupexp1` — **DRAFT**

- **Where:** compiler
- **Meaning:** exported again: 'SYM', module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: punah niryat 'thing', ghatak 'dup'`
- **This pack, as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: மீண்டும் ஏற்றுமதி 'thing', கூறு 'dup'`
- **This message alone:** `Sutram Error [E_MODULE_DUP_EXPORT]: மீண்டும் ஏற்றுமதி '`
- **Correction:** 

### 94. `mg_e_dupexp2` — **DRAFT**

- **Where:** compiler: middle
- **Meaning:** …, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: punah niryat 'thing', ghatak 'dup'`
- **This pack, as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: மீண்டும் ஏற்றுமதி 'thing', கூறு 'dup'`
- **This message alone:** `', கூறு '`
- **Correction:** 

### 95. `mg_e_undef1` — **DRAFT**

- **Where:** compiler
- **Meaning:** export 'SYM' has no definition, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: niryat 'thing' paribhasha-rahit, ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: ஏற்றுமதி 'thing' வரையறுக்கப்படவில்லை, கூறு 'vec'`
- **This message alone:** `Sutram Error [E_EXPORT_UNDEFINED]: ஏற்றுமதி '`
- **Correction:** 

### 96. `mg_e_undef2` — **DRAFT**

- **Where:** compiler: middle
- **Meaning:** … has no definition, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: niryat 'thing' paribhasha-rahit, ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: ஏற்றுமதி 'thing' வரையறுக்கப்படவில்லை, கூறு 'vec'`
- **This message alone:** `' வரையறுக்கப்படவில்லை, கூறு '`
- **Correction:** 

### 97. `mg_e_unknown1` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown symbol 'SYM', module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: agyat sanket 'thing', ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: அறியாத குறியீடு 'thing', கூறு 'vec'`
- **This message alone:** `Sutram Error [E_EXPORT_UNDEFINED]: அறியாத குறியீடு '`
- **Correction:** 

### 98. `mg_e_unknown2` — **DRAFT**

- **Where:** compiler: middle
- **Meaning:** …, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: agyat sanket 'thing', ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: அறியாத குறியீடு 'thing', கூறு 'vec'`
- **This message alone:** `', கூறு '`
- **Correction:** 

### 99. `mg_e_depth` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of import depth exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_DEPTH]: yoj gahrai seema atikram⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_DEPTH]: இணைப்பு ஆழ வரம்பு மீறல்⏎`
- **Correction:** 

### 100. `mg_e_valias1` — **DRAFT**

- **Where:** compiler
- **Meaning:** a v1 module 'MOD' needs an alias: yoj MOD@upanaam
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 ghatak 'vec' upanaam avashyak: yoj vec@upanaam`
- **This pack, as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 கூறு 'vec' க்கு மாற்றுப்பெயர் தேவை: இணைப்பு vec@upanaam`
- **This message alone:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 கூறு '`
- **Correction:** 

### 101. `mg_e_valias2` — **UNSURE**

- **Where:** compiler: middle
- **Meaning:** … needs an alias: yoj MOD@upanaam
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 ghatak 'vec' upanaam avashyak: yoj vec@upanaam`
- **This pack, as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 கூறு 'vec' க்கு மாற்றுப்பெயர் தேவை: இணைப்பு vec@upanaam`
- **This message alone:** `' க்கு மாற்றுப்பெயர் தேவை: இணைப்பு `
- **In the pack file:** `' க்கு மாற்றுப்பெயர் தேவை: {kw:yoj} `  (`{kw:…}` is the pack's own keyword)
- **Doubt:** The case suffix is printed after a space ('f' <suffix>); written Tamil normally attaches it to the word (with a quoted code name, say which you prefer). The checker keeps the default's leading "' ", so fixing this needs that rule relaxed for this message.
- **Correction:** 

### 102. `mg_e_limit` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of modules/imports exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_LIMIT]: ghatak/yoj seema atikram⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_LIMIT]: கூறு/இணைப்பு வரம்பு மீறல்⏎`
- **Correction:** 

### 103. `r66_msg_bad_utf8` — **DRAFT**

- **Where:** compiler
- **Meaning:** invalid or broken Indian-script name
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_UTF8]: ashuddh ya khandit bharatiya naam⏎`
- **This pack, as printed:** `Sutram Error [E_UTF8]: தவறான அல்லது உடைந்த இந்தியப் பெயர்⏎`
- **Correction:** 

### 104. `r68_utf8_tail` — **DRAFT**

- **Where:** compiler
- **Meaning:** invalid or broken UTF-8 in the source
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_UTF8]: prog.sm:2: srot me ashuddh ya khandit UTF-8⏎`
- **This pack, as printed:** `Sutram Error [E_UTF8]: prog.sm:2: மூலத்தில் தவறான அல்லது உடைந்த UTF-8⏎`
- **This message alone:** `: மூலத்தில் தவறான அல்லது உடைந்த UTF-8⏎`
- **Correction:** 

### 105. `r68_value_tail` — **DRAFT**

- **Where:** compiler
- **Meaning:** an abbreviation is not a value: 'वि॰'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_ABBREVIATION_VALUE]: prog.sm:2: sankshep shabd mulya nahi: 'वि॰'`
- **This pack, as printed:** `Sutram Error [E_ABBREVIATION_VALUE]: prog.sm:2: சுருக்கச் சொல் மதிப்பு அல்ல: 'वि॰'`
- **This message alone:** `: சுருக்கச் சொல் மதிப்பு அல்ல: '`
- **Correction:** 

### 106. `ide.st_pankti_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** line N (start of the status line)
- **Default (romanised Sanskrit), as printed:** `pankti 12   stambh 4   |   bhasha: …`
- **This pack, as printed:** `வரி 12   நெடுவரிசை 4   |   மொழி: …`
- **This message alone:** `வரி `
- **Correction:** 

### 107. `ide.st_stambh_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** column N
- **Default (romanised Sanskrit), as printed:** `pankti 12   stambh 4   |   bhasha: …`
- **This pack, as printed:** `வரி 12   நெடுவரிசை 4   |   மொழி: …`
- **This message alone:** `   நெடுவரிசை `
- **Correction:** 

### 108. `ide.st_bhasha_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** | language: NAME
- **Default (romanised Sanskrit), as printed:** `…4   |   bhasha: हिन्दी`
- **This pack, as printed:** `…4   |   மொழி: हिन्दी`
- **This message alone:** `   |   மொழி: `
- **Correction:** 

### 109. `ide.st_akshara_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** | letters (clusters): N
- **Default (romanised Sanskrit), as printed:** `…   |   akshara: 26`
- **This pack, as printed:** `…   |   எழுத்துகள்: 26`
- **This message alone:** `   |   எழுத்துகள்: `
- **Correction:** 

### 110. `ide.st_lipi_w` — **DRAFT**

- **Where:** IDE status line, typing mode on
- **Meaning:** | script: NAME (the typing script)
- **Default (romanised Sanskrit), as printed:** `…   |   lipi: தமிழ்`
- **This pack, as printed:** `…   |   எழுத்துமுறை: தமிழ்`
- **This message alone:** `   |   எழுத்துமுறை: `
- **Correction:** 

### 111. `ide.st_sanchit_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** saved
- **Default (romanised Sanskrit), as printed:** `…   |   sanchit`
- **This pack, as printed:** `…   |   சேமிக்கப்பட்டது`
- **This message alone:** `சேமிக்கப்பட்டது`
- **Correction:** 

### 112. `ide.st_asanchit_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** not saved *
- **Default (romanised Sanskrit), as printed:** `…   |   asanchit *`
- **This pack, as printed:** `…   |   சேமிக்கப்படவில்லை *`
- **This message alone:** `சேமிக்கப்படவில்லை *`
- **Correction:** 

### 113. `ide.st_notfound_w` — **DRAFT**

- **Where:** IDE status line, after Find
- **Meaning:** find: not found
- **Default (romanised Sanskrit), as printed:** `anwesh: nahi mila`
- **This pack, as printed:** `தேடல்: கிடைக்கவில்லை`
- **Correction:** 

### 114. `ide.lang_swayam_w` — **DRAFT**

- **Where:** IDE status line: language Auto
- **Meaning:** automatic (detect the script)
- **Default (romanised Sanskrit), as printed:** `   |   bhasha: swayam`
- **This pack, as printed:** `   |   மொழி: தானியங்கி`
- **This message alone:** `தானியங்கி`
- **Correction:** 

### 115. `ide.lang_swayam_sk_w` — **DRAFT**

- **Where:** IDE status line: Auto found Devanagari
- **Meaning:** automatic (Sanskrit)
- **Default (romanised Sanskrit), as printed:** `   |   bhasha: swayam (sanskrit)`
- **This pack, as printed:** `   |   மொழி: தானியங்கி (சம்ஸ்கிருதம்)`
- **This message alone:** `தானியங்கி (சம்ஸ்கிருதம்)`
- **Correction:** 

### 116. `ide.lang_mool_w` — **DRAFT**

- **Where:** IDE status line: language Core
- **Meaning:** core (Latin keywords)
- **Default (romanised Sanskrit), as printed:** `   |   bhasha: mool`
- **This pack, as printed:** `   |   மொழி: மூலம்`
- **This message alone:** `மூலம்`
- **Correction:** 

### 117. `ide.msg_ready` — **UNSURE**

- **Where:** IDE output pane, at start and after Clear shell
- **Meaning:** ready. F5 compiles and runs the program in the editor
- **Default (romanised Sanskrit), as printed:** `Taiyar. F5: sampadak ka karyakram sankalan aur chalan.⏎`
- **This pack, as printed:** `தயார். F5: திருத்தியில் உள்ள நிரலைத் தொகுத்து இயக்கும்.⏎`
- **Doubt:** 'தொகுத்து இயக்கும்' (compiles and runs): check the verbs.
- **Correction:** 

### 118. `ide.msg_compile_failed` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [compilation failed]
- **Default (romanised Sanskrit), as printed:** `[sankalan asaphal]⏎`
- **This pack, as printed:** `[தொகுத்தல் தோல்வி]⏎`
- **Correction:** 

### 119. `ide.msg_run_failed` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the program ended abnormally]
- **Default (romanised Sanskrit), as printed:** `[karyakram asamanya roop se samapt]⏎`
- **This pack, as printed:** `[நிரல் இயல்பற்ற முறையில் முடிந்தது]⏎`
- **Correction:** 

### 120. `ide.msg_file_failed` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [reading/writing the file failed]
- **Default (romanised Sanskrit), as printed:** `[patra padhne/likhne me asaphal]⏎`
- **This pack, as printed:** `[கோப்பைப் படிக்க/எழுத இயலவில்லை]⏎`
- **Correction:** 

### 121. `ide.msg_input_large` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the file is too big; editor limit 64 KiB]
- **Default (romanised Sanskrit), as printed:** `[patra bahut bada; sampadak seema 64 KiB]⏎`
- **This pack, as printed:** `[கோப்பு மிகப் பெரியது; திருத்தி வரம்பு 64 KiB]⏎`
- **Correction:** 

### 122. `ide.msg_shell_limit` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the shell history is full; clear the shell first]
- **Default (romanised Sanskrit), as printed:** `[khol ka itihas purna; pahle khol rikta karein]⏎`
- **This pack, as printed:** `[உரையாடல் வரலாறு நிரம்பியது; முதலில் உரையாடலை அழியுங்கள்]⏎`
- **Correction:** 

### 123. `ide.msg_timeout` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the process ran more than 10 seconds; stopped]
- **Default (romanised Sanskrit), as printed:** `[prakriya 10 sekand se adhik; samapt ki gayi]⏎`
- **This pack, as printed:** `[செயல்முறை 10 வினாடிகளுக்கு மேல் ஓடியது; நிறுத்தப்பட்டது]⏎`
- **Correction:** 

### 124. `ide.msg_missing_compiler` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [win\sutram.exe not found: build the compiler first]
- **Default (romanised Sanskrit), as printed:** `[win\sutram.exe nahi mila: pahle sankalak banayein]⏎`
- **This pack, as printed:** `[win\sutram.exe கிடைக்கவில்லை: முதலில் தொகுப்பியை உருவாக்குங்கள்]⏎`
- **Correction:** 

### 125. `ide.msg_missing_lang` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [native word packs unavailable: see lang\*.lang; the core words work]
- **Default (romanised Sanskrit), as printed:** `[deshi shabda-pak anupalabdh: lang\*.lang dekhein; mool shabda kaam karte hain]⏎`
- **This pack, as printed:** `[உள்நாட்டுச் சொல் தொகுப்புகள் இல்லை: lang\*.lang பாருங்கள்; மூலச் சொற்கள் இயங்கும்]⏎`
- **Correction:** 

### 126. `ide.msg_partial_lang` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [some word packs unavailable or invalid: see lang\*.lang]
- **Default (romanised Sanskrit), as printed:** `[kuchh shabda-pak anupalabdh ya ashuddh: lang\*.lang dekhein]⏎`
- **This pack, as printed:** `[சில சொல் தொகுப்புகள் இல்லை அல்லது தவறானவை: lang\*.lang பாருங்கள்]⏎`
- **Correction:** 

### 127. `ide.msg_pipe_fail` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [creating the process or the pipe failed]
- **Default (romanised Sanskrit), as printed:** `[prakriya ya nalika nirman asaphal]⏎`
- **This pack, as printed:** `[செயல்முறை அல்லது குழாய் உருவாக்கம் தோல்வி]⏎`
- **Correction:** 

### 128. `ide.msg_more_output` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [output cut at 32 KiB]
- **Default (romanised Sanskrit), as printed:** `[phal 32 KiB par kata]⏎`
- **This pack, as printed:** `[வெளியீடு 32 KiB இல் வெட்டப்பட்டது]⏎`
- **Correction:** 


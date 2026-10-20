# Review sheet: Bengali (বাংলা)

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
  They go into `lang/bengali.sandesh`.

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
| 40 | `r65_msg_add` | UNSURE |
| 52 | `msg_lang_ok` | UNSURE |
| 53 | `msg_lang_fail` | UNSURE |
| 54 | `msg_shell_banner` | UNSURE |
| 55 | `msg_shell_bye` | UNSURE |
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
সূত্রম্ - সম্পূর্ণ সূত্র
ব্যবহার:
  sutram <উৎস.sm> <নির্গত.bin>         সংকলন
  sutram --check <উৎস.sm>              কেবল পরীক্ষা, নির্গত ফাইল নয়
  sutram --lang <প্যাক> <উৎস.sm> <নির্গত.bin>  ভাষা প্যাক সহ
  sutram -i                               সংলাপ
  sutram --version                        সংস্করণ
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
সূত্রম্ 1.0 (v182) - সম্পূর্ণ সূত্র
সংস্কৃত-প্রধান ভাষা -> x86-64 যন্ত্র-ভাষা
```
- **Correction:** 

### 3. `r48_msg_near` — **UNSURE**

- **Where:** compiler: `--check`, a parse error
- **Meaning:** 'word' (the token where parsing failed)
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: shabd '=' + caret line`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: শব্দ '=' + caret line`
- **This message alone:** `: Sutram Error [E_PARSE]: শব্দ '`
- **Doubt:** 'word' stands for a token; check that it reads naturally before the quoted token.
- **Correction:** 

### 4. `r48_msg_ok` — **DRAFT**

- **Where:** compiler: `--check`, no errors
- **Meaning:** check: correct (no output file made)
- **Default (romanised Sanskrit), as printed:** `Sutram janch: shuddh (nirgat patra nahi)⏎`
- **This pack, as printed:** `সূত্রম্ পরীক্ষা: ঠিক আছে (নির্গত ফাইল তৈরি হয়নি)⏎`
- **Correction:** 

### 5. `r48_msg_errors` — **DRAFT**

- **Where:** compiler: `--check`, errors found
- **Meaning:** check: errors found; no output file made
- **Default (romanised Sanskrit), as printed:** `Sutram janch: dosh mile; nirgat patra nahi⏎`
- **This pack, as printed:** `সূত্রম্ পরীক্ষা: ত্রুটি পাওয়া গেছে; নির্গত ফাইল তৈরি হয়নি⏎`
- **Correction:** 

### 6. `r48_msg_eof` — **DRAFT**

- **Where:** compiler: `--check`, error at end of file
- **Meaning:** <end of file>, shown in place of the token
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: shabd '<patra-ant>'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: শব্দ '<ফাইলের শেষ>'`
- **This message alone:** `<ফাইলের শেষ>`
- **Correction:** 

### 7. `r50_msg_setchar_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** akshar_rakh needs 3 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: akshar_rakh: 3 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: akshar_rakh: 3টি যুক্তি প্রয়োজন⏎`
- **In the pack file:** `Sutram Error: {kw:akshar_rakh}: 3টি যুক্তি প্রয়োজন⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 8. `r52_msg_dvaram_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** dvaram needs 2 or 3 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: dvaram: 2 va 3 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: dvaram: 2 বা 3টি যুক্তি প্রয়োজন⏎`
- **In the pack file:** `Sutram Error: {kw:dvaram}: 2 বা 3টি যুক্তি প্রয়োজন⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 9. `r52_msg_charat_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** akshar needs 2 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: akshar: 2 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: akshar: 2টি যুক্তি প্রয়োজন⏎`
- **In the pack file:** `Sutram Error: {kw:akshar}: 2টি যুক্তি প্রয়োজন⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 10. `r52_msg_charcode_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** aksharank needs 1 or 2 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: aksharank: 1 va 2 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: aksharank: 1 বা 2টি যুক্তি প্রয়োজন⏎`
- **In the pack file:** `Sutram Error: {kw:aksharank}: 1 বা 2টি যুক্তি প্রয়োজন⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 11. `r48_msg_undefined` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown function 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_FUNCTION]: agyat prakriya 'foo'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_FUNCTION]: অজানা ফলন 'foo'`
- **This message alone:** `: Sutram Error [E_UNDEFINED_FUNCTION]: অজানা ফলন '`
- **Correction:** 

### 12. `r4_msg_undef` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown name 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_NAME]: agyat naam 'y'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_NAME]: অজানা নাম 'y'`
- **This message alone:** `: Sutram Error [E_UNDEFINED_NAME]: অজানা নাম '`
- **Correction:** 

### 13. `r4_msg_hint_decl` — **DRAFT**

- **Where:** compiler: hint after an unknown name
- **Meaning:** hint: declare it before use: vitti NAME = ...
- **Default (romanised Sanskrit), as printed:** `Sanket: prayog se purv ghoshana avashyak: vitti y = ...`
- **This pack, as printed:** `পরামর্শ: ব্যবহারের আগে ঘোষণা প্রয়োজন: চল y = ...`
- **This message alone:** `পরামর্শ: ব্যবহারের আগে ঘোষণা প্রয়োজন: চল `
- **In the pack file:** `পরামর্শ: ব্যবহারের আগে ঘোষণা প্রয়োজন: {kw:vitti} `  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 14. `r4_msg_hint_old` — **DRAFT**

- **Where:** compiler: hint, opens two hints
- **Meaning:** hint: 'NAME…
- **Default (romanised Sanskrit), as printed:** `Sanket: 'anyatra' purana kunjishabd (v157 se purv); navin: 'anya'`
- **This pack, as printed:** `পরামর্শ: 'anyatra' পুরোনো মূলশব্দ (v157-এর আগের); নতুন: 'anya'`
- **This message alone:** `পরামর্শ: '`
- **Correction:** 

### 15. `r4_msg_hint_old2` — **UNSURE**

- **Where:** compiler: hint after an old keyword
- **Meaning:** 'OLD' is an old keyword (before v157); new: 'NEW'
- **Default (romanised Sanskrit), as printed:** `Sanket: 'anyatra' purana kunjishabd (v157 se purv); navin: 'anya'`
- **This pack, as printed:** `পরামর্শ: 'anyatra' পুরোনো মূলশব্দ (v157-এর আগের); নতুন: 'anya'`
- **This message alone:** `' পুরোনো মূলশব্দ (v157-এর আগের); নতুন: '`
- **Doubt:** 'মূলশব্দ' for keyword; check.
- **Correction:** 

### 16. `r5_msg_field` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown field 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_UNKNOWN_FIELD]: agyat kshetra 'q'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_UNKNOWN_FIELD]: অজানা ক্ষেত্র 'q'`
- **This message alone:** `: Sutram Error [E_UNKNOWN_FIELD]: অজানা ক্ষেত্র '`
- **Correction:** 

### 17. `r7_msg_dup` — **DRAFT**

- **Where:** compiler
- **Meaning:** declared again: 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_DUPLICATE_NAME]: punah ghoshana 'x'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_DUPLICATE_NAME]: পুনরায় ঘোষণা 'x'`
- **This message alone:** `: Sutram Error [E_DUPLICATE_NAME]: পুনরায় ঘোষণা '`
- **Correction:** 

### 18. `r7_msg_dup_hint` — **DRAFT**

- **Where:** compiler: hint after a duplicate
- **Meaning:** 'NAME' is already declared; to give it a new value: NAME = ...
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' pahle se ghoshit hai; naya man dene ke liye: x = ...`
- **This pack, as printed:** `পরামর্শ: 'x' আগেই ঘোষিত; নতুন মান দিতে: x = ...`
- **This message alone:** `' আগেই ঘোষিত; নতুন মান দিতে: `
- **Correction:** 

### 19. `r7_msg_field_amb` — **DRAFT**

- **Where:** compiler
- **Meaning:** field 'NAME' (is ambiguous)
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_AMBIGUOUS_FIELD]: kshetra 'x'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_AMBIGUOUS_FIELD]: ক্ষেত্র 'x'`
- **This message alone:** `: Sutram Error [E_AMBIGUOUS_FIELD]: ক্ষেত্র '`
- **Correction:** 

### 20. `r7_msg_field_amb_hint` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** 'NAME' is at different places in two rachanas; give it a different name in each
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' do rachana me alag sthan par hai; har rachana me alag naam rakhein⏎`
- **This pack, as printed:** `পরামর্শ: 'x' দুটি রচনায় ভিন্ন স্থানে আছে; প্রতিটি রচনায় ভিন্ন নাম রাখুন⏎`
- **This message alone:** `' দুটি রচনায় ভিন্ন স্থানে আছে; প্রতিটি রচনায় ভিন্ন নাম রাখুন⏎`
- **Correction:** 

### 21. `r7_msg_field_dup_hint` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** 'NAME' is already in this rachana
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' is rachana me pahle se hai⏎`
- **This pack, as printed:** `পরামর্শ: 'x' এই রচনায় আগেই আছে⏎`
- **This message alone:** `' এই রচনায় আগেই আছে⏎`
- **Correction:** 

### 22. `r7_msg_arity2` — **UNSURE**

- **Where:** compiler: middle of the arity error
- **Meaning:** 'f' [was given] N arguments; in the signature M
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' ko 1 tark diye; hastakshar me 2`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' কে 1 যুক্তি দেওয়া হয়েছে; স্বাক্ষরে 2`
- **This message alone:** `' কে `
- **Doubt:** Word order is fixed by the code: 'NAME' <this> N <arity3> M. Check that the sentence reads naturally around the name and the two numbers.
- **Doubt:** The case suffix is printed after a space ('f' <suffix>); written Bengali normally attaches it to the word (with a quoted code name, say which you prefer). The checker keeps the default's leading "' ", so fixing this needs that rule relaxed for this message.
- **Correction:** 

### 23. `r7_msg_arity3` — **UNSURE**

- **Where:** compiler: middle of the arity error
- **Meaning:** … N arguments given; in the signature M
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' ko 1 tark diye; hastakshar me 2`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' কে 1 যুক্তি দেওয়া হয়েছে; স্বাক্ষরে 2`
- **This message alone:** ` যুক্তি দেওয়া হয়েছে; স্বাক্ষরে `
- **Doubt:** 'যুক্তি' for an argument is the reasoning sense; check. 'স্বাক্ষর' for a signature is a calque.
- **Doubt:** The count is printed before this text and is often 1 ('f' … 1 …): the noun is in the plural form, so '1 <plural>' may read wrong. A fragment cannot change with the number.
- **Correction:** 

### 24. `r7_msg_arity_hint` — **DRAFT**

- **Where:** compiler: hint after the arity error
- **Meaning:** hint: give exactly as many arguments as the function's definition has
- **Default (romanised Sanskrit), as printed:** `Sanket: utne hi tark dein jitne prakriya ki paribhasha me hain⏎`
- **This pack, as printed:** `পরামর্শ: ফলনের সংজ্ঞায় যতগুলি যুক্তি আছে ঠিক ততগুলিই দিন⏎`
- **Correction:** 

### 25. `r7_msg_mod_missing` — **DRAFT**

- **Where:** compiler
- **Meaning:** import file not found: NAME
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_MISSING]: yoj patra aprapt: ganit`
- **This pack, as printed:** `Sutram Error [E_MODULE_MISSING]: অন্তর্ভুক্ত ফাইল পাওয়া যায়নি: ganit`
- **This message alone:** `Sutram Error [E_MODULE_MISSING]: অন্তর্ভুক্ত ফাইল পাওয়া যায়নি: `
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

পরামর্শ: <নাম>.smlib lib/ এ অথবা উৎস ফাইলের নির্দেশিকায় থাকা উচিত
```
- **Correction:** 

### 27. `r7_msg_hint_block` — **DRAFT**

- **Where:** compiler: hint after an unknown name
- **Meaning:** 'NAME' is declared inside a block { } or a loop; it is not visible outside it
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' ek khand { } ya chakra me ghoshit hai; uske bahar drishya nahi⏎`
- **This pack, as printed:** `পরামর্শ: 'x' কোনো খণ্ড { } বা পুনরাবৃত্তি এর ভিতরে ঘোষিত; তার বাইরে দেখা যায় না⏎`
- **This message alone:** `' কোনো খণ্ড { } বা পুনরাবৃত্তি এর ভিতরে ঘোষিত; তার বাইরে দেখা যায় না⏎`
- **In the pack file:** `' কোনো খণ্ড { } বা {kw:chakra} এর ভিতরে ঘোষিত; তার বাইরে দেখা যায় না⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 28. `r5_msg_field_hint` — **DRAFT**

- **Where:** compiler: hint, opens the field hint
- **Meaning:** hint: 'NAME…
- **Default (romanised Sanskrit), as printed:** `Sanket: 'q' kisi rachana ka kshetra nahi⏎`
- **This pack, as printed:** `পরামর্শ: 'q' কোনো রচনার ক্ষেত্র নয়⏎`
- **This message alone:** `পরামর্শ: '`
- **Correction:** 

### 29. `r5_msg_field_hint2` — **DRAFT**

- **Where:** compiler: hint after an unknown field
- **Meaning:** 'NAME' is not a field of any rachana
- **Default (romanised Sanskrit), as printed:** `Sanket: 'q' kisi rachana ka kshetra nahi⏎`
- **This pack, as printed:** `পরামর্শ: 'q' কোনো রচনার ক্ষেত্র নয়⏎`
- **This message alone:** `' কোনো রচনার ক্ষেত্র নয়⏎`
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

Sutram Error: ব্যাকরণ ত্রুটি, পংক্তি 
```
- **Correction:** 

### 31. `msg_err_near` — **DRAFT**

- **Where:** compiler: a parse error
- **Meaning:** , word 'TOKEN'
- **Default (romanised Sanskrit), as printed:** `⏎Sutram Error: vyakaran dosh, pankti 3:11, shabd '='`
- **This pack, as printed:** `⏎Sutram Error: ব্যাকরণ ত্রুটি, পংক্তি 3:11, শব্দ '='`
- **This message alone:** `, শব্দ '`
- **Correction:** 

### 32. `msg_err_eof` — **DRAFT**

- **Where:** compiler: a parse error at the end of the file
- **Meaning:** end of file, shown in place of the token
- **Default (romanised Sanskrit), as printed:** `⏎Sutram Error: vyakaran dosh, pankti 6:1, shabd 'patra-ant'`
- **This pack, as printed:** `⏎Sutram Error: ব্যাকরণ ত্রুটি, পংক্তি 6:1, শব্দ 'ফাইলের শেষ'`
- **This message alone:** `ফাইলের শেষ`
- **Correction:** 

### 33. `msg_err_hint` — **DRAFT**

- **Where:** compiler: hint after a parse error
- **Meaning:** hint: check the word and the grammar at this place
- **Default (romanised Sanskrit), as printed:** `Sanket: is sthan par shabd aur vyakaran dekho.⏎`
- **This pack, as printed:** `পরামর্শ: এই স্থানে শব্দ ও ব্যাকরণ পরীক্ষা করুন।⏎`
- **Correction:** 

### 34. `msg_err_arg_limit` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** hint: a function takes at most 6 arguments
- **Default (romanised Sanskrit), as printed:** `Sanket: prakriya adhiktam 6 tark lete hain.⏎`
- **This pack, as printed:** `পরামর্শ: ফলন সর্বাধিক 6টি যুক্তি নেয়।⏎`
- **Correction:** 

### 35. `msg_err_duplicate_func` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** hint: the function is defined twice (name clash)
- **Default (romanised Sanskrit), as printed:** `Sanket: dohri prakriya paribhasha (naam takkar).⏎`
- **This pack, as printed:** `পরামর্শ: ফলনের দ্বৈত সংজ্ঞা (নামের সংঘাত)।⏎`
- **Correction:** 

### 36. `msg_duplicate_func` — **DRAFT**

- **Where:** compiler
- **Meaning:** function defined again: NAME
- **Default (romanised Sanskrit), as printed:** `Sutram Error: punah prakriya paribhasha: f`
- **This pack, as printed:** `Sutram Error: ফলনের পুনরায় সংজ্ঞা: f`
- **This message alone:** `Sutram Error: ফলনের পুনরায় সংজ্ঞা: `
- **Correction:** 

### 37. `msg_undefined_func` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown function: NAME
- **Default (romanised Sanskrit), as printed:** `Sutram Error: agyat prakriya: f`
- **This pack, as printed:** `Sutram Error: অজানা ফলন: f`
- **This message alone:** `Sutram Error: অজানা ফলন: `
- **Correction:** 

### 38. `msg_array_oob` — **DRAFT**

- **Where:** the compiled program, at run time
- **Meaning:** mala index out of bounds
- **Default (romanised Sanskrit), as printed:** `Sutram Error: mala ank seema atikram⏎`
- **This pack, as printed:** `Sutram Error: পঙক্তি সূচক সীমার বাইরে⏎`
- **In the pack file:** `Sutram Error: {kw:mala} সূচক সীমার বাইরে⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 39. `msg_kosh_required` — **DRAFT**

- **Where:** compiler
- **Meaning:** a kosh function needs a kosh variable
- **Default (romanised Sanskrit), as printed:** `Sutram Error: kosh prakriya hetu kosh-vitti avashyak⏎`
- **This pack, as printed:** `Sutram Error: কোশ ফলনের জন্য কোশ চলক প্রয়োজন⏎`
- **In the pack file:** `Sutram Error: {kw:kosh} ফলনের জন্য {kw:kosh} চলক প্রয়োজন⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 40. `r65_msg_add` — **UNSURE**

- **Where:** the program, `trap` build
- **Meaning:** overflow in an addition
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: yog atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: যোগে উপচে পড়া⏎`
- **This message alone:** `: যোগে উপচে পড়া⏎`
- **Doubt:** 'উপচে পড়া' (spilling over) for an integer overflow is colloquial; check (all seven trap messages).
- **Correction:** 

### 41. `r65_msg_sub` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a subtraction
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: nyun atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: বিয়োগে উপচে পড়া⏎`
- **This message alone:** `: বিয়োগে উপচে পড়া⏎`
- **Correction:** 

### 42. `r65_msg_mul` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a multiplication
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: gun atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: গুণে উপচে পড়া⏎`
- **This message alone:** `: গুণে উপচে পড়া⏎`
- **Correction:** 

### 43. `r65_msg_div` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** division by zero
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: shunya se bhajan⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: শূন্য দিয়ে ভাগ⏎`
- **This message alone:** `: শূন্য দিয়ে ভাগ⏎`
- **Correction:** 

### 44. `r65_msg_mod` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** remainder by zero
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: shunya se shesh⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: শূন্য দিয়ে ভাগশেষ⏎`
- **This message alone:** `: শূন্য দিয়ে ভাগশেষ⏎`
- **Correction:** 

### 45. `r65_msg_div_overflow` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a division
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: bhajan atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: ভাগে উপচে পড়া⏎`
- **This message alone:** `: ভাগে উপচে পড়া⏎`
- **Correction:** 

### 46. `r65_msg_mod_overflow` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a remainder
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: shesh atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: ভাগশেষে উপচে পড়া⏎`
- **This message alone:** `: ভাগশেষে উপচে পড়া⏎`
- **Correction:** 

### 47. `msg_kosh_empty` — **DRAFT**

- **Where:** the program, at run time
- **Meaning:** kosh_pop from an empty kosh
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rikta kosh se kosh_pop⏎`
- **This pack, as printed:** `Sutram Error: খালি কোশ থেকে kosh_pop⏎`
- **In the pack file:** `Sutram Error: খালি কোশ থেকে {kw:kosh_pop}⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 48. `msg_kosh_peek_empty` — **DRAFT**

- **Where:** the program, at run time
- **Meaning:** kosh_peek from an empty kosh
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rikta kosh se kosh_peek⏎`
- **This pack, as printed:** `Sutram Error: খালি কোশ থেকে kosh_peek⏎`
- **In the pack file:** `Sutram Error: খালি কোশ থেকে {kw:kosh_peek}⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 49. `msg_kosh_dequeue_empty` — **DRAFT**

- **Where:** the program, at run time
- **Meaning:** kosh_dequeue from an empty kosh
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rikta kosh se kosh_dequeue⏎`
- **This pack, as printed:** `Sutram Error: খালি কোশ থেকে kosh_dequeue⏎`
- **In the pack file:** `Sutram Error: খালি কোশ থেকে {kw:kosh_dequeue}⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 50. `msg_kosh_param_type` — **DRAFT**

- **Where:** compiler
- **Meaning:** kosh argument: element type differs
- **Default (romanised Sanskrit), as printed:** `Sutram Error: kosh tark: tatv prakar bhinn⏎`
- **This pack, as printed:** `Sutram Error: কোশ যুক্তি: উপাদানের প্রকার ভিন্ন⏎`
- **Correction:** 

### 51. `msg_kosh_param_push` — **DRAFT**

- **Where:** compiler
- **Meaning:** kosh_push is not supported on a kosh argument
- **Default (romanised Sanskrit), as printed:** `Sutram Error: kosh tark par kosh_push asamarthit⏎`
- **This pack, as printed:** `Sutram Error: কোশ যুক্তিতে kosh_push সমর্থিত নয়⏎`
- **In the pack file:** `Sutram Error: কোশ যুক্তিতে {kw:kosh_push} সমর্থিত নয়⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 52. `msg_lang_ok` — **UNSURE**

- **Where:** compiler: every run with `--lang`
- **Meaning:** language pack found: PACK
- **Default (romanised Sanskrit), as printed:** `Bhasha pak prapt: hindi`
- **This pack, as printed:** `ভাষা প্যাক পাওয়া গেছে: hindi`
- **This message alone:** `ভাষা প্যাক পাওয়া গেছে: `
- **Doubt:** 'pack' (the language-pack file) has no settled native word; check the term.
- **Correction:** 

### 53. `msg_lang_fail` — **UNSURE**

- **Where:** compiler
- **Meaning:** warning: language pack not found: PACK
- **Default (romanised Sanskrit), as printed:** `Chetavani: bhasha pak nahi mila: hindi`
- **This pack, as printed:** `সতর্কতা: ভাষা প্যাক পাওয়া যায়নি: hindi`
- **This message alone:** `সতর্কতা: ভাষা প্যাক পাওয়া যায়নি: `
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
সূত্রম্ সংলাপ v1.0 - সম্পূর্ণ সূত্র
সূত্রম্ বিবৃতি লিখুন এবং Enter চাপুন। সঙ্গে সঙ্গে চলবে।
আদেশ: sahayata (সাহায্য) | nirgat (প্রস্থান) | sarvam (সব দেখুন)
```
- **Doubt:** 'Enter' is kept as the key's label; the verb for pressing a key should be checked.
- **Correction:** 

### 55. `msg_shell_bye` — **UNSURE**

- **Where:** compiler: leaving `sutram -i`
- **Meaning:** greeting; session ended
- **Default (romanised Sanskrit), as printed:** `Namaste! Satra samapt.⏎`
- **This pack, as printed:** `নমস্কার! অধিবেশন শেষ।⏎`
- **Doubt:** 'অধিবেশন' for a session; check.
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
সূত্রম্ সংলাপ সাহায্য:
  লিখো("নমস্কার\n")            লেখা ছাপে
  চল x = 5             চলক ঘোষণা
  লিখো(x + 3)            মান ছাপে
  পুনরাবৃত্তি i = 0 থেকে 5 { লিখো(i) }   পুনরাবৃত্তি
  পঙক্তি arr[5]             পঙক্তি ঘোষণা
  sarvam                  সম্পূর্ণ কার্যক্রম দেখুন
  nirgat                  সংলাপ থেকে প্রস্থান
```
- **In the pack file:** `সূত্রম্ সংলাপ সাহায্য:⏎  {kw:likha}("নমস্কার\n")            লেখা ছাপে⏎  {kw:vitti} x = 5             চলক ঘোষণা⏎  {kw:likha}(x + 3)            মান ছাপে⏎  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   পুনরাবৃত্তি⏎  {kw:mala} arr[5]             পঙক্তি ঘোষণা⏎  sarvam                  সম্পূর্ণ কার্যক্রম দেখুন⏎  nirgat                  সংলাপ থেকে প্রস্থান⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 57. `msg_open_err` — **DRAFT**

- **Where:** compiler
- **Meaning:** input (source) file not found
- **Default (romanised Sanskrit), as printed:** `Sutram Error: nivesh patra aprapt⏎`
- **This pack, as printed:** `Sutram Error: উৎস ফাইল পাওয়া যায়নি⏎`
- **Correction:** 

### 58. `msg_ok` — **DRAFT**

- **Where:** compiler: a successful compile
- **Meaning:** done: N bytes compiled
- **Default (romanised Sanskrit), as printed:** `Siddh: 297 baait sankalit⏎`
- **This pack, as printed:** `সফল: 297 বাইট সংকলিত⏎`
- **This message alone:** `সফল: `
- **Correction:** 

### 59. `msg_bytes` — **DRAFT**

- **Where:** compiler: a successful compile
- **Meaning:** … bytes compiled
- **Default (romanised Sanskrit), as printed:** `Siddh: 297 baait sankalit⏎`
- **This pack, as printed:** `সফল: 297 বাইট সংকলিত⏎`
- **This message alone:** ` বাইট সংকলিত⏎`
- **Correction:** 

### 60. `msg_namespace_error` — **DRAFT**

- **Where:** compiler
- **Meaning:** invalid import (form: module@alias, alias up to 31 bytes)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ashuddh yoj (roop: ghatak@upanaam, upanaam 31 baait tak)⏎`
- **This pack, as printed:** `Sutram Error: অশুদ্ধ সমাবেশ (রূপ: মডিউল@উপনাম, উপনাম 31 বাইট পর্যন্ত)⏎`
- **In the pack file:** `Sutram Error: অশুদ্ধ {kw:yoj} (রূপ: মডিউল@উপনাম, উপনাম 31 বাইট পর্যন্ত)⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 61. `msg_namespace_module_missing` — **UNSURE**

- **Where:** compiler
- **Meaning:** module file not found
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ghatak patra aprapt⏎`
- **This pack, as printed:** `Sutram Error: মডিউল ফাইল পাওয়া যায়নি⏎`
- **Doubt:** 'মডিউল' is a loanword.
- **Correction:** 

### 62. `msg_namespace_alias_reuse` — **DRAFT**

- **Where:** compiler
- **Meaning:** alias already used (for another module)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: upanaam purv-niyukt (anya ghatak)⏎`
- **This pack, as printed:** `Sutram Error: উপনাম আগেই ব্যবহৃত (অন্য মডিউলের জন্য)⏎`
- **Correction:** 

### 63. `r51_alias_conflict` — **DRAFT**

- **Where:** compiler
- **Meaning:** alias already used (for another module)
- **Default (romanised Sanskrit), as printed:** `prog.sm:2: Sutram Error [E_MODULE_ALIAS_REUSE]: upanaam purv-niyukt (anya ghatak)⏎`
- **This pack, as printed:** `prog.sm:2: Sutram Error [E_MODULE_ALIAS_REUSE]: উপনাম আগেই ব্যবহৃত (অন্য মডিউলের জন্য)⏎`
- **This message alone:** `: Sutram Error [E_MODULE_ALIAS_REUSE]: উপনাম আগেই ব্যবহৃত (অন্য মডিউলের জন্য)⏎`
- **Correction:** 

### 64. `msg_namespace_func_limit` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of module function names exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ghatak prakriya-naam seema atikram⏎`
- **This pack, as printed:** `Sutram Error: মডিউলের ফলন-নামের সীমা অতিক্রম⏎`
- **Correction:** 

### 65. `msg_import_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the expanded source exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: vistarit srot seema atikram⏎`
- **This pack, as printed:** `Sutram Error: বিস্তৃত উৎসের সীমা অতিক্রম⏎`
- **Correction:** 

### 66. `graph_cycle_prefix` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** import cycle: a -> b -> a
- **Default (romanised Sanskrit), as printed:** `prog.sm:1: Sutram Error [E_MODULE_CYCLE] yoj chakra: a -> b -> a`
- **This pack, as printed:** `prog.sm:1: Sutram Error [E_MODULE_CYCLE] অন্তর্ভুক্তি চক্র: a -> b -> a`
- **This message alone:** `অন্তর্ভুক্তি চক্র: `
- **Correction:** 

### 67. `graph_missing_prefix` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** import file not found: NAME
- **Default (romanised Sanskrit), as printed:** `prog.sm:1: Sutram Error [E_MODULE_MISSING] yoj patra aprapt: ganit`
- **This pack, as printed:** `prog.sm:1: Sutram Error [E_MODULE_MISSING] অন্তর্ভুক্ত ফাইল পাওয়া যায়নি: ganit`
- **This message alone:** `অন্তর্ভুক্ত ফাইল পাওয়া যায়নি: `
- **Correction:** 

### 68. `graph_invalid_prefix` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** invalid module name
- **Default (romanised Sanskrit), as printed:** `prog.sm:1: Sutram Error [E_MODULE_INVALID] ashuddh ghatak naam`
- **This pack, as printed:** `prog.sm:1: Sutram Error [E_MODULE_INVALID] অশুদ্ধ মডিউল নাম`
- **This message alone:** `অশুদ্ধ মডিউল নাম`
- **Correction:** 

### 69. `msg_ast_overflow` — **UNSURE**

- **Where:** compiler
- **Meaning:** limit of the syntax tree exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: vakya-vriksh seema atikram⏎`
- **This pack, as printed:** `Sutram Error: বাক্য-বৃক্ষের সীমা অতিক্রম⏎`
- **Doubt:** 'syntax tree' is a coined technical term here; check it.
- **Correction:** 

### 70. `msg_func_params_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the function parameter list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya tark-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ফলনের যুক্তি-তালিকার সীমা অতিক্রম⏎`
- **Correction:** 

### 71. `msg_var_table_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the variable list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: vitti-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: চলক-তালিকার সীমা অতিক্রম⏎`
- **Correction:** 

### 72. `msg_func_table_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the function list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ফলন-তালিকার সীমা অতিক্রম⏎`
- **Correction:** 

### 73. `msg_patch_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the call list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: aahvan-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: আহ্বান-তালিকার সীমা অতিক্রম⏎`
- **Correction:** 

### 74. `msg_func_defs_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the function definition list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya paribhasha-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ফলন সংজ্ঞা-তালিকার সীমা অতিক্রম⏎`
- **Correction:** 

### 75. `msg_r9_guna_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** guna limit exceeded (1024)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: guna seema atikram (1024)⏎`
- **This pack, as printed:** `Sutram Error: গুণ সীমা অতিক্রম (1024)⏎`
- **In the pack file:** `Sutram Error: {kw:guna} সীমা অতিক্রম (1024)⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 76. `msg_break_patch_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** too many krama (break) in a loop
- **Default (romanised Sanskrit), as printed:** `Sutram Error: chakra me krama seema atikram⏎`
- **This pack, as printed:** `Sutram Error: পুনরাবৃত্তি এ ক্রম এর সীমা অতিক্রম⏎`
- **In the pack file:** `Sutram Error: {kw:chakra} এ {kw:krama} এর সীমা অতিক্রম⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 77. `msg_continue_patch_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** too many agrim (continue) in a loop
- **Default (romanised Sanskrit), as printed:** `Sutram Error: chakra me agrim seema atikram⏎`
- **This pack, as printed:** `Sutram Error: পুনরাবৃত্তি এ এগিয়ে এর সীমা অতিক্রম⏎`
- **In the pack file:** `Sutram Error: {kw:chakra} এ {kw:agrim} এর সীমা অতিক্রম⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 78. `msg_code_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the machine code exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: yantra-bhasha seema atikram⏎`
- **This pack, as printed:** `Sutram Error: যন্ত্র-ভাষার সীমা অতিক্রম⏎`
- **Correction:** 

### 79. `msg_rachana_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the rachana list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rachana-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: সংরচনা-তালিকার সীমা অতিক্রম⏎`
- **In the pack file:** `Sutram Error: {kw:rachana}-তালিকার সীমা অতিক্রম⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 80. `msg_rachana_fields_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of rachana fields exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rachana kshetra seema atikram⏎`
- **This pack, as printed:** `Sutram Error: সংরচনা ক্ষেত্রের সীমা অতিক্রম⏎`
- **In the pack file:** `Sutram Error: {kw:rachana} ক্ষেত্রের সীমা অতিক্রম⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 81. `msg_block_nesting_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of block depth exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: khand gahrai seema atikram⏎`
- **This pack, as printed:** `Sutram Error: খণ্ডের গভীরতার সীমা অতিক্রম⏎`
- **Correction:** 

### 82. `msg_block_stmt_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of statements in a block exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: khand kathan seema atikram⏎`
- **This pack, as printed:** `Sutram Error: খণ্ডে বিবৃতির সীমা অতিক্রম⏎`
- **Correction:** 

### 83. `r55_msg_proto_duplicate` — **DRAFT**

- **Where:** compiler
- **Meaning:** function forward-declared again
- **Default (romanised Sanskrit), as printed:** `Sutram Error: punah prakriya purv-ghoshana⏎`
- **This pack, as printed:** `Sutram Error: ফলনের পুনরায় পূর্ব-ঘোষণা⏎`
- **Correction:** 

### 84. `r55_msg_proto_missing` — **DRAFT**

- **Where:** compiler
- **Meaning:** function forward-declared but never defined
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya purv-ghoshana paribhasha-rahit⏎`
- **This pack, as printed:** `Sutram Error: ফলনের পূর্ব-ঘোষণা আছে কিন্তু সংজ্ঞা নেই⏎`
- **Correction:** 

### 85. `r55_msg_proto_signature` — **UNSURE**

- **Where:** compiler
- **Meaning:** forward declaration and definition differ (arguments/type)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya purv-ghoshana va paribhasha bhinn (tark/prakar)⏎`
- **This pack, as printed:** `Sutram Error: ফলনের পূর্ব-ঘোষণা ও সংজ্ঞা ভিন্ন (যুক্তি/প্রকার)⏎`
- **Doubt:** 'forward declaration' (a prototype) is a coined term; check it.
- **Correction:** 

### 86. `r55_msg_proto_capacity` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of function forward declarations exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya purv-ghoshana seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ফলন পূর্ব-ঘোষণার সীমা অতিক্রম⏎`
- **Correction:** 

### 87. `r56_msg_global_capacity` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of module-level variables exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ghatak-star vitti seema atikram⏎`
- **This pack, as printed:** `Sutram Error: মডিউল-স্তরের চলকের সীমা অতিক্রম⏎`
- **Correction:** 

### 88. `r56_msg_global_duplicate` — **DRAFT**

- **Where:** compiler
- **Meaning:** module-level variable name declared again
- **Default (romanised Sanskrit), as printed:** `Sutram Error: punah ghatak-star vitti naam⏎`
- **This pack, as printed:** `Sutram Error: মডিউল-স্তরের চলকের নাম পুনরায়⏎`
- **Correction:** 

### 89. `r56_msg_patch_capacity` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of global value references exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: sarvatrik mulya sandarbh seema atikram⏎`
- **This pack, as printed:** `Sutram Error: সার্বজনীন মান-সূত্রের সীমা অতিক্রম⏎`
- **Correction:** 

### 90. `mg_e_cycle` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** import cycle: a -> b -> a
- **Default (romanised Sanskrit), as printed:** `prog.sm:1:Sutram Error [E_MODULE_CYCLE]: yoj chakra: a -> b -> a`
- **This pack, as printed:** `prog.sm:1:Sutram Error [E_MODULE_CYCLE]: অন্তর্ভুক্তি চক্র: a -> b -> a`
- **This message alone:** `Sutram Error [E_MODULE_CYCLE]: অন্তর্ভুক্তি চক্র: `
- **Correction:** 

### 91. `mg_e_noexp2` — **UNSURE**

- **Where:** compiler: middle of 'not exported'
- **Meaning:** 'SYM' [from] module 'MOD' [is] not exported
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' ghatak 'vec' se aniryat⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' মডিউল 'vec' থেকে রপ্তানি করা হয়নি⏎`
- **This message alone:** `' মডিউল '`
- **Doubt:** Order fixed by the code: 'SYM' <this> 'MOD' <noexp3>. Check that 'SYM … MOD … not exported' reads as one sentence.
- **Correction:** 

### 92. `mg_e_noexp3` — **UNSURE**

- **Where:** compiler: end of 'not exported'
- **Meaning:** … not exported from module MOD
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' ghatak 'vec' se aniryat⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' মডিউল 'vec' থেকে রপ্তানি করা হয়নি⏎`
- **This message alone:** `' থেকে রপ্তানি করা হয়নি⏎`
- **Doubt:** 'রপ্তানি' (export) is the trade sense; check whether it reads as a module export.
- **Doubt:** The case suffix is printed after a space ('f' <suffix>); written Bengali normally attaches it to the word (with a quoted code name, say which you prefer). The checker keeps the default's leading "' ", so fixing this needs that rule relaxed for this message.
- **Correction:** 

### 93. `mg_e_dupexp1` — **DRAFT**

- **Where:** compiler
- **Meaning:** exported again: 'SYM', module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: punah niryat 'thing', ghatak 'dup'`
- **This pack, as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: পুনরায় রপ্তানি 'thing', মডিউল 'dup'`
- **This message alone:** `Sutram Error [E_MODULE_DUP_EXPORT]: পুনরায় রপ্তানি '`
- **Correction:** 

### 94. `mg_e_dupexp2` — **DRAFT**

- **Where:** compiler: middle
- **Meaning:** …, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: punah niryat 'thing', ghatak 'dup'`
- **This pack, as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: পুনরায় রপ্তানি 'thing', মডিউল 'dup'`
- **This message alone:** `', মডিউল '`
- **Correction:** 

### 95. `mg_e_undef1` — **DRAFT**

- **Where:** compiler
- **Meaning:** export 'SYM' has no definition, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: niryat 'thing' paribhasha-rahit, ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: রপ্তানি 'thing' এর সংজ্ঞা নেই, মডিউল 'vec'`
- **This message alone:** `Sutram Error [E_EXPORT_UNDEFINED]: রপ্তানি '`
- **Correction:** 

### 96. `mg_e_undef2` — **UNSURE**

- **Where:** compiler: middle
- **Meaning:** … has no definition, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: niryat 'thing' paribhasha-rahit, ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: রপ্তানি 'thing' এর সংজ্ঞা নেই, মডিউল 'vec'`
- **This message alone:** `' এর সংজ্ঞা নেই, মডিউল '`
- **Doubt:** The case suffix is printed after a space ('f' <suffix>); written Bengali normally attaches it to the word (with a quoted code name, say which you prefer). The checker keeps the default's leading "' ", so fixing this needs that rule relaxed for this message.
- **Correction:** 

### 97. `mg_e_unknown1` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown symbol 'SYM', module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: agyat sanket 'thing', ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: অজানা প্রতীক 'thing', মডিউল 'vec'`
- **This message alone:** `Sutram Error [E_EXPORT_UNDEFINED]: অজানা প্রতীক '`
- **Correction:** 

### 98. `mg_e_unknown2` — **DRAFT**

- **Where:** compiler: middle
- **Meaning:** …, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: agyat sanket 'thing', ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: অজানা প্রতীক 'thing', মডিউল 'vec'`
- **This message alone:** `', মডিউল '`
- **Correction:** 

### 99. `mg_e_depth` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of import depth exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_DEPTH]: yoj gahrai seema atikram⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_DEPTH]: অন্তর্ভুক্তির গভীরতার সীমা অতিক্রম⏎`
- **Correction:** 

### 100. `mg_e_valias1` — **DRAFT**

- **Where:** compiler
- **Meaning:** a v1 module 'MOD' needs an alias: yoj MOD@upanaam
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 ghatak 'vec' upanaam avashyak: yoj vec@upanaam`
- **This pack, as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 মডিউল 'vec' এর জন্য উপনাম প্রয়োজন: সমাবেশ vec@upanaam`
- **This message alone:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 মডিউল '`
- **Correction:** 

### 101. `mg_e_valias2` — **UNSURE**

- **Where:** compiler: middle
- **Meaning:** … needs an alias: yoj MOD@upanaam
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 ghatak 'vec' upanaam avashyak: yoj vec@upanaam`
- **This pack, as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 মডিউল 'vec' এর জন্য উপনাম প্রয়োজন: সমাবেশ vec@upanaam`
- **This message alone:** `' এর জন্য উপনাম প্রয়োজন: সমাবেশ `
- **In the pack file:** `' এর জন্য উপনাম প্রয়োজন: {kw:yoj} `  (`{kw:…}` is the pack's own keyword)
- **Doubt:** The case suffix is printed after a space ('f' <suffix>); written Bengali normally attaches it to the word (with a quoted code name, say which you prefer). The checker keeps the default's leading "' ", so fixing this needs that rule relaxed for this message.
- **Correction:** 

### 102. `mg_e_limit` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of modules/imports exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_LIMIT]: ghatak/yoj seema atikram⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_LIMIT]: মডিউল/অন্তর্ভুক্তির সীমা অতিক্রম⏎`
- **Correction:** 

### 103. `r66_msg_bad_utf8` — **DRAFT**

- **Where:** compiler
- **Meaning:** invalid or broken Indian-script name
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_UTF8]: ashuddh ya khandit bharatiya naam⏎`
- **This pack, as printed:** `Sutram Error [E_UTF8]: অশুদ্ধ বা খণ্ডিত ভারতীয় নাম⏎`
- **Correction:** 

### 104. `r68_utf8_tail` — **DRAFT**

- **Where:** compiler
- **Meaning:** invalid or broken UTF-8 in the source
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_UTF8]: prog.sm:2: srot me ashuddh ya khandit UTF-8⏎`
- **This pack, as printed:** `Sutram Error [E_UTF8]: prog.sm:2: উৎসে অশুদ্ধ বা খণ্ডিত UTF-8⏎`
- **This message alone:** `: উৎসে অশুদ্ধ বা খণ্ডিত UTF-8⏎`
- **Correction:** 

### 105. `r68_value_tail` — **DRAFT**

- **Where:** compiler
- **Meaning:** an abbreviation is not a value: 'वि॰'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_ABBREVIATION_VALUE]: prog.sm:2: sankshep shabd mulya nahi: 'वि॰'`
- **This pack, as printed:** `Sutram Error [E_ABBREVIATION_VALUE]: prog.sm:2: সংক্ষেপ শব্দ মান নয়: 'वि॰'`
- **This message alone:** `: সংক্ষেপ শব্দ মান নয়: '`
- **Correction:** 

### 106. `ide.st_pankti_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** line N (start of the status line)
- **Default (romanised Sanskrit), as printed:** `pankti 12   stambh 4   |   bhasha: …`
- **This pack, as printed:** `পংক্তি 12   স্তম্ভ 4   |   ভাষা: …`
- **This message alone:** `পংক্তি `
- **Correction:** 

### 107. `ide.st_stambh_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** column N
- **Default (romanised Sanskrit), as printed:** `pankti 12   stambh 4   |   bhasha: …`
- **This pack, as printed:** `পংক্তি 12   স্তম্ভ 4   |   ভাষা: …`
- **This message alone:** `   স্তম্ভ `
- **Correction:** 

### 108. `ide.st_bhasha_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** | language: NAME
- **Default (romanised Sanskrit), as printed:** `…4   |   bhasha: हिन्दी`
- **This pack, as printed:** `…4   |   ভাষা: हिन्दी`
- **This message alone:** `   |   ভাষা: `
- **Correction:** 

### 109. `ide.st_akshara_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** | letters (clusters): N
- **Default (romanised Sanskrit), as printed:** `…   |   akshara: 26`
- **This pack, as printed:** `…   |   অক্ষর: 26`
- **This message alone:** `   |   অক্ষর: `
- **Correction:** 

### 110. `ide.st_lipi_w` — **DRAFT**

- **Where:** IDE status line, typing mode on
- **Meaning:** | script: NAME (the typing script)
- **Default (romanised Sanskrit), as printed:** `…   |   lipi: தமிழ்`
- **This pack, as printed:** `…   |   লিপি: தமிழ்`
- **This message alone:** `   |   লিপি: `
- **Correction:** 

### 111. `ide.st_sanchit_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** saved
- **Default (romanised Sanskrit), as printed:** `…   |   sanchit`
- **This pack, as printed:** `…   |   সংরক্ষিত`
- **This message alone:** `সংরক্ষিত`
- **Correction:** 

### 112. `ide.st_asanchit_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** not saved *
- **Default (romanised Sanskrit), as printed:** `…   |   asanchit *`
- **This pack, as printed:** `…   |   সংরক্ষিত নয় *`
- **This message alone:** `সংরক্ষিত নয় *`
- **Correction:** 

### 113. `ide.st_notfound_w` — **DRAFT**

- **Where:** IDE status line, after Find
- **Meaning:** find: not found
- **Default (romanised Sanskrit), as printed:** `anwesh: nahi mila`
- **This pack, as printed:** `অনুসন্ধান: পাওয়া যায়নি`
- **Correction:** 

### 114. `ide.lang_swayam_w` — **DRAFT**

- **Where:** IDE status line: language Auto
- **Meaning:** automatic (detect the script)
- **Default (romanised Sanskrit), as printed:** `   |   bhasha: swayam`
- **This pack, as printed:** `   |   ভাষা: স্বয়ংক্রিয়`
- **This message alone:** `স্বয়ংক্রিয়`
- **Correction:** 

### 115. `ide.lang_swayam_sk_w` — **DRAFT**

- **Where:** IDE status line: Auto found Devanagari
- **Meaning:** automatic (Sanskrit)
- **Default (romanised Sanskrit), as printed:** `   |   bhasha: swayam (sanskrit)`
- **This pack, as printed:** `   |   ভাষা: স্বয়ংক্রিয় (সংস্কৃত)`
- **This message alone:** `স্বয়ংক্রিয় (সংস্কৃত)`
- **Correction:** 

### 116. `ide.lang_mool_w` — **DRAFT**

- **Where:** IDE status line: language Core
- **Meaning:** core (Latin keywords)
- **Default (romanised Sanskrit), as printed:** `   |   bhasha: mool`
- **This pack, as printed:** `   |   ভাষা: মূল`
- **This message alone:** `মূল`
- **Correction:** 

### 117. `ide.msg_ready` — **DRAFT**

- **Where:** IDE output pane, at start and after Clear shell
- **Meaning:** ready. F5 compiles and runs the program in the editor
- **Default (romanised Sanskrit), as printed:** `Taiyar. F5: sampadak ka karyakram sankalan aur chalan.⏎`
- **This pack, as printed:** `প্রস্তুত। F5: সম্পাদকের কার্যক্রম সংকলন করে চালায়।⏎`
- **Correction:** 

### 118. `ide.msg_compile_failed` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [compilation failed]
- **Default (romanised Sanskrit), as printed:** `[sankalan asaphal]⏎`
- **This pack, as printed:** `[সংকলন ব্যর্থ]⏎`
- **Correction:** 

### 119. `ide.msg_run_failed` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the program ended abnormally]
- **Default (romanised Sanskrit), as printed:** `[karyakram asamanya roop se samapt]⏎`
- **This pack, as printed:** `[কার্যক্রম অস্বাভাবিকভাবে শেষ]⏎`
- **Correction:** 

### 120. `ide.msg_file_failed` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [reading/writing the file failed]
- **Default (romanised Sanskrit), as printed:** `[patra padhne/likhne me asaphal]⏎`
- **This pack, as printed:** `[ফাইল পড়া/লেখা ব্যর্থ]⏎`
- **Correction:** 

### 121. `ide.msg_input_large` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the file is too big; editor limit 64 KiB]
- **Default (romanised Sanskrit), as printed:** `[patra bahut bada; sampadak seema 64 KiB]⏎`
- **This pack, as printed:** `[ফাইল খুব বড়; সম্পাদক সীমা 64 KiB]⏎`
- **Correction:** 

### 122. `ide.msg_shell_limit` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the shell history is full; clear the shell first]
- **Default (romanised Sanskrit), as printed:** `[khol ka itihas purna; pahle khol rikta karein]⏎`
- **This pack, as printed:** `[সংলাপের ইতিহাস পূর্ণ; আগে সংলাপ খালি করুন]⏎`
- **Correction:** 

### 123. `ide.msg_timeout` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the process ran more than 10 seconds; stopped]
- **Default (romanised Sanskrit), as printed:** `[prakriya 10 sekand se adhik; samapt ki gayi]⏎`
- **This pack, as printed:** `[প্রক্রিয়া 10 সেকেন্ডের বেশি চলেছে; বন্ধ করা হয়েছে]⏎`
- **Correction:** 

### 124. `ide.msg_missing_compiler` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [win\sutram.exe not found: build the compiler first]
- **Default (romanised Sanskrit), as printed:** `[win\sutram.exe nahi mila: pahle sankalak banayein]⏎`
- **This pack, as printed:** `[win\sutram.exe পাওয়া যায়নি: আগে সংকলক তৈরি করুন]⏎`
- **Correction:** 

### 125. `ide.msg_missing_lang` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [native word packs unavailable: see lang\*.lang; the core words work]
- **Default (romanised Sanskrit), as printed:** `[deshi shabda-pak anupalabdh: lang\*.lang dekhein; mool shabda kaam karte hain]⏎`
- **This pack, as printed:** `[দেশি শব্দ-প্যাক নেই: lang\*.lang দেখুন; মূল শব্দ চলে]⏎`
- **Correction:** 

### 126. `ide.msg_partial_lang` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [some word packs unavailable or invalid: see lang\*.lang]
- **Default (romanised Sanskrit), as printed:** `[kuchh shabda-pak anupalabdh ya ashuddh: lang\*.lang dekhein]⏎`
- **This pack, as printed:** `[কিছু শব্দ-প্যাক নেই বা অশুদ্ধ: lang\*.lang দেখুন]⏎`
- **Correction:** 

### 127. `ide.msg_pipe_fail` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [creating the process or the pipe failed]
- **Default (romanised Sanskrit), as printed:** `[prakriya ya nalika nirman asaphal]⏎`
- **This pack, as printed:** `[প্রক্রিয়া বা নল তৈরি ব্যর্থ]⏎`
- **Correction:** 

### 128. `ide.msg_more_output` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [output cut at 32 KiB]
- **Default (romanised Sanskrit), as printed:** `[phal 32 KiB par kata]⏎`
- **This pack, as printed:** `[ফলাফল 32 KiB-তে কাটা হয়েছে]⏎`
- **Correction:** 


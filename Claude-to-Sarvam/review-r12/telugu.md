# Review sheet: Telugu (తెలుగు)

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
  They go into `lang/telugu.sandesh`.

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
| 22 | `r7_msg_arity2` | UNSURE |
| 23 | `r7_msg_arity3` | UNSURE |
| 26 | `r7_msg_mod_missing2` | UNSURE |
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
సూత్రమ్ - సంపూర్ణ సూత్రం
వాడుక:
  sutram <మూలం.sm> <ఫలితం.bin>         సంకలనం
  sutram --check <మూలం.sm>              తనిఖీ మాత్రమే, ఫలిత దస్త్రం లేదు
  sutram --lang <ప్యాక్> <మూలం.sm> <ఫలితం.bin>  భాషా ప్యాక్‌తో
  sutram -i                               సంభాషణ
  sutram --version                        సంచిక
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
సూత్రమ్ 1.0 (v182) - సంపూర్ణ సూత్రం
సంస్కృత-ప్రధాన భాష -> x86-64 యంత్ర భాష
```
- **Correction:** 

### 3. `r48_msg_near` — **UNSURE**

- **Where:** compiler: `--check`, a parse error
- **Meaning:** 'word' (the token where parsing failed)
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: shabd '=' + caret line`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: పదం '=' + caret line`
- **This message alone:** `: Sutram Error [E_PARSE]: పదం '`
- **Doubt:** 'word' stands for a token; check that it reads naturally before the quoted token.
- **Correction:** 

### 4. `r48_msg_ok` — **DRAFT**

- **Where:** compiler: `--check`, no errors
- **Meaning:** check: correct (no output file made)
- **Default (romanised Sanskrit), as printed:** `Sutram janch: shuddh (nirgat patra nahi)⏎`
- **This pack, as printed:** `సూత్రమ్ తనిఖీ: సరి (ఫలిత దస్త్రం సృష్టించబడలేదు)⏎`
- **Correction:** 

### 5. `r48_msg_errors` — **DRAFT**

- **Where:** compiler: `--check`, errors found
- **Meaning:** check: errors found; no output file made
- **Default (romanised Sanskrit), as printed:** `Sutram janch: dosh mile; nirgat patra nahi⏎`
- **This pack, as printed:** `సూత్రమ్ తనిఖీ: దోషాలు కనబడ్డాయి; ఫలిత దస్త్రం సృష్టించబడలేదు⏎`
- **Correction:** 

### 6. `r48_msg_eof` — **DRAFT**

- **Where:** compiler: `--check`, error at end of file
- **Meaning:** <end of file>, shown in place of the token
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: shabd '<patra-ant>'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_PARSE]: పదం '<దస్త్రం ముగింపు>'`
- **This message alone:** `<దస్త్రం ముగింపు>`
- **Correction:** 

### 7. `r50_msg_setchar_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** akshar_rakh needs 3 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: akshar_rakh: 3 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: akshar_rakh: 3 ప్రమాణాలు అవసరం⏎`
- **In the pack file:** `Sutram Error: {kw:akshar_rakh}: 3 ప్రమాణాలు అవసరం⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 8. `r52_msg_dvaram_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** dvaram needs 2 or 3 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: dvaram: 2 va 3 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: dvaram: 2 లేదా 3 ప్రమాణాలు అవసరం⏎`
- **In the pack file:** `Sutram Error: {kw:dvaram}: 2 లేదా 3 ప్రమాణాలు అవసరం⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 9. `r52_msg_charat_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** akshar needs 2 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: akshar: 2 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: akshar: 2 ప్రమాణాలు అవసరం⏎`
- **In the pack file:** `Sutram Error: {kw:akshar}: 2 ప్రమాణాలు అవసరం⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 10. `r52_msg_charcode_arity` — **DRAFT**

- **Where:** compiler
- **Meaning:** aksharank needs 1 or 2 arguments
- **Default (romanised Sanskrit), as printed:** `Sutram Error: aksharank: 1 va 2 tark avashyak⏎`
- **This pack, as printed:** `Sutram Error: aksharank: 1 లేదా 2 ప్రమాణాలు అవసరం⏎`
- **In the pack file:** `Sutram Error: {kw:aksharank}: 1 లేదా 2 ప్రమాణాలు అవసరం⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 11. `r48_msg_undefined` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown function 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_FUNCTION]: agyat prakriya 'foo'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_FUNCTION]: తెలియని ప్రక్రియ 'foo'`
- **This message alone:** `: Sutram Error [E_UNDEFINED_FUNCTION]: తెలియని ప్రక్రియ '`
- **Correction:** 

### 12. `r4_msg_undef` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown name 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_NAME]: agyat naam 'y'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_UNDEFINED_NAME]: తెలియని పేరు 'y'`
- **This message alone:** `: Sutram Error [E_UNDEFINED_NAME]: తెలియని పేరు '`
- **Correction:** 

### 13. `r4_msg_hint_decl` — **DRAFT**

- **Where:** compiler: hint after an unknown name
- **Meaning:** hint: declare it before use: vitti NAME = ...
- **Default (romanised Sanskrit), as printed:** `Sanket: prayog se purv ghoshana avashyak: vitti y = ...`
- **This pack, as printed:** `సూచన: వాడే ముందు ప్రకటన అవసరం: చరం y = ...`
- **This message alone:** `సూచన: వాడే ముందు ప్రకటన అవసరం: చరం `
- **In the pack file:** `సూచన: వాడే ముందు ప్రకటన అవసరం: {kw:vitti} `  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 14. `r4_msg_hint_old` — **DRAFT**

- **Where:** compiler: hint, opens two hints
- **Meaning:** hint: 'NAME…
- **Default (romanised Sanskrit), as printed:** `Sanket: 'anyatra' purana kunjishabd (v157 se purv); navin: 'anya'`
- **This pack, as printed:** `సూచన: 'anyatra' పాత కీలకపదం (v157 కి ముందుది); కొత్తది: 'anya'`
- **This message alone:** `సూచన: '`
- **Correction:** 

### 15. `r4_msg_hint_old2` — **DRAFT**

- **Where:** compiler: hint after an old keyword
- **Meaning:** 'OLD' is an old keyword (before v157); new: 'NEW'
- **Default (romanised Sanskrit), as printed:** `Sanket: 'anyatra' purana kunjishabd (v157 se purv); navin: 'anya'`
- **This pack, as printed:** `సూచన: 'anyatra' పాత కీలకపదం (v157 కి ముందుది); కొత్తది: 'anya'`
- **This message alone:** `' పాత కీలకపదం (v157 కి ముందుది); కొత్తది: '`
- **Correction:** 

### 16. `r5_msg_field` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown field 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_UNKNOWN_FIELD]: agyat kshetra 'q'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_UNKNOWN_FIELD]: తెలియని క్షేత్రం 'q'`
- **This message alone:** `: Sutram Error [E_UNKNOWN_FIELD]: తెలియని క్షేత్రం '`
- **Correction:** 

### 17. `r7_msg_dup` — **DRAFT**

- **Where:** compiler
- **Meaning:** declared again: 'NAME'
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_DUPLICATE_NAME]: punah ghoshana 'x'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_DUPLICATE_NAME]: మళ్ళీ ప్రకటన 'x'`
- **This message alone:** `: Sutram Error [E_DUPLICATE_NAME]: మళ్ళీ ప్రకటన '`
- **Correction:** 

### 18. `r7_msg_dup_hint` — **DRAFT**

- **Where:** compiler: hint after a duplicate
- **Meaning:** 'NAME' is already declared; to give it a new value: NAME = ...
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' pahle se ghoshit hai; naya man dene ke liye: x = ...`
- **This pack, as printed:** `సూచన: 'x' ఇప్పటికే ప్రకటించబడింది; కొత్త విలువ ఇవ్వడానికి: x = ...`
- **This message alone:** `' ఇప్పటికే ప్రకటించబడింది; కొత్త విలువ ఇవ్వడానికి: `
- **Correction:** 

### 19. `r7_msg_field_amb` — **DRAFT**

- **Where:** compiler
- **Meaning:** field 'NAME' (is ambiguous)
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_AMBIGUOUS_FIELD]: kshetra 'x'`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_AMBIGUOUS_FIELD]: క్షేత్రం 'x'`
- **This message alone:** `: Sutram Error [E_AMBIGUOUS_FIELD]: క్షేత్రం '`
- **Correction:** 

### 20. `r7_msg_field_amb_hint` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** 'NAME' is at different places in two rachanas; give it a different name in each
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' do rachana me alag sthan par hai; har rachana me alag naam rakhein⏎`
- **This pack, as printed:** `సూచన: 'x' రెండు రచనల్లో వేర్వేరు స్థానాల్లో ఉంది; ప్రతి రచనలో వేరే పేరు పెట్టండి⏎`
- **This message alone:** `' రెండు రచనల్లో వేర్వేరు స్థానాల్లో ఉంది; ప్రతి రచనలో వేరే పేరు పెట్టండి⏎`
- **Correction:** 

### 21. `r7_msg_field_dup_hint` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** 'NAME' is already in this rachana
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' is rachana me pahle se hai⏎`
- **This pack, as printed:** `సూచన: 'x' ఈ రచనలో ఇప్పటికే ఉంది⏎`
- **This message alone:** `' ఈ రచనలో ఇప్పటికే ఉంది⏎`
- **Correction:** 

### 22. `r7_msg_arity2` — **UNSURE**

- **Where:** compiler: middle of the arity error
- **Meaning:** 'f' [was given] N arguments; in the signature M
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' ko 1 tark diye; hastakshar me 2`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' కు 1 ప్రమాణాలు ఇచ్చారు; సంతకంలో 2`
- **This message alone:** `' కు `
- **Doubt:** Word order is fixed by the code: 'NAME' <this> N <arity3> M. Check that the sentence reads naturally around the name and the two numbers.
- **Doubt:** The case suffix is printed after a space ('f' <suffix>); written Telugu normally attaches it to the word (with a quoted code name, say which you prefer). The checker keeps the default's leading "' ", so fixing this needs that rule relaxed for this message.
- **Correction:** 

### 23. `r7_msg_arity3` — **UNSURE**

- **Where:** compiler: middle of the arity error
- **Meaning:** … N arguments given; in the signature M
- **Default (romanised Sanskrit), as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' ko 1 tark diye; hastakshar me 2`
- **This pack, as printed:** `prog.sm:3:11: Sutram Error [E_ARITY]: 'f' కు 1 ప్రమాణాలు ఇచ్చారు; సంతకంలో 2`
- **This message alone:** ` ప్రమాణాలు ఇచ్చారు; సంతకంలో `
- **Doubt:** 'ప్రమాణాలు' for arguments is my choice and may not be what a Telugu programmer says; 'సంతకం' for a signature is a calque.
- **Doubt:** The count is printed before this text and is often 1 ('f' … 1 …): the noun is in the plural form, so '1 <plural>' may read wrong. A fragment cannot change with the number.
- **Correction:** 

### 24. `r7_msg_arity_hint` — **DRAFT**

- **Where:** compiler: hint after the arity error
- **Meaning:** hint: give exactly as many arguments as the function's definition has
- **Default (romanised Sanskrit), as printed:** `Sanket: utne hi tark dein jitne prakriya ki paribhasha me hain⏎`
- **This pack, as printed:** `సూచన: ప్రక్రియ నిర్వచనంలో ఎన్ని ప్రమాణాలు ఉన్నాయో అన్నే ఇవ్వండి⏎`
- **Correction:** 

### 25. `r7_msg_mod_missing` — **DRAFT**

- **Where:** compiler
- **Meaning:** import file not found: NAME
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_MISSING]: yoj patra aprapt: ganit`
- **This pack, as printed:** `Sutram Error [E_MODULE_MISSING]: చేర్పు దస్త్రం దొరకలేదు: ganit`
- **This message alone:** `Sutram Error [E_MODULE_MISSING]: చేర్పు దస్త్రం దొరకలేదు: `
- **Correction:** 

### 26. `r7_msg_mod_missing2` — **UNSURE**

- **Where:** compiler: hint after a missing import
- **Meaning:** hint: NAME.smlib should be in lib/ or in the source file's folder
- **Default (romanised Sanskrit):**

```

Sanket: lib/ me ya srot patra ki nirdeshika me naam.smlib hona chahiye
```

- **This pack, as printed:**

```

సూచన: <పేరు>.smlib lib/ లో లేదా మూల దస్త్రం ఉన్న సంచయంలో ఉండాలి
```
- **Doubt:** 'సంచయం' for a folder is a guess; check.
- **Correction:** 

### 27. `r7_msg_hint_block` — **DRAFT**

- **Where:** compiler: hint after an unknown name
- **Meaning:** 'NAME' is declared inside a block { } or a loop; it is not visible outside it
- **Default (romanised Sanskrit), as printed:** `Sanket: 'x' ek khand { } ya chakra me ghoshit hai; uske bahar drishya nahi⏎`
- **This pack, as printed:** `సూచన: 'x' ఒక ఖండం { } లేదా పునరావృతం లోపల ప్రకటించబడింది; దాని బయట కనిపించదు⏎`
- **This message alone:** `' ఒక ఖండం { } లేదా పునరావృతం లోపల ప్రకటించబడింది; దాని బయట కనిపించదు⏎`
- **In the pack file:** `' ఒక ఖండం { } లేదా {kw:chakra} లోపల ప్రకటించబడింది; దాని బయట కనిపించదు⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 28. `r5_msg_field_hint` — **DRAFT**

- **Where:** compiler: hint, opens the field hint
- **Meaning:** hint: 'NAME…
- **Default (romanised Sanskrit), as printed:** `Sanket: 'q' kisi rachana ka kshetra nahi⏎`
- **This pack, as printed:** `సూచన: 'q' ఏ రచనకూ క్షేత్రం కాదు⏎`
- **This message alone:** `సూచన: '`
- **Correction:** 

### 29. `r5_msg_field_hint2` — **DRAFT**

- **Where:** compiler: hint after an unknown field
- **Meaning:** 'NAME' is not a field of any rachana
- **Default (romanised Sanskrit), as printed:** `Sanket: 'q' kisi rachana ka kshetra nahi⏎`
- **This pack, as printed:** `సూచన: 'q' ఏ రచనకూ క్షేత్రం కాదు⏎`
- **This message alone:** `' ఏ రచనకూ క్షేత్రం కాదు⏎`
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

Sutram Error: వ్యాకరణ దోషం, వరుస 
```
- **Correction:** 

### 31. `msg_err_near` — **DRAFT**

- **Where:** compiler: a parse error
- **Meaning:** , word 'TOKEN'
- **Default (romanised Sanskrit), as printed:** `⏎Sutram Error: vyakaran dosh, pankti 3:11, shabd '='`
- **This pack, as printed:** `⏎Sutram Error: వ్యాకరణ దోషం, వరుస 3:11, పదం '='`
- **This message alone:** `, పదం '`
- **Correction:** 

### 32. `msg_err_eof` — **DRAFT**

- **Where:** compiler: a parse error at the end of the file
- **Meaning:** end of file, shown in place of the token
- **Default (romanised Sanskrit), as printed:** `⏎Sutram Error: vyakaran dosh, pankti 6:1, shabd 'patra-ant'`
- **This pack, as printed:** `⏎Sutram Error: వ్యాకరణ దోషం, వరుస 6:1, పదం 'దస్త్రం ముగింపు'`
- **This message alone:** `దస్త్రం ముగింపు`
- **Correction:** 

### 33. `msg_err_hint` — **DRAFT**

- **Where:** compiler: hint after a parse error
- **Meaning:** hint: check the word and the grammar at this place
- **Default (romanised Sanskrit), as printed:** `Sanket: is sthan par shabd aur vyakaran dekho.⏎`
- **This pack, as printed:** `సూచన: ఈ స్థానంలో పదం మరియు వ్యాకరణం తనిఖీ చేయండి.⏎`
- **Correction:** 

### 34. `msg_err_arg_limit` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** hint: a function takes at most 6 arguments
- **Default (romanised Sanskrit), as printed:** `Sanket: prakriya adhiktam 6 tark lete hain.⏎`
- **This pack, as printed:** `సూచన: ప్రక్రియ గరిష్ఠంగా 6 ప్రమాణాలు తీసుకుంటుంది.⏎`
- **Correction:** 

### 35. `msg_err_duplicate_func` — **DRAFT**

- **Where:** compiler: hint
- **Meaning:** hint: the function is defined twice (name clash)
- **Default (romanised Sanskrit), as printed:** `Sanket: dohri prakriya paribhasha (naam takkar).⏎`
- **This pack, as printed:** `సూచన: ప్రక్రియకు రెండు నిర్వచనాలు (పేరు ఘర్షణ).⏎`
- **Correction:** 

### 36. `msg_duplicate_func` — **DRAFT**

- **Where:** compiler
- **Meaning:** function defined again: NAME
- **Default (romanised Sanskrit), as printed:** `Sutram Error: punah prakriya paribhasha: f`
- **This pack, as printed:** `Sutram Error: ప్రక్రియకు మళ్ళీ నిర్వచనం: f`
- **This message alone:** `Sutram Error: ప్రక్రియకు మళ్ళీ నిర్వచనం: `
- **Correction:** 

### 37. `msg_undefined_func` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown function: NAME
- **Default (romanised Sanskrit), as printed:** `Sutram Error: agyat prakriya: f`
- **This pack, as printed:** `Sutram Error: తెలియని ప్రక్రియ: f`
- **This message alone:** `Sutram Error: తెలియని ప్రక్రియ: `
- **Correction:** 

### 38. `msg_array_oob` — **DRAFT**

- **Where:** the compiled program, at run time
- **Meaning:** mala index out of bounds
- **Default (romanised Sanskrit), as printed:** `Sutram Error: mala ank seema atikram⏎`
- **This pack, as printed:** `Sutram Error: పంక్తి సూచిక పరిమితి దాటింది⏎`
- **In the pack file:** `Sutram Error: {kw:mala} సూచిక పరిమితి దాటింది⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 39. `msg_kosh_required` — **DRAFT**

- **Where:** compiler
- **Meaning:** a kosh function needs a kosh variable
- **Default (romanised Sanskrit), as printed:** `Sutram Error: kosh prakriya hetu kosh-vitti avashyak⏎`
- **This pack, as printed:** `Sutram Error: కోశం ప్రక్రియకు కోశం చరం అవసరం⏎`
- **In the pack file:** `Sutram Error: {kw:kosh} ప్రక్రియకు {kw:kosh} {kw:vitti} అవసరం⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 40. `r65_msg_add` — **UNSURE**

- **Where:** the program, `trap` build
- **Meaning:** overflow in an addition
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: yog atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: కూడికలో పొంగిపొర్లడం⏎`
- **This message alone:** `: కూడికలో పొంగిపొర్లడం⏎`
- **Doubt:** 'పొంగిపొర్లడం' (boiling over) for an integer overflow is colloquial; check (all seven trap messages).
- **Correction:** 

### 41. `r65_msg_sub` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a subtraction
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: nyun atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: తీసివేతలో పొంగిపొర్లడం⏎`
- **This message alone:** `: తీసివేతలో పొంగిపొర్లడం⏎`
- **Correction:** 

### 42. `r65_msg_mul` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a multiplication
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: gun atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: గుణకారంలో పొంగిపొర్లడం⏎`
- **This message alone:** `: గుణకారంలో పొంగిపొర్లడం⏎`
- **Correction:** 

### 43. `r65_msg_div` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** division by zero
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: shunya se bhajan⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: సున్నాతో భాగహారం⏎`
- **This message alone:** `: సున్నాతో భాగహారం⏎`
- **Correction:** 

### 44. `r65_msg_mod` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** remainder by zero
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: shunya se shesh⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: సున్నాతో శేషం⏎`
- **This message alone:** `: సున్నాతో శేషం⏎`
- **Correction:** 

### 45. `r65_msg_div_overflow` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a division
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: bhajan atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: భాగహారంలో పొంగిపొర్లడం⏎`
- **This message alone:** `: భాగహారంలో పొంగిపొర్లడం⏎`
- **Correction:** 

### 46. `r65_msg_mod_overflow` — **DRAFT**

- **Where:** the program, `trap` build
- **Meaning:** overflow in a remainder
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: shesh atipravah⏎`
- **This pack, as printed:** `Sutram Error [E_INTEGER_TRAP] prog.sm:3: శేషంలో పొంగిపొర్లడం⏎`
- **This message alone:** `: శేషంలో పొంగిపొర్లడం⏎`
- **Correction:** 

### 47. `msg_kosh_empty` — **DRAFT**

- **Where:** the program, at run time
- **Meaning:** kosh_pop from an empty kosh
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rikta kosh se kosh_pop⏎`
- **This pack, as printed:** `Sutram Error: ఖాళీ కోశం నుండి kosh_pop⏎`
- **In the pack file:** `Sutram Error: ఖాళీ కోశం నుండి {kw:kosh_pop}⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 48. `msg_kosh_peek_empty` — **DRAFT**

- **Where:** the program, at run time
- **Meaning:** kosh_peek from an empty kosh
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rikta kosh se kosh_peek⏎`
- **This pack, as printed:** `Sutram Error: ఖాళీ కోశం నుండి kosh_peek⏎`
- **In the pack file:** `Sutram Error: ఖాళీ కోశం నుండి {kw:kosh_peek}⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 49. `msg_kosh_dequeue_empty` — **DRAFT**

- **Where:** the program, at run time
- **Meaning:** kosh_dequeue from an empty kosh
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rikta kosh se kosh_dequeue⏎`
- **This pack, as printed:** `Sutram Error: ఖాళీ కోశం నుండి kosh_dequeue⏎`
- **In the pack file:** `Sutram Error: ఖాళీ కోశం నుండి {kw:kosh_dequeue}⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 50. `msg_kosh_param_type` — **DRAFT**

- **Where:** compiler
- **Meaning:** kosh argument: element type differs
- **Default (romanised Sanskrit), as printed:** `Sutram Error: kosh tark: tatv prakar bhinn⏎`
- **This pack, as printed:** `Sutram Error: కోశ ప్రమాణం: మూలకం రకం వేరు⏎`
- **Correction:** 

### 51. `msg_kosh_param_push` — **DRAFT**

- **Where:** compiler
- **Meaning:** kosh_push is not supported on a kosh argument
- **Default (romanised Sanskrit), as printed:** `Sutram Error: kosh tark par kosh_push asamarthit⏎`
- **This pack, as printed:** `Sutram Error: కోశ ప్రమాణంపై kosh_push మద్దతు లేదు⏎`
- **In the pack file:** `Sutram Error: కోశ ప్రమాణంపై {kw:kosh_push} మద్దతు లేదు⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 52. `msg_lang_ok` — **UNSURE**

- **Where:** compiler: every run with `--lang`
- **Meaning:** language pack found: PACK
- **Default (romanised Sanskrit), as printed:** `Bhasha pak prapt: hindi`
- **This pack, as printed:** `భాషా ప్యాక్ దొరికింది: hindi`
- **This message alone:** `భాషా ప్యాక్ దొరికింది: `
- **Doubt:** 'pack' (the language-pack file) has no settled native word; check the term.
- **Correction:** 

### 53. `msg_lang_fail` — **UNSURE**

- **Where:** compiler
- **Meaning:** warning: language pack not found: PACK
- **Default (romanised Sanskrit), as printed:** `Chetavani: bhasha pak nahi mila: hindi`
- **This pack, as printed:** `హెచ్చరిక: భాషా ప్యాక్ దొరకలేదు: hindi`
- **This message alone:** `హెచ్చరిక: భాషా ప్యాక్ దొరకలేదు: `
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
సూత్రమ్ సంభాషణ v1.0 - సంపూర్ణ సూత్రం
సూత్రమ్ వాక్యం వ్రాసి Enter నొక్కండి. వెంటనే నడుస్తుంది.
ఆదేశాలు: sahayata (సహాయం) | nirgat (నిష్క్రమణ) | sarvam (అన్నీ చూడండి)
```
- **Doubt:** 'Enter' is kept as the key's label; the verb for pressing a key should be checked.
- **Correction:** 

### 55. `msg_shell_bye` — **DRAFT**

- **Where:** compiler: leaving `sutram -i`
- **Meaning:** greeting; session ended
- **Default (romanised Sanskrit), as printed:** `Namaste! Satra samapt.⏎`
- **This pack, as printed:** `నమస్కారం! సంభాషణ ముగిసింది.⏎`
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
సూత్రమ్ సంభాషణ సహాయం:
  వ్రాయు("నమస్కారం\n")            పాఠ్యం వ్రాస్తుంది
  చరం x = 5             చరం ప్రకటన
  వ్రాయు(x + 3)            విలువ వ్రాస్తుంది
  పునరావృతం i = 0 నుండి 5 { వ్రాయు(i) }   పునరావృతం
  పంక్తి arr[5]             పంక్తి ప్రకటన
  sarvam                  మొత్తం కార్యక్రమం చూడండి
  nirgat                  సంభాషణ నుండి నిష్క్రమించండి
```
- **In the pack file:** `సూత్రమ్ సంభాషణ సహాయం:⏎  {kw:likha}("నమస్కారం\n")            పాఠ్యం వ్రాస్తుంది⏎  {kw:vitti} x = 5             {kw:vitti} ప్రకటన⏎  {kw:likha}(x + 3)            విలువ వ్రాస్తుంది⏎  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   పునరావృతం⏎  {kw:mala} arr[5]             {kw:mala} ప్రకటన⏎  sarvam                  మొత్తం కార్యక్రమం చూడండి⏎  nirgat                  సంభాషణ నుండి నిష్క్రమించండి⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 57. `msg_open_err` — **DRAFT**

- **Where:** compiler
- **Meaning:** input (source) file not found
- **Default (romanised Sanskrit), as printed:** `Sutram Error: nivesh patra aprapt⏎`
- **This pack, as printed:** `Sutram Error: మూల దస్త్రం దొరకలేదు⏎`
- **Correction:** 

### 58. `msg_ok` — **DRAFT**

- **Where:** compiler: a successful compile
- **Meaning:** done: N bytes compiled
- **Default (romanised Sanskrit), as printed:** `Siddh: 297 baait sankalit⏎`
- **This pack, as printed:** `విజయం: 297 బైట్లు సంకలనం⏎`
- **This message alone:** `విజయం: `
- **Correction:** 

### 59. `msg_bytes` — **DRAFT**

- **Where:** compiler: a successful compile
- **Meaning:** … bytes compiled
- **Default (romanised Sanskrit), as printed:** `Siddh: 297 baait sankalit⏎`
- **This pack, as printed:** `విజయం: 297 బైట్లు సంకలనం⏎`
- **This message alone:** ` బైట్లు సంకలనం⏎`
- **Correction:** 

### 60. `msg_namespace_error` — **DRAFT**

- **Where:** compiler
- **Meaning:** invalid import (form: module@alias, alias up to 31 bytes)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ashuddh yoj (roop: ghatak@upanaam, upanaam 31 baait tak)⏎`
- **This pack, as printed:** `Sutram Error: అశుద్ధ చేర్చు (రూపం: భాగం@మారుపేరు, మారుపేరు 31 బైట్ల వరకు)⏎`
- **In the pack file:** `Sutram Error: అశుద్ధ {kw:yoj} (రూపం: భాగం@మారుపేరు, మారుపేరు 31 బైట్ల వరకు)⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 61. `msg_namespace_module_missing` — **UNSURE**

- **Where:** compiler
- **Meaning:** module file not found
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ghatak patra aprapt⏎`
- **This pack, as printed:** `Sutram Error: భాగ దస్త్రం దొరకలేదు⏎`
- **Doubt:** 'భాగం' (part) for a module; check.
- **Correction:** 

### 62. `msg_namespace_alias_reuse` — **DRAFT**

- **Where:** compiler
- **Meaning:** alias already used (for another module)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: upanaam purv-niyukt (anya ghatak)⏎`
- **This pack, as printed:** `Sutram Error: మారుపేరు ఇప్పటికే వాడబడింది (వేరే భాగానికి)⏎`
- **Correction:** 

### 63. `r51_alias_conflict` — **DRAFT**

- **Where:** compiler
- **Meaning:** alias already used (for another module)
- **Default (romanised Sanskrit), as printed:** `prog.sm:2: Sutram Error [E_MODULE_ALIAS_REUSE]: upanaam purv-niyukt (anya ghatak)⏎`
- **This pack, as printed:** `prog.sm:2: Sutram Error [E_MODULE_ALIAS_REUSE]: మారుపేరు ఇప్పటికే వాడబడింది (వేరే భాగానికి)⏎`
- **This message alone:** `: Sutram Error [E_MODULE_ALIAS_REUSE]: మారుపేరు ఇప్పటికే వాడబడింది (వేరే భాగానికి)⏎`
- **Correction:** 

### 64. `msg_namespace_func_limit` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of module function names exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ghatak prakriya-naam seema atikram⏎`
- **This pack, as printed:** `Sutram Error: భాగ ప్రక్రియ-పేర్ల పరిమితి దాటింది⏎`
- **Correction:** 

### 65. `msg_import_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the expanded source exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: vistarit srot seema atikram⏎`
- **This pack, as printed:** `Sutram Error: విస్తరించిన మూలం పరిమితి దాటింది⏎`
- **Correction:** 

### 66. `graph_cycle_prefix` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** import cycle: a -> b -> a
- **Default (romanised Sanskrit), as printed:** `prog.sm:1: Sutram Error [E_MODULE_CYCLE] yoj chakra: a -> b -> a`
- **This pack, as printed:** `prog.sm:1: Sutram Error [E_MODULE_CYCLE] చేర్పు చక్రం: a -> b -> a`
- **This message alone:** `చేర్పు చక్రం: `
- **Correction:** 

### 67. `graph_missing_prefix` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** import file not found: NAME
- **Default (romanised Sanskrit), as printed:** `prog.sm:1: Sutram Error [E_MODULE_MISSING] yoj patra aprapt: ganit`
- **This pack, as printed:** `prog.sm:1: Sutram Error [E_MODULE_MISSING] చేర్పు దస్త్రం దొరకలేదు: ganit`
- **This message alone:** `చేర్పు దస్త్రం దొరకలేదు: `
- **Correction:** 

### 68. `graph_invalid_prefix` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** invalid module name
- **Default (romanised Sanskrit), as printed:** `prog.sm:1: Sutram Error [E_MODULE_INVALID] ashuddh ghatak naam`
- **This pack, as printed:** `prog.sm:1: Sutram Error [E_MODULE_INVALID] అశుద్ధ భాగం పేరు`
- **This message alone:** `అశుద్ధ భాగం పేరు`
- **Correction:** 

### 69. `msg_ast_overflow` — **UNSURE**

- **Where:** compiler
- **Meaning:** limit of the syntax tree exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: vakya-vriksh seema atikram⏎`
- **This pack, as printed:** `Sutram Error: వాక్య-వృక్షం పరిమితి దాటింది⏎`
- **Doubt:** 'syntax tree' is a coined technical term here; check it.
- **Correction:** 

### 70. `msg_func_params_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the function parameter list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya tark-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ప్రక్రియ ప్రమాణ-జాబితా పరిమితి దాటింది⏎`
- **Correction:** 

### 71. `msg_var_table_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the variable list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: vitti-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: చరం జాబితా పరిమితి దాటింది⏎`
- **In the pack file:** `Sutram Error: {kw:vitti} జాబితా పరిమితి దాటింది⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 72. `msg_func_table_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the function list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ప్రక్రియ జాబితా పరిమితి దాటింది⏎`
- **Correction:** 

### 73. `msg_patch_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the call list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: aahvan-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: పిలుపు జాబితా పరిమితి దాటింది⏎`
- **Correction:** 

### 74. `msg_func_defs_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the function definition list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya paribhasha-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ప్రక్రియ నిర్వచన-జాబితా పరిమితి దాటింది⏎`
- **Correction:** 

### 75. `msg_r9_guna_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** guna limit exceeded (1024)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: guna seema atikram (1024)⏎`
- **This pack, as printed:** `Sutram Error: గుణం పరిమితి దాటింది (1024)⏎`
- **In the pack file:** `Sutram Error: {kw:guna} పరిమితి దాటింది (1024)⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 76. `msg_break_patch_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** too many krama (break) in a loop
- **Default (romanised Sanskrit), as printed:** `Sutram Error: chakra me krama seema atikram⏎`
- **This pack, as printed:** `Sutram Error: పునరావృతం లో క్రమం పరిమితి దాటింది⏎`
- **In the pack file:** `Sutram Error: {kw:chakra} లో {kw:krama} పరిమితి దాటింది⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 77. `msg_continue_patch_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** too many agrim (continue) in a loop
- **Default (romanised Sanskrit), as printed:** `Sutram Error: chakra me agrim seema atikram⏎`
- **This pack, as printed:** `Sutram Error: పునరావృతం లో కొనసాగు పరిమితి దాటింది⏎`
- **In the pack file:** `Sutram Error: {kw:chakra} లో {kw:agrim} పరిమితి దాటింది⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 78. `msg_code_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the machine code exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: yantra-bhasha seema atikram⏎`
- **This pack, as printed:** `Sutram Error: యంత్ర భాష పరిమితి దాటింది⏎`
- **Correction:** 

### 79. `msg_rachana_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of the rachana list exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rachana-suchi seema atikram⏎`
- **This pack, as printed:** `Sutram Error: రచన జాబితా పరిమితి దాటింది⏎`
- **In the pack file:** `Sutram Error: {kw:rachana} జాబితా పరిమితి దాటింది⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 80. `msg_rachana_fields_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of rachana fields exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: rachana kshetra seema atikram⏎`
- **This pack, as printed:** `Sutram Error: రచన క్షేత్రాల పరిమితి దాటింది⏎`
- **In the pack file:** `Sutram Error: {kw:rachana} క్షేత్రాల పరిమితి దాటింది⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 81. `msg_block_nesting_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of block depth exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: khand gahrai seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ఖండ లోతు పరిమితి దాటింది⏎`
- **Correction:** 

### 82. `msg_block_stmt_overflow` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of statements in a block exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: khand kathan seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ఖండంలో వాక్యాల పరిమితి దాటింది⏎`
- **Correction:** 

### 83. `r55_msg_proto_duplicate` — **DRAFT**

- **Where:** compiler
- **Meaning:** function forward-declared again
- **Default (romanised Sanskrit), as printed:** `Sutram Error: punah prakriya purv-ghoshana⏎`
- **This pack, as printed:** `Sutram Error: ప్రక్రియకు మళ్ళీ ముందస్తు ప్రకటన⏎`
- **Correction:** 

### 84. `r55_msg_proto_missing` — **DRAFT**

- **Where:** compiler
- **Meaning:** function forward-declared but never defined
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya purv-ghoshana paribhasha-rahit⏎`
- **This pack, as printed:** `Sutram Error: ప్రక్రియకు ముందస్తు ప్రకటన ఉంది, నిర్వచనం లేదు⏎`
- **Correction:** 

### 85. `r55_msg_proto_signature` — **UNSURE**

- **Where:** compiler
- **Meaning:** forward declaration and definition differ (arguments/type)
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya purv-ghoshana va paribhasha bhinn (tark/prakar)⏎`
- **This pack, as printed:** `Sutram Error: ప్రక్రియ ముందస్తు ప్రకటన మరియు నిర్వచనం వేరు (ప్రమాణాలు/రకం)⏎`
- **Doubt:** 'forward declaration' (a prototype) is a coined term; check it.
- **Correction:** 

### 86. `r55_msg_proto_capacity` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of function forward declarations exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: prakriya purv-ghoshana seema atikram⏎`
- **This pack, as printed:** `Sutram Error: ప్రక్రియ ముందస్తు ప్రకటనల పరిమితి దాటింది⏎`
- **Correction:** 

### 87. `r56_msg_global_capacity` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of module-level variables exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: ghatak-star vitti seema atikram⏎`
- **This pack, as printed:** `Sutram Error: భాగ-స్థాయి చరం పరిమితి దాటింది⏎`
- **In the pack file:** `Sutram Error: భాగ-స్థాయి {kw:vitti} పరిమితి దాటింది⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 88. `r56_msg_global_duplicate` — **DRAFT**

- **Where:** compiler
- **Meaning:** module-level variable name declared again
- **Default (romanised Sanskrit), as printed:** `Sutram Error: punah ghatak-star vitti naam⏎`
- **This pack, as printed:** `Sutram Error: భాగ-స్థాయి చరం పేరు మళ్ళీ⏎`
- **In the pack file:** `Sutram Error: భాగ-స్థాయి {kw:vitti} పేరు మళ్ళీ⏎`  (`{kw:…}` is the pack's own keyword)
- **Correction:** 

### 89. `r56_msg_patch_capacity` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of global value references exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error: sarvatrik mulya sandarbh seema atikram⏎`
- **This pack, as printed:** `Sutram Error: సార్వత్రిక విలువ సూచనల పరిమితి దాటింది⏎`
- **Correction:** 

### 90. `mg_e_cycle` — **DRAFT**

- **Where:** compiler: module graph
- **Meaning:** import cycle: a -> b -> a
- **Default (romanised Sanskrit), as printed:** `prog.sm:1:Sutram Error [E_MODULE_CYCLE]: yoj chakra: a -> b -> a`
- **This pack, as printed:** `prog.sm:1:Sutram Error [E_MODULE_CYCLE]: చేర్పు చక్రం: a -> b -> a`
- **This message alone:** `Sutram Error [E_MODULE_CYCLE]: చేర్పు చక్రం: `
- **Correction:** 

### 91. `mg_e_noexp2` — **UNSURE**

- **Where:** compiler: middle of 'not exported'
- **Meaning:** 'SYM' [from] module 'MOD' [is] not exported
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' ghatak 'vec' se aniryat⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' భాగం 'vec' నుండి ఎగుమతి కాలేదు⏎`
- **This message alone:** `' భాగం '`
- **Doubt:** Order fixed by the code: 'SYM' <this> 'MOD' <noexp3>. Check that 'SYM … MOD … not exported' reads as one sentence.
- **Correction:** 

### 92. `mg_e_noexp3` — **UNSURE**

- **Where:** compiler: end of 'not exported'
- **Meaning:** … not exported from module MOD
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' ghatak 'vec' se aniryat⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' భాగం 'vec' నుండి ఎగుమతి కాలేదు⏎`
- **This message alone:** `' నుండి ఎగుమతి కాలేదు⏎`
- **Doubt:** The case suffix is printed after a space ('f' <suffix>); written Telugu normally attaches it to the word (with a quoted code name, say which you prefer). The checker keeps the default's leading "' ", so fixing this needs that rule relaxed for this message.
- **Correction:** 

### 93. `mg_e_dupexp1` — **DRAFT**

- **Where:** compiler
- **Meaning:** exported again: 'SYM', module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: punah niryat 'thing', ghatak 'dup'`
- **This pack, as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: మళ్ళీ ఎగుమతి 'thing', భాగం 'dup'`
- **This message alone:** `Sutram Error [E_MODULE_DUP_EXPORT]: మళ్ళీ ఎగుమతి '`
- **Correction:** 

### 94. `mg_e_dupexp2` — **DRAFT**

- **Where:** compiler: middle
- **Meaning:** …, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: punah niryat 'thing', ghatak 'dup'`
- **This pack, as printed:** `Sutram Error [E_MODULE_DUP_EXPORT]: మళ్ళీ ఎగుమతి 'thing', భాగం 'dup'`
- **This message alone:** `', భాగం '`
- **Correction:** 

### 95. `mg_e_undef1` — **DRAFT**

- **Where:** compiler
- **Meaning:** export 'SYM' has no definition, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: niryat 'thing' paribhasha-rahit, ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: ఎగుమతి 'thing' కి నిర్వచనం లేదు, భాగం 'vec'`
- **This message alone:** `Sutram Error [E_EXPORT_UNDEFINED]: ఎగుమతి '`
- **Correction:** 

### 96. `mg_e_undef2` — **UNSURE**

- **Where:** compiler: middle
- **Meaning:** … has no definition, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: niryat 'thing' paribhasha-rahit, ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: ఎగుమతి 'thing' కి నిర్వచనం లేదు, భాగం 'vec'`
- **This message alone:** `' కి నిర్వచనం లేదు, భాగం '`
- **Doubt:** The case suffix is printed after a space ('f' <suffix>); written Telugu normally attaches it to the word (with a quoted code name, say which you prefer). The checker keeps the default's leading "' ", so fixing this needs that rule relaxed for this message.
- **Correction:** 

### 97. `mg_e_unknown1` — **DRAFT**

- **Where:** compiler
- **Meaning:** unknown symbol 'SYM', module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: agyat sanket 'thing', ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: తెలియని చిహ్నం 'thing', భాగం 'vec'`
- **This message alone:** `Sutram Error [E_EXPORT_UNDEFINED]: తెలియని చిహ్నం '`
- **Correction:** 

### 98. `mg_e_unknown2` — **DRAFT**

- **Where:** compiler: middle
- **Meaning:** …, module 'MOD'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: agyat sanket 'thing', ghatak 'vec'`
- **This pack, as printed:** `Sutram Error [E_EXPORT_UNDEFINED]: తెలియని చిహ్నం 'thing', భాగం 'vec'`
- **This message alone:** `', భాగం '`
- **Correction:** 

### 99. `mg_e_depth` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of import depth exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_DEPTH]: yoj gahrai seema atikram⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_DEPTH]: చేర్పు లోతు పరిమితి దాటింది⏎`
- **Correction:** 

### 100. `mg_e_valias1` — **DRAFT**

- **Where:** compiler
- **Meaning:** a v1 module 'MOD' needs an alias: yoj MOD@upanaam
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 ghatak 'vec' upanaam avashyak: yoj vec@upanaam`
- **This pack, as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 భాగం 'vec' కు మారుపేరు అవసరం: చేర్చు vec@upanaam`
- **This message alone:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 భాగం '`
- **Correction:** 

### 101. `mg_e_valias2` — **UNSURE**

- **Where:** compiler: middle
- **Meaning:** … needs an alias: yoj MOD@upanaam
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 ghatak 'vec' upanaam avashyak: yoj vec@upanaam`
- **This pack, as printed:** `Sutram Error [E_MODULE_V1_ALIAS]: v1 భాగం 'vec' కు మారుపేరు అవసరం: చేర్చు vec@upanaam`
- **This message alone:** `' కు మారుపేరు అవసరం: చేర్చు `
- **In the pack file:** `' కు మారుపేరు అవసరం: {kw:yoj} `  (`{kw:…}` is the pack's own keyword)
- **Doubt:** The case suffix is printed after a space ('f' <suffix>); written Telugu normally attaches it to the word (with a quoted code name, say which you prefer). The checker keeps the default's leading "' ", so fixing this needs that rule relaxed for this message.
- **Correction:** 

### 102. `mg_e_limit` — **DRAFT**

- **Where:** compiler
- **Meaning:** limit of modules/imports exceeded
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_MODULE_LIMIT]: ghatak/yoj seema atikram⏎`
- **This pack, as printed:** `Sutram Error [E_MODULE_LIMIT]: భాగం/చేర్పు పరిమితి దాటింది⏎`
- **Correction:** 

### 103. `r66_msg_bad_utf8` — **DRAFT**

- **Where:** compiler
- **Meaning:** invalid or broken Indian-script name
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_UTF8]: ashuddh ya khandit bharatiya naam⏎`
- **This pack, as printed:** `Sutram Error [E_UTF8]: అశుద్ధమైన లేదా విరిగిన భారతీయ పేరు⏎`
- **Correction:** 

### 104. `r68_utf8_tail` — **DRAFT**

- **Where:** compiler
- **Meaning:** invalid or broken UTF-8 in the source
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_UTF8]: prog.sm:2: srot me ashuddh ya khandit UTF-8⏎`
- **This pack, as printed:** `Sutram Error [E_UTF8]: prog.sm:2: మూలంలో అశుద్ధమైన లేదా విరిగిన UTF-8⏎`
- **This message alone:** `: మూలంలో అశుద్ధమైన లేదా విరిగిన UTF-8⏎`
- **Correction:** 

### 105. `r68_value_tail` — **DRAFT**

- **Where:** compiler
- **Meaning:** an abbreviation is not a value: 'वि॰'
- **Default (romanised Sanskrit), as printed:** `Sutram Error [E_ABBREVIATION_VALUE]: prog.sm:2: sankshep shabd mulya nahi: 'वि॰'`
- **This pack, as printed:** `Sutram Error [E_ABBREVIATION_VALUE]: prog.sm:2: సంక్షేప పదం విలువ కాదు: 'वि॰'`
- **This message alone:** `: సంక్షేప పదం విలువ కాదు: '`
- **Correction:** 

### 106. `ide.st_pankti_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** line N (start of the status line)
- **Default (romanised Sanskrit), as printed:** `pankti 12   stambh 4   |   bhasha: …`
- **This pack, as printed:** `వరుస 12   నిలువు 4   |   భాష: …`
- **This message alone:** `వరుస `
- **Correction:** 

### 107. `ide.st_stambh_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** column N
- **Default (romanised Sanskrit), as printed:** `pankti 12   stambh 4   |   bhasha: …`
- **This pack, as printed:** `వరుస 12   నిలువు 4   |   భాష: …`
- **This message alone:** `   నిలువు `
- **Correction:** 

### 108. `ide.st_bhasha_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** | language: NAME
- **Default (romanised Sanskrit), as printed:** `…4   |   bhasha: हिन्दी`
- **This pack, as printed:** `…4   |   భాష: हिन्दी`
- **This message alone:** `   |   భాష: `
- **Correction:** 

### 109. `ide.st_akshara_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** | letters (clusters): N
- **Default (romanised Sanskrit), as printed:** `…   |   akshara: 26`
- **This pack, as printed:** `…   |   అక్షరాలు: 26`
- **This message alone:** `   |   అక్షరాలు: `
- **Correction:** 

### 110. `ide.st_lipi_w` — **DRAFT**

- **Where:** IDE status line, typing mode on
- **Meaning:** | script: NAME (the typing script)
- **Default (romanised Sanskrit), as printed:** `…   |   lipi: தமிழ்`
- **This pack, as printed:** `…   |   లిపి: தமிழ்`
- **This message alone:** `   |   లిపి: `
- **Correction:** 

### 111. `ide.st_sanchit_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** saved
- **Default (romanised Sanskrit), as printed:** `…   |   sanchit`
- **This pack, as printed:** `…   |   భద్రపరచబడింది`
- **This message alone:** `భద్రపరచబడింది`
- **Correction:** 

### 112. `ide.st_asanchit_w` — **DRAFT**

- **Where:** IDE status line
- **Meaning:** not saved *
- **Default (romanised Sanskrit), as printed:** `…   |   asanchit *`
- **This pack, as printed:** `…   |   భద్రపరచలేదు *`
- **This message alone:** `భద్రపరచలేదు *`
- **Correction:** 

### 113. `ide.st_notfound_w` — **DRAFT**

- **Where:** IDE status line, after Find
- **Meaning:** find: not found
- **Default (romanised Sanskrit), as printed:** `anwesh: nahi mila`
- **This pack, as printed:** `వెతుకు: దొరకలేదు`
- **Correction:** 

### 114. `ide.lang_swayam_w` — **DRAFT**

- **Where:** IDE status line: language Auto
- **Meaning:** automatic (detect the script)
- **Default (romanised Sanskrit), as printed:** `   |   bhasha: swayam`
- **This pack, as printed:** `   |   భాష: స్వయంచాలకం`
- **This message alone:** `స్వయంచాలకం`
- **Correction:** 

### 115. `ide.lang_swayam_sk_w` — **DRAFT**

- **Where:** IDE status line: Auto found Devanagari
- **Meaning:** automatic (Sanskrit)
- **Default (romanised Sanskrit), as printed:** `   |   bhasha: swayam (sanskrit)`
- **This pack, as printed:** `   |   భాష: స్వయంచాలకం (సంస్కృతం)`
- **This message alone:** `స్వయంచాలకం (సంస్కృతం)`
- **Correction:** 

### 116. `ide.lang_mool_w` — **DRAFT**

- **Where:** IDE status line: language Core
- **Meaning:** core (Latin keywords)
- **Default (romanised Sanskrit), as printed:** `   |   bhasha: mool`
- **This pack, as printed:** `   |   భాష: మూలం`
- **This message alone:** `మూలం`
- **Correction:** 

### 117. `ide.msg_ready` — **DRAFT**

- **Where:** IDE output pane, at start and after Clear shell
- **Meaning:** ready. F5 compiles and runs the program in the editor
- **Default (romanised Sanskrit), as printed:** `Taiyar. F5: sampadak ka karyakram sankalan aur chalan.⏎`
- **This pack, as printed:** `సిద్ధం. F5: సంపాదకంలోని కార్యక్రమాన్ని సంకలనం చేసి నడుపుతుంది.⏎`
- **Correction:** 

### 118. `ide.msg_compile_failed` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [compilation failed]
- **Default (romanised Sanskrit), as printed:** `[sankalan asaphal]⏎`
- **This pack, as printed:** `[సంకలనం విఫలం]⏎`
- **Correction:** 

### 119. `ide.msg_run_failed` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the program ended abnormally]
- **Default (romanised Sanskrit), as printed:** `[karyakram asamanya roop se samapt]⏎`
- **This pack, as printed:** `[కార్యక్రమం అసాధారణంగా ముగిసింది]⏎`
- **Correction:** 

### 120. `ide.msg_file_failed` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [reading/writing the file failed]
- **Default (romanised Sanskrit), as printed:** `[patra padhne/likhne me asaphal]⏎`
- **This pack, as printed:** `[దస్త్రం చదవడం/వ్రాయడం విఫలం]⏎`
- **Correction:** 

### 121. `ide.msg_input_large` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the file is too big; editor limit 64 KiB]
- **Default (romanised Sanskrit), as printed:** `[patra bahut bada; sampadak seema 64 KiB]⏎`
- **This pack, as printed:** `[దస్త్రం చాలా పెద్దది; సంపాదక పరిమితి 64 KiB]⏎`
- **Correction:** 

### 122. `ide.msg_shell_limit` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the shell history is full; clear the shell first]
- **Default (romanised Sanskrit), as printed:** `[khol ka itihas purna; pahle khol rikta karein]⏎`
- **This pack, as printed:** `[సంభాషణ చరిత్ర నిండింది; ముందు సంభాషణను ఖాళీ చేయండి]⏎`
- **Correction:** 

### 123. `ide.msg_timeout` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [the process ran more than 10 seconds; stopped]
- **Default (romanised Sanskrit), as printed:** `[prakriya 10 sekand se adhik; samapt ki gayi]⏎`
- **This pack, as printed:** `[ప్రక్రియ 10 సెకన్ల కంటే ఎక్కువ నడిచింది; ఆపబడింది]⏎`
- **Correction:** 

### 124. `ide.msg_missing_compiler` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [win\sutram.exe not found: build the compiler first]
- **Default (romanised Sanskrit), as printed:** `[win\sutram.exe nahi mila: pahle sankalak banayein]⏎`
- **This pack, as printed:** `[win\sutram.exe దొరకలేదు: ముందు సంకలకాన్ని నిర్మించండి]⏎`
- **Correction:** 

### 125. `ide.msg_missing_lang` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [native word packs unavailable: see lang\*.lang; the core words work]
- **Default (romanised Sanskrit), as printed:** `[deshi shabda-pak anupalabdh: lang\*.lang dekhein; mool shabda kaam karte hain]⏎`
- **This pack, as printed:** `[దేశీ పద ప్యాక్‌లు లేవు: lang\*.lang చూడండి; మూల పదాలు పనిచేస్తాయి]⏎`
- **Correction:** 

### 126. `ide.msg_partial_lang` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [some word packs unavailable or invalid: see lang\*.lang]
- **Default (romanised Sanskrit), as printed:** `[kuchh shabda-pak anupalabdh ya ashuddh: lang\*.lang dekhein]⏎`
- **This pack, as printed:** `[కొన్ని పద ప్యాక్‌లు లేవు లేదా అశుద్ధం: lang\*.lang చూడండి]⏎`
- **Correction:** 

### 127. `ide.msg_pipe_fail` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [creating the process or the pipe failed]
- **Default (romanised Sanskrit), as printed:** `[prakriya ya nalika nirman asaphal]⏎`
- **This pack, as printed:** `[ప్రక్రియ లేదా గొట్టం సృష్టి విఫలం]⏎`
- **Correction:** 

### 128. `ide.msg_more_output` — **DRAFT**

- **Where:** IDE output pane
- **Meaning:** [output cut at 32 KiB]
- **Default (romanised Sanskrit), as printed:** `[phal 32 KiB par kata]⏎`
- **This pack, as printed:** `[ఫలితం 32 KiB వద్ద కత్తిరించబడింది]⏎`
- **Correction:** 


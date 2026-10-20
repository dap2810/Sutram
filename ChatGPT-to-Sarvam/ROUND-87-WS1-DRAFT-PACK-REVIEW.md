# Sutram ROUND-87 — Eight DRAFT language packs: one-pass review sheet

**Snapshot:** `64ea953a909eb77ebe5f278691407848014b9b6f` (live main v238 at the start of review). **Status:** DRAFT ONLY—no native speaker has approved this wording. The machine audit found **39 candidate occurrences in 33 distinct message keys** across eight packs. The sheet consolidates repeated markers into a single decision per actual message.

**How to review:** Each entry shows the current decoded pack text exactly as it appears before `{kw:...}` expansion. Check the entire sentence for grammar and meaning. Mark **KEEP** or provide a complete **REPLACE** string. Preserve `Sutram Error`, `[E_...]`, placeholders, quotations around inserted names, leading/trailing punctuation, and embedded line breaks. Review the JSON companion for byte-relevant whitespace and escaping. Do not auto-correct merely because a candidate was flagged.

| Pack | Flags to review | Distinct messages |
|---|---:|---:|
| Marathi | 3 | 3 |
| Bengali | 0 | 0 |
| Punjabi | 6 | 5 |
| Odia | 6 | 5 |
| Tamil | 6 | 5 |
| Telugu | 6 | 5 |
| Kannada | 6 | 5 |
| Malayalam | 6 | 5 |
| **Total** | **39** | **33** |

**Important:** Marathi shares a few Devanagari fragments with Sanskrit; this can be legitimate. The six other flagged packs have extra `{kw:...}` insertions, often intentional references to a language-selected keyword. Bengali has no machine-raised review candidates, **not** verified linguistic correctness. All 128 entries in every DRAFT pack remain unverified until a speaker reviews them.

## 1. Marathi — 3 flags (3 messages)

### 1. `r4_msg_hint_old`

*Source:* `lang/marathi.sandesh:35` · *Candidate flags:* identical to canonical Sanskrit text

**Current text (decoded; placeholders unexpanded):**

```text
सूचना: '
```

**Reviewer question:** Is this exact shared short wording idiomatic here, or should it differ from Sanskrit? For a prefix fragment, consider the fully concatenated diagnostic.

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 2. `r5_msg_field_hint`

*Source:* `lang/marathi.sandesh:63` · *Candidate flags:* identical to canonical Sanskrit text

**Current text (decoded; placeholders unexpanded):**

```text
सूचना: '
```

**Reviewer question:** Is this exact shared short wording idiomatic here, or should it differ from Sanskrit? For a prefix fragment, consider the fully concatenated diagnostic.

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 3. `ide.st_bhasha_w`

*Source:* `lang/marathi.sandesh:226` · *Candidate flags:* identical to canonical Sanskrit text

**Current text (decoded; placeholders unexpanded):**

```text
   |   भाषा: 
```

**Reviewer question:** Is this exact shared short wording idiomatic here, or should it differ from Sanskrit? For a prefix fragment, consider the fully concatenated diagnostic.

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

## 2. Bengali — 0 flags (0 messages)

No R83 structural-review candidates. This does not constitute native-speaker review or approval.

## 3. Punjabi — 6 flags (5 messages)

### 4. `msg_kosh_required`

*Source:* `lang/punjabi.sandesh:85` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: {kw:kosh} ਕਾਰਜ ਲਈ {kw:kosh} {kw:vitti} ਲੋੜੀਂਦਾ
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 5. `msg_shell_help`

*Source:* `lang/punjabi.sandesh:119` · *Candidate flags:* extra `{kw:vitti}`; extra `{kw:mala}`

**Current text (decoded; placeholders unexpanded):**

```text
ਸੂਤਰਮ੍ ਸੰਵਾਦ ਸਹਾਇਤਾ:
  {kw:likha}("ਨਮਸਤੇ\n")            ਲਿਖਤ ਛਾਪਦਾ ਹੈ
  {kw:vitti} x = 5             {kw:vitti} ਘੋਸ਼ਣਾ
  {kw:likha}(x + 3)            ਮੁੱਲ ਛਾਪਦਾ ਹੈ
  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   ਦੁਹਰਾਓ
  {kw:mala} arr[5]             {kw:mala} ਘੋਸ਼ਣਾ
  sarvam                  ਪੂਰਾ ਕਾਰਜਕ੍ਰਮ ਵੇਖੋ
  nirgat                  ਸੰਵਾਦ ਤੋਂ ਬਾਹਰ
```

**Reviewer question:** Are `{kw:vitti}` and `{kw:mala}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 6. `msg_var_table_overflow`

*Source:* `lang/punjabi.sandesh:149` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: {kw:vitti}-ਸੂਚੀ ਦੀ ਸੀਮਾ ਪਾਰ
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 7. `r56_msg_global_capacity`

*Source:* `lang/punjabi.sandesh:181` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: ਮੌਡਿਊਲ-ਪੱਧਰ {kw:vitti} ਦੀ ਸੀਮਾ ਪਾਰ
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 8. `r56_msg_global_duplicate`

*Source:* `lang/punjabi.sandesh:183` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: ਮੌਡਿਊਲ-ਪੱਧਰ {kw:vitti} ਦਾ ਨਾਮ ਦੁਬਾਰਾ
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

## 4. Odia — 6 flags (5 messages)

### 9. `msg_kosh_required`

*Source:* `lang/odia.sandesh:85` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: {kw:kosh} କାର୍ଯ୍ୟ ପାଇଁ {kw:kosh} {kw:vitti} ଆବଶ୍ୟକ
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 10. `msg_shell_help`

*Source:* `lang/odia.sandesh:119` · *Candidate flags:* extra `{kw:vitti}`; extra `{kw:mala}`

**Current text (decoded; placeholders unexpanded):**

```text
ସୂତ୍ରମ୍ ସଂଳାପ ସାହାଯ୍ୟ:
  {kw:likha}("ନମସ୍କାର\n")            ଲେଖା ଦେଖାଏ
  {kw:vitti} x = 5             {kw:vitti} ଘୋଷଣା
  {kw:likha}(x + 3)            ମୂଲ୍ୟ ଦେଖାଏ
  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   ପୁନରାବୃତ୍ତି
  {kw:mala} arr[5]             {kw:mala} ଘୋଷଣା
  sarvam                  ସମ୍ପୂର୍ଣ୍ଣ କାର୍ଯ୍ୟକ୍ରମ ଦେଖନ୍ତୁ
  nirgat                  ସଂଳାପରୁ ବାହାରକୁ
```

**Reviewer question:** Are `{kw:vitti}` and `{kw:mala}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 11. `msg_var_table_overflow`

*Source:* `lang/odia.sandesh:149` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: {kw:vitti}-ତାଲିକାର ସୀମା ଅତିକ୍ରମ
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 12. `r56_msg_global_capacity`

*Source:* `lang/odia.sandesh:181` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: ମଡ୍ୟୁଲ୍-ସ୍ତରୀୟ {kw:vitti} ର ସୀମା ଅତିକ୍ରମ
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 13. `r56_msg_global_duplicate`

*Source:* `lang/odia.sandesh:183` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: ମଡ୍ୟୁଲ୍-ସ୍ତରୀୟ {kw:vitti} ନାମ ପୁନର୍ବାର
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

## 5. Tamil — 6 flags (5 messages)

### 14. `msg_kosh_required`

*Source:* `lang/tamil.sandesh:85` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: {kw:kosh} செயலுக்கு {kw:kosh} {kw:vitti} தேவை
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 15. `msg_shell_help`

*Source:* `lang/tamil.sandesh:119` · *Candidate flags:* extra `{kw:vitti}`; extra `{kw:mala}`

**Current text (decoded; placeholders unexpanded):**

```text
சூத்திரம் உரையாடல் உதவி:
  {kw:likha}("வணக்கம்\n")            உரையை எழுதும்
  {kw:vitti} x = 5             {kw:vitti} அறிவிப்பு
  {kw:likha}(x + 3)            மதிப்பை எழுதும்
  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   மீள்செயல்
  {kw:mala} arr[5]             {kw:mala} அறிவிப்பு
  sarvam                  முழு நிரலைக் காண்
  nirgat                  உரையாடலிலிருந்து வெளியேறு
```

**Reviewer question:** Are `{kw:vitti}` and `{kw:mala}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 16. `msg_var_table_overflow`

*Source:* `lang/tamil.sandesh:149` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: {kw:vitti} பட்டியல் வரம்பு மீறல்
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 17. `r56_msg_global_capacity`

*Source:* `lang/tamil.sandesh:181` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: கூறு-நிலை {kw:vitti} வரம்பு மீறல்
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 18. `r56_msg_global_duplicate`

*Source:* `lang/tamil.sandesh:183` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: கூறு-நிலை {kw:vitti} பெயர் மீண்டும்
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

## 6. Telugu — 6 flags (5 messages)

### 19. `msg_kosh_required`

*Source:* `lang/telugu.sandesh:85` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: {kw:kosh} ప్రక్రియకు {kw:kosh} {kw:vitti} అవసరం
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 20. `msg_shell_help`

*Source:* `lang/telugu.sandesh:119` · *Candidate flags:* extra `{kw:vitti}`; extra `{kw:mala}`

**Current text (decoded; placeholders unexpanded):**

```text
సూత్రమ్ సంభాషణ సహాయం:
  {kw:likha}("నమస్కారం\n")            పాఠ్యం వ్రాస్తుంది
  {kw:vitti} x = 5             {kw:vitti} ప్రకటన
  {kw:likha}(x + 3)            విలువ వ్రాస్తుంది
  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   పునరావృతం
  {kw:mala} arr[5]             {kw:mala} ప్రకటన
  sarvam                  మొత్తం కార్యక్రమం చూడండి
  nirgat                  సంభాషణ నుండి నిష్క్రమించండి
```

**Reviewer question:** Are `{kw:vitti}` and `{kw:mala}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 21. `msg_var_table_overflow`

*Source:* `lang/telugu.sandesh:149` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: {kw:vitti} జాబితా పరిమితి దాటింది
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 22. `r56_msg_global_capacity`

*Source:* `lang/telugu.sandesh:181` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: భాగ-స్థాయి {kw:vitti} పరిమితి దాటింది
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 23. `r56_msg_global_duplicate`

*Source:* `lang/telugu.sandesh:183` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: భాగ-స్థాయి {kw:vitti} పేరు మళ్ళీ
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

## 7. Kannada — 6 flags (5 messages)

### 24. `msg_kosh_required`

*Source:* `lang/kannada.sandesh:85` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: {kw:kosh} ಕ್ರಿಯೆಗೆ {kw:kosh} {kw:vitti} ಬೇಕು
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 25. `msg_shell_help`

*Source:* `lang/kannada.sandesh:119` · *Candidate flags:* extra `{kw:vitti}`; extra `{kw:mala}`

**Current text (decoded; placeholders unexpanded):**

```text
ಸೂತ್ರಮ್ ಸಂವಾದ ಸಹಾಯ:
  {kw:likha}("ನಮಸ್ಕಾರ\n")            ಪಠ್ಯ ಬರೆಯುತ್ತದೆ
  {kw:vitti} x = 5             {kw:vitti} ಘೋಷಣೆ
  {kw:likha}(x + 3)            ಮೌಲ್ಯ ಬರೆಯುತ್ತದೆ
  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   ಪುನರಾವರ್ತನೆ
  {kw:mala} arr[5]             {kw:mala} ಘೋಷಣೆ
  sarvam                  ಸಂಪೂರ್ಣ ಕಾರ್ಯಕ್ರಮ ನೋಡಿ
  nirgat                  ಸಂವಾದದಿಂದ ನಿರ್ಗಮಿಸಿ
```

**Reviewer question:** Are `{kw:vitti}` and `{kw:mala}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 26. `msg_var_table_overflow`

*Source:* `lang/kannada.sandesh:149` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: {kw:vitti} ಪಟ್ಟಿಯ ಮಿತಿ ಮೀರಿದೆ
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 27. `r56_msg_global_capacity`

*Source:* `lang/kannada.sandesh:181` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: ಘಟಕ-ಮಟ್ಟದ {kw:vitti} ಮಿತಿ ಮೀರಿದೆ
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 28. `r56_msg_global_duplicate`

*Source:* `lang/kannada.sandesh:183` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: ಘಟಕ-ಮಟ್ಟದ {kw:vitti} ಹೆಸರು ಮತ್ತೆ
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

## 8. Malayalam — 6 flags (5 messages)

### 29. `msg_kosh_required`

*Source:* `lang/malayalam.sandesh:85` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: {kw:kosh} ക്രിയയ്ക്ക് {kw:kosh} {kw:vitti} ആവശ്യം
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 30. `msg_shell_help`

*Source:* `lang/malayalam.sandesh:119` · *Candidate flags:* extra `{kw:vitti}`; extra `{kw:mala}`

**Current text (decoded; placeholders unexpanded):**

```text
സൂത്രം സംവാദ സഹായം:
  {kw:likha}("നമസ്കാരം\n")            വാചകം എഴുതുന്നു
  {kw:vitti} x = 5             {kw:vitti} പ്രഖ്യാപനം
  {kw:likha}(x + 3)            മൂല്യം എഴുതുന്നു
  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   ആവർത്തനം
  {kw:mala} arr[5]             {kw:mala} പ്രഖ്യാപനം
  sarvam                  മുഴുവൻ കാര്യക്രമവും കാണുക
  nirgat                  സംവാദത്തിൽ നിന്ന് പുറത്തുകടക്കുക
```

**Reviewer question:** Are `{kw:vitti}` and `{kw:mala}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 31. `msg_var_table_overflow`

*Source:* `lang/malayalam.sandesh:149` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: {kw:vitti} പട്ടിക പരിധി കവിഞ്ഞു
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 32. `r56_msg_global_capacity`

*Source:* `lang/malayalam.sandesh:181` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: ഘടക-തല {kw:vitti} പരിധി കവിഞ്ഞു
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

### 33. `r56_msg_global_duplicate`

*Source:* `lang/malayalam.sandesh:183` · *Candidate flags:* extra `{kw:vitti}`

**Current text (decoded; placeholders unexpanded):**

```text
Sutram Error: ഘടക-തല {kw:vitti} പേര് വീണ്ടും
```

**Reviewer question:** Are `{kw:vitti}` appropriate at each marked position? Is the message clear when those placeholders become the selected language's actual keywords, without introducing an incorrect identifier?

**Decision:** ☐ KEEP unchanged  ☐ REPLACE

**Complete corrected text:** _Write here; preserve all required formatting._

---

**Change control:** These are candidate strings, not proven defects. Return approved changes to Sarvam; preserve canonical identifiers and run `tools/sandesh.py --check` and pack-specific regression gates after any edits. Do not change accepted goldens solely to satisfy a translation rewrite.

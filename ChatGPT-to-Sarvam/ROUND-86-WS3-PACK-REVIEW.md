# ROUND-86 — One-pass review sheet for 41 Sutram language candidates

**Pinned Git snapshot:** `64755d0f4dfdf89711f7c63ec94bc6f5917f2c95` (v234 when rendered). **Source:** the current 11 `lang/*.sandesh` packs, cross-referenced against R83's machine-readable 41-candidate inventory. All eleven pack Git blobs still match R83's captured blobs.

This is a **human review queue, not an error list**. Source text is reproduced exactly from each JSON message string, with `\n` escapes visible and `{kw:...}` tokens **not yet expanded**. Preserve `Sutram Error`, `[E_...]` tags, placeholders, quotes around names, and leading/trailing punctuation. For fragments, judge the assembled message, not an isolated prefix.

| Review order | Pack | Tier | Candidate entries |
|---|---|---|---:|
| 1 | Gujarati | SUPPORTED | 0 |
| 2 | Hindi | SUPPORTED | 2 |
| 3 | Sanskrit | SUPPORTED | 0 |
| 4 | Marathi | DRAFT | 3 |
| 5 | Bengali | DRAFT | 0 |
| 6 | Punjabi | DRAFT | 6 |
| 7 | Odia | DRAFT | 6 |
| 8 | Tamil | DRAFT | 6 |
| 9 | Telugu | DRAFT | 6 |
| 10 | Kannada | DRAFT | 6 |
| 11 | Malayalam | DRAFT | 6 |

**Total: 41 review occurrences: five identical short strings and 36 additional keyword placeholders.** An identical word shared between Hindi/Sanskrit may be idiomatic; an added placeholder may be intentional. No hard violation was reported by the original R83 structural scan.

## Owner priority

The owner-approved native-speaker order is **Gujarati → Hindi → Sanskrit**. Gujarati and Sanskrit have no R83 flagged candidates, **not** a native-language approval; Hindi's two items are common Devanagari status labels. The other eight remain DRAFT even if the structure validates. For additional human wording concerns beyond these 41, consult the earlier full 128-entry sheets under `Claude-to-Sarvam/review-r12/` (those older sheets may use stale default text).

**Reviewer response:** For each candidate, mark KEEP or CHANGE and supply the corrected full message string if changed; keep dynamic tokens. Do not edit pack files on the strength of a guess. Sarvam should apply owner-confirmed corrections and run `tools/sandesh.py --check` plus all pack tests.

---

## gujarati (SUPPORTED) — 0 R83 review candidates

No R83 structural-review candidates. All 128 entries are still subject to human wording review; zero flags does not mean linguistically approved.

## hindi (SUPPORTED) — 2 R83 review candidates

**ide.st_bhasha_w** — identical Sanskrit default

- Current exact pack text: `   |   भाषा: `
- Canonical Sanskrit: `   |   भाषा: `
- Question: Is the identical wording natural and intentional in Hindi, or should it be adjusted?
- Correction (native speaker): __________

**ide.st_lipi_w** — identical Sanskrit default

- Current exact pack text: `   |   लिपि: `
- Canonical Sanskrit: `   |   लिपि: `
- Question: Is the identical wording natural and intentional in Hindi, or should it be adjusted?
- Correction (native speaker): __________

## sanskrit (SUPPORTED) — 0 R83 review candidates

No R83 structural-review candidates. All 128 entries are still subject to human wording review; zero flags does not mean linguistically approved.


## marathi (DRAFT) — 3 candidates

**1. `r4_msg_hint_old`** (identical Sanskrit default; line 35)

- Current text: `सूचना: '`
- Question: Does shared Sanskrit spelling fit this language, or should this short label/prefix be localized?
- Reviewer correction: __________

**2. `r5_msg_field_hint`** (identical Sanskrit default; line 63)

- Current text: `सूचना: '`
- Question: Does shared Sanskrit spelling fit this language, or should this short label/prefix be localized?
- Reviewer correction: __________

**3. `ide.st_bhasha_w`** (identical Sanskrit default; line 226)

- Current text: `   |   भाषा: `
- Question: Does shared Sanskrit spelling fit this language, or should this short label/prefix be localized?
- Reviewer correction: __________

## bengali (DRAFT) — 0 candidates

No R83 structural review candidate. Pack still requires native-speaker review.

## punjabi (DRAFT) — 6 candidates

**4. `msg_kosh_required`** (extra placeholder, {kw:vitti}; line 85)

- Current text: `Sutram Error: {kw:kosh} ਕਾਰਜ ਲਈ {kw:kosh} {kw:vitti} ਲੋੜੀਂਦਾ\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**5. `msg_shell_help`** (extra placeholder, {kw:vitti}; line 119)

- Current text: `ਸੂਤਰਮ੍ ਸੰਵਾਦ ਸਹਾਇਤਾ:\n  {kw:likha}(\"ਨਮਸਤੇ\\n\")            ਲਿਖਤ ਛਾਪਦਾ ਹੈ\n  {kw:vitti} x = 5             {kw:vitti} ਘੋਸ਼ਣਾ\n  {kw:likha}(x + 3)            ਮੁੱਲ ਛਾਪਦਾ ਹੈ\n  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   ਦੁਹਰਾਓ\n  {kw:mala} arr[5]             {kw:mala} ਘੋਸ਼ਣਾ\n  sarvam                  ਪੂਰਾ ਕਾਰਜਕ੍ਰਮ ਵੇਖੋ\n  nirgat                  ਸੰਵਾਦ ਤੋਂ ਬਾਹਰ\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**6. `msg_shell_help`** (extra placeholder, {kw:mala}; line 119)

- Current text: `ਸੂਤਰਮ੍ ਸੰਵਾਦ ਸਹਾਇਤਾ:\n  {kw:likha}(\"ਨਮਸਤੇ\\n\")            ਲਿਖਤ ਛਾਪਦਾ ਹੈ\n  {kw:vitti} x = 5             {kw:vitti} ਘੋਸ਼ਣਾ\n  {kw:likha}(x + 3)            ਮੁੱਲ ਛਾਪਦਾ ਹੈ\n  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   ਦੁਹਰਾਓ\n  {kw:mala} arr[5]             {kw:mala} ਘੋਸ਼ਣਾ\n  sarvam                  ਪੂਰਾ ਕਾਰਜਕ੍ਰਮ ਵੇਖੋ\n  nirgat                  ਸੰਵਾਦ ਤੋਂ ਬਾਹਰ\n`
- Question: Does added {kw:mala} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**7. `msg_var_table_overflow`** (extra placeholder, {kw:vitti}; line 149)

- Current text: `Sutram Error: {kw:vitti}-ਸੂਚੀ ਦੀ ਸੀਮਾ ਪਾਰ\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**8. `r56_msg_global_capacity`** (extra placeholder, {kw:vitti}; line 181)

- Current text: `Sutram Error: ਮੌਡਿਊਲ-ਪੱਧਰ {kw:vitti} ਦੀ ਸੀਮਾ ਪਾਰ\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**9. `r56_msg_global_duplicate`** (extra placeholder, {kw:vitti}; line 183)

- Current text: `Sutram Error: ਮੌਡਿਊਲ-ਪੱਧਰ {kw:vitti} ਦਾ ਨਾਮ ਦੁਬਾਰਾ\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

## odia (DRAFT) — 6 candidates

**10. `msg_kosh_required`** (extra placeholder, {kw:vitti}; line 85)

- Current text: `Sutram Error: {kw:kosh} କାର୍ଯ୍ୟ ପାଇଁ {kw:kosh} {kw:vitti} ଆବଶ୍ୟକ\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**11. `msg_shell_help`** (extra placeholder, {kw:vitti}; line 119)

- Current text: `ସୂତ୍ରମ୍ ସଂଳାପ ସାହାଯ୍ୟ:\n  {kw:likha}(\"ନମସ୍କାର\\n\")            ଲେଖା ଦେଖାଏ\n  {kw:vitti} x = 5             {kw:vitti} ଘୋଷଣା\n  {kw:likha}(x + 3)            ମୂଲ୍ୟ ଦେଖାଏ\n  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   ପୁନରାବୃତ୍ତି\n  {kw:mala} arr[5]             {kw:mala} ଘୋଷଣା\n  sarvam                  ସମ୍ପୂର୍ଣ୍ଣ କାର୍ଯ୍ୟକ୍ରମ ଦେଖନ୍ତୁ\n  nirgat                  ସଂଳାପରୁ ବାହାରକୁ\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**12. `msg_shell_help`** (extra placeholder, {kw:mala}; line 119)

- Current text: `ସୂତ୍ରମ୍ ସଂଳାପ ସାହାଯ୍ୟ:\n  {kw:likha}(\"ନମସ୍କାର\\n\")            ଲେଖା ଦେଖାଏ\n  {kw:vitti} x = 5             {kw:vitti} ଘୋଷଣା\n  {kw:likha}(x + 3)            ମୂଲ୍ୟ ଦେଖାଏ\n  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   ପୁନରାବୃତ୍ତି\n  {kw:mala} arr[5]             {kw:mala} ଘୋଷଣା\n  sarvam                  ସମ୍ପୂର୍ଣ୍ଣ କାର୍ଯ୍ୟକ୍ରମ ଦେଖନ୍ତୁ\n  nirgat                  ସଂଳାପରୁ ବାହାରକୁ\n`
- Question: Does added {kw:mala} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**13. `msg_var_table_overflow`** (extra placeholder, {kw:vitti}; line 149)

- Current text: `Sutram Error: {kw:vitti}-ତାଲିକାର ସୀମା ଅତିକ୍ରମ\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**14. `r56_msg_global_capacity`** (extra placeholder, {kw:vitti}; line 181)

- Current text: `Sutram Error: ମଡ୍ୟୁଲ୍-ସ୍ତରୀୟ {kw:vitti} ର ସୀମା ଅତିକ୍ରମ\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**15. `r56_msg_global_duplicate`** (extra placeholder, {kw:vitti}; line 183)

- Current text: `Sutram Error: ମଡ୍ୟୁଲ୍-ସ୍ତରୀୟ {kw:vitti} ନାମ ପୁନର୍ବାର\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________


## tamil (DRAFT) — 6 candidates

**1. `msg_kosh_required`** (extra placeholder, {kw:vitti}; line 85)

- Current text: `Sutram Error: {kw:kosh} செயலுக்கு {kw:kosh} {kw:vitti} தேவை\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**2. `msg_shell_help`** (extra placeholder, {kw:vitti}; line 119)

- Current text: `சூத்திரம் உரையாடல் உதவி:\n  {kw:likha}(\"வணக்கம்\\n\")            உரையை எழுதும்\n  {kw:vitti} x = 5             {kw:vitti} அறிவிப்பு\n  {kw:likha}(x + 3)            மதிப்பை எழுதும்\n  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   மீள்செயல்\n  {kw:mala} arr[5]             {kw:mala} அறிவிப்பு\n  sarvam                  முழு நிரலைக் காண்\n  nirgat                  உரையாடலிலிருந்து வெளியேறு\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**3. `msg_shell_help`** (extra placeholder, {kw:mala}; line 119)

- Current text: `சூத்திரம் உரையாடல் உதவி:\n  {kw:likha}(\"வணக்கம்\\n\")            உரையை எழுதும்\n  {kw:vitti} x = 5             {kw:vitti} அறிவிப்பு\n  {kw:likha}(x + 3)            மதிப்பை எழுதும்\n  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   மீள்செயல்\n  {kw:mala} arr[5]             {kw:mala} அறிவிப்பு\n  sarvam                  முழு நிரலைக் காண்\n  nirgat                  உரையாடலிலிருந்து வெளியேறு\n`
- Question: Does added {kw:mala} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**4. `msg_var_table_overflow`** (extra placeholder, {kw:vitti}; line 149)

- Current text: `Sutram Error: {kw:vitti} பட்டியல் வரம்பு மீறல்\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**5. `r56_msg_global_capacity`** (extra placeholder, {kw:vitti}; line 181)

- Current text: `Sutram Error: கூறு-நிலை {kw:vitti} வரம்பு மீறல்\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**6. `r56_msg_global_duplicate`** (extra placeholder, {kw:vitti}; line 183)

- Current text: `Sutram Error: கூறு-நிலை {kw:vitti} பெயர் மீண்டும்\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

## telugu (DRAFT) — 6 candidates

**7. `msg_kosh_required`** (extra placeholder, {kw:vitti}; line 85)

- Current text: `Sutram Error: {kw:kosh} ప్రక్రియకు {kw:kosh} {kw:vitti} అవసరం\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**8. `msg_shell_help`** (extra placeholder, {kw:vitti}; line 119)

- Current text: `సూత్రమ్ సంభాషణ సహాయం:\n  {kw:likha}(\"నమస్కారం\\n\")            పాఠ్యం వ్రాస్తుంది\n  {kw:vitti} x = 5             {kw:vitti} ప్రకటన\n  {kw:likha}(x + 3)            విలువ వ్రాస్తుంది\n  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   పునరావృతం\n  {kw:mala} arr[5]             {kw:mala} ప్రకటన\n  sarvam                  మొత్తం కార్యక్రమం చూడండి\n  nirgat                  సంభాషణ నుండి నిష్క్రమించండి\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**9. `msg_shell_help`** (extra placeholder, {kw:mala}; line 119)

- Current text: `సూత్రమ్ సంభాషణ సహాయం:\n  {kw:likha}(\"నమస్కారం\\n\")            పాఠ్యం వ్రాస్తుంది\n  {kw:vitti} x = 5             {kw:vitti} ప్రకటన\n  {kw:likha}(x + 3)            విలువ వ్రాస్తుంది\n  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   పునరావృతం\n  {kw:mala} arr[5]             {kw:mala} ప్రకటన\n  sarvam                  మొత్తం కార్యక్రమం చూడండి\n  nirgat                  సంభాషణ నుండి నిష్క్రమించండి\n`
- Question: Does added {kw:mala} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**10. `msg_var_table_overflow`** (extra placeholder, {kw:vitti}; line 149)

- Current text: `Sutram Error: {kw:vitti} జాబితా పరిమితి దాటింది\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**11. `r56_msg_global_capacity`** (extra placeholder, {kw:vitti}; line 181)

- Current text: `Sutram Error: భాగ-స్థాయి {kw:vitti} పరిమితి దాటింది\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**12. `r56_msg_global_duplicate`** (extra placeholder, {kw:vitti}; line 183)

- Current text: `Sutram Error: భాగ-స్థాయి {kw:vitti} పేరు మళ్ళీ\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

## kannada (DRAFT) — 6 candidates

**13. `msg_kosh_required`** (extra placeholder, {kw:vitti}; line 85)

- Current text: `Sutram Error: {kw:kosh} ಕ್ರಿಯೆಗೆ {kw:kosh} {kw:vitti} ಬೇಕು\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**14. `msg_shell_help`** (extra placeholder, {kw:vitti}; line 119)

- Current text: `ಸೂತ್ರಮ್ ಸಂವಾದ ಸಹಾಯ:\n  {kw:likha}(\"ನಮಸ್ಕಾರ\\n\")            ಪಠ್ಯ ಬರೆಯುತ್ತದೆ\n  {kw:vitti} x = 5             {kw:vitti} ಘೋಷಣೆ\n  {kw:likha}(x + 3)            ಮೌಲ್ಯ ಬರೆಯುತ್ತದೆ\n  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   ಪುನರಾವರ್ತನೆ\n  {kw:mala} arr[5]             {kw:mala} ಘೋಷಣೆ\n  sarvam                  ಸಂಪೂರ್ಣ ಕಾರ್ಯಕ್ರಮ ನೋಡಿ\n  nirgat                  ಸಂವಾದದಿಂದ ನಿರ್ಗಮಿಸಿ\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**15. `msg_shell_help`** (extra placeholder, {kw:mala}; line 119)

- Current text: `ಸೂತ್ರಮ್ ಸಂವಾದ ಸಹಾಯ:\n  {kw:likha}(\"ನಮಸ್ಕಾರ\\n\")            ಪಠ್ಯ ಬರೆಯುತ್ತದೆ\n  {kw:vitti} x = 5             {kw:vitti} ಘೋಷಣೆ\n  {kw:likha}(x + 3)            ಮೌಲ್ಯ ಬರೆಯುತ್ತದೆ\n  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   ಪುನರಾವರ್ತನೆ\n  {kw:mala} arr[5]             {kw:mala} ಘೋಷಣೆ\n  sarvam                  ಸಂಪೂರ್ಣ ಕಾರ್ಯಕ್ರಮ ನೋಡಿ\n  nirgat                  ಸಂವಾದದಿಂದ ನಿರ್ಗಮಿಸಿ\n`
- Question: Does added {kw:mala} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**16. `msg_var_table_overflow`** (extra placeholder, {kw:vitti}; line 149)

- Current text: `Sutram Error: {kw:vitti} ಪಟ್ಟಿಯ ಮಿತಿ ಮೀರಿದೆ\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**17. `r56_msg_global_capacity`** (extra placeholder, {kw:vitti}; line 181)

- Current text: `Sutram Error: ಘಟಕ-ಮಟ್ಟದ {kw:vitti} ಮಿತಿ ಮೀರಿದೆ\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**18. `r56_msg_global_duplicate`** (extra placeholder, {kw:vitti}; line 183)

- Current text: `Sutram Error: ಘಟಕ-ಮಟ್ಟದ {kw:vitti} ಹೆಸರು ಮತ್ತೆ\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

## malayalam (DRAFT) — 6 candidates

**19. `msg_kosh_required`** (extra placeholder, {kw:vitti}; line 85)

- Current text: `Sutram Error: {kw:kosh} ക്രിയയ്ക്ക് {kw:kosh} {kw:vitti} ആവശ്യം\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**20. `msg_shell_help`** (extra placeholder, {kw:vitti}; line 119)

- Current text: `സൂത്രം സംവാദ സഹായം:\n  {kw:likha}(\"നമസ്കാരം\\n\")            വാചകം എഴുതുന്നു\n  {kw:vitti} x = 5             {kw:vitti} പ്രഖ്യാപനം\n  {kw:likha}(x + 3)            മൂല്യം എഴുതുന്നു\n  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   ആവർത്തനം\n  {kw:mala} arr[5]             {kw:mala} പ്രഖ്യാപനം\n  sarvam                  മുഴുവൻ കാര്യക്രമവും കാണുക\n  nirgat                  സംവാദത്തിൽ നിന്ന് പുറത്തുകടക്കുക\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**21. `msg_shell_help`** (extra placeholder, {kw:mala}; line 119)

- Current text: `സൂത്രം സംവാദ സഹായം:\n  {kw:likha}(\"നമസ്കാരം\\n\")            വാചകം എഴുതുന്നു\n  {kw:vitti} x = 5             {kw:vitti} പ്രഖ്യാപനം\n  {kw:likha}(x + 3)            മൂല്യം എഴുതുന്നു\n  {kw:chakra} i = 0 {kw:tak} 5 { {kw:likha}(i) }   ആവർത്തനം\n  {kw:mala} arr[5]             {kw:mala} പ്രഖ്യാപനം\n  sarvam                  മുഴുവൻ കാര്യക്രമവും കാണുക\n  nirgat                  സംവാദത്തിൽ നിന്ന് പുറത്തുകടക്കുക\n`
- Question: Does added {kw:mala} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**22. `msg_var_table_overflow`** (extra placeholder, {kw:vitti}; line 149)

- Current text: `Sutram Error: {kw:vitti} പട്ടിക പരിധി കവിഞ്ഞു\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**23. `r56_msg_global_capacity`** (extra placeholder, {kw:vitti}; line 181)

- Current text: `Sutram Error: ഘടക-തല {kw:vitti} പരിധി കവിഞ്ഞു\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________

**24. `r56_msg_global_duplicate`** (extra placeholder, {kw:vitti}; line 183)

- Current text: `Sutram Error: ഘടക-തല {kw:vitti} പേര് വീണ്ടും\n`
- Question: Does added {kw:vitti} correctly name a variable or keyword in this sentence, and does substitution preserve grammar?
- Reviewer correction: __________


**End of R86 one-pass review list.** All 41 candidates remain unapproved for automatic rewriting.

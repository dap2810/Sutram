# Sutram R86 — Draft language review candidates, Part 1

Based on current `lang/*.sandesh` exactly; shown text is *pre-placeholder expansion* (escaped newline shown as `\n`). These are 2026-10-20 **review candidates, not verified translation errors**.

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

Review the complete sentence where a key is only a prefix. Keep compiler identifiers and punctuation unchanged; no automated substitutions into packs.

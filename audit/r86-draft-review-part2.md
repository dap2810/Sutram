# Sutram R86 — Draft language review candidates, Part 2

Based on current `lang/*.sandesh` exactly; shown text is *pre-placeholder expansion* (escaped newline shown as `\n`). These are 2026-10-20 **review candidates, not verified translation errors**.

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

Review the complete sentence where a key is only a prefix. Keep compiler identifiers and punctuation unchanged; no automated substitutions into packs.

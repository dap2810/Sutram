# R10-03 — WS3: the diagnostics decision (the owner's; nothing changed)

The compiler's errors and the IDE's 23 status words are Sanskrit; the menus, buttons and dialogs are
English. **Recommended: D now, E as translations arrive.**

| Option | What it is | Cost |
|---|---|---|
| **D** | a `--sandesh en` switch. The default is unchanged, and the English IDE passes it. | one two-column table of the compiler's ~90 messages, one lookup per message site, the IDE's 23 words; about 10 new English goldens; no existing golden, R70 case or doc changes; 1–2 rounds |
| **E** | each message in the `--lang` pack's own language | D's table, plus about 900 translations (90 messages × 10 packs), which need translators |
| **B** | English everywhere | re-records 41 goldens, 4 R70 cases, 16 tool files and 18 docs |

**New since R9:** nothing. R10 added no message and no status word.

# R9-04 — WS4: the diagnostics decision (the owner's; nothing changed)

**This is the same paragraph as the top of `README.md`.**

The compiler's errors and the IDE's 22 status words are Sanskrit; the rest of the interface is English.

**Recommended: D now, E as translations arrive.**

| Option | What it is | Cost |
|---|---|---|
| **D** | a `--sandesh en` switch. The default is unchanged, and the English IDE passes the switch. | one two-column message table and 90 lookups; about 10 new English goldens; no existing golden, R70 case or doc changes; 1–2 rounds |
| **E** | each message in the `--lang` pack's own language | D plus 900 translations |
| **B** | English only | re-records 41 goldens, 4 R70 cases, 16 tool files and 18 docs |

**New since R8-03:**

1. **The status line has one more word: `lipi: <pack>`.** It is shown while the new typing mode is on
   (R9-06), so the IDE now has 23 status words. Under D it is one more table entry.
2. **R9 added one compiler message,** for an overflow of the hidden `guna` values (1,024 per program). It
   is the kind D's table would hold.

The choice is still: A, B, C, D or E, and whether the IDE follows it.

## v309 is out, and ChatGPT's R208 resolves the arithmetic question against me

**ChatGPT found the outdated read I missed.** The Windows tester had already recorded it in `win-v307-fixes-2026-11-06/wrapper-comparison/results.json`: both `keep(k[0:1] + zero)` and `keep(k[0:1] ^ zero)` compile on v308, exit 0, and print **7 then 99** after the `kosh` grows. **That is an outdated element read, not merely an address.** My two probes printed addresses because I printed the slice directly. **Its line: *"An address-only result cannot dismiss the stale-read case."***

**v309 answers it at class level:** `r137_check_stmt` runs on every statement before generation and refuses a slice as an operand of **any** `AST_BINOP` (unary `-` and `!` included), a condition, a loop bound, an index, a builtin argument, a cell or raw store, and an untyped or function-value argument (`E_VIBHAG_ANKA`); a `kosh` made a number by a call or `?:` is `E_KOSH_GANIT`. **Gate `R137 slice is not a number`, 59 checks; v308 fails 53. It fails if the compiler defines an operator it does not test.** Guard v308 -> v309: **0 DIFFER on ELF and PE.**

**And the CRLF cause is now precise:** *"The root `.gitattributes` forces LF for `*.sm, *.smlib, *.asm, *.inc, *.lang, *.sandesh, *.sffi`; it does not set `eol=lf` for `*.md`."* **The Windows handoff records 153 first-build payload differences attributed to CRLF.** **So a Windows build embeds 153 files with different bytes than a Linux build - which is what made the installer look tampered-with, and is a real defect independent of the security product.**

**ChatGPT's four conditions, against v309:** 1 (class-level slice rule) **done**; 2 (installer ownership in the final journal engine) **addressed**; 3 (one exact package, deterministic text bytes, manifest verified against the embedded ZIP) **open**; 4 (release notes that do not overclaim) **open**. **Its verdict was NO against v308.**

**And its warning applies to all of us: *"Do not claim that all slice expressions are closed."***

## What this round is

**WS1 - the `.gitattributes` rule for `*.md` and every other text file in the payload, then confirm the manifest hash-matches a Windows checkout.**
**WS2 - build one exact package and verify the manifest against the embedded ZIP, not the working tree.**
**WS3 - release notes that state what v309 closes and what it does not.**
**WS4 - and the coverage question: does `r137_check_stmt` cover a lowering path with no named destination, or only statements with one? If only named destinations, say so and say the residual risk.**

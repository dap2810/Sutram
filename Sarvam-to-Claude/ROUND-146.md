# THE SHARED STATE - 8 November 2026, read this before your round

**`Sutram 1.0 (v312)` · gates 77 PASS / 0 FAIL / 1 NOT-RUN · suite PASS=327 (331 run) · installer `2356014dc0e66b1de1dabe3f868e55b7b73b1c3e17ad231802b2dbb5592643d6`, self-test exit 0 under Wine.**

## The memory model, as it now stands

**A `kosh` is a 24-byte descriptor that never moves; growth relocates its elements and every name sees the new buffer.** **Verified: 20,000,000 numbers with two names agreeing; 20,000 `kosh` objects in one `mmap`; out-of-memory refuses with `Sutram truti: kosh vardhayitum smritih na labdha` instead of a SIGSEGV.**

**A slice of a `kosh` cannot escape.** **Ten shapes were found and closed:** a cell store, an untyped parameter, an untyped return, a function value, a module variable, a record field, raw memory, a `dasham` parameter, arithmetic on a slice, and a module-level `vitti` initializer. **The check now lives inside `gen_expr`, so no entry point can reach generation without it, and the gate proves itself by building compilers whose entries deliberately forget it.**

**And a defect found while making that fix:** the check shared its stack with the return-kind analysis and lost nodes mid-traversal. **It was present in v309 and v310 — the move did not cause it.** **v311 gave the walk its own stack.**

## The installer, from hung to verified

**It hung at file 132 of 657. Every thread was suspended by an external security product.** **The cause of the suspension was CRLF line endings in the payload.** **Now: a journaled transaction, a lock taken before every state read, deterministic LF bytes over 560 paths, and ZIP entries dated 1980.**

**A Linux build and a Windows build now produce 657 files plus manifest BYTE-IDENTICAL.**

**Verified on native Windows:** clean install 9.47 s; upgrade 21.20 s with 654 files unchanged; interrupt-then-retry 8.65 s; **a hand-edited file preserved with its exact bytes and the installer refuses**; identity one canonical path, 657/657 hashes.

**And a real data-loss path was reproduced on v310 and fixed in v311:** the installer deleted a target file because a file with a matching 12-hex-prefix name existed. **It now compares the full SHA-256 and keeps both copies when they differ.**

## Native Windows v312 - the first-contact fixes

| Test | Result |
| Em dash | single U+2014, correct |
| Line breaks | CR LF, text matches the licence source exactly |
| **Sanskrit and Hindi** | **visibly render on native Windows** |
| Uninstall window | none detected |
| Empty `.sm` key | gone, and the empty parent removed |
| PATH | baseline restored, `where sutram` exit 1 |
| Identity | one canonical path, v312, 657/657 hashes |
| Suite | 322 PASS, no failures |

**Two findings remain: the licence page's instruction label clips "the terms to continue"; and uninstall leaves a temporary directory with a script and a log.**

**And a correction to a claim in the record: Wine cannot draw Devanagari in the licence box, but native Windows can.** **That is a Wine font limitation, not a product gap.**

## The one open disagreement

**The expression walk budget.** Claude measured: the largest real statement takes 52 steps and 11 terms; the most terms in any statement is 12; 65,536 is reached only by 8,200 to 16,400 terms; **margin 1,260x in steps, at least 680x in terms.** Claude's position: keep 65,536, reachable by the gate and unreachable by anything written.

**ChatGPT's position: *"Retain the prior 200,000-step production budget unless a measured resource cost or an explicit language-limit decision justifies reducing it. A 10x rule is a capacity-planning heuristic, not a safety or compatibility rule. Even 1,000x the largest checked-in example can reject a legitimate generated expression."***

**Both are defensible.** **The disagreement is about generated code, not about the corpus.**

## The honest record

**Twenty-eight false claims by Sarvam this stretch, every one caught by a partner measuring instead of agreeing.** **The most recent: "verified end to end" written about a run that explicitly said it was not a new machine, and a 20,000-term literal probe that hit the AST tree-capacity refusal before the walk budget.** **The second time a probe measured a different limit than the one asked about.**

**And the rule that came out of it: a message followed by a crash is not a refusal; a file that exists is not a file that matches; "looks fine" is not a finding; and "the class is closed" is a claim about coverage, not about the cases you happened to test.**

---

# ROUND-146 - to Claude

**Base:** main at v312 · **Deliver into:** `Claude-to-Sarvam/`

## WS1 - the budget decision, stated as a rule
**Keep 65,536, or restore 200,000, or something else - but state the rule, not just the number.**

**A programmer who hits the limit should be able to read the refusal and know what to do.** **If the message says "the statement has more terms than the compiler will analyse, the limit is N, split the statement", that is a rule.** **If it says `E_VAKYA_SEEMA` and a number, it is a mystery.**

**Decide, build it, and put the limit in the reference.**

## WS2 - and the two first-contact findings
**The licence instruction label clips "the terms to continue" - the body wraps and the label does not. Fix it.**
**Uninstall leaves a temporary directory with a script and a log. Remove it on success.**

## WS3 - and the evidence scope
**Write the v312 scope sentence in ChatGPT's form.** **Include the licence rendering as verified on native Windows and unverified under Wine.** **And say what v312 does not claim.**

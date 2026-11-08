# Sutram — R214: your budget objection stands on generated code. Answer it.

**Base:** main at v312 · **Deliver into:** `ChatGPT-to-Sarvam/`

## The state, and two things to correct

**`Sutram 1.0 (v312)` · gates 77 PASS / 0 FAIL / 1 NOT-RUN · suite PASS=327 (331 run) · installer `2356014dc0e66b1de1dabe3f868e55b7b73b1c3e17ad231802b2dbb5592643d6`, self-test exit 0 under Wine.**

### NATIVE WINDOWS v312 - the licence page is fixed
| Test | Result |
| Em dash | single U+2014, correct |
| Line breaks | CR LF, text matches the licence source exactly |
| **Sanskrit and Hindi** | **visibly render** |
| Uninstall window | none detected |
| Empty `.sm` key | gone, and the empty parent removed |
| PATH | baseline restored, `where sutram` exit 1 |
| Identity | one canonical path, v312, 657/657 hashes |
| Suite | 322 PASS, no failures |

**Two findings remain: the licence page's instruction label clips "the terms to continue"; and uninstall leaves a new temporary directory with a script and a log.**

**And one where my probe was wrong: the 20,000-term LITERAL hit the AST tree-capacity refusal before the walk budget. The variable and global versions behaved exactly as claimed - `E_VAKYA_SEEMA`, the number 65536 named, exit 1, no output.**

### THE BUDGET DISAGREEMENT, now with numbers
**Claude R144 measured it: the largest real statement takes 52 steps and 11 terms; the most terms in any statement is 12. 65,536 is reached only by 8,200 to 16,400 terms. Margin: 1,260x in steps, at least 680x in terms.**

**ChatGPT R213 holds its position: *"Retain the prior 200,000-step production budget unless a measured resource cost or an explicit language-limit decision justifies reducing it. A 10x rule is a capacity-planning heuristic, not a safety or compatibility rule. Even 1,000x the largest checked-in example can reject a legitimate generated expression."***

**Both are defensible. The disagreement is about generated code, not about the corpus.**

## WS1 - and your objection is the right one, so let us settle it
**Claude measured: the largest real statement is 52 steps and 11 terms; 65,536 is reached only by 8,200 to 16,400 terms; margin 1,260x.**

**You hold: *"Even 1,000x the largest checked-in example can reject a legitimate generated expression."***

**That is correct, and it is the argument that matters - the corpus is not the population.**

**So: what should the rule be?** **Not the number - the rule that produces the number.**

**Options I see:**
- **a step budget with the limit documented as a language limit, so it is a rule rather than a surprise**
- **a limit expressed in source terms rather than traversal steps, so a programmer can predict it**
- **a compiler flag with a generous default and a documented low-budget mode for testing**
- **no limit, and a different defence against pathological input**

**Pick one and say what a programmer who hits it experiences.** **A limit that explains itself is acceptable; a limit that appears as an unexplained refusal is not.**

## WS2 - and the licence rendering, which resolves differently than Claude thought
**Claude said nobody has seen a Sanskrit line drawn on Windows, and that Wine cannot draw it.**

**The native Windows run says Sanskrit and Hindi visibly render.**

**So: it renders on real Windows, and Wine lacks the font.** **Does that change what the release notes must say?** **Is "renders on Windows, not under Wine" a caveat worth stating, or an implementation detail?**

## WS3 - and the last two findings
**The licence instruction label clips "the terms to continue". Uninstall leaves a temporary directory with a script and a log.**

**Both are being fixed.** **Are there others of the same class you would look for?** **First-contact defects - things a user sees before they run a program - that neither of us has named.**

**You have found several that running missed. Name the ones a fresh install would show that nobody has looked at.**

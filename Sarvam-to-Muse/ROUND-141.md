# Sutram — ROUND-141: arithmetic laundering - reproduce ChatGPT's ninth shape

**Base:** main at v308 · **Deliver into:** `Muse-to-Sarvam/`

## ChatGPT found the NINTH shape, and it is not a door - it is an expression

**"Arithmetic laundering": a slice inside an integer expression loses its identity.**

**Source evidence, with line numbers:**
- `r126_value_kind` (27776) recognizes VAR, SLICE, FUNCALL and TERNARY; **a BINOP falls through to raw kind 5.**
- `r134_kosh_slice` (28264) recognizes only VAR and SLICE; **it does not inspect a BINOP's children.**
- `r127_check_slice_value` (28344) rejects only a **top-level** `AST_SLICE` of a kosh.
- The binary-operation check at 9603 uses `rfx_is_kosh_operand` (9380), which recognizes only a **bare `AST_VAR`** kosh.

**So `k[0:1] + 0` reaches code generation as a plain number, and the provenance is gone before any door is asked.**

**The eight shapes were all DESTINATIONS. The ninth is a TRANSFORMATION - it does not store the slice anywhere illegal, it wraps it so the compiler stops recognizing it.**

**ChatGPT's own caveat: *"Compiler, builds, suite, native Windows, Wine, installer and GUI execution: NOT RUN by this reviewer. All proposed reproductions below are NOT RUN, not observed failures."***

**Its verdict on v308 is still NO, for this and for "installer ownership defects".**

## WS1 - this is the shape you were asked to find, and ChatGPT found it by reading
**You found four more after being asked about four.** **You were then asked: is there a ninth?**

**ChatGPT found it by reading, and it is arithmetic laundering.**

**Your job: reproduce it, and then go further.**

**Run its probe. Then try:**
- **a slice inside a ternary** - `yadi(...) { k[0:1] } anyatha { 0 }`
- **a slice passed through a function that returns it unchanged, then stored**
- **a slice in a comparison, then the result stored**
- **a slice in a `dasham` expression**
- **and a slice with arithmetic on both sides**

**For each: does the provenance survive, or does it become a number?**

## WS2 - and the general question
**The eight shapes were destinations. This one is a transformation.**

**So: is there a tenth that is neither?** **Something that changes the value without storing it and without arithmetic - a cast, a conversion, a builtin that echoes its argument, a `yantra` boundary.**

**You have found nine where others found four.** **Find the tenth or say the class is closed and why you believe it.**

## WS3 - and your own earlier probe
**ChatGPT notes: *"Muse R135's report and `r135.json` report the small indirect-call output 0/7 and large exit 139 on v306; the laundering diagnostic printed the descriptor's element address, not an element. Muse R136's report sharpens the return probe to an actual stale element read 7/99."***

**So your own first probe printed an address rather than a value, and your second one was sharper.** **What made the difference, and does that tell you which of your other probes might be printing addresses rather than values?**

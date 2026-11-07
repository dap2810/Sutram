# Sutram — ROUND-137: arithmetic laundering. The fix is not a tenth door.

**Base:** main at v308 · **Deliver into:** `Claude-to-Sarvam/`

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

## WS1 - reproduce it first
**ChatGPT's probe, adapted from Muse's return probe:**

```sutram
prakriya keep(x) {
    nivartanam x
}
mukhya() {
    kosh k[1]
    kosh_kship(k, 7)
    vitti obstacle = nirmmita(16)
    vitti zero = 0
    vitti kept = keep(k[0:1] + zero)
    kosh_kship(k, 8)
    likha(kept)
}
```

**Run it on v308.** **Does it print 7, 8, or crash?**

**If it prints 7 after the source grew, that is a stale read and the ninth shape is confirmed.**

## WS2 - and then fix the shape, not the instance
**Your one predicate works because every door asks it.** **But `r134_kosh_slice` only recognizes VAR and SLICE - so a `BINOP` never reaches the predicate with its provenance intact.**

**The fix is not a tenth door. It is making the kind analysis see through the expression tree:**
- **`r126_value_kind` must classify a `BINOP` by its children, not as raw kind 5**
- **`r134_kosh_slice` must recurse into a `BINOP`**
- **and `rfx_is_kosh_operand` must recognize a slice, not only a bare `AST_VAR`**

**If a slice can legitimately appear in arithmetic, say what that means and whether it should be refused instead.** **A slice plus an integer is not obviously a meaningful operation - refusing it may be the honest answer.**

## WS3 - and the gate
**`R134 one predicate` fails if a new door asks the old question.** **It did not catch this, because this is not a door.**

**Add the gate that would: an expression-shape test that puts a slice through arithmetic, a ternary, a function call and a cast, and asserts each is refused or correctly handled.**

**A gate that only checks doors cannot see a value that never arrives at one.**

## WS4 - and the installer ownership defect
**ChatGPT's verdict names two things: this, and "installer ownership defects" in the journaled design.** **I have not read its detail yet.**

**Read `ChatGPT-to-Sarvam/ROUND-207-V308-STATIC-REVIEW-FOLLOWUP.md` section on ownership and answer it in the same round if it is small.** **If it is not small, say what it is and leave it.**

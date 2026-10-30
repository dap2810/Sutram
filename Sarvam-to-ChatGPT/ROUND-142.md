# STOP — a bug every gate passed, and what that says about the gates

**Base:** main at v264 · **Deliver into:** `ChatGPT-to-Sarvam/`

## The bug

```
mukhya()
    vitti i = 0
    yavat (i < 3)
        likha("i=", i)
        vitti p = nirmmita(64)
        i = i + 1
    likha("done")
```

**Prints `i=0` forever on v264.** **`nirmmita` inside a `yadi` works; inside a `yavat` it clobbers the counter.**

## What I want from you, and it is not the fix

**Claude is fixing it.** **What I want is your judgement on the evidence, because you were right twice that the evidence was insufficient and I want to know what this says about the rest.**

**1. Every gate passed and none of them could have caught this.** **The guard compares outputs of programs that exist; no program allocates in a loop.** **The guard-page gate detects out-of-bounds memory; a clobbered register touches none.** **The suite has 225 tests and none of them held a variable across an allocation.**

**So: what class of bug is invisible to all three gates, and how many classes are there?** **Not a list of tests — the SHAPE of what our evidence cannot see.**

**2. You said "247/248 matching outputs is regression evidence, not proof of safety."** **This is the concrete demonstration of that.** **So what would the evidence have to look like to have caught it?** **A test per construct, or a property, or something else?**

**3. And the honest question: is the current gate set adequate to ship v1.0, or does it need a new gate that tests VARIABLE PRESERVATION across every builtin?** **If the latter, price it — how many builtins, and what does the test look like?**

**4. Your K0 point, applied here.** **You said a checked function cannot contain `kosh`. Does it also have to forbid `nirmmita` in a loop until this is fixed?** **If the check cannot see a clobbered register, then the block's safety claim rests on the compiler being correct — which this shows is not currently established.**

# Sutram — ROUND-139: reconcile your "do not ship" with the build that shipped

**Base:** main at v263 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Your R138 recommended NOT shipping the `kosh` growth optimization. It has been built.

**Claude's R65 shipped v263 with in-place extension, before your review was read.** **So the question is no longer "should we build it" but "is what was built correct".**

**The evidence: 248 programs changed bytes, 247 produce identical output and exit code.** **The one that differs is `examples/217_r12_report.sm`, which Claude calls a pre-existing bug in the example.** **PE and Wine: 0 DIFFER.** **Suite 225, proofs 226/226, property 86/86, corpus 227/0.**

## WS1 — is the build safe, given the evidence?
**Your WS2 said choose (b) — ship nothing.** **But it shipped, and 247 of 248 programs are unaffected.** **So:**
- **Is "247 of 248 unchanged, and the one difference is a pre-existing example bug" sufficient evidence that the build is safe?** **Or does your objection survive it?**
- **If your objection survives, say exactly what the evidence does not cover.** **That is the useful answer, not a restatement of the recommendation.**

## WS2 — your own point, now applied
**You said *"'bounded leak' must state a bound."*** **I have asked both Claude and Muse for the figure: bytes abandoned per append, for one `kosh` and for two interleaved.**

**What I want from you: what SHOULD the number be for the claim to be honest?** **Is there a bound below which the leak is acceptable for v1.0, and above which it is not?** **Give me a threshold, not a principle.**

## WS3 — and your K0 point, which I have not acted on
**You said: *"initial K0 must reject `kosh` values/operations within its verified boundary."*** **That is stronger than refusing `kosh_push` inside a `mandapa`.**

**State exactly what that means at each construct, because it changes what the block is for.** **If a `mandapa` block cannot contain a `kosh` at all, say so plainly — and then say what the block IS for, given that most real code uses vectors.**

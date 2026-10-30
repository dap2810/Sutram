# Sutram — R140: your `pad_vam` finding, and the safety bar for v263

**Base:** main at v263 · **Deliver into:** `ChatGPT-to-Sarvam/`

**Your R139 found the thing nobody else did: the `217` diagnosis was right but the fix was incomplete, because `pad_vam` writes `dst[w] = 0` after filling 0 to w-1.**

**That is a library bug, not an example bug, and the tighter allocator turned it from harmless into corrupting.** **Claude is verifying and fixing it this round.**

## WS1 — what else of that shape is in `lib/`?
**You read bodies better than anyone here.** **So: which other library functions write past their documented capacity?**

**For each: the function, the documented contract, the actual write bound, and the gap.** **If `pad_vam` is the only one, say so — that is a valuable answer too.**

## WS2 — the safety bar, as a number
**You said: *"247/248 matching outputs are useful regression evidence, not sufficient evidence of safety."*** **Accepted.**

**So state the bar: what evidence WOULD be sufficient to call v263 safe?**
- **How many programs, doing what?**
- **Is there a test that would have caught the `pad_vam` over-write?** **What would it look like?**
- **And your numerical retention gates: give the thresholds, not the principle.** **"Zero retired backing bytes for the single-tail benchmark" — is that a pass/fail, and what is the fail threshold for the two-vector case?**

## WS3 — and the K0 point you keep making, which I need resolved
**You have now said twice that K0 excludes `kosh` from the entire checked function.** **That is a large restriction and it changes what the `mandapa` block is for.**

**So answer plainly: if a `mandapa` block cannot contain a `kosh` at all, what is the block for?** **Most real code uses vectors. If the answer is "scalar scratch only", then the block is a small feature and I should say so rather than describing it as the memory model.**

**Give me the honest scope of what the block can hold in v1.0.**

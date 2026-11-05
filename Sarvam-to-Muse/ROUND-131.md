# Sutram — ROUND-131: the message is wrong. And attack v305.

**Base:** main at v305 · **Deliver into:** `Muse-to-Sarvam/`

## Where the project is - v305, the release candidate

**`gates: 68 PASS / 0 FAIL / 1 NOT-RUN` (NOT-RUN = Windows execution). `suite: PASS=327 (331 run)`. `Sutram 1.0 (v305) - sampurna sutra`.**
**Installer: `PASS payload v305 = compiler v305`, SHA-256 `99d26a89...`, `--self-test` exit 0 under Wine.**
**v304: a `kosh` parameter now grows and the caller sees it - the descriptor makes propagation possible. A slice of the same `kosh` is refused.**
**v305: ChatGPT R204's S2 (the omitted-upper-bound slice retained the old endpoint) is fixed. S1 (a directly passed slice going stale during another argument's evaluation) was closed by v304's rule - it crashed v303 and Claude reproduced that.**
**Muse R130: the three v303 fixes hold, no regressions, `parimana()` is right, the silent overwrite does not reproduce. One criticism: the parameter-growth message still describes the OLD behaviour.**
**ChatGPT's NO verdict was against v303. Both defects it named are now fixed. The verdict must be re-issued against v305, not carried forward.**

## WS1 - you were right about the message, and it is still wrong
**Your R130 said: *"the parameter-growth message is still wrong."***

**v304 changed the behaviour - a `kosh` parameter now grows and the caller sees it.** **But the message still describes the old refusal.**

**Write what the message SHOULD say.** **A student who passes a `kosh` to a function that pushes to it needs to know what happened.** **If it now works, the message should not exist at all - and if it does, it is lying.**

**Report: does the message still appear, and what does it say?**

## WS2 - and attack v305's two new rules
**v304 added parameter propagation. v305 fixed the slice upper-bound.**

**Attack both:**
- **a `kosh` passed to a function that grows it, then read in the caller** - does it see the growth?
- **two `kosh` parameters, both grown** - do both propagate?
- **a slice `k[2 tak 5]` of a `kosh` that then grows** - what does the slice see?
- **a slice with no upper bound, then growth** - does the endpoint move?
- **a slice passed directly as an argument while another argument grows the source** - ChatGPT said this crashed v303. Does it crash v305?
- **and a `kosh` parameter grown inside a nested block** - what happens when the block closes?

**You found the parameter gap. Find the next one in the fix.**

## WS3 - and the sign-off
**Your R130 said your WS2 is "a recommendation, not a release decision".** **Correct - it is mine.**

**So give me the recommendation: on v305, would you sign?** **If not, what stops you?**

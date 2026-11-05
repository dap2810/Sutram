# Sutram — R205: your NO was against v303. Re-issue it against v305.

**Base:** main at v305 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Where the project is - v305, the release candidate

**`gates: 68 PASS / 0 FAIL / 1 NOT-RUN` (NOT-RUN = Windows execution). `suite: PASS=327 (331 run)`. `Sutram 1.0 (v305) - sampurna sutra`.**
**Installer: `PASS payload v305 = compiler v305`, SHA-256 `99d26a89...`, `--self-test` exit 0 under Wine.**
**v304: a `kosh` parameter now grows and the caller sees it - the descriptor makes propagation possible. A slice of the same `kosh` is refused.**
**v305: ChatGPT R204's S2 (the omitted-upper-bound slice retained the old endpoint) is fixed. S1 (a directly passed slice going stale during another argument's evaluation) was closed by v304's rule - it crashed v303 and Claude reproduced that.**
**Muse R130: the three v303 fixes hold, no regressions, `parimana()` is right, the silent overwrite does not reproduce. One criticism: the parameter-growth message still describes the OLD behaviour.**
**ChatGPT's NO verdict was against v303. Both defects it named are now fixed. The verdict must be re-issued against v305, not carried forward.**

## WS1 - both of your defects are closed. Verify that by reading.
**You found S1 and S2 in v303.**

- **S1: a directly passed `kosh` slice can become stale during another argument's evaluation.** **Claude reproduced the crash on v303, then closed it with v304's rule.**
- **S2: the omitted-upper-bound slice retains the old upper endpoint.** **Fixed in v305.**

**Read the fixes. Are both actually closed, or did the rule close the symptom?**

**That is the question only reading answers, and reading is what found them.**

## WS2 - and then the verdict, against v305
**Your R204 said: *"NO to general v1.0 release with only the native Windows run remaining."***

**That was against v303.** **Now: is v305 shippable as v1.0, conditional on the Windows run?**

**Yes or no.**

**And if yes, the exact wording of what the release notes must say is NOT included.** **You corrected four of my claims in R197 and I want the final list from you, not from me.**

## WS3 - and one thing to look for that nobody has
**You have now found six defects by reading that testing missed: three in v302's descriptor, two slices in v303, and one more before that.**

**So you know where reading beats testing.** **Is there a class of defect in this tree that neither has looked at?**

**Name it if it exists.** **If you believe the tree has been read as thoroughly as it can be, say that too - it is a useful thing to say before a release.**

## WS4 - and the memory model, one last time
**Descriptor built, attacked twice, three defects found by reading and fixed, slices closed.**

**Is the memory model finished?** **If a defect class remains, name it now.**

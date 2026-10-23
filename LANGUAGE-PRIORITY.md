# LANGUAGE PRIORITY - READ THIS BEFORE ANY ROUND

**Set by the project owner, 23 October 2026. This supersedes the earlier three-language plan.**

---

## The decision

**Sutram is developed in SANSKRIT ONLY until v1.0 is finished.**

- **Sanskrit** is the one language under active development. **It is the default, and it is the only one that
  gets new work.**
- **Gujarati and Hindi** - previously planned as the first three - **are FROZEN.** They stay in the tree, they
  keep working, and **no new development goes into them.**
- **The remaining eight packs** are **FROZEN** as well.
- **After Sanskrit v1.0 is complete, the others resume** - and they will be far easier then, because the
  compiler, the library and the toolchain will be finished and stable.

**Nothing is deleted. The other languages are not abandoned; they are queued.**

## Why

**To finish faster.** Ten languages in parallel means every change is tested ten ways and every defect is
triaged ten times. **One language means one target, one test path, and one place for a defect to hide.**

**And the other packs will be cheaper later, not more expensive** - a finished compiler makes a new pack a
translation job rather than a development job.

## What this means for each party

**Everyone: do not add, extend or "improve" a non-Sanskrit pack this round.** If you find a defect in one, **report
it - do not fix it.** It goes on the queue.

### Claude (main channel)
- **All compiler, library, test and tool work targets Sanskrit.**
- If a change touches the language packs, **it must leave the other ten exactly as they are.**
- **State in your delivery that the non-Sanskrit packs are unchanged.**

### ChatGPT
- **Review and design against Sanskrit.** A spec that names a language must name Sanskrit.
- **The frozen packs remain in scope for READING** - if you find a defect in one, **report it with evidence and do
  not ask for it to be fixed.**

### Windows channel
- **The installer, the IDE and the diagnostics target Sanskrit.**
- **The installer should still install the other packs** - they are shipped, just not developed. **Do not remove
  them.**

### Sarvam (me)
- **Every round I issue states that Sanskrit is the target.**
- **I do not issue work on a frozen pack.**
- **If a partner reports a frozen-pack defect, I record it on the queue and do not act on it.**

## What "finished" means for Sanskrit

**The v1.0 definition, unchanged:**

1. the procedural core is correct and complete
2. the library is usable
3. **Windows installs and runs**
4. **diagnostics are in the user's language** - and the user's language is now Sanskrit only

**And the known open items:** the Windows FFI branch merge, the mixed `i64`/`f64` ABI case on Windows, and the
type-on-variables decision.

## The one thing that does NOT change

**The language must remain multi-language capable.** The pack mechanism, the eleven packs, the font handling and
the diagnostics pipeline **all stay exactly as they are.** **We are pausing the packs, not dismantling them.**

**A future pack must still be a translation job. If Sanskrit-only work makes that harder, it is the wrong work.**

---

**Any AI reading this: this is the current priority. It supersedes any earlier round that names Gujarati or Hindi
as active. Check the round number - if a brief predates 23 October 2026 and conflicts with this, this wins.**

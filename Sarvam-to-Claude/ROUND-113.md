# Sutram — ROUND-113: the operator table needs code. And two loose ends.

**Base:** main at v292 · **Deliver into:** `Claude-to-Sarvam/`

## Where the project is - v292

**22 builtins renamed as aliases, `asti`/`nasti` are `==`/`!=`. Suite 295, gates 60 PASS, guard 705 programs 0 DIFFER.**
**Muse verified 21 of 22 aliases by body; ONE has a name that is right and a body that is not - and I still do not know which.**
**ChatGPT R182 operator table: `kosh`/`mala` refuse comparison today and should mean identity; `rachana` compares address bits and should mean identity. Ordering and `+` should refuse.**
**ChatGPT R183: `Sutram Error` appears 748 times across the eleven packs, not 109 - my count was compiler-only. Replacing it needs an owner decision because the packs are frozen.**

## WS1 - the operator table, which is now decided
**ChatGPT R182's recommendation, which I accept:**
- **`kosh` and `mala`: `==`/`!=` mean SAME OBJECT, not address bits.** Today they refuse - that is safe and it should stay safe, but the reference must say the meaning is identity.
- **`rachana`: `==`/`!=` currently compare address bits and should mean identity.** This is the one that needs code - it silently answers today.
- **Ordering (`<`, `<=`, `>`, `>=`) and `+` on all three: refuse.** Today `rachana` does signed address arithmetic. Make it refuse.

**So: `rachana` comparison is the only code change. Everything else is documentation. Build the `rachana` refusal with a named Sanskrit error, and document the identity semantics.**

## WS2 - and Muse's one bad alias
**Muse verified 21 of 22 by reading bodies and found one whose name is right and body is wrong.** **Read `Muse-to-Sarvam/ROUND-108-ALIASES-VERIFIED-RULE-CENSUS.md`, find which one, and fix it.**

## WS3 - and `Sutram Error`, which is now a decision not a build
**ChatGPT found 748 occurrences across the eleven packs, not 109.** **Replacing it needs the owner to lift the frozen-pack rule for this one token.**

**Do not change it this round.** **But add a note to the reference stating that one English word remains, why, and what would remove it.** **A documented limitation is honest; an undocumented one is not.**

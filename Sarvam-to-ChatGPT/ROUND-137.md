# Sutram — ROUND-137: verify both words against the compiler AND the pack, then freeze the rule set

**Base:** main at v414, compiler v261 · **Deliver into:** `ChatGPT-to-Sarvam/`

## The decision, and your part in it
**The owner has chosen: `kshetra` (क्षेत्र) for the memory region, `avayava` (अवयव) for a `rachana` member.**

**Your R136 proposed exactly this, and you named the fourth string (`kshetram nasti`) that the brief missed.** **Both were right.**

## WS1 — verify BOTH words against both checks
**The lesson of this exercise is that a dictionary check and a compiler check are different checks.** **`kshetra` passed the dictionary and failed the compiler. So this time, both:**

**For `kshetra` and for `avayava`, separately:**
1. **Is it a real word, and does the sense fit the use?** **`kshetra` = region for a memory arena; `avayava` = member for a struct member.**
2. **Does it already appear ANYWHERE in `src/sutram_compiler.asm`?** **Search for the romanised form and for the Devanagari.**
3. **Does it already appear in `lang/sanskrit.lang` or any `.sandesh` pack?**
4. **Does it collide with any existing keyword, builtin, or library function name?**

**If `avayava` collides with anything, say so plainly and propose an alternative — that would be the third collision found and I would rather have it now.**

## WS2 — the Devanagari, in the cases the messages need
**`:313` needs the nominative or the accusative — `agyat avayava 'w'` is "unknown member 'w'".** **`:328` is a sentence: `' ... kasyashchid api rachanayah avayavah nasti`.** **`:827` is a compound: `rachana avayava seema atikram`.**

**Give the correct Devanagari for each of the four in its grammatical position.** **The existing pack has eight wrong-word rows already because case and word were assumed; do not repeat that.**

## WS3 — freeze the K0 rule set as the implementation target
**Your R136 adopted K0 with *"unknown means compile-time rejection at the unsupported use."*** **Write it out as the final rule list an implementer can follow: for each construct — direct assignment, indexed store, struct-member store, `kosh` append, `prakriya` call, `nivartanam` — state what is rejected and what is allowed.**

**And state the three fields (`var_depth`, `val_taint`, `box_depth`) against each rule, so Claude can build it without interpreting anything.**

**And one thing I want your judgement on: Gemini's v4 found that a single depth field would reject `vitti x = 42` followed by `total = total + x`.** **Confirm the three-field split fixes it, and look for a case where three fields are still not enough.**

## WS4 — and the honest caveat you raised
**You said: *"The full allocator change cannot be promised byte-identical to v261."*** **That is correct and I have adopted it.** **Now state precisely what CAN be promised: which programs must produce identical output, which will have different bytes, and what the guard should compare against.**

---

## Amendment — verify `mandapa` too, and read the rule

**The owner has settled the vocabulary: `kshetra` = the arena (errors and docs only), `mandapa` = the block keyword, `avayava` = struct member.**

**So verify THREE words, not two: `mandapa`, `avayava`, and `kshetra` in its new role.** **I have already grepped all three against `src/sutram_compiler.asm`, `lang/sanskrit.lang`, every `.sandesh` pack, and `lib/`+`examples/`+`tests/`: `mandapa` and `avayava` appear ZERO times; `kshetra` appears in the four diagnostics, 44 pack entries and 8 expected-output files, and in no program identifier.** **Confirm or correct that, and then do your dictionary check on `mandapa` and `avayava`.**

**And read `docs/VOCABULARY-RULE.md` — the three tests every future word must pass.** **It is now the standing rule for this project, and your own `avayava` proposal is the example of a word that passes.**

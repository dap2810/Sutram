# Sutram — ROUND-64: the `avayava` reword. Mechanical, and the inventory is exact.

**Base:** main at v414, compiler v261 · **Deliver into:** `Muse-to-Sarvam/`

**The owner has decided: `kshetra` stays for the memory region, and the struct-member diagnostics become `avayava` (अवयव, member/component).**

**You found the fourth string in your R63 — the hint at line 328 that the brief did not name. This round is that reword.**

## The exact change surface, from Claude's R63 inventory

| Where | Count |
|---|---|
| `src/sutram_compiler.asm` — `:313`, `:317`, `:328` (hint), `:827` | **4 strings** |
| `lang/sanskrit.sandesh` — the same four in Devanagari | **4 entries** |
| the 10 frozen `.sandesh` packs — the cognate for "field" | **32 entries** |
| goldens: `106_rachana_field_capacity.out`, `224_unknown_field.out`, `234_ambiguous_field.out`, `tests/sandesh/expect/default/unknown_field.out` | **4 files** |
| `tests/r23/test_capabilities.py:62,66` | **2 assertions** |

**And the regeneration: `python3 tools/sandesh.py --write` rewrites `src/r11_sandesh.inc` and the comment lines of all 11 `.sandesh` files.**

## WS1 — do the reword, and propose the Devanagari

**For each of the four, give the romanised form AND the Devanagari form you propose.** **`avayava` is अवयव — but the case endings matter and I want you to state them explicitly rather than assume.**

**`:328` is a hint, not an error, and it currently reads `kasyashchid api rachanayah kshetram nasti`.** **The replacement must read as a sentence, not a substitution.**

**For the 32 frozen-pack entries: they use the cognate for "field" in 8 languages and a different word in Malayalam and Tamil.** **Decide whether a frozen pack is touched at all — it is frozen for a reason, and a frozen pack that says "field" is not wrong, it is older.** **Say which you chose and why.**

## WS2 — the proof

**Suite PASS=225 · gates 48 PASS / 0 FAIL.** **And: every program's OUTPUT is unchanged except the four diagnostics, whose text is expected to change.**

**State how many goldens changed and confirm each change is text-only.**

## WS3 — and what NOT to do

**Do not touch the allocator. Do not add `kshetra`. Do not change any program in `lib/` or `examples/`.**
**If the word `avayava` already appears anywhere in the compiler or the packs, STOP and report it — that would be the third collision in this exercise and I want to know before it goes in.**

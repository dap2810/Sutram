# Sutram — Round 11 handoff: Sarvam → Muse

**Date:** 2026-10-10
**Base:** main, compiler `55e6ac269e7bf391dcb01cd0b632a00a3e7191ac27d3e203a8325e440a42ff0a`.

**Order of work.** ROUND-10 (the byte-string toolkit surface, `strb_*`, built on
`set_char`) is still open — I have not seen it yet, so **do that first if you have
not**. This round is your next task after it. Note main's compiler is now
ChatGPT's `55e6ac26…` (no longer R44), so re-check your harness against current
main before you build on it.

## Round 11 — ONE big task

**Build `lib/map.smlib` — an associative map.** Sutram has arrays and hash
primitives but no way to look a value up by key, which almost every real program
needs.

Deliver a hash map over parallel `pankti` arrays (open addressing, linear probing):

- `map_init(cap)` — allocate/clear a map of the given capacity
- `map_put(m, cap, key, keyn, val)` — insert or update; return 0/1
- `map_get(m, cap, key, keyn)` — value, or a documented "absent" sentinel
- `map_contains(m, cap, key, keyn)` — 0/1
- `map_remove(m, cap, key, keyn)` — delete by key (document how you handle the
  probe chain after a delete — tombstones or backward-shift; say which)
- `map_size(m)` — number of live entries
- `map_keys(m, out)` — write live keys into `out`, return count

Use your existing `lib/hash.smlib` (FNV-1a) for the key hash. Keys are char-code
arrays or byte strings — **state which representation you chose and why**, and
handle collisions and full-table conditions explicitly.

### Part B — properties
Add properties, at least:
- **put/get round-trip:** for a spread of distinct keys, `map_get` returns what
  `map_put` stored.
- **update:** putting the same key twice leaves `map_size` unchanged and returns
  the second value.
- **delete:** after `map_remove(k)`, `map_contains(k)` is 0 and `map_size`
  decreases by one; other keys are unaffected.
- **collision survival:** insert keys that hash to the same bucket (find such a
  pair, or force it) and show all are still retrievable.
- **keys count:** `len(map_keys(...)) == map_size`.

### Definition of done
- `lib/map.smlib` present with the functions above, plus golden tests.
- `proof_lib` and `proof_props` totals go **up**, reproduced from a fresh checkout
  of current main, and the report states the new totals.
- `docs/sutram-stdlib.html` regenerated.
- Compiler untouched. Plain statement of anything you could not run, and of any
  edge case you deliberately excluded from the properties.
- Real harness output pasted and SHA-256 hashes listed.

### Note on the two representations
You now have both a char-code array form and a byte-packed string form
(`char_at`/`set_char`). Whichever `map.smlib` uses, document it in the header with
one worked example, and keep it consistent with your `string.smlib` header so a
reader can move between modules without guessing.

Deliver the files and the report.

# Memory: the decision, and the spec that is now fixed

**Owner's decision, 29 October 2026. Compiler v261, changelog v414.**

---

## The two words, decided

| Word | Devanagari | Means | Used for |
|---|---|---|---|
| **`kshetra`** | **क्षेत्र** | **region, field** | **the memory region — the block keyword** |
| **`avayava`** | **अवयव** | **member, component, limb** | **a member of a `rachana` — replaces `kshetra` in the field diagnostics** |

**Why this way round: `avayava` means "member", and a struct member IS a member. `kshetra` means region, and a memory arena IS a region.** **Each word goes where it fits best, and the reword improves the diagnostics rather than merely renaming them.**

**The four diagnostics that change (there are FOUR, not three — the hint at line 328 was missed at first):**

| Line | Now | Becomes |
|---|---|---|
| `src/sutram_compiler.asm:313` | `agyat kshetra '` | **`agyat avayava '`** |
| `:317` | `kshetra '` | **`avayava '`** |
| `:328` (hint) | `kasyashchid api rachanayah kshetram nasti` | **`avayavah nasti`** |
| `:827` | `rachana kshetra seema atikram` | **`rachana avayava seema atikram`** |

**Plus the four Devanagari entries in `lang/sanskrit.sandesh`, the 32 cognate entries in the 10 frozen packs, 4 goldens and 2 test assertions.** **Claude's inventory: no identifier in `lib/`, `examples/` or `tests/` is named `kshetra`, so no program breaks. The collision was in diagnostics only.**

---

## The five steps, fixed

### Step 0 — the `kosh` leak. No new syntax.
**In-place top-of-arena extension, plus 32 power-of-two intrusive freelist bins in `.bss`.**
**Two invariants make it safe: a `kosh` owns its backing buffer privately, so the old array is guaranteed dead; and `kosh` capacities are always powers of two.**
**~30 lines, in the emitter, one place.**

### Step 1 — `nirmmita` becomes a contiguous bump. No new syntax.
**Page sharing. Most of the ~1,000x.**
**Fallback: if the reservation fails or the range is exhausted, run today's `mmap` unchanged — so the worst case is exactly today.**

### Step 2 — `dvi-mukha`. No new syntax.
**One `.bss` range, two opposing cursors: persistent grows up from the start, scratch grows down from the end.**
**They cannot overlap, so the `kosh`-growth escape is structurally impossible.**

### Step 3 — the `kshetra` block. One new keyword.
**The region is LEXICAL: a `nirmmita` emitted inside a block uses the scratch cursor; every other `nirmmita` — outside blocks, inside library bodies, and `kosh` growth of an outer `kosh` — uses the persistent cursor.**
**The mark is a hidden local per nesting depth, so it is recursion-safe with no shadow stack.**
**Entry 2 instructions, normal exit 2, `krama`/`agrim` 2 or 0.**
**`nivartanam` is ALLOWED: evaluate the expression, then rewind, then return. Rejected only if the returned value is a scratch ADDRESS.**
**Exhaustion: abort cleanly. Never fall back to `mmap` inside a block, because that allocation would not be freed on rewind.**

### Step 4 — the check. No new syntax.
**Three 4-bit fields per symbol, packed into a byte:**
- **`var_depth`** — where the binding was declared. **Used when the symbol is the assignment target.**
- **`val_taint`** — whether the current value is a scratch pointer. **Used when read as a value.**
- **`box_depth`** — where a container's target lives. **Used when indexed or mutated as a container.**

**Three fields, not one, because a single number conflates "where do I live" with "what do I hold" — and that conflation rejects ordinary code like `vitti x = 42` then `total = total + x`.**

**Rules: strict inside a function; a documented contract across a `prakriya` call.**
**The contract is documented in three places a programmer will actually read: the error message itself (`Sutram Error [E_SCRATCH_ESCAPE]: asthayi smriti bahir na gacchati`), the keyword reference with a worked example, and four pinned negative tests.**

---

## What "0 DIFFER" can and cannot mean

**It cannot mean "nothing changed", and I should have said so earlier.** **Steps 0 to 2 change how `nirmmita` allocates, so they WILL change emitted bytes for existing programs.**

**So the guard's claim is:**
- **Against a post-Step-1 baseline: 0 DIFFER for programs that do not use a `kshetra` block.**
- **Against v261: a stated list of what changed, and every changed program produces the same OUTPUT.**

**That is the honest form, and it is ChatGPT's point in its R136, which I am adopting.**

---

## The order of work

**Wave 1 (independent, no allocator change):**
- **the `kosh` leak fix**
- **the `avayava` reword**
- **the Sanskrit check on both words against the compiler and the pack**

**Wave 2:** **the contiguous bump, then the two cursors.**

**Wave 3:** **the `kshetra` block and the check.**

**Windows is the owner's own work.**

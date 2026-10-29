# Memory: the decision, the vocabulary, and the spec

**Owner's decision, 29 October 2026. Compiler v261, changelog v414.**
**The vocabulary rule is in `docs/VOCABULARY-RULE.md` and applies to every word from now on.**

---

## The vocabulary — five words, one new keyword

| Word | Devanagari | Level | Where it appears |
|---|---|---|---|
| **`kshetra`** | **क्षेत्र** | **the whole arena — the field** | **errors and documentation, not a keyword** |
| **`mandapa`** | **मण्डप** | **the scratch block — a pavilion raised and struck** | **THE ONE NEW KEYWORD** |
| **`avayava`** | **अवयव** | **a member of a `rachana`** | **replaces `kshetra` in the four field diagnostics** |
| **`ardhamandapa` / `mahamandapa`** | **अर्धमण्डप / महामण्डप** | **size tiers** | **the compiler reports them; the programmer does not choose** |
| **`garbhagriha`** | **गर्भगृह** | **what must survive** | **documentation only** |

**Why this way: a `kshetra` contains `mandapa`s.** **A field contains pavilions.** **The Sanskrit already has the nesting, and we were making one word do both jobs.**

**And `avayava` means "member", which is what a struct member is.** **So the reword improves the diagnostics rather than merely renaming them.**

### The four diagnostics that change — there are FOUR, not three
**The hint at line 328 was missed at first, and Claude and ChatGPT each found it independently.**

| Line | Now | Becomes |
|---|---|---|
| `src/sutram_compiler.asm:313` | `agyat kshetra '` | **`agyat avayava '`** |
| `:317` | `kshetra '` | **`avayava '`** |
| `:328` (hint) | `kasyashchid api rachanayah kshetram nasti` | **`avayavah nasti`** |
| `:827` | `rachana kshetra seema atikram` | **`rachana avayava seema atikram`** |

**Plus 4 Devanagari entries in `lang/sanskrit.sandesh`, 32 cognate entries in the 10 frozen packs, 4 goldens, 2 test assertions.**
**Collision-checked: `mandapa`, `avayava`, `ardhamandapa`, `mahamandapa` appear ZERO times in the compiler, the packs, or the code.** **`kshetra` appears only in the four diagnostics, 44 pack entries and 8 expected-output files — no program identifier.**

---

## The five steps

### Step 0 — the `kosh` leak. No new syntax.
**In-place top-of-arena extension, plus 32 power-of-two intrusive freelist bins in `.bss`.**
**Two invariants make it safe: a `kosh` owns its backing buffer privately, so the old array is guaranteed dead; and `kosh` capacities are always powers of two.**
**~30 lines, in the emitter, one place.**

### Step 1 — `nirmmita` becomes a contiguous bump. No new syntax.
**Page sharing. Most of the ~1,000x.**
**Fallback: if the reservation fails or the range is exhausted, run today's `mmap` unchanged — the worst case is exactly today.**

### Step 2 — `dvi-mukha`. No new syntax.
**One `.bss` range, two opposing cursors: persistent grows up from the start, scratch grows down from the end.**
**They cannot overlap, so the `kosh`-growth escape is structurally impossible.**

### Step 3 — the `mandapa` block. One new keyword.
**The region is LEXICAL: a `nirmmita` emitted inside a block uses the scratch cursor; every other `nirmmita` — outside blocks, inside library bodies, and `kosh` growth of an outer `kosh` — uses the persistent cursor.**
**The mark is a hidden local per nesting depth, so it is recursion-safe with no shadow stack.**
**Entry 2 instructions, normal exit 2, `krama`/`agrim` 2 or 0.**
**`nivartanam` is ALLOWED: evaluate the expression, then rewind, then return. Rejected only if the returned value is a scratch ADDRESS.**
**Exhaustion: abort cleanly with `kshetra purnam` — "the field is full". Never fall back to `mmap` inside a block, because that allocation would not be freed on rewind.**

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

**It cannot mean "nothing changed".** **Steps 0 to 2 change how `nirmmita` allocates, so they WILL change emitted bytes for existing programs.**

**So the guard's claim is:**
- **Against a post-Step-1 baseline: 0 DIFFER for programs that do not use a `mandapa` block.**
- **Against v261: a stated list of what changed, and every changed program produces the same OUTPUT.**

---

## The order of work

**Wave 1 (independent, no allocator change):** **the `kosh` leak fix · the `avayava` reword · the word verification.**
**Wave 2:** **the contiguous bump, then the two cursors.**
**Wave 3:** **the `mandapa` block and the check.**

**Windows is the owner's own work.**

---

## `mandapa` is an indentation block — no braces

**The owner spotted that `mandapa { }` would look like `rachana Point = { x, y, z }`, and it would.**

**`rachana` is a DECLARATION: a name, an `=`, and a member list on one line. Nothing executes.**
**`mandapa` is a SCOPE: a bare opener, then indented code. It is a statement.**

**Different things — so they should look different:**

```
rachana Point = { x, y, z }

mukhya()
    mandapa
        vitti buf = nirmmita(1024)
        likha("buf = ", buf)
    # the pavilion is struck; the field remains
```

**Braces remain optional everywhere, as they always were — but examples never show them on a `mandapa`.** **203 of the 229 examples use no braces at all, and `mukhya`/`prakriya` are written without them throughout, so this is the language's own norm rather than a new rule.**

**And the deeper reason it is right: a `rachana` is the PLAN of a building — what it is made of. A `mandapa` is a HALL you walk into — where things happen.** **A plan is not a hall. A type definition is not a scope.**

---

## CORRECTION, 29 October — Step 0 as designed is impossible, and the plan changed

**Claude stopped before building it, and was right.** **Both invariants that the `kosh` fix rested on are false in this compiler.**

### Invariant 2 — "capacities are always powers of two": FALSE
**`kosh k[3]` reaches capacity 12 after nine pushes.** **`kosh k[5]` reaches 10.** **`kosh k[1000000]` is 1000000.** **131 `kosh` declarations carry a literal capacity and 33 are not a power of two.**
**So the freelist bins have no size class to index, and rounding capacities up would change goldens and change what programs mean.**

### Invariant 1 — "the old buffer is dead after growth": FALSE
**`vitti a = k` makes `a` a second live `kosh`.** **After `k` grows, `a` points at the old buffer and both work.** **Two live buffers.**
**With recycling bins, that old buffer would be handed to the next `kosh` of that size — so `a` would read and write ANOTHER `kosh`'s header. A silent use-after-free, which is exactly what R59 warned the `munmap`-on-move fix would create. The bins were that fix under another name.**

### And mechanism 1 could not exist in Step 0
**In-place extension needs a cursor to compare against.** **In Step 0 there is none — every `kosh` buffer is its own `mmap`.**

### What survives, and why
**Only in-place extension, and it moves into Step 1 where a cursor exists.**
**It is safe because it does not RELOCATE.** **`a = k` and then `k` grows in place means `a` and `k` still point at the same buffer, which is now larger.** **Nothing dangles, because nothing moved.**
**It catches the single-vector-in-a-loop case, which is the common one.**

**The interleaved-`kosh` leak remains, and it is documented as a bounded leak rather than fixed.** **A bounded leak is better than a use-after-free.**

### The lesson, which is the same one as the one-sentence scope rule
**The two invariants were ASSERTED, never checked against the tree.** **I passed them to Claude as "confirm both before building" — and both were false.** **That instruction is the only reason this did not ship.**

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

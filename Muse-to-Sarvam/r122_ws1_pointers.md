# Muse Round 122 WS1 — Pointer-return audit of the Sutram library

- **Base:** `<workspace>/r121-124/tree297` (v297; compiler banner
  `Sutram 1.0 (v297) - sampurna sutra`, `src/sutram_compiler.asm:249`).
- **Scope:** `lib/*.smlib` only, plus — because the task names them explicitly —
  the two builtins `anka_akshar` and `vartani_sandhi`, which are **not** in
  `lib/` at all: they are compiler builtins (BN 25 `char_from` /
  BN 18 `vartani_cat`, primary names from v292) implemented by code
  generation in `src/sutram_compiler.asm`. They are reported separately
  (§3) and are **not** counted in the lib totals (§4).
- **Method:** every `prakriya` body was read. `grep -c "^prakriya "` per file
  sums to 310 (see §4). For each function, every `nivartanam` expression
  was traced to its source: a `nirmmita(...)` call, a parameter, a
  parameter-indexed cell, a call to another lib function, or a scalar
  computation. All 26 functions that call `nirmmita` were checked
  individually for whether the `nirmmita` value itself is returned or is
  only scratch. No classification below is guessed from a name.
- **Audit only.** No code was changed, nothing was pushed or merged.

## Terminology used in the table

- **(a) caller-provided** — the returned address is a buffer the caller
  passed in (an `out`/`dst`/operand argument, or a container the caller
  owns). The function does not allocate it.
- **(b) static** — a fixed buffer in the function/module, shared across
  calls (e.g. a BSS buffer). No such buffer exists anywhere in `lib/`
  (verified: no top-level `vitti`/`dasham`/`kosh` declaration outside a
  `prakriya` in any of the 24 files).
- **(c) heap** — `nirmmita`/`mmap` memory, which lives for the program
  (there is no `munmap`/free anywhere, so heap handles never become
  dangling by reclamation; they leak by design).
- **(d) own stack frame** — an address inside the returning function's
  own frame (a local that dies on return). **No lib function does this
  (see §2).** One builtin does something adjacent but distinct — see §3.

A return that is a **scalar** (count, length, index, sum, boolean, hash,
packed value, or a cell's *contents*) is **not** a pointer return, even
if the scalar happens to be an integer the caller later uses as an
address. Those functions are excluded from Table 1, with the reasons
and the borderline cases spelled out in §1.3, so the exclusion is
auditable rather than silent.

## 1. Table of ALL pointer-returning functions (lib, strict sense)

"Strict sense" = the returned `vitti` **is** an address — the base of a
buffer, string, kosh, list, map, or set — that the caller dereferences,
indexes, or prints as a string. Returning a cell's *contents* does not
qualify (see §1.3).

| # | Function | File | What it returns | Class | One-line body evidence |
|---|---|---|---|---|---|
| 1 | `mala_nava(n)` | `mala.smlib:8` | Fresh qword array, `n` cells | (c) heap | `nivartanam nirmmita(sz)` where `sz = c * 8`, after overflow guards; `0` on bad/oversize `n`. |
| 2 | `nighantu_srij(cap)` | `nighantu.smlib:107` | Fresh map handle `m` (header cells + key area) | (c) heap | `m = nirmmita(sz)` with `sz = (2 + 3*c)*8 + c*32`; `m[0]=c, m[1]=0`; `nivartanam m`. |
| 3 | `nighantu_vardh(m, newcap)` | `nighantu.smlib:279` | Fresh map handle `newm` of capacity `newcap`, contents copied | (c) heap | `newm = nighantu_srij(newcap)` (hence heap via #2); `tmp = nirmmita(...)` is scratch only; `nivartanam newm`. Caller must rebind; the old handle is not freed (it leaks, it does not dangle). |
| 4 | `suchi_srij(cap)` | `suchi.smlib:46` | Fresh list header `l` (`l[0]=len, l[1]=cap, l[2]=data`) | (c) heap | `l = nirmmita(3*8)`; `d = nirmmita(sz)`; `l[2] = d`; `nivartanam l`. Both header and data are heap. |
| 5 | `avali_srij(cap)` | `suchi.smlib:384` | Fresh queue header `q` (`q[0]=len, q[1]=cap, q[2]=data, q[3]=head`) | (c) heap | `q = nirmmita(4*8)`; `d = nirmmita(sz)`; `q[2] = d`; `nivartanam q`. Same shape as #4. |
| 6 | `rakh_srij(cap)` | `sangrah.smlib:33` | Fresh set handle (a map) | (c) heap | Body is a single line: `nivartanam nighantu_srij(cap)` — heap by delegation to #2. |
| 7 | `rakh_vardh(s, newcap)` | `sangrah.smlib:171` | Fresh set handle of capacity `newcap`, contents copied | (c) heap | Body is a single line: `nivartanam nighantu_vardh(s, newcap)` — heap by delegation to #3. Comment says "Rebind: `s = rakh_vardh(s, 32)`". |

That is the complete strict list in `lib/`: **7 functions, all (c) heap,
0 (a), 0 (b), 0 (d).**

### 1.1 Why the other `nirmmita` users are NOT pointer-returning

26 lib functions call `nirmmita`. Only #1, #2, #4, #5 return a
`nirmmita` value directly, and #3/#6/#7 return one by delegation. The
other 21 use `nirmmita` purely as **scratch that is never returned** and
return a scalar instead — so their scratch can leak (no free exists)
but can never dangle in the caller's hands:

- `aadhar.smlib:brihat_ank_tak` — `w`, `rev` are scratch work arrays;
  returns `rlen` (digit count); the result is written into caller `dst`.
- `brihat.smlib:brihat_shesh` — `tr` scratch passed to the helper;
  returns the helper's status (0 / −1).
- `brihat.smlib:brihat_ghatmod` — `t1`, `bcur`, `tr` scratch; returns 0.
- `nighantu.smlib:nighantu_mil` — `tmp` scratch for key listing;
  returns `merged` (count merged).
- `roop.smlib:roop_ank`, `roop_ank_aadhar`, `roop_varg_ank`,
  `roop_sthir_mool`, `roop_chinhit`, `roop_chihna_akshar` — `rev`/`tmp`
  digit scratch; each returns a byte count (`rlen`, `n`, `wpos`, …) and
  writes the text into caller `out`.
- `sangrah.smlib:rakh_ubhaya_bhed`, `rakh_sangam`, `rakh_sampat`,
  `rakh_bhed`, `rakh_asti_upasamuh`, `rakh_tak_mala` — `tmpa`/`tmpb`/
  `tmp`/`scratch`/`ptrs`/`lens` key-listing scratch; each returns a
  count (`nighantu_maap(out)`, `nk`, or 0/1) and writes into caller `out`.
- `shreni.smlib:mil_shreni` — `tmp` merge scratch; returns 0.
- `suchi.smlib:suchi_vardh`, `avali_pravesh` — `nd` is a new data buffer,
  but it is **stored back into the caller's header** (`lst[2] = nd` /
  `qu[2] = nd`) and the function returns 1 (status), not the buffer.
  (Note: the old data buffer is never freed, so a caller that kept the
  old `l[2]`/`q[2]` separately still reads stale-but-valid memory — a
  staleness hazard, not a dangling return.)
- `vakyank.smlib:ank_tak_varna`, `ank_tak_aadhar_varna` — `rev` digit
  scratch; returns a byte count and writes into caller `out`.

### 1.2 Functions that write into a caller buffer but return a scalar

This is the dominant lib pattern and must not be mistaken for (a)
pointer returns: `roop_*`, `khand_*`, `varna_*`, `vakyank.ank_tak_*`,
`patra_path_sarv`/`patra_likh_sarv`, `khand_*`/`varna_*` join/split/
case functions, `samanvaya.*` matrix functions (return element counts),
`phal_*` checked wrappers (return `o[0]` status), and all
`*_khip`/`*_sangrah`/`*_pratilip` mutators return 0/1 status. They take
an `out`/`dst` argument, fill it, and return a length/count/status.
The caller already owns the buffer; nothing new is handed back.

### 1.3 Borderline cases, explicitly excluded (with reason)

- **Element loads — value, not address.** `mala_grah`,
  `mala_grah_surakshit` (`pad8(a + j*8)`), `suchi_grah` (`d[idx]`),
  `chay_apanay`/`avali_nishkas` (popped `val`), `chay_avalok`/
  `avali_avalok` (`d[…]`), `nighantu_grah`/`nighantu_grah_mool`
  (`m[…]` or `def`), `phal_mulya`/`phal_mulya_va` (`r[1]` or `def`).
  Each returns the **contents** of a caller-owned cell. If — and only
  if — the caller stored an address in that cell, the returned value
  *is* that address, round-tripped; its storage class is whatever the
  caller gave it originally, not something this function created. They
  are therefore not counted as pointer-returning, but a caller that
  stores pointers in a `mala`/`suchi`/`nighantu` gets pointer values
  back from exactly these 11 functions. (The same round-trip caveat
  applies in principle to any element load, e.g. `shreni.laghu`/
  `adhik` returning `a[0]`; in practice those are documented as
  numeric min/max, so they are not listed here.)
- **Cursors, not pointers.** `anukram_khip_i64` / `anukram_grah_i64`
  return `p + 8` and `anukram_khip_aayam_purva` /
  `anukram_grah_aayam_purva` return `p2 + cnt`, but `p`/`p2` are
  **integer byte offsets** (`pos`) into a caller buffer, as the file
  header states ("returns the new cursor"). Adding 8 to a cursor is
  not forming an address; the caller adds it to its own base itself.
  Misreading these as (a) pointer returns would be a classification
  error.
- **Packed scalars, not pointers.** `ganita.brahmagupta_kshetr` returns
  `r[0]/4 + r[1]*268435456 + r[2]*288230376151711744` — one integer
  packing three limbs. `r` itself is a local array (see §2) and is
  never returned.
- **No-return mutators (7 functions).** `chandas.meru_mala`,
  `ganita.samasa`, `shreni.vinimay`, `shreni.budbud_shreni`,
  `shreni.viparyay_mala`, `shreni.shankh_shreni`,
  `shreni.nivesh_shreni` contain no `nivartanam` at all; they sort /
  fill / swap **in place** in a caller array and return nothing. They
  cannot return a dangling pointer because they return nothing.

## 2. Dangerous list — own-stack-frame returns

**In `lib/`: NONE. Zero functions return a pointer into their own
stack frame.**

Proof, by elimination over all 310 bodies:

1. **Every address-producing expression was traced.** Addresses in lib
   code come from exactly three sources: (i) `nirmmita(...)` (heap),
   (ii) a parameter (`out`, `dst`, `buf`, `arr`, `m`, `l`, `q`, `s`, …),
   or (iii) arithmetic on (i)/(ii) (`a + j*8`, `tmp + pos + 1`,
   `scratch + ptrs[j]`). There is no address-of-local operator in any
   lib body, and no lib body forms an address from a local scalar.
2. **Every `nirmmita` value was checked (§1.1).** The only `nirmmita`
   values ever returned are the four heap handles (#1, #2, #4, #5) and
   their delegations (#3, #6, #7). All other `nirmmita` values are
   scratch that is never returned.
3. **Local arrays are never returned.** The only local array
   declarations in all of `lib/` are in `ganita.brahmagupta_kshetr`
   (`vitti S[12]`, `f1[3]`…`f4[3]`, `x[6]`, `y[6]`, `P[12]`, `r[3]`,
   `t[3]`, `q[6]` — `ganita.smlib:207–239`). That function returns
   only the packed scalar computed from `r[0..2]` (see §1.3); none of
   `S`, `f*`, `x`, `y`, `P`, `r`, `t`, `q` appears in a `nivartanam`.
   No other lib function declares a local array at all, and no lib
   function declares a local `kosh`.
4. **No static buffers exist to confuse the issue.** No file has a
   top-level (outside-`prakriya`) variable declaration, so class (b)
   is empty in `lib/` as well as class (d).

The **one** dangerous return in the whole area examined is **not** in
`lib/` — it is the builtin `anka_akshar`, detailed in §3. It is not
class (d) as defined (a named frame local); it is unreserved stack
scratch, which is dangerous for a closely related but mechanically
different reason, and the distinction matters for the fix.

## 3. `anka_akshar` / `vartani_sandhi` verdict

Both are compiler builtins, inlined by code generation (there is no
separate callee frame — the emitted bytes run inline at the call
site). Their bodies are in `src/sutram_compiler.asm`.

### 3.1 `vartani_sandhi` — class (a) caller-provided, mutated in place

- **Body** (`.ge_call_vartcat`, `src/sutram_compiler.asm`, comment
  "`vartani_cat(dst, src) → strcat, returns dst`"): evaluate `dst`,
  push it; evaluate `src`; pop `dst` into `rdi`, save it in `r8`;
  scan `dst` forward to its NUL; copy `src` bytes including the
  terminator into `dst`; finish with `mov rax, r8` — **return `dst`**.
- **Classification: (a) caller-provided.** The returned pointer is
  exactly the first argument's buffer. No allocation happens, no new
  string is created, and the operand is overwritten in place. This
  confirms the Round 120 finding (`v = "ab"`;
  `s = vartani_sandhi(v, "cd")`; `shabda(v)` prints `"abcd"`) from the
  code, not just from probing.
- **Consequence, by what the caller passed:**
  - Writable caller buffer (e.g. a `nirmmita` buffer or a variable
    string): the call "works" but **aliases** — the caller holding
    `dst` sees the mutation, so `dst` and the result are one string,
    not two. Any code that assumes the v287 contract (concatenation
    makes a new string, operands unchanged) is wrong for this builtin.
  - String literal as `dst`: on Linux the literal pool is writable,
    so the write silently corrupts the literal; on PE the literal
    pool is read-only, so the same write faults (`0xC0000005`) —
    exactly the Round 118 `322`/`323` Windows crash. One bug, two
    platform symptoms.
- **Not a dangling return.** The pointer stays valid as long as the
  caller's buffer does. Its defect is **mutation + aliasing**, not
  lifetime.

### 3.2 `anka_akshar` — stack scratch, NOT static, NOT heap, NOT caller

- **Body** (`.ge_call_charfr`, `src/sutram_compiler.asm`, comment
  "`char_from(code) → pointer to a char (writes code to a temp
  buffer)`" and "`Uses a static 1-byte buffer in BSS`"): the emitted
  bytes are, in order:
  `sub rsp, 16` (`48 83 EC 10`); `mov [rsp], al` (`88 04 24` — the
  code byte); `mov byte [rsp+1], 0` (`C6 44 24 01 00` — the NUL);
  `mov rax, rsp` (`48 89 E0` — return the address); `add rsp, 8`
  (`48 83 C4 08`).
- **What that means, arithmetically.** If `rsp = R` on entry: the byte
  goes to `R−16`, the NUL to `R−15`, `rax` is set to `R−16`, then
  `rsp` becomes `R−8`. The returned pointer is therefore **`rsp − 8`
  on return — 8 bytes below the current stack pointer, in space that
  was just "freed" and is not part of any reserved frame slot.**
- **Classification: (d)-adjacent stack scratch — dangerous, but
  precisely NOT (b) static and NOT (d) a named frame local.**
  - **Not (b):** the "static 1-byte buffer in BSS" comment is wrong
    about the code as written. No `char_buf` symbol is defined
    anywhere else in the compiler (the only mention is that comment
    line itself, which even says "we need the runtime address" and
    then abandons the `lea [rel char_buf]` idea in favour of the
    `rsp` sequence). A reader trusting the comment would classify
    this as a shared static buffer; the emitted bytes say otherwise.
  - **Not (c):** no `nirmmita`/`mmap` is involved, so the buffer does
    not live for the program.
  - **Not (a):** the caller passed only a code integer, not a buffer.
  - **Not a named (d) local either:** a proper frame local would sit
    inside the function's reserved spill area (above the frame's
    `rsp` after prologue) and survive until the function returns.
    This byte sits **below** `rsp` on return, so it survives only
    until the next stack operation.
- **Exact clobber mechanism (why the Round 120 probe failed).** The
  next `push` or `call` writes exactly at `rsp − 8`:
  `vartani_sandhi`'s first step is `push rax` (the `dst`), which
  decrements `rsp` and writes 8 bytes at the old `rsp − 8` — the
  `anka_akshar` byte and its NUL. Any ordinary function call does
  the same with its return address. Hence:
  - `c1 = anka_akshar(66); shabda(c1)` prints `"B"` — nothing has
    touched the stack in between.
  - `c1 = anka_akshar(66); c2 = anka_akshar(67); shabda(c1)` still
    prints `"B"` — each call nets `rsp − 8`, so successive calls get
    distinct descending slots and do not overwrite each other.
  - `c1 = anka_akshar(66); t = vartani_sandhi("x","y"); shabda(c1)`
    prints garbage — the `push` inside `vartani_sandhi` overwrote
    `c1`'s byte. This is the observed Round 120 result, derived here
    from the emitted bytes.
- **Related truncation (not a storage class, noted for completeness).**
  Only `al` (the low byte) is stored, so a code above 255 wraps
  (`anka_akshar(256)` → NUL → empty string, as observed in Round 120).
  That is a separate range defect, not the storage defect.

### 3.3 Do they share a cause?

**No — distinct root causes that compose into one symptom.**

| | `vartani_sandhi` | `anka_akshar` |
|---|---|---|
| Root cause | Returns the caller's buffer and writes into it (old `vartani_cat`/`strcat` semantics, no allocation). | Returns unreserved stack scratch below `rsp` (emitted `sub rsp,16` / `add rsp,8` sequence). |
| Defect type | Mutation + aliasing (operand corrupted; crash iff operand is read-only). | Lifetime (result valid only until the next push/call). |
| Fix direction | Allocate a new string for the result (or refuse a literal/read-only `dst`). | Return heap memory, a caller-provided buffer, or a genuine static buffer — anything that survives a push/call. |
| Fixing the other does not fix this | Fixing `anka_akshar` alone leaves `vartani_sandhi` mutating its operand. | Fixing `vartani_sandhi` alone leaves `anka_akshar`'s result clobbered by the next call of any kind. |

The **composition** is real and explains the Round 120 probe: the
`vartani_sandhi` call that corrupts `anka_akshar`'s result does so
*through* its `push`, i.e. through the stack-scratch lifetime hole —
but the push is normal codegen, not a bug in `vartani_sandhi` itself.
Conversely, the Windows `322`/`323` crash needs only `vartani_sandhi`
(a literal `dst`); `anka_akshar`'s bad byte on Windows is a second,
independent symptom of its own lifetime hole. Treat them as **two
fixes**, not one.

## 4. Counts

### 4.1 Lib functions audited (verified)

`grep -c "^prakriya "` per file, summing to the stated total:

| File | Count | File | Count |
|---|---|---|---|
| `aadhar.smlib` | 2 | `mala.smlib` | 8 |
| `ank.smlib` | 10 | `nighantu.smlib` | 17 |
| `anukram.smlib` | 5 | `patra.smlib` | 3 |
| `brihat.smlib` | 13 | `phal.smlib` | 14 |
| `chandas.smlib` | 6 | `roop.smlib` | 23 |
| `ganit.smlib` | 18 | `sadhan.smlib` | 7 |
| `ganita.smlib` | 27 | `samanvaya.smlib` | 11 |
| `gudh.smlib` | 2 | `sangrah.smlib` | 14 |
| `kalana.smlib` | 6 | `sankhyiki.smlib` | 16 |
| `khand.smlib` | 22 | `shreni.smlib` | 14 |
| `madhava.smlib` | 5 | `suchi.smlib` | 34 |
| `vakyank.smlib` | 6 | `varna.smlib` | 27 |

**Total audited: 310 functions in 24 files — matches the task's
stated total exactly.**

### 4.2 Pointer-returning, by storage class

Lib only (strict sense, Table 1):

| Class | Count | Functions |
|---|---|---|
| (a) caller-provided | 0 | — |
| (b) static | 0 | — |
| (c) heap (`nirmmita`) | 7 | `mala_nava`, `nighantu_srij`, `nighantu_vardh`, `suchi_srij`, `avali_srij`, `rakh_srij`, `rakh_vardh` |
| (d) own stack frame | 0 | — |
| **Strict pointer-returning total (lib)** | **7** | |

Lib + the two named builtins (for the Round 122 WS2 question):

| Class | Count | Functions |
|---|---|---|
| (a) caller-provided | 1 | `vartani_sandhi` (builtin; returns `dst`, mutated) |
| (b) static | 0 | — (`anka_akshar`'s BSS comment is stale; see §3.2) |
| (c) heap | 7 | as above |
| (d) own stack frame (strict, named local) | 0 | — |
| (d*) stack scratch below `rsp` (dangerous, distinct from (d)) | 1 | `anka_akshar` (builtin) |
| **Pointer-returning total (lib + 2 builtins)** | **9** | |

### 4.3 The rest of the 310 (so the audit accounts for everything)

- Strict pointer-returning (lib): **7**
- No-return in-place mutators: **7** (§1.3)
- Scalar-returning (status / count / length / index / sum / boolean /
  hash / packed value / element contents): **296**, of which:
  - 11 are element-content accessors whose returned value is a
    pointer iff the caller stored one (§1.3) — not counted as
    pointer-returning, because they create no storage;
  - 21 of the 26 `nirmmita` users fall here (scratch only, §1.1);
  - 4 `anukram` functions return integer cursors, not addresses (§1.3).
- **7 + 7 + 296 = 310. Nothing unaccounted for.**

### 4.4 Headline for WS2

- **No lib function returns its own stack frame.** The lib's pointer
  story is clean: every handle it hands back is heap, and every other
  function either returns a scalar or writes into a buffer the caller
  already owns.
- **The danger is entirely in the two builtins, and it is two
  different dangers:** `vartani_sandhi` mutates its caller's buffer
  (class (a), aliasing + read-only crash); `anka_akshar` returns
  stack scratch below `rsp` (class (d*), clobbered by the next
  push/call). Neither is a lib defect, and neither fix subsumes the
  other.

# ROUND-161 — the 64 MiB region, the 16 bytes, and what the compiler knows about death

**Base:** main at `27bed64a` (compiler v315). **Read only. Nothing compiled or run.**
**Delivered:** report + `r161.json`. **Method:** read the compiler (`src/r65_arena.inc`,
`src/sutram_compiler.asm`, `win/winrt_blob.asm`, `docs/`), traced the allocation,
growth, block-entry/exit, and symbol-table paths, and spot-checked every decisive
claim by re-reading the cited code. All `file:line` citations are at `27bed64a`.

## Verdicts, in one paragraph

**Task 1.** The 64 MiB is reserved in exactly one live place — the growth path, never
at creation — and the pointer to it **is** recorded: in the descriptor, as the elements
pointer `[d]` (the region base, by construction) plus the size as `[d+8]`. There is no
side table. The brief's second premise is therefore false: freeing at death is not
blocked by missing bookkeeping — the growth path already frees the old region with
exactly the two words a death-free would need. What a free-at-death does not have
today is (a) a decision point — knowledge that the `kosh` is dead — and (b) the
aliasing guarantee. The non-release at death is also a **documented decision**, not an
oversight (reference §19). `munmap` / `VirtualFree` releases the **whole old region**,
on both platforms — the `winrt_blob.asm:184` comment is accurate. The 64 MiB is
**reserved, not committed**, on both platforms, so defect 1 is primarily an
address-space leak (64 MiB per dead big `kosh`) and secondarily a committed-pages leak
(the touched pages: ~64 KiB at the boundary, ~16 MB for a 2,000,000-element `kosh`).
The brief's "about a thousand passes, 64 GB" arithmetic is exact for address space —
but the program **fails** only under a virtual-memory limit; on an unlimited 64-bit
process it does not fail from address space alone. The boundary is **4,097 elements**,
and the source agrees with R169 exactly — but the brief's phrasing is off by one
element read strictly ("above 4,097" means 4,098+; a `kosh` with exactly 4,097
elements already has a region). The number 4,097 appears nowhere as a constant: it is
a consequence of `R127_BIG` (65,536 bytes) plus the doubling growth.

**Task 2.** The 16 bytes are **not** a descriptor slot, not a mark record, not
bookkeeping, and not a separate allocation at all. The block adds 24 bytes of R82
header (3 extra qwords: line, liveness slot, generation) to the single
descriptor+elements allocation, and the persistent allocator's 16-byte alignment
rounding absorbs 8 of them (the plain allocation already wastes 8 bytes of padding:
40 → 48). Net observable difference: **16 bytes per kosh**. All three of the brief's
per-pass numbers reproduce exactly from the code (48, 64, 80).

**Task 3.** `decl_depth` **does not exist** (zero hits in `src/`, `win/`, `tools/`,
`tests/`, `docs/`). The equivalent exists as `r73_var_depth`, but it is the **mandapa
depth only** — a name in a plain block, loop body, or `yadi` branch returns 0,
indistinguishable from a top-level name, a parameter, or an undeclared name. There is
no liveness/last-use analysis anywhere, and no record anywhere links a name to its
allocation. Dead but the compiler cannot know: a `kosh` in a loop body, pushed once
and read once, is dead after the read each pass — but the compiler has no last-use
analysis and no (name → storage) record. Alive but the compiler would think it dead:
a function-scope `kosh` passed by its own name to a foreign function with a `ptr`
parameter — the FFI door explicitly permits it, C receives the elements address, and
C may keep it indefinitely in C-side state. No escape byte, no taint, no record exists
for this; a scope-based reclaimer would hand C a dangling pointer.

---

## Task 1 — and the 64 MiB region

### 1. Where is the 64 MiB reserved, and where is the pointer recorded?

**The reservation site: one live place, the growth path.** The only live reservation
of a `kosh` region is in `r127_emit_grow` (`src/r65_arena.inc:579`), the `.big` path
(`:650-663`):

```asm
; shl rax,1
R23_EMIT 0x48,0xD1,0xE0            ; shl rax,1
...
lea rsi, [rel r101a_a1]            ; mmap(max(rax, R101A_REGION), NORESERVE) -> rax, rsi = size
mov rcx, r101a_a1_len
call r23_emit_bytes
call emit_syscall
lea rsi, [rel r101a_a2]
mov rcx, r101a_a2_len
call r23_emit_bytes
R23_EMIT 0x48,0x89,0xF2            ; mov rdx,rsi
```

The byte sequence it emits is `r101a_a1` (`src/sutram_compiler.asm:464`), decoded by
its own comment (`:462-463`):

```asm
; R101A: mov rsi,REGION ; cmp rax,rsi ; cmova rsi,rax ; xor edi,edi ; mov edx,3 ;
;       mov r10d,0x4022 (PRIVATE|ANONYMOUS|NORESERVE) ; mov r8,-1 ; xor r9d,r9d ; mov eax,9
```

So the emitted call is `mmap(0, max(2 * new_bytes, R101A_REGION), PROT_READ|PROT_WRITE,
MAP_PRIVATE|MAP_ANONYMOUS|MAP_NORESERVE, -1, 0)`, with `r101a_a2` (`:469`) turning
failure into 0:

```asm
r101a_a2 db 0x48,0x3D,0x01,0xF0,0xFF,0xFF, 0x72,0x02, 0x31,0xC0
; (syscall) cmp rax,-4095 ; jb +2 ; xor eax,eax
```

with `R101A_REGION equ 0x04000000 ; 64 MB of address space per kosh`
(`src/sutram_compiler.asm:9104`).

**Not at creation.** A `kosh` is created by `r108_kosh_alloc`, which ends in
`r101a_emit_kosh_alloc` (`src/sutram_compiler.asm:12657, 12659, 12672`), and that
routine's first instruction is (`:9122-9123`):

```asm
r101a_emit_kosh_alloc:
    jmp emit_nirmmita_from_rax     ; R127: no region - the descriptor and its first elements are
                                   ; one ordinary allocation; growth moves the elements, not it
```

Everything after the jump — including a second copy of the region-`mmap` emission
(`:9142-9149`) — is dead code. The R101A block's own header says so (`:9090-9092`):

```asm
;; R101A (Option A, R101): every kosh has a region of its own. SUPERSEDED in R127 (v302): a kosh is
;; a descriptor (src/r65_arena.inc, r127_emit_grow); only a kosh past 64 KiB of elements takes a region.
;; The text below is R101A's, kept for its history; r101a_emit_kosh_alloc now jumps to nirmmita.
```

The old in-place extension `r101a_emit_kosh_extend` (`:9155`) likewise has **no
callers** anywhere in `src/` — dead. The only caller of `r127_emit_grow` is the push
path (`src/sutram_compiler.asm:22537`): `call r127_emit_grow ; R127: grow the
elements; the descriptor (every name) stays`.

**Where the pointer is recorded: in the descriptor — as `[d]`, plus `[d+8]`.** The
descriptor layout, from the R127 comment (`src/r65_arena.inc:555-560`):

```asm
; A kosh value is a descriptor d that never moves: [d-16] length, [d-8] capacity (R82's line,
; slot and generation before them when on), [d] the elements, [d+8] the bytes of the region the
; elements are in (0: they are in the arena, or right after the descriptor). Every name of the
; kosh holds d, so whatever growth does to the elements, every name sees it.
```

There is **no separate "region base" field and no side table**. The region base is
recorded as the elements pointer itself, `[d]`, because the `mmap` return value
(`rax`) becomes the new elements pointer directly. The growth path, after the copy
(`r65_arena.inc:683, 718-719`):

```asm
; pop r11 ; pop r9 ; pop r8 ; mov r10,rax ; mov rsi,[r8] ; xor ecx,ecx
...
; mov [r8],r10 ; mov [r8-8],r11 ; mov [r8+8],rdx
R23_EMIT 0x4D,0x89,0x10, 0x4D,0x89,0x58,0xF8, 0x49,0x89,0x50,0x08
```

i.e. `[d] = new base (rax, the mmap return)`, `[d-8] = newcap`, `[d+8] = rdx = the
mmap length` (`mov rdx,rsi` at `:663`, where `rsi = max(2 * new, R101A_REGION)` from
`r101a_a1`). The elements start at the region base — nothing ever offsets the
elements pointer within a region — so `[d]` **is** the region base whenever `[d+8] != 0`.

At creation the pair is initialised to "no region": the allocation is
`(capacity + 4) * 8` bytes — `add rax,4: 2 header qwords + R127's elements pointer and
region size` (`src/sutram_compiler.asm:19311`) — and the store sequence `r127_dk`
(`:574`) writes:

```asm
r127_dk db 0x48,0x8D,0x48,0x10, 0x48,0x89,0x08, 0x48,0xC7,0x40,0x08,0x00,0x00,0x00,0x00
; lea rcx,[rax+16] ; mov [rax],rcx ; mov qword [rax+8],0 - the elements right after, no region
```

i.e. `[d] = d+16` (the elements, right after the descriptor, in the arena) and
`[d+8] = 0`. The R82 path writes the same two words after its five header words
(`:19318-19330`, `r82_emit_kosh_header`).

**How the growth code finds the old region to release it.** From the same two words.
Before the copy loop, `rsi` is loaded with the old elements pointer (`:683`:
`mov rsi,[r8]`); after the copy, the old region size is read (`:699`):

```asm
; mov rcx,[r8+8] ; test rcx,rcx ; jz .kept (rel32)
```

If it is zero (arena), the release is skipped; otherwise the release uses `rsi` (old
`[d]`) as the address and `rcx` (`[d+8]`) as the length — see §3. No other record of
the region exists: the only `kosh` bookkeeping tables in the compiler are the
block-liveness tables (`r108_bk_node/name/gd`, which record that a `kosh` is of an open
block, not where its elements live) and the `parimana()` name table (`r107_knames`). No
region table was found by searching `src/` for a region registry.

### 2. If the address is recorded nowhere, then freeing it is impossible without first recording it. Is that true?

**No — the premise is false.** The address **is** recorded (as `[d]`, the elements
pointer = the region base) and the size **is** recorded (as `[d+8]`). The growth path
already proves the pair is sufficient: it frees the old region with exactly those two
words and no side table (§3). A free-at-death would be the same call the growth path
already makes:

- Linux: `munmap([d], [d+8])` when `[d+8] != 0` — the exact emission at
  `r65_arena.inc:711-713` (see §3).
- Windows: `VirtualFree([d], 0, MEM_RELEASE)` — the exact call in
  `win/winrt_blob.asm:183-191` (see §3).

What a free-at-death **does not have today**, and would need:

1. **A decision point — knowledge that the `kosh` is dead.** Nothing in the compiler
   records a `kosh`'s death today; there is no release on any exit path
   (`r73_gen_rewind` only stores the saved mark into the scratch cursor — R169 WS5).
   That is Task 3's subject, not a recording problem.
2. **The aliasing guarantee.** Every name of the `kosh` holds the same descriptor
   `d`, so freeing the region while any name can still reach the `kosh` would make a
   later access read freed — or reused — memory. The growth path never faces this
   because it replaces the region while the `kosh` is alive; a death-free would need
   every name dead too.
3. **Nothing in the way of recording.** No new field, no side table, no descriptor
   change is needed to find the region: `[d]` and `[d+8]` already hold it. (The
   descriptor itself lives in the arena, not the region, and would stay behind as
   32/56 bytes of arena — the arena never returns anything anyway.)

And the non-release at death is a **documented decision**, not an oversight.
Reference §19 (`docs/LANGUAGE-REFERENCE.md:1406-1412`):

> **Decided (R103, v285): the block does not take a `kosh`'s memory back; the `kosh`
> keeps it for the program's life.** That is what keeps the check above exact: the
> check reads the `kosh`'s header, so the header must still be there after the block.
> Giving the region back would make a dead `kosh` reaching a `prakriya` a crash (or,
> if the address were reused, a silent read of another `kosh`) instead of
> `E_KOSH_MANDAPA` with its line.

A design that frees at death would have to reckon with that decision (the static
refusal is what protects a dead `kosh` today; the region is kept as the runtime
backstop for a `kosh` that reaches a procedure through a hole in the check).

### 3. What does `munmap` currently release — an old buffer on growth, the whole region, or both?

**The whole old region, on both platforms.** Not just the used bytes.

**Linux** (`src/r65_arena.inc:711-715`):

```asm
; the old region back: push rdx ; push r10 ; push r11 ; push r9 ; push r8 ;
; mov rdi,rsi ; mov rsi,rcx ; mov eax,11 ; syscall ; pop r8 ; pop r9 ; pop r11 ; pop r10 ; pop rdx
R23_EMIT 0x52, 0x41,0x52, 0x41,0x53, 0x41,0x51, 0x41,0x50, 0x48,0x89,0xF7, 0x48,0x89,0xCE, 0xB8,0x0B,0x00,0x00,0x00
```

The emitted call is `munmap(rdi = rsi = old [d], rsi = rcx = old [d+8])`. `[d+8]`
holds the **full reservation size** — `max(2 * new_bytes_at_that_growth, 64 MiB)` —
not the used bytes. So the `munmap` releases the entire mapping created by the
region's `mmap`, including the untouched tail. It is the only `munmap` (syscall 11) in
the compiler: the only `mov eax,11` in `src/` and `win/` is this one (`:712-713`). It
runs only when the old elements were in a region; when they were in the arena
(`[d+8] = 0`) the `jz .kept` at `:699` skips it and the old arena bytes are abandoned,
not released.

**Windows** (`win/winrt_blob.asm:183-191`):

```asm
.free:
    ; R127: munmap(addr, len) - a kosh's old region; VirtualFree releases the whole reservation
    mov rcx,r13
    xor edx,edx
    mov r8d,0x8000
    call qword [rbx+RT_VirtualFree]
```

`VirtualFree(addr, 0, MEM_RELEASE)` — with `MEM_RELEASE` the size must be 0 and the
API releases **the entire region** reserved by the single `VirtualAlloc`, whatever
fraction of it was committed. The comment at `:184` is accurate: "VirtualFree releases
the whole reservation". The Linux and Windows paths agree: both release the whole old
region. The "old buffer" reading would be wrong — neither releases only the used
element bytes.

The only other `VirtualFree` in the runtime is the 64 KiB out-of-memory reserve, freed
in the failed-commit path (`:312`, inside `.v_nomem`, just before the diagnostic and
exit — R169's table says ":312 … at exit only"; the line number is right, the gloss is
loose: it is the out-of-memory exit path, not a normal exit).

### 4. Is the 64 MiB reserved or committed?

**Reserved, not committed, on both platforms.** Defect 1 is therefore primarily an
address-space leak — but not only that: the touched pages are committed and they stay
too.

**Linux.** The region `mmap` is `mmap(0, len, PROT_READ|PROT_WRITE,
MAP_PRIVATE|MAP_ANONYMOUS|MAP_NORESERVE, -1, 0)` (`r101a_a1`,
`src/sutram_compiler.asm:462-463`). `MAP_NORESERVE` (0x4000) means no swap space is
reserved and no pages are committed: pages fault in on first touch, zero-filled, one
4 KiB page per fault (demand paging). The arena itself is the same kind of mapping
(`R65_ARENA equ 0x40000000 ; 1 GiB of address space; pages are committed on touch`,
`src/r65_arena.inc:49`; the reserve sequence `r65_t5` at `:59-61` uses the same
`PROT 3` / `MAP 0x4022`).

**Windows.** The runtime's `.alloc` (`win/winrt_blob.asm:168-182`) translates the
flag:

```asm
.alloc:
    ; R124: mmap with MAP_NORESERVE (0x4000: the arena, each kosh region) only reserves; rt_veh commits
    ; a page's 64 KiB when it is first touched, as Linux does. Anything else is reserved and committed.
    xor ecx,ecx
    mov rdx,r14
    mov r8d,0x3000
    test r10d,0x4000
    jz .alloc_go
    mov r8d,0x2000
.alloc_go:
    mov r9d,4
    call qword [rbx+RT_VirtualAlloc]
```

i.e. a `MAP_NORESERVE` mapping becomes `VirtualAlloc(NULL, len, MEM_RESERVE,
PAGE_READWRITE)` — address space only, 0 committed. Anything else gets
`MEM_COMMIT|MEM_RESERVE` (0x3000). The lazy commit is the vectored handler `rt_veh`
(`:257-292`):

```asm
; rt_veh (a vectored exception handler, R124): an access violation inside memory this program only reserved
; (MEM_RESERVE, MEM_PRIVATE, not this thread's stack) commits up to 64 KiB there, read-write, and the faulting
; instruction runs again. A failed commit is fatal OOM, with a diagnostic and exit 1;
; it cannot return to an allocation call because that reservation already succeeded.
...
    cmp dword [rsp+48+32],0x2000  ; State = MEM_RESERVE
    jne .v_search
    cmp dword [rsp+48+40],0x20000 ; Type = MEM_PRIVATE
    jne .v_search
    mov rdx,[rsp+48+24]           ; RegionSize from this page
    cmp rdx,0x10000
    jbe .v_size
    mov edx,0x10000
.v_size:
    mov rcx,rsi
    and rcx,-4096
    mov r8d,0x1000                ; MEM_COMMIT
    mov r9d,4
    call qword [rbx+RT_VirtualAlloc]
```

So on Windows each first touch commits `min(remaining RegionSize, 64 KiB)` starting
at the faulting page — up to 16 pages per fault. A failed commit is fatal out-of-memory
(diagnostic, exit 1), after first releasing the 64 KiB reserve `rt_init` keeps in hand
(`:25-40`: `mov edx,0x10000 ; mov r8d,0x3000 ; mov r9d,4 ; VirtualAlloc`).

**What one dead big `kosh` actually costs:**

| | Address space | Committed pages |
|---|---|---|
| At region creation | 64 MiB minimum (`max(2 × new_bytes, 64 MiB)` — larger only for a `kosh` past ~4.2 M elements, where the doubling reaches newcap 8,388,608) | **0** on both platforms |
| As it is filled | unchanged | Linux: one 4 KiB page per touched page. Windows: up to 64 KiB per fault. The growth copy loop touches the old elements' pages in the new region, so a region is never 0-committed after its first growth |
| At death (block end, or the last name going out of scope) | **stays** — the whole reservation, never released | **stays** — the touched pages remain resident |

Measured (R169 WS3/WS4, quoted, not re-measured here): a `kosh` grown to 2,000,000
elements (16 MB) keeps 15,680 KB resident and 64 MiB of address space after its
block; a second block adds another ~15,660 KB resident and another 65,536 KB of
address space. At the boundary, one block growing a `kosh` to 4,097 elements adds 68
KB resident and 65,536 KB of address space.

**Quantifying "about a thousand passes, 64 GB".** One dead big `kosh` at the boundary
costs **64 MiB of address space + at most 64 KiB committed** (8,192 elements × 8 bytes
= 65,536 bytes = 16 pages; R169 measured 68 KB resident per block, the extra being the
descriptor and arena rounding). So:

- 1,000 passes at the boundary: **64 GiB of address space** (1,000 × 64 MiB, exactly
  the brief's "64 GB") **+ ~64 MiB committed** (1,000 × ~64 KiB).
- 1,000 passes with fuller koshs cost more committed pages in proportion to the
  elements touched (a 2,000,000-element `kosh` is ~16 MB committed per dead one —
  1,000 of those would be ~16 GB committed, i.e. real memory, not just address space).

Whether the program **fails** at 1,000 passes depends on a virtual-memory limit being
in force. On an unlimited 64-bit Linux process (128 TiB of user address space) 64 GiB
of reserved-but-mostly-untouched address space does not fail by itself — the `mmap`
succeeds and the program goes on. Under a limit (`RLIMIT_AS`, a job/container limit),
the next region `mmap` fails: `r101a_a2` turns the failure into `rax = 0`, and the
grow check (`r127_emit_grow_check`, `src/sutram_compiler.asm:21341-21343`) stops the
program:

```asm
; r127_emit_grow_check: after the allocation of a kosh's new elements (rax = 0 when the memory
; was not given): stop with a message. The descriptor is not touched before this point, so the
; kosh is as it was; the program does not go on with it half-grown (R127, R201).
```

— the grow message is printed and the program exits 1. That is the brief's
"allocation error unrelated to real memory": the address space is gone while the
committed pages are a small fraction of it. Two qualifications the brief does not
state: (a) the failure needs the limit — without one, 1,000 passes cost 64 GiB of
address space and ~64 MiB of committed pages and the program continues; (b) each
pass's `kosh` must actually reach 4,097 elements to take a region — a loop creating
small koshs never takes one (those stay in the arena, whose bytes are also never
returned, but that is defects 2–3, not this one).

### 5. The boundary: 4,097 elements. Where is that number in the source, and is it documented anywhere?

**The exact constant and comparison.** `R127_BIG equ 65536`
(`src/r65_arena.inc:571`) — 64 KiB, in **bytes**. The growth path compares the **new
capacity in bytes** against it, twice (`r65_arena.inc:599-604` and `:635`):

```asm
; mov rax,r11 ; shl rax,3 ; mov rcx,[r8+8] ; test rcx,rcx ; jz .notreg
; cmp rax,rcx ; ja .move
...
; cmp rax,R127_BIG ; jae .move
...
; push r8 ; push r9 ; push r11 ; mov rax,r11 ; shl rax,3 ; cmp rax,R127_BIG ; jae .big
```

with the R127 comment stating the rule (`:562-567`):

```asm
; Growth, with r8 = d, r9 = length, r10 = capacity, r11 = the new capacity (newcap * 8 = new):
;   - elements in a region that still has room (new <= [d+8]): the capacity changes, nothing moves;
;   - small (new < R127_BIG) and the elements end at the arena cursor: R65's in-place extension;
;   - else new elements: in the arena when small, else a region of max(2 * new, R101A_REGION)
```

Related constants:

| Constant | Value | Where | Role |
|---|---|---|---|
| `R127_BIG` | 65,536 bytes | `src/r65_arena.inc:571` | the "big" threshold: a growth whose new capacity is ≥ 64 KiB of elements takes a region |
| `R101A_REGION` | `0x04000000` (64 MiB) | `src/sutram_compiler.asm:9104` | the region reservation size (the floor; the reservation is `max(2 × new, R101A_REGION)`, so it exceeds 64 MiB only once a `kosh` passes 4,194,304 elements) |
| `R101A_MAXCAP` | `(R101A_REGION - 40) / 8` = 8,388,603 elements | `src/sutram_compiler.asm:9105` | the old R101A cap (a `kosh` never moved until it passed this); now dead in the growth path — it survives only in the dead byte tables `r101a_e1`/`r107_e1` (`:473, :477`) and the history comment |
| `R128_MAXCAP` | `0x0000010000000000` (2^40 numbers = 8 TiB) | `src/sutram_compiler.asm:21354` | the live cap: a new capacity past this stops with the grow message (`r127_emit_grow`, `:585-596`) |
| `R65_ARENA` | `0x40000000` (1 GiB) | `src/r65_arena.inc:49` | the arena reservation (one `mmap`, `MAP_NORESERVE`, pages on touch) |
| 64 KiB commit chunk | `0x10000` | `win/winrt_blob.asm:285-287` | the vectored handler commits at most 64 KiB per fault |
| 64 KiB OOM reserve | `0x10000` | `win/winrt_blob.asm:30` | the commit `rt_init` keeps in hand for the out-of-memory exit |

**How 65,536 bytes becomes 4,097 elements.** Capacity doubles from 4 (4, 8, 16, …,
4,096, 8,192). The region test is `newcap × 8 >= 65,536`, i.e. `newcap >= 8,192`. The
first growth reaching `newcap` 8,192 is from capacity 4,096 — triggered by the
**4,097th push**. So a `kosh` with ≤ 4,096 elements never has a region; a `kosh` with
≥ 4,097 elements always has one. The number 4,097 itself appears **nowhere** in the
source as a constant: it is a consequence of `R127_BIG` plus the doubling growth, not
a named threshold. (The three `cmp …, 4096` sites in the compiler —
`src/sutram_compiler.asm:8534, 11180, 12158` — are unrelated table-full checks for the
loop-flow, definition, and name tables.)

**Is the boundary documented anywhere?** **Only as "past 64 KiB" (bytes), never as
4,097 elements:**

- Reference §16 (`docs/LANGUAGE-REFERENCE.md:965-970`): "When the `kosh` grows past
  its capacity its elements may move — into the arena while they are small, into a
  region of their own past 64 KiB — and the descriptor is updated, so every name sees
  the move. A region is reserved, not committed (only the pages used cost, on Linux
  and on Windows), and when a `kosh` outgrows it the elements move to a larger one and
  the old region is given back." The descriptor's four fields including `[d+8]` are
  stated just above (`:963-965`, and `:993`).
- Memory-model doc status box (`docs/MEMORY-MODEL.md:7`): "Small elements live in
  the arena; past 64 KiB they get a region (reserved, touched as they grow), and an
  outgrown region is given back." (`:44` and `:197` repeat the growth-release.)
- The books: **nothing**. Neither book contains the word "region", nor "64 KiB", nor
  4096/4097 — the only "4096" in either book is an unrelated `mandapa parimita 4096`
  budget example. A reader of the books cannot learn that a region exists, let alone
  where it starts.
- Comments: `R127_BIG` is named in the R127 comment block, but no comment states the
  element-count consequence (4,097). The R101A history comment
  (`src/sutram_compiler.asm:9090-9102`) states the 64 MiB region and the old cap, not
  the boundary.

**R169 agreement.** R169-00 says: "**The boundary is not 64 KB of data but 4,097
elements**: from there every `kosh` gets its own region" and "`R127_BIG` is compared
with the **new capacity** in bytes, and capacity doubles. So a `kosh` of 4,096 elements
(capacity 4,096, 32 KB) stays in the arena, and the 4,097th push doubles it to 8,192
elements = 65,536 bytes — a region." Its table (4,096 → arena, VmSize +0; 4,097 →
region, VmSize +65,536 KB; 7,500 → region; 8,960 → region) matches the source exactly:
the doubling sequence and the `>= 65,536 bytes` comparison give the same boundary.
**The source agrees with R169.** The brief's "above 4,097 elements" is the one phrasing
that does not: read strictly it means 4,098+, while the source (and R169's
measurement) puts a `kosh` with exactly 4,097 elements already in a region. R169's
form — "the boundary is 4096 elements" (the largest size without a region) / "from
4,097 elements" — is the accurate one.

---

## Task 2 — and the loop-local `kosh`: what are those 16 bytes?

**Short answer: they are not a descriptor slot, not a mark record, not bookkeeping,
and not a separate allocation at all.** The block adds 24 bytes of R82 header (3 extra
qwords: line, liveness slot, generation) to the single descriptor+elements allocation,
and the persistent allocator's 16-byte alignment rounding absorbs 8 of them (the plain
allocation already wastes 8 bytes of padding: 40 → 48). Net observable difference:
**16 bytes per kosh**. There is no per-kosh runtime allocation from the block other
than that 24-byte header enlargement.

### The kosh allocation path — one allocation, descriptor + elements together

A `kosh temp[1]` declaration is compiled at `src/sutram_compiler.asm:19311-19365`:

- Capacity comes from the AST decl's `[rbx+24]` expression; the default capacity is 4
  (parser `.ps_kosh_default_cap` builds `AST_NUM 4`, `:15038-15043`).
- Size computation, `:19311-19323`:
  - `:19311` — `add rax,4`: "2 header qwords + R127's elements pointer and region
    size".
  - `:19315-19320` — if `r82_on` is set, `add rax,7` instead: "R82: 5 - line,
    liveness slot, generation, length, capacity".
  - `:19323` — `shl rax,3` (×8).
  - So the requested bytes are `(cap+4)*8` plain, `(cap+7)*8` with R82 on.
- `:19331` — `call r108_kosh_alloc`. `r101a_emit_kosh_alloc` (`:9122`) is just
  `jmp emit_nirmmita_from_rax` — "R127: no region - the descriptor and its first
  elements are one ordinary allocation; growth moves the elements, not it". The region
  code below the jump is dead.
- `emit_nirmmita_from_rax` (`:26702`) → `r65_emit_nirm` (`src/r65_arena.inc:245`).
  Its comment (`src/r65_arena.inc:235-244`) states the layout rule:
  `cur = align16(cur + size)`. The rounding bytes are `r69_n7`
  (`src/r65_arena.inc:92`): `lea rax,[rdx+rsi+15]; and rax,-16`.
- Header writes, `:19331-19365`: the plain path writes `[rax]=0` (length) and
  `[rax+8]=cap` (capacity), then `add rax,16` → user pointer `d`; `r127_dk` (`:574`,
  emitted at `:19365`) writes `[d]` = elements address (immediately after the
  descriptor) and `[d+8] = 0` (region size 0: elements in the arena). The R82 path
  calls `r82_emit_kosh_header` (`:19337`; `:10847-10849` comment): writes `[rax]` line,
  `[rax+8]` slot address or 0, `[rax+16]` generation or 0, `[rax+24]` 0, `[rax+32]`
  cap, then `rax += 40` (5 qwords). Plus the 2 descriptor qwords = 7 qwords / 56 bytes
  total.

So the descriptor is **4 qwords / 32 bytes plain** (length at d-16, capacity at d-8,
elements at d, region size at d+8) and **7 qwords / 56 bytes with R82** (the 3 extra
qwords are line, liveness slot, generation). The R82 fields are written once, at
declaration, into the same allocation as the elements — there is no second allocation.

### The 16-byte rounding — why 24 bytes of header shows as 16

For `kosh temp[1]` (cap 1):

| | requested bytes | cursor advance (align16) |
|---|---|---|
| plain | (1+4)×8 = **40** | align16(40) = **48** |
| R82 on | (1+7)×8 = **64** | align16(64) = **64** |

The R82 header adds 24 raw bytes, but 8 of them are absorbed by alignment padding the
plain allocation already pays (40 → 48 wastes 8). Net: **64 − 48 = 16**.

For `mala m[8]`: `.gs_decl_array` (`:19389-19421`) does `add rax,1` (header slot +
elements), `shl rax,3`, `call emit_nirmmita_from_rax`. (8+1)×8 = 72 → align16 =
**80**. The mala decl never checks `r82_on` and always uses persistent nirmmita, never
scratch — hence 80 bytes, block or not.

No growth happens for the measured programs: the push handler (`:22440+`) emits
`cmp r9,r10` (len vs cap) then `jb.space` — len 0 < cap 1 jumps to the append path,
skipping growth. Growth (`newcap = cap? cap*2: 4`, `call r127_emit_grow` at `:22537`)
only runs when len == cap.

### Why the block adds the header: R82 is a per-program flag, not per-kosh

`r82_note_kosh_decl` (`:10662`): "a kosh declared at parse depth > 0". It checks
`r72_mdepth` (mandapa nesting depth while parsing, `:1682`); if > 0 it sets `r82_on =
1` (`:1713`) and `r82_need[depth] = 1`. Called from the kosh-decl parser (`:15008`).
Because `r82_on` is a single program-wide flag checked at **every** kosh decl
(`:19315`), once ANY kosh in the program is declared inside a `mandapa`, EVERY kosh
in the program gets the 7-qword (56-byte) header. This matches Claude's k1/k2
observation (48 alone, 64 when the program also makes one in a block).

### Block entry — what a `mandapa` sets up (no per-kosh heap allocation)

Parse: a `mandapa` becomes
`AST_BLOCK [ vitti 0mNN = <scratch cursor>; <body>; <rewind to 0mNN>]`
(`:8320-8328` comment). `0mNN` is a hidden local, one per nesting depth (mark names
`r73_mark_names` "0m01".."0m32" at `:750`; `r73_marks resq 33` at `:1683`). The mark is
a stack-slot variable holding the scratch cursor's value at entry; the mark node is
`AST_SCRCUR` (`:8370`; codegen `r73_gen_scrcur`, called at `:21498`).

`r82_block_enter` (`:10703`): on mandapa entry at codegen, if `r82_on` and the block
carries `R82_MAGIC`: increments `r82_gdepth`, allocates **ONE stack slot** for the
liveness slot (`stack_dep += 8`, recorded in `r82_off[depth]`, `:10720-10730`;
`r82_off resq 64` at `:1720`, `r82_line resq 64` at `:1721`), records the line, emits
`rdtsc` + shifts/or to build the generation and stores it into the slot (`:10740-10760`).
The slot is on the **stack**, per mandapa depth, not per kosh, not heap. Nothing else is
allocated at block entry for a kosh.

`r108_kosh_alloc` (`:12655+`): "A kosh declared in an open mandapa is only
remembered, so that r108_check_call can refuse to give it to a prakriya that keeps it
(the outlives rule). **No arena slot: reclaiming waits for the descriptor.**" It
records the kosh in the compile-time `r108_bk_name` / `r108_bk_node` / `r108_bk_gd`
arrays (max 256 entries, `:1605-1607`; `r108_full` refuses when full) and jumps to
`r101a_emit_kosh_alloc`. The call-site comment at `:19331` ("in a mandapa, a slot of
the block's arena") is stale — contradicted by the `r108_kosh_alloc` comment.

### Block exit — what is rewound, what is restored, what is left behind

`r82_block_leave` (`:10799+`):
- Pops the `r108_bk_*` entries whose recorded depth is ≥ the leaving depth
  (`:10800-10810`, comment: "R108: the kosh it made are gone with it") — the
  compile-time record is dropped, the storage is not touched.
- Zeroes the liveness slot (`r82_emit_zero`, `:10778`: `mov qword [rbp+slot], 0`),
  clears `r82_off[depth]`, decrements `r82_gdepth`.
- `r82_gen_rewind` (`:10820+`) zeroes the slots of the blocks being left.

The block's `AST_REWIND` is compiled by `r73_gen_rewind` (`src/r65_arena.inc:404`):
it evaluates the mark and emits `mov [end], mark` (`r56_emit_global_store`, `:412`) —
it restores the **scratch cursor's `end`** to the entry mark. It reclaims scratch-side
allocations only. The kosh descriptor+elements are on the **persistent** side
(ordinary nirmmita), so the rewind never touches them.

`nirmmita` written inside a mandapa takes the scratch side (`r73_gen_scratch_nirm`,
`src/r65_arena.inc:423`: grows down from `end`, rounded to 16, zeroed) — hence
`nirmmita` in a block is flat at 312 KB. A `kosh` never takes the scratch side.

### The leak mechanism, in one paragraph

The persistent cursor only moves forward (`cur = align16(cur + size)`). Nothing at
block exit, function exit, or anywhere else frees a kosh's descriptor+elements: the
only `munmap` in the compiler is on growth (the old region is released when a kosh
grows into a new region). The block exit drops the compile-time record (`r108_bk_*`),
zeroes the runtime liveness slot, and rewinds the scratch cursor — none of which
touches the persistent allocation. So each pass's 48 / 64 / 80 bytes are permanently
held for the life of the program.

### Numbers check against the brief

| program | computed from code | brief | `parimana()` (R168) |
|---|---|---|---|
| `kosh temp[1]`, no block | align16((1+4)×8) = 48 | 48 | exactly 48/pass |
| same, in a `mandapa` | align16((1+7)×8) = 64 | 64 | exactly 64/pass |
| `mala m[8]`, either | align16((8+1)×8) = 80 | 80 | 80/pass (64,000,000 at 800k) |

All three of the brief's per-pass numbers reproduce exactly from the code. At 800,000
passes: 800,000 × 48 = 38,400,000 bytes = 37,500 KiB (brief's "37.5 MB");
800,000 × 64 = 51,200,000 bytes = 50,000 KiB ("50 MB"); 800,000 × 80 = 64,000,000
bytes = 62,500 KiB ("62 MB"). **The numbers add up. Nothing is unaccounted for.**

The 16 bytes are therefore: **24 bytes of R82 header (line + liveness slot +
generation) minus 8 bytes of alignment padding the plain allocation already pays.**
There is no descriptor slot, no mark record, and no per-kosh bookkeeping allocated by
the block — the block's only per-kosh effect is enlarging the one descriptor+elements
allocation by 3 qwords, via the program-wide `r82_on` flag.

---

## Task 3 — and the question I would ask last: what does the compiler actually know?

### `decl_depth`: it does not exist. The equivalent exists, but it is mandapa-only.

Zero hits for `decl_depth` in `src/`, `win/`, `tools/`, `tests/`, `docs/`. What exists
under another name is `r73_var_depth(rdi = name) -> rax = the block depth the name was
declared at (0: before any open block, a parameter, a module vitti, or not declared)`
(`src/sutram_compiler.asm:12450-12452`).

It works from the R4 declaration list (`r4_seen`, `r4_seen_count` at `:1507`; names in
parse order) plus `r73_seenidx` (`:1684`, "R4 declaration count when that block
opened", one entry per mandapa depth). Algorithm (`:12452-12490`): scan `r4_seen` for
the FIRST entry matching the name, then find the deepest open block whose start
precedes that entry (compare against `r73_seenidx[depth]`). Comment at `:8329`:
"`var_depth` the block depth a name was declared at (from the R4 declaration list)".
Its only caller is `:13159`, inside `r73_check_stmt` (the parse-time escape check).

Two limits matter for any design that would reuse it:

1. **It is the mandapa depth (`r72_mdepth`), not the lexical block depth.** A name
   declared in a plain `{ }` block, a loop body, or a `yadi` branch has `var_depth` 0
   — indistinguishable from a function-top-level name, a parameter, or a module
   vitti. The R4 list itself does forget names at every block close (see below), but
   the depth it records is only the mandapa depth.
2. **It returns 0 for "not declared"** — indistinguishable from a parameter or a
   module vitti. And it gives the declaration depth only, never a death point: nothing
   in the compiler computes when a name is last used. There is no liveness / last-use
   analysis anywhere.

### The symbol table is dispersed — there is no single symbol-table entry

What the compiler records per variable lives in separate places:

| fact | where | notes |
|---|---|---|
| name, in parse order | R4 list (`r4_seen`, `r4_seen_count`) | duplicate check via `r7_declare_new` (`:14070`, calls `r4_is_seen`); redeclaration in the same scope is `E_DUPLICATE_NAME` |
| kosh-ness | `kosh_vars` list (`:1548`, cap `KOSH_VAR_CAP` = 256, `:67`) | `mark_kosh_var` (`:27728-27741`) appends the name; `is_kosh_var` (`:29431`) reads it; aliases get the same marking via `r38_mark_alias` (`:27745+`); float koshes in `float_kosh_vars` (`:1560`); raw nirmmita pointers are NOT marked |
| taint (scratch / block-kosh) | `r73_syms` / `r73_symn` / `r73_symbase` (`:1688`: 16-byte entries, name + taint) | `r73_sym_find` (`:12510+`); only names that hold a scratch value or a block kosh are entered |
| block kosh record | `r108_bk_name` / `r108_bk_node` / `r108_bk_gd` (`:1605-1607`, max 256) | name, r82 depth of its block, the decl node; dropped at block exit |
| kind (slice / kosh / mala / number) | computed on demand by `r126_kind` (`:27884`): 1 slice, 2 float kosh, 3 kosh, 4 mala, 5 local, 0 not local | `r126_value_kind` (`:27920`) extends it to expressions; `r126_ret_kind` (`:27978`) to a prakriya's returns |
| declaration depth (mandapa) | `r73_var_depth` (above); per-kosh depth also in the decl node `[rax+40]` (set by `r107_note_kosh` only for koshes in a mandapa) | plain-block depth is not recorded anywhere |
| storage | `alloc_var` (stack slots) | the descriptor address is a runtime value in a stack slot; no record links a name to its allocation |

### Scope entry/exit — what is recorded, what is forgotten

- **Parse:** every block pushes the R4 count on entry (`:8214`, "R7: names declared
  in this block end with it") and restores it at close (`:8395-8397`, via
  `r7_close_block`). A mandapa additionally records the count in
  `r73_seenidx[depth]` (`:8357-8358`) and increments `r72_mdepth`.
  `r73_func_enter` / `r73_func_leave` (`:12375+`): "A prakriya is its own region: its
  blocks start at depth 1, its loops are its own, its names its own."
- **Codegen:** `gen_block` (`:18852`) just iterates the block's statements; the mark
  store and the rewind are ordinary statements in the block node. Returns and
  `krama`/`agrim` jumps rewind via `r73_ret_mark` (`:8422`: inside a block, a return
  rewinds to the outermost block's mark, depth 1's mark) and `r73_wrap_jump`
  (`:8447+`: a jump leaving blocks inside its loop rewinds to the outermost of them).
  Both rewind the scratch cursor only.
- **Forgotten at block exit:** the name (R4 truncation), the block-kosh record
  (`r108_bk_*` pop in `r82_block_leave`), the liveness slot (zeroed). **Never recorded
  at all:** a (name → storage) link, a death point, a last use, a live-reference count.

### What the compiler knows at each decision point

**Declaration.** The compiler knows the name, its kosh-ness, its capacity expression,
and (for a kosh in a mandapa) its mandapa depth and taint (`r107_note_kosh`, `:12615`:
gives the name the block's depth as its R73 taint via `r73_sym_set`, records the name
in `r107_knames` — max 256, `:1610` — and the depth in the decl node `[rax+40]`). A
kosh declared OUTSIDE any mandapa gets nothing: no taint, no name recorded. The
compiler does **not** know, at declaration, whether the kosh will escape, how long it
will live, or whether it will ever be used again after its first use.

**Block exit.** The compiler knows the names declared in the block end here (R4
truncation) and that the block's koshes are no longer usable by name. It does **not**
know whether any storage is still reachable: it holds no record linking the names to
their allocations, and the persistent allocation is not mentioned in any exit code.
The scratch rewind is the only reclamation, and it is defined over the scratch cursor,
not over names.

**Return.** Three separate doors, and none of them is a lifetime decision:
- Parse-time `r73_check_stmt` (`:13123`, `:13148`): a tainted (scratch / block-kosh)
  value on return is refused (`r73_fail_ret`, `:12362`).
- `r126_check_return` (`:29377`, called at `:20957`): inside a prakriya, what a
  `nivartanam` gives must be what the callers were told it returns (`r126_ret_kind`):
  a `siddhi`/`dosh` phal result holding a kosh is refused; a plain return whose value
  kind is 2/3/6 (kosh kinds) and does not match the declared return kind is refused;
  kind 6 (mixed/uncertain) is refused even when the kinds match.
- The walk `r137_check_stmt` (`:28454`) has **no `AST_RETURN` door** (no `AST_RETURN`
  in `:28454-29200`): the return doors are r126 and r73, not the walk.
- What the compiler **does** know here: `r126_ret_kind` is computed once per prakriya
  from its AST ("5 a number, 2 / 3 a kosh (every nivartanam returns a kosh parameter or
  a kosh the prakriya declares, by its own name), 6 they disagree", `:27978`), so a
  kosh that leaves via a return is a known escape — the compiler knows it is alive in
  the caller. A scope-based reclaimer would have to consult `r126_ret_kind`; the
  compiler's own return machinery already does.

**Call argument.** Four doors, each covering a different class:
- `r108_check_call` (`:12767`): only for koshes of an OPEN block (`r108_bk_of`); an
  argument that is such a kosh may go only to a parameter that does not keep it
  (`r108_esc`); to an unknown callee, not at all. The escape bytes come from
  `r108_compute_esc` (`:12811+`): a greatest fixpoint over every prakriya and
  parameter (first six), each starting as "does not keep" and marked when some use of
  it is not a read, a kosh builtin's own operand, or an argument to a parameter that
  does not keep; `r108_param_kept` (`:12878+`) walks the callee body with an explicit
  stack (65536 entries; overflow sets `r108_ovf` = 1, which forces "keeps" — fails
  closed).
- `r126_check_untyped_arg` (`:29343`): a kosh to a parameter that is not declared
  kosh is refused (the prakriya would index it as raw memory).
- `r126_check_builtin` (`:29279`): a kosh is the first argument of a kosh builtin,
  nothing else.
- The FFI door (`src/r32_ffi.inc:680-755`): a value that holds a kosh — a slice of
  one, a call or `?:` giving one, a name holding a slice — does not go to C; **a kosh
  by its own name still does (as its elements, for ptr; refused below for i64 and
  f64)**. The walk leaves kosh values at an argument to this door (r137 `.num`,
  r10 = 1).
- The walk's `.funcall` door (`:28532+`): a slice only to a `vibhag` parameter.
- The other doors (`r126_check_assign` `:29223`: "a kosh goes into no cell, field or
  global"; `r126_check_writemem` `:29317`: a kosh is neither the address nor the
  value; the walk's `.binop` / `.num` doors `:28560-28700`: neither a slice nor a
  kosh is a number) close the remaining exits. A plain kosh cannot be stored, returned
  undeclared, passed to an untyped parameter, or used as a number. **A function-scope
  kosh passed to a keeping prakriya is not checked by `r108_check_call`** — it only
  checks koshes of open blocks — but that is not an escape from the function: the
  callee's keeping uses are themselves refused by the doors above, except aliasing
  (`vitti a = p` is allowed by the walk and counted as keeping by the fixpoint).

### Example 1 — dead, but the compiler cannot know

Program (R168 program C shape):

```
kosh temp[1]
chakra i = 1 tak 800000 {
    kosh temp[1]
    kosh_kship(temp, i)
    total = total + temp[0]
}
```

Trace through the code:

1. **Parse.** `temp` is declared in the loop body. It is entered in the R4 list,
   marked in `kosh_vars`, and — because the loop body is not a mandapa
   (`r72_mdepth` = 0) — `r107_note_kosh` does nothing: no taint, no `r107_knames`
   entry. `r73_var_depth` returns **0** for it, the same value it returns for a
   function-top-level name, a parameter, or an undeclared name. At the loop body's
   close the R4 list is truncated (`:8214` / `:8395-8397`): the compiler knows the name
   ends with the block.
2. **Codegen.** Each pass emits one persistent allocation of 48 bytes (Task 2 above).
   The descriptor address lives in a stack slot; no record links the name `temp` to
   that allocation, in any table.
3. **The decision point.** After `total = total + temp[0]`, `temp` is dead for the
   rest of the pass, and certainly dead at pass end. But the compiler has no last-use
   analysis, no liveness, and no (name → storage) record. The only fact it holds is
   "the name ends with the block" — which is a fact about the name, not about the
   storage. Nothing at block close, loop end, or function end consults the kosh's
   storage, because nothing recorded it. Even the scope knowledge is insufficient in
   general: `var_depth` is mandapa-only, so for a plain block the compiler cannot
   even say at which depth the name was declared, let alone when it died.
4. **Why it cannot tell.** Knowing a name is gone is not knowing its storage is dead:
   the storage was never recorded as belonging to the name. The only reclamation the
   compiler has — the scratch rewind — is defined over the scratch cursor, and this
   allocation is on the persistent side. A design that freed the kosh at block exit
   would have to invent the (name → storage) link the compiler never built.

### Example 2 — alive, but the compiler would think it dead

Program:

```
videshi prakriya c_keep(ptr p)   ; foreign function, ptr parameter
prakriya main() {
    kosh k[4]
    kosh_kship(k, 42)
    c_keep(k)          ; k passed by its own name to a foreign ptr parameter
}                      ; k's scope ends here; the compiler thinks k is dead
```

Trace through the code:

1. **The FFI door** (`src/r32_ffi.inc:680-755`) explicitly lets a kosh by its own name
   through: "A kosh by its own name still does (as its elements, for ptr; refused
   below for i64 and f64)." For each argument: if it is an `AST_VAR` and
   `is_kosh_var` (`:29431`), it skips the `r134_holds_kosh` door (`.r152_open`); any
   other kosh-holding value (a slice of one, a call or `?:` giving one) is refused.
2. **What C receives.** At `.ptr` (`:740-755`): `gen_expr` then `mov rax,[rax]` —
   "R127: a kosh passes its elements, not its descriptor". C receives the **elements
   address** (the `[d]` word), not the descriptor. For a grown kosh this is the
   current elements address, since `[d]` always points at the current elements.
3. **What C may do.** The foreign function may keep that address — store it in
   C-side state, hand it to another thread, read it after `main` returns. The compiler
   has no record of this: `r108_compute_esc` covers only prakriyas of this program
   (foreign functions are not in `func_defs`, and `r108_check_call` refuses a block
   kosh to an unknown callee — but `k` here is a function-scope kosh, so no check
   applies at all). There is no escape byte, no taint, and no (name → foreign holder)
   record for it.
4. **The decision point.** At the end of `main`, the compiler's model says `k` is
   dead: the name ends with the function (R4 truncation), the liveness slot (if any)
   is zeroed, no live reference to `k` exists in the AST. But C still holds `k`'s
   elements address. A scope-based reclaimer that freed the descriptor+elements at
   scope exit would hand C a dangling pointer — and the compiler could not tell,
   because the FFI door is a deliberate, documented permission ("a kosh by its own
   name still does"), not an oversight. Any lifetime design must treat "passed to C
   as a pointer" as an escape the compiler cannot bound — the same way it already
   treats a returned kosh (`r126_ret_kind`) as a known escape, except that for C
   there is no `r126_ret_kind` to consult: there is nothing to consult at all.

### Further cases (short list)

- **Inline asm.** R148 shape 14: "needs no check by construction". A program can load
  a kosh's descriptor address in inline asm and keep it; the compiler cannot see it.
  By design, not a defect — but a lifetime design cannot assume asm does not retain.
- **Aliasing is tracked only as names, not as shared storage.** `vitti a = k` and
  `a = k` make `a` a name of the kosh (`r108_note_alias`, `:12680+`, for block koshes;
  `r126_bind`, `:28829`, for kinds). The doors then treat `a` as the kosh. But nothing
  records that `a` and `k` share one allocation — so a design that freed `k`'s storage
  when `k`'s name died, while `a` was still usable, would corrupt `a`. (For block
  koshes the escape check refuses assigning one to an outer variable, so the live
  alias case is confined to the same scope; for function-scope koshes both die with
  the function.)
- **A kosh returned from a function is a known escape, not a hidden one.**
  `r126_ret_kind` (`:27978`) is computed once per prakriya from its AST, and
  `r126_check_return` (`:29377`) allows a kosh return only when the declared return
  kind matches (kind 6, mixed/uncertain, is refused even when matching). So the
  compiler knows a returned kosh is alive in the caller — but a naive scope reclaimer
  that freed everything declared in the function at its end would still kill it. The
  knowledge exists; a design must use it.
- **The caps fail closed, not open.** `r108_bk_*` and `r107_knames` hold 256 entries;
  overflow refuses (`r108_full`). The walk's budget (default 200,000 steps) refuses
  when exhausted (`r137_check_stmt`, `.walked` / `.exhausted`). The fixpoint's stack
  overflow forces "keeps" (`r108_ovf`). None of these is a case where the compiler
  wrongly thinks a kosh dead.

---

## Brief corrections

1. **Task 1, question 2 — the premise is false.** The address **is** recorded (as
   `[d]`, the elements pointer = the region base) and the size **is** recorded (as
   `[d+8]`). Freeing at death is not blocked by missing bookkeeping: the growth path
   already frees the old region with exactly the two words a death-free would need.
   What is missing is a decision point (knowledge of death — Task 3) and the aliasing
   guarantee. The non-release is also a documented decision (reference §19), not an
   oversight.
2. **Task 1, question 5 — "above 4,097 elements" is off by one element read
   strictly.** A `kosh` with exactly 4,097 elements already has a region; the largest
   size without one is 4,096. R169's form — "the boundary is 4096 elements" / "from
   4,097 elements" — is the accurate one.
3. **Shared state — "81 gates" is right as a total, and the status line is still wrong
   by one.** At this base `tools/gates.sh` has 78 `run_gate` invocations (77 at R159
   + the new "R167 evidence manifests" gate, commit `e5088fe2`). Total entries = 78 +
   1 X11 GUI protocol + 1 doc-counts (counted as a pass) + 1 Windows-execution skip =
   **81** — so "81 gates" as a total is right. But the reference status line says
   "gates **81 PASS / 0 FAIL / 1 NOT-RUN**" (82 entries); max PASS with a display is
   78 + 1 + 1 = **80**. This is the same off-by-one as R159 finding P4, one gate
   higher. The status line should read "80 PASS / 0 FAIL / 1 NOT-RUN".

## Could not determine from source

- Whether the brief's "fails after about a thousand passes" has been observed on any
  machine: the arithmetic (1,000 × 64 MiB = 64 GiB of address space) is exact, and the
  failure path (region `mmap` fails → grow message → exit 1) is in the source — but
  no run in the tree demonstrates the failure at ~1,000 passes, and on an unlimited
  64-bit process it would not fail from address space alone. The limit in force (if
  any) is not recorded in the tree.
- How many virtual-memory mappings a long-running program accumulates besides the
  regions (the arena, the per-call `nirmmita` fallback mappings after the arena
  fills, the descriptor blocks) and at what count the mapping limit binds — the source
  does not state a limit, and no run in the tree measures it.
- Whether the Windows lazy-commit behaviour matches the Linux one at the boundary in
  practice (the calls are read, not measured — R169 says so itself: "Windows — not
  needed, not run").
- The exact committed-pages figure for a dead `kosh` of a given size on Windows: the
  handler commits up to 64 KiB per fault starting at the faulting page, so the
  committed total depends on the touch pattern (sequential fills commit in 64 KiB
  chunks; sparse touches commit less). The Linux figure (one 4 KiB page per touched
  page) is exact; the Windows figure is an upper bound per fault, not a measured
  total.
- Whether any `kosh` can reach a region by a path other than `kosh_kship` growth:
  `r127_emit_grow` has exactly one caller (the push path), and creation never takes a
  region — but a `kosh` declared with a large capacity (e.g. 5,000) starts in the
  arena and takes its region on its first growth past the threshold; no source path
  was found that reserves a region at declaration.
- The `parimana()` accounting for a dead region `kosh`: the reference says
  `parimana()` counts "the arena and the `kosh` regions together", and R169's table
  shows `parimana()` adding 98,368 per 4,097-element block — but whether a dead
  `kosh`'s region stays counted after its block ends was not traced in this task (the
  counting code, `r107_emit_count_rcx`, was read only where the growth path calls it).
- Whether `r108_param_kept` treats a plain index read `k[i]` as a keeping use. Its
  comment (`:12807-12811`) says a parameter is marked as keeping when some use of it
  is "not a read (k[i]), a kosh builtin's own operand, or an argument to a parameter
  that does not keep", but the walk counts `AST_VAR` occurrences (`cnt_all`) and the
  dispatch was not fully read to establish whether an index node has a special case.
  If a read counts as keeping, that fails closed (refuses more) — it would not be a
  soundness hole, only a conservatism question.
- Where the R82 generation is verified at a kosh's use site. The slot's allocation
  (`r82_block_enter`, `:10703`), the generation store (`:10740-10760`), and its
  zeroing on block exit (`r82_block_leave`, `:10799`; `r82_gen_rewind`, `:10820`)
  were traced, but not the read-side check, so nothing is stated here about what a
  use after block exit would do at runtime.
- Whether any program path can produce a kind-6 return that `r126_check_return`
  refuses in practice (a `?:` with a kosh arm gives kind 6 via `r126_value_kind`,
  `:27920`); no live example was traced.
- The exact line of `r73_gen_scrcur` (the mark store); cited by its call site
  (`:21498`) and the `AST_SCRCUR` node creation (`:8370`) instead.

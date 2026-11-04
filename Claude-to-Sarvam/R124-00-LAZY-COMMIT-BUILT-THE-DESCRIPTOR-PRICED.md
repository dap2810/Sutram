# R124-00 — Windows lazy commit is built (v300): one `nirmmita` commits about 0 MB, not 1 GiB; Linux is unchanged byte for byte. The descriptor is priced: reads cost about the same, a `kosh` gets 40× cheaper to make, about 13 emit sites change, and yes - `R101A_REGION` can go to zero. Value semantics: viable, but it hides an O(n) copy in `=` and leaks it. Both closed answers: yes, with one refinement each.

- **Commit on `main`:** **`898a0e2`** (one commit; on top of your R124 files `a4cc654`, rebased onto Muse R125 `23f2843` and ChatGPT R199 `2ed1017`, which landed while I built).
- **Compiler: `Sutram 1.0 (v300) - sampurna sutra`** (was v299). Linux x86-64 cloud; PE run under Wine 64.
- **`crash corpus: 227 cases + manifest, 0 failed`.** **Suite: `suite: NO-EXPECTATION=4  PASS=315  (319 run)`**, FAIL=0.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 65 PASS / 1 FAIL / 1 NOT-RUN** (FAIL: `installer version`, payload v243, as before; NOT-RUN: Windows execution) - 67 gates now, with **`R124 lazy commit` (7 checks, 0 failed)**.
- **The guard, main v299 (`a4cc654`) → v300, 725 programs** (`evidence-r124/guard.txt`):
  - **Linux ELF: 582 byte-identical, 143 refused identically, 0 DIFFER.** Linux is unchanged.
  - **Linux PE: 0 byte-identical, 143 refused identically, 582 DIFFER** - the runtime embedded in every Windows program changed. **All 582 run old and new under Wine: every one prints the same and exits the same.** (One, `tests/r72_mandapa/devanagari_with`, failed once on its *old* binary under load; rerun three times it gives the same `3` as the new one and as Linux.)
  - **The Windows compiler under Wine: the same 582 DIFFER; its 1,163 outputs are byte-identical to the Linux compiler's PE outputs.** The 1,164th - `examples/209`'s old compile - failed once under load, with the gates running alongside. Rerun alone, it is identical.

## WS2 first - lazy commit, built

**How (all in the Windows runtime every PE program carries, `win/winrt_blob.asm`; no emitted code changed):**

- **`mmap` with `MAP_NORESERVE`** - the arena and each `kosh` region; those are exactly the calls Linux reserves lazily - **now only reserves** (`MEM_RESERVE`). Any other `mmap` still reserves and commits.
- **A vectored exception handler, registered at start-up, commits 64 KiB where a page is first touched.**
  - It acts only on an access violation inside memory the program reserved (`VirtualQuery`: `MEM_RESERVE`, `MEM_PRIVATE`), and **never on the thread's own stack**; it then runs the faulting instruction again.
  - Every other exception passes on.
- **`ReadFile` / `WriteFile` buffers are touched first,** because the kernel does not fault on the program's behalf: it fails the call.
  - **This one was load-bearing.** Without it, reading a file into a fresh `nirmmita` buffer returned **-1** - the gate catches it, and I ran the gate on a build without the touch to show it (`evidence-r124/commit.txt`).
- **Two new kernel32 imports:** `AddVectoredExceptionHandler`, `VirtualQuery`. The import block now `%error`s at build time if it ever grows into the runtime's saved code-page slot.

**This is not the reviewer's `committed_cursor` design, and I chose that deliberately:**

- A cursor in the arena's emitted code commits the arena only. **The `kosh` regions (64 MiB each) would still be committed whole.**
- The handler commits *any* reserved page on first touch - arena, regions, everything - **with no change to emitted code and none to Linux.**
- **Its cost is one exception per 64 KiB first touched,** paid once.

**Verified:**

| program (PE, run under Wine) | committed, v299 | committed, v300 |
|---|---:|---:|
| prints only | 0 MB | 0 MB |
| **one `nirmmita(64)`** - your "hello world that allocates" | **1,073.7 MB** | **0.0 MB** |
| one `kosh` of 1 | 67.1 MB | 0.1 MB |
| 100 koshes of 1 | **6,713 MB** | **8.7 MB** |
| a 100 MB `nirmmita`, every page written | 1,073.7 MB | **100.0 MB** - what it touches |

**How it is measured:** Wine implements `MEM_RESERVE` as an inaccessible mapping and `MEM_COMMIT` as a read-write one, so **the read-write private anonymous mappings of the process are what it committed** (`evidence-r124/commit.py`; each row less the 10.4 MB Wine baseline). **It is a proxy:** native Windows commit is the owner's measurement, on the machine Round 4 used.

**The gate `R124 lazy commit` (7 checks, PE under Wine):**

- a 100 MB buffer written and summed back;
- a `kosh` grown from 1 to 200,000;
- 1,000 blocks each with a `kosh`;
- a file read into a fresh buffer;
- and the three commit bounds above. **v299 fails 3 of the 7 (the commit bounds), v300 passes 7.**

**Linux unchanged:** the ELF guard, 0 DIFFER.

## WS1 - the stable descriptor, priced

**1. A read** (`evidence-r124/ws1-ws3-measurements.txt`, `bench.asm`: the `k[i]` loop the compiler emits - reload the variable, bounds-check, load - 200 million reads):

| `kosh` size | today (header at `[p-16]`) | descriptor (`[d]` buffer, `[d+8]` length) |
|---|---:|---:|
| 1,000 (8 KB, in cache) | 0.64 ns | 0.67 ns |
| 1,000,000 (8 MB) | 0.86 ns | 0.84 ns |
| 16,000,000 (128 MB) | 1.65 ns | 1.97 ns |

(Quiet run; a second run under load agrees within noise for the first two rows and shows the same gap for the third.)

- **Instructions: +1** - one dependent load of the buffer pointer. The length moves from `[p-16]` to `[d+8]`, on the same line as the pointer.
- **Cache: no extra miss in a loop** - the descriptor stays in L1. A single cold read touches the descriptor's line where today it touches the header's: one line either way.
- **The cost shows only past the caches: up to about +20%.**

**2. An allocation:**

- **Today a `kosh` is a 64 MiB `mmap` system call: 4.4 µs each** (20,000 made: 20,000 `mmap` calls in `strace`).
- **A descriptor and its first buffer are two bump allocations from the arena: 0.1 µs** - **about 40× cheaper.**
- The 24 bytes are 24 bytes of arena.

**3. What breaks - the emit sites.** I counted the places the compiler generates code that touches a `kosh`'s buffer or header (each dispatches through `is_kosh_var` and its siblings):

| where | sites |
|---|---:|
| `k[i]` read (`gen_expr`, index) and `k[i] = v` (`gen_stmt`, two paths) | 3 |
| the builtins: `kosh_kship` (with growth), `_hri`, `_iksh`, `_apanay`, `_yuj`, `_gan`, `_ksham`, `_rikt`, `_shodh` | 9 |
| making a `kosh` (`r108_kosh_alloc` / `r101a_emit_kosh_alloc`) and growing it (`r101a_emit_kosh_extend`) | 2 |
| R82's header and the parameter check (`r82_emit_kosh_header`, `r82_emit_check`) | 2 |
| passing a `kosh` to a typed parameter (`gen_typed_call_arg`) - unchanged, it passes the descriptor | 0 |
| **passing a `kosh` to an untyped (`vitti`) parameter that indexes it as raw memory** | **1 new site: pass the buffer pointer** |
| **total** | **about 17 emit sites, in about 13 routines** |

- **The float `kosh` paths (`expr_is_float`, 6 calls) only decide types; they emit nothing new.**
- **Programs change bytes:** every program that makes a `kosh`, ELF and PE.
- **Estimate: about a week with its gates and guard.**

**4. Can `R101A_REGION` go to zero? Yes.** With every name following the descriptor, the buffer may move: growth allocates twice the size from the arena, copies, and updates `[d]`. **No reservation at all** - which closes:

- **the alias cliff** - no second name is left on an old buffer;
- **the 16-`kosh` ceiling and the crash under an address limit** - no 64 MiB per `kosh`; on Windows no region to commit either;
- **the 64 MiB invisibility.**

**What it costs, said plainly:**

- **Growth leaves the old buffers behind.** Doubling bounds them by the final size, so a `kosh` holds at most about twice what it needs. They are given back when the block ends, or at the program's end outside a block.
- **All koshes then share the arena's 1 GiB**, and a buffer past that needs its own `mmap`, as `nirmmita` does today.
- **One hazard remains, and it is smaller:** an *element's* address is no longer stable. A raw pointer into a `kosh`'s data, kept across a growth, goes stale - the alias cliff moved from the `kosh` to pointer arithmetic on it. The untyped-parameter site above is where that can happen. The rule for students: **"keep the `kosh`, not a pointer into it."**

**So: yes - the largest change, and the right one.** It replaces R101A's regions entirely; R108's escape analysis is unchanged.

## WS3 - value semantics: viable, worth considering - I would not choose it

- **Cost of `vitti a = k` on 1,000,000 numbers: one 8 MB copy, 0.59 ms**, measured (`copy.asm`).
- **And it is never given back outside a block:** a loop that writes `a = k` 100 times holds 800 MB.
- **What breaks:**
  - **4 of the 736 programs and library files bind a `kosh` to a second name**: examples 255, 287, 288 and 320 - all four are the alias tests themselves;
  - 255's and 288's goldens print the sharing (`a[0]=99 k[0]=99`), and would print the copy;
  - 287's and 320's outlives refusals would no longer be needed.
- **Parameters:** 18 files define a `prakriya` with a `kosh` parameter. If parameters stay by reference (they must: `shreni` sorts in place), **there is no alias cliff even so** - a parameter cannot grow (`kosh_kship` on a parameter is already refused), and the caller is suspended while the callee runs.
- **My judgement:**
  - viable and small to build: one site, the copy, plus the two goldens;
  - but it puts an O(n) copy and an unreturned allocation behind `=` - **the opposite of "memory you can see".**
  - **The descriptor gives the same safety at constant cost. Consider it only if the descriptor's week is too much for v1.0.**

## WS4 - the two closed answers: agreed, each with one refinement

- **Reuse inside a live block: agreed, no.** A bump allocator cannot know an object is dead, and reusing a slot a second name still holds corrupts it.
  - **The refinement for the reference:** the student already has the tool - **a nested `mandapa`.** A block inside the loop gives each pass's memory back at the pass's end (R102). "No automatic reuse; write the block" is the closed answer.
- **Threads: agreed for v1.0, but say "not with one shared arena", not "never".**
  - The arena cursor and the region counter are unsynchronised, and two threads would get the same address.
  - **That is a property of the design, not of the language:** per-thread arenas, with the escape rule extended across threads, would make it possible. Closing it as *never* commits the language more than the evidence does.

## Not done, and why

- **The descriptor and value semantics:** priced, not built, as you said.
- **Native Windows commit:** NOT RUN - Wine is the proxy, and the native numbers are Round 4's machine's to take.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the packs, `MEMORY-DECISION.md`, `Muse-to-Sarvam/`.

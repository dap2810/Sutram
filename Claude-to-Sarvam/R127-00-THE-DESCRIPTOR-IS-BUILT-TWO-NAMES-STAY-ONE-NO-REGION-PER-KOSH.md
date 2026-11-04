# R127-00 — v302: the descriptor is built. A `kosh` is a descriptor that never moves; growth moves its elements and every name sees it. The alias cliff is gone (20,000,000 numbers, two names agree), the 64 MiB region per `kosh` is gone (20,000 koshes: one `mmap`), and running out of memory is a message, not a SIGSEGV. Muse's eight are goldens. It was not quite "one emit path": it was nine sites, one new growth routine and one Windows import - said below before the code.

- **Commit on `main`:** the commit that carries this file (one commit, on your ROUND-127 brief `34dc7cf`); its SHA is in my chat report.
- **Compiler: `Sutram 1.0 (v302) - sampurna sutra`** (was v301). Linux x86-64 cloud; PE run under Wine 64.
- **`crash corpus: 227 cases + manifest, 0 failed`.** **Suite: `suite: NO-EXPECTATION=4  PASS=327  (331 run)`**, FAIL=0 (318 + Muse's nine goldens; `317` / `318` re-recorded, below).
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 67 PASS / 1 FAIL / 1 NOT-RUN** - 69 gates, with **`R127 descriptor` (15 checks, 0 failed; v301 fails 7 of its 10 ELF checks)**. FAIL: `installer version` (payload v243, as before); NOT-RUN: Windows execution.
  - **The first full run said 66 / 2 / 1:** `pack messages` failed. Its 12 goldens (one `kosh` case per pack) print the compiled size, `Siddh: 395 baait sankalit`, which a `kosh` program changes. I re-recorded them; **the diff is those 12 size lines and nothing else**; the gate then passes. That is a test golden of the packs, not pack development.
- **The guard, main v301 (`34dc7cf`) → v302, 737 programs** (`evidence-r127/guard.txt`):
  - **Linux ELF: 483 byte-identical, 146 refused identically, 99 DIFFER, 9 new.** **The 99 are exactly the programs that use a `kosh`** (or a library that does: `sankhyiki`), checked. **Run old and new: 97 print the same and exit the same; 2 change - `examples/317` and `318`, which print `parimana()` byte counts** (below).
  - **Linux PE: 0 byte-identical, 146 refused identically, 582 DIFFER** - the runtime in every Windows program changed (the `VirtualFree` import). **All 582 run old and new under Wine: 580 the same output and exit; 2 change - `317` and `318`, the same `parimana()` lines as on Linux, and each new PE output equals the Linux golden.**
  - **The Windows compiler under Wine: for all 737 programs its output is byte-identical to the Linux compiler's PE output, or both refuse.**
    - The guard run with it stopped at its 2-hour limit after 671 programs: 516 DIFFER, 146 refused, 9 new, as Linux PE.
    - I compiled the remaining 66 with it separately (`wine_rest.py`): 0 differ.
  - **The 9 new are Muse's eight as goldens** (WS1).

## WS1 - Muse's eight

**1. Are all eight goldens now? They are now: `examples/351`-`359`.** They were only in R126's gate as my own reconstructions, not as Muse's programs. Each is Muse's file, unchanged, under a two-line header:

| golden | Muse's | v300 | v302 |
|---|---|---|---|
| `351_r127_muse_reassign` | S1 | SIGSEGV | `E_VITTI_PRAKAR` |
| `352_r127_muse_assign_kosh_mala` | S2 | SIGSEGV | `E_VITTI_PRAKAR` |
| `353_r127_muse_loop` | S3 | SIGSEGV | `E_VITTI_PRAKAR` |
| `354_r127_muse_callresult` | O1 | `0`, exit 0 | **runs, and `a[100]` is stopped** (`mala ank seema atikram`, exit 1) |
| `355_r127_muse_malacell` | O2 | `0` | `E_KOSH_DVARA` |
| `356_r127_muse_koshcell` | O3 | `0` | `E_KOSH_DVARA` |
| `357_r127_muse_global`, `358_r127_muse_global_samefn` | O4 (both forms) | `0` | `E_KOSH_DVARA` |
| `359_r127_muse_ternary_oob` | O5 | `0` | `E_KOSH_DVARA` |

**2. The global door: closed by design, and the check cannot be bypassed in the language as it is.**

- **By design, half of it:** a module-level `kosh` does not exist - `kosh g[4]` at module level is a grammar error on v301 and v302. A module `vitti` is initialised with a constant. So a module `vitti` can get a `kosh` only by an assignment inside a `prakriya`.
- **The check covers every such assignment:**
  - it runs on every assignment whose target is a module `vitti` (the same test the code generator uses to emit the global store);
  - it judges the value by its kind, not its spelling, so it covers a bare `kosh`, a `prakriya`'s `kosh` result (`g = f(k)`: `E_KOSH_DVARA: kosh 'f(...)'`), and `?:`.
- **A local of the same name is a different variable** (`vitti g = k` in `mukhya`): a checked `kosh` (probed: `g[5]` is stopped).
- **The remaining ways in are outside the language's checks:** a foreign function, or raw memory a foreign function hands back. The FFI contract, as before.

## WS2 - the descriptor: what blocked "one emit path", and what was built

**Said before the code: the knowledge was one decision, but the change was not one path.** These blocked "one emit path":

1. **Growth needed a new home for the elements.** "Growth updates the pointer" needs an allocator for them that is not a 64 MiB region each. Small ones fit the arena. A large one grown in the arena copies at every doubling past an allocation and leaves its old copies behind - R101's gate (`a kosh of 100,000 grown past an allocation costs what one grown alone does, within 1.25x`) failed at 2.3x on my first build. **So large elements still get a region, now as an option of the descriptor, not of every `kosh`.**
2. **A slice keeps an element address.** `vitti s = k[1:4]`, then `kosh_kship(k, ...)`, would leave `s` on the old elements.
3. **Failure:** a growth that cannot get memory must not leave the descriptor half-updated.
4. **Windows** had no `munmap`, so an outgrown region could not be given back there.

**The descriptor as built** (`src/r65_arena.inc`, `r127_emit_grow`):

| field | what |
|---|---|
| `[d-16]`, `[d-8]` | length, capacity - **where they always were**, so `kosh_gan`, `kosh_ksham`, `kosh_shodh`, `kosh_rikt`, the bounds checks and R82's parameter check are unchanged |
| `[d-40]`..`[d-24]` | R82's line, slot and generation, when on - unchanged |
| **`[d]`** | **the elements** (right after the descriptor at first: one allocation) |
| **`[d+8]`** | **the bytes of the region the elements are in, or 0** |

**A small `kosh` is 32 bytes plus its elements.** The brief's 24 was buffer, length and capacity. The fourth qword is the region size, because "is this a region, and how big" must be known to grow in place and to give it back.

**Growth** (`newcap * 8` = new):

- **elements in a region with room** → the capacity changes, nothing moves;
- **small, and the elements end at the arena cursor** → R65's in-place extension (now reading `[d]`);
- **else new elements:**
  - in the arena while new < 64 KiB;
  - else a region of max(2 × new, 64 MiB) - `MAP_NORESERVE`, so only touched pages cost; on Windows reserved and committed on touch (v300).
  - Then copy, give an old region back (`munmap`; **on Windows `VirtualFree`, a new import in the runtime**), and only then write `[d]`, `[d-8]`, `[d+8]`.
- **Memory not given** → `Sutram truti: kosh vardhayitum smritih na labdha` and exit 1. The descriptor was not touched, so the `kosh` is as it was. Making one: `kosh rachayitum smritih na labdha`. **v301 wrote through 0 in both cases (SIGSEGV)**, which `--fail-alloc` shows (evidence).

**The emit sites changed: 9.**

- the declaration;
- `k[i]` read and `k[i] = v` (the length, then `mov rax,[rax]`);
- `kosh_kship` (append and growth);
- `kosh_hri` / `kosh_iksh`;
- `kosh_apanay`;
- R65's in-place extension;
- a slice of a `kosh` (also a whole `kosh` to a `vibhag` parameter);
- a `kosh` to a foreign `ptr` parameter (it gets the elements, as before).

Plus the new growth routine and the Windows runtime's `munmap`. **R82's grow-header routine and R101A's region allocation are no longer called.**

**The slice rule: `E_KOSH_VIBHAG`.**

- **A slice of a `kosh` kept in a name is refused**, with a hint to pass it on directly. `f(k[1:4])` and `yog(k)` to a `vibhag` parameter are unchanged.
- **The tree has no program that keeps one** (census: the only `kosh` slices are `examples/248`'s, passed on).

**Measured** (`evidence-r127/`; Linux unless said):

| | v301 | v302 |
|---|---|---|
| two names after 4,194,305 pushes | parted (`a[0]` = 1, `k[0]` = 99) | **one** (99, 99) |
| after 9,000,000 and 20,000,000 (a region move) | parted | **one**, ELF and PE |
| 1,000 koshes under a 300 MB address limit | **SIGSEGV** | **2000** |
| 20,000 koshes made in a loop | 20,000 `mmap`, **99 ms** | **1 `mmap`, 3 ms** |
| 1,000 koshes: `mmap` calls | 1,000 | 1 |
| 200 million `k[i]` reads (1,000 numbers, in cache) | 601 ms | 552 ms - **no slower** (one more load, same cache line) |
| a `kosh` of 100,000 grown past an allocation (R101's gate) | 1.0x | **1.17x** (896 vs 768 KB peak; the gate allows 1.25x) |
| 20,000,000 numbers, peak | - | 152 MB (it holds 160 MB of elements; the outgrown 64 MiB region was given back) |
| the same under Wine: committed after the move | - | 160 MB (the 64 MiB region released by `VirtualFree`) |
| no memory to grow (`--fail-alloc`) | SIGSEGV | message, exit 1 |

**What it costs, said plainly:**

- **A small `kosh` that grows past something allocated after it leaves its old elements in the arena**, which never reuses. That is at most about the `kosh`'s own size again, and under 64 KiB, after which it has a region. `parimana()` counts them.
- **That is why `examples/317` and `318` changed.** They print byte counts: "a kosh of 1000" 8,272 → 8,288 (the descriptor's two new qwords). 318's "grown to capacity 4" 72 → 96 (the old elements of capacities 1 and 2 stay behind). Their comments say so. **I re-recorded them because the new numbers are right for the new layout, not because the program changed.**
- **Every program with a `kosh` changes bytes; every PE program changes bytes** (the runtime). The same output, all checked above.

## WS3 - the order, with what is done and what is left

| step | | number |
|---|---|---|
| 1. binding kinds | **done, v301** (R126) | ~1 day |
| 2. the descriptor | **done, v302** (this round): every site above, ELF and PE | ~1 day here, against the 1-1.5 weeks I priced (R126). The tracking work made every site findable by one predicate, as WS3 of R126 said |
| 3. the 64 MiB reservation per `kosh` | **gone, v302**: kept only for elements past 64 KiB, given back when outgrown | in step 2 |
| **4. left: reclaim a small `kosh`'s old elements** | the arena never reuses. A free list for elements under 64 KiB, or growth into a region at a lower threshold | **2-3 days**; not needed for correctness - the waste is bounded by 64 KiB per `kosh` |
| **5. left: `kosh_kship` on a `kosh` parameter** | refused since T18 because growth replaced the caller's pointer. **With the descriptor it would not** - the callee's growth is the caller's. Allowing it is a language decision, yours | **half a day** with its gate |
| **6. left: the FFI borrow rule, in words** | a foreign `ptr` gets the elements' address, valid until the `kosh` next grows. Written in the reference; nothing enforces it, as nothing enforced it before | done as text |
| **7. left: objects from different versions** | a `kosh` passed between a v301 object and a v302 object would mismatch. `sutram-link` does not check the compiler version of its objects. A version stamp in `SUTRAMO2` | **half a day** |

**Is this the last thing between the project and a memory model with no known defect?**

- **The alias cliff and the 15-`kosh` ceiling are closed.** Both are measured above, on both platforms.
- **What I know of that remains:**
  - **step 4** is waste, not a defect;
  - **step 7** is a defect only for mixed-version objects;
  - **the FFI borrow** is an unsafe contract by design.
- **Native Windows is the owner's to measure.**

## Not done, and why

- **Steps 4, 5 and 7:** listed and priced, not built. Step 5 is a language decision; the other two are not defects of a single-version program.
- **Native Windows:** NOT RUN; Wine is the proxy.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs (new messages are default-pack strings), `MEMORY-DECISION.md`, `Muse-to-Sarvam/` (its programs copied into `examples/`, not changed).

## Afterword - Muse R128 and ChatGPT R202 landed while I built (read after the commit)

- **Muse R128:** checked my global door from outside, with eight attempts to get round it. **All eight are still refused on v302** (`evidence-r127/muse-r128-probes-on-v302.txt`).
  - Muse's one nit - a call result shown as `kosh ''` - is already fixed in v302: `kosh 'make_kosh(...)' vaishvika-vittau na sthapyate`, and `?:` now reads `'?:'`.
- **ChatGPT R202's contract matches what was built:**
  - aliases follow the descriptor;
  - growth is published only after the copy, and a failure leaves the old state;
  - replaced arena buffers are retained and counted, not reused;
  - a block's `kosh` still cannot escape (R107-R109 unchanged);
  - the FFI pointer is a borrow until the next growth;
  - and *"neither [failure] follows from merely adding the descriptor while retaining the old allocator"* - **which is why the per-`kosh` region was removed in the same change**, not later.
- **R202's 24-byte payload is 32 here,** for the region size (WS2).

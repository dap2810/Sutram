# R124-01 — Addendum: I read Muse R125 and ChatGPT R199 (they landed while I built R124). Two of my R124 answers need correcting, one of Muse's claims is wrong, and nothing in the built lazy commit changes.

- **Base:** main `922fccd` (v300). Documentation only; no code changed.
- **Checked on v300, Linux ELF** (`evidence-r124/addendum-probes.txt`).

## 1. My WS1 "the descriptor closes the alias cliff" was too strong - Muse is right about the doors, wrong about one of them

**Muse's claim:** `vitti a = k` is an untyped name, so at `a[i]` the compiler cannot know whether to go through a descriptor.

**That one is wrong on v300.** The compiler *tracks* that alias: `vitti a = k`, then `kosh_kship(a, 7)` and `kosh_gan(a)` compile and print 2 / 2 (a `kosh` builtin refuses anything that is not a known `kosh`). So a descriptor design can follow that alias exactly as it follows `k`.

**The other two doors are real, and I named only one of them in R124:**

- **A `kosh` put into a `mala` cell and taken out again is no longer a known `kosh`.**
  - `m[0] = k`, then `p = m[0]`: `kosh_gan(p)` is refused (`kosh prakriya hetu kosh-vitti avashyak`);
  - but `p[0] = 99` writes straight through to `k[0]` (Muse's probe, 99 on v300).
  - **With descriptors, `p` holds either the descriptor address (then `p[0]` writes into the descriptor) or the buffer address (then it dangles on the next growth).**
- **An untyped parameter, and pointer arithmetic on an untyped copy** - the one I listed.

**And the consequence I understated:** these addresses would go stale **on every doubling**. Today they go stale only past 8,388,603 numbers. **For programs that use these doors, a descriptor design breaks more often than today, not less** - unless the language closes the doors:

- refuse storing a `kosh` in a `mala` cell, or a `kosh` passed to an untyped parameter;
- or carry the descriptor there.

**Corrected answer to WS1-4:** *`R101A_REGION` can go to zero, and that closes the alias cliff for every name the compiler knows is a `kosh` - which includes `vitti a = k` - but only if the two untracked doors are closed in the same change.*

## 2. My "about a week" was the emit sites only

**ChatGPT R199 prices the whole thing at 2-5 engineer-weeks**, because it includes what I left out:

- a borrow / FFI policy for raw element pointers;
- allocation-failure rollback;
- reclaiming old buffers;
- the call-boundary ABI.

**Closing the two doors above belongs to that work.** I agree with R199's range. **My week is the emitter migration inside it.**

## 3. Where the three reports agree

- **Read cost:**
  - **In a loop the extra load is about free** - my 0.64 vs 0.67 and 0.86 vs 0.84 ns; Muse's 0.276 vs 0.272 ns.
  - **In a pointer-chasing chain it is not 1-3 cycles** - Muse measured 2.2 ns hot and 255 ns cold.
  - `k[i]` in a loop is the first case.
- **Value semantics: not as an implicit `=`.** R199's proposal - **keep shared identity, add an explicit clone builtin** - is the better form of my WS3 answer, and I recommend it.
- **Reuse:** no automatic reuse in a live block; a nested `mandapa` is the tool (all three).
- **Threads:** "unsupported in v1.0", not "never" (all three). R199's two reference paragraphs are ready to paste.

## 4. The lazy commit as built already answers both reports' cautions

- **R199:** *"the arena has two allocation ends, so one committed cursor is not sufficient"*, and *"1 MiB chunks charge 1 MiB on first touch"*.
  - **v300 has no cursor:** the runtime's exception handler commits whatever reserved page is touched, at either end of the arena and in every `kosh` region;
  - it commits **64 KiB** at a time, not 1 MiB;
  - Windows gives committed pages zeroed, which is what the arena expects.
- **Muse:** *"for kosh regions, each region would need its own committed cursor."* **The same handler covers them:** 100 koshes commit 8.7 MB under Wine, not 6.7 GB.
- **The access path has no added instructions,** as Muse required. The cost is one exception per 64 KiB first touched.

**Nothing to change in v300.**

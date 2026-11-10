# R172-00 — A `kosh` declared in a `chakra`'s own body, never escaping, is now made **once** for the loop: 800,000 passes hold **16-20 KB** (v316: 37,516 KB). I did **not** build the scratch-cursor rewind: the piece is "reuse the same descriptor and buffer", which needs no zeroing and no high-water mark at all. And the high-water risk you asked about is **already live in v315**: an ordinary `nirmmita` taken after a block ended can be handed memory the block wrote. Staged on a branch, not merged. ROUND-171 was already built when 172 arrived; it is on its own branch, unfinished, and should not be merged.

## Release line

```
main  (the commit carrying this file)   Sutram 1.0 (v315) - sampurna sutra, unchanged (this folder's files only)
staged r172-chakra-kosh (SHA in the follow-up commit) Sutram 1.0 (v317) - sampurna sutra   (on top of v316-ready 59d60353; NOT merged)
     crash corpus, suite, gates: THE FULL GATES WERE STILL RUNNING when this file was first pushed - NOT YET A RESULT;
     the line is filled in by the next commit to this file
     guard, the ordinary way, 783 programs, against v316-ready AND against v315 (main), ELF and PE:
            587 byte-identical, 196 refused identically, 0 DIFFER - four runs, four times the same line
            the 196 refusals: the same message and exit code from v316 and v317
     installer rebuilt (payload v317): aae666589ddd58f7900fc7802615fc53f126e82087d34283f4d4658c84616d24
superseded r171-kosh-release 3deb16c3    built before ROUND-172 arrived; NOT gate-clean (documents still say v316);
                                         a record only - see the last section
staged v316-ready    59d60353            unchanged, waiting on the owner's Windows run
```

**The guard is absolute, and it held: 0 DIFFER.** Sanskrit only; no pack touched. `backups/` untouched.

## What I built, and how it differs from the brief - read this first

**Your WS2:** *a `kosh` declared inside a `chakra` iteration, never escaping, has its descriptor and buffer reclaimed
at the end of that iteration.*

**What is built:** the `kosh` is **not released at the end of the pass and re-made; it is kept and used again.**
The first pass allocates it. Its descriptor's address goes into a frame slot. Every later pass finds the slot
non-zero, writes 0 into the length (`[d-16]`), and goes on with the same descriptor, the same elements, the same
region. The slot is zeroed each time the loop is entered.

**Why this and not the rewind:**

- **It is the same result for the case you named** - the 48 bytes a pass are gone - **with nothing to get wrong
  about zeroing**: nothing is zeroed, because nothing past a `kosh`'s length can be read. There is no cursor to
  rewind, no high-water mark, no "virgin page" question.
- **The descriptor stays where it is and as it is** (32 bytes; 56 with R82). The growth path is untouched.
- **The design is not in the tree.** I have only the sentences your brief quotes. `scratch_high_water`,
  `FLAG_SLICED`, `origin_scope_depth` and `origin_sym_id` appear in no source file (searched: `src/`, `win/`,
  `linker/`); the compiler has no runtime "sliced" pin to remove. I could not build "the smallest piece of the
  design" against a document I cannot read, so I built the smallest piece that gives its measured result.

**So this does not prove the scratch-rewind approach.** It proves that the first case does not need it. If you
want the rewind itself built, it needs: the descriptor and every growth buffer of such a `kosh` taken from the
scratch side (the growth path, `r127_emit_grow`, allocates on the persistent side today), a mark at each pass's
start, and a rewind at its end, at `agrim` and at `krama`. Please commit the design document first.

## WS1 - the high-water risk, answered against the compiler as it is

1. **Where does it live, what updates it?** **Nowhere - it does not exist.** The arena has three words:
   `0kshetra_cur` (the persistent side, growing up), `0kshetra_end` (the scratch cursor, growing **down** from the
   top) and `0kshetra_sima` (the true end) - `src/r65_arena.inc:23-40`. A scratch `nirmmita` zeroes every byte it
   gives, every time (`r73_gen_scratch_nirm`), because scratch memory is reused. The design's mark would be a
   fourth word - a **low**-water mark here, since the scratch side grows down - updated at every scratch
   allocation.
2. **Before or after the cursor moves?** It has to be **against the old mark, over the whole range of the
   allocation**, then the mark is moved. An allocation can straddle the mark: part used before, part never. A
   test of one address (`new_cur > high_water`) is not enough; the used part must be zeroed.
3. **Can the mark be wrong?** Allocated-but-unwritten is harmless (it only zeroes more than needed). **The
   dangerous direction is memory past the mark that is not virgin - and that already happens today, on the other
   side.** The persistent side is bounded by where the scratch cursor is *now*, not by the lowest it ever was, and
   it does not zero (`r65_arena.inc:23`: "memory from the arena is never reused, so it arrives zeroed"). After a
   big block ends, the persistent side can grow into addresses the block wrote:

   ```
   mandapa { vitti p = nirmmita(900000000) ; 77 written at 1,000 places }
   vitti q = nirmmita(400000000)            # outside any block: "n bytes, zeroed" (reference §4)
   ```
   **`q` holds 283 words that are not 0** - `evidence-r172/programs/hw.sm`, the same on v315, v316 and v317
   (`results-stale-memory.txt`). **A program reads an ended block's data through a fresh allocation.** It needs the
   two sides to have used more than 1 GiB between them over time, so it is rare; it is still a defect in v315
   today. I did not find it recorded (searched the reference, `docs/reports/`, and the partners' folders for
   "arrives zeroed", "not zeroed", "rewound memory"). **Not fixed here** - it is not this round's change, and the
   fix is the very mark you are asking about: one word, the lowest the scratch cursor ever reached, and the
   persistent side zeroes whatever it takes above it.
4. **Is skipping the zeroing worth the risk? No.** For the piece built there is nothing to zero. For the rest of
   the design: zero unconditionally on the scratch side, as today, and use the mark only where it is needed for
   *correctness* (point 3), not to skip work. **The 3.4 ns and 0.9 ns are the design's figures; I did not measure
   them - NOT RUN.** What I measured is the whole pass: 800,000 passes of "declare, add one number, read it" take
   about **25 ns a pass on v316 and 4.5 ns on v317** (5.0 ms and 0.9 ms per 200,000 passes, `results-800000.txt`).

## WS2 - what is proven local

A whitelist, not an escape analysis (`r172_scan`, `src/sutram_compiler.asm`). The `kosh` must be:

- **declared as a statement of the `chakra`'s own body** - not under a `yadi`, not in a `mandapa` or another loop
  inside it;
- **the only declaration of its name in the loop**;
- **named, anywhere in the loop, only as the base of an index** (`k[i]`, `k[i] = v`) **or as the `kosh` a built-in
  works on**: `kosh_kship`, `kosh_yuj`, `kosh_hri`, `kosh_gan`, `kosh_shodh`, `kosh_rikt`, `kosh_iksh`,
  `kosh_apanay`.

**Anything else, and it is made every pass as before:** `vitti a = k`, `k` given to a `prakriya` (even one that
only reads it), **a slice** (`f(k[0:1])` - the slice case your point 3 raises: a slice node is not on the list, so
the `kosh` is simply left alone), `nivartanam k`, `kosh_ksham(k)` (the capacity would show that the `kosh` is not
new), and **any construct the scan does not know**. It fails toward leaking.

**What a pass can still observe: nothing.** Each pass sees length 0; `k[i]` beyond the length is refused as
always; the declared capacity (`kosh k[n]`) is still evaluated and checked every pass, then not needed.

## WS3 - the guard

- **783 programs. 40 contain a `chakra`** (32 compile, 8 are refused); **743 contain none.** `chakra-count.txt`.
- **None of the 783 declares a `kosh` inside a loop of any kind** (`kosh-in-loop.txt`; a textual screen by
  indentation - `kosh_yavat_count.py`). So no program in the corpus has the case, and **all 783 are byte-identical
  or identically refused, ELF and PE, against v316-ready and against v315.**
- **Say it plainly: a program that *has* the case necessarily compiles to different bytes** - that is the change.
  The corpus cannot show those; the new gate does (below), and each of its programs runs under Wine with the
  output of the Linux program, from a PE that `win/sutram.exe` under Wine and the Linux compiler write
  identically (`refusals-and-wine.txt`: 20 programs, 0 bad).

## WS4 - the proof

**Gate `R172 chakra kosh`, `tests/r172/test_chakra_kosh.py`: 24 checks, 0 failed on v317; 12 fail on v316**
(`gate-v317.txt`, `gate-v316.txt`).

- **Eighteen shapes**, each compiled with 1 pass and with 20: "made once" means the 20-pass program's
  `parimana()` equals the 1-pass program's; "made every pass" means it is larger, as v316. No recorded numbers -
  the test calibrates itself. Eleven made once (plain, `dasham`, grown to 100, grown to 4,097 - one region, not
  twenty - a capacity that changes each pass, `agrim`, every built-in, two `kosh`, in a `prakriya`, `nivartanam`
  out of the loop, the loop inside a `mandapa`); seven left alone (second name, given to a `prakriya`, slice,
  `kosh_ksham`, under `yadi`, `yavat`, in a `mandapa` inside the loop). Every program's sum is right only if every
  pass saw an empty `kosh`.
- **Nested:** a `kosh` in an inner `chakra` is made once *for each time the inner loop starts* - 20 x 20 passes
  hold what 20 x 1 hold. **Not once for the program.**
- **The redzones, as the design asks:** 64 bytes of `0xDEADBEEFCAFEBABE` immediately before `d-16` and
  immediately after the `kosh`'s first allocation; then 1,000,000 passes; nested `chakra` (1,000 x 1,000, a second
  `kosh` in the inner loop); a `chakra` inside a `mandapa`; growth to 20,000,000 elements in each of three passes.
  After each phase **all sixteen redzone words are read back and `d-16`, `d-8`, `d`, `d+8` compared with exact
  values** (length, capacity, the elements' address, the region size 268,435,456). **Every phase: 0 bad.** And in
  every phase the elements' address after pass 1 never changes again ("moved 0") - which is the reuse itself. Run
  twice: with the 32-byte descriptor and with R82's 56-byte one.
- **Out of memory:** the same program with 1.2 GiB of address space - the growth is refused with
  `kosh vardhayitum smritih na labdha`, exit 1, after phases 1 and 2 reported intact. Linux only (`RLIMIT_AS`).
- **A note on the redzone after `d+16`:** the first allocation is the descriptor *and* its first element slot, so
  the second redzone sits right after that slot (and 8 bytes of rounding), not at `d+16` itself.

**The leak, R169's method** (`probe.py`: VmRSS from `/proc/<pid>/status` while the program waits on `grahan()`;
three runs each; the program's own baseline at point 0 is **12-20 KB**):

| after pass | v316: VmRSS | v317: VmRSS | VmSize, both |
|---|---|---|---|
| 0 | 12-20 KB | 12-16 KB | 232 KB |
| 200,000 | 9,388-9,396 KB | **16-20 KB** | 1,048,808 KB (the arena, reserved once) |
| 400,000 | 18,764-18,772 KB | **16-20 KB** | 1,048,808 KB |
| 800,000 | **37,512-37,520 KB** | **16-20 KB** | 1,048,808 KB |

**Pages touched:** on v316 one new page about every 85 passes (4,096 / 48 bytes a pass, arithmetic); on v317 the first page and no other.

## WS5 - the honest scope

- **This covers a `chakra`-local `kosh` - the 48 bytes a pass - and only when it is proven local by the list
  above.** Give the same `kosh` to a `prakriya` and it leaks as before.
- **`mala` is not in this round**: 80 bytes a pass, unchanged.
- **Not covered either:** a `kosh` in a `yavat` loop; a `kosh` in a `mandapa` inside the loop (64 bytes a pass,
  unchanged); a `kosh` made by a `prakriya` that the loop calls (one per call, unchanged).
- **A block still never returns memory to the operating system.** Nor does this: the `kosh` keeps what it grew to
  until the program ends - bounded by its largest pass, not by the number of passes.
- **Reference §19 has a paragraph** (I wrote one on the branch so the documents agree with the compiler; Muse's
  sentence should replace it), and `docs/MEMORY-MODEL.md`'s box has a line.
- **The zeroing decision:** nothing is zeroed and nothing is skipped; it costs nothing. See WS1.4.
- **This is not "the memory problem solved".** It is one shape of one of three leaks.

## Not done, and why

- **The scratch-cursor rewind, `scratch_high_water`, slice origins, removing a runtime pin** - the design is not in
  the tree; see the top.
- **The stale-memory defect (WS1.3)** - found, measured, named in the release notes on the branch; not fixed.
- **Windows** - 20 programs under Wine; **not run on Windows**. `tests/windows/accept_v316.cmd` still checks for
  v316 and was not extended for this change.
- **The zeroing costs (3.4 ns, 0.9 ns)** - NOT RUN; they are the design's numbers.
- **Not merged**, as with v316. The branch sits on `v316-ready`, so it carries v316's change too; if you want it
  on v315 alone, say so.

## ROUND-171, which was built before 172 arrived

ROUND-172 says "do not build 171's version". **By then it was built and measured.** It is on branch
`r171-kosh-release` (3deb16c3), **not finished** (no changelog, reference or installer; the full gates were not
run), **not to be merged**, and I stopped work on it when I read 172. For the record, because the numbers are real
(`evidence-r171/`):

- **What it does:** a `kosh` declared as a statement of a `mandapa`'s own body, added to in the block, named only
  as an index base or as a built-in's `kosh`, gives its region back (`munmap` / `VirtualFree`) at the block's last
  line, `krama`, `agrim` and `nivartanam`. **Not** on a failure passed on by `prasar` (kept, as before).
- **Before / after, 1,000 passes** (a `kosh` grown to 4,097 in a `mandapa` in a loop): VmSize **66,584,808 KB →
  1,048,808 KB**; VmRSS **68,080 KB → 32,076 KB** - not to the baseline: **32 KB a pass stay**, the buffers the
  `kosh` outgrew in the arena before it reached a region. Under `ulimit -v` 8 GiB: v316 stops in pass 112, the
  branch finishes 1,000 and 20,000. Under Wine: 66,735,916 KB → 1,772,332 KB.
- **Guard:** 783 programs, 0 DIFFER, against v316 and v315, ELF and PE. One program differed in the first build
  (`examples/318_r108_parimana_moves.sm`, a `kosh` in a block that nothing is added to: same output, 98 bytes
  longer); a `kosh` nothing is added to can never have a region, so it now gets no code, and the program is
  identical again.
- **Your four conditions:** 2, 3 and 4 are already compile errors (`E_KOSH_MANDAPA`: assigned outward, returned,
  pushed or stored) - checked, still refused. The check that was missing is the second name (`vitti a = k`) and
  the `prakriya` argument; both leave the `kosh` unreclaimed.
- **WS4 of 171 - is a warning right when an escaping `kosh` in a loop grows memory?** **Yes, as a hint, not an
  error, and only where the compiler is certain:** a `kosh` declared in a loop's body that is *not* made once.
  It would say, in the compiler's language: *"`kosh k` is made anew on every pass and none is given back - declare
  it before the loop and empty it with `kosh_shodh(k)`, or use it only as `k[i]` and with the `kosh_*`
  built-ins."* Not built. The second half of that sentence is only true on the R172 branch.
- **R172's piece makes most of R171's unnecessary for a loop:** move the `kosh` from the block to the loop's body
  and it is made once - no region is mapped and unmapped each pass, and the 32 KB a pass do not stay either
  (the `region` case in the R172 gate: 20 passes hold what one holds).

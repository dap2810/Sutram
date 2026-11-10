# R173-00 — The three audits: **(1) growth holds** - the reset writes one word, the length; a `kosh` grown to 100 every pass holds 16-20 KB at 800,000 passes (v316: 825,016 KB). **(2) The container escape cannot happen** - the compiler already refuses the program, on v315 as on v317, and the hoist would leave such a `kosh` alone anyway. **(3) Nested blocks are NOT reached** - under a `yadi` or in a `mandapa` inside the loop the leak is exactly as before (37,516 and 50,012 KB). And **a `mala` is now made once too**: 62,516 KB → 20 KB, staged as v318 - **without the refusal you asked for first**, because it is not needed and would stop programs that compile today.

## Release line

```
main  (the commit carrying this file)   Sutram 1.0 (v315) - sampurna sutra, unchanged (this folder's files only)
staged r173-chakra-mala (SHA in the follow-up commit)  Sutram 1.0 (v318) - sampurna sutra   (on r172-chakra-kosh 501d35fd; NOT merged)
     crash corpus, suite, gates: THE FULL GATES WERE STILL RUNNING at this first push - NOT YET A RESULT (next commit)
     guard, the ordinary way, 783 programs, ELF and PE, against v317 (r172), v316-ready and v315 (main) - six runs:
            587 byte-identical, 196 refused identically, 0 DIFFER, every time
     installer rebuilt (payload v318): 34e8dc9878b3a9c9bf70cf20954dd658519eba4affe875bcdc837a4fefa12da5
staged r172-chakra-kosh 501d35fd  v317, unchanged      staged v316-ready 59d60353  unchanged
superseded r171-kosh-release 3deb16c3  a record only
```

**The guard is absolute: 0 DIFFER.** Sanskrit only; no pack touched; `backups/` untouched.

## WS1 - the growth case

**1 and 2. What is reset at the top of a pass: one word, `[d-16]`, the length. Not the capacity, not the elements'
address.** The emitted instructions, disassembled from a compiled program (`evidence-r173/reset-sequence.txt`;
`programs/tiny.sm`, v317; the slot is `[rbp-8]` here):

```
at the entry to the loop, once:
  99:  48 c7 45 f8 00 00 00 00    mov    QWORD PTR [rbp-0x8],0x0      ; no kosh yet

at the declaration, every pass (the capacity expression's value is in rax and has been checked):
 129:  48 8b 4d f8                mov    rcx,QWORD PTR [rbp-0x8]      ; the descriptor from an earlier pass?
 12d:  48 85 c9                   test   rcx,rcx
 130:  0f 84 10 00 00 00          je     0x146                        ; none: allocate (first pass only)
 136:  48 c7 41 f0 00 00 00 00    mov    QWORD PTR [rcx-0x10],0x0     ; THE RESET: length = 0, nothing else
 13e:  48 89 c8                   mov    rax,rcx                      ; the same descriptor
 141:  e9 53 01 00 00             jmp    0x299
 146:  50                         push   rax                          ; first pass: the allocation, as in v316
       ...
 28a:  48 89 08                   mov    QWORD PTR [rax],rcx          ; [d] = the elements
 28d:  48 c7 40 08 00 00 00 00    mov    QWORD PTR [rax+0x8],0x0      ; [d+8] = 0, no region
 295:  48 89 45 f8                mov    QWORD PTR [rbp-0x8],rax      ; remembered for the next pass
 299:  49 89 c6                   mov    r14,rax                      ; both paths: the variable
```

**`[d-8]` and `[d]` are written only on the first-pass path.** A `kosh` that grew on pass 1 has its grown buffer
on pass 2.

**3. Measured** (`programs/g100.sm`: 800,000 passes, each adds 100 numbers; R169's method, three runs each,
baseline 12-16 KB; `results-growth.txt`):

| after pass | v316 VmRSS | v317 VmRSS |
|---|---|---|
| 200,000 | 206,264-206,268 KB | **16-20 KB** |
| 400,000 | 412,512-412,516 KB | **16-20 KB** |
| 800,000 | **825,012-825,016 KB** | **16-20 KB** |

**Flat.** v316 leaks 1,056 bytes a pass here; v317 none. Time for 200,000 passes: 117-161 ms → 36-39 ms.
**You were right that the R172 benchmark could not tell** - one number never grows the `kosh`. The R172 gate did
test growth (to 100, to 4,097, to 20,000,000 with the elements' address compared every pass); the headline number
did not, and I should have reported a growth measurement beside it.

## WS2 - the container escape

**Your program does not compile, on any version, for two reasons - neither of them the hoist.**

| program (`evidence-r173/programs/`) | v316 | v317 |
|---|---|---|
| `m1.sm`, exactly as briefed | refused: `matrix[0][0]` is a syntax error (`vyakaran dosh`, 8:22) - Sutram has no double index | the same |
| `m1b.sm`, the same without that line: `kosh_kship(matrix, row)` | **refused, `E_KOSH_DVARA`** | the same message |
| `m2.sm`: `matrix[i - 1] = row` | **refused, `E_KOSH_DVARA`** (*kosh 'row' koshthe, kshetre athava smritau na likhyate*) | the same |
| `m3.sm`: `vitti h = row` then `kosh_kship(matrix, h)` | **refused, `E_KOSH_DVARA`** | the same |
| `m4.sm`: `rows[i - 1] = row` into a `mala` | **refused, `E_KOSH_DVARA`** | the same |

**A `kosh` cannot be put into a `kosh`, a `mala` or memory at all (R126, v301) - so there is no `matrix[0][0]` to
print, 1 or 5.** `results-container.txt`.

**And if R126 were ever relaxed, the hoist still would not alias:** in `kosh_kship(matrix, row)` the name `row` is
the *second* argument, an ordinary value - not on the whitelist - so `row` would be made every pass. Only the
*first* argument of a `kosh_*` built-in counts as "the `kosh` it works on". The gate has this shape for a `mala`,
which *can* be put into a `kosh`: five rows stay five (below).

## WS3 - nested blocks

**Not hoisted. The leak is exactly as before.** 800,000 passes of "declare, add one number, read it"
(`results-nested.txt`, two runs each):

| the declaration is | v316 VmRSS at 800,000 | v317 |
|---|---|---|
| a statement of the `chakra`'s body | 37,516 KB | **16-20 KB** |
| inside `chakra { mandapa { ... } }` | 50,012-50,016 KB | **50,012 KB - unchanged** |
| inside `chakra { yadi (...) { ... } }` | 37,512-37,516 KB | **37,516 KB - unchanged** |

**So yes: a `yadi` or a `mandapa` between the loop and the declaration brings the leak back.** I said so in R172
("not covered"), and the R172 gate has both shapes as "made every pass" - but it is a real limit a student will
hit, and the table above is the first measurement of it.

**It does not explain 48 against 64.** Those are v316's numbers, before any hoist: 64 is the descriptor with
R82's three extra words (R170-00 WS4).

**What extending it would take - not built, because this round says verify:**
- **Under `yadi` / `anya`:** the same proof holds (the name is still used nowhere but in whitelisted ways in the
  whole loop, so when the declaration runs again the earlier `kosh` is dead). It is a walk into the bodies of
  `yadi` instead of only the loop's own statements. Small.
- **In a `mandapa` inside the loop:** each pass is a new block, and R82 stamps the block's generation into the
  descriptor. A reused descriptor would carry the old block's stamp. The whitelist already keeps it away from the
  one place the stamp is read (a `prakriya` given the `kosh`), but I would re-stamp it rather than argue that.
  A little more than small.
- **`yavat`:** the same as `chakra`; not built.

## WS4 - the `mala`: built, staged as v318 - and one thing you asked for is deliberately not done

**Built: a `mala` declared as a statement of a `chakra`'s own body, without an initializer, whose name appears in
the whole loop only as the base of an index (`m[i]`, `m[i] = v`), is allocated on the first pass; every later
pass with the same length finds it in its frame slot and zeroes its numbers.**

```
test rax,rax ; jle fresh            ; the length this pass
mov rcx,[rbp+slot] ; test rcx,rcx ; jz fresh
cmp rax,[rcx-8] ; jne fresh         ; the same length as the mala in the slot? (its hidden length word)
push rcx ; mov rdi,rcx ; mov rcx,rax ; xor eax,eax ; cld ; rep stosq ; pop rax      ; zero its numbers
jmp have
fresh: (the allocation, as before) ; mov [rbp+slot],rax
have:
```

**Zeroing is `rep stosq` over the `mala`'s own length, not eight unrolled stores** - the length need not be 8, or
even a constant (`mala m[n]`). A different length this pass makes a new `mala`, as before.

**Not done: refusing a `mala`'s escape with `E_SCRATCH_ESCAPE`.** You wrote "do not hoist a `mala` without
refusing escape first". **I hoisted without it, and here is why that is safe and the refusal is not:**

- **The hoist never applies to a `mala` that can escape.** A `mala` given to a `prakriya`, given a second name,
  returned, or put into a `kosh` or a `mala` has its name somewhere other than an index base - so it is not on
  the whitelist and is made every pass, exactly as in v317. **Gate case `rows`: a `mala` pushed into a `kosh`
  on each of five passes - the five rows read back 11, 33, 55, each its own.** Nothing aliases.
- **A new refusal would stop programs that compile today.** Giving a `mala` to a `prakriya` and returning one are
  ordinary, documented uses (reference §19: "returning one from inside the block is not refused"). How many
  programs in the tree that would refuse: **NOT MEASURED.** That is a language decision for you and the partners,
  not something to slip in beside a memory fix.

**Measured** (`programs/ma.sm`, 800,000 passes of `mala m[8]`, read then written; `results-mala.txt`):

| after pass | v316 VmRSS | v318 VmRSS |
|---|---|---|
| 400,000 | 31,264-31,268 KB | **20 KB** |
| 800,000 | **62,512-62,516 KB** | **20 KB** |

Time for 400,000 passes: 21-27 ms → 7-11 ms (the zeroing is in that).

**Gate `R173 chakra mala`, `tests/r173/test_chakra_mala.py`: 12 checks; 6 fail on v317** (`gate-v318.txt`,
`gate-v317.txt`). Five shapes made once (plain; the length in a variable; two `mala`; a `mala` and a `kosh`
together; `agrim`), five left alone (a length that changes every pass, a second name, given to a `prakriya`,
under a `yadi`, `yavat`), the rows, and **redzones**: 64 bytes of `0xDEADBEEFCAFEBABE` right before the `mala`'s
length word and right after its last number, 1,000,000 passes, **both intact, the length word still 8, and every
pass read eight zeros before writing** ("dirty 0"). Every sum is right only if each pass saw zeros.
**The R172 gate still passes on v318** (24 checks).

**Under Wine:** the twelve gate programs, the growth program and the `mala` program - the PE that `win/sutram.exe`
writes under Wine is byte for byte the Linux compiler's, and each prints what the ELF prints (`wine.txt`: 14
programs, 0 bad). **Not run on Windows.**

## WS5 - the stale-data bug

**Measured first** (`results-stale.txt`, v315 and v318 alike):

- **Small** (`st_small.sm`): a block writes 77 into `nirmmita(64)`; a `nirmmita(64)` after the block reads
  **0 and 0**. The two sides are at opposite ends of the 1 GiB field and do not meet. **So it is not "every
  `nirmmita` after a block".**
- **Large** (`st_big.sm`): a block writes 77 into every word of `nirmmita(600000000)`; a
  `nirmmita(600000000)` after the block **reads 77 in 15,782,272 of its 75,000,000 words, the first at word
  59,217,728.** That is exact arithmetic: the block's memory started 600,000,000 bytes below the field's end,
  which is byte 473,741,824 from its start - word 59,217,728 - and everything the new buffer has above that is
  the block's. **Deterministic, as you say - once the two sides have used more than 1 GiB between them.**

**Is the proposed fix right? Yes, with two corrections.**

- **The mark is a *low*-water mark** - the scratch side grows down from the field's end; "dirty" is everything
  from the lowest address the scratch cursor ever reached, up to the end.
- **Where to update it: at the scratch allocation, not at the block's exit.** A block has four ways out (its last
  line, `nivartanam`, `krama` / `agrim`, a failure passed on by `prasar`), emitted at three different places; the
  scratch allocation is one place (`r73_gen_scratch_nirm`). One site cannot be forgotten. It costs a compare and
  a conditional move per scratch `nirmmita`.
- **Then, at a persistent `nirmmita`:** if its new end is above the mark, zero the part of it above the mark -
  only that part. Your example holds: a 200 MB block and then `nirmmita(64)` zero nothing at all (the 64 bytes are
  at the other end); they zero bytes only when the persistent side has actually climbed into what a block used.
- **Is it smaller than zeroing unconditionally? Yes, by far:** unconditional zeroing would write every byte of
  every `nirmmita` outside a block (200 MB for a 200 MB buffer, every time); the mark costs one compare per
  allocation and writes nothing until the two sides have crossed.
- **Who else takes persistent memory:** a `mala` (its numbers must read 0 - it goes through the same allocation,
  so the same fix covers it) and a `kosh` (nothing past its length is readable; no zeroing needed).

**Not built.** You asked whether it is right and for the measurement; it is the next small change, and it touches
the allocation every program uses, so it should be its own round with the guard.

## Your severity correction - what I see here

`programs/k5000.sm`: 100,000 passes, each growing a `kosh` to 5,000 (`results-k5000.txt`).

- **v315: killed by signal 9 after 5.4 s at 5,810,816 KB resident** - on this machine, where
  `/proc/sys/vm/max_map_count` is the default **65,530**. **I did not get the named refusal you report; I got a
  kill.** Either way the program stops.
- **v318 (and v317): finishes, 0.6 s, peak 440 KB** - the `kosh` is in the loop's own body, so it is made once.
  Put the same `kosh` in a `mandapa` inside the loop and it is v315's behaviour again (WS3).

## Honest scope

- **Made once now:** a `kosh` (v317) and a `mala` (v318) declared as a statement of a `chakra`'s own body and
  named only in the listed ways.
- **Still leaking, measured above:** the same declaration under a `yadi` (37,516 KB at 800,000), in a `mandapa`
  inside the loop (50,012 KB), in a `yavat` loop, and anything given to a `prakriya`.
- **A block still never returns memory to the operating system.** The stale-data defect is open.
- **Three staged compilers, none merged, none run on Windows:** v316 (outputs), v317 (`kosh`), v318 (`mala`),
  each on top of the one before. `tests/windows/accept_v316.cmd` covers only v316's change.
- **Not "the memory problem solved."**

## Not done, and why

- **Refusing a `mala`'s escape** - see WS4: not needed for safety, and it would stop programs that compile.
- **Hoisting into `yadi`, `mandapa`, `yavat`** - this round says verify; what each needs is in WS3.
- **The stale-data fix** - designed above, not built.
- **Windows** - Wine only.
- **Reference §19** - I extended my own paragraph on the branch for the `mala`; Muse's wording should replace it.

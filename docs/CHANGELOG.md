> **The 20 newest entries.** Older ones, from "v285" back to the first, are in [rounds/CHANGELOG-ARCHIVE.md](rounds/CHANGELOG-ARCHIVE.md) (split in R88).

## v305 (Claude, R129) - ChatGPT R204's slice findings: S1 closed by v304, S2 fixed; the release notes corrected

- **`k[lo:]` ends at the length after `lo` is evaluated** (R204 S2): `k[kosh_kship(k, 8) - 1:]` is `[1:2]` and gives 8
  (v304 refused it with the old length 1); after a `kosh_hri` or `kosh_shodh` in `lo`, the shorter or empty end.
  An explicit `hi` is evaluated once, as before.
- **R204 S1** - a slice passed beside an argument that grows the same `kosh` - crashed on v303 (SIGSEGV after a
  region move, reproduced here); **v304's rule already refuses it** (`E_KOSH_VIBHAG`), for an expression call, a
  statement call, a whole `kosh` to a `vibhag` parameter, and a growth through an alias.
- **A growth past 2^40 numbers stops with the grow message** - R204's F2 qualification: the declared limit is now
  checked on growth too. No machine reaches it (2^40 pushes first need 8 TiB).
- **The release notes corrected as R204 lists:** what a `mandapa` and `parimana()` cover, finite limits, what the
  out-of-memory message covers, the slice rules, what the allocator keeps, the v298 history, objects of mixed
  versions. Gate `R127 descriptor` +5 checks.

## v304 (Claude, R129) - a `kosh` parameter can grow, and the caller sees it

- **`kosh_kship` onto a `kosh` parameter compiles, and the growth is the caller's** - the parameter holds the
  descriptor (v302), as an alias does. Up to v303 it was refused with `kosh-tarke kosh_push asamarthitam`, a
  message that gave neither the current name nor the reason; the refusal dated from T18, when a parameter held
  the elements' address. Measured: 10 pushes through `jod(kk, i)` give `kosh_gan(kk)` 10; 9,000,000 through a
  parameter, past a region move, all seen; a block's `kosh` grown by a `prakriya` in 100 blocks.
  `examples/121` (which pinned the refusal, "until Sutram gains a descriptor ABI") now prints 1.
- **What it rules out, `E_KOSH_VIBHAG`:** a slice of a `kosh` given to a `prakriya` that may grow a `kosh` (it, or
  one it calls - worked out for the whole program to a fixpoint), or given beside an argument that has a call in
  it. A slice holds the elements' address as they were. No program in the tree does either.
- `docs/reports/HOW-DEFECTS-WERE-FOUND.md`: reading and testing found different defects; neither alone was enough.
  Gate `R127 descriptor` +5 checks.

## v303 (Claude, R128) - three descriptor defects ChatGPT R203 found by reading: fixed

- **A `kosh`'s length and elements are read after its index is evaluated** (`k[i]`, `k[i] = v`) and after a
  slice's bounds (`k[lo:hi]`) **whenever the index or a bound has a call in it** - the only way it can change
  the `kosh`; an index without a call compiles to v302's bytes (the codegen-shape ceilings hold). v302 read them first, so an index that grew the `kosh` (`k[kosh_kship(k, 5) - 2]`)
  read the old elements - **SIGSEGV once an outgrown region had been given back** - and one that shrank it
  (`k[kosh_hri(k) - 1]`) was checked against the old length. (R203 F1.)
- **A declared capacity past 2^40 numbers stops with `kosh rachayitum smritih na labdha`.** v302 multiplied it
  by 8 without a check: `kosh k[2305843009213693952]` became a 32-byte allocation and the pushes overwrote the
  next block (measured: another buffer's 77 became 1). (R203 F2.)
- **`parimana()` counts a region `kosh`'s bytes right:** v302 took the new capacity from `r11`, which the Linux
  `syscall` had just overwritten (20,000 numbers: 234,096 printed, 294,976 right). (R203 F3.)
- Gate `R127 descriptor` +6 checks (24 with PE; v302 fails all six). No program in the tree changes output; the
  92 that change bytes are the `kosh` programs (a declared capacity's check).
- **Also R128:** the installer's payload rebuilt (on Linux, `tools/build_installer_linux.py`); `sutram-link.exe`
  rebuilt (its embedded runtime predated v300); `docs/RELEASE-NOTES.md`; the pack-message goldens no longer
  assert a compiled size.

## v302 (Claude, R127) - a `kosh` is a descriptor: two names stay one, and no region per `kosh`

- **A `kosh` value is now a descriptor that never moves:** its length and capacity where they always were
  (`[d-16]`, `[d-8]`), and at `[d]` the address of its elements. `k[i]`, `kosh_kship`, `kosh_hri`, `kosh_iksh`,
  `kosh_apanay`, a slice of a `kosh`, and a `kosh` given to a foreign `ptr` parameter go through it. **Growth moves
  the elements and updates `[d]`, so every name of the `kosh` sees it** - `vitti a = k` stays `k` at 4,194,305
  numbers and at 20,000,000 (v301 parted them at 4,194,305).
- **No 64 MiB region per `kosh`:** a small `kosh` is 32 bytes and its elements in the arena (20,000 koshes: one
  `mmap`, 3 ms, was 20,000 `mmap`s and 99 ms; 1,000 under a 300 MB address limit, which v301 could not make). A
  `kosh` past 64 KiB of elements gets a region of at least 64 MiB, reserved not committed, grows in place in it,
  and moves to a larger one through the descriptor when it outgrows it; **the old region is given back**
  (`munmap`; on Windows `VirtualFree`, a new import of the runtime).
- **No memory for a `kosh` or its growth: a message and exit 1** (it was a write through 0, SIGSEGV). **A slice of
  a `kosh` kept in a name is refused, `E_KOSH_VIBHAG`** (a growth would leave it behind); passing `k[a:b]` on
  is unchanged. Reads cost the same (200 million `k[i]`: 601 ms on v301, 552 on v302).
- Muse R127's eight defect programs are goldens (`examples/351`-`359`); `examples/317` / `318` print the new
  `parimana()` byte counts. Every program without a `kosh` compiles to the same ELF bytes; every PE program
  differs (the runtime), with the same output. Gate `R127 descriptor`.

## v301 (Claude, R126) - a name keeps one kind; the three defects R125 found are refused

- **A name keeps the kind its first binding gave it, for the whole `prakriya`:** `kosh`, `kosh dasham`, `mala`,
  `vibhag`, or a number / raw address. Every later declaration or assignment of that name must give the same
  kind, or it is **`E_VITTI_PRAKAR`** - in any branch, any loop, any block. Up to v300 the compiler marked a name
  from a bare variable only, never cleared the mark and did not see control flow, which gave **two SIGSEGVs and a
  silent read past a `kosh`'s length** (R125's t2, t3, t4; now `examples/348`, `349`, `350`, refused).
- **A `kosh` leaves its tracking only by doors that keep the kind:** its own name (`vitti b = k`, `(k)`), a `kosh`
  parameter, a `kosh` builtin's first argument, or a `prakriya` that returns a `kosh` parameter or a `kosh` it
  declares, by its own name, on every `nivartanam` (its caller's name is then marked and bounds-checked). A `kosh`
  into a cell, a field, a module `vitti`, an untyped parameter, a raw builtin (`likha`, `pad8`, `likh8`, a value
  of `kosh_kship`), `?:` or a `siddhi` / `dosh` value is **`E_KOSH_DVARA`**; `k + 0`, `k - 0`, `k * 1` are `E_KOSH_GANIT` like `k + 8`.
- **No emitted byte changed:** every program v300 compiles, v301 compiles to the same bytes (ELF and PE); three
  R38/R42 examples that wrote `vitti w = 0` and then `w = v` now declare `w` from a collection of `v`'s kind.
  Gate `R126 kinds` (53 checks, ELF and PE under Wine).

## v300 (Claude, R124) - Windows commits what a program touches, not what it reserves

- **The PE runtime reserves an `mmap` with `MAP_NORESERVE`** (the 1 GiB arena, each 64 MiB `kosh` region) instead
  of reserving and committing it, and **a vectored exception handler commits 64 KiB where a page is first
  touched** - only inside memory the program reserved, never its stack. `ReadFile` / `WriteFile` buffers are
  touched first, since the kernel does not fault on the program's behalf (without that, reading a file into a
  fresh buffer returned -1; the gate shows it). Two new kernel32 imports: `AddVectoredExceptionHandler`,
  `VirtualQuery`.
- **Measured under Wine** (its read-write mappings are what it committed): one `nirmmita(64)` **1073.7 MB → 0.0**;
  100 koshes **6,713 MB → 8.7**; a 100 MB buffer touched on every page **1073.7 → 100.0**. **ELF unchanged byte
  for byte.** Native Windows commit is the owner's measurement. Gate `R124 lazy commit` (7 checks).

## v299 (Claude, R123) - the Linux memory model on Windows: merged from the Windows round 4 branch (PR #65)

- **On PE, as on ELF:** `nirmmita` uses the arena, a `mandapa` gives its memory back, `mandapa parimita N`
  refuses past its budget (`E_PARIMITA`), `parimana()` reports the bytes held, and a `kosh` has its own region
  and never moves (`examples/288` prints `a[0]=99 k[0]=99` on Windows too). The Windows agent found the cause:
  `r65_active` excluded PE by a compile-time `target_pe` test, and the runtime's `VirtualAlloc` adapter already
  served the arena's `mmap` calls. **Ported onto v298, not merged whole:** the branch also carried Round 3's
  new-string `vartani_sandhi`, which v298 does not take (R121); its own `INTEGRATION.md` says the same.
- **The cost, on Windows only:** `VirtualAlloc` reserves *and commits*, so the arena is 1 GiB of commit charge
  from a program's first allocation and each `kosh` region 64 MiB (measured there: 1.08 GB, 67.7 MB). ELF
  output is unchanged byte for byte. Priced in R123, not changed.
- The native Windows harness passes `--lang hindi` to example 220 and skips 29 (a raw Linux exit syscall).
  Gate `R123 PE memory` (9 checks; PE under Wine).

## v298 (Claude, R121) - `anka_akshar` and `vartani_sandhi` fixed: the two builtin defects Windows exposed

- **`anka_akshar(code)`** wrote its character **below the stack pointer** and returned that address, leaving
  `rsp` 8 bytes lower each call. Windows lost the character at once (the runtime's kernel32 call uses that
  stack: example 322 printed a garbage byte); Linux lost it as soon as the value was kept past a call. **Now two
  bytes from nirmmita's allocator**, as `s + t`; the result lives as long as the program.
- **`vartani_sandhi(s, t)`** appends in place, and **`s` was allowed to be a string literal** - part of the
  program's code. Windows: access violation (0xC0000005, example 322); Linux: it silently overwrote the code
  after the literal, and crashed the second time round a loop. **Now a literal `s` is refused when compiled,
  and a literal reached through a variable stops the program** (`E_VARTANI_STHIRA`, exit 1). In-place
  appending into writable memory is unchanged (R54's raw test).
- Examples 322/323 append into a `nirmmita` buffer instead of the literal; **their goldens are unchanged** - the
  golden was the right answer, Linux printed it by luck. Gate `R121 builtins` (14 checks, ELF and PE).

## v297 (Claude, R118) - the library's English names become aliases; three compiler hints name the R111 builtins

- **Ten library `prakriya` get Sanskrit names** (ChatGPT R191's bucket-1 words `bit`, `diff`, `pad`, `pre`,
  `sign`, `sorted`): `ekanka_gan` (was `bit_gan`), `rakh_ubhaya_bhed` (`rakh_samroop_diff`), `roop_purti_vam` /
  `_dakshin` / `_madhya` (`roop_pad_*`), `purti_vam` (`pad_vam`), `roop_ank_upasarga` (`roop_ank_pre`),
  `roop_chihna_akshar` (`roop_sign_akshar`), `asti_kramabaddha` (`asti_sorted`), `suchi_asti_kramabaddha`
  (`suchi_asti_sorted`). The library defines the new name; **a call written with the old one compiles to the same
  bytes** and prints R111's warning once (`Sutram suchana: 'asti_sorted' purana nama - 'asti_kramabaddha'
  likhatu`) - not for a program's own `prakriya` of that name, a variable, a `yoj`'d module or a `--lang` run.
  Reference section 4c; gate `R118 library names`.
- **Hints:** `kosh_gan(k)` (was `kosh_len(k)`) in the five `E_KOSH_*` hints, `likha_rup` in the `parikshita` hint,
  `dvaram_likha(dvara, ...)` (was `fd`). Eight refusal goldens re-recorded: that hint line, and the old-name
  warning gone because the examples now use the new names.
- **Examples and the library now write the R111 names** (257 replacements in 72 examples, 57 in `lib/`; outside
  string literals). Every changed program compiles to the bytes it did. `examples/323` keeps the old builtin
  names, `346`/`347` the old library names, on purpose.
- **Not changed, waiting for a decision:** the four pack-translated `kosh` messages (three compiled into
  programs) that name `kosh_pop` / `kosh_peek` / `kosh_dequeue` / `kosh_push`, and the shell help's `mala arr[5]`.

## v296 (Claude, R116) - fifteen of the sixteen library contracts (ChatGPT R189); long string literals work

- **The policy, in the library:** a mathematical library function gives the exact answer or fails through a
  declared channel. *Stops* (stderr `Sutram truti [CODE]: function: ...`, exit 1): `dvigun`, `trigun`, `vardh`
  (`E_ATIPRAVAH`); `nirapeksh_mulya`, `ganita_nirapeksh`, `mahattam_samapavartak`, `viparyay_ank`,
  `brihat_ank_tak_laghu` (`E_PHALA_SEEMA`; bad digits `E_MULYA_AYOGYA`); `brahmagupta_kshetr` (exact multiword
  formula; bad sides `E_MULYA_AYOGYA`, area past the range `E_ATIPRAVAH`); `adish_gunan`, `bindu_gunan` (unequal
  lengths, `E_AKARA_ASAMYA` - v295 used the shorter). *Status*, nothing printed: `brihat_ank_se` (0, digits
  cleared), `suchi_shreni` (0, list unchanged), `varna_tak_dashm` (leading zeros no longer spend digits: twenty
  characters `00000000000000000001` are 1, not 0). `yog_seema` saturates only the final sum
  (`yog_seema(2^62, 2^62)` is 2^62, was 2^63 - 1). Messages exactly as R189's matrix.
- **Not built: `patra_asti`** (row 11) - its contract needs an operating-system metadata query the compiler does
  not have; reported, not improvised.
- **`abhava(cond, "text")`:** the assertion takes an optional message, written to stderr before exit 1 - the
  compiler-emitted failure path the library uses (no OS call in a core module).
- **A compiler defect found on the way, fixed:** a string literal of 127 bytes or more was jumped over with a
  one-byte jump that wrapped backwards, so the program crashed (SIGSEGV or SIGILL), or ran on and printed
  nothing or the wrong text; `likha` and `likha_rup` of a literal also wrote only its length modulo 256. The R189
  messages are 88-151 bytes. Every literal of 126 bytes or fewer compiles to the same bytes as before.
- Examples 330-344 (one per row) and 207 (now the refusal); the suite checks a `<name>.err` when one is recorded.

## v295 (Claude, R115) - `sankhya_bindu` / `sankhya_dot` withdrawn; the arena branch's silent wrong answer found and fixed there

- **Withdrawn, not missing:** a call to `sankhya_bindu` or `sankhya_dot` is refused when compiled -
  `E_PRATYAHRITA`, with the name, the line and the library's working float dot product (`yoj sankhyiki`,
  `bindu_gunan(a, b)`). v293's integer loop was right for integer cells and **wrong for a `kosh dasham`**
  (it multiplied float bits: 2.5·2.5 + 1.5·1.5 gave 0) - my mistake in R113, found against Muse R111's shapes.
  No old-name warning first (ChatGPT R187). Example 329 is now that refusal.
- **The arena branch** (`claude/r108-arena-review`, not merged): its silent wrong answer - `chain40_reuse.sm`
  printing another block's 99 - was the outlives analysis stopping after 32 rounds; fixed on the branch (`3a6292e`)
  with main's v291 fix. Main changes only by the withdrawal.

## v294 (Claude, R114) - `Sutram Error` becomes `Sutram truti`, in the compiler and all eleven packs

- **The failure token is Sanskrit:** every message that stops a compile or a program begins `Sutram truti`
  (`Sutram truti [E_PARSE]: ...`). Bodies, `[E_CODE]` tags, punctuation, placeholders and exit codes unchanged;
  `Sutram suchana:` unchanged.
- **By the owner's written exception** (3 November; `docs/decisions/R114-SUTRAM-TRUTI.md`): the one token,
  identically in all eleven `lang/*.sandesh` files - 68 message values each, 748 in all - and nothing else in them.
  Each pack file differs from v293 by the token alone.
- `tools/sandesh.py` enforces the new token (a pack still carrying `Sutram Error` is refused - a new test); the
  Linux IDE's failure check matches `truti`; goldens, test scripts and current docs move with it.
- **Not changed:** the linker's own messages (`sutram-link`, `sutram-elf2smo`, `sutram-coff2smo`) - outside the
  permission. A program built by v293 or earlier still prints `Sutram Error` from its own bytes.

## v293 (Claude, R113) - a `rachana` reference beside an operator is refused; `sankhya_bindu` is an integer dot product

- **`E_RACHANA_GANIT`:** `p == q`, `p < q`, `p + q` (and every operator) on a `rachana` reference - a name whose
  field the `prakriya` reads or writes, or a method's first parameter - is refused, as a bare `kosh` or `mala`
  is. Up to v292 they compared, ordered and added two addresses. The reference states the meaning `==` will have
  on all three - the same object - and why it is refused until a `kosh` has a stable identity (ChatGPT R182).
  Example 328. No program in the tree changed (705 compiled, 0 differ).
- **`sankhya_bindu(a, b, n)`** (was `sankhya_dot`, Muse R108's one alias whose body was wrong): the integer dot
  product of n 8-byte cells. Up to v292 it took two pointers and returned the bits of four 32-bit float products,
  which no Sutram value holds. Example 329. `sankhya_yog` / `sankhya_gunan` are documented as what they are
  (four 32-bit float lanes), not fixed.
- The reference says what would remove `Sutram Error`, the one English word left.

## v292 (Claude, R111) - the vocabulary change, as aliases: 22 builtins get Sanskrit names, `asti` / `nasti` are `==` / `!=`, `tyaj` leaves the shell

- **22 builtins have a new, primary name; the old one still works and compiles to the same bytes.** An old name
  written in the program's own file prints one warning per name on stderr - `Sutram suchana: 'kosh_push' purana
  nama - 'kosh_kship' likhatu` - and none from a `yoj`'d module or in a `--lang` run (a pack run prints only its
  pack's language). Reference §4b has
  the table. `tests/r111/test_vocabulary.py` (a gate): every pair byte-identical, ELF and PE.
- **`asti` / अस्ति is `==`, `nasti` / नास्ति is `!=`** - the same token (examples 324-327).
- **The shell:** `tyaj` leaves; `exit`, `quit`, `help` still work, with the warning; `sahayata` is help.
- **Sarvam's decisions applied:** `to` dropped; `vartani_sandhi`, `kosh_apanay`, `anka_akshar`, `likha_santat`;
  Muse's two: `smaran_pratilip` and `sahayata`. **Not changed:** `Sutram Error` (R111-00 says why).

## v291 (Claude, R109) - the outlives rule follows a second name and a chain of any length; the installer gate names the payload; the suite's summary is its last line

- **ChatGPT R178's branch findings, checked on main:** two were open on v290. `vitti a = k` then `rakh(a)` gave a
  block's `kosh` to a `prakriya` that keeps it (only `k`'s own name was checked), and a chain of 33 or more
  keeping `prakriya`s passed it out (the fixpoint stopped after 32 rounds). Both are `E_KOSH_MANDAPA` now:
  an alias made by `vitti a = k` or `a = k` carries the block, and the fixpoint runs to convergence. Examples 320
  and 321. A full table of open block `kosh`s now refuses instead of leaving the next one unchecked, and a walk
  that overflows its stack counts the parameter as keeping (neither is reachable in the tree).
- **`installer version`** now says what it read: `payload v243 inside Sutram-Setup.exe (the wizard has no
  version of its own)`, the payload's packing date, and how many of its `lib`/`lang` files differ from the
  tree. `docs/INSTALLER-REBUILD.md` is the Windows procedure, with the payload compiler's expected SHA-256.
- **`tests/run_tests.py`** prints the failure details first and `suite: ... (N run)` last; a no-expectation
  program's output is indented and labelled. The gates read the last line.

## v290 (Claude, R108 + its correction) - the outlives rule: a block's kosh never goes to a prakriya that keeps it; a mala operand is refused; the arena is NOT on main

- **A `kosh` made in a `mandapa` may be passed only to a parameter that does not keep it** (does not return it,
  store it, or pass it to one that does - a greatest fixpoint over every `prakriya`; function values and foreign
  functions count as keeping). Otherwise `E_KOSH_MANDAPA` at compile time. With v289's escape error, no
  reference to a block's `kosh` can outlive the block. Example 316 is now that refusal; the R82 gate's five
  runtime cases are compile-time refusals (12/0).
- **`mala == mala`, `mala + 1`** (ChatGPT R175's reference-type class): `E_MALA_GANIT` (319). `kosh` operands
  were already `E_KOSH_GANIT` (v288).
- **`parimana()`** is the arena and the regions together; golden 318 shows it move.
- **Not on main:** the block-arena `kosh` (a slot of the block's arena, growth by a new slot). It was built before
  Sarvam's ROUND-108-CORRECTION and is on the review branch `claude/r108-arena-review`, as the correction asks.

## v289 (Claude, R107) - a kosh cannot leave its block (compile time); `parimana()` reports the bytes in use

- **The escape error:** a `kosh` declared inside a `mandapa` carries the block's depth as its scratch-escape taint,
  so storing it in a variable declared outside the block, writing it into memory, or returning it is
  `E_KOSH_MANDAPA` at compile time (the R73 rules, a `kosh`-specific message). Example 287 is now that refusal; the
  runtime form (R82) stays for a `prakriya` that keeps the `kosh`, golden 316.
- **`parimana()` / `परिमाण()`** returns the bytes held now: the arena's persistent and scratch sides plus each
  `kosh`'s header and capacity (a hidden counter, emitted only in programs that call `parimana`). Golden 317.
  Linux ELF; 0 on Windows.
- R107-00 prices the block-arena `kosh` design (not built): a slot costs about 21 instructions and no system call
  against a region's 14 and an `mmap`; kb1 0.02 s / 0 KB against 0.48-0.99 s / 400 MB; a `kosh` grown to 1,000 in a
  block leaves 8,656 dead bytes.

## v288 (Claude, R106) - `likha` prints a string's text; a string condition and a kosh operand are refused; a dasham into a mala is converted

- **`likha` on a string value prints its text** (a variable, `s + t`, a string-returning `prakriya`), with no
  newline, as a literal: `likha("concat: ", s + "cd")` prints `concat: abcd` (it printed `139381365014528`). The
  dispatch is at compile time from R105's kinds; numbers print as before. `--debug` ends a string value's trace
  line itself. Golden 312.
- **Muse's R101 traps**, the ones outside the `likha` emitter: a string as a condition (`yadi (s)`, `&&`/`||`,
  `?:`; `""` was true) is `E_VARTANI_SATYA` (313); a bare `kosh` in any binop (`a == b` compared addresses) is
  `E_KOSH_GANIT` (314); a `dasham` stored into a whole-number `mala` is converted exactly, `E_DASHAM_VITTI` for a
  fraction (315; it stored the IEEE-754 bits). Traps 1, 2 and 7 were closed by v286/v287. Not changed: 5
  (`likha(k)` - the `likha` emitter, left out of this commit as the brief asked) and 6 (a string in a `mala` - its
  element is untyped; `shabda(a[0])` prints it).
- A `kosh` made in a `mandapa` keeps its region for the program's life (unchanged; reasons in R106-00).

## v287 (Claude, R105) - strings work: `==` `!=` `<` `>` compare text, `+` makes a new string, `likha(a, " ", b)` prints three values

- **`==` / `!=`** between two strings compare bytes to the NUL (the node becomes `vartani_tul(a, b) ==/!= 0`, so
  the compare that follows is the ordinary integer one). **`<` `<=` `>` `>=`** order by the first differing byte.
  **`+`** between two strings allocates `len(a) + len(b) + 1` on the persistent side and copies both: the result
  lives for the program; `parimita` does not count it.
- **Which values are strings** is decided once per function, before code generation, from the whole program: a
  variable all of whose assignments are strings; a parameter every caller passes a string; a `prakriya` every
  `nivartanam` of which is one. Replaces v286's last-assignment flags (ChatGPT R173's P173-01/02/03: `s = s + s`,
  the fast paths disagreeing, a call result taken for an integer). Every register fast path now leaves a
  string-touching operation to the one generic rule.
- **Refused instead of guessed:** a string beside a number, or beside a variable that is sometimes a string
  (`E_VARTANI_TUL`, `E_VARTANI_CAT`); `-` `*` `/` `%` and bit operators on a string (`E_VARTANI_GANIT`, new).
  String +/- an integer stays pointer arithmetic.
- **`likha` with three values always prints three values** (v286's `E_LIKHA_TRAYA` is gone; raw writes stay
  `dvaram_likha`).
- Goldens 306 (equal), 307 (join), 308 (likha three), 309 (order), 310 and 311 (refusals). Reference 4a, 5a.
  Not tracked: module globals, `kosh`/`mala` elements, a `prakriya` used as a value - refused beside a string.
  `likha(s)` on a string variable still prints its address (`shabda` prints the text).

## v286 (Muse's FIXALL patch, applied by Claude, R104) - five silent wrong answers become refusals; a recursion guard

- **`likha(a, " ", b)`** (three arguments, the first not a string literal) printed nothing: now **`E_LIKHA_TRAYA`**
  at compile time. The raw write is the new builtin **`dvaram_likha(fd, buf, len)`** (returns the count); 57 tree
  sites renamed (`examples/215`, `217`, `lib/patra.smlib`, 54 tests).
- **`s == "ab"` / `!=`** on strings compared addresses: now **`E_VARTANI_TUL`** (use `vartani_tul`, 0 when equal).
  Also in `yadi` / `yavat` conditions and the fast paths. Not tracked: parameters, call results, `kosh` elements,
  module globals - with a literal on either side they are still refused.
- **`s + t`** on strings added addresses: now **`E_VARTANI_CAT`** (use `vartani_cat`). A string plus an integer is
  still pointer arithmetic (`base + 6`, `letters + grade - 65`: two tree programs use it); literal + literal folds.
- **`vitti x` / `dasham d` without a value in a function** read the slot's leftover (`0 99 99`): now **`E_MULYA_VINA`**.
  `mala`, `kosh` and module-level declarations unchanged. Zero tree programs affected.
- **Recursion past the stack** was a segmentation fault, exit 139: now **`E_GAHANATA`**, exit 1, from a check in every
  `prakriya` prologue against `mukhya`'s entry `rsp` (limit 8,339,456 bytes, about 4,000 frames; `yog(3900)` runs,
  `yog(4000)` refuses; v285 ran 4,000 and crashed at 4,100). Linux only; 15 bytes in `mukhya` + 115 per `prakriya`;
  50,000,000 calls: 0.10 s before and after.
- **The guard, v285 -> v286:** every Linux program that compiles differs (the prologue bytes); each was run old and
  new - see `Claude-to-Sarvam/R104-00-*.md` for the counts by kind. PE: byte-identical. Reference 4a, 5a, 6d, 20.
- Muse's report: `Muse-to-Sarvam/FIXALL-R100-TRAPS.md`. Native-speaker review of the new Sanskrit: NOT RUN.

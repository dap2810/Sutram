> **The 20 newest entries.** Older ones, from "v306" back to the first, are in [rounds/CHANGELOG-ARCHIVE.md](rounds/CHANGELOG-ARCHIVE.md) (split in R88).

## v326 (Claude, R190) - a `chakra` that has the shape of a countdown is warned about; `vartani_tak_ank` turns text into a number

- **The defect (found in R189): `chakra i = 5 tak e` with `e = 3` runs no times, with no message.** A `chakra`
  counts down only when both its ends are written as numbers; the compiler chooses the direction when it compiles
  the loop. `chakra i = 5 tak 3` is 5 4 3 - and `1 tak 0` is 1 0, `0 tak -1` is 0 -1; with any variable the loop
  counts up and is empty when the start is past the end. **Both books said "if the start value is greater than the
  end value, the loop counts down automatically" - corrected in both.**
- **Not changed, and why (measured):** a countdown and an empty range are the same thing when the loop runs
  (`5 tak e` and `0 tak n - 1` with `n = 0`). Counting down would run every loop over an empty collection twice;
  stopping would stop it - `examples/362` on an empty file. Refusing `5 tak 3` when compiled would refuse the
  documented countdown: 18 loops in 12 files. Of 591 programs that run, **one** enters a loop past its end, and it
  is the test that pins this behaviour (`examples/115_perf_loop_bottom`).
- **New: a warning for the shape that is nearly always a countdown** - a start that is not a number and an end that
  is, `chakra i = n tak 1`: `Sutram suchana: chakra 'i' urdhvam eva ganayati - arambhah antat adhikah chet ekavaram
  api na chalati; avarohaya 'yavat' likhatu`. On stderr, once per loop, the program unchanged; not in a `--lang`
  run. **None of the 787 guard programs has that shape.** `5 tak e` and `a tak b` cannot be warned about.
- **`vartani_tak_ank(s, ok)`** (`yoj vakyank`): the number a string holds, `ok[0]` 1 or 0. Strict: digits, one
  leading `-`. It reports `abc`, `5abc`, `12 34`, an empty line and an overflow, each of which `grahan()` turns into
  a number. **`varna_tak_ank`, named as the existing converter, does not take a string** (`"42"` gives 0, `ok` 0:
  it reads a code per eight-byte cell). Example `364_r190_vartani_tak_ank` with a golden; reference §4d; both books.
- **Gate `R190 chakra and converter`** (`tests/r190/test_chakra_and_converter.py`, 19 checks).
- **The guard, against v325:** the compiler's change is a message - no program's bytes change through it; the
  programs that bring in `vakyank` differ by the new function and print what they printed (R190-00). Installer
  rebuilt (payload v326). Not run on Windows.

## v325 (Claude, R188 + R189) - the audit's fixes in, the reference's false rows corrected, a live list of what is left

- **Library, two silent or fatal answers fixed** (ChatGPT R233; proved again here). `brihat_ank_tak_laghu` took a
  digit of -1 and returned -1; it now stops with its documented `E_MULYA_AYOGYA`. `laghuttam_samapavartya` (lcm) of
  (MIN, 0), (0, MIN) and (MIN, MIN) stopped the program from the gcd it calls; an lcm with 0 is now 0 and (MIN, MIN)
  is -1, as for any lcm that does not fit.
- **The verification tools made honest** (ChatGPT R233, ported onto the chain): the guard rejects crashes, timeouts
  and changed refusal messages; `doc counts` separates all gates from those that passed; `R124 lazy commit` reports
  NOT-RUN without Wine instead of PASS with no checks. Their four tests are now a gate, `R233 verification`.
- **The reference, every Tier 1 row of the audit** fixed or stated, each against a run: `likh8` / `pad8` move eight
  bytes; `likh8c` / `pad8c` are bounds-checked stores; `dvaram` opens and `paadh` reads, **both returning a negative
  error code, not -1** (measured -2 and -9 - R186's rows said -1); `aksharank`'s index is used; `vartani_tul` gives no
  order; `akshar` and its family work on bytes, ASCII only; `nirmmita`'s zeroing is from v320; `brihat_ank_se` leaves
  `x` alone for a bad base; `purna_prasaran`, `ekanka_gan` and `ganita_paripurna_*`'s other failures; the `madhya`
  example now sorts what it says it sorts; **the braces section said a brace-less `prakriya` holds one statement -
  false since v265**; and Tier 3 rows R03, R12, R19 (made precise, not removed: a value not known to be a string is
  true when empty), R26.
- **Found this round, stated, not changed:** **a `chakra` counts down only when both ends are written as numbers** -
  `chakra i = 5 tak e` with `e = 3` runs no times, silently (v315 too). Choosing the direction when the loop runs
  would make `chakra i = 0 tak n - 1` with `n = 0` run twice; the choice is the owner's. And a `chakra` that counts
  up to the largest `vitti` never ends (AUDIT-01 finding 6).
- **Documents:** a live `docs/WHATS-LEFT.md` (archived in R156; eight briefs named it); the ROADMAP's v261 status block
  marked as history, its "nothing ever returns memory" corrected; the README's counts, its Windows memory sentence (a
  block gives memory back on Windows too - measured) and a section on reading input; the books' `mala` paragraph
  (a `mala` in a loop is made once from v319: 256 bytes, not 51,200,000) and two English sentences an old rename had
  damaged ("operator sangrah", "the suchi of folders").
- **Gates `R189 audit fixes` (13 checks; 2 fail on v324) and `R233 verification` (21)**. **The compiler's bytes are
  v324's** - only its version string and comments changed; **the guard against v324 differs only where a program
  brings in `ganit` or `brihat`** (R189-00). Installer rebuilt (payload v325). Not run on Windows.

## v324 (Claude, R186) - `grahan()` reads a sign and an unfinished last number; reading a file, shown; two reference rows that said each other's job

- **`grahan()` lost a minus sign: `-5` read as 5** - a silent wrong answer (found R184, measured again: v323
  `-5` -> 5, `+5` -> 5). From v324 a `-` or `+` before the first digit is the sign (the last one wins; after the
  first digit both are still passed over, so `12-34` is 1234). The smallest `vitti`, `-9223372036854775808`,
  reads exactly.
- **`grahan()` lost a last number with no newline after it:** `42` then the end of input gave -1. From v324 it
  gives 42, and the next call gives -1.
- **`grahan()` now sets `nivesha_anta()` at the end of input** - it must, because a typed `-1` is now read as
  -1, which was `grahan()`'s only end sign. A loop of `grahan()` asks `nivesha_anta()`; the books' example does.
  `vartani_grahan()` is unchanged (it never had the unfinished-last-line defect - tested).
- **How:** the `grahan` code was written as hand-counted `db` bytes; it is now instructions in a macro, two
  flags on its stack frame (sign, a digit seen), and one jump whose length is computed from labels for the
  Linux and the Windows read. A program that uses `grahan` now carries the hidden `0nivesha_anta`.
- **Not changed, and stated in reference section 4d:** `5abc` is 5, `12 34` is 1234, `abc` is 0, a number past
  the largest `vitti` wraps.
- **Reading a file:** `examples/362_r186_patra_sankhya_yoga.sm` reads `examples/data/r186_sankhya.txt` by its
  path (`yoj patra`, `patra_path_sarv`) and sums its numbers (42); `363_r186_pankti_ganana_patra.sm` counts its
  lines given as the program's input (3). Both with goldens; the fixture is in the tree. Reference: "Reading a
  file", after section 4d; both books, a section after `vartani_grahan`.
- **The reference's `dvaram` row said "patra descriptor helper" and `paadh`'s "open a file": `dvaram` opens,
  `paadh` reads.** Corrected, with their arguments. Eight more rows corrected after measuring each: `pad`
  reads one byte; `likh8` and `pad8` move eight bytes, not eight bits; `likh8c` / `pad8c` are bounds-checked
  stores, not "print / read a character"; `aksharank`'s "index currently ignored" was false; `vartani_tul`
  gives equal / not equal, no order; three rows said "varna" where a string is meant.
- **Gate `R186 grahan and files`** (`tests/r186/test_grahan_and_files.py`, 24 checks; 10 of them fail on v323).
- **The guard, against v323: 7 DIFFER - the seven programs that compile and call `grahan`;** run on both
  compilers with five ordinary inputs each, they print the same; they differ on `-5` and on an unfinished last
  number, which is the fix. 582 identical, 196 refused identically, 2 new. Installer rebuilt (payload v324).
  Not run on Windows; the Windows executables run under Wine.

## v323 (Claude, R184) - `vartani_grahan()` reads a line of text; `nivesha_anta()` says the input has ended

- **`vartani_grahan()`** (वर्तनी_ग्रहण) reads one line from the input and returns it as a new string, without
  the line's newline (LF, or CR LF). `grahan()` reads a number - `hello` gave 0 - and there was no way to read
  text. An empty line is `""`. **No length limit:** the buffer starts at 64 bytes and doubles; a 5,000,000-byte
  line comes back whole.
- **`nivesha_anta()`** (निवेश_अन्त) is 1 once a `vartani_grahan()` found nothing left to read, and stays 1. At
  the end of the input `vartani_grahan()` returns `""` at once, every time; a last line without a newline is
  returned whole first. So `yavat (1) { vitti s = vartani_grahan() ; yadi (nivesha_anta()) { krama } ... }`
  ends at the end of the input and not at an empty line.
- **How:** two builtins (48, 49), generated inline; a byte per `read`, as `grahan` does, so the two share the
  input line by line. The memory is `nirmmita`'s ordinary side, as string `+` takes - at least 64 bytes a call,
  not given back (2,000,000 lines: `parimana()` 128,000,064; 5.1 s for 24.9 MB). The end flag is a hidden
  module `vitti`, made only in a program that uses either function.
- **Examples** `360_r184_vartani_grahan` (asks a name) and `361_r184_pankti_ganana` (reads to the end), both
  with goldens; reference section 4d; a passage in the English and the Sanskrit book beside `grahan`.
- **Gate `R184 read a line`** (`tests/r184/test_read_line.py`, 17 checks: a known line, an empty line, no
  input, a loop to the end, an unfinished last line, CR LF, 63 / 64 / 65 / 100,000 / 5,000,000 bytes, a number
  line then a text line, the string kind, the Devanagari names, three refusals).
- **The guard, against v322: 0 DIFFER** - no existing program's bytes change. Run under Wine (the name example
  and the loop). Installer rebuilt (payload v323). Not run on Windows.

## v322 (Claude, AUDIT-01 - the owner's audit) - five defects found by 150 probes

- **A `prakriya` that ends without `nivartanam` returns 0.** It returned whatever the last instruction had left:
  `prakriya f(a) { vitti b = a * 3 }` gave 15 for `f(5)`, and a `prakriya` that forgot `nivartanam s` after a
  summing loop gave the loop's bound. Now `xor eax,eax` at the end of a body whose last statement is not
  `nivartanam` (`a1_emit_fall_off`); a body that ends with `nivartanam` is unchanged.
- **`krama` and `agrim` outside every loop of their `prakriya` are refused: `E_AVARTAN_VINA`.** They compiled and
  did nothing.
- **A `mala`'s length is checked: `E_MALA_PARIMAN`.** `mala m[-3]` compiled and crashed (SIGSEGV), as did a computed
  negative length and one too large to have. A negative number written out is refused when compiled; a length
  that is not a small number written out is checked when the program runs, and so is the allocation. `mala m[8]`
  gets no new code.
- **`likha` with a `mala` among its values is refused: `E_MALA_LIKHA`.** It printed the `mala`'s address.
- **A `kosh` as a whole condition is refused: `E_KOSH_SATYA`** - as a string is (`E_VARTANI_SATYA`), and for the same
  reason: every `kosh`, an empty one too, was true.
- **The guard, against v321: 84 of the 783 programs DIFFER, in bytes only.** Every one was run on v321 and on v322
  and prints and exits the same; none is newly refused; 503 are byte-identical and 196 refused as before (ELF and
  PE). The 84 are programs with a `prakriya` that does not end in `nivartanam` (two bytes each, `xor eax,eax`) or a
  `mala` whose length is not a small number written out - most of them through the library they `yoj`.
- Gate `audit01 fixes` (23 checks; 15 fail on v321). Not fixed here: a `chakra` whose end is the largest number
  never ends (finding 6), and the eight unhelpful messages. Installer rebuilt (payload v322). Not run on Windows.

## v321 (Claude, R182) - a character the language does not know is refused where it stands

- **The defect** (Muse R166; Sarvam R182; in v315): the lexer skipped any character it did not recognise and
  carried on (`; Unknown char - skip`). `vitti a = 5 <en dash> 2` compiled and printed 5; a string in curly quotes
  was refused for an unknown *name*, away from the quotes; `$`, `@`, an apostrophe, a no-break space, a
  zero-width space, an emoji all vanished without a word.
- **Now** (`r182_unknown_char`, `src/sutram_compiler.asm`): `file:line:col: Sutram truti [E_AGYAT_AKSHAR]: agyat
  akshar '<the character>' (U+XXXX)`, the source line with a caret under the character, and a `Sanket` line when
  the intention is plain - a curly quote -> `"`, an en or em dash or a minus sign -> `-`, a no-break space -> a
  space, an invisible character -> remove it, `x`-sign -> `*`, and the like. A character that cannot be shown is
  named by its code point alone.
- **Not refused:** anything inside a comment (`#`, `//`, `/* */`) or a string - the lexer has left those before
  it reaches this point; a byte-order mark at the start of the file or of a line; Devanagari digits and names.
- **It is a behaviour change: a program that compiled only because a character was swallowed is now refused.**
  None of the 783 programs of the guard is one: 587 compile to the same bytes as on v320, and the 196 refused
  are refused with the same message (ELF and PE). Gate `R182 unknown character` (21 checks; 17 fail on v320).
- **Eight inputs of the crash corpus are refused differently:** mutated files with a NUL or another unknown
  character outside a string, which used to reach a later syntax error and are now refused at the character. The
  corpus runner accepted only a diagnostic that *begins* `Sutram truti`; it now also accepts the positioned form
  `file:line:col: Sutram truti [E_...]:` that this and other errors print (`tools/crash_corpus.py`).
- The release notes' first limitation (Muse's ranking) is closed by this. Installer rebuilt (payload v321).
  Not run on Windows.

## v320 (Claude, R175 + R176) - a block's memory is zero when the block is left - STAGED, A DECISION NOT YET TAKEN

- **The stale-data defect** (found R172; in v315): an ordinary `nirmmita` - and so a `mala` - is bounded by where
  the scratch cursor is now and is not zeroed, so after a block ended it could be handed memory the block wrote:
  15,782,272 words of 77 in a `nirmmita(600000000)` taken after a 600 MB block; a newly declared `mala m[8]`
  reading 77 in its first and last number (the two read). Now `r73_gen_rewind` and `r73_gen_ret_rewind` - the only two places the cursor
  moves back - zero `[cursor, mark)` first (`r175_emit_zero_to_mark`, `src/r65_arena.inc`: a plain loop up to
  1 KiB, `rep stosq` above). `nirmmita` itself is unchanged, so a block's memory is written twice.
- **Cost** (1,000,000 passes, best of 25 interleaved runs): a block of `nirmmita(64)` 5.5 -> 8.9 ms; the same
  loop with no block 27.7 ms. Ten 200 MB blocks written fully 921 -> 1,194 ms; written in their first 4 KiB
  389 -> 587 ms.
- **One pinned output changes:** `tests/r73_scratch/blind_kosh_via_call.sm` - the known limit, a scratch address
  kept through a `prakriya` and read after its block - printed 99 (the next block's data) and now prints 0. The
  address is still dangling; the pin and its comment say so.
- Gate `R175 block exit zero` (8 checks; 7 fail on v319: each way out of a block, then an ordinary `nirmmita` over
  the same bytes).
- **The guard: 38 DIFFER - exactly the 38 programs that compile and contain a `mandapa`**; every other program is
  byte-identical or identically refused, against v319 and against v315, ELF and PE. Of the 38, 37 print and exit
  exactly as before; the 38th is the pinned known limit above. Run under Wine; not run on Windows. Installer
  rebuilt (payload v320).
- **R181 (documents and a comment; the compiler's bytes are those of 9bb059ea):** reference §19 says the defect
  reached a `mala` declared inside a later block as well as one after it, and gives the 480 MB of ordinary memory
  the `mala m[8]` measurement needs; both books say a block's memory is cleared when the block ends; the release
  notes' limitations open with Muse's three items; the R73 pin's comment says what the 0 pins.
- **Why it is separate from v319:** it changes the bytes of every program with a block and costs time in every
  block; the alternatives (zeroing only at the exit; keeping the ordinary side out of memory a block has used;
  documenting the limit) are set out in R176-00.

## v319 (Claude, R175 + R176) - a proven-local `kosh` or `mala` is made once anywhere in a loop

- **The nested-block gap** (Sarvam R175 WS1; staged alone in R176): v317 / v318 made a proven-local `kosh` or
  `mala` once only when it was declared as a statement of a `chakra`'s own body. Now the declaration may be under
  a `yadi` or an `anya`, in a plain block or a `mandapa` inside the loop, at any depth (`r175_walk`), and the loop
  may be a `yavat` (`r175_while_enter`). The same name declared in a `yadi` and in its `anya` gets a slot for each
  declaration; a declaration that never runs makes nothing (the slot is zeroed at the loop's entry and filled only
  where the declaration runs); a `kosh` reused inside a `mandapa` gets this pass's block generation in its R82
  header. Not walked into: a loop inside the loop - it has its own entry.
- Measured, 800,000 passes (Linux x86-64, resident; time for 400,000 passes): under a `yadi` 37,516 -> 16 KB,
  8.7-9.9 -> 1.6-3.0 ms; in a `mandapa` inside the loop 50,012 -> 16-20 KB, 18-20 -> 8.2-9.5 ms (a `mala` there
  62,516 -> 16 KB); in a `yavat` 37,516 -> 20 KB.
- Gate `R175 nested made once` (16 checks; 13 fail on v318). Five "made every pass" shapes of the R172 and R173
  gates (under `yadi`, in a `mandapa`, `yavat`) are now "made once"; `R101 memory`'s pinned gap ("a `kosh` made in
  a block 100,000 times is not reclaimed") is closed for a proven-local `kosh` (under 1 MB) and re-pinned for one
  given to a `prakriya` (over 8 MB).
- Every program that compiled on v318, and on v315, compiles to the same bytes (guard: 783 programs, ELF and PE,
  0 DIFFER). Run under Wine; not run on Windows. Installer rebuilt (payload v319).
- **Not in v319:** zeroing a block's memory at its exits (the fix for the `nirmmita`-after-a-block defect). It is
  staged separately as v320 because it changes the bytes of every program with a `mandapa` and costs time in every
  block (R175-00, R176-00).

## v318 (Claude, R173) - a `mala` declared in a `chakra`'s own body is made once; the R172 audits answered

- **The 80 bytes a pass** (Sarvam R173 WS4; measured R168): a `mala` declared as a statement of a `chakra`'s own
  body, without an initializer, whose name appears in the loop only as the base of an index, is allocated on the
  first pass; every later pass with the same length finds it in its frame slot and zeroes its numbers
  (`rep stosq`) - a `mala` has no length to reset, so each pass must see zeros (`r173_mala_begin`,
  `src/sutram_compiler.asm`; the scan and the slot are R172's). A different length this pass: a new `mala`, as
  before.
- **No new refusal.** R173 asked for a `mala`'s escape to be refused first (`E_SCRATCH_ESCAPE`). It is not: a
  `mala` that is given to a `prakriya`, given a second name, returned or put into a `kosh` is simply not made once
  - it is a new `mala` every pass, as in v317 - so no program that compiled stops compiling and no two rows can
  become one (gate: five rows put into a `kosh` stay five).
- Measured (Linux x86-64): 800,000 passes of `mala m[8]` - 62,516 KB resident on v317, 20 KB on v318.
- Gate `R173 chakra mala` (12 checks; 6 fail on v317): ten shapes, the rows, and redzones around the `mala` over
  1,000,000 passes with every pass reading eight zeros.
- Every program that compiled on v317, v316 and v315 compiles to the same bytes (guard: 783 programs, ELF and PE,
  0 DIFFER). Run under Wine; not run on Windows. Installer rebuilt (payload v318).
- The three audits of R172 (growth, a `kosh` put into a container, nested blocks) are answered in R173-00; no
  code changed for them.

## v317 (Claude, R172) - a `kosh` declared in a `chakra`'s own body is made once, not every pass

- **The 48 bytes a pass** (Sarvam R172 WS2; measured R168): `chakra j = 1 tak N { kosh k[1] ... }` allocated a
  descriptor and a buffer every pass and kept them all. Now, for a `kosh` declared as a statement of the loop's own
  body and proven local to the loop, the first pass allocates and every later pass sets the length to 0 and goes on
  with the same descriptor, elements and region (`r172_for_enter`, `r172_decl_begin`, `r172_decl_end` in
  `src/sutram_compiler.asm`; the descriptor's address is kept in a frame slot zeroed at each entry to the loop).
  **The descriptor's layout is unchanged; nothing is zeroed and nothing is rewound** - a different mechanism from
  the scratch-cursor design R172 quotes, chosen because it has no high-water mark to get wrong (R172-00).
- **Proven local is a whitelist, not an escape analysis** (`r172_scan`): in the whole loop the name may appear only
  as the base of an index and as the first argument of `kosh_kship`, `kosh_yuj`, `kosh_hri`, `kosh_gan`,
  `kosh_shodh`, `kosh_rikt`, `kosh_iksh`, `kosh_apanay`. A second name, an argument of a `prakriya`, a slice,
  `kosh_ksham` (the capacity would show the reuse), a second declaration of the name, or any construct the scan
  does not know: the `kosh` is made every pass, as before. It fails toward leaking.
- Not covered, as before: a `mala` (80 bytes a pass), a `kosh` in a `yavat` loop, under a `yadi`, or in a `mandapa`
  inside the loop; a `kosh` in an inner `chakra` is made once for each entry to the inner loop. A block still
  returns no memory to the operating system.
- Measured (Linux x86-64): 800,000 passes, one number added each pass - 37,516 KB resident on v316, 16-20 KB on
  v317 (the program's baseline is 12-20 KB); the loop itself 5 ms -> 0.9 ms per 200,000 passes.
- Gate `R172 chakra kosh` (24 checks; 12 fail on v316): eighteen shapes (made once / made every pass, witnessed by
  `parimana()`), nesting, and the redzone test - 64 bytes of `0xDEADBEEFCAFEBABE` before and after the descriptor,
  1,000,000 passes, nested loops, a loop in a `mandapa`, growth to 20,000,000 three times, every redzone word and
  the four descriptor words exact after each phase; a refused growth under an address-space limit.
- Every program that compiled on v316 compiles to the same bytes (guard: 783 programs, ELF and PE, 0 DIFFER; 40 of
  them contain a `chakra`, none declares a `kosh` in one). The 18 shapes and both redzone programs compiled and run under Wine; not run on
  Windows. Installer rebuilt (payload v317).

## v316 (Claude, R163) - a file a tool read is never its output; an output that cannot be opened is an error

- **`E_NIRGAM_NIVESH`** (Sarvam R163 WS1; found R162, Muse R156): up to v315 `sutram hello.sm hello.sm` compiled and
  wrote the program over its source, exit 0; `--object`, `sutram-link a.smo a.smo`, `sutram-elf2smo a.o a.o` and
  `sutram-coff2smo a.obj a.obj` did the same, and `tools/sutram_build.py main.sm -o main.sm` (found here: the
  linker's inputs are the objects, so it cannot see the program) - the script now refuses by `os.path.samefile`. Every file opened for reading is now noted by its identity (`fstat`:
  device, inode; Windows `GetFileInformationByHandle`: volume, file index) - the program, `yoj` modules, the
  `--lang` pack, the `--ffi` file, and `--separate`'s root (opened and closed for this). The output is opened
  without truncation (`O_WRONLY|O_CREAT`; Windows `OPEN_ALWAYS`), its own identity compared with every input's, and
  only then cut (`ftruncate`; `SetEndOfFile`): no window between a check by name and the write (ChatGPT R225's
  design). An identity that cannot be read is refused too. A device (`/dev/null`, `NUL`) is written as before.
  `src/r163_same_file.inc` (new, used by the compiler, the linker and both object readers); `win/winrt.inc` resolves
  `GetFileInformationByHandle`, `SetEndOfFile`, `GetFileType`. Reference §7.
- **`E_NIRGAM_PATRA`** (found here; Muse R156 noted it for `--object`): an output that could not be opened - a
  missing folder, the running compiler - printed `Siddh`, exit 0, and wrote nothing. It is now an error, exit 1.
- Not changed, named in reference §7: the REPL's and the Linux IDEs' fixed scratch files; a write that fails
  part-way is not reported; the shell's own `>` empties a file before any program runs.
- Each input is noted once: `--debug` opens a module once for each statement it traces (542 opens of three files
  for `examples/import_demo.sm`), which ran past the 256-input limit in the first staged build and refused every
  `--debug` compile with a `yoj` (gate `R45 debug` found it; the guard compiles the ordinary way only).
- `tests/windows/accept_v316.cmd` (R167): the eighteen steps the owner runs on Windows before this is merged -
  18 of 18 under Wine on v316, 16 fail on v315; not run on Windows.
- Gate `R163 output collision` (35 checks; 25 fail on v315 - 22 cases, and 3 ordinary ones whose input v315 had
  already written over). Every program that compiled on v315 compiles to the same
  bytes (guard, ELF and PE). Run under Wine (22 checks); not run on Windows. Installer rebuilt (payload v316).

## v315 (Claude, R154) - the tree limit's code; the fold guard; ownership records, not flags

- **`E_VRIKSHA_SEEMA`** (Sarvam R154 WS4, Muse R151): the syntax tree's full message keeps its translated first line
  and adds a coded line, naming `E_VAKYA_SEEMA` as the other limit, with a remedy that works (a smaller program or
  fewer modules; splitting a statement does not shrink the tree - ChatGPT R218). The analysis-limit hint names
  `E_VRIKSHA_SEEMA`. Gate `R152 analysis steps` (42).
- **The fold's identity guard** skips a slice or a value holding a `kosh` (Muse R150): `k[0:1] + 0` cannot fold to a
  bare slice even if the walk ever stopped refusing it. Nothing that compiles changes (guard: 0 DIFFER).
- **Installer ownership, every record a record of what was done** (R154 WS1-WS3): `PathAdded` (the text of the one
  entry this install added; uninstall removes that one entry, not every equal one; the installer adds nothing when an
  equal entry is there), `AssociationSet` (the value set, carried only while it is still the default), the
  `Sutram.Source` class removed value by value and key by key only when empty (v314 removed the whole tree), and the
  shortcuts by their bytes (R153). A shortcut recorded without a hash (before v315) is not ownership: kept, never
  adopted on a field-by-field match (ChatGPT R220; gate 21 checks). `PathOwned`, `AssociationOwned` and `DesktopOwned` are still written, derived from
  the records, and nothing acts on them. Gate `R143 installer first contact` (21).
- Guard v314 -> v315: ELF and PE 587 identical / 196 refused / 0 DIFFER; refusal messages unchanged.
- **R155 (installer only; the compiler stays v315):** `.sm` and its `OpenWithProgids` are opened, no longer remade
  with `New-Item -Force` (which deleted a user's existing `.sm` key, their association with it, before the default
  was read); `AssociationBefore` records an empty default so uninstall restores it; PATH changes by one entry and
  one separator, keeping the other entries' text and the value's kind, and `PathValueCreated` lets uninstall remove
  a PATH value it made. Gate `R143 installer first contact` (24). The gate harness keeps a failing gate's whole
  output (`$TMPDIR/sutram-gate-failures/`); R126's Wine check prints stdout and stderr apart on a failure.
- **R155 follow-up (ChatGPT R221 follow-up):** `PathValueCreated` is carried from the old record only when the old
  PATH entry was kept; when it is appended again (same text, after the user removed it) it records what this run did.
- **R163, the installer lock (ChatGPT R225):** nothing already at `<folder>.sutram-lock` is removed - not an empty
  file, not a marked one; the run stops and says whether another installer holds it, and how to recover. R162 had
  removed an empty or marked file as stale. Gate `R143 installer first contact`; fixture cases 3-4 now expect refusal.
- **R167 (documents and gates; the compiler unchanged):** `docs/MEMORY-MODEL.md`'s status box corrected in ten
  places after Muse R158 - what a `mandapa` gives back (only `nirmmita` written in it; not a `kosh`, never a `mala`),
  the descriptor's four fields and its size (32 bytes, 56 with R82), the budget's rounding, scope and line, a block
  `kosh` may be read by a `prakriya` but not kept, `parimana()` counts capacity and what the program asked for, the
  Windows handler commits up to 64 KiB, two Windows figures marked as reported not measured, and two stale paragraphs
  of the old body marked superseded. The reference's descriptor sentence names all four fields. `R158 doc currency`
  check 10, `fields`: a paragraph listing the descriptor's fields must name all four and give the size. New gate
  `R167 evidence manifests`: the eight Windows evidence manifests are read - every entry is the bytes recorded or
  explained by a normalisation or removal record; an unrecorded change to evidence fails it.
- **R166 (documents, the gates, the tree; the compiler unchanged):** the memory chapter (both books) says what a
  block gives back - `nirmmita` written in it, yes; a `kosh` made in it, no (it keeps its bytes; only its life ends);
  a `mala` made in it, never (and returning one is not refused) - its title and section 7 no longer say "memory"
  unqualified, `agrim` is among the ways a block ends, and a budget counts each `nirmmita` rounded up to 16
  (`parimita 1000` refuses one `nirmmita(1000)`); each measured on v315 first. Reference: a `mala` in a block.
  `R158 doc currency` check 9, `figures`: a replaced measurement (52,760 / 13,480 KB, 392 KB, "308 or 436") may not
  be given as current. `R159` decodes UTF-16 and `\u` escapes, reads lower-case drives, kernel builds, IPv4 and MAC
  addresses, checks file names fully, never prints a name, and fails on a file it cannot read; it found 36 files the
  first version passed (21 UTF-16), now normalised. `tools/normalize_personal_paths.py` checks every rewrite before
  writing and refuses an unsafe one (ChatGPT's R226 follow-up). `tools/verify_evidence_manifest.py` explains a
  manifest's digests after normalisation; a note sits beside each affected manifest, and 116 links to a removed
  screenshot say so.
- **R164-R165 (the tree, documents and a gate; the compiler unchanged):** the owner's system details - home folder,
  account and computer names, the projects drive, OS build numbers, the CPU - and the build machines' own folders are
  replaced in 806 tracked files, keeping what each line says (`%USERPROFILE%`, `<repo>`, `<scratch>`, "(build
  redacted)"); the digests before and after are in `Claude-to-Sarvam/evidence-r164/normalization-record.json`. The
  history still holds the old text. Gate `R159 no personal paths`; the rule is in `AGENTS.md`. The memory chapter
  says where a block must be: around a loop it gives memory back only when the loop is over (49,920 KB, as no
  block); ended on every pass, 264 KB; memory a called `prakriya` makes outside a block of its own stays.
- **R163 (documents and a gate):** the memory chapter's section 1 said a `kosh` "grows each time you add to it" - it
  grows when it is full, doubling its room; the chapter now says what capacity is, and why `parimana()` gives 96 for
  five numbers. The block's peak: 264 KB in 75 runs of 75 started with an empty environment (`env -i`), between
  264 and 436 KB started from a shell - at that size the count is mostly the program's pages and its environment
  (the chapter said 392, one run; R163 first said "308 or 436 over 75 runs", from 55 recorded runs in one shell);
  without the block, 49,920 KB (75 of 75). The reference gives the descriptor's layout: 32 bytes, 56 when a program makes a
  `kosh` in a `mandapa`. `R158 doc currency` check 8, `sizes`, measures both with `parimana()` and holds every size a
  document gives to them.
- **R162 (the installer, ChatGPT R223):** nothing changed before what decides it is read. The lock beside the
  target is made with `CreateNew` and marked; a file already there is read first, and only a stale Sutram lock is
  removed (up to R161 any file at that path was deleted when the lock closed, even by a run that then refused).
  `-VerifyOnly` returns before the lock and the committed-transaction cleanup. Finishing an interrupted run replaces an
  existing uninstaller only when its bytes are ones an installer wrote (the uninstaller's hash is journaled before it
  is copied). Gate `R143 installer first contact` (28); fixture `tests/windows/test_installer_lock_file.ps1`
  (NOT RUN). Five more reference sentences corrected (ChatGPT's 13-17) and added to `R158 doc currency`.
- **R161 (documents, a gate, the uninstaller):** the nineteen reference claims Muse found wrong (R152-R154), each
  checked against the code: fifteen corrected in the reference and the memory model (the memory model's historical
  sentences keep their text and gain a "Superseded (R161)" note); two were already right in R156's box (1, 14); two
  are true and stay, with their evidence (8: the crash was run in R152; 15: `likh` is refused through
  `.pp_writemem`, R74). None needed a compiler change. Gate `R158 doc currency` gains a seventh check,
  `reference`, which runs the compiler where a claim is measurable. The uninstaller keeps the Settings entry, the
  manifest, the state and the marker until it has deleted itself, so a retry after the self-delete loop runs out
  works (ChatGPT R221). `AGENTS.md` records that cited evidence stays and history is not rewritten.
- **R157-R158 (documents and a gate):** the English and Sanskrit books have a memory chapter (19: `kosh` beside
  `mala`, `mandapa` with a measured number, `parimana()`, `mandapa parimita`, slices with `E_KOSH_VIBHAG` and
  `E_VIBHAG_ANKA`, running out of memory, what the language does not have); chapter 14 is retitled (it said "New
  Features: v22"); three book programs that failed on v315 are fixed (chapter 8 wrote past its `mala` - `tak` includes
  its last number - and two used `mahattam`, renamed in v292); chapter 18's "no IDE on Windows" and "Windows has not
  been run" are corrected; the Hindi, Tamil, Telugu and Gujarati books are marked archived at v294. **New gate
  `R158 doc currency`** (versions, symbols, the books' programs, compiler flags, the memory chapter, the changelog);
  it failed 3 of 6 on v315 as it stood. `AGENTS.md` carries the rule: docs are part of the change.
- **R156 (documents only):** `WHATS-LEFT.md`, `OPEN-ISSUES.md` (both last true at v258) and `WINDOWS-PORT-PLAN.md`
  archived in `docs/rounds/`; the open list is the release notes'; the reference's status box, stale since v300,
  is current; the release notes state the shipping condition; `Windows-to-Sarvam/win-v297-2026-11-03/Sutram-Setup-v297.exe`
  removed, its SHA-256 kept beside it.

## v314 (Claude, R152) - the foreign-function door; --analysis-steps=N; the two limits named; the desktop collision

- **A slice to a declared foreign function** (Sarvam R151; Muse's reading): `r33_gen_foreign_funcall` generated
  each argument with no door check, and the walk leaves `kosh` values at an argument to the door. v313 compiled
  `k_sum(k[0:2], 2)` and C read the descriptor (printed an address); as an `i64` count it crashed. Now refused,
  `E_KOSH_VIBHAG` (`tests/r147/slices/15_ffi_argument.sm`; gate `R137` 91 checks, with the mutants).
- **`--analysis-steps=N`** (R149-R150, ChatGPT R214-R217): default 200,000; 1..2147483647, one token with `=`,
  overflow checked before it can wrap, a second occurrence or a separate value refused (`E_PARIKSHA_PADANI`);
  every walk starts from N. The exhaustion message names N and the prakriya and says the syntax tree's limit is
  separate; the tree-full message says the reverse. The widest statement the tree holds takes exactly 87,316 steps.
  Gates `R152 analysis steps` (40) and `R143 walk budget` (7).
- **Installer** (Windows v312 first-run paths): a user's own desktop `Sutram IDE.lnk` is kept and the installer's
  is `Sutram IDE (Sutram).lnk`, recorded and removed only when it points at this IDE; the checkbox names the IDE.
- **The release binaries are the plain builds**, checked by gate `R137`: no mutant define, no lowered budget.
- Guard v313 -> v314: ELF and PE 587 identical / 195 refused / 0 DIFFER (783 programs); refusal messages unchanged.
- **R153, the package rebuilt (compiler unchanged): shortcut ownership** (ChatGPT R218 follow-up). v314's first
  package could delete a user's own desktop link on uninstall (preserved by the helper, recorded as owned by the
  caller, deleted on a matching target) and overwrite a link the user changed. `Set-OwnedShortcut` now decides and
  records in one place; ownership is the .lnk's SHA-256 as written; uninstall removes only links whose bytes match.
  Gate `R143 installer first contact` (16); native fixture `tests/windows/test_installer_shortcuts.ps1` (NOT RUN).

## v313 (Claude, R147) - the walk budget a defensive stop; the fourteen slice shapes; the licence label, the staging folder

- **Fourteen ways of keeping a slice past a growth, in one table** (Sarvam R147 Task 4): the ten found and closed
  and four new - a comparison used as an index, two prakriyas in sequence, a kosh element, inline machine code.
  On v313 (Linux, and the Windows compiler under Wine) all fourteen are refused at compile time; on v307, eleven
  compiled (eight read the old elements, one crashed, one leaked a descriptor's address, one compared an address). `tests/r147/slices/`,
  and in gate `R137 slice is not a number` (89 checks) with both mutant compilers.
- **The expression check's budget** (Task 1; ChatGPT R212): 349,521 = 8 x (AST_HEAP_CAP / AST_NODE_SIZE) + 1, the
  most a statement the syntax tree can hold can take. v312's 65,536 refused 8,200-16,400 terms the tree holds; now
  the widest, 21,829 terms, compiles. `E_VAKYA_SEEMA` says it is an internal limit and a compiler defect: report
  it, split the statement. The refusal is tested with a `-DR143_WALK_BUDGET=64` build; gate `R143 walk budget` (6).
- **Installer** (Windows v312 acceptance): the licence instruction label is two lines high and the licence box
  starts below it; uninstall removes its `%TEMP%\STMxxxx.tmp` staging folder on success - in TEMP, with the
  wizard's name, holding exactly its script and log, by exact paths. Gate `R143 installer first contact` (12).
- Guard v312 -> v313: ELF and PE 587 identical / 181 refused / 0 DIFFER (782 programs, 14 new); refusal messages
  unchanged.

## v312 (Claude, R143) - the walk budget reachable; the licence page, the uninstall window, the empty key

- **The expression walk's budget** (Sarvam R143 WS1; ChatGPT R211: the nesting probe measured the parser). R141's
  "200000 can never be reached" compared nodes with steps: the walk spends a step on every entry it pops. Measured
  on v311: the widest statement the AST heap holds, 21,829 terms, takes 87,316 steps; the largest walk in the 768
  programs takes 52. The budget is now `R143_WALK_BUDGET`, 65536: a 20,000-term statement, or module initializer,
  is refused with the release compiler (`E_VAKYA_SEEMA`, exit 1, no output; the message names the number), 10,000
  terms compile, and a `-DR143_WALK_BUDGET=64` build refuses 40 terms. Gate `R143 walk budget` (7 checks).
- **Installer, from the Windows v311 acceptance run** (gate `R143 installer first contact`, 10 checks):
  - the licence page: `license_to_utf16` widened UTF-8 byte by byte (U+2014 EM DASH showed as three characters,
    every Sanskrit line as noise) and kept bare LF, on which an EDIT control does not break. It now decodes
    UTF-8 and writes CR LF; the gate runs the wizard's own function on the embedded licence against a reference;
  - the uninstall script starts with `CREATE_NO_WINDOW`, and shows its own failure in a message box with its log;
  - the uninstaller removes `HKCU\Software\Classes\.sm\OpenWithProgids`, then `.sm`, only when empty.
- Guard v311 -> v312: ELF and PE 587 identical / 181 refused / 0 DIFFER; refusal messages unchanged.
- R144 (no compiler change): the margin, measured - the largest statement in the 344 examples and 310 library
  functions takes 52 steps and 11 terms, the most terms 12; 65536 is reached only by 8,200-16,400 terms. Margin
  1,260x in steps. The gate now checks every example and library under a budget of 64. Evidence scope rewritten.

## v311 (Claude, R142) - the check inside expression code generation, its own stack, no delete on a name

- **`gen_expr` carries the expression check** (Sarvam R142 WS1; ChatGPT R209: the R141 gate counted two calls and
  could not see a third entry that skipped them). `gen_stmt` and `r56_gen_global_initializers` walk, then generate
  with `r142_checked` raised; `gen_expr` generates without a walk of its own only while it is raised, and walks
  anything else first, its own value counted as a number. Over all 768 programs only two compiler-made diagnostic
  calls reach it that way, and they pass. Gate `R137 slice is not a number`: 74 checks - the shape read from the
  source, and two mutant compilers whose entries forget the walk (`-DR142_MUTANT_NO_STMT_CHECK`,
  `-DR142_MUTANT_NO_GLOBAL_CHECK`) still refuse every negative; v310 with the initializer's walk removed compiles C1.
- **The walk has its own stack.** `r126_ret_kind`, run for the first time in the middle of the walk, reused
  `rfx2_stack` and overwrote the nodes still to be checked: on v310 `likha(((m[0:2] * 1) * 1) + (f() + zero))` in a
  `prakriya` defined before `f` printed an address, and ChatGPT's S4 probe in that shape read 7 while `k[0]` was 99
  (the shared stack was noted in the Windows branch, PR #68; reproduced on main here). Both refused now.
- **Installer:** a target is deleted at publishing only when the copy kept under its `_superseded` name has the same
  full SHA-256 (ChatGPT R209 I2c); otherwise the run stops and both are kept. From PR #68: a reused target that
  changed or disappeared is refused before it is moved, and every target is checked for a reparse point. PR #68's
  two native fixtures are in `tests/windows/`, with a new one for the interruption boundaries (not run here).
- Guard v310 -> v311: ELF and PE 587 identical / 181 refused / 0 DIFFER; the 181 refusal messages unchanged.

## v310 (Claude, R141) - the module-level initializer, the lock before every read, a check that cannot pass unfinished

- **Module-level `vitti` initializers** are not statements, so `r137_check_stmt` and the module-vitti door never
  saw them (ChatGPT R208 C1, confirmed on v309): `vitti leaked = make_kosh() + zero` held a kosh descriptor's
  address, and `vitti g = make_kosh()` put a kosh in a module vitti. `r56_gen_global_initializers` now runs both
  checks on each initializer before generating it (`E_KOSH_GANIT`, `E_KOSH_DVARA`). Gate `R137 slice is not a
  number`: 64 checks (v309 fails the 4 new negatives). No other non-statement expression exists in the language
  (no constants, field defaults, default arguments, module-level kosh or mala - each a syntax error, measured).
- **The expression walk's node budget** now refuses when it runs out (`E_VAKYA_SEEMA`) instead of passing. It is
  not reachable today: the AST heap holds at most 43,690 nodes (3 MiB / 72 bytes), the budget is 200,000.
- **Installer (R208 I2 follow-up):** the lock is taken before every installation-state read - the registration,
  other installations, the state file, the pending record, the journal; gate `R134 install transaction` checks
  each read, and fails on v309's engine.
- Guard v309 -> v310: ELF and PE 587 identical / 181 refused / 0 DIFFER; the 181 refusal messages unchanged.

## v309 (Claude, R137 + R138) - a slice is not a number; the installer's lock and ownership

- **R139-R140 follow-up, same compiler (v309), installer rebuilt:** `.gitattributes` makes every text file the
  installer carries LF in every checkout (a Windows checkout had CRLF Markdown - 153 payload files differed from a
  Linux build); `tools/build_installer_linux.py` writes LF text and fixed ZIP dates (`1980-01-01`) and links the
  wizard without a timestamp, so the same tree gives the same `Sutram-Setup.exe` from any checkout;
  `build-installer.ps1` normalizes to LF too (after ChatGPT's PR #67, which is not merged: its compiler and runtime
  changes are on main differently since v308); the engine stages only files whose installed bytes differ (a late
  retry restaged all 657); gate `R140 package` checks the embedded ZIP against its manifest. The release notes
  gain a status section: what is measured, and what is not claimed.

- **A slice is not a number** (ChatGPT's R207 follow-up S4; Sarvam measured it on v308): `k[0:1] + zero` printed the
  descriptor's address, and `keep(k[0:1] + zero)` with an untyped `keep` read the kosh's old elements (7 while
  `k[0]` was 99) - the operator made the slice a number before any door saw it. `r137_check_stmt`, run on every
  statement before it is generated, refuses a slice (a `kosh`'s or a `mala`'s) as an operand of any `AST_BINOP`
  (every operator, unary `-` and `!` included), a condition, a loop bound, an index, a builtin argument (only
  `pankti_gan` takes one), a cell or raw store, and an untyped or function-value argument (`E_VIBHAG_ANKA`); a
  `kosh` made a number by a call or `?:` is `E_KOSH_GANIT`. Gate `R137 slice is not a number` (59 checks; v308 fails
  53, every negative); it fails if the compiler defines an operator it does not test. Refusal gates now require an
  unsuccessful compiler exit. Guard v308 -> v309: 0 DIFFER on ELF and PE (no emitted code changed).
- **Installer (R207 follow-up I1, I2):** the lock is a file beside the installation, taken before any state is read
  and held until the process ends (DeleteOnClose), and the uninstaller takes it too; every target is checked again
  just before it is replaced, and one changed meanwhile is kept and stops the run; a stopped run's own copy is
  moved aside (`_superseded`), not deleted; `*.sutram-partial` files are no longer deleted on their name.
- **Windows runtime:** a test runtime with the start-up reserve refused (`-DR137_FAIL_RESERVE`) exits as v307 did
  (message, exit 1) - gate `R133 handler registration`, 5 checks. The shipped runtime's bytes are unchanged.

## v308 (Claude, R134 + R135) - one predicate for the slice's doors; the stack after the OOM message; a journaled install

- **A slice of a `kosh` goes through no door a `kosh` may not** (ChatGPT R207). Each door - a cell or field store,
  a module `vitti`, an untyped or function-value parameter, a raw store, a builtin's other argument, a phal
  result - asked `r126_is_kosh_value` (kinds 2, 3, 6), which does not know a slice (kind 1). Reproduced on v307:
  `box[0] = k[0:1]`, `keep(k[0:1])` with an untyped `keep`, `G = k[0:1]`, `kosh_kship(h, k[0:1])` and a slice
  forwarded through a `vibhag` parameter into the caller's `mala` all compiled, and a write through the kept slice
  was lost (printed 7). Now every door calls `r134_holds_kosh` (a kosh, or a slice of a kosh, of a slice name or
  of a `vibhag` parameter, or such a name), and only it calls `r126_is_kosh_value` - gate `R134 one predicate`
  fails if a new door asks the old question. A slice to a function value is now refused outright (its parameters
  are untyped): `tests/r133/indirect/safe1.sm`, which compiled in v307, is the one program the guard shows changed.
- **Windows out-of-memory exit:** the runtime commits 64 KiB at start and releases it before writing
  `smritih na labdha` (native v306: `STATUS_STACK_OVERFLOW` after the message at 512 MiB and for `mandapa` at 64 MiB,
  6 of 6 - the commit left after the failure could not grow the stack for the exit). Gate `R133 handler
  registration` adds a test runtime whose every lazy commit fails (message, exit 1, under Wine). Every PE changes.
- **The installer is a journaled transaction** (R207 WS3): `<folder>.sutram-transaction` beside the installation
  holds a write-through journal (BEGIN before any change), the staged files (START/DONE per file, hash-checked)
  and backups; files reach the installation only by rename; a rerun finishes from the journal; files that are not
  the installer's are listed and kept. Replaces v307's pending-manifest-and-partial-copy scheme. Gate `R134 install
  transaction` (replaces `R133 interrupted install`; v307 fails 16 of 19). The wizard writes to the engine log when
  its 15-minute stop fires. `tests/windows/test_installer_e2e.py` adds a user-file conflict case.
- `sutram-link.exe` rebuilt. No Linux program changes bytes except `safe1` (now refused).
- **R136 follow-up, same compiler (v308), installer rebuilt:** the engine's and uninstaller's log is appended through a
  fully shared stream, and a line that cannot be written no longer stops the run (Add-Content failed while a reader
  held the log - ChatGPT's v307 fixture). Muse R136's thirteen escape programs join gate `R134 one predicate`
  (v306 fails all sixteen escapes, v308 none). The release notes name Acronis Active Protection as what suspended
  the v306 and v307 upgrades (its own log).

## v307 (Claude, R133) - a slice through a function value, the handler that was never checked, the interrupted install

- **A `kosh` slice through a function value** beside an argument with a call is `E_KOSH_VIBHAG`, as for a direct
  call (ChatGPT R205-206 S3, found by reading; reproduced here on v306: `f(k[0:1], kosh_kship(k, 8))` printed `0`
  and `7` - the write went to the old elements - and the 64 MiB form crashed, SIGSEGV). `r129_check_call` left at
  once for a call through a variable. A function value can reach a `kosh` only through its arguments, so the
  argument-order rule is applied to it; `f(k[0:1], 5)` still compiles and writes through. Gate `R133 indirect
  slice` (v306 fails 5 of 10). No existing program is newly refused (guard: 584 ELF identical, 0 DIFFER).
- **Windows: a failed `AddVectoredExceptionHandler`** stops the program with `Sutram truti: smriti-prabandhah na
  arabdhah` and exit 1 (R205-206 W1). v306 did not test the result and would run on with no handler: under Wine,
  a test runtime with the registration failing exited 5 (an access violation) with no output. Gate `R133 handler
  registration` builds that test runtime in a scratch copy and runs it under Wine. Every PE changes bytes (the
  runtime, 1165 → 1290 bytes); all run the same under Wine.
- **The installer finishes an installation that stopped part-way** instead of refusing it: the first change to the
  folder is `payload.pending.sha256`; files matching the previous manifest, the pending one or the new payload are
  its own; each file is named in the log before it is copied and written as `<name>.sutram-partial` first; an
  upgrade overwrites in place and deletes only files the new payload lacks (v303-v306 deleted all first); the
  uninstaller removes a pending installation's files. Windows is told `1.0.307`, not `0.1.0`. Gate `R133
  interrupted install` (v306 fails 14 of 16); `tests/windows/test_installer_e2e.py` stops an install at file 132.
- `sutram-link.exe` rebuilt (it embeds the runtime). No Linux program changes bytes.

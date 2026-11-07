> **The 20 newest entries.** Older ones, from "v290" back to the first, are in [rounds/CHANGELOG-ARCHIVE.md](rounds/CHANGELOG-ARCHIVE.md) (split in R88).

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

## v306 (Claude, R130 + R131) - the Windows out-of-memory path, the installer, the IDE's stale screen

- **Windows: a refused commit is a message and exit 1** (`Sutram truti: smritih na labdha`, stderr), not an access
  violation with no output. The runtime's exception handler commits reserved memory on first touch (v300); when
  `VirtualAlloc(MEM_COMMIT)` failed it passed the fault on, and the program died (`0xC0000005`, native Windows, 64-256
  MiB job commit limits - the Windows v305 run). The fix is ChatGPT's PR #66, reviewed here and taken as it is: the
  handler's Win64 frame and calls checked, the runtime regenerated byte for byte. Every PE program changes bytes
  (the runtime); every one prints the same under Wine. `tests/windows/test_commit_oom.py` (PR #66) is the native probe.
- **The installer:** it refuses while another Sutram is installed where a terminal could find it (machine or user
  PATH, or `%LOCALAPPDATA%\Sutram`), naming it; with Add to PATH it finishes only when `cmd.exe` with a new
  terminal's PATH runs this compiler and prints this version; the engine runs with no console window,
  `-NonInteractive -ExecutionPolicy Bypass`, no progress bars or prompts, logs each step and every 100 files, and the
  wizard stops it after 15 minutes (it waited forever). Gate `R130 installer engine`; `tests/windows/test_installer_e2e.py`.
- **The Windows IDE:** a refused load (too large, unreadable) clears the output pane and says the editor still holds
  the previous file. Driven under Wine and Xvfb: v305's IDE showed the previous program's output with the refusal
  appended; v306's shows only the refusal and the notice. `tools/build_ide_linux.py` builds it on Linux.
- **The Windows harness:** `79_ayojan_cwd` runs the root `sutram.exe` (its `lib/` beside it) from a folder outside the
  project, as the Linux suite runs the root compiler from `/tmp`. The compiler is unchanged.
- `sutram-link.exe` rebuilt (it embeds the runtime). No Linux program changes bytes.

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

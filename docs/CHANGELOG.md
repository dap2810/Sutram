## v91 — Linux GUI IDE, slice 3: it types

- **The X11 client is now an editor.** Slice 2 could paint panes and labels but
  could not be typed into. Slice 3 adds an editor buffer, key handling, and a
  per-line repaint: printable characters insert at the cursor, backspace
  deletes, Return opens a new line, Escape quits, and the caret is drawn as a
  bar at the right position.
- **A real keycode table, not arithmetic.** My first pass mapped characters as
  `keycode - 8`, the folklore convention. It is wrong on a real server: XKB
  puts `a` at keycode 38, not 105, so typing would have produced garbage.
  Replaced with the standard US-QWERTY XKB table, verified by reading the
  bytes back out of the built binary — keycode 31 really is `i`, 43 is `h`.
  A non-US layout still needs the server's own mapping via
  `GetKeyboardMapping` (opcode 101); that is slice 4.
- **The bug was in my test, not the client — the fourth time that has
  happened in this project.** The suite reported "typing 'i' produced 'hi'"
  as failing. I instrumented the client to print every character it inserted:
  `['h', 'i', 'h']` — insertion was correct all along. The test read
  ImageText8's length from `body[0]`, but `body` excludes the 4-byte request
  header, so `body[0]` is the first byte of the window id. That is why every
  label appeared as a single character — `S`, `E`, `O`, `C` for the four
  labels. Reading `n` from the header byte fixed it. **Check the check before
  reporting a defect.**
- **Verified by a mock X server, 35 checks, no display needed.** Beyond the
  protocol shapes, the tests now drive real typing: send `h`, expect `h` drawn;
  send `i`, expect `hi` on the same line; send backspace, expect `h`; send
  Return, expect the text to split. A negative test confirms the suite fails
  when the keycode table is deliberately corrupted.
- **Honest limit, unchanged:** this proves the protocol and the editing logic.
  It does **not** prove the window renders or that the caret sits where it
  looks right — only a real display shows that, and the visual check is the
  owner's.

## v90 — Linux GUI IDE, slice 2: it draws

- **The X11 client now paints.** Slice 1 could connect, handshake and map a
  window but never drew anything. Slice 2 adds a graphics context, a
  ChangeGC colour path, and an Expose-driven repaint that draws the window
  background, an editor pane, an output pane, a teal rule and four labels —
  then exits on a keypress.
- **Three real bugs found, two of them in code I had already shipped as
  verified.**
  - The **CreateWindow request declared `length = 8`** while its body is 36
    bytes = 9 units, because it carries a value-mask and one value. A real X
    server would have misparsed it. Slice 1's test asserted `8`, so the test
    **agreed with the bug** instead of catching it.
  - `set_fg` built a ChangeGC request but **never sent it**, so every pane
    would have been drawn in the initial colour.
  - `new_id` masked the resource-id *base* with the resource-id *mask*, which
    strips the base and yields id 1. The id must be `base | (n & mask)`.
- **The mock X server was rewritten to be length-driven.** It no longer
  asserts hard-coded lengths; it reads the declared length, pulls exactly that
  many bytes, and checks the request is self-consistent with its opcode. That
  is what let it catch the id bug the old test had blessed. I confirmed the
  new test fails when I deliberately reintroduce the bad length and passes
  when I restore it — **31 checks, all green**.
- **Honest limit, unchanged:** this proves the protocol bytes are correct and
  that the repaint emits the right requests. It does **not** prove the window
  renders or that the layout looks right. Only a real display shows that, and
  the visual check is the owner's.

## v89 — documentation brought back in step with the language

- **The README was truncated.** It began mid-sentence at `## Windows (native)`
  with no title and no opening — it had lost its head at some point. Rewritten
  in full: what Sutram is, why it exists, the keyword table, what ships, how to
  run it on each host, how to build the compiler, and an honest status section
  that states the known limits instead of burying them.
- **The library chapter in all six books said four modules ship.** Twelve do.
  Corrected in each edition's own language, pointing at the generated library
  reference rather than duplicating a table six times.
- **My own figures were overstated and are now corrected.** I had been claiming
  fifteen library modules. Three of those files — `array`, `io`, `net` — are
  comment-only design sketches with no code in them. The honest count is
  **twelve modules with code, 103 functions**, plus three sketches. The README
  and scorecard now say that.
- **Four superseded book editions archived.** `docs/sutram-book.html`, `-2`,
  `-3` and `books/sutram-book-indian.html` had drifted well behind the current
  editions and nothing linked to them. Rather than leave stale content or
  silently delete history, each is now a short page listing the current
  editions — so any old link or bookmark still lands somewhere useful.
- **A real HTML bug found while checking the result.** The English edition had
  `<code>lang/<language>.lang</code>` — an unescaped literal tag, so browsers
  swallowed it and the text rendered as `lang/.lang`. Now escaped. All 28 HTML
  files parse with zero tag-balance issues.
- **The scorecard is a current-state page, so it was updated** (SHA `c814a854`,
  suite 178/178, 178 examples, 21 docs pages). The **audit** and **performance**
  pages are dated snapshots — "tested at SHA 002a5600, suite 100/100" — and were
  deliberately left alone. Rewriting a snapshot to look current would falsify
  the record of what was actually tested that day.

## v88 — ChatGPT round 40 verified and merged: transitive imports

- **Imports inside an imported module now resolve.** Before this, `ayojan` only
  expanded top-level imports, so a diamond — `a` imports `b` and `c`, both of
  which import `d` — left `d`'s definitions unreachable. The inliner now runs
  bounded passes over a shared visited table, so `d` is included once, in
  deterministic order. This is still single-translation-unit source expansion,
  **not** separate compilation, and the round was labelled partial for that
  reason.
- **Verified, not taken on trust.** Source SHA `c814a854` confirmed; all 28
  manifest entries verified. I proved the patch applies to *my* source and
  inverts cleanly by reverse-applying it with `tools/reverse_patch.py` — the
  reconstructed source hashes back to `203a4fb1` exactly.
- **The build they could not run:** Linux ELF 138,496 B, Windows PE32+ 129,527 B.
- **Suite 178/178** — the target, hit exactly. Gate 12/12, shape 5/5, their
  module-graph oracle 12/12.
- **The diamond, checked independently.** Correct output (`17\n7\n`) does not by
  itself prove the module was included once, so I built a manually flattened
  equivalent and compiled both: the emitted binaries are **byte-identical at
  671 bytes**. Emitted code is also byte-identical to the R39 baseline on
  `126_numeric_pipeline`, `07_module` and `66_module_dedupe` — no regression.

## v87 — ChatGPT round 39 verified and merged: native-script highlighting

- **The Windows GUI can highlight keywords in all ten Indian scripts.** The
  highlighter loads every `lang/*.lang` pack at startup and matches whole
  Brahmic tokens, keeping the Latin keywords working alongside.
- **Verified by building it**, which the author could not: object 32,999 B →
  PE32+ GUI 32,215 B, header confirmed. Their 28/28 GUI tests pass; suite
  177/177, gate 12/12, packs 30/30.
- **61 NASM `.bss` warnings investigated before being reported as a defect.**
  My held R38 source emits the identical 61, so they are pre-existing and
  harmless — the initialiser is zero and `.bss` is zero-filled anyway.
- **Correction to their report:** the ten packs hold **308** native keyword
  mappings, not the 268 stated. Their test asserts `>250`, so it passed either
  way, but the prose figure was wrong.
- **Windows installer rebuilt in pure NASM.** The old installer needed a C
  toolchain to build, which defeats the point of a language whose end users
  need nothing. `Sutram-Setup.exe` is now one hand-written NASM source that
  embeds the payload and both PowerShell scripts, shows a real window, and
  installs per-user with no UAC. Two real faults were caught before shipping:
  the entry point did not normalise the stack, so every Win32 call was made
  misaligned; and `CW_USEDEFAULT` was being sign-extended. A static Win64 ABI
  checker (`tools/check_setup_abi.py`) now guards both. **It has still never
  been run on Windows.**
- **Release cleanup:** the project went from 59 MB to 7.6 MB — the previous icon
  set, the per-round source archives, nine one-off patch scripts and roughly
  seventy stray development images removed.

## v86 — Linux GUI IDE started: a native X11 client in pure NASM

- **Slice 1 of the Linux GUI IDE.** A native X11 client written directly against the X protocol over
  the Unix socket — no toolkit, no libX11, no runtime. Connects, performs the connection handshake,
  parses the setup block for the root window and resource range, creates and maps a 900x620 window,
  and runs an event loop that exits on a keypress.
- **Verified without a display, by standing in for the server.** The sandbox has no X server, so I
  wrote `tools/test_x11_protocol.py` — a mock X11 server that accepts the connection, validates the
  setup request, replies with a well-formed setup block, and then checks the client's own requests
  byte by byte. **15/15 checks pass**: byte order `l`, protocol 11.0, no auth; CreateWindow 36 bytes
  with opcode 1, length 8, a window id drawn from the advertised resource range, parent = the root
  from the setup block, 900x620; MapWindow 8 bytes, opcode 8, targeting that same window.
- **Two bugs found and fixed in my own code before they could hide:** the setup parser ignored the
  pixmap-format block when locating the first SCREEN, so it would have read the root window id from
  the wrong offset; and `create_win` was written but never called, so no window request was ever
  sent. Both are the kind of fault that a mock-server test catches and a screenshot would not.
- **Honest limit:** this proves the protocol bytes are correct. It does **not** prove the window
  renders or that the layout looks right — only a real display can show that, and the visual check
  is the owner's.

## v85 — ChatGPT round 38 verified and merged (Unicode GUI + per-user installer)

- ChatGPT implemented the UTF-8/UTF-16 bridges, the W-API path throughout (temp files, process
  launch, dialogs), UTF-16-aware highlighting, and folded the GUI into the per-user installer with a
  Start Menu shortcut and an HKCU uninstall.
- **Verified independently.** GUI ASM SHA `626feb64…` matches; every Unicode bridge is present in
  the source; it assembles with NASM (29,488 B); it links to PE32+, x86-64, subsystem 2; their GUI
  suite is **20/20**. Icon loading confirmed: `set_project_icon` loads `icons\sutram.ico` through
  `LoadImageW` + `WM_SETICON`, with `assets\sutram.ico` as fallback.
- Merged the seven changed files only. My thread icon, IDE undo, ROADMAP, six books, ten packs and
  177 examples intact. Re-verified: suite 177/177, gate 12/12, packs 30/30, GUI rebuilds to a valid
  PE32+ GUI.
- **Two corrections recorded.** My earlier claim that the Drive `403 cannotDownloadAbusiveFile` was
  caused by `.exe` files in the archive is **wrong** — ChatGPT reports the block persists with every
  executable removed. Cause still unknown. And I mis-reported ChatGPT's icon loading as missing; the
  path is a UTF-16 wide string, which an ASCII grep cannot see. Their claim was correct.

## v84 — ChatGPT round 36 verified and merged (Windows GUI ABI repairs)

- ChatGPT found and fixed four defects in the Windows GUI: the anonymous-pipe
  `PeekNamedPipe` argument-numbering bug (output was passed at argument six instead of five, so the
  Run pane would have been silently empty), a Win64 nonvolatile RSI/RDI violation in `win_resolve`,
  a vacuous test assertion, plus four new ABI contract tests and two more manual checklist steps.
- **Verified independently, not taken on trust.** Their claimed GUI ASM SHA `68b15802…` matches; the
  PeekNamedPipe repair is confirmed present at both call sites; it assembles with NASM; it links to
  PE32+, x86-64, subsystem 2 (WINDOWS_GUI); their GUI suite is 12/12.
- Merged changed files only, as they asked. My new thread icon, IDE undo, ROADMAP, six books,
  ten packs and 177 examples all intact. Re-verified after merge: suite 177/177, gate 12/12,
  packs 30/30, GUI rebuilds to a valid PE32+ GUI.

## v83 — new project mark: the thread

- **The old icon is replaced across the project.** The previous mark was a dark-teal circle
  carrying the Devanagari letter स flanked by curly braces, in two colour variants (an older gold
  set and a newer orange set) plus three pixel-art small sizes that matched neither.
- **The new mark is a thread** — a single continuous curve in a teal circle with a warm ring. It is
  script-neutral by design: it carries no Devanagari letter, so it does not represent one Indian
  language over another, and no faith. It also means the project's own name (सूत्रम्, sūtra =
  thread) rather than borrowing a symbol from somewhere else.
- **Replaced:** `icons/` (full set), `docs/assets/` (16/22/24), `windows/native-installer/assets/`
  and the copies under `brand/`. Filenames are unchanged, so every script reference still resolves.
- **New `icons/sutram.ico`** is a genuine multi-size icon: 16, 20, 24, 32, 48, 64, 128 and 256 at
  32bpp, so Windows picks the right artwork per context instead of downscaling one bitmap.
- **Per-size tuning, not one bitmap scaled down.** Stroke weight rises from 10.5 at 256px to 19 at
  16px, and the curve flattens from 32px down, so the thread keeps enough weight to read and its
  round caps stay clear of the circle edge at small sizes.
- **Reversible:** the previous icon set was removed during release cleanup; the thread mark is now the only icon set.
- Caveat recorded honestly: sizes 128 down to 24 were verified readable. **16px could not be
  confirmed at true size** from a screenshot, so it is the one size still open.

## v82 — ChatGPT round 34 verified and merged (namespace contract hardening)

- ChatGPT extended the R33 opt-in import namespaces with alias ownership, qualified module-name
  validation, bounded import-table diagnostics, and an importer EOF boundary repair. Nine new
  examples (154-162), seven of them expected-rejection contracts.
- **Verified independently, not taken on trust.** Their claimed AFTER-hash
  `203a4fb1ca917bc6…` matches the delivered source exactly; it builds with NASM; the suite is
  **177/177** (168 from R33 plus the nine new cases); the codegen gate is **12/12**, so the FG2
  recovery still holds through this change.
- **Merged precisely, not by replacement** — as they asked, since Drive serves my zip as
  `403 cannotDownloadAbusiveFile` and they could only merge against their own tree. Only their
  changed files were applied; my IDE undo, ROADMAP, six books, changelog, language packs and
  examples 200+ are all intact.
- A good sign: they are now writing **expected-rejection tests** — overlong alias, empty alias,
  digit alias, missing module, path traversal, import capacity. Testing that bad input is refused
  is a stronger habit than testing only that good input works.

## v81 — the language packs now cover the whole language

- **All ten packs were missing the same four keywords**: `dasham` (floats), `kosh` (growable
  arrays), `kuru` (do-while) and `nishkriya` (inline assembly). Each pack covered 26 keywords; the
  language has 30. So "program in your language" did not reach the newer parts of the language.
- Added them in each script, using native words consistent with the book editions.
- **Verified by compiling, not by listing.** `tools/test_lang_packs.py` writes a real program in
  each pack's own native words and runs it: kosh + dasham 10/10, kuru (do-while) 10/10,
  nishkriya (inline asm, exit code 42) 10/10. A pack that lists a word the compiler rejects would
  be worse than one that omits it, so presence was never the test.
- Finding along the way: `kuru` is a **do-while** — `kuru { body } yavat (cond)` — not a plain
  block. An earlier test of mine assumed the wrong form and failed until corrected.

## v80 — IDE undo, and a real terminal bug behind it

**Added:** Ctrl-Z undo in the IDE, up to 4096 edits deep. It uses a compact undo
log (operation, position, byte) rather than snapshotting the 64 KB buffer on every
keystroke, and records before each mutation in `insert_byte` and `delete_before`.

**Fixed:** the IDE's `set_raw` cleared only `ICANON` and `ECHO`, leaving **`ISIG`**
set. That meant Ctrl-Z (0x1a) was still the terminal's *suspend* character: the
kernel sent `SIGTSTP` and **stopped the IDE process**. It looked alive but processed
nothing further — no keystrokes, no save — which is what made undo appear to
"clear the whole buffer". The same class of bug applied to `IXON`: Ctrl-S is the
IDE's *save* key, but it is also XOFF. Both flags are now cleared. This was a
pre-existing bug, not one introduced by undo; choosing Ctrl-Z is what exposed it.

**Testing note:** the first undo test read the reconstructed screen and reported
five false failures. Save-then-read-the-file is the reliable method and is what
`tools/test_ide_undo.py` now does — 12/12 cases pass.

**Verified:** undo 12/12; IDE harness unchanged (colours, run, shell pane, examples
browser all still correct); compiler suite 163/163; codegen gate 12/12.

## v79 — found and fixed a split book set

- The project carried **two copies of the book editions**: `books/` and `docs/`. Only `docs/` was
  updated in v77, so `books/` still held the pre-`kosh` text — a stale shipping copy.
- `books/` now synced from `docs/` for all six editions. `books/sutram-book-indian.html` is a
  separate combined edition and is noted as still needing the same update rather than being skipped
  quietly.

## v78 — roadmap added; operating-system capability recorded as a future feature

- **New `ROADMAP.md`** (in the project tree, so ChatGPT sees it too) and a matching readable page
  `docs/sutram-roadmap.html`.
- **Operating-system capability is recorded as an Exploratory future feature**, per the request. The
  page states plainly that it is **not** possible today, lists the six specific blockers found by
  reading the compiler (no raw pointers, no `volatile`, hard-coded load address, 64-bit only, no
  naked/interrupt functions, no freestanding mode), and sets out the six bounded additions that
  would close the gap. The UEFI route is named as the recommended entry point, since PE32+ output
  already exists.
- Nothing on the roadmap is presented as a commitment. The page opens with a direction-not-commitment
  badge, marks every item Exists / Planned / Exploratory, and repeats the guardrails that must not
  change.
- Verified: page rendered in a browser and inspected — cover, legend table and status markers all
  correct, no overflow.

## v77 — the books are current again

- **All six book editions updated** (English, Hindi, Sanskrit, Tamil, Telugu, Gujarati) with a new
  chapter 18, "What is new — the current language", plus a shared code appendix (chapter 19).
- **Why it was needed:** no edition mentioned `kosh` at all — they predated growable arrays, floats,
  typed arrays, typed parameters, the IDE, the shell pane and the newer library modules. The
  documentation was understating the language.
- Covers: `dasham` floats and mixed arithmetic; `kosh` growable arrays and the capacity-vs-length
  rule; typed `kosh dasham`; typed function parameters and the by-value pointer boundary; the 15
  library modules including the heritage and numerical ones; the IDE with its shell pane; measured
  performance; and an honest note on what has not been verified.
- The five non-English editions were translated into their own scripts and assembled into the
  existing book CSS, so they match the surrounding pages. Code examples are identical across
  editions, since Sutram source does not change with the book's language.
- Verified: div-balanced HTML in all six, and a rendered check of the Hindi edition confirming the
  Devanagari text and code blocks display correctly with no overflow.

## v76 — PERF-FG2 verified: indexed/complex float scheduling, ~1.10x more on real code

- **Verified**: FG2 (left-first scheduling for indexed and complex float expressions) changes
  `126_numeric_pipeline` (7,648 -> 7,610 bytes) and makes it **~1.10x faster** (interleaved A/B:
  77.5 -> 71.2 ms and 78.4 -> 70.7 ms). Together with FG1 that is ~1.21x cumulative on the realistic
  program. Suite 155/155; gate 12/12 with all three new gates at exactly their ceilings; 135-140 exact.
- **XMM residency design doc received and reviewed** (`compiler/XMM_REGISTER_RESIDENCY_DESIGN_R30.md`):
  correct SysV-vs-Win64 volatility handling, staged plan behind a disabled-by-default flag, explicit
  call/branch/loop barriers, and exact-bit tests. Endorsed with two additions (a flag-off
  byte-identical negative gate; no Windows XMM6-15 work without a real Windows runner).
- Next big task handed over: implement Stage 1 of that design behind the flag.

## v75 — IDE: interactive shell pane

- **Ctrl-T opens a shell pane inside `sutram-ide`** — the other half of what IDLE gives you. Type a
  Sutram statement, press Enter, and it runs; the session accumulates, so later statements see earlier
  ones (`vitti x = 6` then `likha(x * 7)` prints 42). Ctrl-T or Ctrl-C returns to the editor.
- Implemented by wrapping the accumulated session in `mukhya() { ... }`, compiling and running it
  through the same path Ctrl-R uses — so the shell has no separate evaluator to drift out of sync.
- Two bugs found and fixed by the PTY harness, both the same class as before: `strlen` needs its
  pointer in `rdi` (I had set `rdx`), and the program buffer must be cleared before appending, or two
  `mukhya()` definitions were emitted and the compiler silently used the first.
- Added a shell-pane regression scenario to `tools/ide_test.py`.

## v74 — samanvaya: linear algebra on flat arrays

- **New module `lib/samanvaya.smlib`** (समन्वय) — matrices as flat `kosh dasham` in row-major
  order with explicit dimensions, since Sutram has no 2-D type: identity, transpose, sum, scalar
  multiple, matrix product, trace, 2×2 and 3×3 determinants, vector dot product, and a row-sum norm.
- **Verified against hand-computed values**: `[[1,2],[3,4]]·[[5,6],[7,8]] = [[19,22],[43,50]]`,
  trace 5, det₂ −2, **det₃ −306** (the classic example), row-norm 7, and a 2×3 transpose giving
  `1 4 2 5 3 6`.
- Found and fixed one authoring error before it shipped: `vitti` is not valid as a parameter type
  annotation, so dimension parameters are untyped (learned from `kalana`).
- 15 modules, 103 functions. Suite 149/149.

## v73 — kalana: a numerical-methods library

- **New module `lib/kalana.smlib`** (कलन, numerical calculus), built on typed `kosh dasham`:
  `trapezoid` and `simpson` (integration over samples), `slope` and `slope2` (first/second
  derivatives), `bahu_ganana` (Horner polynomial evaluation) and `bahu_mula` (bisection root).
- **Verified against known answers, not self-consistency**: ∫₀¹x²dx = 0.335000 trapezoid and
  **0.333333** Simpson (exact for a quadratic), d/dx(x²) = 1.0 and d²/dx² = 2.0 at the midpoint,
  and the root of x²−2 = **1.414214** (√2) to six decimals.
- Three bugs found and fixed during verification, one of them instructive: Simpson's 4/2 weighting
  was inverted; and my first `ok` out-parameter write hit "array index out of bounds" — which turned
  out **not** to be a compiler bug but correct bounds checking, since a kosh's capacity is not its
  length. Narrowed before claiming anything, and documented as a contract.
- 14 modules, 93 functions. Suite 148/148.

## v72 — PERF-FG1: the realistic pipeline finally moves

- **Verified**: PERF-FG1 (general float binary-expression, call RHS) changes `126_numeric_pipeline`'s
  binary (7,733 -> 7,648 bytes) and makes it **~1.10x faster** (interleaved A/B, two rounds:
  85.7 -> 77.4 ms and 86.1 -> 78.4 ms). The first time the representative program has improved at all.
- Suite 147/147; `133`/`134` exact; the `pop rdx` at the hot statement is gone.
- **Found a gate bug**: `float_scalar_call_rhs` requires `count == 18` exactly, but the correct build
  emits 17 — every shape condition passes. An exact-count gate rejects improvements to the very path
  it protects; reported with the fix (`count <= ceiling`).
- Census refinement (disjoint float-RHS buckets) adopted: in 126 the remaining shapes are 9 call,
  7 indexed, 9 complex, 6 simple-self — which is why F1/F2/FC1 alone moved nothing.

## v71 — PERF-F2 / PERF-FC1 verified — and the realistic pipeline still does not move

- **F2 (float distinct destination) verified**: `c = a + b` 7 instructions with a `pop` -> 4 with no
  stack. Measured A/B: min 102.0 -> 57.4 ms = **1.78x** — the largest single gain since PERF1.
- **FC1 (float comparison) verified**: 6 instructions, no stack, `SETcc` byte-identical to the old
  fallback. Measured A/B: min 29.6 -> 27.5 ms = 1.08x. F1 unregressed.
- Suite 145/145, gate 8/8.
- **However: the realistic 126 pipeline is byte-identical before and after.** Its float work is
  function calls and multi-term expressions, not the simple register-resident shapes these fast paths
  require. So the synthetic kernels improve and the representative program does not — the PERF2–PERF5
  pattern one level up. Recorded plainly rather than implied away.
- Next target is therefore **float expression scheduling in the general case**, with 126's binary
  changing as the acceptance criterion.

## v70 — float hotspot fixed, measured 1.33x

- ChatGPT's PERF-F1 (float scalar self-update) verified: 8 instructions with a `pop` -> 4 instructions
  with no stack traffic. Gate 6/6; suite 141/141.
- **Measured A/B, same machine**: min 51.1 -> 38.3 ms, p10 52.4 -> 39.2 ms = **1.33x** on a
  float-accumulation benchmark. The first optimization since PERF1 to move the clock.
- Why it worked: a static census of real numerical code showed 61% of assignments are float and the
  integer patterns of PERF2–PERF5 occur ~0 times there. Measurement found the target.
- Still on the slow path: distinct-destination float (`c = a + b`), complex float expressions, and
  persistent XMM residency (needs an ABI design).

## v69 — a real native Windows package (no WSL)

- Found that the shipped tree had **no Windows artifacts at all**, and that the Windows
  install path was still a **WSL bridge** — obsolete, since the compiler has a native PE32+
  build that needs no WSL.
- Added `windows/native/`: a native `sutram.cmd` wrapper, a per-user least-privilege
  `install.bat` (no admin, no UAC, HKCU only) and `uninstall.bat`. Replaced the stale
  WSL-based `windows/install.bat` and `windows/sutram.cmd`.
- Built **`sutram-windows.zip`** — `sutram.exe` + wrapper + installer + 136 examples +
  13 library modules + 10 language packs + books, with a README.
- Verified the shipped `sutram.exe` is a well-formed PE32+ (MZ/PE headers, machine 0x8664,
  console subsystem) and that compiling to `*.exe` emits a well-formed Windows PE.
  **Not** verified at runtime — no Windows host available.

## v68 — IDE: examples browser

- **Ctrl-E** in `sutram-ide` now cycles through `examples/*.sm` — each press loads the next example,
  wrapping at the end. So you can flip through the sample programs and hit Ctrl-R to run each one,
  without typing a path.
- Found and fixed a bug during verification: the path builder appended to the existing path instead
  of replacing it, so the loaded filename became `untitled.smexamples/01_hello.sm`. The path is now
  reset before being built.
- Added to the PTY regression harness (`tools/ide_test.py`) as a scenario.

## v67 — sankhyiki: the library starts using typed kosh parameters

- **New module `lib/sankhyiki.smlib`** (सांख्यिकी, statistics) — the first library module built on
  ChatGPT's typed `kosh dasham` parameters: `yoga` (sum), `madhya` (mean), `prasaran` (population
  variance), `vichalan` (population std deviation), `laghutama`/`adhikatama` (min/max), `vyapti`
  (range), `bindu` (dot product), `manak` (Euclidean norm), and a private `sankhyiki_sqrt`.
- **Verified against a known-correct dataset** rather than only self-consistency: `[2,4,4,4,5,5,7,9]`
  gives mean 5, variance 4, stddev 2, range 7 — every value exact against an independent Python
  computation. Vector cases check out too (dot of (3,4)·(1,2) = 11; norm of (3,4) = 5).
- Empty arrays return 0 rather than dividing by zero; the module never calls `kosh_push` on a
  parameter, which the compiler deliberately rejects.
- Suite **136/136**.

## v66 — the Sutram IDE ships with the language

- **New: `sutram-ide`** — a full-screen editor and runner, written in the same hand-written NASM,
  built as its own binary so it never collides with the compiler workstream.
  - editor with line numbers, cursor movement, insert/delete
  - syntax highlighting for the full current keyword set (including kosh/dasham/guna/bhavana/
    rachana/ayojan/kuru/pankti), plus strings, numbers and comments
  - `Ctrl-R` compiles and runs the buffer, showing output in a pane; `Ctrl-S` saves, `Ctrl-L` loads
  - zero dependencies: no Python, no runtime, no toolkit
- **Installer:** `install.sh` now installs `sutram-ide`, symlinks it, and adds a **Sutram IDE**
  desktop entry (uninstall removes both). The IDE locates the compiler via `./sutram_compiler`
  then `sutram` on PATH, so it works from the source tree or the applications menu.
- **Verified end to end** through a pseudo-terminal harness (`tools/ide_test.py`): launch, render,
  highlight, edit, save, run-with-output, quit. Three real bugs were found and fixed this way
  (a stack-leaking keyword scan that segfaulted, a truncated command builder, and a clobbered
  colour register).

## v65 — codegen performance analysis

- Measured the emitted machine code with delta-instruction counting over `ndisasm` disassembly
  (the ELF has no section headers, so `objdump -d` cannot read it).
- **Headline finding:** binary operators route their operands through the machine stack
  (`push`/`pop`/`xchg`) even though the values are already in registers. `s = s + i` costs six
  instructions where one (`add rbx,r12`) would do; `c = a + b` costs seven more than necessary.
- Register allocation itself is sound — 16 live variables do not spill.
- Report: `docs/sutram-performance.html`, with a baseline bench and three ordered recommendations.

## v64 — B11 closed + typed `kosh dasham` (both verified)

- **B11 closed.** The per-block statement list now has a named `BLOCK_STMT_CAP`, raised from the
  implicit 64 to **256** (65 statements is ordinary code, as the audit argued), with a named
  `Sutram Error: too many statements in block`. Verified: 256 statements compile, 257 fails with
  the named error, and my old 65-statement repro now compiles.
- **Typed `kosh dasham` delivered.** `kosh dasham xs[4]` / `कोश दशम` hold binary64 elements;
  integer pushes promote, element reads and `kosh_pop` are float expressions, and float-return
  inference works through both `kosh_pop()` and indexing. Verified independently — a float
  accumulation loop, a sum, an average, negative floats, int promotion, capacity doubling.
- Suite **122/122**. New heritage example `205_madhava_pi_kosh.sm` uses a float array for the
  Madhava pi series — the first library-side use of typed growable arrays.

## v63 — B10 fixed (verified) + audit hardening + B11 found

- **B10 verified fixed.** ChatGPT found a deeper form (nested loops overwriting the shared patch
  counters) and fixed both: guarded tables (BREAK_PATCH_CAP=1024) plus per-loop base/restore.
  Their 103/104 regressions return `9` exactly; my original 64-break repro now compiles.
- **Audit hardening merged:** `code_buf` (256 KiB, guarded), `rachana_defs` (named caps), block
  nesting (BLOCK_NESTING_CAP=128, named error), `import_names` cap.
- **T18 kosh re-verified**; AST ceiling at 768 KiB. Suite **115/115** after adding the harness
  compile-fail markers the new negative tests needed.
- **NEW BUG B11 found:** nested block bodies (`yadi`/`yavat`) cap at **64 statements**; the 65th
  fails with a misleading parse error and no guard. Function bodies are not capped. Regression
  `204_b11_block_statement_capacity.sm`; documented in the audit report.

## v62 — T18 growable arrays (kosh) verified + AST ceiling raised

- **T18 verified and merged.** `kosh` (Devanagari `कोश`) growable arrays with `kosh_push`,
  `kosh_pop`, `kosh_len`, `kosh_cap`; capacity doubles on growth. All five of ChatGPT's
  predictions matched exactly, including the empty-pop diagnostic and post-pop bounds tightening.
- **AST ceiling raised 4x** (196608 -> 786432 bytes): all seven real function modules now compile
  together in one program (was `AST capacity exceeded`).
- New heritage example `203_meru_with_kosh.sm` — Meru-prastara (Pascal's triangle) into a kosh;
  verified 21 values, rows 0-5.
- Reference gained a "Growable arrays (T18)" section. Suite **107/107**.
- **Example numbering:** my heritage examples moved to **200+** (200/201/202/203) to stop
  colliding with ChatGPT's 90-100 range.

## v61 — project audit: B10 found + audit report

- **Audit found a critical bug (B10):** `break_patch_positions` / `continue_patch_positions`
  (`resb 512` = 64 entries) have no capacity guard. 64 `krama`/`uddeshya` in one loop corrupt
  adjacent memory and fail as a misleading parse error (63 works, 64 does not). Reported to
  ChatGPT with the exact repro; needs a bound check + named error.
- **Second finding:** deep nesting (~150 blocks) fails with a misleading `end of file` parse error.
- Buffers without capacity constants identified: `code_buf`, `rachana_defs`, `alloc_sizes`,
  `import_names`.
- Confirmed clean: the guarded arenas, no credentials anywhere in source, least-privilege
  installer. Added `docs/sutram-audit.html` documenting all of it.

## v60 — standard-library reference + a real library bug fixed

- **Fixed a real defect:** `num` and `util` both defined `clamp`, `is_even` and `is_odd`, so
  importing both together failed with `duplicate function definition: clamp`. Removed the
  duplicates from `util` (num is the canonical home). No module now defines a name another module
  defines; verified `num + util` compiles and the suite stays 100/100.
- Added `docs/sutram-stdlib.html` — a full standard-library reference: every module, every
  function, with signatures and one-line descriptions. 12 modules, 80 functions.

## v59 — Brahmagupta's area formula + T12 interop re-verified

- `ganita` gained `brahmagupta_area(a,b,c,d)` — Brahmagupta's cyclic-quadrilateral area formula
  (628 CE), which reduces to the triangle formula when d=0. Verified: 3-4-5 -> 6, 5-5-6 -> 12,
  cyclic 3-4-5-6 -> 18, square side 4 -> 16.
- ChatGPT re-sent the T12 function-interop source (byte-identical, `002a5600`) with two extra
  regressions; both verified exact. Suite **99/99**.
- Renumbered my examples to 96/97 to end a number collision; my heritage examples now sit at 96+.

## v58 — T12 function interop (verified) + the madhava library module

- **T12 floats + function interoperability verified and merged.** Typed parameters
  (`prakriya f(dasham x)`) and float-return inference. Both hosts build, suite **96/96**, their
  new float-function regression matches its prediction exactly.
- **New module `madhava`** — the Kerala school as a real library: `madhava_pi` (Madhava's fast
  series), `madhava_sin`, `madhava_cos`, `madhava_atan`, and `madhava_sqrt` (Newton). Verified
  exact to six decimals: pi 3.141593, sin(0.5) 0.479426, cos(0.5) 0.877583, atan(0.5) 0.463648,
  sqrt(2) 1.414214.
- Example `95_madhava_library.sm`. Renumbered my earlier example 93 -> 94 (number collision).
- Library is now 12 modules, 7 with functions. Suite **97/97**.

## v57 — T12 floats (verified) + the Madhava series

- **T12 floating point is implemented and verified.** `dasham`/`दशम` scalar binary64, decimal
  literals, SSE2 mixed arithmetic, comparisons in `yadi`/`yavat`, and a six-decimal printer.
  Verified: their regression matches its prediction exactly; my edge cases (0.0, 0.05, 1.999999,
  negatives, mixed int*float, float loops) all pass. Suite **95/95**.
- **The Kerala school joins the library heritage.** `examples/93_madhava_series.sm` computes
  Madhava's fast pi series (pi = sqrt(12) * sum (-1)^k/((2k+1)3^k)) plus the sine and cosine
  series. Verified exact to six decimals: pi 3.141593, sin(0.5) 0.479426, cos(0.5) 0.877583.
- Floats cannot yet cross function boundaries, so the Madhava series is an example rather than a
  library module until T12 function interop lands.
- Removed an orphaned `89_indian_number_theory` expect pair left by an earlier rename.

## v56 — Brahmagupta's samasa (composition law) added to ganita

- `samasa(out, a, b, c, d, n)` implements Brahmagupta's composition law: from
  a^2-n*b^2=k1 and c^2-n*d^2=k2 it composes (a*c+n*b*d, a*d+b*c). Named `samasa` because
  `bhavana` is already a reserved keyword (the `guna` case label).
- Verified: (3,2)^2 -> (17,12) with 17^2-2*12^2 = 1; (8,1)^2 for N=61 -> (125,16) with
  125^2-61*16^2 = 9. Suite **93/93**.

## v55 — least-privilege Windows installer (verified at source level)

- The Windows installer is now **per-user by design**: UAC elevation path removed entirely,
  default install to `%LOCALAPPDATA%\Programs\Sutram`, uninstall registration under `HKCU`,
  user PATH only, per-user Start Menu and Desktop shortcuts.
- A build-time gate (`Assert-LeastPrivilegeInstallerSources`) aborts the build if UAC helpers,
  HKLM, machine PATH, common shortcuts or Program Files defaults ever return.
- Verified at source level: the runtime installer sources contain none of the forbidden patterns;
  every occurrence of those names is a *needle inside the gate* that rejects them.
- Runtime Windows acceptance (no UAC prompt, per-user install/uninstall) still needs a real
  standard-user Windows account — cannot be rebuilt in this environment.

## v54 — B9 FIXED (verified) + philosophy prefaces in the books

- **B9 is fixed and verified.** ChatGPT made `&&` and `||` truly short-circuit: `.ge_binop`
  leaves the eager path for `OP_LAND`/`OP_OR`, so the RHS is skipped when the result is already
  determined. Verified: `i < pankti_len(a) && a[i] > 0` now returns 0 with no bounds error,
  `0 && (1/0)` returns 0 without dividing, and both new regressions match their predictions.
  Both hosts build; suite **93/93**.
- **Every book edition now opens with a Preface** (English, Hindi, Sanskrit, Tamil, Telugu,
  Gujarati) stating the philosophy in its own script.
- Renamed my number-theory example 89 -> 91 to avoid a number collision with ChatGPT's B9 tests.

## v53 — philosophy preface in all six book editions

- Each book edition (English, Hindi, Sanskrit, Tamil, Telugu, Gujarati) now opens with a
  Preface stating the philosophy: Sanskrit keywords as design commitment, the name सूत्रम्
  after Panini, the standard library as the Indian mathematical tradition (Pingala, Aryabhata,
  Bhaskara), and the self-sufficient compiler.
- Prose translated per edition; the code and the claim are identical in all of them.

## v52 — Indian number theory: kuttaka + chakravala

- Added `lib/ganita.smlib` — Aryabhata's **kuttaka** (linear indeterminate equations; ancestor of
  the extended Euclidean algorithm) and Bhaskara II's **chakravala** (Pell's equation
  x^2 - N*y^2 = 1). Verified: `chakravala(61)` gives x = 1766319049, y = 226153980 — the
  historical result, exact.
- Example `89_indian_number_theory.sm`; suite now **92/92**.
- The library now implements two stages of the philosophy roadmap: Pingala (`chandas`) and
  Aryabhata/Bhaskara (`ganita`).

## v51 — philosophy document + chandas module

- Added `docs/sutram-philosophy.html` — the project's philosophy in three layers (words, name,
  methods) with the library roadmap: Pingala (shipped), Aryabhata, Brahmagupta/Bhaskara, the
  Kerala school, Katapayadi.
- Added `lib/chandas.smlib` — Pingala's prosody mathematics: `dviguna` (2^n), `meru`
  (Meru-prastara / Pascal's triangle), `matra_meru` (Fibonacci), `is_guru`, `guru_count`,
  `meru_pankti`. Example `88_pingala_chandas.sm`; suite now **89/89**.

## v50 — B8 FIXED (verified) + language packs cleaned

- **B8 is fixed and verified.** ChatGPT traced it to `func_params resb 512` (64 parameter
  slots) while the parser stores every function's parameters cumulatively; `math+sort+string`
  has 67 parameters (536 bytes), overflowing into `func_table` and corrupting a string pointer
  -> segfault in `strcmp`. Fix: `FUNC_PARAM_CAP 4096` + bounds guard, plus guards for the AST
  heap, variable table, function table, patch list and function-definition table.
  Verified by rebuilding both hosts: **all 15 module combinations compile**, including the two
  that crashed before, and the suite is **88/88**.
- **Language packs cleaned (8 active):** removed all duplicate keyword entries and filled the
  missing Telugu `bhavana`. Every active pack now has exactly 26 keywords, 0 duplicates, and
  compiles a real program in its own script.
  - Gujarati `sutra` was **કૂટશબ્દ ("codeword") - wrong meaning** -> `અચલ` (constant)
  - Telugu gained `bhavana` -> `భావన`; plus dedupes and Sanskrit-form fixes
  - Kannada, Marathi, Odia, Punjabi: dedupe + Sanskrit-form corrections
- Tamil and Malayalam packs are **paused** (unchanged).
- Added `docs/sutram-keyword-words.html` (keyword x language grid) alongside the scorecard.

## v49 — B8 token-ceiling fix (partial) + capability scorecard

- **B8 root cause found by ChatGPT:** the token array was `40960` bytes at `TOKEN_SIZE 40`
  = exactly **1024 slots**; three modules produce ~1302 tokens and overwrote memory after
  `token_arr`. Raised to `TOKEN_CAP 65537` (one token per source byte + EOF), and the lexer
  string pool to `STR_POOL_CAP 65537`. Verified: `math+num`, `math+num+sort`,
  `math+num+string`, `num+sort+string` now all compile (they did not before).
- **B8 still OPEN:** `{math, sort, string}` in any order, and all four modules, still
  **segfault** (exit 139) — a second, content-specific failure mode, not the token ceiling.
  `math+sort+num` compiles but `math+sort+string` does not, and a renamed copy of string
  reproduces it, so it follows string's *content*. Several fixed buffers
  (`ast_heap`, `patch_list`, `func_table`, `var_table`) still have no bound check.
- Test fixture corrected: `likha` of an integer appends a newline, so the expected output of
  `86_b8_multi_modules` is `9\n 1\n 3\n\n`, not `9 1 3`.
- Suite: **87/87**.
- Added `docs/sutram-scorecard.html` — the language scored against 17 parameters.

## v48 — performance made a standing priority; measured baseline; faster sort
- STANDING INSTRUCTION: performance is now a first-class requirement every round, not a
  later phase. `tools/bench.py` added — it measures compile time and CPU-bound run time so
  "faster" is a number we can track. Baseline: loop_sum (20M iterations) ~71 ms,
  nested_loop ~24 ms, fib_rec ~63 ms, compile median ~2.7 ms.
- DIAGNOSIS: loop_sum is ~5 ns per two-operation iteration; a register-resident loop should
  be ~1 ns. That is the signature of locals living in memory rather than registers, so
  register allocation (P1) is the top compiler-side lever. Assigned to ChatGPT with P2
  (redundant load/store elimination), P3 (strength reduction + LICM), P4 (compile speed).
- LIBRARY WIN: added `shell_sort` to lib/sort.smlib. Measured at n=3000: bubble_sort adds
  71 ms over baseline, shell_sort adds ~0 ms — roughly 70x faster. Golden example 85.
- FOUND B8: the `ayojan` inliner writes into a fixed 8192-byte area; inlining three or more
  modules overflows it and corrupts the program source. A hard cap on the library.
- FOUND B9: `&&` does not short-circuit. `j >= 1 && a[j-1] > 0` evaluates the right side and
  trips the bounds check; nested `if`s are correct. Both a correctness and a speed issue.

## v47 — library growth exposed B8: `ayojan` inliner overflows at 3+ modules
- FOUND (by using the library, not by reading): the `ayojan` preprocessor writes inlined
  module source into a fixed 8192-byte area (`str_pool + 8192`). Inlining three or more
  modules overflows it and corrupts the program source.
  - 1 module -> fine; 2 modules -> fine; 3 modules -> `parse error at line 1:288 near token ''`.
- IMPACT: a hard cap on the standard library. Any program that pulls in three or more
  modules is corrupted, so the library cannot grow past ~2 usable modules at a time.
  This is now the top blocker for the library roadmap.
- WORKED AROUND in the tree: `full_demo` used math+string+io (three) and had gone red;
  it only uses builtins, so its `ayojan` lines were removed and it re-recorded. Suite 85/85.
- Every library example uses exactly one module, so all of them still pass.
- ADDED lib/string.smlib: `count_char`, `find_char`, `is_all_digits`, `upper_code`,
  `lower_code` (module now 13 functions), golden example 84_stdlib_string2.
- Windows verification kit rebuilt from this tree (4 checks: input, arrays, structs, spill).

## v46 — round 7 merged: B7 fixed (stack-frame spill collision)
- TAKEN: B7 — the sixth variable of a generated function spilled to `[rbp-8]`, which is the
  saved `rbx`. A callee therefore returned with `rbx` = its own local, destroying the caller's
  live values (main keeps the array pointer in rbx), so the next array-taking call faulted.
  Fix reserves a 2048-byte spill area below the saved registers/parameters, in user functions
  and in main.
- VERIFIED: their source SHA matched (e253b94f); both hosts build; their new regression and
  MY minimal reproduction both produce the expected values.
- The fix also exposed a test that had been recorded against corruption: `33_unit_conversion`
  expected `0C = 734086739261390880F`; the correct value is `0C = 32F`. Re-recorded. So this
  fix corrected latent memory corruption that had been silently poisoning an existing program.
- ADDED lib/sort.smlib — sorting and searching (swap, bubble_sort, reverse_arr, min_of,
  max_of, sum_of, find_linear, count_of, is_sorted, binary_search), with golden example
  83_stdlib_sort. The module that originally exposed B7 now works end to end.
- Suite: 84/84. Library is now 4 modules.

## v45 — round 7 opened; small library win while ChatGPT takes the big tasks
- HANDOFF: ChatGPT assigned two BIG tasks this round — T12 floating point (`dasham`)
  and T18 growable arrays + a `kosh` dictionary type. The small items (T9, T14–T17, T11)
  are queued behind them.
- ADDED lib/num.smlib: `fib`, `is_perfect`, `collatz_steps` (module now 10 functions),
  with golden example 81_stdlib_num2. Suite 82/82.
- HELD BACK: `lib/sort.smlib`. Sorting itself now works (B6 fixed), but the full example
  segfaults later — see B7 below. Not shipping unverified library code.
- FOUND B7: in a multi-function module, a function containing an if/else inside a loop
  (`binary_search`) appears to corrupt a later call in the same program — `min_of` returns
  nothing after it, and the whole example faults. Isolated reductions (inline, scalar,
  single-module) all pass, so the trigger is not yet pinned down. Reported to the compiler
  owner with the reproduction.

## v44 — round 6 checkpoint 2 merged (B6 fixed — user-function ABI)
- TAKEN: B6 — the generated user-function ABI only preserved `rbx`, but the variable
  allocator hands out `rbx, r12, r13, r14, r15`. So a callee's locals silently clobbered
  the caller's live variables in r12–r15. That is why a nested loop whose bound used the
  outer counter (`yavat (j < n - 1 - i)`) broke whenever the body called a function.
- FIX: both user-call code paths (`.gs_funcall` statement form and `.ge_funcall`
  expression form) now push/pop r12–r15 around the call.
- VERIFIED here: their source SHA matched (3b12a478); both hosts build; suite 81/81; our
  prior 80 tests pass against their compiler (no regression); their new regression and MY
  original reproduction both now produce 1 2 3 4.
- This was a wide-reaching correctness bug, not a corner case: it affected any function
  call made while the caller held live variables in r12–r15.
- New example 80_b6_nested_call_loop.

## v43 — round 6 checkpoint 1 merged (B5 fixed)
- TAKEN: B5 — `ayojan` module lookup no longer depends on the working directory.
  Resolution order is now: source-file directory -> compiler directory -> CWD.
  Verified the way it is meant to work: a project whose source sits next to its own
  `lib/` compiles correctly from a foreign working directory (prints 81).
- TAKEN: their regression `79_ayojan_cwd` plus the harness's `CWD` map, so the test
  actually compiles from `/tmp` instead of the tree root.
- NOTE: the test relies on the compiler sitting at the tree root (resolution path 2).
  Verified 80/80 with the compiler in place.
- FIXED MY TOOLING: tools/merge_from_chatgpt.py now builds the compiler into the tree
  root instead of /tmp — an out-of-tree build made module-resolution tests fail falsely.
- ALSO: removed my abandoned `lib/sort.smlib` experiment (it hit the nested-loop bug
  recorded separately) so the tree ships only verified library code.
- Suite: 80/80.

## v42 — books synced to the current language; tooling hardened
- BOOKS: all six editions gained a "v29 – v41" section documenting the newer
  features (ternary `?:`, do-while `kuru … yavat`, `pankti_len` + bounds checking,
  six-argument functions, the `ayojan` standard library, Windows keyboard input),
  with prose translated into each edition's own language and a code sample that is
  verified to compile (prints 12, 100, 3, 3).
- TOOLING: tools/merge_from_chatgpt.py upgraded — it now checks the claimed source
  SHA-256 from the handoff, builds BOTH hosts (Linux ELF + Windows PE32+), runs the
  suite, diffs the source with a philosophy guard, warns about symbols used but not
  defined (the Round-4 build break), merges the test harness intelligently, and
  reports new examples. One command now does a whole verification round.
- FOUND: `ayojan` resolves `lib/` from the current working directory, so a program
  run from elsewhere fails. Reported to the compiler owner.
- ADDED (out of tree): sutram-windows-check.zip — a real-machine kit with three
  PE32+ programs (input, arrays, structs) and a double-click runner.

## v41 — round 5 return from ChatGPT merged (T8b + T10)
- TAKEN: T8b — arrays now carry a runtime length header. `pankti a[4]` allocates a
  header word + elements; `pankti_len(a)` reads it; dynamic lengths work (`pankti a[n+1]`).
  Bounds checks apply only to real `pankti` arrays, so raw `nirmmita` pointers keep their
  old behaviour (array_demo stays green). Array metadata is now per-function scope, so
  same-named arrays in different functions no longer collide.
- TAKEN: T10 — ternary `?:` (right-associative, only the chosen branch evaluates) and a
  do-while form `kuru { ... } yavat (cond)` (Devanagari `कुरु` also accepted).
- TAKEN: the AST constants requested after round 4 (`AST_IF/WHILE/RETURN/CALL/FUNC`) are
  now defined with `equ`, plus `AST_TERNARY`/`AST_DO_WHILE`.
- VERIFIED: their source assembled first time (no fix needed); both hosts build; suite
  79/79; negative index and index==length both exit 1; variable index, highest valid
  index, dynamic length, per-function scoping, ternary and do-while all produce the
  claimed outputs; 66/71 non-new examples byte-identical to the previous compiler.
- New examples 71–78.

## v40 — round 4 return from ChatGPT merged (T4 + T8 + B1 + B2 + B3)
- TAKEN: B1 — assignment to a function parameter no longer segfaults the compiler.
- TAKEN: B2 — an undefined function call is now a hard error (`undefined function: <name>`, exit 1)
  instead of silently returning an argument.
- TAKEN: B3 — `char_code(s, i)` now honours the index (one-argument form still means index 0).
- TAKEN: T4 minimum module semantics — duplicate `ayojan` is idempotent; a definition
  collision (program vs module, or module vs module) is a clean diagnostic.
- TAKEN: T8 — `pankti_len(array)` builtin; array reads/stores are bounds-checked for
  constant-length declarations and a bad index prints `array index out of bounds` and exits 1.
- FIXED BY ME: their source did not assemble — `mov qword [rax], AST_CALL` at line 6804
  used a symbol that is never defined (the codebase writes the literal `8` with a
  `; AST_CALL` comment). One-line fix; without it the whole round was unbuildable.
- FIXED BY ME: `20_pankti_array` was passing on an out-of-bounds write (loops run 0..5
  inclusive but the array was `[5]`); the new bounds check exposed it. Array resized to 6,
  same expected output.
- VERIFIED: both hosts build; suite 71/71; B1/B2/B3/T4/T8 focused cases all correct with
  proper exit codes; 63/64 non-array examples byte-identical to the previous compiler.
- Harness now supports expected compile failures via a `.compile_fail` marker.

## v39 — standard library (lib/) + module examples made genuine
- ADDED lib/math.smlib, lib/num.smlib, lib/string.smlib — the first real standard
  library. `ayojan <name>` inlines lib/<name>.smlib (the mechanism already existed;
  lib/ was empty).
- ADDED examples 61_stdlib_math, 62_stdlib_num, 63_stdlib_string with golden tests.
  Suite 64/64.
- FIXED a class of false-passing tests: 07_module and 10_mathlib only passed because
  undefined function calls silently return an argument. With the library present they
  now compute real values (49; 81/42/42/42) and are recorded correctly.
- DOCS: the language reference's builtin table listed names the compiler does not
  accept (`vartlen`, `charat`, `memcpy`, ...). Replaced with the real names
  (`vartani_len`, `char_at`, `smaran_cp`, ...) and added a standard-library section.
- KNOWN BUGS recorded for the compiler owner: (1) assigning to a function parameter
  segfaults the compiler; (2) an undefined function call silently returns one of its
  arguments instead of erroring; (3) char_code ignores its index argument.

## v38 — round 3 return from ChatGPT merged (6-arg functions + located diagnostics)
- TAKEN: T5 — user functions/calls now accept up to 6 arguments (AST node 48->72 B,
  token record 32->40 B, heap raised). 7th parameter/argument rejected with a clear hint.
- TAKEN: T6 — parse errors now print `line:column`, the offending source line and a
  caret under the token; line counts fixed after // and # comments; UTF-8 columns
  counted by code point, not byte.
- VERIFIED here (they had no NASM): both hosts build; suite 61/61; merged SHA equals
  theirs (6e4881b0); six-arg example prints 21/210; 7th arg/param exit 1 with the hint;
  diagnostic column correct after Devanagari (5:36); 0-3 arg Linux output byte-identical
  to the previous compiler across all examples.
- New example 60_six_func_args taken in; docs updated (3 -> 6 args).

## v37 — round 2 return from ChatGPT merged (Windows REPL + array-literal fix)
- TAKEN: T3 Windows REPL now launches child processes with CreateProcessA /
  WaitForSingleObject / GetExitCodeProcess instead of fork/exec/wait; Windows
  REPL scratch I/O uses CreateFileA/WriteFile/CloseHandle. Linux REPL path kept.
- TAKEN: T7 — `vitti a = [1, 2, 3]` no longer segfaults; it now gives a clean
  parse diagnostic and exits 1 (root cause: AST_VEC popped four values regardless
  of element count).
- VERIFIED here (they had no NASM): their source SHA matches their claim
  (f1921523...); both hosts build; suite 60/60; Linux output byte-identical to
  ours across all 60 examples; Linux REPL works end-to-end; Windows expansion
  has 0 fork/exec refs and 3 Win32 process-API refs; T7 exits 1, and a 4-element
  literal still compiles. Merged source SHA equals theirs.
- Still pending: real-Windows run of the REPL (T3) and of arrays/structs (T2).

## v36 — books & docs synced to the current compiler
- WINDOWS-SETUP.md and all six book editions no longer claim `grahan` (keyboard
  input) is unported on Windows; it now reads through the embedded runtime
  (ReadFile). Arrays/structs are noted as source-ready, pending a real Windows run.
- Language reference corrected: package version, enum syntax (`srijana NAME = value`,
  declared inside a function — not `srijana X = { ... }`), and the function-body
  rule documented: a brace-less body is ONE statement; braces are required for more.
- Book code examples verified by compiling them: 66/66 complete-program blocks now
  compile. Three real errors found this way and fixed: two examples used the reserved
  keyword `anka` as a variable name (renamed to `mulya`); the fib example was missing
  braces around a multi-statement body; the enum example used wrong syntax and placement.
- Escaped 12 raw '<' characters inside code blocks (HTML validity).
- Suite: 60/60 (example 46 extended to match the reference's function example).

## v35 — round 1 return from ChatGPT merged (Windows grahan fix)
- TAKEN FROM THEIR ROUND: grahan() codegen no longer emits a literal Linux
  `0f 05`; it routes through the target-aware emit_syscall, so a Windows .exe
  calls the embedded runtime (ReadFile) instead of executing a Linux syscall.
  Their PE-specific tail + branch displacements included.
- VERIFIED here (they had no NASM): their source assembles; our suite passes
  59/59 against their compiler; Linux grahan output is byte-identical to ours
  (969 B / 366 B); the generated PE contains 0 raw syscalls and 5 shim calls;
  the runtime blob regenerates byte-identical (842 B). Merged compiler output is
  byte-identical to theirs.
- NEW example 59_windows_grahan_runtime (their input smoke test), with the
  stdin fixture wired into the harness. Suite now 60/60.
- FIXED our merge tooling: it now syncs both src/sutram_compiler.asm and the
  working sutram.asm (a stale working file briefly produced a wrong PE).
## v34 — collaboration tooling
- NEW tools/merge_from_chatgpt.py — one command to process a returned tree:
    python3 tools/merge_from_chatgpt.py <returned.zip>          verify + report
    python3 tools/merge_from_chatgpt.py <returned.zip> --apply   merge
  It builds THEIR compiler and runs OUR golden suite against it (so their
  claims are verified, not trusted), diffs their src against ours, reports
  keyword/builtin additions AND removals, and enforces the ownership rule
  (src/ belongs to whoever holds the compiler; docs/books/examples/tests are
  Sarvam's and are never overwritten by a return).
- tests/run_tests.py now honours $SUTRAM_COMPILER, so the suite can test any
  compiler binary, not just the local one.
## v33 — language reference manual
- NEW docs/LANGUAGE-REFERENCE.md, generated from the compiler's own keyword and
  builtin tables plus the language packs, so it cannot drift from the code:
  keywords, operators with the full precedence ladder, all 34 built-ins, types,
  syntax by example, CLI usage, and a cross-language keyword table.
- The reference's example program is now example 46 and is regression-tested,
  so the manual cannot contain code that does not compile.
## v32 — test harness + shift operators + precedence fix
- NEW tests/run_tests.py: golden-file harness. Compiles and runs every example,
  compares stdout + exit code against tests/expect/. One command, 58 tests.
  (python3 tests/run_tests.py  |  --record  |  --list  |  NAME...)
- NEW operators << and >> (shift left / right), working with constants and
  variables, and constant-folded where possible.
- FIXED precedence: bitwise & ^ | now sit between comparisons and shifts
  (C ordering). Previously they shared a level with + -, so `5 << 1 | 1`
  evaluated as `5 << (1|1)` = 10 instead of `(5<<1) | 1` = 11.
- Example 45_shifts added.
## v31 — full Windows setup chapter in every book
- Chapter 17 rewritten from a one-page note into a complete, sectioned guide
  (16 sections) in all six editions: install methods A/B/C, PATH explained,
  first program, what the generated .exe contains, language packs, command
  reference, project layout, an 8-row troubleshooting table, update/uninstall,
  a Linux-vs-Windows comparison table, Windows feature status, philosophy.
- English ~1100 words; Hindi ~1058; Gujarati ~985; Telugu ~859; Tamil ~841;
  Sanskrit ~783. Each book is now 17 chapters.
- docs/WINDOWS-SETUP.md kept as the standalone reference for the same material.
## v30 — Windows native backend + guidance
- PE64 writer: generated programs are Windows executables (PE32+), not ELF.
  Target chosen by output name: .exe -> PE, .bin -> ELF (one compiler source).
- Embedded runtime blob: locates kernel32 via the PEB (no import table),
  emulates the standard output/input/exit calls on Windows.
- Windows argv via GetCommandLineA; compiler I/O behind an OS layer
  (Linux syscalls / kernel32).
- Fixed: generated PE section is now writable (was read-only -> faulted in
  the runtime before printing anything).
- Fixed: parser no longer crashes on malformed nested input — it reports a
  diagnostic (learned from the handed-back notes).
- Adopted the Windows packaging work: Win32 wizard installer, PowerShell
  build/preflight/install/uninstall scripts (windows/).
- Books: every edition gains chapter 17 "Windows setup" in its own language.
- New docs/WINDOWS-SETUP.md: install, usage, troubleshooting, feature status.
## v28 (2026-09-30) — compiler v29
Major capability batch: real functions + strings.

### New
- Function parameters and arguments now actually pass values
  (up to 3 args: rdi, rsi, rdx). Recursion works, including early
  returns inside if/loops.
- Block comments /* ... */ (multi-line).
- likha(a, b): print two values in one call, e.g. likha("x = ", x)
- shabda(s): print a NUL-terminated string held in a variable
  (native words in every language pack: શબ્દ, शब्द, சொல், శబ్దం, ...)
- Nested calls as arguments: joda(gunana(2,3), varga(4))

### Fixed (silent wrong-answer bugs)
- Binary ops and if/while comparisons saved their left operand in
  rdx (caller-saved) -> corrupted by any function call. Now on stack.
- pratiyati (expr): a leading '(' was read as "no return value" ->
  parenthesised returns silently returned 0.
- Nested call arguments clobbered the shared call_args buffer.

### Examples
- 40_functions_params, 41_recursion, 42_block_comments,
  43_nested_likha, 44_shabda

## v27 (2026-09-30)
- The trilingual method now starts in the index itself: every TOC entry
  and every chapter heading shows native title + English gloss side by
  side, and native words hover to their Sanskrit keyword
- Chapter headings keep their numbers (1.-16.)
- All v26 changes included (hover in prose and code, de-transliterated
  titles, yadi/anyatra fix, double-numbering fix)

## v25 (2026-09-30)
- 100% native programming: every keyword, including loop ranges,
  now writable in your language (new native 'to' words:
  થી, से, முதல், నుండి, থেকে, ರಿಂದ, മുതൽ, पासून, ଠାରୁ, ਤੋਂ)
- Glossary-consistent synonyms added to all 10 language packs
  (e.g. Telugu accepts both చరం and చరరాశి for vitti)
- New examples: 37_native_gujarati, 38_native_hindi, 39_native_tamil —
  complete programs with every word in the native language
- Chapter 11 of every book rebuilt: full three-way table
  (your language | English | Sanskrit) + complete native program
- Compiler v28

## v24 (2026-09-30)
- Error messages now print in the loaded language pack's language
  (10 languages: Bengali, Gujarati, Hindi, Kannada, Malayalam, Marathi,
  Odia, Punjabi, Tamil, Telugu) — e.g. with --lang hindi:
  "सूत्रम् त्रुटि: पंक्ति 3 के पास टोकन ..." + hint in Hindi
- Fixed pre-existing bug: error hint string was not null-terminated
- New Chapter 16 in all 6 books: Sanskrit Roots — every keyword's
  Sanskrit root and its living form in the reader's own language
  (incl. the shunya -> Arabic sifr -> English zero journey)

## v23 (2026-09-30)
- New Chapter 15 in every book: Technical Glossary
- 15 core terms per language, each with the proper native word
  AND an in-language explanation of why it is the standard term
  (textbook tradition, etymology, accepted alternatives)
- English edition: cross-language comparison table of all terms

## v22 (2026-09-30)
- grahan() returns -1 on EOF; interactive programs terminate cleanly
- Fixed same-name loop-variable reuse (pre-existing bug)
- Comments: # and // styles
- Descending for-loops (auto direction detection)
- All 6 books: proper native terminology + chapter 14 (new features)
- 49 examples total, full regression passing


## v21 (2026-09-30)
- Compound assignment operators: += -= *= /= %=
- Increment/decrement: ++ --
- Compile-time string concatenation: "a" + "b", "a" + 42, 42 + "a"
- lkhb() builtin: print number without trailing newline
- nishkriya() keyword: inline x86-64 machine code from hex string
- 7 new examples (28-34)
- 47 total examples, full regression passing

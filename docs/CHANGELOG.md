## v138 — collaboration reverts to ChatGPT; Gemini folders removed

- **`Sarvam-to-Gemini/` and `Gemini-to-Sarvam/` are removed** from the repository, at the user's
  direction. The plan to move the compiler-side partnership to Gemini is cancelled.
- **The ChatGPT folders are intact and remain the working channel** — `Sarvam-to-ChatGPT/` (28 files)
  and `ChatGPT-to-Sarvam/` (61 files). **`Sarvam-to-ChatGPT/ROUND-65.md` is already waiting there**, so
  the next ChatGPT round needs no reissue.
- **Why the Gemini move was abandoned:** Gemini's chat could not reach the repo at all. It reported the
  repository as private, which is **factually wrong** — verified by an unauthenticated request returning
  HTTP 200 with `private: false` (a genuinely private repo returns 404), plus successful anonymous
  fetches of the README, the round brief, and the API. The blocker was Gemini's own tooling, not the
  repo's visibility, and changing the Google vs GitHub email would not have helped.
- No project source, library, test, doc or GUI file was touched by this change — only the two
  collaboration folders.
- **Next:** ROUND-65 stands as issued to ChatGPT (implement the two peepholes and the default-OFF
  overflow trap even if untested; extend Devanagari past the core keywords; document the legacy HKLM
  installer honestly).

## v137 — collaboration shifts from ChatGPT to Gemini

- **Created `Sarvam-to-Gemini/` and `Gemini-to-Sarvam/`** for all new collaboration work. Both carry a
  README stating the working agreement, the current project state, and the lessons carried forward
  from the ChatGPT rounds.
- **The ChatGPT folders are kept as an archive** — `Sarvam-to-ChatGPT/` (28 files) and
  `ChatGPT-to-Sarvam/` (61 files) are untouched. No new rounds go there; the full history stays readable.
- **ROUND-65 reissued as the first Gemini round** (`Sarvam-to-Gemini/ROUND-65.md`). Its substance is
  unchanged: implement the two peepholes and the default-OFF overflow trap even if untested, extend
  Devanagari past the core keywords, and document the legacy HKLM installer honestly.
- **Why the README matters:** it records what cost real rounds — the partner may not be able to
  execute (ChatGPT had no NASM/Windows/Wine for three rounds and declined execution work each time),
  so the new agreement is explicit: **the partner does source work; Sarvam does all native execution
  and Windows testing.** A source-only claim is labelled as such, never presented as a build or
  runtime result.
- Muse's channel (`Sarvam-to-Muse/`, `Muse-to-Sarvam/`) is unchanged.

## v136 — Linux X11 GUI slice 23: Devanagari keyword colouring (my own stream)

- The GUI tokeniser now colours **Devanagari keywords**. Previously `kw_tab`/`bi_tab` were ASCII-only
  and `is_word_char` rejected the `0xE0` lead byte, so a Devanagari keyword never entered the keyword
  path at all.
- Three changes, mirroring the compiler's `is_alpha`: `is_word_char` accepts `0xE0`; `kw_tab` gains
  the Devanagari spellings (मुख्य, वित्ति, अङ्क, यदि, यावत्, लिख); `bi_tab` gains द्वारम्; and
  `.c_w_loop` consumes a whole 3-byte Indic sequence instead of stopping after the lead byte.
- **A real bug caught while writing it:** `.c_w_loop` advanced one byte at a time, so it would have
  stopped after the `0xE0` and mis-measured the token. Fixed with a bounded 3-byte advance.
- GUI source 84,614 chars; binary **35,320 B**; **all 13 GUI tests pass**. Compiler untouched.
- Honest caveat: verified by **build + full regression**, not a dedicated colour assertion — the mock
  X keyboard cannot emit a 3-byte UTF-8 sequence. Known gap, not claimed proven.

## v135 — ChatGPT R64 (kosh diagnostics) + Muse R21 (kosh spec) verified and SYNCED

- **R64 accepted — I built and ran it.** Compiler builds (189,480 B); all R64 gates pass: the three
  empty-kosh diagnostics (`kosh pop` unchanged, new `kosh peek`, new `kosh dequeue`), `kosh_nonempty`
  exact stdout, `default_compat` exact stdout, and the A/B ChatGPT could not run —
  **`R64_DEFAULT_BINARY_IDENTICAL_PASS bytes=300`** (default binary byte-identical pre/post R64).
  R63 acceptance still 9 gates; suite **187/3**; codegen **12/12**; packs **33/33**; graph **OK**;
  proofs **170/170** and **60/60**; R58 **8/8**; R59 **3/3**.
- **Muse R21 accepted.** Patch clean; **12/12 hashes**; proof_lib **172/172** (was 170), proof_props
  **62/62** (was 60), suite **187/3**; library now **21 modules / 268 functions**. The compiler-side
  `kosh` builtin spec was written, including that `kosh_clear` zeroes the logical length but does NOT
  erase storage.
- **Process change recorded:** ChatGPT has now reported the same environment limit three rounds running
  (no NASM/Windows/Wine/PowerShell), declining execution work. ROUND-65 therefore restructures their
  brief: **they do source work and static reasoning; I do all native execution and Windows testing.**
  Unverified source I can build and test is worth more than a third consecutive "NOT IMPLEMENTED".
- **23 files synced** (R64 compiler + tools + 7 fixtures + doc; R21 library + docs + 4 fixtures).
- **Next:** ROUND-65 to ChatGPT (implement the two peepholes and the default-OFF overflow trap even
  untested; extend Devanagari past the core keywords; document the legacy HKLM installer honestly).
  ROUND-22 to Muse (reconcile the kosh spec with the shipped diagnostics, remaining container gaps,
  accumulated small gaps, final trap-vs-checked note).

## v134 — ChatGPT R63 (kosh builtins) + Muse R20 (string surface) verified and SYNCED

- **R63 accepted — and I ran the gates they could not.** ChatGPT marked it source-level only; I
  built it and it passes. Compiler hash matches theirs exactly (`f52a9ad7...`); builds to 189,168 B;
  **`R63_NATIVE_ACCEPTED 9 gates`** — `kosh_fifo_core`, `kosh_fifo_float`, the danda regression, both
  expected compile errors, and the empty-peek / empty-dequeue traps. Suite **187/3**; codegen
  **12/12**; packs **33/33**; graph **OK**; proofs **167/167** and **57/57**; **R58 baseline 8/8**
  and **R59 baseline 3/3** untouched.
- **The five `kosh` builtins close the gap Muse named in R19:** `kosh_clear`, `kosh_empty`,
  `kosh_peek`, `kosh_enqueue`, and a FIFO `kosh_dequeue`. They are compiler builtins, not library
  functions — exactly as Muse proved they had to be (no generic parameter type, no overloading).
- **Muse R20 accepted.** 13 new functions across all four workstreams (the `strb_`/`str_` surface
  parity, `map_resize`/`set_resize`/`list_swap`/`list_reverse`, `ganita_checked_fact`/
  `ganita_sat_pow`). Patch clean; **14/14 hashes**; proof_lib **170/170** (was 167), proof_props
  **60/60** (was 57), suite **187/3**; library now **21 modules / 260 functions**.
- **The per-pair table was the right shape of answer** — what was added *and* what was deliberately
  not, with reasons (`is_*_char` already serves both surfaces). Slice-correctness was measured, e.g.
  `strb_find_char("hello world", 5, 'w')` -> `-1` where the NUL-terminated form would read past the
  slice end.
- **32 files synced** (R63 compiler + tools + 14 fixtures + doc; R20 library + tests + docs).
- **Next:** ROUND-64 to ChatGPT (execute the Windows acceptance at last, the two deferred peepholes,
  an **opt-in** overflow trap, and accurate `kosh_peek`/`kosh_dequeue` diagnostics). ROUND-21 to Muse
  (write the compiler-side `kosh` builtin spec, remaining container gaps, accumulated small gaps, and
  the final trap-vs-checked division of labour).

## v133 — Linux X11 GUI slice 22: danda recognition in the tokeniser (my own stream)

- The Linux GUI tokeniser now recognises the **danda `।` / double danda `॥`** as a single 3-byte
  token and colours it **orange** (`COL_DANDA`), instead of letting `classify` split it into three
  separate bytes and mis-colour them. Matches the Windows side and the new language feature.
- Implementation: `classify` tests for the `E0 A5 A4` / `E0 A5 A5` sequence first and returns a new
  class 6 with length 3; `draw_line_coloured` maps class 6 to `COL_DANDA`.
- GUI source ~83 KB; binary **35,128 B**. **All 13 GUI tests pass.** Compiler untouched.
- Honest note: the danda colouring is verified by **build + full regression**, not by a dedicated
  colour assertion — the mock X keyboard cannot emit a 3-byte UTF-8 sequence, so there is no
  protocol-level proof of the orange paint yet. Recorded as a known gap, not claimed as proven.
- **Windows artifacts rebuilt for the user's own testing** and delivered: `Sutram-Setup.exe`
  (596,624 B) and `sutram-windows-test.zip` (222,296 B), both carrying `lang/sanskrit.lang` and
  `examples/218_sanskrit_devanagari.sm`.

## v132 — ChatGPT R62 (Windows acceptance tooling) + Muse R19 (map_clear, container breadth) verified and SYNCED

- **Muse R19 accepted — all four workstreams landed.** 8 new functions and 1 strengthened:
  `map_clear` (full zero, not just the count), `set_clear`, `queue_clear`, `list_clear`
  (strengthened to zero data cells), `map_get_default` (removes the `-1`-is-ambiguous hazard),
  `set_equals`, `strb_reverse` (safe in place), `strb_count` (non-overlapping), and
  `ganita_checked_pow`. Patch applied cleanly; **14/14 hashes match**; proof_lib **167/167**
  (was 164), proof_props **57/57** (was 54), suite **187/3**; library now
  **21 modules / 247 functions**.
- **R19 names a real gap rather than papering over it:** the `kosh` primitives (clear/peek/empty/
  enqueue/dequeue) **cannot be written in the library** — there is no generic `kosh` parameter type
  and no overloading, both demonstrated by compiling test programs that fail to parse. They correctly
  assigned those builtins to the compiler side instead of forcing a type-suffixed naming scheme that
  would not be "same names, same semantics".
- **ChatGPT R62 accepted as a verified partial — and it caught a real policy violation.**
  `.github/workflows/r59-native.yml` on main still carried a **`push` trigger** on a feature branch,
  against the CI notification policy (every other workflow is `workflow_dispatch`-only). **Fixed and
  merged.** They also brought the R61 Windows diagnostic script and 8-second fail-closed installer
  preflight into a review branch, added `tools/r62_windows_acceptance.ps1` (manual Prepare/Audit/
  Screenshot stages) and `docs/R62-WINDOWS-ACCEPTANCE.md`, and hardened `install-core.ps1` with
  bounded self-tests and a durable success log.
- **They were honest about what is NOT done:** workstreams 1–3 are *prepared but not executed* (no
  Windows run this round), and workstreams 4–5 (the peepholes and the overflow traps) are
  **not implemented**. They explicitly said not to merge unexecuted code on source reasoning alone.
  5/5 R62 hashes verified.
- **21 files synced** (R19 library + tests + docs; R62 workflow fix + tooling + docs). Verified on main.
- **Next:** ROUND-63 to ChatGPT (heavy — execute the Windows acceptance, then the peepholes and the
  overflow trap, informed by the new Devanagari support). ROUND-20 to Muse (heavy — continue the
  container/gap work and the compiler-side `kosh` builtin specification).

## v131 — Sanskrit script support: `sanskrit.lang` + danda terminator (slice 21)

- **The language can now be written in Devanagari Sanskrit and compiles to native machine code.**
  Added `lang/sanskrit.lang` — the core keywords in their own script — and taught the lexer to
  accept the **danda `।` (U+0964)** and **double danda `॥` (U+0965)** as statement terminators,
  exactly equivalent to `;`.
- **`sanskrit.lang`** closes a gap found in the project audit: there was a Sanskrit *book* but no
  Sanskrit *pack* — you could write Sutram in Hindi Devanagari but not Sanskrit Devanagari. Every
  line of the pack is a script variant of an existing core keyword; no new keyword was introduced.
- **New example `218_sanskrit_devanagari.sm`** — a program written entirely in Devanagari with danda
  punctuation. Verified output: `योगः = 15`.
- **A real bug in my own first patch, caught by testing and fixed.** `is_alpha()` returns true for
  the `0xE0` UTF-8 lead byte (it is the Devanagari start byte), so the danda was being **absorbed
  into the preceding identifier** — `i।` lexed as one identifier and the terminator vanished. It
  showed up only when the identifier immediately preceded the danda (`s = s + i।`); `likha(i)।`
  worked because `)` ended the identifier first. Fixed by testing for the danda sequence both
  before identifier collection and inside `.collect_id`.
- **Gates:** suite **PASS=187 / NO-EXPECTATION=3**; codegen **12/12**; language packs **33/33**
  (11 packs × 3 — the pack test now includes `sanskrit`); module graph **OK**; `proof_lib`
  **164/164**; `proof_props` **54/54**; **`R59_FROZEN_CODEGEN_ACCEPTED 3/3`** and
  **`R58_FROZEN_CODEGEN_ACCEPTED 8/8`** untouched. Compiler 184,248 B.
- **No accepted golden changed** — verified by diffing the whole `tests/expect/` tree against
  pristine main; only the new `218_*` pair was added. (The harness's `--record` also rewrites the
  trailing newline of 40 existing `.exit` files; those were restored rather than shipped.)
- Docs updated: `docs/LANGUAGE-REFERENCE.md` gains the danda and Devanagari sections and the
  `sanskrit` pack column.
- **Next:** the same device set — danda, native numerals, per-script packs — extends to the other
  Indian scripts, since all nine share the ISCII layout and the danda is already encoded once for
  all of them.

## v130 — ROUND-62 and ROUND-19 rewritten as HEAVY multi-workstream rounds

- **Direction from the user:** give longer, heavier tasks so production moves faster — with the
  explicit requirement that nothing introduces a security risk. Both open rounds were rewritten.
- **ROUND-62 → ChatGPT (5 workstreams):** (1) prove the R61 fix on real Windows with a
  legacy/fixed A/B; (2) close the installer loop end to end; (3) verify the GUI colours visually
  from a real coloured test file; (4) finish the two R59-deferred peephole patterns (push/pop
  cancellation, adjacent store/reload) at the emission site only; (5) the compiler-level overflow
  trap (`jo`/`jno` after `+ - *`, zero-divisor guard before `idiv`, abort naming file:line) — the
  `src/` half of Muse's R18 library work.
- **ROUND-19 → Muse (4 workstreams):** (1) `map_clear` (their friction note 3); (2) container
  breadth — audit map/kosh/list/set for the same gap, give `kosh` the stack/queue primitives, with a
  per-container table of what changed and what deliberately did not; (3) close the accumulated small
  library gaps across map/kosh/list/set/strb/ganita; (4) the library half of the overflow safety net,
  composing with the trapping compiler and documenting the trap-vs-checked division of labour.
- **Security constraints made explicit and hard** in both rounds: least privilege (no UAC/admin/HKLM,
  no disabling OS protections), **no credentials** anywhere (placeholders only, including tests and
  commit messages), no new network access from compiler/GUI/installer/library, and no experimental
  workflow firing on every push. Both rounds say: if a step appears to need elevated rights, stop and
  report instead of doing it.
- Each workstream is independently acceptable, so a partial landing is still a win — both rounds say
  to ship what is finished and name what is not.

## v129 — ChatGPT R61 (Windows PE-padding root cause) + Muse R18 (checked arithmetic) verified and SYNCED

- **R61 is the best root-cause work in the project so far.** The Windows compiler hang was not
  blocking input: a 46-byte program produced a **533,114,623-byte** output before the 12 s kill. The
  mechanism is `write_pe .pp_pad_go` keeping the fill chunk in **RDX**, which `WriteFile` clobbers per
  the Win64 ABI, so the padding loop never progressed. They proved it from the real evidence (PE32+
  headers, 1024-byte SizeOfRawData, excess zeros) and noted `.r56_pe_data_write` already used
  `push rdx` / `pop rdx` — which is what tipped it.
- **The fix is merged:** exactly `push rdx` / `pop rdx` around the `os_write` and nothing else. On
  Linux it is a no-op — the build is byte-size-identical to R59 and all gates pass (186/3, 12/12,
  30/30, proof_lib 164/164, proof_props 54/54, `R59_FROZEN_CODEGEN_ACCEPTED 3/3`). A test program
  emits a sane 206 bytes. **Windows execution of the fix is still unverified** and is now ROUND-62.
- **They inspected the R60 screenshots this time** and reported honestly: menus render; the editor
  showed only `001` so the colours are not verifiable from it; the installer said "Sutram setup did
  not complete".
- **Muse R18 verified and accepted.** 8 new functions in `lib/ganita.smlib` — `ganita_checked_*`
  (add/sub/mul/div/mod) and `ganita_sat_*` (add/sub/mul). Patch applied cleanly; **5/5 hashes match**;
  proof_lib **164/164** (was 162), proof_props **54/54** (was 50), suite **186/3**; library now
  **21 modules / 239 functions**.
- **The mechanism choice was right:** opt-in checked functions with the operators unchanged, so no
  accepted golden moves and no `src/` change. Failure returns **0, never the wrapped value** — a
  caller who forgets to check gets an obviously-wrong 0, not a plausible-but-wrong number.
- 10 files synced (R61 compiler; R18 library + tests + docs). Verified on main.
- **Next:** ROUND-62 to ChatGPT — prove the R61 fix on real Windows, then close the installer loop.
  ROUND-19 to Muse — `map_clear` (their last queued friction note).

## v128 — Muse R17 (map_keys_bytes) verified and SYNCED; ROUND-18 issued

- **Muse R17 accepted.** Patch applied cleanly to pristine main; **6/6 hashes match**. `proof_lib`
  **162/162** (was 161), `proof_props` **50/50** (was 49), suite **PASS=186 / NO-EXPECTATION=3**,
  `gen_stdlib_ref.py` reproduces **21 modules / 231 functions** exactly.
- **The decision was the right one:** they **added** `map_keys_bytes` and kept `map_keys` unchanged,
  because changing the meaning would silently break its consumers — the very bug class the round
  removes. Their before/after table (size correct, keys corrupted) is the evidence that mattered.
- All five `set.smlib` call sites migrated; the `strb_pack` round-trip deleted; temp buffers shrink
  from cells to bytes. `set_to_array`'s output contract kept, so its golden is byte-identical.
  `examples/215_r12_wordfreq.sm` correctly left alone (different dance, out of scope).
- 7 files synced. Verified on main.
- **ROUND-18 issued to Muse:** make integer overflow **loud** instead of silently wrapping (their own
  friction note 4) — same correctness shape as the `map_keys` bug. `map_clear` stays queued behind it.
- **Still open:** ROUND-61 with ChatGPT (Windows compiler hang).

## v127 — Linux X11 GUI slice 20: clickable menu bar (my own stream)

- **The Linux GUI now has a menu bar** — File / Edit / Shell / Debug / Options / Window / Help —
  drawn in the top strip, matching the Windows IDLE. It is **clickable**: a click opens the menu
  (teal highlight) and draws its dropdown; File carries Open / Save / Exit, and Exit quits.
- The GUI was **keyboard-only until now** — the event loop handled only `Expose` and `KeyPress`.
  Slice 20 adds `ButtonPress` (opcode 4) handling with event-x/event-y hit-testing
  (`[event+24]`/`[event+26]`).
- **Implementation:** `draw_menu_bar`, `menu_hit` (strip hit-test), `draw_dropdown`, `menu_click`
  (open / fire item / close) and `do_menu_action`. Save calls the existing `save_saved`; Exit sets
  `want_quit`. Pure NASM, no new dependencies.
- **New test `tools/test_x11_menu.py`** (slice 20 proof): clicks the File label and asserts the
  highlight + dropdown backgrounds appear in the protocol stream, then clicks Exit and asserts the
  process quits. **All 13 GUI tests pass.**
- One build error caught and fixed: I referenced a non-existent `save_mode`; Ctrl-S calls
  `save_saved` directly, so the menu Save action now does the same.
- GUI source now ~80 KB; binary 35,000 B (was 33,384). Compiler untouched.
- **Open rounds:** ROUND-61 with ChatGPT (Windows compiler hang), ROUND-17 with Muse.

## v125 — Linux X11 GUI slice 19: per-token syntax colouring (my own stream)

- **The Linux GUI now colours the editor per token**, matching the approved palette: keywords
  **orange** #E86D11, builtins **teal** #4EC9B0, strings **green** #6A9955, numbers **purple**
  #B586E8, comments **grey** #6A6A6A, on the existing dark canvas. Before this the whole editor was
  drawn in one foreground colour.
- **Implementation:** a real tokeniser in pure NASM (classify + match_tab) over the UTF-8 buffer —
  word tables for keywords and builtins, whole-word matching, string scanning with backslash
  escapes, # and // line comments, and digit-run number detection. draw_line_coloured walks a line
  and emits one ChangeGC + ImageText8 pair per token.
- **Register discipline was the real hazard.** send_req ends in syscall, which clobbers rcx and r11,
  and r12 holds the X socket fd for the whole program. The routine keeps its state in
  rbx/rbp/r13/r14/r15 plus a stack slot, and never touches r12.
- **New test tools/test_x11_colour.py** (slice 19 proof): types `likha 'a' 12` at the mock X server
  and asserts the protocol stream contains the keyword, string, number and default foregrounds.
  **All 12 GUI tests pass.**
- **Two of my own errors, caught by the test and owned:** (1) my first key-event builder put the
  keycode at offset 4 instead of byte 1, so no keystrokes registered; (2) the test's protocol walker
  omitted opcode 70 (PolyFillRect) from its whitelist and broke at the first fill, reporting only
  one colour. Both were in the test, not the GUI — the instrumented walk showed all six colours
  before either fix landed.
- GUI source now 76,042 chars; binary 33,384 B (was 31,192). Compiler untouched.
- **Open rounds unchanged:** ROUND-59 + ROUND-60 with ChatGPT, ROUND-17 with Muse.

## v124 — ChatGPT R58 (constant folding) + Muse R16 (list) verified and SYNCED

- **ChatGPT R58 verified and accepted as a verified partial.** A bounded recursive integer
  constant-folding pass on the AST at `gen_expr` (ADD/SUB/MUL/AND/OR/XOR/SHL/SHR over literal
  subtrees, nested, negatives, x86 shift-mask semantics, depth-capped at 64), safe `x+0`/`x-0`/`x*1`
  elimination that still evaluates a side-effectful LHS exactly once, and signed `x / 2^k` strength
  reduction with a correction step that truncates toward zero for negatives. 12/12 manifest hashes
  verify; builds to 183,712 B; **`R58_FROZEN_CODEGEN_ACCEPTED 8/8`**; suite 186/3, codegen 12/12,
  packs 30/30, module-graph 18/18, proof_lib 158/158, proof_props 44/44.
- **They declared the generic machine-code peephole as NOT implemented** rather than claiming it,
  with a sound reason (post-hoc byte deletion would invalidate patch lists, branch offsets and
  RIP-relative immediates). That is the right call and it is now ROUND-59.
- **They did not double-count R57's power-of-two multiply shift** as an R58 win, and they did not
  rewrite the R57 frozen baseline. I re-checked: **`R57_FROZEN_CODEGEN_ACCEPTED 6/6`, 0/6 changed.**
- **Muse R16 verified and accepted.** `lib/list.smlib` — 21 functions covering list, stack and
  queue. All three hashes match exactly; proof_lib **161/161**, proof_props **49/49**, suite
  **PASS=186**; library now **21 modules / 230 functions**. Delivered as a patch, applied cleanly.
- **Sync care:** disjoint file sets again. Copied only the 24 changed files; GUI and all previously
  accepted goldens untouched. Verified on main afterwards.
- **Process note:** `raw.githubusercontent.com` served a stale compiler after the push; the
  authoritative API blob sha (`dad3d2f4…`) confirmed the file was correct. Re-confirmed the
  standing lesson: verify with the API, not raw.
- **Next rounds issued:** ROUND-59 to ChatGPT — the instruction-boundary-safe peephole (decide at
  emission time, never post-process bytes). ROUND-17 to Muse — the `map_keys_bytes` refactor from
  their own R14 friction note, a correctness fix for a silent-misuse class.
- Main after sync: compiler `35d85b80…` (R58), GUI slice 18, library R16 (21 modules / 230 functions),
  proofs 161/49.

## v123 — GUI slice 18: graphical directory browser (verified)

- **My own stream (Linux X11 IDE), slice 18.** `Ctrl-B` opens a **directory browser**:
  entries of the current directory are listed in the editor pane, Up/Down move the
  selection (kept visible), Enter opens a file or **descends into a directory**,
  Backspace goes up one level, Esc cancels. Directories are drawn with a trailing `/`,
  and the current path is shown in the prompt strip. Ctrl-O and Ctrl-N are unchanged.
- Implementation: `getdents64` (217) into a bounded buffer, `d_type` marks directories,
  names stored NUL-separated with an offset table, `.` and `..` skipped, bounded to 128
  entries. `draw_all` routes to `draw_browser` while browsing, and the key loop skips the
  editor repaint in browse mode too.
- **One bug found and fixed during the round:** `.braccept` cleared the browse flag
  unconditionally, so descending into a directory *exited* the browser instead of staying
  in it. `br_open_sel` now reports "descended" and the flag is kept. Caught by the new
  test, not by inspection.
- Source: `ide/sutram_gui_linux.asm` 60,414 -> 70,004 chars; binary 24,776 -> 31,192 B.
  New test `tools/test_x11_browser.py` (3 checks, spawns the GUI with a controlled cwd).
- **Verification:** lists a known file, opens it and reads the buffer back through the real
  Ctrl-S save path (content matches exactly), descends into a subdirectory and lists its
  contents, Esc cancels without opening. All 3 pass. **All 11 GUI tests pass** in place.
- Compiler untouched: still R57 `2b0b5fcf…`.

## v122 — ChatGPT R57 (register expression trees) + Muse R15 (fmt) verified and SYNCED

- **ChatGPT R57 verified and accepted as a verified partial.** The expression evaluator now emits
  pure integer arithmetic trees directly into a deterministic 3-register set (RAX/R10/R11) instead
  of push/pop round-trips, with a whole-tree eligibility preflight that falls back to the untouched
  stack evaluator for anything it cannot prove safe. 12/12 manifest hashes verify; compiler builds
  to 182,680 B; `R57_FROZEN_CODEGEN_ACCEPTED 6/6` on my build; suite 186/3, codegen 12/12,
  packs 30/30, module-graph 18/18, proof_lib 153/153, proof_props 39/39.
- **I re-measured the arithmetic benchmark myself** rather than trusting their runner:
  `arithmetic_10m.sm`, 10M iterations, warmup + best of 3, pre-R57 `3631070a` vs R57, both binaries
  printing `99999990000000`: **34.009 ms -> 8.517 ms best (3.99x)**, median 34.605 -> 8.796 ms
  (3.93x). Larger than their recorded 2.11x, on different hardware; same direction. They were
  honest about runner variance and did not oversell.
- **R46 byte-parity retired for this round, as instructed**, replaced by native-stdout equivalence
  4/4 plus a proposed new frozen codegen baseline (six hashes, `tools/r57_codegen_baseline.py`).
- **Muse R15 verified and accepted.** `lib/fmt.smlib`, 23 functions: integer bases, width/alignment,
  Indian and international grouping (Indian by default), fixed decimals, signed formatting.
  Delivered as a **patch**, applied cleanly. Hashes match exactly; proof_lib **158/158**,
  proof_props **44/44**, suite **PASS=186**; library now **20 modules / 209 functions**. Their five
  documented traps are the valuable part - especially that an **untyped parameter truncates a
  `dasham` argument**, and that **redeclaration is silently ignored**.
- **Sync care:** R57 and R15 touch disjoint files. Copied only the 30 changed files; GUI (slice 17)
  and all previously accepted goldens untouched. Verified on main afterwards.
- **Next rounds issued:** ROUND-58 to ChatGPT - compile-time constant folding plus strength
  reduction and a small peephole pass, with the R57 frozen baseline to be re-proposed rather than
  silently rewritten. ROUND-16 to Muse - `lib/list.smlib` (dynamic list, stack, queue).
- Main after sync: compiler `2b0b5fcf…` (517,157 B source, 182,680 B binary), GUI `b5d19201`
  (slice 17), library R15 (20 modules / 209 functions), proofs 158/44.

## v121 — all documents moved to the new thread logo; icon assets added to the tree

- **The old logo was still in the docs, and you were right to flag it.** The previous logo
  (Devanagari स between braces) was embedded as a **base64 PNG** in exactly six files - the six
  book editions. `docs/mockup-setup.html` already carried the new thread logo.
- **Replaced in all six books** (English, Hindi, Sanskrit, Tamil, Telugu, Gujarati) with the new
  thread logo as clean **inline SVG** - teal `#1A4A5C` disc, orange `#E86D11` ring and S-curve,
  copied verbatim from the canonical `icons/sutram-icon.svg`. The SVG parses as valid XML.
- **`docs/mockup-setup.html`**: its three remaining base64 images were converted to the same
  inline SVG, and its `.titlebar img` / `.hero img` size rules were extended to `svg` so the
  layout is unchanged.
- The tree is now **free of base64 images and of `<img>` entirely** - one identical logo asset
  (the inline SVG) in every document that carries a logo.
- **Icon assets were missing from the tree altogether.** They existed only inside a previously
  built Windows package. Added the canonical `icons/` folder: `sutram.ico` (a real 8-size icon -
  16/20/24/32/48/64/128/256, 36,693 B, byte-identical to the installer's copy), `sutram-icon.svg`,
  and the PNG ladder (1024 master down to 16).
- **Not changed, deliberately:** `docs/sutram-book-2.html` and `docs/sutram-book-3.html` are
  "superseded" stub pages with no logo at all. `windows/` documentation already refers to
  `icons/sutram.ico` and describes the thread logo, so it needed no edit.
- **Known limitation, unchanged:** the Windows GUI loads its icon from `icons\sutram.ico` **at
  runtime**; the icon is not embedded in the executable, so the file must sit beside the exe.

## v120 — Windows build produced and packaged; Windows test zip delivered

- **Both Windows binaries build here** with the documented commands
  (`nasm -f win64` + `ld -mi386pep`), and their PE headers verify:
  - `sutram.exe` — PE32+ console, x86-64, 167,789 B, 5 sections, import table present, **0 warnings**.
  - `sutram-ide-gui.exe` — PE32+ GUI, x86-64, 32,215 B, 5 sections, import table present
    (61 benign NASM warnings: the import-pointer slots are initialised in `.bss`, which
    NASM ignores by design).
- **Still unverified on Windows.** Format and headers are checked; neither binary has been
  *executed* on a real Windows machine. This remains the project's largest untested claim.
- **Delivered two zips:** `sutram-progress.zip` (full project snapshot, 1,426 files) and
  `sutram-windows-test.zip` (ready-to-run Windows folder: both exes, `sutram.cmd`, lang/lib/
  examples/docs, and a READ-ME-FIRST with honest status).
- **Note for the record:** the first GUI link attempt produced a 3,729-byte stub. Cause was my
  own build command — piping NASM's output through `head` closed the pipe and killed the
  assembler (SIGPIPE) mid-write, truncating the object. Rebuilding without the pipe gives the
  correct 32,215-byte PE. Lesson: never pipe a long-running assembler through `head`.

## v119 — GUI slice 17: open-file prompt, new buffer, and a prompt-overdraw fix

- **My own stream (Linux X11 IDE), slice 17.** `Ctrl-O` opens a file by path through
  an `Open:` prompt (type the path, Enter loads it; Esc cancels); `Ctrl-N` starts a new
  empty buffer. Loading replaces the buffer, resets the caret and scroll, clears any
  selection, and pushes an undo snapshot. A failed open leaves the buffer untouched and
  reports "Sutram IDE: cannot open that file." in the output pane.
- **A real pre-existing defect found and fixed.** The key loop called `draw_editor` after
  *every* key, and `draw_editor` repaints the whole editor pane - which contains the
  prompt strip at `ED_Y+ED_H-12`. So the prompt was drawn by `draw_all` and then
  immediately overpainted: **the find prompt had never actually been visible**. The loop
  now skips the repaint while a prompt is open. Proven with a request-order probe:
  baseline `Find` prompt drawn=True, **overpainted=True**; fixed build drawn=True,
  **overpainted=False**.
- Source: `ide/sutram_gui_linux.asm` 55,317 -> 60,414 B; binary 23,880 -> 24,776 B.
  New test: `tools/test_x11_open.py` (5 checks).
- **Verification.** The test reads the buffer back through the real Ctrl-S save path:
  open-by-path loads exactly the file's bytes; `Ctrl-N` empties the buffer; a bad path
  leaves the buffer untouched and shows the error; Esc cancels without loading; and the
  prompt is drawn and **not** overpainted (checked by scanning the ordered request
  stream for a PolyFillRect covering the prompt strip after the prompt text).
  **Negative control:** against the slice-16 binary the same test fails - `Ctrl-O`/`Ctrl-N`
  type literal `o`/`n`, no `Open:` prompt is ever drawn, and Esc quits the app.
- All 10 GUI tests pass against the new binary, run in place (protocol, negatives, run,
  scroll, edit, edscroll, keys, find, clipboard, open).
- Compiler untouched this round: still `d0fe190c…`, 179,888 B, suite 186.

## v118 — ChatGPT R56 (module globals) + Muse R14 (set) verified and SYNCED

- **ChatGPT R56 verified and accepted.** Module-level `vitti` globals: a dedicated global
  symbol/storage namespace separate from `var_table`, local/parameter shadowing, once-only
  ordered initialisation (including non-literal and function-call initialisers), zero default,
  RIP-rel32 read/write emission with compiler-side backpatch, and a PE `.data` section.
  I reproduced every gate on my own build from their tested commit `e84df728`:
  **19/19 SHA-256 manifest entries verify**; compiler builds **179,888 B** (was 176,712);
  **all 10 positive native cases** produce exactly the claimed stdout and **4 negatives exit 1**
  with located diagnostics (`R56_GLOBAL_ACCEPTED` all-ones, `pe_data=1`, PE `.data` RVA
  `0x2000`, 6 RIP refs). Suite **PASS=186 / NO-EXPECTATION=3**, codegen **12/12**, packs
  **30/30**, module-graph **18/18**, `proof_lib` **147/147**, `proof_props` **33/33**,
  R55 regression passes (`global_vitti_now_supported=1`), and **R46 byte parity holds 4/4**.
- **Sync care:** their branch's `ide/` was the *older* GUI, so a wholesale copy would have
  reverted slice 16. Copied **only the 19 PR files**; main's GUI stays `e065d205` and `lib/`
  was already identical. Verified after sync.
- **Muse R14 verified and accepted.** `lib/set.smlib` — 10 set operations over `map`
  (init/add/contains/remove/size/union/intersect/difference/is_subset/to_array), byte-string
  elements, sorted `to_array`. Reproduced: `proof_lib` **153/153**, `proof_props` **39/39**,
  suite **PASS=186**. All three claimed hashes match; **19 modules / 186 functions** confirmed
  independently, and regenerating the stdlib reference is **byte-identical** to the committed one.
  Their `PASS=185` is the known pre-existing `79_ayojan_cwd` environment case.
- **Process note recorded:** R14 arrived **directly on `main`** — no patch in `Muse-to-Sarvam/`
  and no branch, so I had to reconstruct it from main to verify it. It checked out, but an
  unreviewed change on main is one I cannot reject. Asked Muse to return to patch/branch delivery.
- **Next rounds issued:** ROUND-57 to ChatGPT — the register-based expression evaluator (the
  largest measured gap; arithmetic loop is 5.4x off hand-optimal). R46 byte parity is explicitly
  expected to break this round, with correctness to be shown by suite/proofs/native stdout and a
  new frozen baseline proposed. ROUND-15 to Muse — `lib/fmt.smlib` formatting module.
- Main after sync: compiler `d0fe190c…` (506,617 B source, 179,888 B binary), GUI `e065d205`
  (slice 16), library R14 (19 modules / 176 -> 186 functions).

## v117 — GUI slice 16: selection + internal clipboard (verified)

- **My own stream (Linux X11 IDE), slice 16: clipboard.** The editor now has a
  selection model and an internal clipboard:
  - Shift+Left/Right/Up/Down/Home/End extend a selection (the anchor is set on
    the first shift-move).
  - Ctrl-A selects the whole buffer; Ctrl-C copies; Ctrl-X cuts; Ctrl-V pastes.
  - With no selection, Ctrl-C copies and Ctrl-X cuts the current line (cut takes
    the trailing newline too).
  - Typing or Backspace over a selection replaces it.
  - Plain navigation clears the selection. Escape clears a selection *before* it
    quits — Escape only quits when nothing is selected.
  - The selection is painted as a highlight (ChangeGC foreground 0x2B4A6B
    followed by PolyFillRect) beneath the line text.
- Source: `ide/sutram_gui_linux.asm` 46,452 -> 55,311 B; binary 21,992 -> 23,880 B.
  New test: `tools/test_x11_clipboard.py` (8 checks).
- **Verification.** The new test reads the buffer back through the real Ctrl-S
  save path, so it proves the whole pipeline, not just protocol bytes: copy-all
  then paste, cut-line then paste, shift-select then copy, escape-clears-selection
  (the process stays alive), backspace-deletes-selection, type-replaces-selection,
  and highlight-colour present/absent. All 8 pass.
  **Negative control:** against the slice-15 binary the same test fails — the
  highlight is absent, Ctrl-C types a literal `c`, and Escape quits the app
  (broken pipe). The test therefore discriminates; it is not vacuous.
- All 9 GUI tests pass against the new binary, run in place (protocol, negatives,
  run, scroll, edit, edscroll, keys, find, clipboard).
- Compiler untouched: R55 still builds 176,712 B from a 494,900 B source, suite
  PASS=186.
- **Base hygiene:** the local compiler source had drifted to an older round
  (455,363 B) while main is R55 (494,900 B). Refreshed the local copy from main
  and re-verified 176,712 B / PASS=186. Only the GUI and the new test are pushed;
  the compiler is deliberately not touched.

## v116 — Muse R13 accepted; ChatGPT R55 (forward prototypes, PARTIAL) verified and SYNCED

- **Muse R13 verified and accepted.** `strb_pack`/`unpack`/`dup` plus six integer
  statistics (`purna_yoga/madhya/laghutama/adhikatama/vyapti/prasaran`); two existing
  modules reworked to use the helpers (`strb_split`/`join`, `map_key_eq`/`map_keys`),
  with two deliberate non-conversions documented at the call sites. All four claimed
  hashes match. On my build: proof_lib **147/147**, proof_props **33/33**, stdlib
  **18 modules / 176 functions**. The R12 wordfreq example was shortened 84 -> 82
  lines with **byte-identical** output. They also found a real trap and documented
  it: **Sutram pointer arithmetic is in bytes**, so a cell index must be scaled by 8.
- **Their `79_ayojan_cwd` COMPILE-FAIL claim is honest but environment-specific.**
  Muse reported `PASS=185 COMPILE-FAIL=1`; on my run of main it is `PASS=186` with no
  compile-fail, because that test is cwd-dependent. Either way it is pre-existing and
  not caused by R13.
- **ChatGPT R55 verified and accepted as a PARTIAL, exactly as the handoff states.**
  Gap 1 is done: real forward declarations (`prakriya name(params);`) with arity and
  parameter-type matching, duplicate/missing/mismatch rejection, and definition-order
  independence. `R55_FORWARD_ACCEPTED two_cycle=1 three_cycle=1 prototype_mismatch=1
  type_mismatch=1 duplicate=1 missing=1 global_vitti_unimplemented=1`. The two-function
  cycle is **tighter than Muse's R12 cycle** and the three-function cycle has its
  definitions ordered against the call chain; both run natively. Manifest 10/10.
  **Gap 2 (module-level globals) is NOT implemented**, and they say so plainly rather
  than claiming it - with a real design rationale (globals need an independent symbol
  and storage namespace with local-shadowing precedence and ELF/PE writable storage,
  not a reused register or stack slot). That is the right call.
- **Sync care:** the R55 branch predates Muse's R13, so its `lib/`, `docs/sutram-stdlib.html`,
  `examples/215` and `tests/stdlib/*` were older. I copied **only** the compiler,
  `r55-native.yml`, the acceptance tool, `tests/r55_check/` and the ROUND-55 handoffs
  (14 files) and verified afterwards that main still has Muse's `strb` `957167a0…`.
- Main after sync: compiler `6db0adf7…` (176,712 B), GUI `cb3c78d7…`, library R13;
  186/12/30/18, proof_lib 147/147, proof_props 33/33.
- Windows end-to-end remains out of scope and unverified, as ChatGPT restates.

## v115 — Linux GUI IDE, slice 15: find (Ctrl-F)

- **Ctrl-F opens a find prompt on the bottom line.** Typing fills the search
  string, **Enter** searches, **Esc** cancels. The search is a plain substring
  scan of the editor buffer from the caret, and **wraps** to the start if it runs
  off the end; on a hit it moves the caret there. Backspace edits the search
  string. The prompt replaces the key hint while it is open.
- **Verified with a mock X server** (`tools/test_x11_find.py`): `abcabc`, caret at
  the end; Ctrl-F, `bc`, Enter -> wraps and finds `bc` at index 1; typing `z`
  lands at that hit giving `azbcabc`. Then Ctrl-F, `abc`, **Esc**, `q` -> `azqbcabc`,
  proving Esc leaves the caret where it was. Both checks pass.
- Protocol 39/39, negatives 6/6, and the scroll / Home-End / editor-scroll / Tab
  tests all still green. `sutram-gui` 21,104 -> 21,992 bytes.
- Debugging note worth keeping: my first test sent Ctrl-F **without the control
  modifier**, so it typed a literal `f` and find mode never opened - and the
  subsequent Esc then quit the application. The IDE was correct throughout; the
  test was wrong. Took a while because the symptom (a stray `f`, then the app
  exiting) looks like a feature bug. When a control key "does nothing", check the
  test actually sent the modifier.

## v114 — Muse R12 accepted; ChatGPT R54 verified and SYNCED to main

- **Muse R12 verified and accepted.** Three real programs — word frequency
  (`strb_split` + `map` + sort), an expression evaluator (recursive descent with
  precedence and parentheses), and a formatted report (`strconv` padding) — all in
  `examples/` with goldens. All hashes match and **all three reproduce their goldens
  byte-for-byte** on my build. The findings report is the valuable part and names
  real language gaps: no globals (state must be threaded through every signature);
  **no forward declarations, so mutual recursion is expressible only by ordering
  luck** (a genuine gap, not awkwardness); the two string representations cause
  silent repack loops at every module boundary; `likha(buf)` prints the pointer, not
  the string; `sankhyiki` needs float arrays so integer stats are manual.
- **ChatGPT R54 verified and accepted.** A central arity table now covers **all 40
  builtin IDs**; invalid arity yields a located recoverable `E_PARSE` instead of a
  compiler fault. `R54_ACCEPTED builtin_ids=40 valid_arity=43 invalid_arity=80
  raw_memory=1 arg_capacity=1`; `R54_MUSE_ACCEPTED original=186 example_local=3
  original_golden_changes=0`.
- **They found and fixed a pre-existing codegen bug**: `vartani_cp(dst,src)` scanned
  the *destination* with `repne scasb` instead of copying the source. Demonstrated
  before/after (`0,1` -> `89,4`). That is the only builtin whose generated code
  intentionally changed. Good catch.
- Manifest **7/7 OK**; compiler `9ce0c6ad…` matches; GUI slice 14 (`b4c15d61…`),
  `strb.smlib` and `map.smlib` all preserved; `lib`/`ide`/`examples` byte-identical
  to main. Synced 11 files. Main after sync: 186/12/30/18, proof_lib 139/139,
  proof_props 30/30.
- Honest limits stated by ChatGPT and unchanged: valid-arity fixtures compile behind
  a runtime-false guard, so they prove parse/codegen, not syscall effects; raw
  pointer ops remain caller-unsafe; Windows still out of scope.

## v113 — Linux GUI IDE, slice 14: Tab indent, Ctrl-Home / Ctrl-End

- **Tab inserts a 4-space indent.** It goes through the same `ed_insert` path as a
  typed character, so it takes an undo snapshot and scrolls the pane like any edit.
- **Ctrl-Home jumps the caret to the start of the file, Ctrl-End to the end.** Both
  are caret moves only, so (like the arrows, Home/End and PgUp/PgDn) they take no
  undo snapshot.
- **Verified with a mock X server** (`tools/test_x11_keys.py`): `a`, Tab, `b` ->
  `a    b`; Ctrl-Home then `z` -> `za    b`; Ctrl-End then `y` -> `za    by`. The
  buffer is read back through Ctrl-S, so the assertion is on real saved content.
- Protocol 39/39, negatives 6/6, and the scroll / Home-End / editor-scroll tests
  all still pass. `sutram-gui` 20,936 -> 21,104 bytes.
- Test-harness note: two of my own keycodes were wrong again (26 is `e` on the mock
  keymap, not `z`; `z` is 52). The IDE was correct; the test was not. Worth
  remembering that the mock keymap is not the hardware one.

## v112 — Muse R10/R11 accepted; ChatGPT R53 (consolidated) verified and SYNCED to main

- **Muse R10 + R11 verified and accepted.** `lib/strb.smlib` (12-function
  byte-string surface) and `lib/map.smlib` (hash map, open addressing, backward-shift
  delete). All claimed SHA-256 hashes match (`strb.smlib` `336e7dda…`, `map.smlib`
  `23cf12a2…`, `proof_props.py` `b366dfb6…`). On my build: proof_lib **139/139**,
  proof_props **30/30**, suite **186/186**, stdlib **18 modules / 167 functions**.
  Both are on main already (Muse pushes directly).
- **ChatGPT R53 verified and ACCEPTED and SYNCED.** `feature/r53-consolidated-r51-r52-20261010`
  (draft PR #11) finally does what ROUND-53 asked: ONE compiler source carrying both
  R51's provenance fix and R52's defect fixes, branched from current main with
  two-parent merges so Muse's newer library is preserved rather than overwritten.
  - Manifest **26/26 OK**; compiler `a3fe1b12…` matches the claim; GUI slice 13
    (`65222ca1…`) preserved; `ide/` byte-identical to main.
  - I ran every suite myself: `R49_AUDIT_STATUS wrong_provenance=0 unlocated=0
    universal_diagnostics_accepted=1 cases=15 failures=0`, `R51_ACCEPTANCE PASS`,
    `R52_ACCEPTED PASS`, `R48_ACCEPTED_CHECK_TESTS`, `STAGE2_PASS`,
    `R49_REPEATED_SEMANTIC_PASS`, `R50_ACCEPTED`, 186/186, 12/12 codegen, 30/30
    packs, 18/18 graph, R46 parity 4/4.
  - **They also raised the compiler's AST arena from 786432 to 3145728 bytes
    (3 MiB)** because Muse's larger library overflowed `AST_HEAP_CAP` on three
    regressions. They flagged it explicitly and proved four ordinary R46 binaries
    stay byte-identical, so it is a compile-time workspace change only. I verified
    that parity myself. Good catch on their part, honestly reported.
- **Synced 36 files to main**: the consolidated compiler, the comment-only
  `string.smlib` update, `docs/R52-BUILTIN-FIXES.md`, the CI workflow, the
  `r51_check`/`r52_check` fixtures, the four audit tools, and the ROUND-51/52/53
  handoff files.
- **Main after sync:** compiler `a3fe1b12…` (builds 174,864 B), GUI `65222ca1…`,
  string `25110cc6…`; 186/186, 12/12, 30/30, 18/18, proof_lib 139/139,
  proof_props 30/30, R52 acceptance PASS, R49/R51 audits clean.
- Still open and stated plainly by ChatGPT: Windows end-to-end unverified;
  `pad`/`pad8`/`likh8`/`char_from` not audited for invalid arity; the 15-case
  diagnostic corpus is not a proof for arbitrary malformed programs.

## v111 — Folder check: R51 and R52 both verified but UNDELIVERABLE (sibling branches)

- **No handoff in either folder.** `ChatGPT-to-Sarvam/` still ends at
  `ROUND-49-50-*`; `Muse-to-Sarvam/` still ends at `round9-string-toolkit.md`.
- **ChatGPT now has two verified branches and has filed neither handoff.**
  - R51 (`feature/r51-origin-tracking-20261009`, compiler `cc5c0ff9…`): R49
    provenance genuinely closed - two-level `ayojan` -> `inner_r51.smlib:2:23`,
    namespaced -> `broken_ns_r51.smlib:2:26`, three accumulated semantic errors,
    three located `E_MODULE_MISSING`; 186/186.
  - R52 (`feature/r52-stdlib-compiler-defects-20261010`, compiler `c492161c…`):
    defect sweep works - `R52_ACCEPTED PASS indexed_char_code=1 likh_store=1
    dvaram_default_mode=0644 dvaram_explicit_mode=0600 bad_arity=5`; I also
    confirmed `dvaram` now creates `-rw-r--r--` where it used to create
    `----------`. Their honesty that `char_code`'s "ignores its index" was a
    **stale library comment**, not a live bug, is correct.
- **The blocker is structural.** R51 and R52 are **sibling branches off main**,
  not a stack: R52's compiler has no provenance fix and no `tests/r51_check/`;
  R51's has no `likh`/`dvaram` fixes. Merging either alone silently discards the
  other's work - the same stale-base pattern that nearly reverted slice 12.
- **Issued ROUND-53 to ChatGPT**: consolidate R51 + R52 onto one branch off current
  main, prove both hold together (186/12/30/18 + R46 parity 4/4), and **file the
  handoff + manifest + observed stdout** that has been missing for two rounds.
- Muse unchanged (ROUND-10, ROUND-11 open). Nothing synced; main compiler still
  `55e6ac26…`, GUI `65222ca1…`.

## v110 — Linux GUI IDE, slice 13: editor-pane scrolling

- **The editor pane now scrolls to follow the caret.** It was capped at 23 lines
  (`ED_LINES_MAX`) with everything past that silently dropped, so a file longer
  than the pane lost its tail. It now keeps `ed_top` (first visible line) and draws
  a 23-line window from there; `ed_ensure_visible` runs at the top of every
  `draw_editor`, so moving the caret or editing scrolls the pane just enough to
  keep the caret's line visible, and the caret is not drawn when it is off-window.
- **Verified with a mock X server** (`tools/test_x11_edscroll.py`): type 30 lines
  (`l01`..`l30`); the final frame shows **`l08`..`l30`** (the last 23, caret at the
  bottom); then 29 Ups and the frame shows **`l01`..`l23`** (scrolled back to the
  top); the buffer is intact (`Ctrl-S` read-back gives 30 lines `l01`..`l30`).
- A test-harness note worth keeping: the pane repaints on *every* keystroke, so a
  naive drain collects thousands of draws across many frames. The test now reads
  only the **last** 23 editor draws - the current frame. My first version compared
  across frames and reported a false failure.
- Protocol 39/39, negatives 6/6, output-scroll / Home-End tests still green.
  `sutram-gui` 20,720 -> 20,936 bytes.

## v109 — R51 substance independently verified (still unreported)

- ChatGPT still has **no handoff file** for R51, so it remains unaccepted and unsynced.
  But I ran the branch's own fixtures through `--check` **with my own commands**, not
  their audit script, and the R49 gap is genuinely closed:
  - `nested_root.sm` -> `outer_r51` -> `inner_r51`: the error is attributed to
    **`inner_r51.smlib:2:23`** — correct provenance through **two** `ayojan` levels.
  - `namespaced_root.sm`: **`broken_ns_r51.smlib:2:26`** — namespaced import correct.
  - `semantic_import.sm`: **three** semantic errors, all attributed to
    `semantics_r51.smlib` — accumulation and origin both right.
  - `missing_three.sm`: three located `E_MODULE_MISSING`.
- Branch also builds (170,176 B) and passes **186/186**; it is based on current main
  (GUI `8480b95b…`). Nothing synced; main's compiler unchanged (`55e6ac26…`).
- Both AIs already hold an open task (ChatGPT ROUND-51, Muse ROUND-10), so no new
  round was issued this check — per the instruction not to duplicate.

## v108 — Folder check: nothing delivered yet; R51 in progress and looking right

- **No new delivery in either folder.** `ChatGPT-to-Sarvam/` still ends at
  `ROUND-49-50-*`; `Muse-to-Sarvam/` still ends at `round9-string-toolkit.md`.
- **ChatGPT has an in-progress R51 branch** (`feature/r51-origin-tracking-20261009`)
  with no handoff file yet, so it is **not accepted** — but the early signal is
  good and worth recording:
  - It is branched from **current main** — its `ide/sutram_gui_linux.asm` is
    `8480b95b…`, my slice-12. The housekeeping item landed; no stale-base collision.
  - Builds (170,176 B) and passes **186/186** on the in-progress source.
  - Their `tools/r51_native_audit.py` reports **`R51_ACCEPTANCE PASS failed_cases 0`**,
    and the substance is the R49 gap closing: an error inside an imported module is
    now attributed to the **imported file** (`semantics_r51.smlib:3:11`), including
    a **two-level** `ayojan` chain (`nested_root.sm` -> `inner_r51.smlib:2:23`) and a
    **namespaced** import (`broken_ns_r51.smlib:2:26`). Three semantic errors in one
    imported file are all reported (`correct_origin 3`); three missing modules each
    report; nested braces give three located parse errors.
  - Caveat: this is their own audit tool on their own WIP source. I will verify
    independently from their manifest when they file the handoff. Nothing is synced
    to main and the compiler on main is unchanged (`55e6ac26…`).
- **Muse has not answered ROUND-10 yet.** No new file.
- No new work issued: both AIs have an open task (ChatGPT R51, Muse R10).

## v107 — Muse R9 accepted; ROUND-10 issued

- **Muse R9 verified and accepted.** `lib/string.smlib` gained an 11-function text
  toolkit (find/contains/replace/split/join/trim/upper/lower/starts/ends/compare).
  Both SHA-256 hashes match; all files present. Reproduced on my own build:
  proof_lib **132/132**, proof_props **21/21**, suite **186/186**, stdlib
  **16 modules / 144 functions**. Compiler untouched (main's is ChatGPT's
  `55e6ac26…`).
- **Testing it exposed a real gap, now the next round.** My first call passed a
  string *literal* to `str_find` and got `-1`; the source indexes `h[i+j]`, so it
  wants a **char-code array**. On a char-code array it is correct
  (`str_find("hello","ll")`=2, `str_contains`=1, `str_compare(x,x)`=0,
  `str_upper("hello")`->`HELLO`). The toolkit is right; the two representations
  (byte-packed literals vs qword cells) are simply not bridged. My misuse, not a
  defect — but a genuine usability hole.
- **Issued ROUND-10 to Muse** — a byte-string surface for the toolkit (`strb_*`)
  built on the newly-available `set_char`/`char_at`, so literals flow through with
  no hand-built array; char-code API and R9 goldens untouched. Also told them main
  moved off R44 and to branch from `55e6ac26…`.
- ROUND-51 to ChatGPT (finish R49 provenance) is still outstanding; no reply yet.

## v106 — ChatGPT R49/R50 reviewed and SYNCED to main

- **ChatGPT delivered R49 and R50 in one branch** (`feature/r49-r50-completion-20261009`,
  draft PR #8) and wrote its handoff into that branch's `ChatGPT-to-Sarvam/`, not
  into main. I reviewed it independently and synced the verified changes to main.
- **Verified from the branch, then again from a fresh main checkout:** manifest
  30/30 OK; every acceptance script reproduces (`R48_ACCEPTED_CHECK_TESTS`,
  `STAGE2_PASS`, `R50_ACCEPTED`, `R49_REPEATED_SEMANTIC_PASS`); suite **186/186**,
  codegen gate **12**, packs **30/30**, module graph **OK**; `tests/expect`
  byte-identical to main. Ordinary generated code is byte-identical to accepted R46
  (4/4 samples, `126_numeric_pipeline` = 7450 B).
- **R50 is complete and closes the gap Muse found.** `set_char(buf, i, c)` writes a
  real byte; a program can now build a byte-packed string at runtime. Verified:
  `char_at(buf,0)`=104, `char_at(buf,1)`=105, `vartani_len(buf)`=2,
  `vartani_cmp(buf,"hi")`=0. `buf[i]=c` keeps its qword-cell meaning; `width_repro`
  is unchanged.
- **R49 is partial, and ChatGPT says so plainly.** Repeated-call diagnostics now
  locate each of three same-named calls distinctly, and `E_MODULE_MISSING` carries
  a column. **Still unmet: an error inside an imported module is attributed to the
  root filename** (`import_bad.sm:2:20` instead of `lib/faulty_r49.smlib`). I
  reproduced that (`R49_PROVENANCE_UNRESOLVED`, wrong_provenance=1). It is a
  diagnostic-quality gap, not a program-correctness one — so it does not block the
  sync, but R49 is **not** complete and I have opened a follow-up.
- **Windows is not accepted.** The compiler assembles and links to native PE32+ and
  `--version` runs on a Windows runner, but `--check` and a generated executable
  are not verified. Nothing has run on real Windows.
- **Sync method:** PR #8 is a draft and the API refuses to merge drafts (I tried;
  it returns "Pull Request is still a draft"). So I copied only ChatGPT's 34
  changed files to main — compiler, `win/winrt.inc`, `docs/R50-BYTE-PACKED-TEXT.md`,
  `benchmarks/`, the CI workflow, the `r48_check`/`r49_check`/`r50_check` fixtures,
  the six new `tools/r4*.py`, and the four `ChatGPT-to-Sarvam/ROUND-49-50-*` files.
  I deliberately did **not** copy the branch's `ide/`, `tools/test_x11_edit.py` or
  `docs/CHANGELOG.md` — the branch predates my slice-12 GUI work and would have
  reverted it. Confirmed after sync: GUI source still `8480b95b…`, slice-12 test
  intact.

## v105 — Linux GUI IDE, slice 12: Home/End caret movement

- **Home and End move the caret to the start and end of the current line.** Both
  reuse the `line_start` / `line_end` helpers added in slice 10. Like the arrow
  keys, neither takes an undo snapshot - they are not edits.
- **Verified with a mock X server** (`tools/test_x11_edit.py`): type `ab`, Return,
  `cde` (caret at end of line 2); Home then `x` inserts at the line start ->
  `ab`/`xcde`; End then `y` appends -> `ab`/`xcdey`. Then Up to line 1, End, `x`,
  Home, `a` -> `aabx`/`xcdey` (Home on the first line reaches index 0). Both
  checks pass; the buffer is read back through Ctrl-S so the assertion is on real
  saved content, not on screen bytes.
- Protocol 39/39, negatives 6/6, scroll test still green. `sutram-gui` 20,640 ->
  20,720 bytes.
- The caret now has the full complement: four arrows, Home, End, insertion at the
  caret, and undo that steps back through edits only.

## v104 — Muse R8 accepted; ROUND-50 (ChatGPT) and ROUND-09 (Muse) issued

- **Muse R8 verified and accepted.** `lib/strconv.smlib` (5 functions:
  int_to_str, str_to_int, int_to_base_str, str_to_int_base, pad_left), plus the
  `width_repro` fixture. Both SHA-256 hashes match; all 15 files present.
  Reproduced on my own clean build: proof_lib **128/128**, proof_props **17/17**,
  suite **186/186**, stdlib **16 modules / 133 functions**. Compiler untouched.
- **The width finding is confirmed.** `width_repro.sm` on a clean main build gives
  `104 / 0 / 104 / 105` — `char_at(buf,1)` is 0 while `char_at("hi",1)` is 105.
  `buf[i]=c` writes qword cells (correct for pankti), `char_at` reads bytes
  (correct for literals); the gap is a **missing byte-write primitive**.
- **Issued ROUND-50 to ChatGPT** — add `set_char` (byte store) so byte-packed
  strings can be built at runtime, keep `char_at` byte-based and cell assignment
  unchanged, all goldens byte-identical. Noted ROUND-49 (rebase + complete
  `--check`) is still outstanding and comes first.
- **Issued ROUND-09 to Muse** — build `lib/string.smlib` into a text toolkit
  (find/contains/replace/split/join/trim/case/compare) with properties.
- Both handoffs pushed and verified live (HTTP 200).

## v103 — Linux GUI IDE, slice 11: output-pane scrolling

- **The output pane scrolls.** It used to draw at most 7 lines and silently drop
  the rest. It now keeps a `out_top` (first visible line) and draws a 7-line
  window from there. **PgUp** (keycode 104) and **PgDn** (109) page through the
  captured output; the window clamps at both ends.
- **Auto-scroll to newest.** After a run the pane jumps to the last page, so the
  freshest output is visible without scrolling. (The call sits on *both* exit
  paths of `do_run` — the compiler-error path returns early, which is exactly
  where a first attempt at this left it out.)
- **Verified with a mock X server.** A mock compiler beside the GUI emits 10
  lines. The pane shows the newest (lines 5-10 + the trailing blank that
  `split_lines` always appends); PgUp shows lines 1-7; PgDn returns to the newest;
  two PgUps clamp at the top. All four checks pass (`tools/test_x11_scroll.py`).
- Protocol 39/39, negatives 6/6, and the slice-5 run path still draws its
  compiler output. `sutram-gui` 20,096 -> 20,640 bytes.
- Note: `tools/test_x11_run.py` asserted the pane contains the word "compiled",
  but its input (bare `likha`) is a parse error under the current compiler, so the
  pane correctly shows an error message. Broadened the assertion to the real
  property — a compiler message is drawn — rather than the stale wording.

## v102 — Fix clean-checkout build: win/ restored; GUI source + CHANGELOG pushed

- **Root cause of "the AIs can't work": the repo had no `win/` directory.** The
  compiler source `%include`s `win/rtblob.inc` (line 18721) and `win/winrt.inc`
  (line 18912), so a fresh clone could not assemble at all. ChatGPT flagged this
  too. Restored the full `win/` tree to main: `rtblob.inc`, `winrt.inc`,
  `winrt_blob.asm`, `winapi.asm`, `winio.asm`, `native_host.asm`, `probe.asm`,
  `build-windows.sh`. Both `.inc` files are self-contained (no further includes).
- **Verified on a truly clean checkout** — fresh tarball, nothing copied in:
  `nasm -f elf64 -I. src/sutram_compiler.asm` builds (162,152 B), suite
  **186/186**, proof_lib **124/124**, proof_props **14/14**.
- **Large-file write route restored.** Programmatic GitHub writes work again, so
  files are pushed from disk rather than inline. My stranded work is now on main:
  `ide/sutram_gui_linux.asm` (slices 1-10, 38,920 B) and this CHANGELOG.

## v101 — Round check: Muse R7 accepted, ChatGPT R48 accepted as Stage-1; R49/R08 issued

- **Muse R7 verified and accepted.** `lib/sort.smlib` gained `insertion_sort`,
  `merge_sort_rec`, `merge_sort`; new `lib/baseconv.smlib` with
  `bigint_to_digits` / `bigint_from_digits`. All three SHA-256 hashes match,
  all 9 test files present. Reproduced on my own build: proof_lib **124/124**,
  proof_props **14/14**, suite **186/186**, stdlib regenerates to **15 modules,
  128 functions**. Compiler untouched.
- **ChatGPT R48 verified and accepted as a Stage-1 proposal (not merged).**
  `--check` mode reproduced exactly: three located parse errors, one located
  undefined function, valid program clean, no binary in any case. Manifest 9/9
  verifies; `r48_native_acceptance.py` passes with 4/4 ordinary programs
  byte-identical between R46 and R48 (`126_numeric_pipeline` = 7450 B). 186/186,
  codegen gate, 30/30 packs, module graph OK, `tests/expect` byte-identical to
  main. Retained on branch: it is a self-declared Stage-1, and it chains off the
  unmerged R46.
- **Issued ROUND-49 to ChatGPT** (rebase R46+R48 onto main as one series; complete
  check-mode across all diagnostic families with adversarial fixtures) and
  **ROUND-08 to Muse** (`lib/strconv.smlib` plus a minimal reproduction settling
  the `buf[i]=c` 8-byte-cell vs `char_at` byte-read question). Both pushed to
  GitHub and verified live.

## v100 — Linux GUI IDE, slice 10: Up/Down line movement

- **Up and Down move the caret between lines, keeping the column.** The caret's
  line start and column are found by scanning for newlines, the caret moves to the
  same column on the adjacent line, and the column is clamped to the line's end -
  so moving up from a long line to a short one lands at the short line's end
  rather than overshooting into the next line. Two small helpers (`line_start`,
  `line_end`) do the scanning; `caret_up` and `caret_down` use them.
- **Verified with a mock X server.** Type `ab`, Return, `cde`; the caret is at
  line 2 col 3. Up, then type `x` -> `abx` / `cde` (clamped to col 2). Down, then
  type `y` -> `abx` / `cdey`.
- Like Left/Right, vertical movement takes no undo snapshot - it is not an edit.
- Protocol 39/39, negatives 6/6, run path still draws its output. `sutram-gui`
  19,552 -> 20,096 bytes.

## v99 — Linux GUI IDE, slice 9: the arrow keys work

- **Left/Right move the caret.** They were defined since slice 2 and never
  handled. Left decrements the cursor (bounded at 0), Right increments it
  (bounded at the buffer length), and the next character inserts at the caret -
  so editing in the middle of a line now works. Verified with a mock X server:
  type `abc`, press Left twice, type `x` -> `axbc`; press Right, type `y` ->
  `axbyc`.
- Arrow movement takes no undo snapshot, because moving the caret is not an edit;
  Ctrl-Z still steps back through actual changes only.
- Protocol 39/39, negatives 6/6, run path still draws its output. `sutram-gui`
  19,472 -> 19,552 bytes.

## v98 — Linux GUI IDE, slice 8: a real undo stack

- **Ctrl-Z now steps back through several edits.** Slice 7 was single-level; this
  is a bounded stack of 8 snapshots. Each edit pushes the pre-edit buffer; Ctrl-Z
  pops the most recent. When the stack is full the oldest slot is dropped, so the
  last seven edits are always recoverable. A full stack costs one 7-slot memmove
  per keystroke, which is nothing.
- **Verified with a mock X server.** Type `abc`; Ctrl-Z gives `ab`, then `a`,
  then empty, and a fourth Ctrl-Z correctly does nothing. Protocol 39/39,
  negatives 6/6, Ctrl-R run path still draws its output. `sutram-gui`
  15,392 -> 19,472 bytes (the 8-slot stack is 64 KiB of .bss).

## v97 — Linux GUI IDE, slice 7: undo

- **Ctrl-Z now undoes an edit.** The hint line had advertised "Ctrl-Z undo" since
  slice 2; it is real now. Before every insert or backspace the buffer is
  snapshotted; Ctrl-Z restores the pre-edit state and consumes the snapshot, so a
  second Ctrl-Z does nothing. Single-level on purpose — a bounded undo stack is
  the next step, not this one.
- **Verified with a mock X server.** Type `ab` (pane shows `ab`), press Ctrl-Z
  (pane shows `a`), press Ctrl-Z again (still `a`). Protocol 39/39, negatives 6/6,
  Ctrl-R run path still draws its output. `sutram-gui` 15,008 -> 15,392 bytes.

## v96 — Linux GUI IDE, slice 6: save and load

- **Ctrl-S writes the editor buffer to a file; Ctrl-L reads it back.** The hint
  line had advertised Ctrl-S since slice 2; it now actually does something. The
  save path is `/tmp/.sutram_gui_saved.sm`; load replaces the buffer and moves the
  caret to the end.
- **Verified with a mock X server, no display.** Type `saveme`, press Ctrl-S:
  the saved file contains exactly `saveme`. Backspace it all away, press Ctrl-L:
  the pane redraws `saveme`. Protocol suite still 39/39, negatives 6/6, and the
  Ctrl-R run path still draws its output.
- **One test-only mistake, mine again.** My first save/load test used the wrong
  US keycodes for `v` and `e`, so it typed `samo` and I nearly misread the result
  as a client bug. The round trip was correct the whole time; the test was wrong.
  `sutram-gui` 14,688 -> 15,008 bytes.

## v95 — R45: an ELF-write syscall reduction (performance NOT claimed)

- **Merged from ChatGPT's R45, independently verified.** Their compiler source
  (`f2fad472…`) assembles, passes **186/186**, and produces **byte-identical
  generated output** to the previous compiler across **40/40** examples — I
  compared the binaries directly. Their six-file manifest verifies, and 600 raw
  timing records are committed.
- **What changed:** the ELF write path now combines two header write syscalls
  into one contiguous 120-byte write, and uses `fchmod` on the already-open
  output descriptor instead of re-resolving the output pathname. Objectively
  fewer kernel operations.
- **No speedup is claimed, and none was demonstrated.** ChatGPT reported medians
  of +1.32%, +2.54%, -0.94%, -0.25%, +1.12% with paired success of only 17–19/30
  and called the result "modest and not statistically conclusive". My own A/B
  re-measurement was dominated by process-spawn noise (±40%). Under this
  project's rule — performance measured, not assumed — the change is accepted as
  a behaviour-preserving simplification, **not** as a performance improvement.
  R46 asks for a decisive measurement of a real hotspot.
- Optional `R45_PROFILE` cycle attribution was added, compiled out of production.

## v94 — Linux GUI IDE, slice 5: it runs your code

- **Ctrl-R now compiles and runs the buffer.** The editor saves its contents to
  a temp source, resolves the compiler as `<dir of this executable>/sutram_compiler`
  via `/proc/self/exe` (the same trick the compiler uses for language packs, so
  the IDE and compiler ship together with no configuration), forks it with
  stdout+stderr piped back, and — if compilation succeeds — runs the result.
  The captured output is drawn in the output pane.
- **The child's output is appended, not overwritten.** The first version
  captured the compiler's message and then ran the binary into the same buffer,
  erasing it. `exec_capture` now appends at the current length.
- **A real bug of my own, found by testing.** `mov qword [rel run_out+4095], 0`
  was meant to NUL-terminate the capture buffer. It writes 8 bytes at offset
  4095, overrunning the 4096-byte buffer by seven and landing on `run_out_len`,
  zeroing the length — so the pane drew nothing and the capture looked broken.
  Fixed to a single byte. This is why the tests exist.
- **Verified with a mock compiler, no display.** `tools/test_x11_run.py` puts a
  stub `sutram_compiler` beside the GUI, types `likha`, presses Ctrl-R, and
  asserts the pane draws the stub's output. Protocol suite still 39/39, negatives
  6/6, build byte-reproducible. `sutram-gui` 12,728 -> 14,688 bytes.

## v93 — Linux GUI IDE, slice 4: it asks the server how to type

- **The editor now uses the server's own keyboard layout.** Slice 3 typed with
  a hardcoded US-QWERTY table. Slice 4 sends `GetKeyboardMapping` (opcode 101)
  for keycodes 8..126, reads the reply, and builds `kc_map[keycode] = ASCII`
  from keysym index 0. A non-US layout now types correctly.
- **The fallback is deliberate.** If the reply is not a Reply, or
  `keysyms_per_keycode` is zero, or the array is short, `km_ok` stays 0 and
  `handle_key` falls back to the US table — the editor still works on a server
  that refuses the request.
- **Proven by a server that lies.** The mock serves the standard map with one
  deliberate exception: keycode 43 (US `h`) is served as `Z`. The test then
  asserts the client draws `Z` and *not* `h` — which is only possible if it
  really used the server's mapping. A fallback assertion would not distinguish
  the two.
- **Negative tests, two protocol edges.** `tools/test_x11_negatives.py` runs a
  server that answers with a non-Reply and one with `per=0`; in both the client
  must fall back to `h` and invent nothing. 6 checks, all pass.
- **A test bug found and fixed, again in the test.** The first negative run hung
  for 60 s: the client hardcodes `/tmp/.X11-unix/X0`, but the test had bound a
  tempdir socket, so the client never connected and `accept()` blocked. Second
  bug: shutting the socket's write side to simulate a refusal also stopped the
  test sending the follow-up keypress. Both were mine, not the client's.
- Protocol: 39 checks (was 35), 0 failures. GUI builds reproducibly:
  `nasm -f elf64 ide/sutram_gui_linux.asm -o /tmp/g.o && ld -o sutram-gui /tmp/g.o`
  is byte-identical across runs. `sutram-gui` 12,272 -> 12,728 bytes.

## v92 — Merge: module export visibility (both assistants' work integrated)

- **Two AIs built the same feature and collided; resolving that was the round.**
  ChatGPT's R41 cycle detector was already merged. Muse's R41 patch
  (`Muse-to-Sarvam/2026-10-09-deliverable.patch`) could not apply: it was built
  on a base predating ChatGPT's R41, and its anchor at
  `src/sutram_compiler.asm:1746` expected `; Expand imports` where the merged
  source now has `call graph_preflight_v1`.
- **Rebased by fixing the one stale anchor.** Muse's R41 then assembled and
  passed 186/186, gate 12/12, packs 30/30, module oracle 18/18, R41 acceptance
  3/3. All five Muse R41 features verified working: `E_MODULE_CYCLE` with the
  full cycle path, public export, `E_MODULE_NOT_EXPORTED` (real private-symbol
  isolation), `E_MODULE_DUP_EXPORT`, `E_MODULE_V1_ALIAS`.
- **ChatGPT's R42 Stage 1 was reviewed, built, and rejected as a duplicate.**
  Their SHA-gated patcher applied to `cd7a2908...`, assembled, and passed
  181/181. But it only *declares* `niryat` visibility — on their own fixture 04
  a private symbol stays callable — while Muse's implementation *enforces* it.
  Two parallel visibility systems in one compiler is a defect, not a merge, so
  the more complete implementation was taken. ChatGPT's one unique diagnostic
  (`E_EXPORT_UNDEFINED` for undeclared exports) is carried to R43.
- **Kept ChatGPT's cycle detector.** Removing `graph_preflight_v1` changes the
  diagnostic on `164_r41_cycle_reject.sm` (Muse's alias rule fires first), so
  both pre-passes stay. Redundancy documented; R43 cleanup.
- **A source-shape test needed relaxing, not the source.** The module oracle's
  `test_optin_only_gate` asserted exact adjacency
  (`call graph_preflight_v1` then `; Expand imports`); the merge inserts the
  module pre-pass between them. Rewritten to assert ordering, the real contract.
- Suite 181 -> **186** (Muse's five R41 examples now pass, expectations
  recorded). Compiler source SHA `cd7a2908...` -> `6036dd1c...`.

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

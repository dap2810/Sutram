# R152-00 — v314. R151: Muse's reading was right. A slice of a `kosh` given to a declared foreign function compiled on v313: C read the slice's descriptor (it printed an address) and, as a count, crashed. Fixed at the foreign call, with the line and the gate. R150: `--analysis-steps=N` built to the contract, every case tested (40). The two limits now name themselves. Of the four first-run paths, Windows found one defect, the desktop collision, now fixed. R152: the list of what is left, and the direct answer - no, nothing makes a release wrong, with one condition. The reference had one wrong sentence, about this very door; it is corrected.

## Release line

```
gates: 78 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v314) - sampurna sutra
```

- **Commit:** the one carrying this file (SHA in my chat report). Base: `6b3b699` (v313 + ROUND-148 to 152).
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Installer:** `Sutram-Setup.sha256` = `a0e786e44d26780ef5f20f4103eaefdd7b33474762ebd41611499144cc4e03eb`, `PASS payload v314 = compiler v314`, self-test exit 0 under Wine, gate `R140 package` 7/0.
- **THE GUARD, v313 (`6b3b699`) → v314, 783 programs, compiled the ordinary way before and after, bytes compared:**
  - **Linux ELF: 587 identical, 195 refused identically, 0 DIFFER**, and 1 new: the FFI probe.
  - **Linux PE: the same.**
  - **The 195 refusals print v313's exact messages.**
  - **No existing program changes or is newly refused.** The runtime and `sutram-link.exe` are byte-unchanged.
  - **The Windows compiler (v314) under Wine:** = the Linux PE output for all 783 (587 identical, 196 refused by both - the 195 and the FFI probe, which without `--ffi` is refused as an unknown name), 0 differ.

**Not done:**
- **No native Windows run of v314.**
- **R148 to R150 are answered here, as far as v313 had not already answered them.** The labels, the staging folder and the fourteen shapes were in v313 (R147-00).

## R151 WS1 - the fifteenth shape: confirmed, then closed

**The probe.** These use `tests/r33/kinds.o`, the existing FFI test object: `k_sum(ptr p, i64 n)` sums `n` longs from `p`. They were built with `tools/sutram_build.py --ffi tests/r33/kinds.sffi --foreign tests/r33/kinds.o`.

| v313 | program | result |
|---|---|---|
| `k_sum(k, 2)` | a `kosh` by name, `ptr` | **15** - right: its elements |
| `k_sum(k[0:2], 2)` | **a slice, `ptr`** | **compiled; printed `139676486729762`** - C summed the slice's descriptor |
| `k_sum(xs, k[0:1])` | **a slice as the `i64` count** | **compiled; Segmentation fault, exit 139** |
| `k_sum(m[0:2], 2)` | a `mala` slice | refused, `E_VIBHAG_ANKA` |

**So Muse's reading was right on every count:** no door in `r33_gen_foreign_funcall`, the walk deferring, and `r129_check_call` taking `.unknown`. **The runtime effect Muse could not determine is a wrong value, or a crash.** The Windows compiler under Wine (v313) also compiled it, with an msabi sidecar.

**Closed** (`src/r32_ffi.inc`, `r33_gen_foreign_funcall`, the argument loop):
- each argument that is not a `kosh` by its own name goes through `r134_holds_kosh`, the same predicate as every other door;
- if it holds a `kosh` - a slice, a call or `?:` giving one, a name holding a slice - it is refused through `r126_fail_door`;
- the message: *"kosh-vibhagah 'k' bahya-prakriyayai (FFI) na preshyate - bahya: k_sum"*, `E_KOSH_VIBHAG`;
- **a `kosh` by name still passes its elements to `ptr`,** as R127 made it.

**Measured:**
- all three `kosh` forms above are refused on v314, Linux and the Windows compiler under Wine;
- gate `R33 FFI kinds` still passes, 29/0, so the legitimate kinds are unchanged.

**Gate:** the shape is `tests/r147/slices/15_ffi_argument.sm`, compiled with `--ffi … --object` in gate `R137` (91 checks), with both mutants. **On v313 it fails** (`evidence-r152/slice-gate-on-v313.txt`).

## R151 WS2 - the `mala` asymmetry: deliberate, and that is exactly the bug

**Deliberate:**
- At an argument position (`r10 = 1`), the walk refuses a `mala` slice there and then. **No door handles a `mala` slice.**
- It leaves a `kosh` value to the door that follows. **The doors exist to give a `kosh` its own message** (`E_KOSH_VIBHAG`, `E_KOSH_DVARA`). R140 made that choice when the walk was first written, so that door refusals kept their codes.

**The flaw:** the deferral is only safe if every argument position has a door. **The foreign call was the one that did not.** So yes: it explains why the FFI shape was never caught. Every other call path had a door to defer to.

**What would stop the next one:** an inventory of every construct that takes an argument, against the list of doors. **I have not made that audit.** It is in the list below.

## R151 WS3 - Muse's five, answered

1. **The synthesized `mandapa` blocks: verified by reading.**
   - They are `AST_BLOCK`s with a statement count: 3 for `{decl, body, rewind}` (the build at line 8383) and 2 for `{rewind, jump}` (line 8450).
   - `gen_block` sends each element through `gen_stmt` (`r45_gen_block_body`: `mov rax, [rbx + 16 + r13*8]` / `call gen_stmt`). So each is walked.
   - The rewind's `gen_expr` (`r65_arena.inc:410`) is reached inside a checked statement, on a compiler-made node: the mark.
2. **`r58_fold_tree`: verified - the whole function.**
   - It rewrites only `AST_BINOP` whose two children are `AST_NUM`, for integer and bitwise operators. Its own header says it "never descends into calls, float/string nodes or arbitrary AST forms".
   - It runs inside `r142_gen_expr_body`, after the walk, so the walk always sees the unfolded tree.
   - Its identity reductions (`x+0`, `x*1`) apply after the walk too. `keep(k[0:1] + 0)` and `k[0:1] * 1` are refused on v314, measured.
3. **`r65_root_globals`, `backpatch_calls`, `r56_patch_global_storage`: verified, and none calls `gen_expr`.**
   - `r65_root_globals` calls `r65_active` and `r65_ensure_globals`.
   - `backpatch_calls` calls `backpatch`, `r28_add_reloc` and messages.
   - `r56_patch_global_storage` calls `emit_u32`, which patches addresses.
   - **They emit no value of a program.**
4. **The budget arithmetic: verified.**
   - 3,145,728 / 72 = 43,690 nodes (rounded down), × 8 + 1 = **349,521**.
   - The walk's push loop is offsets 8 to 64: **eight fields**. Gate `R143` reads both sizes and the loop from the source and recomputes the bound on every run.
   - (The release default is now 200,000, below.)
5. **Could a release binary carry a mutant flag? Now checked, not assumed.** Gate `R137` builds the compiler plainly - `nasm` with no `-D` - and requires the committed `sutram_compiler`, `sutram.exe` and `win/sutram.exe` to equal it byte for byte.
   - A binary built with a mutant flag, or with a lowered budget, differs.
   - No build script defines either flag; only the gates' own test builds do.

## R151 WS4 - the three numbers, confirmed against v313's source

- **No `r157`.** The walk is `r137_check_stmt`, at line 28402 on v313. Its stack `r142_wstack` is at 1565, and `r142_push` at 28677. **Muse is right.**
- **146 `call gen_expr`:** 133 in `src/sutram_compiler.asm`, 13 in `r23_capabilities.inc` (4), `r25_phal.inc` (2), `r32_ffi.inc` (3) and `r65_arena.inc` (4). Plus one `jmp gen_expr` at 9035. **Muse is right** (147 entries in all, as R142-00 said).
- **The R137 gate: 89 checks on v313** run in its own mode (`evidence-r147/slice-gate-on-v313.txt`); 88 with `--compiler`, which skips the mutants. **Neither is 64 or 87.** It is 91 on v314.
- **Do the documents repeat them?** Reference, memory model, release notes, master and path document were searched: **no `r157`, no call-site count, and no R137 check count.** The changelog quotes counts per version, and each was right for its version.

## R150 WS1 - `--analysis-steps=N`, to the letter

**Built in `_start`** (`r152_scan_flag`). It runs before any other argument is looked at, on Linux and Windows. Each valid token is read and dropped.

**The contract:**
- one token: `--analysis-steps=` and ASCII digits;
- the range is checked as `acc > (2147483647 - digit) / 10` before `acc` is updated;
- zero is refused, and so is a second occurrence;
- the value starts every walk again: each statement, each initializer, each `gen_expr` fallback;
- the release default is 200,000.

**Every case was tested** (gate `R152 analysis steps`, 40 checks):

| case | result |
|---|---|
| `=00064`, `=200000`, `=2147483647` | **accepted**; the program compiles and runs |
| `=1` | **accepted**; then the compile is refused by a budget of 1, naming 1 |
| `=000001` | **accepted**, named as 1: displayed normalised |
| empty, `0`, `000`, `-1`, `+1`, `200k`, `1e5`, `0x100`, `1_000`, `1.5`, `1/2`, leading, embedded and trailing whitespace, a tab, Arabic-Indic, Devanagari and full-width digits, `5x`, `2147483648`, `4294967297`, a 20-digit value | **rejected**: exit 1, no output, `E_PARIKSHA_PADANI` |
| `--analysis-steps 200000` (separate value) | **rejected** |
| a second occurrence, same or different value | **rejected** |
| `--analysis-stepsX`, `--analysis-steps:5` | **rejected** |
| after the file arguments | **accepted, and in force** |
| with `--check`, `--lang`, `--ffi … --object` | **in force** |
| a module-level initializer | **counted with N** |
| the usage text | names the flag and the effective default, **200000** |

**The test build and the release binary:**
- `-DR143_WALK_BUDGET=64` still lowers the default, and an explicit flag overrides it (tested).
- The release binary is the plain build, gated (WS3 item 5 above).

**Determinism, measured:** the widest statement the tree holds is refused at `--analysis-steps=87315` and compiles at `87316`.

**One thing the contract asks that the compiler cannot give: the source line.**
- The check sees the statement after parsing, and the tree keeps no positions. Only `--debug` records them.
- So the message names the **prakriya** - or *"mukhya athava vaishvika-arambhah"* - not the line.
- Keeping a line in every node is a larger change. I did not make it. It is in the list.

## R150 WS2 - can a reader tell the two limits apart? Now yes

**Before v314:**
- The tree's message was *"vakya-vriksh seema atikram"* (the syntax-tree limit exceeded), with no code and no advice.
- The analysis message did not say it was not the tree's.
- **Your probe could not tell them apart, and the messages did not help.**

**v314:**
- **The analysis limit:** *"Sutram truti [E_VAKYA_SEEMA]: vakyasya parikshanam 87315 padeshu na samaptam (parikshana-seema) - prakriya 'f'"*. The hint: split the statement (keeping intermediates in names), or raise `--analysis-steps=<more>` (1 - 2147483647; default 200000). *"Iyam parikshana-seema; vakya-vriksha-seema prithak, tasyam --analysis-steps na sahayyam karoti"* - this is the analysis limit; the syntax tree's limit is separate, and the flag does not help with that one.
- **The syntax tree's limit:** the same first line (kept, so the translated packs still find it), then *"Sanket: karyakramasya vakya-vrikshah purnah (3 MiB) - iyam vakya-vriksha-seema, na parikshana-seema (E_VAKYA_SEEMA); --analysis-steps atra na sahayyam karoti"* and what to do. In English: the program's syntax tree is full; this is the tree's limit, not the analysis limit, and `--analysis-steps` does not help here.
- **Each message names itself and the other.** The remedies differ, and each says its own.
- **Not done:** the frozen language packs do not have the new hint lines, so they appear in Sanskrit in every pack.

## R150 WS3 - the four first-run paths

Windows ran all four on v312 natively (`Windows-to-Sarvam/win-firstrun-paths-2026-11-08/`). My reading of the code agrees with each result:

| path | Windows observed (v312) | the code | state |
|---|---|---|---|
| 1. Start-menu Terminal, PATH declined | **works** - prints the version; `where` finds the installed compiler | the shortcut runs `cmd /K "set "PATH=<bin>;%PATH%" && sutram --version"`: PATH is set for that window whatever was chosen | **works** |
| 2. a `.sm` with spaces, Devanagari, `&` or `%` in its path | **works** - all five | the command is `"<gui>" "%1"` | **works** |
| 3. a desktop `Sutram IDE.lnk` already there | **broken** - the user's link (to Notepad) kept, none made, so the only "Sutram IDE" opened Notepad; and the checkbox said "Sutram Terminal" | v314: the user's is kept and the installer's is **`Sutram IDE (Sutram).lnk`**, recorded in the state (`DesktopLink`); install and uninstall remove a link only when it points at this IDE; the checkbox says "Sutram IDE". Gate `R143 installer first contact` (15). | **fixed, NOT RUN natively** |
| 4. the documentation shortcut | **works** - the book is installed and the shortcut opens it | made only if `docs\sutram-book-english.html` exists; it is in the payload (657 entries), so a release always makes it. The absent case could only arise from a broken package, which the manifest check refuses first | **works** (absent case: untestable, and unreachable with a verified package) |

## R152 WS1 - what is left before v1.0, in order

| # | item | kind | size |
|---|---|---|---|
| 1 | **A native Windows run of v314:** install and uninstall, the 15 slice probes, the FFI refusal with the Windows FFI, `--analysis-steps`, the desktop collision and checkbox, the licence page | verification | 1 Windows round |
| 2 | **An inventory of every construct that takes an argument or stores a value, against the list of doors** - the FFI door was missing for this reason; nobody has listed them all | verification (a reading), maybe a defect | 1 round |
| 3 | **The compare-then-delete race** in the installer's superseded branch: keep a uniquely named copy instead of deleting | defect | small |
| 4 | **The uninstaller's five name-based deletes** of the installer's own record files: record their hashes and check them | defect | small |
| 5 | **A source line in check diagnostics** (`E_VAKYA_SEEMA` and the slice refusals at code generation): give nodes a position | defect (usability) | medium |
| 6 | **A new machine or user profile on Windows** - every native run so far is one existing account | verification | 1 Windows round |
| 7 | **The out-of-memory exit on Windows** - last measured on v309 | verification | part of 1 or 6 |
| 8 | **The suite time on Windows** - one sample, 24% slower on v312 than v311, not attributed | verification | part of 1 |
| 9 | **The Windows package builder** - `Compress-Archive` is not deterministic; the release is the Linux build, and says so | defect (minor) or document | small |
| 10 | **The packs' new Sanskrit-only lines** (the size-limit hints, the FFI door) - the packs are frozen | document (a known gap) | none, by the freeze |
| 11 | **The reference and release notes, one more read against the code** after these changes - this round found one wrong sentence (WS3 below) | document | small |
| 12 | **Rebuild the installer and re-run the gates** after any of the above | verification | each time |

## R152 WS2 - "do not ship this"?

**No.** Nothing in the code or the documents makes a release wrong rather than imperfect:
- **The documents claim no memory safety.** Raw `nirmmita` is unchecked, and `yantra` is outside the model, both said plainly.
- **Every slice escape found so far is refused,** and the claim is stated as the shapes found, not the class.
- **The installer's data-loss defects are fixed** and measured natively. The remaining race needs another program writing to the very file the installer is about to replace, between the installer's hash of it and its delete.

**One condition, not a defect: do not ship a package that has not been installed and run on Windows.** v314 has not been. Until item 1 is done, v314 is a candidate, not a release. A release built from code changed since the last native run would be wrong, not imperfect.

**And one risk to say out loud:** item 2. The FFI shape showed that the walk's deferral to the doors is only as safe as the list of doors. I believe the list is now complete. **That belief comes from the shapes tested, not from an inventory.**

## R152 WS3 - the reference, checked against the code

- **`r157`:** in no document.
- **A count of `call gen_expr` sites:** in no reference or memory document.
- **A count of R137 checks:** in no reference or memory document. The changelog's per-version counts were right for their versions.
- **"Closed" without its argument:** none found. The release notes say *"Not closed, and not claimed"* and list the shapes. The reference's one "closed" (line 1348) is about v291's two named ways around a `kosh` rule, and names them.
- **But one sentence was wrong, and it was about this very door.** The reference said, after "pass the slice on directly - `f(k[1:4])`": *"A foreign function's `ptr` parameter receives the elements' address too"*. **That was not what the compiler did.** v313 passed the slice's descriptor.
  - **Corrected:** a slice is not given to a foreign function (v314, `E_KOSH_VIBHAG`); v313 passed its descriptor; pass the `kosh` itself and the bounds as numbers. The page says the earlier wording was wrong.
  - The release notes' FFI line and the memory model's status box now say the same.

Evidence: `Claude-to-Sarvam/evidence-r152/`.

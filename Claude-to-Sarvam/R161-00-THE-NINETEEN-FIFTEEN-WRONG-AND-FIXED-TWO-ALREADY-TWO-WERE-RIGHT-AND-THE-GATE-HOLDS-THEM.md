# R161-00 — WS1: I checked each of the nineteen against the code before touching the page. Fifteen were wrong and are corrected; two were already fixed in R156; **two were right**, and the partners were wrong about them. For the two that were right, the evidence is in the tree. None needed the compiler changed, so the compiler is untouched. Gate `R158 doc currency` has a seventh check that holds all nineteen, and it fails on the tree before this commit. WS2 and WS3: recorded in `AGENTS.md`. WS4: one more defect fixed by reading, a read-only preflight script, and a run order. **The package for Tuesday is `67e079598963b8952855cf9ae7a55630872a143b70279959941e30e41db29d0b`.**

## Release line

```
gates: 79 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v315) - sampurna sutra      (compiler unchanged since 308c2161)
installer 67e079598963b8952855cf9ae7a55630872a143b70279959941e30e41db29d0b
```

- **Commit:** the one carrying this file (SHA in my chat report). Base: `1c6dfc5d`.
- **The guard: NOT re-run** - no compiler, runtime, library or pack byte changed.
- **The installer is rebuilt:** the uninstaller changed (WS4), and the reference and changelog are in the payload. Gate `R140 package` 7/0. **`a845e2e6…` and `a11703c2…` are both superseded.**

## WS1 - the nineteen

**Method:** for each, the code first, then the page. Muse's list (`Muse-to-Sarvam/ROUND-154-NINETEEN-LIST-SCRIPT-FOOTPRINT.md`) gives the line of each; ChatGPT's R222 repeats several. Where a claim can be measured, I measured it on v315.

| # | the page said | the code does (checked how) | done |
|---|---|---|---|
| 1 | every `kosh` has a region of its own | a descriptor; the elements move | **already fixed** in R156's status box |
| 2 | "Generated from the compiler source … so it cannot drift" | it is written by hand, and drifted | **corrected:** it says it can drift and that the compiler is right. The stale header line "Compiler: v29 · Package: v35" went with it |
| 3 | three-argument `likha` needs a string literal first | `likha(a, b, a)` prints `797` (run) | **corrected** - the page contradicted itself 30 lines later |
| 4 | at most two modules | `examples/99` brings in seven and compiles (run); the limit is 128 KiB of expanded source (`IMPORT_BUF_CAP`) and the tree | **corrected** |
| 5 | `s + k` → `E_VARTANI_CAT` | `E_KOSH_GANIT` (run): the `kosh` check comes first | **corrected** - its own row |
| 6 | `rikta kosh se kosh_pop` etc. | `Sutram truti: riktat koshat kosh_pop` / `_peek` / `_dequeue` (run) | **corrected** |
| 7 | the slice descriptor is "three words" | two: elements, length - 16 bytes of the frame (`r23_gen_slice`) | **corrected** |
| 8 | "as an `i64` count, crashed (confirmed)" | **true.** R152 ran it: segmentation fault, exit 139 (`evidence-r152/ffi-shape.txt`). Muse read R150, which predates the run | **kept, with the evidence cited** and the printed value |
| 9 | a `kosh` of 1,000 is 16 + 8,192; example block "8272" | 32-byte descriptor + 8,192 = 8,224; `examples/317` prints `8288` = 64 + 8,224 (run; = its golden) | **corrected** - block and sentence |
| 10 | parimita does not count a `kosh` "(it has its own region)" | the rule holds; the reason is wrong for a small `kosh`, which is in the arena | **corrected** reason |
| 11 | 400 MB "from v284 (each `kosh` now has its own region)" | true v284-v301 only; **v315 measured: 106,240 KB** (same program, `/usr/bin/time`) | **corrected**, with the v315 number |
| 12 | "the 344 examples" | 344 is `examples/*.sm` + `examples/*/*.sm`, the set the walk-budget gate compiles (331 top level, 347 at any depth) | **corrected:** says which set, and that it was measured at v312 |
| 13 | "R148's measured boundary" (16,385) | measured natively on Windows against the v312 baseline (`Windows-to-Sarvam/win-v313-2026-11-08/BUDGET.md`), relayed in your ROUND-148 | **corrected** attribution |
| 14 | status box at v300 | - | **already fixed** in R156 |
| 15 | the scratch-escape check covers `likh` | **true.** Muse and ChatGPT (R222) both read `r73_check_call`, which does not list `BN_LIKH`. **But `likh` is not a call:** it parses to `AST_WRITEMEM`, and `.pp_writemem` calls `r73_check_stored` (R74). `likh(outer, buf)` in a block is refused, `E_SCRATCH_ESCAPE … smritau na likhyate` (run) | **kept** - the gate now runs it |
| 16 | MM: "the push emission explicitly rejects growth on a kosh parameter" | allowed from v304; the refusal is dead code | **superseded note** on the historical sentence |
| 17 | MM: growth "updates the named variable's pointer"; "no reclamation" | updates the shared descriptor; an old region is `munmap`ped (`src/r65_arena.inc`) or `VirtualFree`d (`win/winrt_blob.asm`) | **superseded notes** |
| 18 | MM: aliases not established as updated | every name holds one descriptor (v302; R127 grew a `kosh` to 20,000,000 with two names agreeing - Muse's "R129" is R127) | **superseded note** |
| 19 | MM: "no `munmap` / free emission anywhere"; the leak test "expected to FAIL" | `munmap` is emitted | **superseded notes** |

**Totals:** 15 corrected (11 in the reference, 4 in the memory model), 2 already fixed, 2 true and kept.

**Code or page?** You asked me to prefer changing the code where a student relies on the behaviour. **In every case the code already does the better thing:**
- `likha` prints three values;
- any number of modules works;
- `s + k` is refused;
- the messages are clear;
- old regions are returned.

The page described something worse than the truth. So the page changed. Changing the messages to match the old page would change program output bytes, and the guard would rightly object.

**The memory model's body is an R70 snapshot**, labelled historical at its top. ChatGPT asked that historical passages be framed, not silently rewritten. **So each false sentence keeps its text and gains a "Superseded (R161): …" note** saying what the code does now.

**`R158 doc currency`, check 7, `reference`** (`tests/r158/test_doc_currency.py`):
- **For all nineteen:** the false text may not come back. A memory-model sentence may stay only with its "Superseded (R161)" note.
- **Where a claim can be measured, it is measured on every run:**
  - `likha(a, b, a)` must print `797`;
  - `s + k`'s code must be the one the page's row names;
  - each empty-`kosh` message must be quoted verbatim;
  - `examples/317`'s output must be the page's block;
  - the example count must be the tree's;
  - `r23_gen_slice` must still make 16 bytes;
  - `likh(outer, scratch)` in a block must be refused;
  - `munmap` must still be in `src/r65_arena.inc`;
  - the two cited evidence files must say what the page says.
- **A self-test** puts one old claim back and strips one "Superseded" note, and requires both to be caught.
- **On the tree before this commit** (`1c6dfc5d`): **15 old texts and 9 failed measurements** (`evidence-r158/gate-r161-on-1c6dfc5d.txt`).
- **On this commit:** 19 checks, 0 failed.

**What it still cannot do,** as Muse's R154 says of 12 of the 19: tell that a new sentence is false. These nineteen are pinned; the twentieth will need a reader.

## WS2 - the cleanup decision

**Recorded in `AGENTS.md`, in its first section** (*"Evidence stays, and so does the history (decided by Sarvam, R161)"*):
- cited evidence is not deleted - named by a report, made by a script, or covered by a wildcard;
- a byte-identical copy may go, with a manifest;
- do not reopen this without the owner.

**One correction to R159's evidence that ChatGPT caught:** `evidence-r159/removed-identical-copies.tsv`'s header named its columns in the wrong order. Fixed: the columns are removed path, bytes, SHA-256, the copy kept.

## WS3 - history

**The same `AGENTS.md` paragraph:**
- the repository is large because every claim is backed by evidence;
- rewriting history would shrink the clone - most of it is old binaries - but would change every commit SHA that hundreds of records and the guard's baselines cite, force every clone to be made again (the owner's Windows clone first), and need a forced push;
- *"We keep the evidence and accept the size."* For a small download at release, make a new repository from the release tree and keep this one as the archive.

## WS4 - is there anything I would not want tested cold?

**One thing I would not have wanted tested at all, and fixed by reading first - the uninstaller's retry (ChatGPT R221).**
- **The old order:** the uninstaller removed its Settings entry, the manifest, `install-state.ini` and `.sutram-install`, and only then tried, 100 times over 10 seconds, to delete itself.
- **If that ran out**, it said "close it and retry". A retry then found *"This folder is not marked as a valid Sutram installation"*, and there was no Settings entry to retry from. ChatGPT was right.
- **Now those four go only after the uninstaller has deleted itself.** Every step before is safe to repeat: it removes only what is still there and still matches its record. The message names Settings and the uninstaller's path.
- **Gate `R143 installer first contact`, 25 checks:** the new one fails on the old uninstaller.

**What should exist before the run - and now does:** `tests/windows/preflight_installer_state.ps1`. **It is read-only.**
1. **It parses `install-core.ps1` and `uninstall-core.ps1`** and fails on any syntax error. The engine's PowerShell changed in R154, R155, R155-01 and now. **None of it has run.** A syntax error would stop the install at its first line; this finds one without installing anything.
2. **It writes what the registry and PATH hold** to `build\installer-preflight\<label>.json`:
   - `.sm`, `Sutram.Source` and the Settings entry, each value with its kind, and every subkey;
   - PATH's exact text and kind, or that it is absent;
   - every `.lnk` in the Start-menu Sutram folder and on the desktop, with its SHA-256.

   **Run it before and after each case**, so "unchanged" is a comparison of two files, not a look.

**What I would not do cold:**
- **Run the `.sm` and PATH cases on the owner's own account.** They deliberately write `HKCU\Software\Classes\.sm` and the user PATH. **Use a separate Windows user account** - which also gives the new-profile run no earlier test has had - or at least `reg export` the three keys and `HKCU\Environment` first.
- **Reproduce the old defect to see it.** `a845e2e6` and anything older would delete an existing `.sm` key. If you want to see it, only on that separate account. The fix does not need it: case 1 below tests what matters.

**The order I would run:**
1. **`preflight_installer_state.ps1 -Label before`** - stop if it fails.
2. **`tests\windows\test_installer_shortcuts.ps1`** (R153). It writes only under `build\`.
3. **The `.sm` key case** (R155-00, Tuesday item 1). **This is also the first test of what Windows PowerShell 5.1 does with `New-Item -Force`.** I read that in open-source PowerShell; it has never been run.
4. **The empty-default, PATH-as-text, no-PATH and the two PATH-reinstall transitions** (R155-00 items 2-4, R155-01).
5. **The retry, deliberately:**
   - hold `Sutram-Uninstall.exe` open from another PowerShell, e.g. `[IO.File]::Open($p,'Open','Read','Read')`, so it cannot be deleted;
   - uninstall from Settings: expect the new message after about 10 s, and Sutram still in Settings;
   - close the handle and uninstall again: expect it to finish.
6. The rest of the v314/v315 list.

Each case ends with `preflight_installer_state.ps1 -Label after-<case>`.

**Not done:** no PowerShell or Windows here, so none of the above has run - the preflight script included.

Evidence: `Claude-to-Sarvam/evidence-r158/gate-r161*.txt`, `Claude-to-Sarvam/evidence-r161/`.

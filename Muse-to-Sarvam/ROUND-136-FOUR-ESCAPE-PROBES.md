# Sutram — ROUND-136: run ChatGPT's four escape probes

**Base:** main at v306 (`218fb84e`) · **Compiler:** v306, unchanged since R134
(`8edb8b90` → `218fb84e` is docs, briefs, and deliverables only — no `src/`
change) · **Deliver into:** `Muse-to-Sarvam/`

## Verdict up front

**All four of ChatGPT's escape probes reproduce. A stale read is what we
found — three times over, plus a silent stale write, a lost write, and a
crash.** And it is not four paths. Testing independently, I found **four more**
— a slice in a global, in a rachana field, in raw `nirmmita` memory, and
through a `dasham` parameter (which crashes instead of reading stale). The
cause is the one ChatGPT named: the rule is enforced in four separate places,
each with a hardcoded kind list, and none of them includes the slice's kind
(kind 1). Every untyped storage is an escape. **The slice class is not
closed, and the count is now eight escape shapes, not four.**

**Claude's reconstruction of the interrupted install is sound** — 131
matching payload files, five previous installation-state files, and an empty
`PROJECT-OVERVIEW.md` at position 132 — with two qualifications (below) and
one correction to the size question.

The gates still read 69 PASS / 0 FAIL / 1 NOT-RUN and the suite still reads
PASS=327. Neither closes this.

## WS1 — four probes, one per predicate

All run on the committed v306 binary. The question per probe was: does it
print the old value, the new value, or crash?

| # | Predicate | Probe | Result |
|---|-----------|-------|--------|
| 1 | cell store | `r136_ws1_cell_minimal.sm` (brief's form) | **Reproduces.** Compiled, exit 0, printed `140733170577648` — a stack address (`0x7ffd…`). The slice descriptor pointer persisted in the `mala` cell past the growth. The slice escaped into untyped storage. |
| 1 | cell store | `r136_ws1_cell_write.sm` (R207's form) | **Reproduces, silent stale write.** Compiled, exit 0, printed `7`. The raw write of 99 went to the abandoned buffer; `k[0]` stayed 7 — exactly ChatGPT's prediction. |
| 2 | untyped parameter | `r136_ws1_untyped_param.sm` | **Reproduces, lost write.** Compiled, exit 0, printed `77` then `7`. The callee grew the source, wrote 77 through the descriptor it received as an untyped parameter, and read its own write back (77) — but `k[0]` stayed 7. The write went to the abandoned buffer. |
| 3 | untyped return | `r136_ws1_untyped_return.sm` | **Reproduces, stale read — the worst outcome.** Compiled, exit 0, printed `7` then `99`. The slice came back through the untyped identity `keep(x)`, the source grew, `k[0]` was changed to 99 — and the program read the **old value 7** through the laundered slice while `k[0]` is 99. |
| 4 | function value | `r136_ws1_funcval_small.sm` (R135 verbatim) | **Reproduces.** Compiled, exit 0, printed `0` then `7` — the same silent stale write as R135, re-run on this base. |
| 4 | function value | `r136_ws1_funcval_large.sm` (R135 verbatim) | **Reproduces, crash.** Compiled, **exit 139 (SIGSEGV)**, no output — the region-release fault again. |

Notes on the four:

- **Probe 1 vs R135's shape 3.** In R135 a slice stored in a *kosh* cell
  refused at run time (exit 1, bounds message). A slice stored in a *mala*
  cell does not refuse at all — the cell-store branch
  (`r126_check_assign .cell`) rejects `r126_is_kosh_value` (kinds 2, 3, 6)
  and a slice is kind 1, and `r127_check_slice_value` is not applied by that
  branch. Same spelling, different cell kind, opposite outcome. The mala
  cell is the open one.
- **Probe 3 is sharper than R135's launder probe.** R135's version printed
  the descriptor's first word (a garbage address). This version
  double-dereferences through the returned value (`vitti addr = t[0]`,
  `likha(addr[0])`) and reads the **element** — the old value, after the
  source grew and changed. That is the stale read the brief asked for.
- **Probe 2 vs probe 3.** Probe 2 erases the slice at the parameter (the
  callee receives the descriptor pointer as an untyped `x` and grows the
  source itself). Probe 3 erases it at the return (the identity function
  hands the descriptor pointer back as an untyped result). Both need no
  indirect call — R207's point that the parameter/result path erases kind
  "without an indirect call" is confirmed.

## WS2 — and if any of them reproduce

**They did. All four. So I tested independently for a fifth path — and found
four more.** The cause is the four predicates, not a fifth mechanism: one
shared policy gap (kind 1 is never in any refusal list) with every untyped
storage as an instance of it.

| # | Independent probe | Result |
|---|-------------------|--------|
| 5 | **global** — `r136_ws2_global.sm`: slice assigned to a global `vitti g`, source grown, `k[0]` changed to 99, read back through `g` | **Reproduces, stale read.** Compiled, exit 0, printed `7` then `99`. A slice stored in a global escapes; the stale read returns 7 while `k[0]` is 99. The R131 store refusal does not cover a global target. |
| 6 | **rachana field** — `r136_ws2_field.sm`: slice stored in a field (`b.s = k[0:1]`), same growth + change + read-back | **Reproduces, stale read.** Compiled, exit 0, printed `7` then `99`. A slice stored in a field escapes. |
| 7 | **raw memory** — `r136_ws2_rawmem.sm`: slice stored in a `nirmmita` buffer cell (`p[0] = k[0:1]`), same growth + change + read-back | **Reproduces, stale read.** Compiled, exit 0, printed `7` then `99`. Raw memory has no checks at all; the descriptor pointer persists and reads stale. |
| 8 | **`dasham` parameter** — `r136_ws2_dasham_param.sm`: slice passed to a `dasham` parameter, callee grows the source, indexes through it | **Reproduces, crash.** Compiled, **exit 139 (SIGSEGV)**, no output. The boundary does not refuse — and the result is a crash, not a clean refusal. |
| — | **ternary** — `r136_ws2_ternary.sm`: `vitti s = 1 ? k[0:1] : k[0:1]` | **Closed.** Compile-refused `E_KOSH_DVARA` ("`?:` kadachit kosh dadati kadachit na…"). The ternary's kind is 6, which `r126_is_kosh_value` recognizes — closed by accident of the kind numbering. |
| — | **conditional assignment** — `r136_ws2_cond_assign.sm`: `s = k[0:1]` inside a `yadi` block | **Closed.** Compile-refused `E_KOSH_VIBHAG`. The assignment check applies inside a block, not only at declarations — as ChatGPT said, `r127_check_slice_value` covers named declarations *and* assignments. |

The dasham crash, pinned (`r136_ws2_dasham_diag.sm`): a callee that only
prints its `dasham` parameter prints `140724879295072.000000` — the
descriptor pointer's **value** as a float. So the slice arrives at a `dasham`
parameter with its value preserved (int→float conversion, exact at this
magnitude) but its **bit pattern destroyed** (the double encoding of 1.4e14
is `0x4270…`, not the pointer `0x7ffd…`). Indexing through it then reads an
unmapped address and faults. The dasham boundary neither refuses the slice
nor preserves the pointer. (The diagnostic also leaks the address as a float
— an ASLR disclosure through a different channel.)

**The count.** Eight escape shapes reproduce on v306: mala cell (write and
read forms), untyped parameter, untyped return, function value (write and
crash forms), global, rachana field, raw `nirmmita` memory, `dasham`
parameter (crash). Two more shapes are closed (ternary, conditional
assignment) — both by existing kind checks that happen to catch them, not by
a slice policy. The fix ChatGPT names — **one predicate for the slice class**:
mark kosh-derived slices and reject erasure into cells, fields, globals,
untyped parameters/results, and unresolved calls, preserving provenance
through aliases, subslices, and forwarded `vibhag` parameters — covers all
eight. A fix that closes only the four named predicates leaves the other
four open. (Considered and not probed separately: a subslice of a `vibhag`
parameter — it is marked as a slice var, and returning it refuses; escaping
it would need one of the same untyped/indirect boundaries above, so it adds
no new hole. Forwarding a `vibhag` parameter to a direct call is checked by
`r129_check_call` as before.)

**No regressions.** Suite on the `218fb84e` binary: **PASS=327,
NO-EXPECTATION=4 (331 run)** — identical to R134/R135. The direct-call
controls still refuse `E_KOSH_VIBHAG` (R135 small-direct, growfn-direct),
and direct slice use still works (`ws2_slice_immediate.sm`: `120|3|120|3`).

## WS3 — and the reconstruction

**Claude's reconstruction is sound** — 131 matching payload files, five
previous installation-state files, and an empty `docs/rounds/PROJECT-OVERVIEW.md`
at position 132 — with two qualifications and one correction to the size
question. I checked it against the snapshot
(`Windows-to-Sarvam/win-installer-diag-2026-11-06/before.json`, 137 files)
and the v303/v305 payload manifests extracted from the committed
`Sutram-Setup.exe` binaries.

1. **"131 matching payload files" — CONFIRMED.** All 131 complete installed
   files match the **v303** manifest by SHA-256: **131 of 131, zero
   exceptions.** Qualification: "matching" means matching the v303 payload
   — the payload the copy was installing. Against the v305 package the same
   files read 122 match / 9 differ (plus the empty file as the 10th); the 9
   differs are exactly the 9 files whose hashes changed between the v303
   and v305 manifests (`bin\sutram.exe`, `BUILDING.md`, `CHANGELOG.md`,
   `LANGUAGE-REFERENCE.md`, `MEMORY-MODEL.md`, `PATH-TO-COMPLETION.md`,
   `RELEASE-NOTES.md`, `NEGATIVE-CORPUS.md`, `CHANGELOG-ARCHIVE.md`). The
   other two v303↔v305 differences (`examples\121_t18_kosh_param_push_reject.sm`,
   `win\sutram.exe`) are not in the installed set — never reached.
2. **"Five previous installation-state files" — CONFIRMED.** All five
   non-payload files carry Nov 3 timestamps, predating the Nov 6 18:35
   attempt: `.sutram-install` 20:54:37, `install-state.ini` 20:54:38,
   `install.log` 20:54:38, `payload.manifest.sha256` 20:51:36,
   `Sutram-Uninstall.exe` 20:51:45. The on-disk manifest is the old
   643-entry one (per `left-behind.md`), not the v303 656-entry one —
   consistent with the copy never reaching it. The empty file is the only
   Nov 6 file in the snapshot (18:35:34).
3. **"Empty `PROJECT-OVERVIEW.md` at position 132" — CONFIRMED as a count,
   qualified as a position.** The arithmetic is exact: 131 complete + 1
   empty + 5 state = 137. "Position 132" means it was the 132nd file **in
   copy order** — established by counting (131 files completed before it),
   not by manifest order (it is manifest index 104; the copy order is
   filesystem enumeration order, which cannot be reproduced exactly from
   here). And exactly one file was interrupted: all 131 complete files match
   the v303 manifest **by hash**, so none of them is a partial write — the
   empty file is the only interrupted one.
4. **"Large enough that a partial write would leave it empty" — the framing
   is backwards; the size is consistent, for the opposite reason.**
   `PROJECT-OVERVIEW.md` is **7,633 bytes, 177 lines**. The v303 copy path
   (`Copy-Item` → `[IO.File]::Copy`) writes through a buffered stream whose
   default buffer is 80 KiB — larger than the whole file. Such a file is
   written in a single buffered write flushed at close, so a stall anywhere
   between create and close leaves exactly **0 bytes** — the observed
   signature. A file *larger* than the buffer would more likely be left
   **partial** (nonzero bytes) instead. So the file is *small* enough to be
   left empty, not large enough — and its size does not explain the stall
   (a 7.6 KB file copies in under a millisecond; the stall is an external
   hang). The size explains only the empty-vs-partial signature, and it
   explains it exactly.

What the reconstruction cannot establish (and does not claim to): the copy
order itself, and the hang's cause. Both remain unknown — as R135 also found.

## The five release conditions — where they stand

1. **Slice closure — NOT MET.** Eight escape shapes reproduce on v306; the
   hazardous cases are not yet compile-time refusals. (Safe direct read/write
   controls still hold.)
2. **Windows setup and OOM — NOT MET.** The handler-registration gap (W1)
   is read-verified (R135) and not run; the native cases must run against
   the actual replacement binaries.
3. **Recoverable interrupted installation — NOT BUILT.** The design exists
   (R207 WS3: transaction journal, created and durably published before
   anything is deleted or truncated, in a private directory beside the
   target on the same volume; log `START <path>` before copying; never
   stream directly into an existing destination). No implementation has
   landed.
4. **Exact candidate acceptance — NOT YET.** No replacement candidate exists
   to build, package, and verify.
5. **Truthful release description — PARTLY.** The hang history is now
   correct in R135/R136 (stall and refusal are separate events; the file is
   identified; the cause is unknown), but the release notes still need the
   R205–206 corrections applied.

The unexplained historical hang need not block release on its own (R207) —
but the slice class, as measured here, does.

## Files delivered

- `Muse-to-Sarvam/ROUND-136-FOUR-ESCAPE-PROBES.md` — this report.
- `Muse-to-Sarvam/r136.json` — the structured results.
- `Muse-to-Sarvam/r136_ws1_*.sm`, `Muse-to-Sarvam/r136_ws2_*.sm` — 13
  probes (WS1 four, WS2 six, plus the dasham diagnostic).

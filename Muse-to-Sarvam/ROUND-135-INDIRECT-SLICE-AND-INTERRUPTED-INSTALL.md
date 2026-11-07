# Sutram — ROUND-135: the interrupted install, and the function-value slice

**Base:** main at v306 (`5bd58aee`) · **Compiler:** v306, unchanged since R134
(`8edb8b90` → `5bd58aee` is docs, briefs, and R134 deliverables only — no `src/`
change) · **Deliver into:** `Muse-to-Sarvam/`

## Verdict up front

**ChatGPT's S3 reproduces — both candidates, exactly as predicted.** The slice
rule is fixed for a direct call and still reachable one indirection further out,
and I found a second laundering path of the same class. **The slice class is
not closed.**

**The interrupted install's file is identified — and it is not the manifest's
132nd line.** The copy stopped on `docs\rounds\PROJECT-OVERVIEW.md`, a small
ordinary file. Nothing about it explains the stall. **The hang's cause is still
unexplained.**

**The installer trap persists in v306.** The ownership guard is byte-identical
to v305; an interrupted install still traps the next run behind a "user file"
refusal, with no repair path.

ChatGPT's NO on v306 stands, and is now stronger. The gates still read
69 PASS / 0 FAIL / 1 NOT-RUN and the suite still reads PASS=327 — neither
closes S3.

## WS1 — reproduce ChatGPT's function-value slice

Method: read the check first (`r129_check_call`, `r126_check_untyped_arg`,
`r126_value_kind`, `r23_check_return`, the two call emitters), then ran the
probes on the committed v306 binary. ChatGPT's trace is confirmed at the
source, line for line:

1. `r129_check_call` (`src/sutram_compiler.asm:28301`) calls
   `r23_call_is_indirect` and leaves immediately on a nonzero result. It does
   not inspect any argument on that path. An unknown callee (`rfx3_fn_index`
   returns -1) also leaves.
2. `func_param_type` (26851) looks up the syntactic callee name. For a local
   function variable no definition has that name, so it returns 0, the
   scalar/default path.
3. `gen_typed_call_arg` (27158 onward) calls `r126_check_untyped_arg` (28699).
   That check rejects kosh kinds 2, 3, 6 — but a slice is kind 1
   (`r126_value_kind`, 27772: `AST_SLICE` → 1). An explicit `k[0:1]` is not
   rejected there.
4. A slice is not a `dasham`; scalar conversion is a no-op. `r23_gen_slice`
   emits the same two-word descriptor (current raw element address and
   length), and the indirect callee receives its pointer intact.
5. `.ge_funcall` (expression calls) evaluates arguments **left to right**; its
   second argument can therefore move the `kosh` after the first argument
   captured the address. `r23_emit_indirect_call` then calls the function
   value; the callee's `vibhag` indexing uses the captured address.

### Shape 1 — a slice passed to a `prakriya` called through a variable

**Small candidate (ChatGPT's, verbatim) — REPRODUCED, silent stale write.**

`r135_ws1_small_indirect.sm` — compiled, exit 0, printed:

```
0
7
```

exactly as ChatGPT predicted. The callee wrote 99 into the abandoned buffer;
`k[0]` stayed 7. The write was silently lost, exit 0, no message.

Controls, all on v306:

- Direct call (`r135_ws1_small_direct.sm`, `badal(k[0:1], kosh_kship(k, 8))`)
  — compile-refused `E_KOSH_VIBHAG`, as in R131.
- No-growth positive control (`r135_ws1_small_indirect_nogrow.sm`,
  `f(k[0:1], 0)`) — compiled, printed `0` then `99`. Without growth the
  write lands. The defect is the growth plus the relocation, not the indirect
  call as such.
- **Statement form (`r135_ws1_small_indirect_stmt.sm`) — does NOT reproduce.**
  It printed `99`: the write landed. The reason is in the code, not in a
  check: `.gs_funcall` (statement calls) evaluates arguments in **REVERSE**
  order ("Evaluate args in REVERSE order"), so the growth runs before the
  slice is captured and the slice is made from the new buffer. `.ge_funcall`
  (expression calls) evaluates left to right. The statement form is safe by
  evaluation order, not by a check — if that order ever changed, it would
  break too. ChatGPT's note was right: the statement form must not be
  mistaken for a fix.

**Large candidate (ChatGPT's, verbatim) — REPRODUCED, use-after-release.**

`r135_ws1_large_indirect.sm` — compiled, then **exit 139 (SIGSEGV), no
output**. The slice captured the full 64 MiB region; the next push moved it
and released it; the callee read the released address. The direct version
(`r135_ws1_large_direct.sm`) compile-refuses `E_KOSH_VIBHAG`.

### Shape 2 — a slice returned from a `prakriya` and stored, then the source grown

The documented paths are closed; a third path is open.

- Direct return (`r135_ws1_return_direct.sm`, `nivartanam k[0:1]`) —
  compile-refused, `Sutram truti: vibhag prakriyayah na pratyarpaniyah`, as
  the reference (§17) documents.
- Pass-through of a `vibhag` parameter (`r135_ws1_return_passthru.sm`,
  `nivartanam s`) — compile-refused with the same message. The parameter
  marking works: a `vibhag` parameter is marked as a slice var
  (`src/sutram_compiler.asm:18488-18491`), and `r23_check_return`
  (`src/r23_capabilities.inc:510`) refuses any slice expression or slice
  variable on return.
- **Laundering through an untyped parameter — REPRODUCED.**
  `r135_ws1_return_launder.sm`:

  ```
  prakriya launder(x) {
      nivartanam x
  }
  mukhya() {
      kosh k[4]
      kosh_kship(k, 10)
      kosh_kship(k, 20)
      vitti obstacle = nirmmita(16)
      vitti t = launder(k[0:1])
      kosh_kship(k, 30)
      kosh_kship(k, 40)
      kosh_kship(k, 50)
      k[0] = 99
      likha(t[0])
      likha(k[0])
  }
  ```

  Compiled, exit 0, printed `131351504224288` then `99`. The first number is
  not an element — it is a pointer read as data.

  The diagnostic probe (`r135_ws1_return_launder_diag.sm`) pins what `t` is:

  ```
  t     = 140728493615824  (0x7ffde7df2ad0)
  t[0]  = 139932844687392  (0x7f44a7800020)
  t[1]  = 1
  k[0]  = 10
  ```

  `t` is a **stack address** (`0x7ffd…`) — the slice descriptor itself, living
  in the caller's frame. `t[0]` is the **element address** (`0x7f44…`, the
  arena). `t[1]` is the length, 1. So a slice value is a pointer to a
  two-word descriptor in the maker's frame; passed to an untyped parameter
  (one qword ABI) the raw descriptor pointer goes through unchanged, is
  returned, and lands in a `vitti` — from which it can be indexed as raw
  memory. The earlier run's garbage number (`131351504224288` =
  `0x7776a7c00020`) is the same thing under ASLR: the element address printed
  as an integer.

  Why the return check misses it: `r23_check_return` refuses a slice
  expression or a *marked* slice variable. An untyped parameter is never
  marked, so `nivartanam x` passes; and `r126_ret_kind` reports the callee's
  return as kind 5 (a number), so `vitti t = launder(...)` passes too. This
  is a second live defect of the same class — provenance erased at an
  untyped boundary — and it also leaks a frame address.

### Shape 3 — a slice held in a `kosh` and read after growth

**Closed in behavior, misleading in message.**

`r135_ws1_slice_in_kosh.sm` (store `outer[0] = k[0:1]`, grow, write `k[0] =
99`, read back via `vitti s = outer[0]`, `likha(s[0])`) — compiled, but the
program **refuses at run time, exit 1: `Sutram truti: mala ank seema
atikram`**. The same refusal fires in all three variants I ran to isolate
it: store-only (`r135_ws1_slice_in_kosh_storeonly.sm`, nothing after the
store but `likha(1)`), read-back (`r135_ws1_slice_in_kosh_readback.sm`),
and read-without-growth (`r135_ws1_slice_in_kosh_read_nogrow.sm`). The
store itself is what refuses — no slice is ever persisted, no stale value is
ever read, no crash. Safe, and loud.

But the message is wrong for what is happening: this is a type error (a
two-word slice into a one-word cell), not an index out of bounds. A student
seeing "mala ank seema atikram" would look for a bad index that does not
exist. Cosmetic, but the diagnostic is misleading.

For contrast, the direct store (`r135_ws1_slice_store_direct.sm`, `vitti s =
k[1:3]`) still compile-refuses `E_KOSH_VIBHAG`, as in R131.

### Shape 4 — a slice passed to a `prakriya` that grows the source in a different argument

**First design closed by a different door; redesigned design reproduces.**

My first version (`r135_ws1_growfn_indirect.sm`, `f(k[2:5], k)` — the kosh
itself as the second argument through a function value) **compile-refuses**,
but not on the slice: `E_KOSH_DVARA`, "kosh 'k' asankhyita-tarke na
preshyate - prakriya: f" — the whole-kosh door from R126. Passing a kosh
through a function value is already refused; the slice was never the thing
that stopped it.

So the growing argument has to be a *call*, not a kosh: `r135_ws1_growfn_indirect2.sm`
(`f(k[2:5], grow_it(k))`, where `grow_it` grows `k` and returns 1) —
**compiled, exit 0, printed `77` then `30`. REPRODUCED.** The callee's
write of 77 went to the abandoned buffer (its own `s[0]` read returns 77
from the old buffer); `k[2]` stayed 30 — the write was lost. The direct
control (`ws2_s1_call2.sm` from R131, `use_slice(k[2:5], grow_it(k))`,
re-run on v306) compile-refuses `E_KOSH_VIBHAG`, as before. (Note: R131's
`ws2_s1_call.sm` uses a `vitti` second parameter, which is a parse error —
`vitti` is not a valid parameter type. The `dasham` variant is the real
control; it refuses.)

### What closes it (for Claude, not built here)

The check has to protect slice provenance **before** relying on the target's
formal parameter kind, at every boundary where the target is unknown or the
value is untyped:

1. **Indirect calls:** refuse a kosh-derived slice as an argument to a call
   through a function value (the conservative v1 fix ChatGPT names), or
   run the same `r129_check_call` analysis against the value's possible
   targets. The current early exit in `r129_check_call` on
   `r23_call_is_indirect` is the hole.
2. **Untyped parameters:** a slice descriptor pointer must not pass through
   a one-word untyped parameter as a raw value. Either refuse a slice at an
   untyped parameter, or mark it so the return check (`r23_check_return`)
   and the call-result kind (`r126_ret_kind`) see it as a slice, not a
   number.
3. Keep safe direct slice writes working (the no-growth controls prove they
   work), and keep both the silent-write control (small) and the
   region-release control (large) as the acceptance pair — a fix that only
   stops the crash still leaves the silent stale write.
4. Do not rely on the statement form's reverse evaluation order. It is
   load-bearing today and is not a check.

### No regressions

- Suite on the 5bd58aee binary: **PASS=327, NO-EXPECTATION=4 (331 run)** —
  identical to R134.
- R129's 11 probes re-run: all hold (20M two-name agreement bad=0;
  20,000-kosh grow variant prints `0|10000|19999|999|1003`; cliff gone,
  `99|88|88`; parameter growth `11|55`). `ws1_paramindex` still refuses at
  run time with the bounds message — that probe deliberately indexes
  `k[100]`; the refusal is the expected safe behavior. `ws2_20k_maps`
  prints `ready` and then blocks on `grahan()` by design (it waits for the
  harness to read `/proc/PID/maps`); the timeout here is the missing
  harness, not a regression. `ws1_20k_grow` still refuses `E_VITTI_PRAKAR`
  (the v301 refusal — the working variant is `ws1_20k_grow2`).
- R131 slice probes re-run: immediate use `120|3|120|3`; S2 `149|4`;
  `may_grow` direct refuses `E_KOSH_VIBHAG`; slice-store refuses;
  parameter growth `11|22|99|3`. All identical.
- R127/R128 probes re-run: all 8 defects still refuse (compile or run
  time); the non-defect controls behave as designed; the 4.2M cliff probe
  prints `99|99` — both names agree.

## WS2 — and the interrupted install

**How does it decide a file is a "user file" rather than its own?**

The decision is the **inline upgrade-safety block in
`windows/native-installer/install-core.ps1`, lines 385–403 in v306** — it is
not a named function. (`Verify-Payload`, line 256, checks the *new* payload
against its own manifest; `Remove-ManifestFiles`, line 212, removes the
*old* payload's files; the user-file decision itself is the inline `foreach`
in the main install flow.)

The condition, exactly:

> For each file in the **new** staged payload (every file under `$stage`,
> except `payload.manifest.sha256` itself): if a file with the same relative
> path already exists in `$InstallDir`, it is "ours" — safe to overwrite —
> **only if** (a) its relative path is a key in `$previousFiles`, the **old**
> installed `payload.manifest.sha256` parsed as `<sha256> *<relpath>` lines,
> **and** (b) the installed file's current SHA-256 equals the hash recorded
> for that path in the old manifest. If either fails, it throws on the first
> such file: `Upgrade would overwrite a user file; preserve it elsewhere
> first: <target>`.

So the answer to the brief's question is **no — not "anything already
present"**. A file is a "user file" iff it is present **and** (not in the old
manifest **or** its hash differs). The trap is that a product file fails both
ways:

- (a) **Not in the old manifest** — a file the new payload adds, or any file
  when the on-disk manifest is from an older payload (here the on-disk
  manifest has 643 entries, from the Nov 3 install — not the v303 656, not
  the v305/v306 657).
- (b) **Hash differs because the payload changed** — the measured case:
  installed `sutram-link.exe` hashes `b6c722e9…`, which matches the *new*
  package, but the old manifest expects `84d653fb…`. The guard reads "hash
  differs from the old manifest" as "user-modified", but a product file can
  differ from the old manifest because the payload changed. The guard cannot
  distinguish user-modified from payload-changed, and the installer offers
  no repair or reconcile path — only manual removal of the file.

Two further precisions from the source:

- The check only examines files that are in the **new** payload (it iterates
  the staged files). A file on disk that is not in the new payload is never
  examined here; `Remove-ManifestFiles` removes it only if it is in the
  *old* manifest, otherwise it is left alone.
- It throws at the **first** mismatch, naming one file. The enumeration
  order is `Get-ChildItem` filesystem order, so which file is named can
  vary; the error never lists all mismatches.

**Where the ownership record lives, and when it is written:**

- `$InstallDir\payload.manifest.sha256` — the installed manifest. It is
  copied as one of the payload files (its position in copy order is
  filesystem enumeration order, not first or last). An interrupted copy may
  leave the *old* manifest in place — as it did here, which is why the next
  run compares new files against an old manifest.
- `$InstallDir\.sutram-install` — the marker, written after the copy.
- `$InstallDir\install-state.ini` — written at step 12; holds
  `UninstallerSHA256` and `PathOwned`. The earlier check (lines 356–367)
  refuses with "Existing installation ownership metadata is incomplete" if
  the marker exists but the manifest is missing or `UninstallerSHA256` is
  absent from state.
- The *new* payload's manifest is generated at **build** time by
  `windows/native-installer/build-installer.ps1`
  (`Get-ChildItem -LiteralPath $stage -File -Recurse | Sort-Object
  FullName`) and embedded in the wizard's `payload.zip`.

**Unchanged in v306.** The guard block is byte-identical to v305 — the
v305→v306 diff adds only `Copy-StagedFiles` and the progress/confirm
preferences. The interrupted-install trap is still live in v306.

**The v306 log point (the brief's second clause) is correct.** The R130
hand-back said "the last log line names the file" if the copy stops again.
What `Copy-StagedFiles` actually logs is every 100 files:
`Copied <n> of <total> files; last: <rel>`. A stall at the copy's 132nd
file leaves the last log line naming file **100**, not 132. The log narrows
a stall to a 100-file window; it does not name the exact file. The
ownership refusal, by contrast, does name its file (the throw message
carries the full target path) — but that is a refusal, not a stall.

**W1 — handler registration (read-only verification, not a WS).** ChatGPT's
second failure-path gap is confirmed at the source: `rt_init`
(`win/winrt_blob.asm`) calls `AddVectoredExceptionHandler` and never tests
the return value in `rax` — it restores the frame and returns immediately.
If registration returns NULL, the program continues with reserve-only
allocations and no handler to commit a first touched page; that first touch
can still terminate with an access violation and no new diagnostic. Windows
only; **NOT RUN** here.

## WS3 — and the file the copy stopped on

**The file is `docs\rounds\PROJECT-OVERVIEW.md`. It is not the manifest's
132nd line — and the manifest cannot identify it.**

The evidence is the partial-install snapshot
(`Windows-to-Sarvam/win-installer-diag-2026-11-06/before.json`, 137 files):

- Exactly **one** file in the snapshot is 0 bytes, with the empty-file SHA
  (`e3b0c44…`): `docs\rounds\PROJECT-OVERVIEW.md`, modified
  **2026-11-06T18:35:34** — the install attempt's time. A copy that stalls
  mid-file leaves the destination created but unwritten — exactly this
  signature. The other 131 payload files are complete.
- "File 132" is the **count**, not a manifest index: 131 files complete + 1
  empty = 132 payload files present. The copy was writing its 132nd file
  when it stalled.

Why the manifest reading is wrong: the 132nd line of the v303 manifest is
`docs\rounds\R72-BASELINE-OBSERVED.md` (2,618 bytes, 25 lines) — but that
file is **absent** from the partial install; it was never reached. The
installed set is not a manifest-order prefix: manifest indices 1–104 are
present, 105–134 are missing (30 files, `docs\rounds\R34-…` through
`docs\rounds\TEST-ME.md`), and 135–167 are present. The copy did not
proceed in manifest order — `Copy-Item -Recurse` enumerates the extracted
stage in filesystem order, which differs from the manifest's sorted order.
(My depth-first alphabetical simulation reproduces manifest order exactly,
and the installed set differs from it, so the copy order was neither
manifest order nor alphabetical depth-first.) The 132nd line of the
v305/v306 manifest is a *third* file (`R71-SPECIFICATION-EVIDENCE.md`) —
another sign the manifest index is not the answer. (Side note on the count:
the brief says "of 657" — the v303 manifest has 656 entries, 657 ZIP
entries including the manifest itself; 657 is the v305/v306 manifest count.)

**The file itself:**

- `docs\rounds\PROJECT-OVERVIEW.md` — **7,633 bytes, 177 lines** in the
  payload (3,580 compressed in the ZIP); manifest index 104 in v303.
- Content: the project overview ("Read this first" — what the project is,
  what is fixed, what exists, what is proven, what is not).
- Nothing unusual: ASCII name, ordinary `.md`, mid-range size (neighbors in
  that region run 2,505–9,942 bytes; the payload's largest file is 705,487
  bytes). It contains Devanagari in the title (सूत्रम्), as many files do,
  and one code block. It is not the first file of a new directory in manifest
  order (it sits inside `docs\rounds\`, preceded by five other rounds files
  and followed by thirty more).

So the file gives **no** explanation for the stall — which rules out
"large file", "unusual name", and "first file of a new directory" as causes.
The hang's cause is still unexplained, as Claude said. What the file does
establish is *where* in the copy it happened (a small ordinary docs file,
131 files in) and that the copy order is filesystem enumeration order, not
manifest order — so any future per-file logging must log the actual file
being copied, and 100-file granularity would not have named this one.

The sequence, reconstructed from `before.json`, `left-behind.md`, and
`HANG.md`: Nov 3, an older install completed (643-entry manifest, marker,
state, and log written 20:51–20:54). Nov 6 18:35, the v303 installer ran as
an upgrade, removed the old payload files, started copying, and stalled
writing `PROJECT-OVERVIEW.md`. The diagnostic attempts (20:39, 20:42)
refused at the ownership check and copied nothing. The repair preserved the
137 files and completed with the unchanged v305 installer into an empty
folder.

## What remains

- **Slice class: not closed.** S3 reproduces in two forms (silent stale
  write; region-release segfault), and the untyped-parameter laundering path
  is a second live defect of the same class. The fix belongs to Claude; the
  acceptance pair is the small control (no silent write) plus the large
  control (no crash), with the direct-call refusals and the no-growth
  positive controls still holding.
- **Installer trap: live in v306.** The guard is unchanged; the only escape
  from an interrupted install is manual. The ownership-guard
  product-vs-user-file distinction (and partial-upgrade recovery) is still
  the owner's/Claude's decision.
- **Hang cause: still unexplained.** The file it stopped on is identified
  and unremarkable. A clean-state reproduction (disposable standard-user
  Windows environment) is still needed.
- **Windows execution of v306: still NOT RUN by anyone** (the OOM fix was
  natively verified only on a source-built v305 candidate). The v306 Windows
  round remains the owner's.
- **Still open in v306 (unchanged):** dead `msg_kosh_param_push` (line 680);
  block-kosh parimana 96 vs 64; DisplayVersion `0.1.0`; the wizard's 90%
  display order; the string+ PE check skip (latent, allocation-time only —
  see R134 N2); the handler-registration gap (W1 above, read-verified).
- **Correction to the R134 record:** R134 said the v303 stall's cause was
  "still not established" and the ownership refusal was "the wreckage, not
  the cause" — both stand. What R134 did not establish is *which* file the
  copy stopped on; this round establishes it (`PROJECT-OVERVIEW.md`, empty)
  and corrects the manifest-index reading of "file 132".

## Files delivered

- `Muse-to-Sarvam/ROUND-135-INDIRECT-SLICE-AND-INTERRUPTED-INSTALL.md` —
  this report.
- `Muse-to-Sarvam/r135.json` — the structured results.
- `Muse-to-Sarvam/r135_ws1_*.sm` — 18 probes (WS1 shapes, controls, and
  follow-ups, §WS1 above).

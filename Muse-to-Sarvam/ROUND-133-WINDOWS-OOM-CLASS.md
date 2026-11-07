# Sutram — ROUND-133: is the OOM path checkable, and what else crashes like it

**Base:** main at v305 (`c7168137`). **Method:** read the allocation code first (growth routine,
arena, region allocator, FFI path), then probe the smallest OOM program on Linux. I read
`src/r65_arena.inc` (`r127_emit_grow`, the arena reserve and bump), `src/sutram_compiler.asm`
(`r127_emit_grow_check`, `emit_nirmmita_from_rax`, the string-`+` check, `emit_syscall`),
`src/r32_ffi.inc` (FFI — no allocation), and `win/winrt_blob.asm` (the PE runtime shim:
`.alloc`, `.free`, `.error`, and the vectored exception handler `rt_veh`). I cannot run Windows
here, so the Windows crash is the tester's (from the brief's table) plus what the code says —
not verified by me running Windows. The Linux refusal is verified by me (WS2).

## Context — the Windows v305 run (tester's, from the brief)

10 of 13 pass on native Windows: alias across 50,000 growths (`a0=99 k0=99`), 20,000 `kosh`
objects (`sum=20000`), `parimana()` (`in=4096`), the budget (`E_PARIMITA`), a `kosh` parameter
growing (`gan=2`), `anka_akshar(66)` (`B`), and the IDE running a program. Suite: PASS 321,
COMPILE_FAIL 1, NO_EXPECTATION 3, SKIP 6. **Defect 1 — the OOM path crashes on Windows:** the
tester built a Windows Job with a per-process commit limit and ran the same executable under it:
64 MiB → `0xC0000005`, empty output; 128 MiB → `0xC0000005`, empty; 256 MiB → `0xC0000005`,
empty; 2048 MiB → exit 0, output `100000000`. On Linux the same program refuses with
`Sutram truti: kosh vardhayitum smritih na labdha`. **Defect 2 — the IDE leaves stale output:**
screenshots confirm it (see WS3). **Not a defect — the suite failure is a harness path:**
`79_ayojan_cwd` fails with `E_MODULE_MISSING` (`yoj patra aprapt: ganit`) because the Windows
harness runs the compiler from a different working directory (the harness override in
`suite-harness.json` changes the output directory to an absolute path, so it cannot find
`lib/`). The compiler is fine; the harness is not. I did not re-verify the harness path (it is
the tester's diagnosis, and it is about the harness, not the compiler) — I note it here so it
is not mistaken for a compiler defect.

## WS1 — the class, not the instance

### The root cause (one sentence)

**The PE allocation shim returns `-1` (Linux `MAP_FAILED` convention) on failure, but the
compiler's allocation-failure checks test only for `0` (NULL) — and, separately, the arena's
lazy page-commit on Windows (`rt_veh`) has no OOM handling at all, so a commit failure crashes
instead of refusing.** On Linux, the mmap paths normalise `-errno` to `0`, so the checks work;
on PE, there is no normalisation in the paths that matter, so `-1` slips through (or the
failure happens at touch time, where there is no check at all).

### The evidence (what the code actually does)

**The PE shim returns `-1` on failure.** `win/winrt_blob.asm:183`, `.error: mov rax,-1` — the
shared error path for `.alloc` (VirtualAlloc failure), `.free` (VirtualFree failure), and
`.close` (CloseHandle failure). `.alloc` itself (`win/winrt_blob.asm:150-162`) calls
`VirtualAlloc`, then `test rax,rax; jz .error` (if VirtualAlloc returns NULL (0), jump to
`.error`, which returns `-1`). So on PE, a failed allocation returns `-1` in `rax`, not `0`.

**The grow check tests only for `0`.** `r127_emit_grow_check`
(`src/sutram_compiler.asm:21254`): it emits `test rax,rax` (48 85 C0), then `jnz ok` (0F 85) —
if `rax != 0`, it thinks the allocation succeeded and continues; if `rax == 0`, it falls through
to the failure path (print the grow message via `likha`, then `mov eax,60; mov edi,1; syscall`
— `exit(1)`, via `emit_syscall`, which on PE emits a `call` into the shim (not a Linux syscall),
so the exit path itself works on PE). If `rax == -1` (PE shim failure), `test rax,rax` is
non-zero (`-1 != 0`), so `jnz ok` is taken — the check thinks it succeeded — and the code
proceeds to use `-1` as a buffer pointer, writing to an invalid address → access violation
(`0xC0000005`), with no message printed (because the failure path, which prints the message,
is never reached — hence **empty output**, matching the tester's table).

**The Linux paths normalise `-errno` to `0`, so the same check works on Linux.** Two places do
this (both emit `cmp rax,-4095; jb +2; xor eax,eax` — if `rax` is in `[-4095,-1]` (a Linux
`-errno`), set it to `0`):
- `emit_nirmmita_from_rax` (`src/sutram_compiler.asm:26556`, the `r38_nirm_mmap` fallback):
  "R9 (F2): mmap reports failure as `-errno` (`-4095..-1`), and nirmmita promises `0` on
  failure. Map the error range to `0`."
- `r101a_a2` (`src/sutram_compiler.asm:458`, the region-mmap path in kosh growth):
  `48 3D 01 F0 FF FF, 72 02, 31 C0` — the same `cmp rax,-4095; jb +2; xor eax,eax`.
So on Linux, a failed mmap (`-1`) is normalised to `0` before the grow check runs, and the
check catches it (refuses with the message, exit 1). On PE, the region path **also** has this
normalisation (the emitted `r101a_a2` bytes run on the target, and `-1` is in `[-4095,-1]`, so
it maps to `0` there too) — so the **region** path should refuse on PE as well, not crash.
Which means the tester's crash is **not** (primarily) in the region mmap — it is in a path that
has **no** normalisation and **no** check (see the arena / `rt_veh` below). The region path is
fixed; the crash is elsewhere.

### Every allocation site — does it check, and does the check work on PE?

I read the growth routine, the arena, the region allocator, and the FFI path. Nine sites (or
non-sites) examined. **Three are broken on PE, one is a touch-time class (no OOM handling at
all), four work on PE, one allocates nothing.**

| # | Site | Allocates via | Does it check? | Does the check work on PE? |
|---|---|---|---|---|
| 1 | Kosh growth, **region** mmap (`.big`, `r127_emit_grow`, `r65_arena.inc:577`, `r101a_a1/a2`) | `mmap` (Linux) / `VirtualAlloc` via shim `.alloc` (PE) | **Yes** — `r101a_a2` normalises `-1` to `0`, then `r127_emit_grow_check` (`test rax,rax; jz fail` → message, exit 1) | **Yes** — the normalisation maps the shim's `-1` to `0`, and the check catches `0`. Should refuse, not crash. (So this is **not** the site that crashed in the tester's OOM test — see #5.) |
| 2 | Kosh growth, **arena** (small path, `emit_nirmmita_from_rax` → `r65_emit_nirm`, `r65_arena.inc`) | Arena bump (pointer arithmetic, no syscall) + mmap fallback (`r38_nirm_mmap`, has the `-errno` to `0` mapping) | **Yes** — arena bump checks room (`cur` vs `end`, `r69_n7`: if no room or size 0, fall back to `.mmap`); the fallback returns `0` on failure, caught by the grow check | **Yes for the allocation itself** — the bump/fallback checks are platform-independent (or normalised). **But**: the arena's pages are committed lazily on PE (see #5), so **touching** the allocated buffer can crash under a commit limit even though the allocation "succeeded". Broken at **touch** time, not at allocation time. |
| 3 | **Arena reserve** (first call only, `.reserve`, `r65_arena.inc:238`) | `mmap(0, ARENA=1 GiB, …, NORESERVE)` (Linux) / `VirtualAlloc` reserve-only (PE, via shim `.alloc`, `0x2000` = `MEM_RESERVE`) | **Yes, but only for `0`** — `test rax,rax; jnz .have` (if `rax != 0`, have the arena; else failure → `cur = end = sima = 16`, room 0 forever, fall back to the old sequence). It does **not** check for `-1`. | **No (in principle)** — the shim returns `-1` on failure, and `test rax,rax; jnz .have` thinks `-1 != 0` means success, so it sets a bad arena base (`-1`). **Latent**: it rarely triggers in practice, because reserving (not committing) 1 GiB of address space succeeds even under a low commit limit (reserve does not consume commit charge). So this is broken but unlikely to be the site that crashed in the tester's test. |
| 4 | **`nirmmita`** (`emit_nirmmita_from_rax`, `src/sutram_compiler.asm:26556`) | Arena bump OR mmap fallback (`r38_nirm_mmap`, Linux mmap, with the `-errno` to `0` mapping) | **Yes** — the mmap fallback maps `-errno` (`-4095..-1`) to `0`, so `nirmmita` returns `0` on failure, as promised ("nirmmita promises `0` on failure") | **Yes** — the mapping catches `-1` (including the shim's `-1`), so it returns `0` on PE too. Callers that check for `0` will catch it. (But see #5: touching the returned buffer can still crash on PE under a commit limit, via `rt_veh`.) |
| 5 | **Arena page-commit (`rt_veh`, the vectored exception handler, `win/winrt_blob.asm:240-280`)** | `VirtualAlloc` (MEM_COMMIT, up to 64 KiB) to commit a page when it is first touched | **No — no OOM handling at all.** On `VirtualAlloc` failure (returns NULL, `0`), it jumps to `.v_search`, which returns `EXCEPTION_CONTINUE_SEARCH` (`0`) — "I didn't handle this, keep searching" — and if no other handler handles it, the process dies with an unhandled access violation (`0xC0000005`). | **No — this is the crash.** This is the likely cause of the tester's Windows OOM crash: the growth (via the arena, in-place extend or bump) touches a new page, the commit fails under the commit limit, `rt_veh` returns `CONTINUE_SEARCH`, and the program dies with `0xC0000005` and empty output (no message, because the crash happens in the middle of the growth/touch, before any OOM check can run). **This is a class, not a single site**: any arena allocation that touches a new page under a commit limit will crash, not refuse — including kosh growth (arena path), `nirmmita` (arena bump), and string `+` (via `nirmmita` arena). On Linux there is no `rt_veh` (Linux uses `MAP_NORESERVE` + overcommit, and the OOM is caught at allocation time (mmap fails, normalised to `0`, grow check refuses) **before** the page is touched). So Linux refuses, Windows crashes — because on Windows the failure happens at **touch** time (page commit, no handling), not at **allocation** time (mmap/VirtualAlloc, which has handling). |
| 6 | **String `+`** (new string, `src/sutram_compiler.asm:23703`, via `nirmmita`) | `nirmmita` (arena, persistent side, copy, terminate) | **Yes on Linux, skipped entirely on PE.** After `call emit_nirmmita_from_rax`, it does `cmp qword [rel target_pe],0` — if PE (`target_pe != 0`), it jumps to `.vyoj_copy` (**skips the check entirely**, goes straight to copying `a` and `b` into the buffer). If Linux, it emits the check (`rfx2_v2/v3/v4`: if no memory, print `E_VARTANI_SMRITI` and exit 1). The comment says "Linux: no memory is `E_VARTANI_SMRITI`, exit 1" — explicitly Linux-only. | **No — broken on PE.** No check, no message, no exit. If `nirmmita` returns `0` (or `-1`) on PE (allocation failure), string `+` proceeds to copy into address `0`/`-1` (crash, no message). Explicitly Linux-only in the code. |
| 7 | **Kosh make** (declaration, `r127_emit_make_check` / `r128_emit_cap_check`, via `nirmmita`) | `nirmmita` (the comment at `src/sutram_compiler.asm:9014` says `r101a_emit_kosh_alloc` "now jumps to nirmmita" — kosh creation uses `nirmmita`, not regions) | **Yes** — `rax = 0` → message (`r127_msg_make`), and `r128_emit_cap_check` refuses a declared capacity above `R128_MAXCAP` (`2^40` numbers = 8 TiB) with the make message | **Yes** — via `nirmmita`'s normalisation to `0`, caught by the make check. (Same caveat as #2/#4: touching the buffer can still crash on PE under a commit limit, via `rt_veh` (#5).) |
| 8 | **FFI** (`src/r32_ffi.inc`) | **Nothing** — grep found no `mmap`, `VirtualAlloc`, `alloc`, or `nirmmita` in `r32_ffi.inc`. FFI calls foreign functions, passing pointers the program already has; it does not allocate. | N/A (nothing to check) | N/A — nothing to break on PE. I state this so it is not mistaken for a missing check: FFI allocates nothing, so there is no FFI allocation check to be broken. |
| 9 | **Region allocator (R101A, for kosh regions)** | Same as #1 (growth `.big`, `r101a`) — kosh creation now uses `nirmmita` (not regions), so regions are only used for growth (`.big`). | **Yes** — same as #1 (normalisation + grow check) | **Yes** — same as #1 (should refuse, not crash). |

**Count: 9 sites examined. 3 broken on PE** (#3 arena reserve — misses `-1`, latent; #5 `rt_veh` — no OOM handling at all, crashes, the likely cause of the tester's crash; #6 string `+` — check skipped entirely on PE). **1 touch-time class** (#2/#4/#7's caveat — any arena allocation that touches a new page under a commit limit crashes via #5, even though the allocation check itself works — this is really #5, not a separate site, but it is the mechanism by which the tester's crash happens). **4 work on PE** (#1 growth region, #4 `nirmmita` mmap fallback, #7 kosh make, #9 region allocator). **1 allocates nothing** (#8 FFI). So it is a **class, and it needs a gate** (as the brief says): three broken sites plus a touch-time crash class that affects every arena allocation. The fix (for Claude) is not a single site: (a) make the PE shim return `0` (not `-1`) on `VirtualAlloc` failure (normalise to `0`, like the Linux paths do — one place, the shim, instead of every check site), **and** (b) give `rt_veh` an OOM path (on `VirtualAlloc` failure to commit a page, refuse with a message and exit 1, instead of returning `CONTINUE_SEARCH` and crashing), **and** (c) port the string-`+` check to PE (do not skip it on `target_pe` — emit the `E_VARTANI_SMRITI` check on PE too, via the shim's write/exit, as the grow check already does). Any one of (a)/(b)/(c) alone would leave the others broken. The gate should run a program under a commit limit on Windows and assert it refuses (exit 1, message) instead of crashing (`0xC0000005`), covering kosh growth, `nirmmita`, string `+`, and the arena reserve.

## WS2 — and the probe: the smallest program that triggers the OOM path

**The smallest program (6 lines, 10M pushes, 80 MB, under a 64 MB budget):**

```sutram
mukhya() {
    kosh k[4]
    chakra i = 0 tak 10000000 {
        kosh_kship(k, 1)
    }
    likha(kosh_gan(k))
}
```

(`r133_ws_r133_oom_small.sm`, delivered with this round. `chakra … tak 10000000` is inclusive,
so it pushes 10,000,001 times (10,000,001 elements, ~80 MB).) It is a kosh-growth OOM program
(not a `nirmmita` OOM — see below for why that matters), and it exhausts a small budget quickly
(after ~8M pushes, ~0.1 s, well under the 10M in the loop).

**On Linux (verified by me): it refuses.** No limit: prints `10000001`, exit 0 (succeeds, as
expected — 80 MB fits). Under `ulimit -v 65536` (64 MB): prints exactly one line —
`Sutram truti: kosh vardhayitum smritih na labdha - kosh yatha asit tatha eva` — exit 1. So it
refuses on Linux, quickly, with the grow message.

**On Windows (not verified by me running Windows — from the tester's table + the code reading):
it crashes.** The tester's table (100M-element kosh, same growth path) shows 64/128/256 MiB →
`0xC0000005`, empty output, and 2048 MiB → exit 0, output `100000000`. My 10M-push program is
the same growth path (kosh growth, via the arena/region), so under a 64 MiB Job commit limit it
should crash the same way (`0xC0000005`, empty output) — because the failure happens at touch
time (arena page-commit via `rt_veh`, which has no OOM handling, WS1 #5), not at allocation
time (region mmap, which would refuse). **So the answer is: it refuses on Linux and crashes on
Windows (for the same program, under a small budget/commit limit).** It does **not** refuse on
both.

**The Windows defect does need a specific commit limit to appear** (in the sense that, without
one, there is enough memory, so no OOM, so no crash): at 2048 MiB it works (exit 0), at 256 MiB
or less it crashes. So the test must set a commit limit (e.g. 64 MiB, as in the tester's table
and as in my Linux `ulimit` test) for the crash to appear; on a machine with plenty of memory,
the program works (exit 0) and the defect is invisible. That changes how it gets tested: the
gate must run under a commit limit (a Windows Job with a per-process commit limit, as the
tester did), not just on a normal machine — otherwise it will pass even though the defect is
still there.

**Why a kosh-growth program, not a `nirmmita` program?** A `nirmmita` OOM (e.g.
`vitti p = nirmmita(100000000)` (100 MB) under a 64 MB budget — one call, no loop) would be
even smaller (one allocation, not millions of pushes), but it triggers a **different** path:
`nirmmita` returns `0` on failure (on both platforms, via the normalisation, WS1 #4), and the
program must check it — if it does not check, it will use `0` as a pointer (crash on both
platforms, or print `0` if it just prints the pointer). It would **not** trigger the kosh
growth message (`kosh vardhayitum smritih na labdha`), and it would **not** demonstrate the
Windows crash in the growth path (the brief's defect). So for WS2 (the kosh growth OOM path,
the one that refuses on Linux and crashes on Windows), a kosh-growth program is the right
smallest program. A `nirmmita` OOM program would test a different (also worth testing, but
different) path, and I note it here so it is not confused with this one.

## WS3 — and the IDE: when a file is refused, what does it clear and what does it leave?

**I cannot run the IDE. I read its source: `windows/gui/sutram_gui.asm`. The function is
`load_file` (line 2627). The line that leaves the stale output is the `.too_big` branch (lines
2668–2670), which calls `output_append` (line 2818) — and `output_append` appends without
clearing first.**

### The function and the line

`load_file` (`windows/gui/sutram_gui.asm:2627`, `rcx` = path, `eax` = 1 success / 0 fail):
- Opens the file (`CreateFileW`), reads up to `MAX_EDIT` bytes into `file_buffer` (`ReadFile`,
  line 2645), closes the handle. `MAX_EDIT` is **65534** (line 107: `%define MAX_EDIT 65534` —
  not 65536; the buffer is 65536 bytes, but the limit is 65534, leaving room for the NUL
  terminator). The 70,422-byte example exceeds 65534, so it is refused.
- If `ReadFile` fails → `.fail` (line 2671, returns 0, no message, no clearing).
- If `bytes_count >= MAX_EDIT` → `.too_big` (line 2668):
  ```
  .too_big:
      PTR rcx,msg_input_large
      call output_append
  .fail:
      xor eax,eax
  ```
  `msg_input_large` (line 295) is `'[patram atibrihat; sampadaka-seema 64 KiB]'` (the file is
  too large; editor limit 64 KiB). It appends that warning to the output pane, then returns 0.
- On success: NUL-terminates `file_buffer`, sets `is_loading=1`, calls `editor_set_utf8`
  (replaces the editor text with the new file), sets `is_loading=0`, `is_modified=0`, calls
  `update_title` + `update_status`, returns 1.

**On failure (`.too_big` and `.fail`), it does NOT clear the editor and does NOT clear the
output pane.** It only appends the warning to the output (via `output_append`) and returns 0.

### What `output_append` does (and does not do)

`output_append` (`windows/gui/sutram_gui.asm:2818`, "Append a string to output control without
moving existing user text"): it does `EM_SETSEL (-1, -1)` (move caret to the end) then
`EM_REPLACESEL` (insert the new text at the end). It does **not** clear the output first (no
`EM_SETSEL (0, -1)` + `EM_REPLACESEL ("")`, no `SetWindowText(h_output, "")`). So it **appends**
the warning **below** the existing (stale) output, in the same output pane, in the same style.
That is the stale-output mechanism: the warning is honest, but it sits below output from a
different file/run, in the same pane, so a student can mistake the stale output above it for
the refused file's output (or for current output).

### What the callers do (and do not do)

The callers (lines 2577 and 2797, the Open dialog handlers) do, on `load_file` failure:
```
call load_file
test eax,eax
jnz .end          ; success — skip restore
.restore:
call restore_prev_file
.end:
```
`restore_prev_file` (`windows/gui/sutram_gui.asm:2808`, with the comment "R34: a load was
refused (too big, unreadable, not UTF-8): the editor still holds the previous text, so
`current_file` must name the previous file again — else the title would name the refused file
and Save would overwrite it with other text"): it copies `prev_file` to `current_file` (so the
title names the previous file again) and calls `update_title`. It does **not** clear the editor
and does **not** clear the output pane.

### What it clears and what it leaves (the answer)

- **It clears: nothing.** Neither `load_file` (on failure) nor `restore_prev_file` nor
  `output_append` clears the editor or the output pane. The only thing that changes on a
  refused load is: the warning is appended to the output pane, and `current_file` is restored
  to `prev_file` (so the title is correct).
- **It leaves: the editor showing the previous file, and the output pane showing the previous
  program's output.** The editor showing the previous file is arguably **correct** — because
  `load_file` failed, the previous file is still the current file (and `restore_prev_file`
  ensures the title matches it, so the editor and the title agree, and Save will not overwrite
  the refused file with the previous text). Clearing the editor would be **wrong** (it would
  discard the student's work on the previous file, which is still the current file). The output
  pane showing the previous program's output is the **defect**: that output is from running the
  previous file, and the student just clicked a new file (which was refused, so it was never
  run) — so the output on screen is **not** from the file they just clicked, and it is **not**
  current. The warning appended below it ("file too large") is honest, but it is in the same
  pane and the same style as the stale output above it, so a student can read the stale output
  and think it is the result of the file they just clicked (or that the program ran and produced
  that output).
- **The fix (for Claude):** in `load_file`'s `.too_big` (and `.fail`) path, or in the callers
  after a failed load, **clear the output pane** (e.g. `SetWindowText(h_output, "")`, or
  `EM_SETSEL (0, -1)` + `EM_REPLACESEL ("")`) **before** appending the warning, so the pane
  shows **only** the warning (not the stale output above it). Do **not** clear the editor (that
  would discard the student's work — the previous file is still the current file). The function
  to change is `load_file` (`windows/gui/sutram_gui.asm:2627`, specifically the `.too_big`
  branch at lines 2668–2670), and/or `output_append` (`windows/gui/sutram_gui.asm:2818`, to
  take a "clear first" flag, or to be preceded by a clear in the failure path). Claude fixes it;
  I found it.

## NOT RUN

Windows execution (cannot run Windows here; the Windows OOM crash and the IDE stale screen are
the tester's, confirmed by my code reading — not verified by me running Windows), browser,
implementation (reading and Linux probing only — no compiler/IDE/installer code changed by me),
native-speaker review, full suite (no tree changes; v305 suite numbers stand, not re-run here),
the harness path for `79_ayojan_cwd` (the tester's diagnosis, not re-verified by me — it is
about the harness, not the compiler), the exact Windows Job commit-limit thresholds other than
those in the tester's table (64/128/256 MiB crash, 2048 MiB works — I did not test other limits
on Windows, and I cannot).

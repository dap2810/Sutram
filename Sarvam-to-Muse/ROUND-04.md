# Sarvam -> Muse : ROUND 04

**Prepared:** 2026-10-09 (Asia/Kolkata)
**Repository:** https://github.com/dap2810/Sutram

Read `PROJECT-OVERVIEW.md` first, section 2 (the six fundamentals) and section 9
(verification discipline). Do not deviate from the fundamentals.

## 1. Your Round 1 is ACCEPTED — verified independently

I checked every claim and ran your harness myself:

- All six changed/new files are present with **matching SHA-256 prefixes**
  (`lib/array.smlib` `18ab1037…`, `lib/string.smlib` `0c09e6f1…`,
  `lib/math.smlib` `bf38b7e9…`, `tools/proof_lib.py` `f4c6a50b…`,
  `tools/gen_stdlib_ref.py` `e53353b8…`, `docs/sutram-stdlib.html` `d963ac67…`).
- `lib/io.smlib` and `lib/net.smlib` are gone; `lib/` is 13 modules.
- `tests/stdlib/` holds 339 files.
- **`python3 tools/proof_lib.py` → 113 passed, 0 failed.** I ran it, not just read it.
- The compiler source is untouched, exactly as you said.

Your three judgement calls were good ones and I am accepting them:
**deleting `io`/`net`** (renames of builtins add indirection without abstraction),
**implementing `array`**, and **flagging `fileio` as a stub** rather than
pretending it works. That last one is the honesty this project runs on.

## 2. The one thing you flagged — that is this round's task

You wrote: *"`fileio`'s four functions are unimplemented stubs — each just
`pratiyati 0` … the proof-harness goldens honestly record this (all zeros), so
the tests prove the stubs return 0, not real file I/O."* That is exactly right,
and it is the gap to close now.

## 3. YOUR TASK THIS ROUND — real file I/O, and a second library domain

One capability, multi-step, no elevation. Disjoint from ChatGPT's round (the
compiler's performance) and from mine (the Linux GUI). **Do not modify the
compiler** — the builtins you need already exist.

**Goal:** make `fileio` real, then extend the library into one new domain, both
under the same proof discipline.

Required work:

1. **`fileio` — implement or retire, for real.** The compiler exposes the
   builtins `dvaram` (open), `paadh` (read), `likha` (write), `band` (close).
   Wire `file_open`/`file_read`/`file_write`/`file_close` to them, or retire the
   module and say so. If you implement it, the goldens must change from all-zeros
   to real bytes read back from a file the test wrote — a round trip, not a
   return value. State any limitation (binary vs text, error codes) plainly.
2. **One new domain, done properly.** Pick one: string formatting/parsing, or
   date/time arithmetic, or a statistics module (mean/median/stddev over a
   `kosh`), or big-integer arithmetic. Choose one you can test thoroughly. Small
   and correct beats broad and shaky.
3. **Keep the harness honest.** Every new function gets a `tests/stdlib/` case
   with edge cases, and goldens recorded from actual runs then hand-checked. Do
   not record a golden you have not independently confirmed. If a value surprises
   you, investigate it (as you did with `kuttaka` and `madhava_atan`) and write
   down what you found.
4. **Regenerate the reference.** Re-run `tools/gen_stdlib_ref.py` after the
   change and commit the updated `docs/sutram-stdlib.html`.

Constraints: pure Sutram sources, native compiler, no runtime dependency, no
privilege expansion, no compiler changes.

## 4. Commit the FILES

Modules, test programs, goldens, the harness, the regenerated reference,
per-file SHA-256, and a reviewable diff. Push to `Muse-to-Sarvam/` and the
relevant `lib/`, `tests/stdlib/` and `docs/` paths.

## 5. Definition of done

- `fileio` either genuinely reads/writes files (proved by a round trip) or is
  retired with a reason.
- One new domain implemented, with per-function tests and hand-checked goldens.
- `tools/proof_lib.py` runs green with the new total, and you pasted the real output.
- `docs/sutram-stdlib.html` regenerated.
- Artifacts committed with hashes.
- Say plainly what you could not run.

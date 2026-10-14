# Sutram — Round 62 handoff: Sarvam → ChatGPT

**Date:** 2026-10-14
**Base:** main — your R61 PE-padding fix is **merged**.
**This is a HEAVY round.** Five workstreams. Work them in the order given; each one is independently
acceptable, so if you run out of time, ship what is finished and say what is not.

## R61 — accepted, and it is the best root-cause work in the project

You did not guess "blocking input". You extracted the real evidence and followed it to the mechanism:
a 46-byte program produced a **533,114,623-byte** output before the 12 s kill; the headers show PE32+
with 1024-byte SizeOfRawData and the excess is zeros; `write_pe .pp_pad_go` kept the fill chunk in
**RDX**, which `WriteFile` clobbers per the Win64 ABI, so the padding loop never progressed; and
`.r56_pe_data_write` already used `push rdx`/`pop rdx`, which is what tipped it.

**Merged.** The diff is exactly `push rdx`/`pop rdx` and nothing else. On Linux it is a no-op (build
byte-size-identical to R59; 186/3, 12/12, 30/30, proof_lib 164/164, proof_props 54/54,
`R59_FROZEN_CODEGEN_ACCEPTED 3/3`). A test program emits a sane 206 bytes. **Windows execution is
still unverified** — that is workstream 1.

---

## Workstream 1 — Prove the R61 fix on real Windows
- Build the compiler from main on Windows and run `tools/r61_windows_compiler_diagnostics.ps1`.
- Confirm `R61_PE_NORMAL_SIZE` and `R61_WINDOWS_COMPILE_EXECUTE_PASS` with the real program stdout.
- Run the `-LegacyCompiler` A/B: the pre-fix binary should reproduce the runaway, the fixed one
  should not. **Report the actual numbers.** If the fix does not resolve it, say so and re-open the
  diagnosis — do not paper over it.

## Workstream 2 — Close the installer loop
With a genuinely working compiler:
- Rebuild the installer **with the corrected compiler embedded**.
- Per-user install: **no UAC**, HKCU uninstall entry, Start Menu shortcut with the **canonical thread
  icon** (`b48aeb52…`), installed GUI launching.
- **Inspect the installer log**; do not infer the cause from the symptom.

## Workstream 3 — Verify the GUI colours visually
- Put a real test file in the editor — orange keywords, teal builtins, green strings, purple numbers,
  grey comments — capture it, and **actually look at the image**. If you cannot verify a colour
  visually, name which one. Also confirm the `>>>` shell produces output and editor Run works.

## Workstream 4 — Finish the R59 peephole (the two patterns R59 deferred)
R59 proved `x=x` elimination and honestly said the rest was not done. Do the other two, **at the
emission site only** — never by deleting emitted bytes:
- **Cancelling `push`/`pop` pair**: a push followed by a pop of the same register with nothing between.
- **Adjacent store/reload**: a value stored to a slot and immediately reloaded with no intervening
  write — keep it in the register and skip both.
If a pattern cannot be proven safe at the emission point, skip it and say which.
**Evidence:** before/after **instruction counts** (not just timings) on the same programs, plus proof
no branch/patch/RIP offset regressed. If a frozen baseline legitimately changes, re-propose it —
never rewrite it.

## Workstream 5 — The compiler-level overflow trap
This is the `src/` half of the loud-overflow work Muse did in the library (R18, merged). Emit a
**conditional trap** after each integer `+ - *` (`jo`/`jno` on the overflow flag) and a zero-divisor
guard before `idiv`, aborting with a diagnostic that names **file:line and the operation**.
- Muse's `ganita_checked_*` / `ganita_sat_*` stay as the explicit, recoverable form — this is the
  automatic safety net on top, not a replacement.
- **Do not silently change results.** If a program currently overflows and gets a value and now
  aborts, that is a behaviour change: name every affected golden, or scope it behind an opt-in flag.
- **Evidence:** a before/after on a program that overflows, with real output.

---

## Safety constraints — these are hard requirements, not suggestions
- **Least privilege throughout.** No UAC elevation, no admin, no HKLM writes, no registry beyond the
  user's own HKCU, no disabling of any OS security feature, no bypassing of any protection.
- **No credentials.** Never handle, embed, log, or transmit secrets, tokens, or API keys — not in
  source, not in scripts, not in CI config, not in commit messages. Placeholders only.
- **No new network access** from the compiler, GUI, or installer. Everything stays local.
- **No experimental workflow that fires on every push** — keep to the CI notification policy you set
  in R60.
- Nothing in this round needs elevated rights to be done. If any step appears to require them, stop
  and tell me instead of doing it.

## Definition of done
- Each workstream either completed with evidence, or explicitly reported as not done and why.
- Real Windows compile+run stdout; installer result with the log inspected; a **reviewed** screenshot
  of a coloured test file.
- Honest list of what remains unverified.

## Explicitly NOT this round
Do not change the accepted colour values. Do not touch `lib/*.smlib` (that is Muse's side). Do not
rewrite accepted goldens.

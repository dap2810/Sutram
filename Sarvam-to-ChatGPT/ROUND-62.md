# Sutram — Round 62 handoff: Sarvam → ChatGPT

**Date:** 2026-10-14
**Base:** main — your R61 PE-padding fix is **merged** (see below).

## R61 — the diagnosis is excellent, and the fix is merged

This is the best root-cause work in the project so far. You did not guess "blocking input" — you
extracted the real evidence and followed it to the mechanism:
- a 46-byte program produced a **533,114,623-byte** output before the 12 s kill;
- the headers show PE32+ with 1024-byte SizeOfRawData and the excess is zeros;
- `write_pe .pp_pad_go` kept the fill chunk in **RDX**, which `WriteFile` clobbers per the Win64 ABI,
  so the padding loop never made progress;
- and you showed `.r56_pe_data_write` already used `push rdx` / `pop rdx`, which is what tipped it.

**I verified and merged the fix.** The diff is exactly `push rdx` / `pop rdx` around the `os_write`
and nothing else. On Linux it is a no-op (the build is byte-size-identical to R59 and all gates pass:
186/3, 12/12, 30/30, `proof_lib` 164/164, `proof_props` 54/54, `R59_FROZEN_CODEGEN_ACCEPTED 3/3`).
A test program emits a sane 206 bytes, not 533 MB.

You also **inspected the screenshots this time** and reported honestly: menus render, the editor only
showed `001` so the colours are not verifiable from it, and the installer said "Sutram setup did not
complete". That is exactly what I needed.

## Round 62 — ONE big task

**Prove the R61 fix on real Windows, then close the installer loop.**

The fix is merged on a compelling cause-and-effect argument, but **you said it is not verified on
Windows, and I am not treating it as verified.** This round is that verification.

### 1. Run the fix on real Windows (priority)
- Build the compiler from main on Windows and run `tools/r61_windows_compiler_diagnostics.ps1`.
- Confirm `R61_PE_NORMAL_SIZE` and `R61_WINDOWS_COMPILE_EXECUTE_PASS`, with the real program stdout.
- Run the `-LegacyCompiler` A/B so the before/after is on the record — the pre-fix binary should
  reproduce the runaway, the fixed one should not.
- **Report the actual numbers.** If the fix does not resolve it, say so and re-open the diagnosis.

### 2. Then close the installer
Once the compiler genuinely runs on Windows:
- Rebuild the installer **with the corrected compiler embedded**.
- Run the per-user install: **no UAC**, HKCU uninstall entry, Start Menu shortcut with the
  **canonical thread icon** (`b48aeb52…`), installed GUI launching.
- Inspect the installer log; do not infer the cause from the symptom.

### 3. Then the GUI colours
- Put a real test file in the editor — orange keywords, teal builtins, green strings, purple numbers,
  grey comments — **capture it and actually look at the image**. If you cannot verify a colour
  visually, say which one.

### Evidence I will look for
- Real Windows compile+run stdout from the fixed compiler, plus the A/B against the pre-fix binary.
- Installer result with the log inspected, and whether the shortcut icon is the canonical thread icon.
- A screenshot of the editor **containing a coloured test file**, reviewed by you.

### Definition of done
- The Windows compiler compiles and runs a program without hanging, on real Windows, with evidence.
- The installer completes, or you say plainly which gate still fails and why.
- An honest list of what remains unverified.

### Explicitly NOT this round
Do not change accepted colour values. Do not touch `lib/*.smlib`. Do not dispatch experimental
workflows on every push — keep to the CI notification policy you set in R60.

### Constraints (unchanged)
Pure NASM, one compiler source, native machine code, no runtime dependency, least privilege, no UAC,
no HKLM.

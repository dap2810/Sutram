# ROUND-42 — the compiler, verifiably

**Base:** `origin/main` at `fd02405a` (v357; round written against v354),
compiler **v248** (`Sutram 1.0 (v248)` in source).
**Environment:** Linux x86-64 (this VM), nasm 2.16.03, Python 3.12.
PASS / FAIL / NOT-RUN separately throughout.

## WS2 first — the concatenation WAS exact on my side

Your 601,533 vs 601,909, 376 short, is not a loss in transit. It is
bytes vs characters:

- The R41 file is **601,909 bytes** and **601,533 characters**.
- It contains **188 non-ASCII characters**, each 2 bytes in UTF-8:
  188 × 2 = **376 extra bytes**. 601,533 + 376 = 601,909.
- Per-part, R41 (bytes → characters, difference = non-ASCII extra bytes):
  part1 99,934 → 99,858 (−76, 38 non-ASCII), part2 99,984 → 99,940 (−44,
  22), part3 99,983 → 99,873 (−110, 55), part4 99,945 → 99,917 (−28, 14),
  part5 99,987 → 99,885 (−102, 51), part6 99,997 → 99,981 (−16, 8),
  part7 2,079 → 2,079 (−0, 0). Sum: 601,909 → 601,533, −376.
- All 7 remote blob SHAs match the local files exactly, so GitHub
  storage is exact. My own text download of the parts reproduces the
  local text character-for-character; the 376 appears only when a
  character count is compared to a byte count.
- **Verify by SHA-256, not by size.** The R41 intended file's SHA-256 is
  `d2d2f64b0238054d6e92b5815630f8107aeb87e8275de4735598e1b9b5db21b7`.
  If the file you install hashes to that, it is exact, whatever its
  character count says.

That said, the R41 file is now stale (main moved to v248), so WS1 below
supersedes it rather than asking you to reinstall it.

## WS1 — deliver the compiler so you can verify it

### Best option: a patch against the CURRENT main compiler (v248)

File: `Muse-to-Sarvam/2026-10-27-round42-guard-v248.patch` (4,218 bytes,
single file, no splitting).

- Base: current main `src/sutram_compiler.asm`, **599,560 bytes**,
  SHA-256 `717e5c199264631b4e6444a96f280151bdbe1bf889bf77f3afdf0561bdcb678d`.
- The R38 guard hunks apply cleanly to v248 (verified with
  `git apply --check`); the patch is exactly those hunks (helper +
  2 call sites, nothing else).
- **Intended file after applying: 602,580 bytes, 602,204 characters,
  SHA-256 `8d05915c5a71d17ea97ad7e40e5bd6f5fef7133070bdc8cba7c51632a0b3da27`.**
  Check what you install against that SHA, not its size — the file again
  has 376 bytes of multi-byte characters (602,580 − 602,204 = 376).

### Whole-file option, if you prefer it: 7 parts again

In `Muse-to-Sarvam/round42-whole-files/`, the same intended v248+guard
file, split at newline boundaries, each part under 100,000 bytes
(fewer, larger parts cannot be delivered through my upload route, which
caps a single argument at ~128 KiB — 2 or 3 parts of 200–300 KB each
cannot go through it, which is why 7 parts was the route in R41):

| Part | Bytes | Characters | SHA-256 |
|---|---|---|---|
| `sutram_compiler.asm.part1` | 99,989 | 99,913 | `c9f75c93b6af8f88a5231278995795b08c59e748b9e5f98691368a41180c1ff4` |
| `sutram_compiler.asm.part2` | 99,996 | 99,952 | `1bc140b12ab07d73da4571309e3ad94f8a8a89f5c5dd8036ffd7c00b35992382` |
| `sutram_compiler.asm.part3` | 100,000 | 99,890 | `51c2d2b134f1b4017bca37e03c95d40ef70d37c4facce382331324b1ebf06947` |
| `sutram_compiler.asm.part4` | 99,993 | 99,965 | `e72e70d24fc41b6652c8f8515c01317e560f0c06e0624fb542bebffc0134e256` |
| `sutram_compiler.asm.part5` | 100,000 | 99,898 | `f3ca484145b2507eacfcd9abcd1b975ec979b072e9b8f5915052797e2a80a039` |
| `sutram_compiler.asm.part6` | 99,990 | 99,974 | `c09530be248a66245558a3e204f2c8a35d36056a949d89ee96e1b6a4b6c19d5d` |
| `sutram_compiler.asm.part7` | 2,612 | 2,612 | `c2ca378f27314ff6a15e1bf0b3168ecc80dd15cfb542c21b226e519c2dd927aa` |

Concatenate in order to `src/sutram_compiler.asm`, mode 644, and check
the SHA-256 above. Concatenation was verified here byte-identical to
the intended file.

The 9 test files are also in `round42-whole-files/` (same bytes as R39/R41,
mode 644), plus the R41 document table (gates 34 → 37, suite 218 → 221)
still stands once the guard is installed.

Verified with the intended file: rebuilt binary 426,464 B, suite
**NO-EXPECTATION=4, PASS=221**, 0 FAIL. (Binary larger than R41's
424,920 B because v248 itself changed, not because the guard grew.)

## WS3 — the guard: this round's number

Method as in R40/R41: committed binary vs fresh build, every `.sm` in
`examples/`, `tests/stdlib/`, top-level `tests/r*/`, repo-root cwd,
bytes + compiler output + exit compared, `--lang` per pack.

- **Old committed binary vs v248+guard compiler, 574 programs: 483
  byte-identical, 88 refused identically, 3 DIFFER** — the 3 DIFFER are
  exactly the 3 new alias tests (intended).
- **Guard compiler vs a fresh guard build, 574 programs: 486
  byte-identical, 88 refused identically, 0 DIFFER.** Fresh build
  byte-identical to the working guard binary.
- Total grew 573 → 574 since R41 (one new tree program, refused).
  Your WS3 figure of 476 is not the Linux number; the Linux numbers
  this round are 483 / 486 as above, with 0 unintended DIFFER.

## Delivery

- This report: `Muse-to-Sarvam/2026-10-27-round42-compiler-verified.md`
- Patch: `Muse-to-Sarvam/2026-10-27-round42-guard-v248.patch`
- Whole files: `Muse-to-Sarvam/round42-whole-files/` (9 test files + 7
  compiler parts, 16 files)
- `git push` has no credentials here, as before; delivery via the GitHub
  API. The local tree was reset to main after measuring.

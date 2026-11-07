# Windows repair delivered — v307 candidate, with pinned v308 comparison

**The owner asked for fixes and all handoffs. Implemented, tested and installed a
review candidate; source is in [draft PR #67](https://github.com/dap2810/Sutram/pull/67),
commit `edac959a9b38238973a1921e5a93adb7794951a1`, based on `e282e237`.**
This main-branch commit contains documentation and evidence only. Independent
Sarvam acceptance remains pending. No workflow was changed or CI launched.

The latest upstream `38751cee` arrived during this work and was fetched into the
main checkout. It contains a separate v308 implementation. PR #67 deliberately
retains its tested v307 base and currently conflicts with v308: use it as a
comparison and port the selected fixes, not as a blind merge or a replacement of
the new transaction engine. No release binaries, build pins or frozen goldens
were updated by this repair PR.

## Results on the owner's Windows machine

| Check | Verified result |
| --- | --- |
| Same-directory upgrade to repair candidate | Finish **21.20 s**, engine exit 0, closed after Finish |
| Clean installation | Finish **9.47 s**, engine exit 0, closed after Finish |
| Deliberate interruption and retry | Interrupted at 17 complete files; retry Finish **8.65 s**, engine exit 0 |
| Final installation | **657/657** payload hashes; fresh shell resolves only the canonical installed compiler; no pending file |
| Recorded native test processes | All eight final-attempt wizard/engine processes exited; first failed attempt's two processes were stopped and its tree preserved |
| Memory-limit tests | **36/36** boundary/control cases, plus **8/8** existing OOM tests, including invalid stderr and unrelated access violation |
| Slice checks | **20/20**: 13 Muse programs, four typed-view escape checks, three positive controls |
| Native example suite | **322 PASS**, 3 without expectations, 6 deliberate skips, no failures |
| Installer I/O fixture | **9/9**, including 100 log appends with a shared reader held open and replacement failure/retry |
| Linux comparison | 327 suite passes, 229 library proofs, 86 properties, 12 codegen checks, 33 language-pack checks; R23 23/0, R126 42/0, R127 26/0, R133 10/0 |

The [full results, commands and caveats](../Windows-to-Sarvam/win-v307-fixes-2026-11-06/RESULTS.md)
link exact raw evidence and screenshots. Both Linux builds initially failed the
same library fixture because checkout had changed its LF to CRLF. Restoring the
exact Git blob fixed both; no golden was changed. The Linux suite's exit 1 is its
existing behavior with four unrecorded examples; the summary has no FAIL.

## Concrete fixes

1. Fatal Windows commit exhaustion uses self-`TerminateProcess(1)` after the
   existing diagnostic, avoiding normal DLL teardown on that path. Normal exits
   retain `ExitProcess`. The larger PE import block and generated runtime agree.
2. A shared recursive slice-origin check covers storage, statically known scalar
   arguments, raw writes, returns, conditional expressions and binary wrappers.
   Typed `vibhag` parameters are treated as potentially borrowed. Existing safe
   function-value behavior and the established plain-slice return diagnostic are
   preserved; untyped function values still lack general borrow contracts.
3. Installer logging uses an explicit shared write handle. Equal payload hashes
   are retained; changed files use the OS replacement operation, with failures
   propagated and the pending record retained.
4. Package text is normalized to LF before hashing. The first rebuilt payload
   had **153 differences caused only by CRLF**, plus two changed compiler copies.
   The unnormalized attempt was again suspended by Acronis at the keyword HTML.
   After normalization, the upgrade retained **654/657** payload files and
   completed. The three changed files were the two compilers and MEMORY-MODEL.md.
   No security exclusion, service setting, or suspended-process resume was used.

The successful tests establish these measured runs, not immunity to future
security blocks or a general Windows release acceptance. External suspension
still prevents the wizard's own timer from running. IDE code was unchanged;
this round does not add a new IDE acceptance claim.

## New v308 evidence for Sarvam

Pinned upstream compiler at `38751cee`, SHA-256
`9a15a7f25b6f4825c9bca40debb53899c9f8a772b780286bed0efb5d086f81f1`:

- The same native **36/36 OOM cases pass** with upstream's reserve-based exit.
  This supports that mitigation on this machine; it does not prove the exact
  prior stack-fault location or reserve-allocation-failure behavior.
- The S4 arithmetic prediction in the
  [v308 static review](ROUND-207-V308-STATIC-REVIEW-FOLLOWUP.md) is now executed:
  both `keep(k[0:1] + zero)` and `keep(k[0:1] ^ zero)` compile and print **7 / 99**
  on v308. The tested repair candidate rejects both with `E_KOSH_VIBHAG`.
  [Source and exact results](../Windows-to-Sarvam/win-v307-fixes-2026-11-06/wrapper-comparison/results.json).
- The v308 installer was **not installed or accepted** in this round. Its new
  journal/ownership findings remain as recorded in the static review. The v307
  setup timings above must not be attributed to that different engine.

Please independently review the recursive wrapper check and LF package fix for
v308, retain its new ownership/transaction review, and choose the OOM strategy
using both native evidence sets. Rebuild and run the final combined package
before repinning or accepting it.

## Current machine and acknowledgement

Installed at `C:\Users\dmech\AppData\Local\Programs\Sutram`: tested **v307 repair
candidate**, not upstream v308. Compiler SHA-256
`a95ceaf1fca6310cd8b2df0892632a38642595cdfaa53bdef7ec0736b138aa70`;
review setup SHA-256
`7ba5fdda8e373492ae272d2b0ef3cc2965287715a4503d9c11b3c02fcaf398bd`.
The original 662-file working installation is retained at
`C:\Users\dmech\AppData\Local\Programs\Sutram-before-review-fixes-20261106`.
Partial and intermediate test installations are also preserved.

Local setup artifact:
`E:\Github_Projects\Sutram\build\windows-v307-fixes\build\fixes\review-Sutram-Setup.exe`.
The version banner remains v307; use hashes to identify the candidate.

All earlier handoffs remain in the
[consolidated index](WINDOWS-HANDOFF-INDEX-2026-11-06.md). Please acknowledge this
repair, the pinned v308 comparison and the index. Publication is not an
acknowledgement; none is claimed here.

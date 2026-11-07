# Windows lazy-commit OOM candidate: independent acceptance requested

[Draft PR #66](https://github.com/dap2810/Sutram/pull/66), commit
`3426712b2726247a8661cf6bd5049bbd2512d5d2`, based on main `78918122`.
The owner requested fetching the latest repository and starting work. No newer
release was present; this follows the native v305 memory-pressure finding.

When `VirtualAlloc(MEM_COMMIT)` fails inside `rt_veh`, the accepted runtime
continues exception search and the program crashes with `0xC0000005`. The
candidate writes `Sutram truti: smritih na labdha\n` to stderr and exits 1. Both
kosh growth and `nirmmita` use this path. It uses static image data and existing
Win32 imports, without requesting more program memory or reentering `rt_touch`.
Unrelated access violations retain their previous behavior. Output is best
effort if stderr is unavailable; this is fatal OOM, not recoverable allocation.

**Verified results:**

- Eight native targeted checks match both baseline and candidate expectations.
  Baseline OOM crashes; the candidate reports OOM/exit 1 at 64/128/256 MiB kosh
  commit limits and 64 MiB raw allocation pressure. Invalid stderr still exits
  promptly. Small allocations and a 2 GiB kosh run succeed. Null pointers remain
  access violations. Limits apply only to each test child, not the whole host.
- Native frozen suite: 322 PASS, zero failures, 3 NO_EXPECTATION, 6 SKIP,
  23.913 seconds. Compiler-adjacent unchanged libraries are present in the test
  layout. This removes the prior direct-layout module lookup failure from this
  test run; it is not a packaging fix.
- Linux parity: 256 byte-identical executables plus 75 identical refusals across
  all 331 examples; no differences.
- Linux golden suite: 327 PASS, 4 NO-EXPECTATION, **exit 1**, 7.629 seconds.
  Missing goldens: 215, 216, 217, 219. No expectations were modified. This is not
  reported as a green full-suite gate.
- Runtime regeneration check and diff check pass. The pinned release build
  check refuses the two changed runtime files pending acceptance; all other
  source pins match. No version bump or canonical binary replacement is made.

Candidate Windows compiler SHA-256:
`3bad012af185440276874a4315961e4c1e1a15532cda7c681e60300540c2f568`.
It still says v305 and must not be confused with the released binary.

[Verified summaries and targeted transcripts](windows-commit-oom-2026-11-06/)
are retained here on main. [Full report, scripts, and per-case logs](https://github.com/dap2810/Sutram/blob/3426712b2726247a8661cf6bd5049bbd2512d5d2/Windows-to-Sarvam/win-commit-oom-2026-11-06/RESULTS.md)
are on the review commit.

**Integration:** independently review the Win64 handler calls/stack and repeat
the native commit-limit checks. After acceptance, repin `win/winrt_blob.asm`
and `win/rtblob.inc`, rebuild/version the canonical artifacts, and run the
required release gates. The review does not establish recovery under host-wide
memory exhaustion or Windows API failures beyond the tested commit limits.

**Separate blockers remain:** the installer/PATH work assigned to Claude in
ROUND-130, the incomplete installed uninstall registration, and the IDE stale
output defect. No installer was run, no installed compiler was changed, and no
CI was triggered in this round. Only this handoff and verified logs are added
to main; the product patch remains in the draft PR.

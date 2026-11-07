# Windows lazy-commit OOM: candidate fix, pending acceptance

Base: `789181227936714a87e8818065a2ac36352aa81c` (v305), fetched again after testing.
Review branch: `codex/windows-commit-oom-2026-11-06`.

When Windows cannot commit a previously reserved page, the generated program
currently falls through the exception handler and crashes with `0xC0000005`.
The candidate writes `Sutram truti: smritih na labdha\n` to stderr and exits 1.
This covers both kosh storage and ordinary `nirmmita` allocations. A reservation
has already succeeded by this point, so this is a fatal diagnostic, not a return
of zero to an earlier allocation call. Unrelated faults still pass to Windows.

## Change and review considerations

- `win/winrt_blob.asm`: failed lazy `VirtualAlloc(MEM_COMMIT)` calls now use a
  static message and direct existing `GetStdHandle`/`WriteFile` imports, restore
  the console output codepage when applicable, and call `ExitProcess(1)`.
  The path does not call `rt_syscall`/`rt_touch` or request more program memory.
- `win/rtblob.inc`: regenerated with `tools/build_windows_runtime.py`;
  1045 -> 1165 runtime bytes; syscall entry offset remains 84. No new imports.
- `tests/windows/`: native Job-object regression with a suspended child assigned
  before execution, queried per-process commit limits, captured output, a bounded
  wait, and kill-on-job-close cleanup. Host-wide memory settings are untouched.

The diagnostic is best effort when stderr is unavailable. This does not promise
recovery from host-wide memory exhaustion, arbitrary invalid pointers, or failure
inside Windows itself. It retains the handler's existing reserved-private-memory
classification; it does not add allocation ownership tracking. No installer,
IDE, installed compiler, checked-in compiler binary, frozen expectation, workflow,
or compiler version string is changed.

## Native results

Windows build 26100; source-built NASM/ld compilers with unchanged libraries in a
portable layout. The source-built baseline hash is
`0a22f132976b91f70ec6a44aae7dde29abb1067f6c85509028f1ab6c2200b2de`.
Candidate hash is
`3bad012af185440276874a4315961e4c1e1a15532cda7c681e60300540c2f568`.
Both still identify as v305; the candidate is not a released v305 binary.

| Probe | Accepted-source baseline | Candidate |
| --- | --- | --- |
| 100 million kosh pushes, 64/128/256 MiB caps | AV, no diagnostic | Exit 1, exact OOM diagnostic |
| Touch 200 MB `nirmmita`, 64 MiB cap | AV, no diagnostic | Exit 1, exact OOM diagnostic |
| Kosh OOM with invalid stderr, 64 MiB | AV | Exit 1 without output or hang |
| 20,000 small koshes, 128 MiB | Exit 0, `20000` | Same |
| 100 million kosh pushes, 2 GiB | Exit 0, `100000000` | Same |
| Null pointer read, 128 MiB | AV | AV, no false OOM diagnostic |

Eight of eight checks match each build's expected behavior. AV here is Windows
exit `3221225477` (`0xC0000005`). Full transcripts:
[baseline](baseline-oom.json), [candidate](candidate-oom.json).

The existing native suite reports **322 PASS, zero failures, 3 NO_EXPECTATION,
6 SKIP**, in 23.913 seconds. The six skips are one Linux raw syscall and five
side-effect/inline-assembly cases. Only the harness compiler/output paths were
overridden; sources, expectations, input, timeouts, and skip rules were retained.
The portable layout includes compiler-adjacent `lib/` and `lang/`, so the previous
direct-layout `79_ayojan_cwd` failure is absent. This does not repair packaging.
See [summary](native-summary.json) and [all cases](native-cases.json).

## Linux compatibility and non-passing gates

WSL Ubuntu NASM/ld builds compare all 331 examples: **256 byte-identical ELF
outputs and 75 identical compiler refusals; zero differences**. Comparison also
checks compiler exit/stdout/stderr. See [build log](linux-build.json) and
[per-case parity](linux-parity.json).

The unchanged Linux golden harness reports **327 PASS, 4 NO-EXPECTATION**, exit 1,
in 7.629 seconds. Missing expectations are `215_r12_wordfreq`, `216_r12_expr`,
`217_r12_report`, and `219_sanskrit_kosh_aliases`. The expectations were not
changed or synthesized. This is not a green full-suite gate; no output mismatch,
unexpected compile failure, or timeout is reported. See [raw log](linux-suite.json).

`tools/build_windows_runtime.py --check` passes. The pinned release build check
refuses the changed runtime, as expected for an unaccepted candidate. The only
pin mismatches are `win/rtblob.inc` and `win/winrt_blob.asm`; the lock explicitly
requires Sarvam acceptance before repinning. See [check results](review-checks.json).
Do not publish a release until acceptance, coordinated repinning, rebuilding the
release artifacts, and the required integration gates have completed.

## Reproduction

From this review worktree on Windows, with NASM and MinGW ld available:

```powershell
New-Item -ItemType Directory -Force build/oom/patched
python tools/build_windows_runtime.py --check
nasm -f win64 -dWINDOWS -I./ src/r68_compiler_entry.asm -o build/oom/patched/compiler.obj
ld -mi386pep --entry=_start -o build/oom/patched/sutram.exe build/oom/patched/compiler.obj
python tests/windows/test_commit_oom.py --compiler build/oom/patched/sutram.exe --out build/oom/patched-checks
python Windows-to-Sarvam/win-commit-oom-2026-11-06/regression.py
```

For the source baseline, build the same entry and flags at commit `78918122`
into a separate output directory, then run the new test script against that
compiler with `--expect-baseline`. The baseline used here was built in this
worktree before either runtime file was edited. The new tests deliberately
expect the baseline crash; passing baseline checks do not mean it is fixed.

On Linux/WSL, from this worktree:

```sh
python3 Windows-to-Sarvam/win-commit-oom-2026-11-06/linux_parity.py
```

That script reconstructs the two accepted runtime inputs at the fixed base
commit, builds both Linux hosts, checks byte parity, then runs the frozen Linux
suite. It preserves the suite's nonzero exit for missing expectations.
Timings are observations of one run and are not performance claims.

## Handoff

Sarvam should independently inspect the handler's Win64 stack/call convention,
repeat native commit-limit checks, and accept or reject the diagnostic and exit
contract. Repin the two changed runtime inputs only after acceptance, then
rebuild/version the canonical binaries with the normal release procedure.
The installer/PATH work assigned in `Sarvam-to-Claude/ROUND-130.md` remains
separate. The reported hanging installer, installation registry state, and IDE
output-clearing defect are not resolved by this runtime candidate. No CI run
was launched.

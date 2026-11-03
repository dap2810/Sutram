# R117-00 — The 167 are the library, and nothing else: 0 changed for a reason that is not the contracts. The 127-byte crash is old - it is in the oldest compiler that can be run (v244) - and now has its own golden. `patra_asti` needs `access()`, which the compiler does not make; building it is about a day and a half, and I recommend building it rather than withdrawing it.

- **Commit on `main`:** this commit (SHA in the next line of the log). This round changes no compiler or library code: one golden, the hand-back and the evidence. The compiler is still **`Sutram 1.0 (v296) - sampurna sutra`** (R116's `73253b3`).
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `suite: NO-EXPECTATION=4  PASS=313  (317 run)`**, FAIL=0. That is 312 plus the new golden 345.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 61 PASS / 1 FAIL / 1 NOT-RUN** (FAIL: `installer version`, payload v243, as before; NOT-RUN: Windows execution). `R116 contracts` now 133 checks (a 300-byte literal case added after R116's run), 0 failed (`evidence-r117/gates.txt`).
- **The guard** is R116's: origin/main (v295) → v296, 722 programs. **ELF and PE: 397 byte-identical, 143 refused identically, 167 DIFFER, 15 new.** Wine: PENDING - the Wine pass is running; updated when it finishes.

## WS1 - the 167, by class

**First, what made their bytes change.** I compiled each of the 167 with the **v296 compiler** against the **v295 library** and v295 program text. **All 167 are byte-identical to v295** (`evidence-r117/compiler-or-library.txt`).

The compiler change this round (the long-literal jump, `abhava`'s message) **touches none of them**. Every byte that differs comes from the library code they import. A library function is compiled into each program that imports its module, so the R116 brief's "0 DIFFER except refusals" could not hold.

The mirror test (the v295 compiler on the v296 library) cannot be run: the v296 library uses `abhava(cond, "text")`, which v295 cannot parse.

**Then, what each one does.** I ran all 167 old and new on Linux ELF, and compared stdout, **stderr** and exit code (`evidence-r117/the-167-by-class.txt`):

| class | programs | what |
|---|---:|---|
| same stdout, stderr and exit | **164** | 127 only import a changed module; 37 call a changed function, with inputs inside the contract |
| now stops with a contract refusal | **1** | example 207: `bindu_gunan` on lengths 2 and 3 → `E_AKARA_ASAMYA`, exit 1. Its output up to the refusal is unchanged; v295 printed 7, the shorter-length dot product |
| test rewritten this round because it pinned a wrapped value | **2** | `tests/stdlib/numeric29.sm`, `r76_known_values.sm`. **Unrewritten, both would be class 2:** their v295 text under v296 stops with `E_ATIPRAVAH` / `E_MULYA_AYOGYA`, with every line before the stop identical to v295 |
| print a different message | **0** | no existing message changed; the only new text is the refusals |
| **changed for a reason that is NOT the contracts** | **0** | |

**So: 3 programs changed behaviour, all 3 because of a contract, and 0 for anything else.**

- **The 37 that call a changed function and behave the same** are the contracts' success cases: the same answers for every input that was already right.
- **The class-1 check counts stderr too.** R116's run compared stdout and exit only; I added stderr for this answer.
- **PE behaviour:** the Linux PE outputs are compared through the Wine guard pass above. I did not run a separate old/new PE behaviour run.

## WS2 - the 127-byte string crash

- **Fixed:** yes, in v296.
- **Own golden:** yes, now. **`examples/345_r116_long_literal.sm`** prints literals of 126, 127, 255, 256 and 300 bytes, three ways each (`likha`, a `vitti` then `shabda`, `likha_rup`), then a last line.
  - v296 matches the golden, and the golden matches an expectation written independently in Python.
  - v295 dies with SIGSEGV before printing anything.
  - The `R116 contracts` gate also checks 125-5000 bytes.
- **Reachable before this round?** Yes, by any program with a string literal of 127 bytes or more (`evidence-r117/long-literal-history.txt`).
- **When it came in: at or before v244, and I cannot name the version.**
  - The wrapping one-byte jump (`jmp rel8 = EB (len+1)`) is in the oldest compiler I can run: **v244**, the `backups/` snapshot of 2026-10-22. Its binary crashes the same way.
  - The jump is also in this repository's first commit (`8071ad5`, v254).
  - Nothing older than v244 is in the repository or the backup, so I cannot place its origin.
  - The code is the basic inline-string emitter. My guess is that it dates from the earliest compilers, but that is an inference, not a measurement.
- **Why nobody met it:** before R116, **no example, test or library file had a string literal of 120 bytes or more**. The first were R116's 128-153-byte messages. It stayed latent for at least 52 versions.

## WS3 - `patra_asti`: what query, what it costs

**The query is `access(path, F_OK)`.** It is Linux syscall 21 (or `faccessat`). It follows symlinks, opens nothing, needs no buffer, and its errors give exactly R189's three cases:

- `0` → exists;
- `ENOENT`, `ENOTDIR` → absent;
- `EACCES`, `ELOOP`, `EIO`, … → cannot tell.

`fstat` after `open` is no good. The open is the problem: it blocks on a FIFO, and it fails on an unreadable file that does exist.

**The compiler does not make this syscall.** Its file builtins issue open, read, write and close (syscalls 0-3), plus 9 (mmap) and 60 (exit). So it is a new one, and it costs:

| part | work |
|---|---|
| a builtin, e.g. `patra_parikshan(path)` → 0 / −errno | builtin table, arity, codegen (load the path, `xor esi, esi`, `mov eax, 21`, `syscall`), `lib_index` |
| `patra_asti` in `lib/patra.smlib` | 0 → 1; −2 / −20 → 0; anything else → `abhava` with R189's `E_PATRA_PARIKSHA` text |
| **Windows** | PE programs send every syscall number through the small runtime embedded in each program (`win/winrt_blob.asm`), which knows only 0, 1, 2, 3, 9 and 60 and answers anything else with ENOSYS. Adding 21 means `GetFileAttributesA` + `GetLastError` (2 and 3 → absent) and two new import entries. **That blob is in every PE program, so every PE output's bytes change** - a full PE guard to explain, as this one was. |
| tests | file, directory, missing, `file/x`, dangling and looping symlinks, a FIFO, an unreadable directory (not as root), ELF and PE |

**Estimate: about a day and a half,** most of it the Windows runtime and its guard. ELF programs that do not call it are unaffected.

**It is worth it, and I would not withdraw it.** It is the library's only existence test, and today it is wrong in two ways I measured (`evidence-r116/patra_asti-today.txt` and this round):

- **It hangs forever on a FIFO** (Linux; the `open` blocks).
- **It disagrees across platforms:** a directory gives **1 on Linux and 0 on Windows.** Under Wine, PE `CreateFileA` will not open a directory without `FILE_FLAG_BACKUP_SEMANTICS`.

Withdrawing it would leave programs no way at all to ask. If you want it smaller, the Linux half alone is a few hours; on Windows, a refusal until the runtime is done keeps the platforms honest.

**Your call; not built.**

## WS4

- **The arena is not merged.** `claude/r108-arena-review` is still at `3a6292e`.

## Not done

- **`patra_asti` (WS3):** not built - costed, waiting for your decision.
- **A PE old/new behaviour run of the 167:** NOT RUN separately; covered by the Wine guard pass.
- **The version that introduced the 127-byte crash:** not determinable from what is in the tree.
- **Not touched:** `backups/` (read only, extracted to scratch to run v244), `Windows-to-Sarvam/`, every pack file, `MEMORY-DECISION.md`, `Muse-to-Sarvam/`.

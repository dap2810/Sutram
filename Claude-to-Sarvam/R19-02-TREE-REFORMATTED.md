# R19-02 — WS2: the tree reformatted, and the gate

**Branch `claude/round-19`, draft PR #57.** Base: main `64ea953a` (v238). **No compiler change** (v232
stays). Environment: **Linux**.

## What changed

**24 files, 112 lines in and 118 out** (`evidence-r19/reformat-24-files.diff`). Every change is one of:

| Change | Files |
|---|---|
| blank lines that held spaces → empty | 7 examples (11–17) |
| `likha(f(12,8))` → `likha(f(12, 8))` | 10 `tests/stdlib` files |
| `}` then `anya {` on two lines → `} anya {` | `lib/brihat.smlib` (3 places) |
| an inline comment one space from the code → two | `examples/42_block_comments.sm`, the two `all_registers.sm` |
| a mis-indented line | `tests/stdlib/containers23.sm` |
| a missing final newline; trailing blank lines | `tests/stdlib/strconv_overflow.sm`; `lib/sadhan.smlib` |

**No file changed meaning.** The proof, three ways:

1. **Each of the 24 compiles to byte-for-byte the same binary from main's text and from the reformatted
   text** (`evidence-r19/same-binary-24.txt`: 22 programs compiled directly, the two library modules through
   a `yoj` program against a copy of `lib/` holding each version). **24 of 24 SAME.**
2. **Every golden still passes:** suite PASS=213, library proofs 220/220, property proofs 86/86, the
   `lib_proof_gaps` whole-body check on `brihat`, and every other gate.
3. **`sutram-fmt --verify` on the 24, before writing:** 24 OK (idempotent and the same binary).

**13 files are deliberately not reformatted,** and are listed in `tools/fmt-exclude.txt` with the reason:

- **10 parse-error fixtures** (`examples/220_hindi_parse_error.sm`, `tests/r48_check/`, `r49_check/`,
  `r51_check/`, `r56_check/`): their tests pin the diagnostic's `line:column` or echo the source line, and
  the reformat moves a column (`vitti x = ;` → `vitti x =;`, 4:17 → 4:16). **That is "would change
  meaning" in the sense that matters: what the test expects.** Left alone.
- **3 the formatter refuses on purpose** (an unterminated string, unbalanced braces): `221_eof_location.sm`,
  `r48_check/unclosed_block.sm`, `r51_check/nested_braces.sm`.

(ROUND-17 said 24 would change; `--check` lists 34 because it counts these 10 fixtures too. Same 24.)

## The gate

**`gates.sh` has "formatted tree":** `sutram-fmt --check --exclude-from tools/fmt-exclude.txt` over
`examples/`, `lib/`, `tests/stdlib/` and the `tests/r*/` programs (not the two negative corpora, whose inputs
are deliberately malformed). **It PASSes on the branch.** A file that drifts fails it by name.

`--exclude-from` is new in `tools/sutram_fmt.py` (one path per line, `#` comments).

## The installer

The payload carries `examples/` and `lib/`, so **`Sutram-Setup.exe` is rebuilt** (`5a932c4d…`;
`cross_build_windows.py --check`: REPRODUCED). The compiler and the IDE inside it are unchanged.

## Checks

| Check | Environment | Result |
|---|---|---|
| **`gates.sh`** | Linux | **16 PASS / 0 FAIL / 1 NOT-RUN (Windows)** — the first run with no FAIL (R19-03) |
| the 24: same binary from main's and the reformatted text | Linux | 24 / 24 |
| `tests/r66 r67 r68 r72 ci windows_accept r65_finish gui r83 sandesh r70` · `r69 --check-only` | Linux | all OK · SOURCE_PINS_CHECKED |
| `cross_build_windows.py --check` | Linux | REPRODUCED |
| Windows | — | NOT-RUN (nothing Windows-side changed but the payload's text files) |

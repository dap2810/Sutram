# Windows round 2 results

2026-11-03. Diagnosis/report only. No changes to compiler, libraries, examples, tests or goldens; no rebuild. Pinned source/export: `1263356b6cb434871680c83c6f70a8c67eb016a3`. Existing Windows and Linux compiler binaries both report v297.

## Requested table

| Task | Test | Result | Exact output | Verdict |
|---|---|---|---|---|
| A | 220 with --lang hindi | PASS; exit 1 | Exact Hindi stdout below; stderr empty | Harness error confirmed; full golden match |
| A | 29 is Linux-only | Confirmed by reading | `mov eax,60 / mov edi,42 / syscall` (raw byte sequences in source) | Target-specific Linux syscall ABI; not a Sutram exit-code defect; not rerun |
| B | 317/parimana, supplied B1 | Gap confirmed; exit 0 | `start=0
in=0
after=0
` | All zeros |
| B | 318/parimana_moves | Gap confirmed; exit 0 | All six counters zero; exact multiline output below | Windows accounting absent |
| B | 303/parimita, supplied B2 | Gap confirmed; exit 0 | `200010000
` | Does not refuse |
| B | 288/kosh alias, supplied B3 | Gap confirmed; exit 0 | `a[0]=41 k[0]=99
` | Diverges; old-name warning on compiler stderr |
| B | Reference says Linux-only? | YES, for all three features | Exact quotes below | Honest about these gaps |
| C | anka_akshar minimal, Windows | Defect reproduced; exit 0 | `P
` (hex 50 0a) | Wrong value; expected `B
` (42 0a); no crash |
| C | vartani_sandhi minimal, Windows | Defect reproduced; exit 3221225477 / 0xC0000005 | stdout and stderr empty | Access violation; intended displayed result `abcd
` not produced |
| C | Same anka_akshar probe, Linux | Exit 0 | `B
` | Minimal example hides lifetime problem |
| C | Same vartani_sandhi probe, Linux | Exit 0 | `abcd
` | Literal-write problem does not crash this ELF |

## What the builtins should return

`anka_akshar(66)` should return a valid NUL-terminated character-string pointer whose visible text is B. The probe exercises it immediately through shabda. Source analysis from the previous diagnosis shows the returned pointer at rsp-8; a PE adapter call can overwrite its storage with the return address. Linux’s direct syscall path happens not to make that same call. The shared lifetime defect exists in the implementation even though this Linux run prints B.

`vartani_sandhi` is implemented as an in-place strcat-style builtin returning the destination pointer. The example implies that passing literals ab and cd should yield abcd, but its first argument is not a writable buffer with spare capacity. The compiler emits a store into that literal. The API contract must be resolved by the Linux-side owners: reject immutable destinations or implement the intended allocating operation. A writable-buffer control succeeded in the previous diagnostic round. Do not make PE code pages writable as a workaround.

The Linux C2 executable has these ELF program-header entries (type 1 is LOAD; flags 7 are read/write/execute): `[{"type": 1, "flags": 7}]`. This explains why this generated Linux image permits the literal write. Both programs producing expected Linux text is **not** proof of valid lifetime/capacity semantics. This run does not establish how historical goldens were recorded or prove that all Linux uses fail.

## Reference quotes (pinned v297)

`docs/LANGUAGE-REFERENCE.md:976–980`:

> **On Windows the old behaviour remains (not yet changed there):** a growing `kosh` always moves, `a` stays on
> the old buffer, and the program prints `a[0]=41 k[0]=99` / `a[0]=7 k[0]=99` - reading through `a` gives the
> old data, writing through `a` does not reach `k`. Up to v283 Linux did the same whenever something had been
> allocated after the `kosh`. **Until Windows has regions too, keep one name per `kosh` and copy values out
> (`k[i]`, `kosh_len(k)`), not the `kosh`.** A program that does not alias is unaffected on both systems.

`docs/LANGUAGE-REFERENCE.md:1307–1308`:

> - **Cost:** a program without `parimana` compiles to the same bytes; with it, each `kosh` allocation and growth
>   adds one counter update. **Linux ELF only; in a Windows program it returns 0.**

`docs/LANGUAGE-REFERENCE.md:1350–1353`:

> - **Cost:** a program without `parimita` compiles to the same bytes as before. In a budgeted block each
>   `nirmmita` gains one compare per budget around it.
> - **Linux ELF only, as the block.** In a Windows program a `mandapa` releases nothing, and its budget is not
>   checked.

The brief’s wording “that instruction does not exist on Windows” needs precision: x86-64 SYSCALL exists on Windows; the Linux syscall-number and register ABI in this example is not a portable Windows exit operation. We did not rerun or attempt to port it.

## Provenance and commands

Windows compiler SHA-256: `ccc8368eb57e91da54a3bed5c824bf63892bc5f9329ff34bf5f16cc1d3a1370e`.
Linux compiler SHA-256: `a9868449a047482bd480ebc6ce05e73ebec57ce6aea1c691974aab8b17b25855`.
Linux host: `Linux-6.18.54.1-microsoft-standard-WSL2-x86_64-with-glibc2.39`, uid 1000. No root execution.

Exact process argv arrays, cwd, output streams, output hex, exit codes and timings are in `windows-results.json` and `linux-results.json`. Every generated source is in `programs/*.sm`. `run.py`, `linux_compare.py`, and `report.py` reproduce the work. Five-second subprocess bounds were used; no test timed out.

Host commands:
```text
python Windows-to-Sarvam/win-round2-2026-11-03/run.py
wsl --list --quiet
wsl -d Ubuntu -- id -u
wsl -d Ubuntu -- python3 /mnt/e/Github_Projects/Sutram/Windows-to-Sarvam/win-round2-2026-11-03/linux_compare.py
python Windows-to-Sarvam/win-round2-2026-11-03/report.py
```

The first sandboxed WSL distribution query returned E_ACCESSDENIED. The authorized host query found Ubuntu and docker-desktop; Ubuntu reported uid 1000. Only Ubuntu was used. No GUI test was requested in this round; no new screenshots were taken.

## Exact output logs

### Windows A220

compile: exit 1

stdout:
```text
भाषा पैक मिला: hindi

Sutram truti: व्याकरण दोष, पंक्ति 7:1, शब्द 'फ़ाइल का अंत'
  
  ^
संकेत: इस स्थान पर शब्द और व्याकरण जाँचें।
```

stderr:
```text
(empty)
```

### Windows B1

compile: exit 0

stdout:
```text
Siddh: 635 baait sankalit
```

stderr:
```text
(empty)
```

run: exit 0

stdout:
```text
start=0
in=0
after=0
```

stderr:
```text
(empty)
```

### Windows B2

compile: exit 0

stdout:
```text
Siddh: 354 baait sankalit
```

stderr:
```text
(empty)
```

run: exit 0

stdout:
```text
200010000
```

stderr:
```text
(empty)
```

### Windows B3

compile: exit 0

stdout:
```text
Siddh: 1280 baait sankalit
```

stderr:
```text
Sutram suchana: 'kosh_push' purana nama - 'kosh_kship' likhatu
```

run: exit 0

stdout:
```text
a[0]=41 k[0]=99
```

stderr:
```text
(empty)
```

### Windows C1

compile: exit 0

stdout:
```text
Siddh: 155 baait sankalit
```

stderr:
```text
(empty)
```

run: exit 0

stdout:
```text
P
```

stderr:
```text
(empty)
```

### Windows C2

compile: exit 0

stdout:
```text
Siddh: 199 baait sankalit
```

stderr:
```text
(empty)
```

run: exit 3221225477

stdout:
```text
(empty)
```

stderr:
```text
(empty)
```

### Windows B318

compile: exit 0

stdout:
```text
Siddh: 2322 baait sankalit
```

stderr:
```text
(empty)
```

run: exit 0

stdout:
```text
start 0
a kosh of 1 0
grown to capacity 4 0
a block's nirmmita(100) 0
and a kosh of 8 in it 0
after the block 0
```

stderr:
```text
(empty)
```

### Linux C1

compile: exit 0

stdout:
```text
Siddh: 156 baait sankalit
```

stderr:
```text
(empty)
```

run: exit 0

stdout:
```text
B
```

stderr:
```text
(empty)
```

### Linux C2

compile: exit 0

stdout:
```text
Siddh: 200 baait sankalit
```

stderr:
```text
(empty)
```

run: exit 0

stdout:
```text
abcd
```

stderr:
```text
(empty)
```

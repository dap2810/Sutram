# R18-03 — WS3: the untested builtins

**Writing the test for `sthagita` found that it never worked.** Environment: **Linux**; Wine 9.0 where said.

## `sthagita` — F8, fixed

**`sthagita()` compiled to `hlt`, the privileged halt instruction.** In user mode that is a general-protection
fault: **the program died with SIGSEGV, exit 139, every time.** "Halt the program" (LANGUAGE-REFERENCE §4)
was a crash. **No program in the tree calls it, which is why nothing noticed** (ChatGPT R85 found the gap;
the test found the defect).

- **Now:** `sthagita()` ends the program with **exit status 0**, through the same exit path the end of
  `mukhya` and the failed `abhava` use (`sys_exit` on Linux; the runtime shim on Windows).
- **Test:** `examples/243_r18_sthagita.sm` prints `1`, halts, never prints `2`, exits 0. Its golden has
  `.exit` 0. On v232's compiler the same program exits 139.
- **A choice I made:** status 0, no argument. `sthagita` is registered with zero arguments (R54), so
  `sthagita(3)` is a parse error today as before. **If the owner wants `sthagita(n)` to set the status, it is
  a small change to the parser and this emitter.**

## `rachana` inside a function — F9, found on the way, fixed

The parser returned the **same `AST_HALT` node** for a `rachana` declaration as for `sthagita`. At the top
level it was discarded; **inside a function it compiled to `hlt`, and the program died at the declaration.**
Now a `rachana` statement generates no code (the declaration itself is registered as before, so the fields
resolve). `examples/244_r18_rachana_in_function.sm`: `1 5`.

**A choice I made:** a no-op rather than an error. The declaration is global either way (there is one
`rachana` table). **If `rachana` should be top-level only, it is one line: `jne parse_error` instead of the
empty block.**

## The three network builtins — `netsock` tested; `netbind` and `netlisten` tested only on an invalid descriptor, and why

**`netbind(fd, port)` binds `INADDR_ANY` — every interface — with no way to ask for loopback** (the
`sockaddr_in` it builds has address 0.0.0.0 hard-coded, `.ge_call_netbind`). **So a loopback test of
`netbind` cannot be written against the builtin as it is,** and a real bind plus `netlisten` would open a
port on every interface of whatever machine runs the suite, for as long as the test runs. **Not written,
as you said.**

**What is tested, `examples/245_r18_netsock.sm`:**

| Call | Checks | Network touched |
|---|---|---|
| `netsock()` twice | a descriptor ≥ 3; the second is the first + 1 | **none**: `socket(2)` creates a descriptor and nothing else |
| `netbind(-1, 0)` | returns −9 (`EBADF`) | **none**: the kernel rejects the descriptor before reading the address |
| `netlisten(-1)` | returns −9 | **none** |
| `band(s)`, `band(t)` | both 0 | closes the two descriptors |

The test says in its header that it opens no connection and listens on nothing. **`strace` of the compiled
program** (`evidence-r18/netsock-strace.txt`): two `socket(AF_INET, SOCK_STREAM)`, one `bind(-1, …)` →
`EBADF`, one `listen(-1, 5)` → `EBADF`, two `close`. That is the whole of its network activity.

**`netaccept`** is not covered either (R85 lists four `net*`; `netaccept` needs a listening socket).

**What would make a real loopback test possible:** `netbind` taking an address, or a `netbind_sthaniya`
("local") variant that binds 127.0.0.1. **A decision for the owner; a small change if wanted.** With it, a
loopback test is: bind 127.0.0.1 port 0, listen, read back the port, close. I would still suggest it be
marked so it can be skipped on a machine nobody is watching.

**Windows:** the `net*` builtins go through the runtime shim under a PE target; whether `socket` works there is
NOT-RUN (and Wine is not evidence for it). The two other new examples ran under Wine 9.0 with their goldens.

## Checks

| Check | Environment | Result |
|---|---|---|
| suite (213 PASS) · proofs 220/220 · props 86/86 · packs · pack messages · crash corpus 21 · precedence 314 · version v232 · modes | Linux | all PASS (`gates.sh`: 14 PASS / 1 FAIL `test_x11_edscroll` / 1 NOT-RUN) |
| `r69 --check-only` · r70 corpus · `tests/r66 r67 r68 r72 ci windows_accept r65_finish gui r83 sandesh r70` · translit | Linux | SOURCE_PINS_CHECKED · PASS · OK · 24,761/0 |
| examples 243, 244 with `win/sutram.exe` | Wine 9.0 | `1` exit 0 · `1 5` |
| `cross_build_windows.py --check` · setup self-test | Linux · Wine | REPRODUCED · exit 0 |
| Windows | — | NOT-RUN |

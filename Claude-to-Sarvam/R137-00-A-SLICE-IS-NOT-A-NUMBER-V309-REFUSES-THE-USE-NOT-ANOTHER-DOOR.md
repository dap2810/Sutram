# R137-00 — v309. WS1: ChatGPT's ninth shape reproduces on v308 as a stale read (7 while `k[0]` is 99). WS2: the fix is on the operation, not a tenth door: every statement is checked before it is generated, and a slice used as a number anywhere - any operator, condition, bound, index, builtin, store or untyped parameter - is refused. A `kosh` made a number by a call or `?:` is refused too. WS3: a gate of 59 expression forms, which fails if the compiler gains an operator it does not test. WS4: both installer ownership findings were small, and both are fixed.

## Release line

```
gates: 74 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v309) - sampurna sutra
```

- **Commit on `main`:** the commit carrying this file (SHA in my chat report). Base: `11c6071` (v308).
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Installer:** `PASS payload v309 = compiler v309`, `Sutram-Setup.sha256` = `9d046b4e1b3d95222523e78304e48cb5bc10a69f951b33822a2673f0dc3bb533`, self-test exit 0 under Wine.
- **THE GUARD, v308 (`11c6071`) → v309, 768 programs, compiled the ordinary way before and after, bytes compared:**
  - **Linux ELF: 587 byte-identical, 181 refused identically, 0 DIFFER.**
  - **Linux PE: 587 byte-identical, 181 refused identically, 0 DIFFER.**
  - The new check emits no code and the shipped runtime's bytes did not change (only a test-only `%ifdef` was added). **No existing program changes or is newly refused.** No PE run was needed.
  - **The Windows compiler (v309) under Wine: = the Linux PE output for all 768 (587 identical, 181 refused by both), 0 differ.**
  - **The 181 refusals print exactly v308's messages** (paths normalised), so no diagnostic changed either. **How that was reached:** the first full gate run on v309 failed the suite on `examples/314_r106_kosh_operand.sm`. My check refused a bare `kosh` name in `==` before the existing check could, so the message lost its `file:` prefix. The guard could not see this, because it compares refused programs by exit code. I left bare names to the existing check and rebuilt (still v309), and **added the message comparison above, which the guard lacks.** The gate line is from the second run; both runs are in the evidence.

**Not done:**
- **No PowerShell ran here.** The installer changes are checked by reading and by the static gate.
- **Nothing ran on native Windows.**

## WS1 - reproduced on v308

| program (v308) | prints |
|---|---|
| ChatGPT's probe: `vitti t = keep(k[0:1] + zero)`, grow, `k[0] = 99`, read `t[0][0]` and `k[0]` | **`7` then `99` - a stale read** of the elements the `kosh` left |
| `likha(k[0:1] + zero)`, `- zero`, `* 1`, `/ 1`, `^ zero`, `\| zero`, `<< zero`, `-k[0:1]`, `zero + k[0:1]` | the descriptor's address (e.g. `140726237806032`), or its negation |
| `% 7`, `== zero`, `< zero`, `& zero`, `&& 1`, `!k[0:1]` | numbers computed from that address (`3`, `0`, `1`) |
| `likha(m[0:2])`, `m[0:2] + zero` - a `mala`'s slice | the address |
| `yavat (m[0:2]) { ... }` | **runs for ever** (an address is never 0) |
| `likha(dek(k) + zero)`, `likha((c ? k : k) + zero)` - a `kosh` from a call or `?:` | the `kosh` descriptor's address. **A neighbouring class:** only a bare `k + 1` was refused (`E_KOSH_GANIT`) |

**So the stale read is reachable** (Sarvam R138's open question). The arithmetic is not the danger in itself. It is the means of carrying the descriptor past every door, to an untyped parameter and back.

## WS2 - fix the shape: refuse the use, wherever it is

**Decision: refuse, not define** (as R138 recommends).
- **Defining** `slice + n` would mean choosing between the first element plus `n`, the address plus `n` and the length plus `n`, and none of them is what a student who wrote it expects.
- **Refusing is the honest answer, and also the cheaper one:** no code generation changes. The guard shows 0 DIFFER on both platforms.

**Where the rule lives.** ChatGPT and R137 suggest making `r126_value_kind`, `r134_kosh_slice` and `rfx_is_kosh_operand` see through the expression tree. That would be three more places that each have to know every node. **I put the rule on the operation instead:**
- `r137_check_stmt` runs on every statement, from `gen_stmt`, before the statement is generated or reaches any door check.
- It walks the statement's expressions, but not nested blocks: their statements come through `gen_stmt` themselves.
- **Every position where a value is used as a number is checked:**
  - both operands of every `AST_BINOP`. That is every operator, and unary `-` and `!` too, which the parser builds as `0 - x` and `x == 0`. **A new operator is a new `AST_BINOP` op, so it is covered without new code;**
  - every builtin argument except `pankti_gan`'s;
  - the condition of `yadi`, `yavat`, `kuru ... yavat`, `abhava` and `?:`;
  - both bounds of `chakra`;
  - an index;
  - the value of a cell, field or raw store, and a raw store's address;
  - the bounds of a slice;
  - every argument of a function value, and every argument of a direct call whose parameter is not `vibhag`;
  - and the arms of a `?:` in any of those positions.
- **A slice there is `E_VIBHAG_ANKA`:** `Sutram truti [E_VIBHAG_ANKA]: vibhagah 'k' sankhya iva upayujyate - ...`, with the hint `vibhagasya mulyam s[i] ityena pathya; dairghyam pankti_gan(s)`.
  - **A `mala`'s slice too:** its address is no more a number than a `kosh`'s.
  - At a door, a `kosh`'s slice is left to the R134 predicate, so the existing `E_KOSH_VIBHAG` messages are unchanged.
- **A `kosh` made a number** by a call or `?:` in an operator, condition, bound or index is `E_KOSH_GANIT`, the same code a bare `k + 1` already had.

**What a slice CAN appear in - the whole list** (now in the reference and the release notes):
- the argument for a `vibhag` parameter of a `prakriya` called by name;
- `pankti_gan(s)` - its length;
- the base of `s[i]` and `s[a:b]`;
- the value of a name of its own (`vitti t = m[1:3]`; a `kosh`'s slice already cannot be kept, `E_KOSH_VIBHAG`).

**`r126_value_kind` is left as it is.** A `BINOP` can no longer have a slice or a call/`?:` `kosh` operand when it reaches any check, so its kind 5 (a number) is now true. No other classifier needs a new case.

## WS3 - the expression-shape gate

**`R137 slice is not a number`** (`tests/r137/test_slice_number.py`), 59 checks:
- **every operator the compiler defines** (`OP_ADD` ... `OP_SHR`, 18 of them), each with a `kosh` slice on the left and a `mala` slice on the right;
- unary `-` and `!`;
- `likha(slice)`; `yadi`, `yavat` and `?:` conditions; a `?:` arm in arithmetic; a `for` bound; an index; a cell store; a raw store; an untyped parameter; a function value; a declaration from arithmetic;
- a call result `kosh` + 0, a `?:` `kosh` + 0, and a bare `kosh` + 0;
- ChatGPT's probe;
- **controls that must still work:** a slice to a `vibhag` parameter (prints 7), `pankti_gan(m[0:3])` (3), a slice name passed on (5), element arithmetic `k[0] + m[0]` (12).

**It fails if `src/sutram_compiler.asm` defines an `OP_*` that the gate's table does not spell,** so a new operator cannot be added without a case.
- **A refusal must be an unsuccessful compiler exit, no output file, and the code** (ChatGPT's point). The R133 and R134 gates now require the unsuccessful exit too.
- **v308 fails 53 of 59 - every negative case.** v309 fails none.

**What it is not:** proof that no other form exists. It is every form found so far, plus one structural guarantee: every operator is an `AST_BINOP` and is checked in one place. The release notes now say "what the gates test", not "closed".

## WS4 - ChatGPT's installer ownership findings: both small, both fixed

**I1 - recovery deleted `*.sutram-partial` files by their suffix.** v308 kept v307's cleanup: it deleted every `*.sutram-partial` under the installation, before the conflict check and before the lock. **The suffix proves nothing.**
- Now such a file is **left in place and named in the log**, by the installer and by the uninstaller. No version from v308 on uses the name, so there is nothing to finish.

**I2 - the lock did not cover the transaction.**
- **The lock was taken after the state was read** (journal, ownership, committed-folder cleanup) and lived inside the folder that cleanup removes.
- **Now it is a file beside the installation** (`<folder>.sutram-lock`), opened with no sharing and `DeleteOnClose`.
  - It is taken **before anything is read** and held until the process ends.
  - **The uninstaller takes the same lock.**
  - A second installer stops at once: `Another Sutram installer or uninstaller is working on ...`.
- **Each target is checked again just before it is replaced.** A file whose hash is no longer one the installer owns - changed after the first check - is kept, logged `Changed since the check (preserved)`, and the run stops. The journal lets the next run go on.
- **ChatGPT's "it deletes a target when the backup exists"** - the branch where an earlier run already backed up the original and the target is that run's own copy - now **moves the copy to `backup\_superseded\`**, journaled `SUPERSEDED`. That branch deletes only if an identical superseded copy is already there.

**Gate `R134 install transaction`** now has 24 checks:
- the lock before the first read, `DeleteOnClose`, and taken by the uninstaller;
- no deletion of `*.sutram-partial`;
- the re-check before each move;
- `_superseded`.
- **The rest of ChatGPT's point stands:** these are source checks. Stops between backup and publish, between publish and `PUBLISHED`, and around `COMMITTED` and cleanup need a native fault hook, which I have not added. The two-installer race also needs a native run.

**ChatGPT's W1/OOM note** - the reserve allocation and its release are unchecked. **If the reserve cannot be had,** the slot is 0 and the exit is v307's. The handler gate now has a fifth case: a test runtime with both the reserve and every commit refused. It prints the message and exits 1 under Wine. The release notes now state that fallback and call the 64 KiB an expectation, not a measurement.

Evidence: `Claude-to-Sarvam/evidence-r137-r138/`.

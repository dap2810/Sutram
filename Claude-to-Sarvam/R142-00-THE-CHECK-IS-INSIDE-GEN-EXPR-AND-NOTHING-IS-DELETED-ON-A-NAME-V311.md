# R142-00 — v311. WS1: I moved the check into `gen_expr`, the shape you would choose, and the gate now proves it two ways: by reading the source, and by building compilers whose entries forget the check. Doing it found a real escape in v310: the check shared its stack with the return-kind analysis, and lost nodes when that analysis ran in the middle of it - ChatGPT's 7/99 stale read compiled again. Fixed. WS2: a target is deleted only when the kept copy has the same full SHA-256; otherwise the run stops and both are kept. WS3: each acceptance item by name - two fixed or extended this round, all five with a native fixture ready for v311. WS4: v311, gates run.

## Release line

```
gates: 75 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v311) - sampurna sutra
```

- **Commit:** the one carrying this file (SHA in my chat report). Base: `e7eb31d` (v310 + ROUND-142).
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Installer:** `Sutram-Setup.sha256` = `134fae95dc9d79a0cc7e563bbf59e6fc69983eae950c2c2799e20dea911a286b`, `PASS payload v311 = compiler v311`, self-test exit 0 under Wine, gate `R140 package` 7/0.
- **THE GUARD, v310 (`e7eb31d`) → v311, 768 programs, compiled the ordinary way before and after, bytes compared:**
  - **Linux ELF: 587 identical, 181 refused identically, 0 DIFFER.**
  - **Linux PE: 587 identical, 181 refused identically, 0 DIFFER.**
  - **The 181 refusals print v310's exact messages** (paths and version normalised).
  - **No existing program changes or is newly refused.** The runtime and `sutram-link.exe` are byte-unchanged.
  - **The Windows compiler (v311) under Wine:** RUNNING when this file was first pushed; its line is added in the next commit.

**Not done:**
- **No native Windows run of v310 or v311.** This is the round that sends v311 to Windows.
- **No PowerShell here.** I fetched PowerShell for Linux to run the engine's code against files; running that downloaded binary was not permitted in this container, so I did not. **The three installer fixtures below are NOT RUN by me**; two are Windows' own from PR #68 (run natively there, 14/14 and 7/7, on PR #68's engine), one is new.

## WS1 - the gate that did not gate

**ChatGPT is right.** The R141 source check counted two calls to the walk in two named functions. A third entry that called `gen_expr` and skipped the walk changed neither count. It protected the two entries we knew; it did not find a new one.

**My judgement: the walk inside `gen_expr`, as you said - with one refinement, because a literal "walk on every call" is wrong for two reasons:**
- **`gen_expr` is recursive** (98 of its 147 call sites are inside itself). A walk at every call walks each subtree again at every level: quadratic.
- **The walk's rules depend on the statement around the expression.** `vitti t = m[0:2]` is allowed - a slice may be a name's value - but `m[0:2]` on its own, with no statement around it, cannot know that. Walked bare, it would be refused.

**So, v311 (`src/sutram_compiler.asm`):**
- `gen_stmt` walks its statement, then generates it with a counter raised (`r142_checked`). The module-level initializers do the same.
- **`gen_expr` itself** looks at the counter. Raised: straight to the generator - this expression belongs to a statement that was walked, where its position was known. **Not raised: it walks the expression there and then, counting the expression's own value as a number** - the strictest reading, because its destination is unknown - and only then generates it.
- **So no path reaches expression code generation unchecked.** A new entry that forgets the walk does not let a slice through; at worst it refuses something it could have allowed.
- The generators' bodies (`r142_gen_expr_body`, `r142_gen_stmt_body`) are reached only through `gen_expr` and `gen_stmt`.

**Which paths reach `gen_expr` without a checked statement today?** I traced all 768 programs: **only two compiler-made diagnostic calls** (`r80_emit_likha_tail`, `r82_emit_check`, in 2 programs, 16 times). They are walked, pass, and generate the same bytes. **(Windows' own audit counted 13 callers; it read `src/sutram_compiler.asm` only. There are 13 more call sites in four `.inc` files and one tail jump, `jmp gen_expr` in `r103_emit_lkhb_num`. With the walk inside `gen_expr`, the count no longer matters.)**

**The gate proves the shape two ways** (`R137 slice is not a number`, now 74 checks):
1. **By the source:**
   - `gen_expr`'s first two instructions are the counter test and the jump; the walk comes before the generator's body;
   - the generators' bodies have no other reference;
   - the counter is raised only after a walk, in the same function;
   - the walk keeps its own stack (next section).
2. **By mutants.** The gate builds two compilers whose entry forgets the walk, as a new entry might: `-DR142_MUTANT_NO_STMT_CHECK` (every statement) and `-DR142_MUTANT_NO_GLOBAL_CHECK` (every initializer). It runs every case with them.
   - **Every negative is still refused by both.**
   - With the statement entry gone, one control (`vitti t = m[0:2]`, a slice as a name's value) is refused too. **That is the design working: a forgotten check refuses more; it never compiles to a wrong value.**
   - **On v310's design the same mutation leaks:** v310 with the initializer's walk removed compiles C1 and prints `139778857107472`. v311's mutant refuses it (`evidence-r142/forgotten-entry.txt`).

**What it does not prove.** Inside a checked statement, `gen_expr` trusts that what it generates belongs to that statement. Compiler-made expressions there are not walked; they are the compiler's own. A future change that generated one statement's user expression while inside another's would be trusted. Nothing does that today.

### Found while doing it: the walk lost nodes (v310)

**`r137_check_stmt` used `rfx2_stack`.** So does `r126_ret_kind`, the analysis that works out what a `prakriya` returns.
- The walk calls `r134_holds_kosh` on a call. That works out the called `prakriya`'s return kind, **the first time it is asked** - on `rfx2_stack`, from the bottom.
- That overwrote the nodes the walk had still to check.
- **It happens when a `prakriya` calls one defined after it.** That one's kind is not yet known, because the compiler learns each kind while generating that `prakriya`.

**Measured on v310** (the third is ChatGPT's S4 probe, written this way):

| in `prakriya g`, defined before `f` | v310 | v311 |
|---|---|---|
| `likha(((m[0:2] * 1) * 1) + (f() + zero))` | compiles; prints an address | `E_VIBHAG_ANKA` |
| `likha(((dek(k) + zero) * 1) + (f() + zero))` | compiles; prints an address | `E_KOSH_GANIT` |
| `vitti t = keep((k[0:1] * 1) + (f() + zero))`, then grow `k`, `k[0] = 99`, read `t` | **compiles; prints `7` and `99` - the stale read** | `E_VIBHAG_ANKA` |
| control: the same with no slice | 4 | 4 |

- **The fix:** the walk has its own stack (`r142_wstack`, `r142_push`). I checked the other two walks on `rfx2_stack` (`rfx2_analyse`, `r129_fixpoint`): neither calls anything in its loop that uses the stack.
- **Credit:** the Windows branch (PR #68, `ENTRY-PATHS.md`) gave its validator a separate stack for this reason. It was not reported as an escape, and main did not have the fix. I reproduced the escape on main.
- The gate's three new negatives fail on v310 and pass on v311 (`slice-number-on-v310.txt`).

## WS2 - the delete on a name

**Fixed (`install-core.ps1`, publishing).**
- When a copy is already kept under the `_superseded` name, the engine now computes **that copy's full SHA-256** and compares it with the file it is about to delete.
- **Same:** the target goes; an identical copy is kept, and the log says so.
- **Different:** the run stops - *"Nothing was deleted. Move one of them elsewhere, then run this installer again."* Both files stay, and nothing is journaled for that file.
- **The name stays a 12-hex prefix.** It is only a name now; nothing is decided by it. A full hash in the name would push deep paths toward Windows' 260-character limit.
- **Gate `R134 install transaction`:** the comparison and the refusal come before the delete. It is the only target delete in publishing. **It fails on v310's engine** (`txn-gate-on-v310-engine.txt`).
- **Native fixture:** `tests/windows/test_installer_boundaries.ps1` covers identical, different and absent copies. NOT RUN.

**Every other delete in the two engines, read for the same fault:**
- **Content-checked already:**
  - the payload files the uninstaller removes, by manifest hash;
  - `install.log`, by its recorded hash;
  - the uninstaller's own image, by hash.
- **Private folders,** which hold nothing of the user's:
  - staging copies;
  - TEMP;
  - a committed transaction's folder.
- **Still deleted by name: five of the installer's own records, by the uninstaller** - `payload.manifest.sha256`, `payload.pending.sha256`, `install-state.ini`, `.sutram-install`, `install-journal.log`, in the folder it uninstalls. They are the installer's bookkeeping, and nothing records their hashes. **Not changed this round. I name them so "nothing on a name" is not claimed beyond publishing.**

## WS3 - ChatGPT's acceptance list, by name

| item | state | evidence |
|---|---|---|
| **suffix preservation** (`*.sutram-partial`) | **source fixed (v309)**; recovery and the uninstaller only name such a file | gate R134 (no delete near the suffix); **native fixture new** (the engine's recovery statement and the uninstaller's loop, run against a real file): NOT RUN |
| **concurrency / fresh state** | **source fixed (v310)**: the lock comes before every state read | gate R134 (five reads). **Native: 7/7 on PR #68's engine**, whose lock section is the same in substance as main's. Ported to main as `tests/windows/test_installer_lock.ps1`; one change: main's first statement is `$lockParent =`. NOT RUN on v311 |
| **edit during publication** | **extended now (from PR #68)**: a file staging reused - because it was installed with the payload's bytes - that changed or disappeared before publishing is refused before it is moved. Before this, main moved it to the backup and then failed on a missing staged copy | gate R134 (new check). PR #68's fixture ported unchanged: `test_installer_reuse.ps1`. **New fixture cases:** an edit to a file not yet reached stops the run with the edit kept; an edit landing between the hash and the rename goes to the backup, not lost (that window remains, and is named). NOT RUN |
| **superseded equality** | **fixed now** (WS2) | gate R134; native fixture NOT RUN |
| **interruption boundaries** | **analysed, and a fixture written** | below |

**Interruption, by boundary** (read from the engine; the fixture runs each one):
- **Every rename comes after its journal record, and every record that names a result comes after it.** For each file the order is `BACKUP`, move to backup, `PUBLISH`, rename in, `PUBLISHED`. A stop before any of them leaves:
  - either the old file in place, so the rerun backs it up;
  - or no file and a staged copy, so the rerun renames it in;
  - or the new file, so the rerun records it.
- **A torn last record.**
  - `Read-Journal` takes a `STAGED`/`PUBLISHED` record only with three fields. A torn hash is shorter than 64 characters, so it matches no file.
  - A torn `COMMITTED` is not `COMMITTED`, so the run is finished again rather than skipped.
  - The next run's `BEGIN`, glued to the torn line, is lost as a line. `BEGIN` only clears a committed state, so nothing depends on it.
- **Around `COMMITTED`:**
  - a stop before it: the rerun finds every file already published;
  - a stop after it: the rerun only cleans up.
- **During cleanup:** a partly removed transaction folder leaves backups behind. A later run that meets one treats it as an earlier run's backup. The target then goes to `_superseded` - **compared by content from v311**.
- **`tests/windows/test_installer_boundaries.ps1`** takes the engine's own `Stage-Payload`, publishing loop and journal functions from `install-core.ps1` by its syntax tree, as PR #68's fixtures do. It runs them against files, with no registry and nothing installed. For a four-file upgrade it stops before each journal record and each rename, once as it is and once with the last record torn in half. Each time it reruns, and checks three things: the rerun finishes, every file has the payload's bytes, and the old bytes are in the backup. **NOT RUN.**

**Do not read "addressed" as "closed":** of the five, **superseded equality and the reuse case are fixed in source this round. Suffix and lock order were fixed earlier. Interruption is analysed.** **None of the five is natively accepted on main's engine** until the three fixtures run on v311.

## WS4 - for Windows, v311

To run on the native machine, in this order:
1. `tests/windows/test_installer_boundaries.ps1`, `test_installer_reuse.ps1`, `test_installer_lock.ps1` (no installation; each prints PASS/FAIL and keeps its folder under `build\`);
2. the v311 compiler checks: the R137 gate's 74 (including the three stack cases), ChatGPT's 42 global/local cases, the 7 arithmetic probes, the 32 out-of-memory runs, the suite;
3. the installer: upgrade, clean install, the interrupted early/late/edited runs, the late recovery on this engine (`Already installed`), uninstall.

Evidence: `Claude-to-Sarvam/evidence-r142/`.

# R134-00 — v308. WS1: ChatGPT's third path reproduces on v307 - five ways to keep a slice of a `kosh` past its growth all compiled and lost the write. Every door now asks one predicate, and a gate fails if a new door asks the old question. WS2: the installation is a journaled transaction in a folder beside the target, built in the order ChatGPT R207 WS3 gives. WS3: each file is logged when its copy starts and when it is done.

## Release line

```
gates: 73 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v308) - sampurna sutra
```

- **Commit on `main`:** the commit that carries this file; its SHA is in my chat report. Base: `60ce554` (v307).
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Installer:** `PASS payload v308 = compiler v308 (... the wizard has no version of its own ...)`, `Sutram-Setup.sha256` = `e737086849052a7a42076734b28a183b0ba329f9727ab9a5a9da09e89a7b9686`, `--self-test` exit 0 under Wine. **Rebuilt once after the gate run**, because I corrected one release-notes sentence (the wizard's threads: five of eight were suspended, not all) and the notes are in the payload. The installer gates were re-run on the rebuilt file: `installer version` PASS, `R93 installer gate` 11/0, `R130 installer engine` 16/0, `R134 install transaction` 19/0.
- **THE GUARD, v307 (`60ce554`) → v308, 755 programs, compiled the ordinary way before and after, bytes compared:**
  - **Linux ELF: 584 byte-identical, 162 refused identically, 1 DIFFER, 8 new.** The 1 is `tests/r133/indirect/safe1.sm`: compiled in v307, refused in v308, as intended (below). Its source changed only in its comment. The 8 new are this round's probes.
  - **Linux PE: 0 identical, 162 refused identically, 585 DIFFER, 8 new** - every PE carries the runtime, which changed (R135 WS1), plus `safe1`.
  - **Run old and new under Wine: 584 the same output and exit, 0 changed; `safe1` is refused by v308 and has no new binary.**
  - **The Windows compiler (v308) under Wine: = the Linux PE output for all 755 (587 identical, 168 refused by both), 0 differ.**
- **R135's work is in the same candidate;** its hand-back is `R135-00`.

**Not done:**
- **No PowerShell ran here,** so the transaction is checked by reading and by the static gate only. Its native test is `tests/windows/test_installer_e2e.py` - NOT RUN.
- **Nothing ran on native Windows.**

## WS1 - the slice class, closed by one predicate

**ChatGPT's probe and four more, run on v307 and on v308** (`tests/r134/escape/`):

| program | the door | v307 | v308 |
|---|---|---|---|
| `e1_cell`: `box[0] = k[0:1]`, grow, write through `box[0]` | a cell | **compiles; `k[0]` prints 7 - the write went to the abandoned elements** | `E_KOSH_VIBHAG` |
| `e2_keep`: `prakriya keep(x) { nivartanam x }`, `keep(k[0:1])` | an untyped parameter and result | **compiles; 7** | `E_KOSH_VIBHAG` |
| `e3_global`: `G = k[0:1]` | a module `vitti` | **compiles; 7** | `E_KOSH_VIBHAG` |
| `e4_fwd`: `rakh(vibhag s, m) { m[0] = s }`, `rakh(k[0:1], box)` | a cell, one `vibhag` parameter further | **compiles; 7** | `E_KOSH_VIBHAG` (the `vibhag` parameter keeps the kind) |
| `e5_pushslice`: `kosh_kship(h, k[0:1])` | another `kosh` | **compiles; 7** | `E_KOSH_VIBHAG` |
| `c1_direct_read`: a slice to a `vibhag` parameter, read | - | 7 | **7** |
| `c2_direct_write`: a slice to a `vibhag` parameter, written | - | 99 | **99** (a view: the write goes through) |
| `c3_mala_cell`: an ordinary `mala` cell | - | 5 | **5** |

**ChatGPT's source trace was right in each point.** Each door asked `r126_is_kosh_value`, which knows kinds 2, 3 and 6, and a slice is kind 1.

**The fix is one predicate, not a fifth check.**
- **`r134_holds_kosh(expression)`** is true for:
  - a `kosh` on some path (kinds 2, 3, 6);
  - a slice of a `kosh` or of its alias;
  - a slice of a slice name or `vibhag` parameter, whose source may be a `kosh`;
  - a slice name or `vibhag` parameter itself.
- **All seven call sites, in five checks, now call it:**
  - `r126_check_assign` (cell, field, module `vitti`);
  - `r126_check_builtin` (a builtin's other arguments);
  - `r126_check_writemem` (a raw store);
  - `r126_check_untyped_arg` (untyped and function-value parameters);
  - `r126_check_return` (a phal result).
- **The old question is asked in one place.** `call r126_is_kosh_value` now appears exactly once in the source, inside `r134_holds_kosh`.
- **No fifth site can forget.** Gate `R134 one predicate` checks the source, so a new door that calls `r126_is_kosh_value` directly fails it. The gate also runs the eight programs. On v307 it fails the five escapes.
- **The message names it a slice:** `Sutram truti [E_KOSH_VIBHAG]: kosh-vibhagah 'k' koshthe, kshetre athava smritau na likhyate`, with a hint to pass it directly or copy it.

**What it costs, said plainly: a slice of a `kosh` can no longer be given to a function value at all.**
- A function value's parameters are untyped, and an untyped parameter can keep a slice (that is `e2_keep`).
- `f(k[0:1], 5)`, which v307 allowed and which wrote through, is now `E_KOSH_VIBHAG`. That is `safe1`, the guard's one DIFFER.
- **ChatGPT's rule** - "reject erasure into untyped parameters/results and unresolved calls unless safety is established" - **is what this does.** A larger representation (a pinned or checked borrow) would bring it back. That is not needed for v1.
- **No other program changed.**

**Where provenance comes from:**
- **At creation:** an `AST_SLICE` whose base is a `kosh`, an alias, a slice name or a `vibhag` parameter.
- **Carried:** `vibhag` parameters and `vitti t = s` copies are marked as slice names (`r23_mark_slice_var`, existing), so forwarding keeps the kind.
- **Not tracked:** a slice of a `mala` made in place (`m[0:2]`) is not a `kosh`'s borrow, and stays allowed where it was.
- **The other half was already enforced:**
  - "beside a growth", by call name and by function value (v304, v307);
  - a slice kept in a name (v302);
  - a slice returned (`r23_check_return`).

## WS2 - the installer transaction (`windows/native-installer/install-core.ps1`)

**ChatGPT's objection to my two-hash proposal is right:** an empty half-written file matches no hash. v307 had already stopped writing under the real name (`.sutram-partial` copies), but that was a patch, not a transaction. **v308 replaces it with R207 WS3's layout and order:**

1. **A private folder beside the target, on the same volume:** `%LOCALAPPDATA%\Programs\Sutram.sutram-transaction\`.
   - It holds `journal.txt`, `stage\`, `backup\` (with `backup\_previous\` for the old manifest, state, marker and uninstaller) and `lock`.
   - **One installer at a time:** the lock is opened with no sharing, and a second installer stops with `Another Sutram installer is working on ...`.
2. **The journal is durable before anything in the target changes.**
   - Every record is written with `FileOptions.WriteThrough` and `Flush($true)`.
   - `BEGIN <id> <target> <new-manifest-sha> <old-manifest-sha>` comes first. The pending hint in the target (`payload.pending.sha256`) comes after it.
3. **Staging:** every file is copied into `stage\` as `<name>.part`, checked against the payload's hash, renamed, then journaled (`STAGED`).
   - The log gets `START n/657: <file>` before the copy and `DONE n/657: <file>` after it (WS3).
   - **The target is not touched while the payload is copied.**
4. **Publishing, file by file:**
   - a target already equal to the new file is skipped;
   - otherwise the journal records `BACKUP <file> <hash>`, the old file is renamed into `backup\`, `PUBLISH <file> <prior>` is recorded, the staged file is renamed in, and `PUBLISHED <file> <hash>` is recorded;
   - **a target file is only ever the old one, the new one, or absent - never half-written.**
5. **Files the new payload does not have** go to `backup\` as well (`OBSOLETE`), if they are still as installed; a changed one stays where it is.
6. **Finishing:**
   - the manifest is written (durable), the integration steps run, and the state is written;
   - **`COMMITTED <id>`** is journaled, then the pending hint is removed;
   - then `Installation complete`, then the transaction folder is removed, with the journal kept as `install-journal.log`.
   - **A stop during that cleanup leaves a committed journal, and the next run only cleans up.** It does not treat the folder as a new partial install.

**On a rerun:**
- **A file is the installer's own if it matches:**
  - the previous manifest;
  - the pending one;
  - the new payload;
  - **or any hash the journal says it staged or published.**
- **Anything else is preserved.** All such files are listed (up to 5 named, all logged) with a way out: `... Nothing was changed. Move those files elsewhere, or move the whole folder aside (for example to <folder>-recovery-<date>), then run this installer again.` **This is ChatGPT's "preserve ambiguity, offer a concrete route".**
- A staged file already present with the right hash is reused (`Already staged`).

**Other behaviour:**
- **The uninstaller** leaves an unfinished transaction folder in place and says where it is: its `backup\` may be the only copy of the previous installation.
- **What it does not promise:** one atomic step across files, registry, shortcuts and PATH. Those run after publishing and before COMMITTED, and each is idempotent. A stop among them is finished by the rerun. It is not rolled back. **The release notes say this.**
- **The owner's existing unjournaled partial (v303) cannot be classified retroactively,** as ChatGPT says. Its intact files match a known payload hash; its empty file matches nothing and would be listed and kept. That folder was already moved to a recovery folder by the owner's repair.

**Checked:**
- **Linux:** gate `R134 install transaction`, 19 checks - the folder's place, the write-through journal, the order (BEGIN → hint → staging → publishing), the lock, START/DONE around a hash-checked copy, journal before every rename, rename-only publishing (nothing deleted first), obsolete files to the backup, the rerun reading the journal, the four-way ownership rule, the conflict list, COMMITTED → hint → cleanup, the committed-journal cleanup, the uninstaller, the wizard's timeout line, the version, and the embedded scripts. **On v307's scripts it fails 16 of 19.** It replaces R133's interrupted-install gate, whose design this supersedes.
- **Windows (NOT RUN):** `tests/windows/test_installer_e2e.py`:
  1. kills an install while its log says `START 132/` and checks the journal is left;
  2. puts a user's own `README.md` where the payload would write one and checks a run refuses, names it, and leaves it alone;
  3. removes that file, runs again, and checks completion, with no transaction folder or hint left;
  4. then the new terminal and uninstall.
- **ChatGPT's remaining evidence requests** (interrupting after a publish but before its journal line, and around the final commit) are **not** in the e2e test. They need a hook to stop the engine at a chosen journal line, which I did not add. **Say if you want it.**

## WS3 - the logging

Done: `START n/N: <file>` before each copy, `DONE  n/N: <file>` after it, and `PUBLISH n/N: <file>` before each rename. **On the owner's v306 stall this would have named the file in progress.**

Evidence: `Claude-to-Sarvam/evidence-r134-r135/`.

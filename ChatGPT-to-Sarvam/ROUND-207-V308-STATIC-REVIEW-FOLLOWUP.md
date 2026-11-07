# R207 follow-up — v308 static review: release NO; arithmetic laundering and recovery ownership remain

Reviewed main: `0a4bbfde32ce51adcf3ee764c13647f0c37edbec` (v308), message “v308 claims the slice class is closed - test all eight, find the ninth, and try to bypass the gate”. Latest ChatGPT brief remains `Sarvam-to-ChatGPT/ROUND-207.md`; no ROUND-208 was present. This is a follow-up to R207 against actual new implementation, not an invented new assignment.

**Verdict: NO to release acceptance on this pinned candidate.** The eight named shapes have source fixes and contributor-reported regression evidence. A further expression-erasure candidate and installer ownership defects need resolution; final-package native acceptance is still outstanding.

**Method:** read AGENTS.md, PROJECT-MASTER.md and the design charter; inspect GitHub API-pinned source, commit patches and contributor evidence. Compiler, builds, suite, native Windows, Wine, installer and GUI execution: **NOT RUN by this reviewer**. All proposed reproductions below are **NOT RUN**, not observed failures. No production edits, CI launches, merges or background monitoring. The installer SHA below is the repository's recorded value, not an independent package hash measurement in this review.

## 1. What actually changed

The old documentation-only snapshot `218fb84e` is superseded:
- `60ce554d42e501131855db34f6ea8b5634229fda`: v307 indirect-call check, registration-return check, pending-install recovery.
- `2625083b4df2dd1c5c082b3bebc820936c1d89e8`: v308 shared predicate, OOM reserve, journaled installer.
- `11c6071c89b19ebfa71472954ebd497907226114`: expanded escape corpus, installer logging changes and rebuilt installer, compiler unchanged according to Claude R136.

Muse R135's report and `r135.json` report the small indirect-call output 0/7 and large exit 139 on v306; the laundering diagnostic printed the descriptor's element address, not an element. Muse R136's report and `r136.json` sharpen the return probe to an actual stale element read 7/99, and report eight escape shapes. These are **Muse's executions**, not mine.

Claude R136's `evidence-r136/muse-probes.txt` and `one-pred-on-v308.txt` report the thirteen Muse programs refused on v308, and 27 checks/0 failed including direct read=7, direct write=99 and ordinary mala cell=5. Source inspection agrees that all seven previous door calls now use `r134_holds_kosh`. The conservative rejection of even a no-growth function-value slice is disclosed; safe direct typed uses have reported positive controls.

This establishes progress on those programs, **not closure of every expression that can carry the descriptor**.

## 2. S4 — arithmetic wrapper can erase slice provenance (P1, source prediction; NOT RUN)

At `src/sutram_compiler.asm`:
- `r126_value_kind` (27776) recognizes VAR, SLICE, FUNCALL and TERNARY; a BINOP falls through to raw kind 5.
- `r134_kosh_slice` (28264) recognizes only VAR and SLICE. It does not inspect a BINOP's children.
- `r127_check_slice_value` (28344) rejects only a top-level AST_SLICE of a kosh.
- The binary-operation check at 9603 uses `rfx_is_kosh_operand` (9380), which only recognizes a **bare AST_VAR** kosh. Its mala/record checks likewise do not catch AST_SLICE. `rfx_kind` classifies AST_SLICE as non-string.
- Thus a slice inside integer arithmetic can reach code generation as a number. The generic emitter (25595 onward) evaluates the slice descriptor pointer and emits arithmetic on it.

Proposed ninth shape, adapted from Muse's R136 return probe:

```sutram
prakriya keep(x) {
    nivartanam x
}
mukhya() {
    kosh k[1]
    kosh_kship(k, 7)
    vitti obstacle = nirmmita(16)
    vitti zero = 0
    vitti t = keep(k[0:1] + zero)
    kosh_kship(k, 8)
    k[0] = 99
    vitti addr = t[0]
    likha(addr[0])
    likha(k[0])
}
```

**NOT RUN. Prediction:** the wrapper passes the untyped boundary as kind 5 while adding zero preserves the descriptor pointer; after relocation, the read can yield stale 7 while k[0] is 99. Compilation and exact output must be independently established. Also try direct assignment and cell-store versions of the same expression, plus `^ zero`.

Use a **variable** zero. A literal `+ 0` is a poor discriminator: `.r58_ft_identity` can strip that wrapper before the boundary sees it, exposing the top-level slice and producing a refusal. The source explicitly has this identity-folding path. Do not mistake that refusal for coverage of nonliteral expressions.

Required direction: reject inappropriate arithmetic on borrowed slices before their kind is erased, or preserve provenance through all value-preserving expression forms. Keep ordinary element arithmetic and safe direct slice use. Add negative tests for wrappers at each relevant boundary.

**Gate limitation:** `test_one_predicate.py` counts the old predicate's calls and looks for the new predicate in five bodies. A newly missed expression form needs no additional old-predicate call and therefore passes that structural check. Its 21 programs contain no arithmetic wrapper. “One call site” is an architectural check, not proof of class closure. The runtime portion should also require an unsuccessful compiler exit for a negative case, rather than just no output file plus diagnostic text.

## 3. I1 — recovery deletes ambiguous user files by suffix (P1, static finding)

`windows/native-installer/install-core.ps1:441-449` recursively enumerates **every** `*.sutram-partial` below the installation and deletes it whenever a pending file or unfinished journal exists. No manifest entry, journal record, hash or recorded temporary-file identity proves ownership. This runs **before** the conflict check and **before** the transaction lock at 536.

**Proposed reproduction — NOT RUN:** stop a disposable installation with an unfinished journal, place a user-created `notes.sutram-partial` (including a nested version) in the target, record its bytes, and rerun. Source predicts deletion even if a separate user-file conflict later refuses the install with “Nothing was changed.”

The suffix alone cannot establish that v307 created the file. Preserve and report ambiguous legacy partials, or require a recorded exact temporary-file identity. Do not recursively delete matching names as recovery.

## 4. I2 — lock and ownership checks do not cover the full transaction (P1, static race)

The engine reads journal/ownership state at 431 and 498-519, may remove a committed transaction at 432-435, and removes partial files at 441-449 **before acquiring its exclusive lock** at 536. It does not refresh ownership decisions after acquiring the lock. Publishing rehashes a destination at 568, but checks only whether it equals the new payload; otherwise it moves it to backup (or deletes it when that backup already exists, 574-579).

**Proposed race — NOT RUN:** let run B finish its ownership preflight while run A owns the lock; let A complete and release the lock, then let B acquire it using its stale preflight. Separately, change a destination after preflight but before publishing. The publication branch does not revalidate that changed hash against the allowed ownership set; backup cleanup can ultimately discard the newly changed file.

Acquire a stable lock before reading/recovering transaction state and hold it through cleanup; refresh all decisions under it. Revalidate each target immediately before replacement and preserve a newly ambiguous file. A lock inside a directory that cleanup deletes also needs a deliberate lifecycle.

The journal implementation is real progress: write-through + Flush(true), hash-checked sibling staging, START/DONE, intent records before ordinary rename publication. But the strong claims “nothing changes before BEGIN”, “nothing changed on conflict”, and “one installer at a time” are not established by substring checks in `test_install_transaction.py`. Recovery's existing-backup branch also explicitly deletes a target at 576 before that iteration's PUBLISH record. Describe and test that branch accurately rather than claiming universal rename-only replacement.

## 5. W1 and OOM — fixed branch, incomplete acceptance

**W1 source fix present:** `win/winrt_blob.asm:23-24` tests the registration return and branches to `rt_init_noveh`, which writes a static diagnostic, restores the console code page when needed, and calls ExitProcess(1).

Claude's `evidence-r134-r135/veh-and-commit-gate.txt` reports 4/0, including registration-failure and commit-failure test runtimes under **Wine**. Reading `tests/r133/test_veh_registration.py` confirms these are separately built fault-injection runtimes, not a native fault test of the final package. Both injection macros force RAX to zero **after** the real API call, so they exercise the error branch, not actual resource exhaustion or absence of a registered handler.

**v308 OOM mitigation present:** startup commits 64 KiB and stores RT_OOM_RESERVE; .v_nomem clears the slot and releases it before printing/exiting. However startup reserve allocation is unchecked and VirtualFree's success is unchecked. “At least 64 KiB available at exit” is conditional on those operations succeeding; even then it is not a native measurement or a guarantee against every competing commit consumer. Add explicit reserve-allocation-failure coverage and state the fallback contract.

The decisive final-binary native job-limit cases remain required: B3 448/480/512/544/640 MiB, the mandapa 64 MiB case, repeated runs, full exit statuses and stderr, plus successful controls. Message-only success is insufficient. The stack-growth explanation is a hypothesis supported by the pattern; a native trace/stack-commit probe is needed to establish it, as Claude R136 now acknowledges.

## 6. Installer history and release gate

The v303 hang was real: 131 copied payload files plus zero-byte `docs/rounds/PROJECT-OVERVIEW.md`; the later ownership refusal was its aftermath, not its cause. The original v303 stall's cause remains unestablished in this review. Later reports attribute v306/v307 upgrade suspensions to Acronis logs; that must not retroactively establish the v303 cause without corresponding evidence.

Current `Sutram-Setup.sha256` records:
`a8446b039b100aaf23830bff8f16f4851c1c1b9b11cff1e82b56af85e622a13d`.
This supersedes R134's e7370868… package. **Independent hashing/extraction of this v308 package: NOT PERFORMED here.**

No v308 native acceptance directory was found in the pinned tree. Claude R134/R136 explicitly report no native Windows/PowerShell execution for this candidate. Their 73 PASS / 0 FAIL / 1 NOT-RUN line is Linux/Xvfb evidence, not Windows acceptance. The existing interruption fixture stops staging; it does not cover stops between backup and publish, publish and PUBLISHED, metadata finalization, COMMITTED and cleanup, or the races above.

Release YES still requires:
1. Reproduce/resolve S4 and retain the eight-shape refusals and safe-use controls.
2. Final-candidate native registration-failure and real lazy-commit OOM acceptance, including reserve failure behavior.
3. Interrupted-install recovery across publication/finalization boundaries while preserving ambiguous and concurrently modified user files.
4. Exact-package native clean install, same-folder upgrade, PATH/new terminal, IDE and uninstall acceptance.
5. Release notes limited to established evidence. The current slice-class and unconditional OOM wording is stronger than this review supports; the 69-gate summary is also stale relative to the reported 73.

## Pinned Git blob identities

These are Git blob SHA-1 identifiers from the reviewed tree, **not SHA-256 package measurements**.

| Path | Git blob |
|---|---|
| `src/sutram_compiler.asm` | `cfd7863d71902286d755e39e72ec19b9d4c7ae71` |
| `win/winrt_blob.asm` | `692115ee5f86ccde3d8f09d8b833cd55791343ae` |
| `windows/native-installer/install-core.ps1` | `2f56e780451d9cdbbaaca1872348a7db68e520d5` |
| `tests/r134/test_one_predicate.py` | `25bffe60c06057b2f6b6e856cf4472c2f7fe3a5f` |
| `tests/r134/test_install_transaction.py` | `a94e9c004a982bb75c61aa9abc108cd059f67674` |
| `tests/r133/test_veh_registration.py` | `c07e7ee12555ff09381604491039536fb39dec21` |
| `Sutram-Setup.exe` | `168ca47bc292b01f7ac26b1201345c5ba6ced11c` |

Only this documentation handoff is to be committed. Proposed programs and installer scenarios above are **NOT RUN**.

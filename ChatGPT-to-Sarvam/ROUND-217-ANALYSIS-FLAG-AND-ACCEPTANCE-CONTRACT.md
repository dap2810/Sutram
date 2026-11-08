# R217 — exact analysis-budget interface and bounded Windows acceptance

Reviewed main: `d935506a56190dded437317512ad0721fc87fd2f`. New input: `Sarvam-to-ChatGPT/ROUND-217.md`. This commit changes only that brief since my R216 response. The interface below is a **specification for implementation**, not a claim that v313 exists or passes.

Compiler/build/suite/native Windows/installer execution: **NOT RUN — read-side role, no toolchain used**. Static reading only. No product source changes.

## WS1 — exact flag contract

Adopt the requested `--analysis-steps=N` and release default **200000**. This supersedes the optional 65536 policy in R216 because the project has now chosen the configurable policy.

| Input/property | Required behavior |
|---|---|
| Syntax | One argv token, exactly `--analysis-steps=` followed by one or more ASCII decimal digits |
| Range | **1 through 2147483647 inclusive**; this is a deliberate supported interface range, not a claim that all corresponding programs fit |
| Leading zeros | Accept; interpret as decimal; display normalized decimal |
| Examples accepted | `--analysis-steps=1`, `--analysis-steps=00064`, `--analysis-steps=200000`, `--analysis-steps=2147483647` |
| Examples rejected | Empty value, 0 (including 000), -1, +1, 200k, 1e5, 0x100, 1_000, decimal fractions, embedded/leading/trailing whitespace, non-ASCII digits, trailing junk |
| Overflow/out of range | Reject before multiplication/addition can wrap; no truncation, saturation, or fallback to default |
| Separate value | Reject `--analysis-steps 200000`; the equals sign is required |
| Repetition | Reject a second occurrence, even with the same value; no first-wins/last-wins ambiguity |
| Scope | Invocation-wide setting; reset the remaining count to N at each independent expression/statement validation entry, including global initializers and the gen_expr fallback |
| Test build | Keep the compile-time low default for targeted tests. Explicit flag overrides that default. Help/diagnostics report the effective build default/value; never ship the low-default binary as the release binary |

Range parsing can check `acc > (2147483647 - digit) / 10` before updating `acc`. A signed 64-bit counter safely holds this contract. The upper bound is a representability policy, not a timeout guarantee.

**Step meaning:** one work-list entry popped by the validation walk, including entries subsequently recognized as non-node fields. Allow exactly N pops. If work remains before pop N+1, refuse. An empty work list after pop N succeeds if all other checks succeeded. Do not describe N as nodes, terms, tokens, recursion depth, or a whole-compilation budget. Nested helper work is not automatically covered by this counter.

Raising N must not change any AST allocation, parser nesting, explicit work-stack, pointer, arithmetic, or semantic guard. Work-stack exhaustion must still refuse; it must not discard pending work. A failed/incomplete validation cannot leave a successful checked state or fall through to code generation.

### Exact diagnostic templates

Keep Sanskrit-primary diagnostic wording and the existing stable `E_VAKYA_SEEMA` code. The following are proposed verbatim default romanized-Sanskrit strings. Braced fields are substitutions, not literal output; each displayed line ends with a newline.

For budget exhaustion:

```text
Sutram truti [E_VAKYA_SEEMA]: parikshana-pada-seema {N}; parikshanam na samaptam; sankalanam nirastam.
Sthanam: {file}:{line}:{column}
Sanket: vakyam laghutareshu vibhaja; madhyamani mulyani namabhih rakshya. Athava --analysis-steps=N ityatra adhikam mulyam dehi.
Suchana: vakya-vriksha (AST), vakya-vishleshana, smriti cha prithak seemabhih baddhani; --analysis-steps=N tasam seemah na vardhayati.
```

Meaning: analysis-step limit N; checking did not finish; compilation refused. Split the expression and name intermediate values, or increase the flag. AST, parsing and memory have independent limits that the flag does not raise.

Use the **effective runtime N**, not a compile-time string. Print the original source location of the checked root when available, including imported-file mapping. If only file/line are known, print those without an invented column. If no trustworthy source location exists, replace the entire location line with exactly:

```text
Sthanam: ajnatam
```

For missing/malformed/out-of-range flag values:

```text
Sutram truti [E_PARIKSHANA_VIKALPA]: --analysis-steps=N; N kevalam 1..2147483647 madhye dashamika purnankah bhavet.
```

For repetition:

```text
Sutram truti [E_PARIKSHANA_VIKALPA]: --analysis-steps=N ekavaram eva deyam.
```

These mean respectively “N must be a decimal integer in the stated range” and “supply the option only once.” Do not echo arbitrary malformed argv bytes into a diagnostic.

**Failure behavior:** exit **1**, no newly emitted executable or object from the failed compilation, no success banner. Validate options before reading/creating compilation outputs. On semantic/capacity failure preserve any pre-existing destination rather than deleting a user's earlier binary; remove only temporary outputs owned by this invocation. “No executable” means no output produced by this failed invocation, not destruction of a pre-existing file. A caller/IDE must honor the failed status and must not run an old destination as if compilation succeeded.

### Distinguish capacity from analysis work

At this pin, `AST_HEAP_CAP` is **3145728 bytes**. Both `alloc_ast` and `reserve_ast_block_extra` refuse through `msg_ast_overflow`, currently the uncoded “vakya-vriksh seema atikram.” Do not reuse E_VAKYA_SEEMA for this.

For those AST arena exhaustion paths, specify:

```text
Sutram truti [E_VRIKSHA_SEEMA]: vakya-vriksha (AST) smriti-seema {B} bytes; sankalanam nirastam.
Sthanam: {file}:{line}:{column}
Sanket: sankalana-ekakasya aakaram nyunam kuru. --analysis-steps=N imam seemam na vardhayati.
```

Here B comes from the actual AST arena capacity; use the same location fallback. Meaning: the AST storage limit was reached; reduce the compilation unit's size; the flag will not increase this limit. Splitting one expression into more assignments need not reduce total AST storage and must not be promised as this error's remedy. Moving text into a textually included file is likewise not a storage fix.

| Failure | Stable code / resource | Useful action |
|---|---|---|
| Analysis traversal unfinished | E_VAKYA_SEEMA / steps per validation | Split expression, or increase N within supported range |
| AST arena full | E_VRIKSHA_SEEMA / AST bytes | Reduce the compilation unit; increasing N does not help |
| Other parser/work-stack capacity | Keep a separately named resource diagnostic; do not label it either of the above unless that resource actually failed | Follow that resource's remedy; the flag does not enlarge it |

Other limits include block statement counts and nesting: do not call every parse failure “AST heap full.” When two limits could bind, report whichever guard actually fires first; no promise that a higher N makes the source compile. Codes and flag spelling stay stable across language-pack translations.

### Focused acceptance cases for the implementer

These are requested checks, **NOT RUN by me**:

- Parse the acceptance/rejection examples above, including a very long decimal value and duplicate flags. Reject before output side effects.
- With a measured valid fixture requiring K steps, K succeeds and K-1 refuses with the effective N. Explicit override on the low-default build agrees with the release build at the same N.
- Exercise local statements, global initializers and the gen_expr fallback; retain low-budget fault coverage where production AST capacity otherwise prevents reaching exhaustion.
- Force AST capacity independently with a generous N: E_VRIKSHA_SEEMA, correct byte capacity, nonzero exit and no newly emitted output. Do not require a guessed universal term threshold.
- At a generous N, known-invalid slice/operand fixtures must remain rejected. Raising the resource allowance cannot waive semantic checks.
- Verify original source locations where available, unavailable-location fallback, and preservation of an existing output on failure.

## WS2 — concrete first-use places to look

I do **not** believe there is nothing left to inspect. Nor can static reading establish that nobody has tested a case. These are concrete user-visible paths not established by the evidence I reviewed, with source anchors:

1. **Start-menu Terminal with “Add to PATH” unchecked.** In `windows/native-installer/install-core.ps1`, the Start-menu terminal uses a constructed cmd /K command and its own PATH prefix, while the normal fresh-shell check runs only when AddPath is true. Launch that actual shortcut from Explorer on a Unicode/spaced install path; confirm the intended compiler and a simple compile/run work. This is distinct from checking registry PATH text or invoking the binary by full path.
2. **A .sm file opened through the shell.** The same script writes the open command as the GUI plus a quoted "%1", and preserves an existing extension default. Use Open With Sutram on a filename containing spaces and non-ASCII characters; confirm the intended file is opened and can be edited/run. With another default application, verify ordinary double-click still follows the user's existing choice. Registry presence alone does not establish argument handling in the IDE.
3. **Desktop shortcut collision.** The script intentionally preserves a pre-existing unowned `Sutram IDE.lnk`. Check what a first-time user sees when that link points elsewhere: Start-menu Sutram should still work, the existing shortcut should remain untouched, and completion guidance must not imply that every desktop icon now launches the new installation.
4. **Documentation shortcut and first save.** The script creates the documentation link only when the English book exists; inspect it offline. Start the IDE from its shortcut, save a new small program to a writable user directory, then build/run it. Confirm the working directory does not make a novice write into the installation or lose track of the output.

These are **places to look, not four newly discovered bugs**. The existing display-scaling/keyboard checks remain useful, but I am not making every candidate here a fresh release gate. The agreed finite acceptance scope should identify which checks it includes and record the rest as untested.

The five historical findings should not all be called open: the v312 native evidence already supports fixes for licence encoding, unwanted uninstall console and empty .sm key on its tested configuration. The clipped instruction and temporary-file cleanup are the outstanding findings discussed in R216; v313 fixes require their own evidence.

## WS3 — smallest honest YES sentence

**“YES for the documented v1 scope on the tested Windows configuration: the identified final package passes the agreed acceptance checks, verifies the remaining installer fixes and the specified budget behavior, with any reused evidence tied to unchanged components.”**

This is a conditional acceptance sentence, **not today's approval**. “Being fixed” is not the evidence that a fix passed. Retain the existing fixed acceptance list; do not silently expand it with every new investigation idea. The new flag is now a chosen behavior, so its focused checks belong to that change. No universal defect-free or all-Windows claim is required.

## WS4 — method-note rule

**A test-ready brief must pin an existing artifact at an immutable repository commit, record its setup and embedded compiler SHA-256 identities, verify that its embedded identity matches the requested build before issue, and require the recipient to repeat that preflight; a mismatch blocks installation and must never be relabeled as the requested build.**

A manifest/version claim is not enough if the embedded compiler bytes differ. If native --version cannot be executed by the issuer, cross-check the embedded hash against the named compiler build evidence and explicitly leave native --version as mandatory recipient preflight. If no verified mapping exists yet, issue only **DRAFT — blocked on artifact publication/verification**. Never fill identities from a planned version or a mutable “latest” path.

This would have caught a v313 brief pointing to bytes still embedding v312 before it became an executable acceptance request. Rebuilt packages get new hashes and an explicit decision about which unchanged-component evidence transfers.

No source edits, builds, CI launches, merges, or Windows executions were performed.

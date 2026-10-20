# Sutram — systematic negative corpus, Round 70

**Status: six executable test definitions and a tested runner; current native
corpus acceptance remains pending.** Two programs and messages are copied
byte-for-byte from existing accepted fixtures. Four are new source-derived
expectations. Those categories must not be reported as six newly observed
compiler passes until the native runner has actually succeeded.

Snapshot: `dde0613ca16f3e41345b1b1055733151780ef9d7`.
The machine-readable contract is
[`tests/negative/r70/manifest.json`](../tests/negative/r70/manifest.json).
No existing `tests/expect/` patra or example was changed.

## 1. Category table and exact diagnostic contract

Every case requires **compiler exit 1**, empty stderr and **no generated output
path**. Text is compared without whitespace stripping or CRLF normalization.
`{source}` below is replaced only by the exact temporary absolute input filename.
All explicitly shown full diagnostics end with one LF.

| Category | Fixture and rejected construct | Diagnostic requirement | Provenance |
|---|---|---|---|
| Bad type | `bad_type.sm`: integer `kosh` passed to `kosh dasham` parameter | Full stdout: `Sutram Error: kosh tark: tatv prakar bhinn\n` | Existing example 120 and its exact golden; copied identities checked. |
| Bad arity | `bad_arity.sm`: seven arguments to a user function | In order: `Sutram Error: vyakaran dosh, pankti `, then `Sanket: prakriya adhiktam 6 tark lete hain.\n` | New fixture; explicit `parse_primary.pp_ic_parse` limit and diagnostic string. Full framing is not pinned. |
| Unknown identifier | `unknown_identifier.sm`: `does_not_exist(7)` | Full stdout: `Sutram Error: agyat prakriya: does_not_exist\n` | Existing example 69 and its exact golden; function identifier only. |
| Malformed literal | `malformed_literal.sm.hex`: digit-shaped `E0 A5 20` bytes in a numeric value position | Full stdout: `Sutram Error [E_UTF8]: {source}:2: srot me ashuddh ya khandit UTF-8\n` | New fixture; R68 prelex UTF-8 diagnostic path. |
| Unterminated string | `unterminated_string.sm`: open quote consumes the intended call delimiter and closing brace | In order: `Sutram Error: vyakaran dosh, pankti `, `patra-ant`, `Sanket: is sthan par shabd aur vyakaran dekho.\n` | New source-derived rejection expectation; no dedicated unterminated-string diagnostic is invented. |
| Misplaced keyword | `misplaced_keyword.sm`: `vitti a = वि॰`, with `--lang sanskrit` | Full stdout (R11: in the Sanskrit pack's language): `भाषा-पुटः प्राप्तः: sanskrit\n` then `Sutram Error [E_ABBREVIATION_VALUE]: {source}:2: संक्षेप-शब्दः मूल्यं नास्ति: 'वि॰'\n` | New fixture; existing exact alias and R68 value-start guard. |

The two fragment matchers intentionally test stable error identity/hint rather
than pretending the complete parse-error line, column, snippet and whitespace
have already been measured. Their manifest says `ordered_fragments`, not `exact`.

## 2. Coverage limits that must stay visible

The unknown-identifier case tests an undefined **function**. It does not prove
that every undeclared local, invalid field, or uninitialized read is rejected.
The source's field-resolution fallback and limited-name comparison need their
own characterization tests; they are not newly sanctioned language semantics.

The malformed-literal case tests an invalid encoding in a digit-shaped sequence.
It does not certify rejection of `0x`, `1e+`, an excessive integer literal or
multiple decimal points. Those need separate numeric grammar decisions and
regressions, not invented error messages.

The unterminated-varna case also loses the intended parsed closing delimiter.
A pass proves rejection of this exact invalid program, not a universal lexical
rule that every unterminated quote is diagnosed at its opening location.

The arity case tests the maximum-six-argument boundary, not every call whose
arity differs from its declaration. Missing arguments, surplus arguments below
that maximum, and signature mismatches need independent coverage.

A correct diagnostic for the misplaced abbreviation is not evidence of arbitrary
prefix expansion, localized messages for every pack, or imported-source location
mapping. The R68 messages name the root input and expanded line.

## 3. Native acceptance command

Use a complete checkout containing the pinned R68 sources. The large inherited
compiler is unchanged by R70. The runner verifies these Git blobs before invoking
any compiler (re-pinned in ROUND-03 together with `manifest.json`):

| Input | Required Git blob |
|---|---|
| `src/sutram_compiler.asm` | `8625095aa53027bbaf4eef29e7afe76e525d1008` |
| `src/r68_compiler_entry.asm` | `42389aaf73179726d91e23359aee2199734036e1` |
| `src/r68_diagnostics.inc` | `a6f7bb196702626d6b7f116f32e678d9daf73eba` |
| `src/r68_unicode_helpers.inc` | `69103e059634aa6b5b871ce7c06c2f4b9c742ff1` |
| `src/r66_indic_lexer.inc` | `998b6cb75a7e11cf6d488cf84a84a2154ffdebf0` |
| `src/r67_stack_pair.inc` | `e8472bd1cad767cf06b0c00fcf88793419362db5` |
| `lang/sanskrit.lang` | `48fbf99a94f2f810911501860817c3fc27de95a3` |

Build the R68 diagnostic entry, not just the bare compiler. An example on the
reviewer's existing Linux NASM toolchain is:

```sh
nasm -f elf64 -I. src/r68_compiler_entry.asm -o /tmp/r70-corpus.o
ld -o /tmp/r70-corpus-compiler /tmp/r70-corpus.o
python3 tools/r70_negative_corpus.py --compiler /tmp/r70-corpus-compiler \
  --report /tmp/r70-native-negative-report.json
```

Use fresh paths; the report writer refuses overwrite. A separately calculated
`--compiler-sha256 <64-lowercase-hex-digits>` can bind the chosen binary to a
reviewed artifact. The report always records its gudh. **Matching source pins
and a binary gudh do not, by themselves, prove the binary was built from those
sources**; preserve the independent build command/log as well.

Unknown source drift is an error, not a reason to bypass the verifier. Re-review
and version the corpus profile for a new source identity. The runner does not
build, install, download, change permissions or invoke an automatic CI job.

## 4. How the runner avoids false passes

Before negatives, it compiles and executes a valid `likha(42)` control with the
default pack selection and with Sanskrit. A broken compiler that merely rejects
every input cannot satisfy the run. This runner is deliberately a Linux ELF
execution profile, not cross-platform acceptance.

Each negative is written to a fresh private temporary directory. The malformed
fixture is transported as ASCII hex and decoded into exact invalid bytes;
Unicode replacement characters are never substituted. Fixture patra hashes and
decoded program hashes are checked separately. The temporary filename is used
in location expectations without broad output normalization.

All `SUTRAM_*` variables are removed from the subprocess environment; only the
case's explicit pack option is supplied. This prevents an unrelated inherited
check mode or pack from silently changing the profile.

Signals, wrong nonzero exits, timeouts, missing diagnostics, extra stderr, and
unexpected output paths all fail. `lexists` also detects dangling output
symlinks. **An unexpectedly compiled negative output is never executed.** The
only generated programs run by this harness are the explicit positive controls.
No expectation is auto-recorded from whatever an unverified compiler happens to
print. The manifest permanently labels current-run status as pending; native
results belong in a separate report.

Exit 0 from the native runner means the controls and all six declared rejection
contracts passed. Exit 1 means at least one negative failed; exit 2 means a
precondition/control/execution setup failed. Either is a non-acceptance phal.

## 5. Runner validation versus compiler validation

```sh
python3 tools/r70_negative_corpus.py --validate-only
python3 -m unittest discover -s tests/r70 -p 'test_*.py' -v
```

`--validate-only` checks corpus schema, coverage, fixture hashes and program
bytes. It prints `native_status: NOT_RUN` and explicitly says production source
pins were not checked. The unit tests use mocked compiler processes for native
flow scenarios. Passing them proves runner behavior, **not Sutram's rejection
behavior**. Two inherited source/diagnostic copies are checked against their real
Git blob identities, without rewriting the accepted originals.

**Verification limit:** the six-category corpus and runner are delivered and the
runner tests pass; full compilation/rejection of this corpus has not been run in
this environment. Sarvam must record that phal before WS2 is native-accepted.

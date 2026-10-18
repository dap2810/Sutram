# Sutram — evidence-bounded specification, Round 70

**Status: a specification of the evidenced subset, not a complete language standard.**
Review snapshot: `dde0613ca16f3e41345b1b1055733151780ef9d7`.
Compiler source Git blob: `64ea028a5ccf56117c132a7efd0673cbe2df3fc6`.
The R68 diagnostic entry is a separate source patra, blob
`42389aaf73179726d91e23359aee2199734036e1`. Building the bare compiler and building
that entry are not interchangeable diagnostic profiles.

This document implements the foundation-first direction of the
[design charter](sutram-design-parameters.html) and
[Round 70 brief](../Sarvam-to-ChatGPT/ROUND-70.md). The brief calls the charter a
19-item document and uses older item numbers; the pinned charter has 20 items.
The relevant headings are **11, memory/resources; 13, freestanding; 20,
specification/evidence**. This review follows those headings without editing the
charter or pretending the numbering agrees.

## 1. Meaning of the evidence labels

**Pinned fixture** means a concrete source program and its existing expected
output/exit or compile-fail marker were inspected. It establishes the behavior
that test demands, not that every related expression has been tested. Historical
acceptance belongs to the repository's recorded test runs; these fixtures were
not re-executed with a Sutram compiler in this review.

**Source observation** means the inspected implementation contains the described
path. It is not a promise that the path is correct or portable. **Documented
contract** identifies an existing component document and retains its scope.
**Unspecified** means this review found insufficient directly inspected evidence
to establish a dependable general rule. It does not mean every choice is safe,
that the compiler may exploit C-style undefined behavior, or that no test could
exist elsewhere in the repository.

A future change can promote a rule only by adding/identifying discriminating
fixtures and recording execution on the intended compiler profile. Do not infer
an entire language specification from a test filename or from native code output.

## 2. Procedural core and keyword grammar

The evidenced core uses `.sm` source and canonical Sanskrit keyword spellings.
Programs in the inspected fixtures enter through `mukhya()`; explicit brace bodies
are exercised by the float, short-circuit and type tests. The precedence fixture
also exercises a brace-less **main** body with several statements. This does not
establish identical rules for brace-less user functions.

The following are exercised forms, not a complete EBNF grammar:

```sm
prakriya set0(a, v) {
    a[0] = v
    prati v
}

mukhya() {
    vitti x = 3
    dasham y = 1.5
    mala cells[1]
    cells[0] = x
    yadi (x > 2) { likha(x) }
    likha(set0(cells, 4))
}
```

The composite illustration above is explanatory; the constituent forms are
supported by the linked fixtures, not by a claimed new run of that composite.
`prakriya` introduces a named function, `prati` returns, `vitti` introduces a
scalar variable, and the inspected `mala`/`kosh` cases provide indexed storage.
A typed parameter form `kosh dasham a` is exercised by the accepted negative type
case. There is no claim here of first-class functions, closures, generics, methods,
ownership syntax, a complete inferred type system or a formal module ABI.

**Unspecified here:** complete declaration grammar, name shadowing rules,
exhaustive scope rules, duplicate local declarations, every missing initializer,
all illegal keyword positions, a complete return-type contract, and a complete
argument-count-vs-declaration rule. The implementation's maximum-six-arguments
path is identified in the negative corpus; that limit alone is not proof of every
function-signature check.

Evidence: [short-circuit source](../examples/89_b9_short_circuit.sm),
[float source](../examples/92_t12_dasham_float.sm),
[precedence source](../examples/22_precedence.sm), and
[type mismatch source](../examples/120_t18_kosh_param_mismatch.sm).

## 3. Operator precedence and associativity

The older [language reference](LANGUAGE-REFERENCE.md) lists this inventory,
loosest to tightest. It is retained here as a **documentation inventory**, not
silently promoted to a fully tested normative table:

| Listed level | Operators | Evidence boundary in this review |
|---|---|---|
| 0 | `? :` | General precedence and right associativity unspecified here. |
| 1 | `\|\|` | Short-circuit cases are pinned; its relation to all other levels is not. |
| 2 | `&&` | Short-circuit cases are pinned; its relation to all other levels is not. |
| 3–5 | bitwise `\|`, `^`, `&` | The `3 & 4` phal is pinned. Cross-level rules are unspecified here. |
| 6–7 | `== !=`, then `< > <= >=` | Several ordinary comparisons are pinned; chained-comparison semantics are not. |
| 8 | `<< >>` | General precedence, negative counts and out-of-range counts unspecified here. |
| 9 | `+ -` | Arithmetic/grouping examples below are pinned. Complete associativity is not. |
| 10 | `* / %` | The specific remainder/addition relation below is pinned. Complete cross-level coverage is not. |
| 11 | unary operators and grouping | Explicit grouping is pinned. The reference's unary `!` entry is not certified by the inspected fixtures. |

[Example 22](../examples/22_precedence.sm) and its
[exact golden](../tests/expect/22_precedence.out) demand:
`(3 + 4) * 2` prints `14`; `10 % 3 + 1` prints `2`; `3 & 4` prints `0`;
and the two indicated comparison/logical conditions take their expected branches.
The fixture also pins the extra newlines it explicitly prints.

These observations do **not** distinguish every possible parse tree. In
particular, no general left-associativity guarantee for subtraction/division,
right-associativity guarantee for ternaries, or full C-equivalent operator
hierarchy is established here. Add discriminating tests such as nonassociative
chains before promising those rules; those suggested tests are not existing
acceptance evidence.

## 4. Evaluation order

The source and [golden for example 89](../tests/expect/89_b9_short_circuit.out)
pin conditional right-side evaluation with an observable mutation:

| Expression, with `a[0]` initially 10 | Result | `a[0]` afterwards |
|---|---:|---:|
| `0 && set0(a, 20)` | 0 | 10 |
| `1 \|\| set0(a, 30)` | 1 | 10 |
| `1 && set0(a, 40)` | 1 | 40 |
| `0 \|\| set0(a, 50)` | 1 | 50 |

The last two rows occur after the preceding rows in the same program. This pins
skipping/executing those right operands and Booleanized results for those inputs.
The mutation demonstrates shared underlying mala storage in that call, not an
ownership or borrow rule.

**Unspecified:** a universal left-to-right or right-to-left order for ordinary
binary operands, multiple function arguments, builtin arguments, assignments with
complex indexes, and all combinations of nested side effects. Compiler emission
comments are not a replacement for order-sensitive tests. Until specified,
programs intended to be portable across compiler changes should separate such
side effects into statements; this is usage advice, not a new semantic rule.

## 5. Integer and floating-point behavior

### Integer profile

The inspected implementation represents ordinary integer cells in qwords. The
[overflow safety document](OVERFLOW-SAFETY.md) records signed 64-bit,
two's-complement wrapping for plain addition/subtraction/multiplication in the
default profile, with separately documented checked and saturating library forms.
That is a **documented component contract supported by prior reported gates**;
this review does not manufacture a fresh all-boundaries run.

Do not generalize wrapping to division. The same document distinguishes a zero
divisor and `INT64_MIN / -1` (also the corresponding hardware remainder operation)
from an ordinary wrapped phal. Default-profile hardware termination is not a
recoverable language exception, and a crash is not a successful compile-time
rejection.

`SUTRAM_R65_TRAP_INT=1` is an optional **NASM compiler-build define**, omitted by
default, not a source keyword or ordinary command-line language switch. The
recorded trap contract uses `Sutram Error [E_INTEGER_TRAP] <patra>:<line>: ...` for
selected integer overflow/divisor errors. Whether all synthesized operations,
all imported locations and all profile combinations obey an identical rule is
not certified here.

The checked-library convention is `0` on failure with `ok[0] = 0`, exact phal
with `ok[0] = 1` on success; saturating operations have their own seemit/sentinel
contracts. **Do not claim transparent composition with trap mode.** The existing
document explicitly says perform-then-check add/subtract/multiply/ghat/factorial
forms can abort before checking under that mode, unlike guard-first division,
remainder and absolute-value forms. No library implementation is changed here.

**Unspecified here:** out-of-range literal acceptance, implicit narrowing for all
types, the entire integer conversion lattice, exact floating-to-integer boundary
behavior, shift-count edge cases, and recoverability of every machine exception.

### Floating-point profile

[Example 92](../examples/92_t12_dasham_float.sm) and its
[golden](../tests/expect/92_t12_dasham_float.out) exercise `dasham`/`दशम`, finite
mixed arithmetic, negative values, comparisons and six-decimal-place output:

```text
3.750000
1
3.250000
-1.250000
0.300000
1
2.500000
7
```

The source identifies binary64 scalar storage. Printing `0.300000` after
`0.1 + 0.2` is not proof of exact decimal equality. **Unspecified:** NaN payloads,
infinities, signed zero distinctions, subnormals, rounding-mode control,
exception flags, exponent literal grammar and exact formatting for every value.

## 6. Strings, bytes and indexed storage

The [ASCII index fixture](../examples/65_char_code_index.sm) requires
`aksharank("AZ", 1)` to print `90`, with
[golden `90\n`](../tests/expect/65_char_code_index.out). This contradicts the older
reference's statement that the index is ignored for that case; the concrete
fixture is the evidence used here. **It does not establish Unicode code-point or
grapheme indexing.** No normalization, grapheme-counting, encoded-length or
embedded-NUL guarantee is inferred from an ASCII example.

For `kosh`, the existing [builtin specification](KOSH-BUILTINS.md) records
length/capacity, integer or binary64 element cells, append, LIFO pop/peek, FIFO
dequeue and length-only clear. The inspected `kosh_clear` emission sets length to
zero and does not erase backing storage. That is not cryptographic erasure or
automatic memory reclamation. See [MEMORY-MODEL.md](MEMORY-MODEL.md).

The accepted type-error fixture rejects passing an integer `kosh` to a typed
binary64 `kosh` parameter. This is a specific static type check, not evidence that
all raw-pointer conversions or aliases are safe. Distinguish **typed kosh
parameters** from a nonexistent generic collection type.

## 7. Language packs and Unicode

[The pack gate](../tools/test_lang_packs.py) explicitly invokes `--lang` for 11
packs and checks three groups: `kosh` plus `dasham`, `kuru`, and `yantra`.
It reads native spellings for existing canonical words; the tests are about one
language with multiple keyword spellings, not different evaluation semantics.
That runner strips leading/trailing output whitespace: it is not a full byte
identity proof for all translated programs.

The inspected Sanskrit pack contains exact `वि॰ -> vitti`, `लि॰ -> likha`,
`प्र॰ -> prakriya`, and `प॰ -> prati` aliases. These are exact language-pack
entries, not arbitrary prefix abbreviation, new Unicode rules or statement
terminators. The digit/danda include and earlier acceptance tools specify the
scoped native numeric surface; they do not establish complete Unicode
identifier normalization or confusable-name detection.

**Unspecified here:** CLI-versus-environment selection precedence, every search
path and fallback on missing packs, conflicting duplicate entries, per-import
pack selection, normalization equivalence, all malformed non-ASCII forms, and
all-script glyph rendering. Existing references to `SUTRAM_LANG` describe an
interface; no directly inspected precedence test is presented for it.

## 8. Errors and reproducibility

[NEGATIVE-CORPUS.md](NEGATIVE-CORPUS.md) separates two inherited exact diagnostics
from four newly proposed rejection fixtures. `E_UTF8` and
`E_ABBREVIATION_VALUE` belong to the R68 entry profile. Its source reports the
root input filename and an expanded-source line after imports, **not necessarily
original imported-patra provenance**. Runtime bounds/empty-container errors and
integer traps are different stages from compiler rejection.

The R70 runner requires exit 1, the declared diagnostic contract and no output
path, plus successful positive controls. A signal, timeout, generic startup
failure or generated executable cannot be relabelled a passed negative test.
Neither a successful build nor an existing golden demonstrates freestanding or
Windows execution. See [FREESTANDING.md](FREESTANDING.md).

**Verification limit:** source/golden inspection and corpus-runner unit tests were
performed; no complete Sutram compiler or Windows execution was performed in
this review. Rules marked unspecified remain deliberately unspecified.


## Round 71 evidence refinement — two narrowly specified existing cases

**Added 2026-10-16. These clauses come from existing source/accepted expectation
pairs, not from new native executions in this review.** The rest of this
specification's distinctions between tested, observed and unspecified remain.

### Effectful typed-mala indexing

In `examples/140_r30_index_side_effect.sm`, a typed `kosh dasham` initially holds
2.0. `mutate_index(arr)` writes 9.0 to `arr[0]` and returns the index 0. The
expression `arr[mutate_index(arr)] + 1.5` must produce 10.500000 in this fixture;
the following reads print 9.000000 and 7.500000 (after subtracting 1.5).
The accepted `tests/expect/140_r30_index_side_effect.out` pins those bytes.

This establishes that **this indexed load observes the index expression's
mutation**, rather than reading the old cell value before the index expression.
It does not establish every ordinary binary-operand/argument order, nor prove
that an idempotent mutation ran exactly once. Those wider rules still require
separate tests.

Source Git blob: `8ef32a23a8557ffc8a84bc58d9cc6428cc0e5d08`.
Expected-output Git blob: `8b474f6e0357c890a3cbb356a351a63adaa302ef`.

### Two positive floating-to-integer collection conversions

In `examples/112_t18_kosh_integer_conversion.sm`, pushing 2.9 into an integer
`kosh` and reading it prints 2. Assigning 4.8 to its integer cell and popping the
cell prints 4. The accepted output is exactly `2\n4\n`.

These **two positive, in-range collection conversions** are specified by the
fixture. They do not alone specify all scalar assignments, negative/out-of-range
conversions, NaN, infinity or a general rounding rule. The fixture's comment is
broader than the values it tests; only the evidenced values are promoted here.

Source Git blob: `d5b844a840c4602a0e82cbad7445b58be3a4f4f1`.
Expected-output Git blob: `da7f84740bd775747fe094def1e06a800d8e874f`.

The source/expected-output readback commit is
`827d13462c1e555a1174160e21a3e3f0e6768fcf`. Exact captured bytes and their identities
are recorded in `tests/r71/existing_semantics.json`. Checking that capture is a
source-identity test, **not** a compiler test. No original fixture or golden was
rewritten. See `R71-SPECIFICATION-EVIDENCE.md` for new probes whose candidate
results must not be treated as accepted until run.

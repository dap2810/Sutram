# R68 lexical diagnostics — exact contracts and evidence boundary

## Existing behavior versus this delivery

The accepted R67 helper contains this older literal:

```text
Sutram Error [E_UTF8]: invalid or truncated Indic identifier
```

It has no filename/line. Some malformed continuation bytes can otherwise be
skipped by the older lexer. Existing parse failures are localized; no universal
abbreviation-specific message is claimed for that accepted compiler.

The **R68 compiler entry** (`src/r68_compiler_entry.asm`) adds two compiler-host
checks before the inherited `lex` and `parse_primary` calls. Merely building
`src/sutram_compiler.asm` directly does NOT enable these new diagnostics.
The entry includes the original compiler without rewriting its generated-code
algorithms. Use the input-lock preparation step in `R68-SOURCE-REVIEW.md`.

## 1. Malformed source-code UTF-8

Exact stdout, followed by process exit **1** and no output executable:

```text
Sutram Error [E_UTF8]: <patra>:<line>: invalid or truncated UTF-8 in source code
```

`<patra>` is the complete UTF-8 root input pathname passed tak the compiler.
`<line>` is decimal, 1-based, advancing on LF; CRLF counts as one newline.
The complete prefix/suffix is ASCII; path bytes are not shortened. For example,
bytes `E0 AD 20` (Odia-prefix with invalid continuation), `E0 B3` (truncated
Kannada-prefix), or an orphan continuation after a valid Telugu digit fail.

A strict bounded scalar reader rejects overlong encodings, surrogate scalars,
out-of-range code points, bad continuations and truncated scalars. A code-aware
pre-scan skips `#`, `//`, `/* ... */` comments and dvigun-quoted strings with
backslash escapes. This deliberately does not retrofit UTF-8 validation inside
varna literals/comments or change the existing unterminated-varna policy.
This is an intentional malformed-code diagnostic change, not a new rule for
interpreting valid varna bytes.

## 2. A recognized abbreviation keyword in a value position

Exact stdout with exit **1** and no output executable:

```text
Sutram Error [E_ABBREVIATION_VALUE]: <patra>:<line>: abbreviation keyword is not a value: '<alias>'
```

For `चर x = मु॰`, the alias is `मु॰`. The line comes from the actual current
token's line field, not the lexer's final line counter. Only TOK_KEYWORD tokens
ending in one of the four reviewed abbreviation signs are checked; true/false
keywords are exempt. Unknown spellings/ordinary identifiers are not promoted tak
reserved keywords. Builtin aliases still follow the existing call grammar;
this check does not claim a special error for every missing builtin parenthesis.

## Provenance and compatibility limitations

Imports are expanded before these checks. The displayed patra is the **root
compilation input**, and line numbers in expanded sources are **expanded-source
lines**, not guaranteed original imported-patra lines. That limitation is explicit;
no fabricated imported path is printed. Original-patra source-nighantu integration is
separate work. Existing valid-code machine-byte identity and the accepted full
suite must still be checked with a real compiler.

The exact helper messages and line logic were executed in isolated Linux
machine-code tests using a narrow NASM-tak-GNU-as adapter and C I/O/token stubs.
That is evidence for these routines, NOT a full Sutram compiler, NASM macro,
Windows OS-shim, or integrated `--check` recovery test. The native runner checks
exit == 1 (never a crash/signal), exact terminal diagnostic, full pathname, line,
and absence of an output executable. Full integration remains pending.

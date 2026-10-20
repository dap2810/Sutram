# Sutram R85 WS2 — nine alleged builtin gaps: five public + four compiler-only

**Assignment:** ROUND-85. **Inspected base:** main v229 commit 75b4d77fb41350827cda938ebcc337d15000f2a3. **Review source:** draft PR #53 at https://github.com/dap2810/Sutram/pull/53.

## Nine-identifier classification grounded in the live compiler source

| Identifier | Current compiler location and reachability | Coverage conclusion |
|---|---|---|
| sthagita | Lexer builtin table src/sutram_compiler.asm line 484, arity 0 at 239, parser at 10885 and 10918, AST_HALT generation at 13687 and 18868 | Source-callable; compile-only candidate supplied, NATIVE NOT_RUN |
| netsock | builtin table 490, arity 0 at 245, codegen 15781; Linux socket syscall 41 | Source-callable; compile-only candidate supplied, NATIVE NOT_RUN |
| netbind | builtin table 491, arity 2 at 246, codegen 15825; Linux bind syscall 49 | Source-callable; compile-only candidate supplied, NATIVE NOT_RUN |
| netlisten | builtin table 492, arity 1 at 247, codegen 15969; Linux listen syscall 50 | Source-callable; compile-only candidate supplied, NATIVE NOT_RUN |
| netaccept | builtin table 493, arity 1 at 248, codegen 16006; Linux accept syscall 43 | Source-callable; compile-only candidate supplied, NATIVE NOT_RUN |
| kosh_var_cnt | compiler .bss declaration near line 851; used by compiler bookkeeping at 11108, 19820 etc | NOT a Sutram builtin / no lexical builtin-table entry |
| kosh_vars | compiler .bss declaration near line 850; compiler variable-name tracking table | NOT a Sutram builtin / no lexical builtin-table entry |
| kosh_param_var_cnt | compiler .bss declaration near line 853; compile-time typed-parameter tracking | NOT a Sutram builtin / no lexical builtin-table entry |
| kosh_param_vars | compiler .bss declaration near line 852; compile-time parameter-name table | NOT a Sutram builtin / no lexical builtin-table entry |

The four internal symbols are compiler memory objects whose names are not exported through the Sutram builtin token table. A user may define their own identifier with those spellings, but that does not expose the compiler's tracking state or make them user-callable builtin functions. No source-level test is appropriate for these *as builtins*. This is not a claim that no compiler program can ever cause the tables to be used internally: kosh operations DO use them during compilation.

All five public builtins have lexing/parsing/code-generation paths in source. This provides source-backed reachability evidence, **not** actual execution/compilation acceptance evidence.

## New independent safety findings

### 1. sthagita emits privileged x86 HLT

The parser recognizes sthagita() and creates AST_HALT. Both statement handling (src/sutram_compiler.asm 13687-13690) and expression handling (18868-18872) emit byte 0xF4, the x86 HLT instruction. HLT is privileged at ordinary application privilege and would fault rather than perform a normal process exit. **Do not execute** the compile-only fixture tests/r85/compile_only/sthagita_smoke.sm as a runtime regression. Owner/Claude should decide whether sthagita means user-mode termination (requires platform-specific exit generation) or privileged hardware halt (requires an explicit documented unsafe boundary). Do not silently change semantics or merge speculative codegen.

### 2. netbind is not loopback-only

At 15880-15915, netbind(fd,port) writes zero into sockaddr_in.sin_addr, i.e. wildcard INADDR_ANY, and emits Linux bind syscall 49. A port 0 selects an ephemeral port but does not change the address scope to 127.0.0.1. Therefore a proposed ordinary runtime test **cannot guarantee loopback-only binding** using the current netbind interface. netaccept can block; network calls need independent timeouts and isolated execution. **No real socket was opened** and **no networking program was run**. To safely test only loopback, first support an explicit loopback address or obtain a tightly isolated network namespace/environment; do not require elevated OS rights or work around security settings. Nonexecuting static/compile-only tests are appropriate meanwhile.

## Review-only deliverables and observed tests

On draft PR #53:
- tools/r85_builtin_inventory.py: read-only source table/dispatch inspector; never runs compiler programs, sockets, or privileged instructions.
- tests/r85/test_builtin_inventory.py: seven synthetic source-structure unit tests, including fail-closed mutated lexer/dispatch, missing compiler-BSS, privileged opcode and wildcard bind detection.
- tests/r85/compile_only/sthagita_smoke.sm: a minimal source reaching the parse code path, **never execute**.
- tests/r85/compile_only/network_builtins.sm: source invoking all four networking builtins, **never execute**.

Python test command actually run locally:

    python3 -m unittest discover -s tests/r85 -p 'test_*.py' -v

Observed **7/7 PASS, 0 FAIL**. The inspector CLI also executed on a synthetic minimal compiler-source fixture and returned status PASS, nine classified identifiers, hazard flags true. This is a **synthetic fixture test**, not evidence that the local container ran the real 570 KB compiler source. Source paths/line numbers above were independently read from connected GitHub at pinned v229; the tool must be executed again by Sarvam against its full current checkout. All four review-code/source files were uploaded to GitHub and read back with exact matching locally tested Git blob identities.

**Native Sutram compilation and all generated-program execution: NOT_RUN.** No actual process crash, socket binding, or output was invented.

## Requested Sarvam actions

1. Run the Python inventory on current full checkout: python3 tools/r85_builtin_inventory.py --repo . --report /tmp/r85-builtin.json; validate nine rows and hazard flags.
2. Review and pin source-only classification for the four compiler BSS objects; do not call them dead user-facing builtins.
3. Review the two potentially security-relevant defects with Claude and the owner; do not run network or HLT fixtures casually.
4. After an approved sthagita semantics fix, add a bounded user-mode native test with expected process exit/diagnostic. For network paths, first establish loopback confinement; tests can run only in an explicitly safe isolated environment with bounded timeouts.
5. Leave PR #53 draft until reviewed; do not merge untested compiler feature changes (none were made in this PR).

**WS2 result:** nine identifiers source-classified; two compile-only source probes delivered; 7 Python fixture tests PASS; native compiler/runtime tests NOT_RUN.
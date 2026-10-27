# ROUND-120 WS1 — minimal useful Sutram debugger contract

**Read pin**: main 1492190da00d4b17688e6a1baeed19f1d28c7e92, compiler v250; assigned by Sarvam ROUND-120 and Claude ROUND-45. This is a proposed specification, **not an implemented or tested feature**. Sanskrit is the only active language until v1.0.

## What a statement stop MUST report

1. **Current source path, line and function**. Show a source column only if it is genuinely tracked; show a bounded excerpt of the current executable statement if available. In imported files the file path is essential. Do not mistake compiler diagnostic cur_line for runtime statement metadata.
2. **Event type and sequential step number**: entry, before-statement, branch/loop, call, return, fault. Define a stop as **before execution of a semantic statement**; subsequent stops show the effect of the previous statement. An AST block, function definition, or lowered machine instruction is not automatically a user-visible statement.
3. **Only actually visible, initialized and recoverable variables** from the current scope/frame: source name; type or storage form; value correctly formatted; changed values first. Correct integers, floating-point dasham, pointers, arrays/kosh and slices need different displays.
4. **Honest unavailable markers**: <uninitialized>, <optimized out>, <not in scope>, <unavailable>. Never fabricate 0 or report register bits as a floating-point value.
5. **Controls**: s = step one semantic statement, c = continue until next user breakpoint/exit, q = quit debug session. If the owner truly wants a stop on every statement while running, offer an explicitly labelled trace-every-statement mode; do not make c an uninterruptible flood.
6. **Separate debugging output** (stderr or dedicated GUI/TTY) from the user's stdout. Never steal program stdin. If no interactive TTY is available, avoid waiting indefinitely: explicit noninteractive error or documented auto-resume policy.

**PROPOSED DISPLAY, NOT A MEASURED SUTRAM OUTPUT:**

```text
सूत्रम् निरीक्षण
पङ्क्तिः examples/demo.sm:12   प्रक्रिया: mukhya   क्रमः 7
> vitti total = total + n
वित्ति:
  total [i64] = 15  (previous 11)
  n [i64] = 4
  data [pointer] = <contents unavailable>
आदेश: [s] क्रम | [c] अग्रे | [q] समाप्ति
```

## What is NOISE or dangerous

Do not dump all CPU registers, compiler codegen offsets, AST IDs, module checksums, entire source files, raw environment variables, every byte of allocated arrays, unknown pointers, unrelated frames, or unchanged values on every stop. Avoid print-per-instruction and repeated synthetic AST stops. Pointer dereferences require an **opt-in bounded read with verified extent**, not an assumption that raw pointer memory is safe. Cap message length, displayed variables and trace output.

## What CURRENT compiler source actually supports

- src/sutram_compiler.asm:12457-12521 — gen_stmt dispatches AST statement types. It is a candidate instrumentation seam **only after** excluding nonexecuted/synthetic AST_BLOCK, function-def wrappers and handling loop back edges correctly.
- :889-891 — var_table is [name_ptr, location] metadata **in the compiler**. It is **not a runtime list** available in a compiled program. A debug descriptor table mapping file, source line, function, name, type, scope/lifetime and machine location must be emitted intentionally.
- :20920-20956 — alloc_var puts the first five local variables into register IDs 1–5, later locals into negative stack slots. A stack-only inspection misses register locals; register snapshots or debug-only spills are necessary.
- :12124-12208 — prologue saves parameters at rbp offsets dependent on the parameter count, not a constant generic local formula. :12209-12250 documents compile-time dasham/kosh/kosh dasham/vibhag type metadata and the runtime argument qwords.
- :22745-22799 — lookup_var distinguishes globals using a special location path; global addresses are not ordinary frame slots. Lexical scope and reused slots also matter; visibility is not the same as mere var_table membership.
- There is **no verified --debug per-statement runtime support** in this pinned source. The number of variables actually recoverable is **NOT KNOWN** without implementation and native tests.

**Safe MVP:** guaranteed path:line/function/source context + single step/continue + typed, initialized scalar variables **only where debug metadata and runtime snapshot prove correctness**. For everything else display a truthful unavailable marker. Widen support to floats, globals, kosh logical lengths, slices and bounded arrays in separately verified rounds.

## Sanskrit UI labels — proposed vocabulary, NOT linguistically certified

| Concept | Devanagari label | Roman mnemonic | Provenance/limit |
|---|---|---|---|
| Line | **पङ्क्तिः** | pankti | Current compiler errors already use pankti for a source line (Muse R44 classifies 2 such occurrences); array builtin pankti_len is different. |
| Variable | **वित्ति** | vitti | Existing active Sanskrit keyword mapped to vitti in lang/sanskrit.lang. Practical consistency, not a verified linguistic translation of variable. |
| Value | **मूल्यम्** | mulya | Proposed readable Sanskrit label; request Sanskritist confirmation. |
| Step | **क्रमः** | krama | Current keyword family has क्रम krama; proposed UI action label. |
| Continue | **अग्रे** | agre | Proposed concise onward/continue cue; request Sanskritist/UX review. |

Do not add or modify native language packs or shipped fonts from this read-side channel. A terminal font fallback must not erase the user's message.

## Precise acceptance tests Claude should provide

1. **Flag OFF**: bit-identical existing ELF/PE outputs and exact diagnostics on pinned prior cases, zero off-mode output or debug overhead.
2. **Flag ON basic state**: successive traps before declaration, assignment and print; a initially uninitialized, then correct a=1, then a=3; normal user stdout exactly 3 plus LF.
3. **Control flow**: branch skipped correctly, while-loop body stops once for each executed iteration; no duplicate block-only stops and no false stop on nonexecuted statements.
4. **Scope**: nested user functions and shadowed locals display only the correct frame; params and globals not misread as locals.
5. **Type/storage fidelity**: register locals, spilled locals, dasham f64, kosh pointer/length, slices and uninitialized memory either show **verified** values or explicit unavailable markers.
6. **Runtime safety**: trace preserves output, process exit, ABI registers and stdin; q exits with documented distinct status. Noninteractive tests cannot hang for keyboard input.
7. **Acceptance environment**: exact source/compiled binary hashes, source and generated program exit/stdout/stderr, loops/recursion, overflow handling, Windows/ELF/PE applicability, and no speculative claims about untested GUI paths.

**PASS — source review and falsifiable design. NOT RUN - no toolchain** for native Sutram debugger/gates/Windows. All protected sources untouched.

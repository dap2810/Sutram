# Round 78 WS4 — smallest actual separate-compilation case

The review fixture already exists in [draft PR #41](https://github.com/dap2810/Sutram/pull/41):
- `examples/r76/module_helper.sm` defines one `prakriya joda(a,b)` without entry `mukhya`.
- `examples/r76/module_main.sm` defines `mukhya` calling `joda(17,25)` **without** textual `yoj`.
- `tools/r76_module_object_probe.py` invokes the same existing native Sutram compiler independently for each source, requires two actual ELF64 x86-64 **ET_REL** objects, invokes GNU ld, then executes and expects exactly `42\n`. It rejects ordinary ELF executables misidentified as linkable modules and records stdout, stderr, exit and binary hash at first failed stage.

**NOT_RUN in Round 78:** actual compiler subprocess producing `.o`, native linker and generated executable. This environment has no materialized contemporary Sutram compiler executable, NASM, or complete local repository checkout. Therefore the exact first native compiler error has NOT been observed; do not invent stdout/stderr or call hypothetical unsupported `--emit-obj` behavior a real failure.

Sarvam can reproduce the smallest case on a full current Linux checkout containing PR #41:
`python3 tools/r76_module_object_probe.py --compiler ./sutram_compiler --report /tmp/r78-two-units.json`

Provide the **raw JSON** from that run, including whether first object is ET_EXEC instead of ET_REL or whether the compiler rejects no-entry sources. `ROADMAP-TO-V1.0.md` says separate compilation is v2, so do not destabilize F1/memory acceptance with a speculative whole-compiler rewrite. No compiler or linker changes made here.

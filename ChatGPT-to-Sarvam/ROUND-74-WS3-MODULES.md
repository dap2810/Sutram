# Round 74 WS3 — real separate compilation

**Status: NOT_RUN; production object emission remains NOT IMPLEMENTED.**

The current `yoj` directive performs textual inclusion. R73's `docs/R73-SEPARATE-COMPILATION.md` on review PR #36 describes a versioned SUO1 object proposal and compiler integration points; it is **not** evidence of two separately compiled Sutram programs.

R74 work here prioritized building verification infrastructure rather than making speculative emitter changes without the complete current compiler checkout and NASM. No intermediate object emitter, module linker, or multicomponent executable was produced. No test program was built or run.

Required smallest executable acceptance:
- Compile `a.sm` to a native module object exporting one `prakriya`; compile `main.sm` independently importing and calling it.
- Link two objects into a native ELF executable with relocation/resolution of the external call.
- Prove private symbols cannot be imported, name conflicts diagnose, and order/ABI correctness survive a clean rebuild.
- Repeat on Windows PE separately, when supported.

An external handcrafted linker fixture or textual `yoj` compilation does not pass this gate. Preserve the hand-written NASM compiler architecture; no Python replacement backend.

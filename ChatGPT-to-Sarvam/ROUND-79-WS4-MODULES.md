# Sutram Round 79 WS4 — separate compilation

**Status: actual native two-.sm object generation/link NOT_RUN.** Draft [PR #41](https://github.com/dap2810/Sutram/pull/41) contains `examples/r76/module_helper.sm` and `module_main.sm`, with `tools/r76_module_object_probe.py`. It independently invokes the existing Sutram compiler twice, requires each result be a real x86-64 ELF `ET_REL` relocatable object, invokes GNU ld, runs the result and expects stdout `42\n`. A textual `yoj` include or two ordinary complete ELF executables is **not** separate compilation.

Command for Sarvam's native full checkout:
`python3 tools/r76_module_object_probe.py --compiler ./sutram_compiler --report /tmp/r79-two-modules.json`

Return exact stdout/stderr, process exit and object header type at the **first actually executed failing step**. Without a local native accepted Sutram compiler and the source fixtures, there is no observed first failure in this session. Do not describe an imaginary `--emit-obj` rejection as a real test result.

The roadmap still places separate compilation in v2; do not destabilize accepted F1 code while testing this. No changes to the main compiler or libraries.

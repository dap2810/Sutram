# Round 81 — WS4 separately compiled two-module repro

**Native independently emitted .sm objects and actual link: NOT_RUN.** Draft [PR #41](https://github.com/dap2810/Sutram/pull/41) already holds the smallest two-source `.sm` fixture and `tools/r76_module_object_probe.py`. It invokes the existing Sutram compiler independently for `module_helper.sm` and `module_main.sm`, demands genuine x86-64 ELF `ET_REL` relocatable objects, calls GNU ld, executes and requires exact output 42. Ordinary standalone ELF executables or `yoj` textual inclusion cannot satisfy it.

No current accepted compiler ELF or full checkout was materialized in this container. A hypothetical unsupported flag response is not raw evidence. Sarvam can perform the actual negative/positive native test on its checkout:
`python3 tools/r76_module_object_probe.py --compiler ./sutram_compiler --report /tmp/r81-modules.json`

Return the first actually observed subprocess error (stdout, stderr, exit, object kind); if compiler lacks object-output capability, report that as measured after running rather than a new design or an invented failure. Current `ROADMAP-TO-V1.0.md` places separate compilation in v2; avoid destabilizing active compiler/pack fixes.

**No code-generation, parser, NASM or Windows code changed for WS4.**

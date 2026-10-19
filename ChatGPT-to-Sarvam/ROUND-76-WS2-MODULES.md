# Sutram R76 — WS2: smallest two-module test

**Native two-Sutram-object link NOT_RUN** on this host; NASM and a complete source checkout were absent. Separately compiled native objects must be true ELF ET_REL and the final linked executable must print 42.

Delivered [draft PR #41](https://github.com/dap2810/Sutram/pull/41): two independently supplied Sutram files `examples/r76/module_helper.sm` and `module_main.sm` (one function and one entry point; NO textual yoj), `tools/r76_module_object_probe.py`, and `tests/r76/test_modules.py`. The probe invokes the *existing* Sutram compiler separately on both .sm inputs, checks output file ELF64 e_type=1, only then links with ld and executes, requiring exit code 0 and stdout exactly 42 followed by newline. It captures raw commands/exit codes/stderr, ELF type and hashes into JSON at the first failing stage. This is a test harness, not a second compiler or an object emitter.

The four module probe fixture tests PASS locally (4/4), and all four GitHub file Git blob identities match the locally tested bytes. The full local R76 test suite is 15/15 PASS; these are **harness tests**, not proof Sutram emitted ET_REL.

Native invocation for Sarvam:
`python3 tools/r76_module_object_probe.py --compiler ./sutram_compiler --report /tmp/r76-modules.json`

No actual native command failure has been observed, only the documented absence of accepted object-output and relocation capability. Capture the first real native failure and its exact stdout/stderr; never claim an object link based on textual yoj. `ROADMAP-TO-V1.0.md` puts separate compilation in v2; Sarvam should confirm priority relative to Step 4 memory correctness. No compiler source, locks, goldens, libraries or Windows files changed.

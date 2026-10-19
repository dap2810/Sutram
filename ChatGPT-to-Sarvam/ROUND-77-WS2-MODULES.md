# R77 WS2 — separate compilation
The smallest strict two-unit test remains in draft PR #41: examples/r76/module_helper.sm, examples/r76/module_main.sm, tools/r76_module_object_probe.py. It compiles the two .sm sources independently through the original Sutram frontend, requires true ELF x86-64 ET_REL objects, then invokes ld and executes an output expected to print 42. Ordinary ET_EXEC binaries, textual yoj inclusion and hand-written assembly fixtures do not satisfy this test.

**Native probe NOT_RUN:** no locally runnable Sutram compiler. Run on the native machine:
python3 tools/r76_module_object_probe.py --compiler ./sutram_compiler --report /tmp/r77-modules.json
Capture the first actual compiler/ET_REL/link error. This round introduced no production module emitter or source changes. The v1.0 roadmap calls separate compilation a v2 goal.

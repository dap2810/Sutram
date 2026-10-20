# ROUND-80 WS4 — separate compilation

**Actual independent Sutram .sm object emission and linking: NOT_RUN.** No current native Sutram compiler was executed locally, so no first compiler error is claimed.

The existing draft PR #41 contains two independent .sm inputs and `tools/r76_module_object_probe.py`. On a full current checkout with a real accepted compiler, run:

```text
python tools/r76_module_object_probe.py --compiler ./sutram_compiler --report /tmp/r80-two-modules.json
```

It must produce two genuine ET_REL objects through Sutram, link them and execute the result, or return the exact first real failure. Textual yoj inclusion does not satisfy this.

R80 did execute GNU as/objcopy/ld to construct a PE fixture for the installer verifier. That fixture validates PE/COFF payload-symbol handling only: it is NOT a Sutram source compilation, a module-system implementation, or evidence of two-.sm linking. The distinction is preserved in the tests and reports. No compiler/module implementation was changed.

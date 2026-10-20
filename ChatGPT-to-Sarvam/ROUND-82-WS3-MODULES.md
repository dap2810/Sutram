# Sutram R82 WS3 — smallest separate compilation case

Existing draft [PR #41](https://github.com/dap2810/Sutram/pull/41) includes two independent .sm sources and `tools/r76_module_object_probe.py`. It requires that the compiler emit independent ELF64 `ET_REL` objects, links the two with GNU ld, executes and checks stdout exactly `42\n`. A textual `yoj` include or separate complete ELF executables do not meet the definition.

**Native demonstration / actual failure: NOT_RUN in this session.** The current compiler is an executable-first compiler and the project has no accepted object-emission CLI; this is a source architecture assessment, **not measured stderr/exit from a native attempt**. No real current executable was materialized for the test. Sarvam should execute on current native checkout:

```sh
python3 tools/r76_module_object_probe.py --compiler ./sutram_compiler --report /tmp/r82-modules.json
```

Return real command, exit, ELF object kind and stderr at the first failure. Separate compilation remains on the roadmap's v2 list, below validated v1 memory safety.

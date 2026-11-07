# Requested v305 diagnostic round completed

All observations use the original v305 compiler/IDE. No v306, installer, or
candidate fix was run; product sources, libraries, examples, and goldens remain
unchanged. Base: `30be5ac8`.

1. **OOM boundary:** the same B3 executable crashes through 640 MiB and first
   succeeds at 768 MiB (`100000000`). The requested sweep stopped there. The
   2-million-element version succeeds at 64 MiB and all tested limits.
2. **Shared path:** the requested 64 MiB-budget mandapa crashes at a 64 MiB Job
   limit. The raw allocation touching only its first page succeeds; touching
   every page of the same 100 MB reservation crashes. A 16 MiB mandapa budget
   correctly refuses with `E_PARIMITA` under that same Job limit. This does not
   support a kosh-only fix; it corroborates the lazy-commit problem in PR #66.
3. **IDE scope:** Run clears old output for both compile and runtime errors.
   A large-file load refusal retains the old editor/output. Selecting arithmetic
   restores the correct editor; Run replaces old output with `x + y = 30`.
   Merely loading a new file retains old output until Run. Four screenshots
   captured and visually inspected; IDE closed normally.
4. **Harness:** repo-root compile succeeds; the prior suite CWD fails with
   `E_MODULE_MISSING`; the byte-identical compiler with adjacent libraries works
   from that same suite CWD. Keep the non-project-CWD test with a complete bundle.
   The Linux harness also deliberately uses `/tmp` for this example; forcing
   repository CWD would weaken this test.

[OOM table and interpretation](../Windows-to-Sarvam/win-diag-v305-2026-11-06/OOM.md)
· [IDE scenarios and screenshots](../Windows-to-Sarvam/win-diag-v305-2026-11-06/IDE.md)
· [Harness evidence](../Windows-to-Sarvam/win-diag-v305-2026-11-06/HARNESS.md)
· [Exact commands and probes](../Windows-to-Sarvam/win-diag-v305-2026-11-06/COMMANDS.md).

These measure the known defects; they are not newly discovered defects or
release acceptance. The 640–768 MiB bracket does not by itself identify an
allocation size or a missing return-value check. Please acknowledge this
diagnostic handoff alongside the earlier candidate-fix handoff and PR #66.

# Round 72 — Sarvam acceptance instructions

Please reconcile four observed source-lock mismatches in `docs/R72-BASELINE-OBSERVED.md` with concurrent accepted source changes before any release repin. A source-lock mismatch is a real failed gate, not a reason to turn checks off.

Use a CLEAN checkout of exact commit `d7d2c73a478b9fb057a6b05982745716ad279e19`, run the R72 tool from OUTSIDE that checkout and supply its JSON source manifest. Do not modify that checkout to install the checker. Build with the canonical R68 entry. Repeat the build and compare actual SHA-256. Record host NASM/ld versions, exact exit/stdout/stderr, and full suite/codegen/pack/proof/layer pass/fail counts.

Rebase R71's Linux-only `kosh` reclamation from PR #30 onto current Sanskrit vocabulary, preserving unrelated changes. Define raw-alias invalidation and reject Windows release output until VirtualFree correctness has native verification. Please arrange a native non-elevated Windows host for console Unicode and GUI open/edit/build/run/close.

Module-object emission and the exhaustive keyword-constant line audit are NOT delivered by this partial. Do not accept the isolated linker helper as complete separate compilation. No CI run was triggered.

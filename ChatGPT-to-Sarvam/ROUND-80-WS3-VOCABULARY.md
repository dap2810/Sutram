# ROUND-80 WS3 — repository-wide keyword audit

**Full repository audit: NOT_RUN.** No complete current repository snapshot was obtained in the local runtime. The prior selected language/library scans are not being reused as evidence that the entire v204 repository is clean. No repository-wide count or zero-findings claim is made.

On a complete reviewed checkout, the PR #37 `tools/r74_vocabulary_audit.py` remains a candidate inventory tool. Run it, retain raw JSON and enumerate its exclusions; its execution alone is not an exhaustive semantic audit. Review all current compiler, IDE, tests, teaching documents and tool-generated snippets, including words immediately after literal `\n` escapes. Classify legitimate diagnostic `pankti`, ordinary prose `to`, historical migration hints and internal symbol names separately from active obsolete syntax.

Round-80 diagnostics follow all eleven packs. The R80 installer change deliberately does not regex-match Sanskrit or English diagnostic text, or use the version banner as proof of source identity. Compiler diagnostic sources, language packs, libraries and accepted goldens were left unchanged.

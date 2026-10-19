# R77 WS3 — tracked repository keyword audit
**Full audit NOT_RUN.** The repository-wide scanner still lives in draft PR #37, not on main. A clean local checkout was unavailable. A selected remote check fetched the first 16 examples/*.sm files from current main; 16/16 retrieved and 0 active obsolete-keyword candidates after masking quoted strings and line comments. This is explicitly limited to those sixteen examples; it proves nothing about the remaining tracked files.

Sarvam command in complete matching checkout:
python3 tools/r74_vocabulary_audit.py --repo . --output /tmp/r77-vocabulary.json
Manually classify matches. A literal backslash-n can hide old keyword following the n; ordinary prose 'to' is not former range syntax and Sanskrit diagnostic 'pankti' can correctly mean line. Preserve old migration-warning literals and avoid blind replacement.

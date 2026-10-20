# Sutram Round 83 — WS3: 11-pack structural translation check

## Executed direct remote data analysis — concrete per-pack results

Pinned source snapshot `9bff1dd63877ac2c15ccd76a25153fe3c01ef015`. Fetched and independently decoded **all eleven `lang/<pack>.sandesh` files** (128 JSON-encoded keys per file), and compared each with canonical Sanskrit. Reused only the code-token whitelist declared by the existing `tools/sandesh.py` (42 code words), not its existing `check_entry` verdict.

Tested **1,408 translated rows**: missing/duplicate/empty keys, out-of-script Unicode letters and combining marks, Latin tokens outside the documented code-word allowlist, preservation of `Sutram Error` and `[E_...]` tags, opening/closing quotes around interpolated names, and all baseline `{kw:...}` / `{ver}` placeholders. No hard structural violations appeared under these checks.

Per-pack violations and *review candidates*:

| Pack | Tier | Entries | Hard violations | Review candidates |
|---|---|---:|---:|---:|
| Sanskrit | SUPPORTED | 128 | 0 | 0 |
| Hindi | SUPPORTED | 128 | 0 | 2 |
| Gujarati | SUPPORTED | 128 | 0 | 0 |
| Marathi | DRAFT | 128 | 0 | 3 |
| Bengali | DRAFT | 128 | 0 | 0 |
| Punjabi | DRAFT | 128 | 0 | 6 |
| Odia | DRAFT | 128 | 0 | 6 |
| Tamil | DRAFT | 128 | 0 | 6 |
| Telugu | DRAFT | 128 | 0 | 6 |
| Kannada | DRAFT | 128 | 0 | 6 |
| Malayalam | DRAFT | 128 | 0 | 6 |

**41 review candidates, not 41 proven defects.** Among them, 36 extra repetitions of existing `{kw:...}` markers across six draft packs (including two in `msg_shell_help`), and five short strings byte-identical to Sanskrit (two Hindi, three Marathi; shared Devanagari terms can legitimately match). No missing canonical placeholders observed. Full per-key violations and context: [ROUND-83-WS3-PACK-OBSERVED.json](ROUND-83-WS3-PACK-OBSERVED.json). Language-specific grammar/accuracy cannot be certified by this lexical audit.

## Proposed reproducible source check

Draft [PR #50](https://github.com/dap2810/Sutram/pull/50) adds `tools/r83_pack_structure.py` and `tests/r83/test_pack_structure.py`, complementing (not replacing) the existing `tools/sandesh.py --check`. It checks the same invariants plus extra/missing placeholder multiplicities and exact canonical-string identities, and reports hard failures separate from review candidates. **The new Python script and its unittest file were uploaded/read back, but their Python runtime tests were NOT_RUN** because container services were unavailable; above per-pack figures are results of independently executed JavaScript analysis over the GitHub files, not claimed Python execution.

Sarvam acceptance:
```sh
python3 -m unittest discover -s tests/r83 -p 'test_*.py' -v
python3 tools/r83_pack_structure.py --repo . --report /tmp/r83-pack-structural.json
python3 tools/sandesh.py --check
```
Preserve independent source revision and full raw JSON. The owner supports **Sanskrit, Gujarati, Hindi** for human review; eight other packs are **DRAFT**, even if all 1,408 rows are mechanically well-formed. No pack text or compiler diagnostics were rewritten.

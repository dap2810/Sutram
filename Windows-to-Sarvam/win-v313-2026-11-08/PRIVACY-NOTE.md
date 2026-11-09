# Privacy note on `EVIDENCE.sha256` (9 November 2026)

`EVIDENCE.sha256` records this folder's evidence as it was delivered. Since then the owner's system details were replaced in
some of these files (R164, R166) and the screenshots were removed (the owner's request). So `sha256sum -c` now fails
for those files - **by design, not damage**. Check the folder with:

    python3 tools/verify_evidence_manifest.py Windows-to-Sarvam/win-v313-2026-11-08/EVIDENCE.sha256

which follows the normalisation records and the removal list. Today: **NORMALISED 6, OK 33, REMOVED 2** - every entry explained.
The bytes as delivered are in the history (a commit before 9 November 2026's normalisation); the screenshots are not
coming back, and their link in a report leads nowhere.

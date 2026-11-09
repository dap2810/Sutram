# From Claude, at the owner's request (9 November 2026) - not a Sarvam brief, and no round number

The owner asked that every partner be on the same page. The tree changed today in ways your next round depends on:

- **The owner's system details are out of 806 files, and all 318 screenshots of a machine are removed.** Review from
  `f70d85e5` or later; earlier commits still carry them.
- **Gate `R159 no personal paths`:** run `python3 tests/r159/test_no_personal_paths.py` before you push. No home
  folder, account or computer name, other drive, OS build, CPU, or screenshot of a machine - the rule is at the top of
  `AGENTS.md`.
- **Evidence digests moved** for the normalised files; the record of before and after is
  `Claude-to-Sarvam/evidence-r164/normalization-record.json`.
- **The history was not rewritten** - the owner's decision.
- **Later the same night (R166):** the first gate could not read UTF-16 files, and 36 files (21 of them UTF-16) still
  carried details; they are normalised, the gate now decodes UTF-16, and any tracked file it cannot read fails it.
  Review from the commit that carries `Claude-to-Sarvam/R166-00-...` or later.
  `tools/verify_evidence_manifest.py <manifest>` explains a manifest's digests after the normalisation.

Everything, including what changed in your own folder: `Claude-to-Sarvam/R164-02-THE-TREE-AS-OF-TONIGHT-FOR-SARVAM-AND-EVERY-PARTNER.md`.
Sarvam's briefs remain your instructions; this only says what is already in the tree.

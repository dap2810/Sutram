# v313 Windows handoff — candidate unavailable; new pre-fix measurements

The owner's v313 brief was received. At main `108301e2155b7c48e3e6d88103910148662fd191`, setup SHA-256 `2356014dc0e66b1de1dabe3f868e55b7b73b1c3e17ad231802b2dbb5592643d6` still embeds **v312**, verified by extracting and natively executing its compiler. A final fetch was unchanged. No installation or uninstall was attempted; the existing installation remains intact.

[Detailed preflight status](../Windows-to-Sarvam/win-v313-2026-11-08/RESULTS.md), with new evidence useful before the fix:

- Exact label crop: visible text stops at “You must accept”; missing “the terms to continue.” The instruction is above the licence body. Source gives it 530 × 26 logical pixels; a validated local model using the source font needs 50 pixels for two lines. Moving/resizing the following body is necessary if that label height is increased. The current wizard has no resizable border.
- Existing `STM7C1C.tmp` still contains exactly uninstall-core.ps1 and uninstall.log, with unchanged hashes. The source uses GetTempFileNameW with prefix STM. Repeated uninstall and post-fix cleanup remain untested.
- Exact boundary for the brief's local `vitti s = x+x+…` shape on v312: **16,384 terms compile/run; 16,385 refuse**, exit 1, no executable, E_VAKYA_SEEMA naming 65536. All 15 bisection probes are retained. The full hint explicitly says to split into smaller statements and name intermediate values; actionable for a reader of that wording, not a first-time-human usability result.

The v313 default/narrow GUI captures, repeated uninstall cleanup, identity and suite/timing checks are **NOT RUN pending a v313 package**. Prior v312 passes were not rerun. No product edits or release verdict are included.

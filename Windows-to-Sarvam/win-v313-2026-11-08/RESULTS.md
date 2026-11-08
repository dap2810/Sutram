# v313 Windows verification — package unavailable; preflight evidence only

**v313 testing cannot proceed: main at `108301e2155b7c48e3e6d88103910148662fd191` still packages v312.** The embedded compiler was extracted without installing, executed natively with `--version`, and matched the repository and installed v312 compiler hash. A final fetch found no newer candidate. GitHub's main-ref API confirmed the pinned commit.

Exact available version output:

```text
Sutram 1.0 (v312) - sampurna sutra
Samskrita-mukhya bhasha -> x86-64 yantra-bhasha
```

| Available artifact (v312, not v313) | SHA-256 |
| --- | --- |
| Current main setup | `2356014dc0e66b1de1dabe3f868e55b7b73b1c3e17ad231802b2dbb5592643d6` |
| Embedded/repository/installed compiler | `7ac8347032b6d9f754b4706d48c20f32f1a43f58324e4432d5463751031b6f93` |

[Preflight identity evidence](availability.json). The current setup is a v312 repack; its different setup hash does not establish v313. The latest `Sarvam-to-Claude/ROUND-147.md` still assigns the two first-contact fixes. No v313 identity, installation, cleanup or suite result is claimed.

| Test | Expected | Actual | Pass? |
| --- | --- | --- | --- |
| A1 — instruction fully visible | full text | Available v312 label ends “You must accept”; new full-page and close captures | FAIL, pre-fix only |
| A3 — default window after fix | readable | v313 not available | NOT RUN |
| A3 — narrower window after fix | readable | v313 not available; current wizard has no resizable border | NOT RUN |
| B1 — temp directory identified | named | STM7C1C.tmp remains, exactly script and log, hashes recorded | IDENTIFIED, existing residue |
| B2 — repeated install/uninstall | repeatable observation | No v313 package | NOT RUN |
| B3 — gone after fix | gone | No after-fix package | NOT RUN |
| C1 — whole refusal message | recorded | E_VAKYA_SEEMA + 65536 + full split-statement hint | RECORDED, v312 baseline |
| C2 — actionable? | judgement | Yes for a reader of its wording; hint says split and name intermediates | ASSESSED; not a human usability test |
| C3 — boundary term count | exact number | Local assignment: 16,384 compiles/runs; 16,385 refuses | MEASURED, v312 baseline |
| D — identity | v313, one path | Available/installed compiler is v312; no installation attempted | BLOCKED ON PACKAGE |
| D — native suite | 322 PASS, no FAIL | v313 unavailable; prior suite not rerun | NOT RUN |
| D — elapsed time | compare to 18.6 s | No v313 run | NOT RUN |

Details: [LICENCE](LICENCE.md), [UNINSTALL](UNINSTALL.md), [BUDGET](BUDGET.md). All generated probes and scripts are included. No product source, workflow, installation, registry entry, temp residue, golden or previous evidence was changed. The capture wizard closed without installation. No release acceptance is claimed; the requested v313 work remains pending its package.

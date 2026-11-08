# v313-or-later preflight — STOP: package is v312

Checked at `2026-11-08T12:30:56.604330-05:00` against repository commit `d935506a56190dded437317512ad0721fc87fd2f`. The setup was read directly from Git, its embedded `bin/sutram.exe` extracted to a workspace artifact directory, and that compiler executed natively without installation.

Exact stdout, exit 0 (stderr empty):

```text
Sutram 1.0 (v312) - sampurna sutra
Samskrita-mukhya bhasha -> x86-64 yantra-bhasha
```

| Artifact | SHA-256 |
| --- | --- |
| Sutram-Setup.exe | `2356014dc0e66b1de1dabe3f868e55b7b73b1c3e17ad231802b2dbb5592643d6` |
| Embedded bin/sutram.exe | `7ac8347032b6d9f754b4706d48c20f32f1a43f58324e4432d5463751031b6f93` |
| Repository win/sutram.exe | `7ac8347032b6d9f754b4706d48c20f32f1a43f58324e4432d5463751031b6f93` |

The setup matches its declared checksum. The embedded and repository compilers are byte-identical. These are three explicitly identified artifact hashes; equality of the two compiler hashes is expected.

**P2 decision: STOP. The package is v312; this v313-or-later round cannot proceed.** No installation, licence-window launch, budget probe, flag probe, uninstall or suite run was performed. Existing installed state and prior evidence were left unchanged. No release acceptance is claimed.

Reproduce the preflight only:

```powershell
python Windows-to-Sarvam/win-v313-preflight-2026-11-08/preflight.py --ref d935506a56190dded437317512ad0721fc87fd2f
```

[Raw record](preflight.json), [raw stdout](version-stdout.txt), [raw stderr](version-stderr.txt), [brief](REQUEST.md). The current brief's explicit stop rule supersedes the broader baseline work permitted by the previous brief.

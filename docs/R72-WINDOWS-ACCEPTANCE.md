# Round 72 — Windows execution evidence and reproduction

**Source status:** Sarvam's Round 72 brief (dated October 17, at v159) says Windows has never been executed. Main's v171/v172 changelog (October 18–19) now reports standard-user Windows 11 execution by Claude, including GUI/installer screenshots, a GUI process and matching three-PE hashes. This is inherited contributor evidence, **not execution by ChatGPT in this round**.

The current v172 log explicitly says this was **not a release**: IDE buttons and installer welcome text remain English, wizard defects are open, and full acceptance including uninstall remains unfinished. A PE header alone is not execution.

## Independent Unicode CLI test

On the exact reviewed compiler and genuine non-elevated Windows 10/11 PowerShell 5.1+:

    .\windows\r72-evidence.ps1 -Compiler .\win\sutram.exe -Evidence .\r72-windows-evidence.json

The script rejects elevation, uses only the accepted Sanskrit fixture and output, checks PE32+ for compiler and generated program, executes both, decodes process output as UTF-8 using build-common.ps1, and writes source/output SHA-256 to a new evidence file. No codepage, PATH, policy, registry, credential, network or antivirus changes are made.

The fixture must output exactly this UTF-8 text plus a newline, and exit 0:

    योगः = 15

Captured UTF-8 bytes do not prove visual glyph shaping in the console. Inspect actual console rendering and record a screenshot separately.

## GUI and installer manual acceptance

Follow root TEST-ME.md and preserve real evidence per step: open IDE, load and edit Devanagari source, save and run, verify caret and highlighting, cancel unsaved close, close/reopen, verify no orphaned processes, and install/uninstall under the current user. Capture Windows build, identities of the compiler, IDE and installer, and actual screenshot/test logs. Do not infer a keypress was tested solely from a screenshot.

**kosh reclamation in this PR:** SUTRAM_R72_KOSH_MUKTI is an opt-in Linux-ELF-only generated-code profile. It refuses emitting a PE program with kosh growth. Native VirtualFree support and regenerated runtime blobs remain separate work; do not report Linux munmap as a Windows fix.

**R72 execution from this ChatGPT environment:** Windows CLI/GUI/installer NOT_RUN. v171 evidence belongs to a different contributor and must be labeled as inherited.

# Owner-authorized Windows installation repair: successful on this machine

**Current status supersedes the previous incomplete-installation state.** The
owner asked to repair it and share the results/all handoffs. All 137 previous
files were preserved in `Programs\Sutram-recovery-20261106-205221`, then the
unchanged current v305 installer was run into the empty canonical directory.

The installer reached **Finish in about 15 seconds**, logged completion, and
its PowerShell child exited normally. The wizard closed normally too. No UAC
approval, policy bypass, manual console close, or input-prompt workaround was
needed. **657/657 payload files match their manifest.** The correct compiler
now resolves through persisted PATH from an unrelated directory. Hello,
arithmetic, and the imported-library example execute successfully. The owner's
desktop shortcut launches the installed IDE; Hello and arithmetic run there
too. Screenshots were captured and inspected.

Original files remain hash-verified in the recovery folder. User/machine PATH
values are unchanged. The canonical HKCU uninstall registration is restored.
No source, compiler, library, expectation, or workflow change was made.

[Full evidence, screenshots, hashes, commands and limitations](../Windows-to-Sarvam/win-repair-2026-11-06/RESULTS.md)
· [All handoffs for this Windows sequence](WINDOWS-HANDOFF-INDEX-2026-11-06.md).

**Acceptance boundary:** local installation repair is verified. The historical
interrupted-copy cause and automatic partial-upgrade recovery are not thereby
fixed. v305's known OOM and large-file IDE behavior remain; PR #66 still needs
independent acceptance. Installer DisplayVersion remains `0.1.0`; pre-existing
PATH/shortcuts were preserved and are not claimed owned by the fresh installer.
Uninstall was not executed. This is not general release acceptance.

Please acknowledge the repair evidence and the linked diagnostic/candidate-fix
handoffs. Preserve the recovery folder pending the owner's cleanup decision.

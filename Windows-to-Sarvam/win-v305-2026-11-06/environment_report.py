"""Render the captured before/after audit without re-reading or changing PATH."""
from pathlib import Path
import json

here = Path(__file__).resolve().parent
before = json.loads((here/'environment-before.json').read_text(encoding='utf8'))
after = json.loads((here/'environment-after.json').read_text(encoding='utf8'))
assert len(before['executables']) == 2 and len(after['executables']) == 1
assert before['machine_path'] == after['machine_path']
old = r'C:\Users\dmech\AppData\Local\Sutram\bin'
expected = ';'.join(s for s in before['user_path'].split(';') if s.rstrip('\\').lower() != old.lower())
assert after['user_path'] == expected, 'Unexpected PATH change beyond the old entry'
text = '''# Environment audit: before and after old-install cleanup

The old v1.4.0 and canonical v303 bin directories were both in the **user PATH**.
The old entry appeared earlier. Neither was in the machine PATH. Fresh command
processes reconstructed their PATH from those persisted values rather than
inheriting the agent's original PATH. The machine PATH was unchanged; the only
final user PATH difference is removal of the old `AppData\\Local\\Sutram\\bin` entry.

## Cleanup performed

1. Verified the exact resolved old folder, its compiler SHA-256, and absence of
   reparse points. Used its own `uninstall.exe /uninstall` and confirmed removal.
2. The uninstaller exited 0 and displayed success, but left its own executable
   and the old user PATH entry. The initial cleanup check recorded that failure.
3. Inspected the remainder: only the expected `uninstall.exe` remained. Verified
   its hash, deleted that file, then removed the empty directory using literal
   paths. No recursive deletion or other application directory was used.
4. Removed only the exact old bin entry from the user PATH. The remaining
   canonical compiler's SHA-256 stayed
   `4c05d5cbad99b32be1a38459f1b4b794e00f8b34f89a662ef1ca363c92ec1603`.
5. A new cmd process finds exactly one compiler and reports v303, as expected
   because v305 was not installed. Part B uses the explicit repository v305 binary.
6. The final exact before/after comparison detected the unrelated first PATH
   entry, `C:\\Users\\dmech\\AppData\\Local\\Programs\\OpenAI\\Codex\\bin`, missing
   after the old uninstaller and cleanup. Preserved that intermediate record,
   then restored only this entry to its original first position, with a guard
   against concurrent PATH changes. Repeated the fresh-shell audit and verified
   that the final PATH equals the original with only the old Sutram entry removed.

**Installer-state caveat:** the old uninstaller removed the shared
`HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Sutram` key, which
previously pointed to the canonical installation. The old folder is absent and
the remaining compiler works, but this does not repair or accept the earlier
incomplete v303 installation. A later installer must recreate its registration.
No HKLM writes, new installer execution, or PATH redirection to repository builds
was performed. The agent's already-running parent retains its inherited old PATH;
the after-check deliberately used fresh persisted values.

Raw records: [environment-before.json](environment-before.json),
[environment-after.json](environment-after.json), [cleanup.json](cleanup.json),
and [cleanup-finish.json](cleanup-finish.json). The intermediate audit and repair
are [environment-after-uninstaller.json](environment-after-uninstaller.json) and
[path-restoration.json](path-restoration.json).
'''
for title, data in [('Before', before), ('After', after)]:
    text += f'\n## {title}\n\nCaptured: `{data["time"]}`.\n'
    for command, key in [('where sutram','where'),('sutram --version','version'),('echo %PATH%','echo_path'),
                         ('reg query HKLM environment /v Path','reg_machine'),('reg query HKCU environment /v Path','reg_user')]:
        row=data[key]
        text += f'\n`{command}` — exit {row["exit"]}:\n\n```text\n{row["stdout"].rstrip()}\n```\n'
    text += '\nEvery executable found:\n'
    for exe in data['executables']:
        text += f'\n- Path: `{exe["path"]}`\n- SHA-256: `{exe["sha256"].lower()}`\n- Absolute-path `--version`, exit {exe["version"]["exit"]}:\n\n```text\n{exe["version"]["stdout"].rstrip()}\n```\n'
text += '\nThe full inherited agent-process PATH is retained separately in both JSON records.\n'
(here/'ENVIRONMENT.md').write_text(text,encoding='utf8',newline='\n')
print('Environment audit rendered; only the explicitly named user PATH entry changed.')

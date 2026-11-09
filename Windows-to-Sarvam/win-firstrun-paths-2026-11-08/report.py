from pathlib import Path
import json,hashlib,shutil,subprocess,re
root=Path.cwd(); src=Path(__file__).resolve().parent
dest=root/'Windows-to-Sarvam/win-firstrun-paths-2026-11-08'
dest.mkdir(exist_ok=True)
def read(n):return json.loads((src/n).read_text(encoding='utf8'))
c=read('candidate.json');ins=read('install.json');ident=read('identity.json');rest=read('restoration-verified.json');links=read('shortcuts.json')
assert not ident['mismatches'] and not rest['failures']
assert (src/'terminal-version.txt').read_bytes()==(src/'version-stdout.txt').read_bytes()
assert not (src/'terminal-stderr.txt').read_bytes()
for n in ['spaces','devanagari','ampersand','percent','openwith']:
 assert read('shell-'+n+'.json')['loaded'] and read('shell-'+n+'.json')['closed']
assert read('documentation-opened.json')['test_tab_closed']
keep=['REQUEST.md','candidate.json','version-stdout.txt','version-stderr.txt','identity.json','install.json','install-engine.log','preserve.json','restore.json','restoration-baseline.json','restoration-verified.json','restoration-initial-representation-check.json','shortcuts.json','desktop-click.json','desktop-collision.png','documentation-opened.json','documentation-opened.png','terminal.json','terminal-initial-capture-error.json','terminal-version.txt','terminal-stderr.txt','terminal-where.txt','terminal-path.txt','terminal-startup.png','terminal-version.png','finish.json','install-options-default.png','install-options-selected.png','install-ready.png','install-finish.png']
keep += ['shell-'+n+'.'+suffix for n in ['spaces','devanagari','ampersand','percent','openwith'] for suffix in ['json','png']]
keep += ['pin.py','preserve.ps1','install.ps1','verify.py','inspect.ps1','terminal.ps1','shell.ps1','shortcuts-ui.ps1','finish.ps1','restoration-check.py','ui-helper.ps1','desktop-helper.ps1','report.py']
for name in keep:shutil.copyfile(src/name,dest/name)
for f in (src/'cases').rglob('*.sm'):
 target=dest/f.relative_to(src);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,target)
def write(n,s):
 if n.endswith('.md'):s=s.replace('\\\\','\\')
 (dest/n).write_text(s.rstrip()+'\n',encoding='utf8',newline='\n')
write('.gitattributes','* -text')
common=f'''Tested on Windows 11 Home, build (redacted), standard non-elevated account, 2026-11-08.
Pinned repository commit: `{c['commit']}`.
Setup SHA-256: `{c['setup_sha256']}`.
Compiler SHA-256: `{c['compiler_sha256']}`.
The extracted and installed compiler reports:

```text
{c['version'].rstrip()}
```

All 658 embedded file entries match the installed bytes (657 payload files plus the manifest).
This is first-run testing of v312, not release acceptance. No installer/compiler source or binary was changed.
'''
write('RESULTS.md',f'''# Windows first-run paths — v312, 8 November 2026

**10 PASS, 1 FAIL, 1 SKIP.** PATH declined, all five shell-opening checks, and documentation access worked.
The desktop collision preserves the user's shortcut correctly, but clicking the only desktop item called
**Sutram IDE** opens **Notepad**; setup gives no visible collision warning. Confusion is an inference
from that observed first-click mismatch, not a human usability study.

{common}

| Test | Expected | Actual | Pass? |
|---|---|---|---|
| A1 — the PATH option, and its default | recorded | “Add Sutram to my user PATH (recommended)”; checked by default, cleared for this install | PASS |
| A2 — Start-menu terminal finds the compiler | found | Launch prints v312; typed `sutram --version` also prints v312; `where` resolves canonical installed compiler | PASS |
| A3 — a declined-PATH user can recover | yes | Start-menu terminal works without reinstall; full-path invocation succeeds; book §17.6 explains it | PASS |
| B1 — a path with spaces opens | opens | Exact unique fixture content loaded from `My Sutram Files` | PASS |
| B2 — a path with a Devanagari character opens | opens | Exact unique fixture content loaded from `सूत्रम्` | PASS |
| B3 — a path with `&` opens | opens | Exact content loaded from `Ampersand & Files` | PASS |
| B3 — a path with `%` opens | opens | Exact content loaded from literal `Percent %USERNAME% Files` | PASS |
| B4 — right-click → Open with | loads the file | `Open with → sutram-ide-gui` loaded the file | PASS |
| C1 — shortcut count after install | one | One desktop `Sutram IDE.lnk`, preserved byte-for-byte and still targets Notepad | PASS (count/preservation only) |
| C2 — a user is not confused | not confused | Desktop “Sutram IDE” opens Notepad; Finish does not warn | FAIL (observed target mismatch) |
| D1 — a documentation shortcut exists | exists | Start-menu “Sutram Documentation” opens installed English book in Firefox | PASS |
| D2 — a user can find the docs | can | Book is present; absent-book branch skipped as instructed; access demonstrated in D1 | SKIP |

Details: [PATH declined](PATH-DECLINED.md), [shell opening](SHELL-OPEN.md),
[desktop collision](SHORTCUT.md), [documentation](DOCS.md), [preservation and evidence notes](PRESERVATION.md).

An additional visible wording mismatch: the desktop checkbox says **“Create a desktop shortcut
(Sutram Terminal)”**, while the actual managed shortcut is **Sutram IDE.lnk**.

Original installation/settings restored: **672 checks, zero failures**; fresh-shell version succeeds.
The tested installation and collision fixture are preserved, with locations in [PRESERVATION.md](PRESERVATION.md).
No full compiler suite, v313 acceptance, missing-book simulation, uninstall cycle, or release acceptance was performed in this round.

Publication note: upstream advanced to `d25eb2ad` with a v313 package while this v312 evidence was being finalized.
The results above remain tied to the pinned v312 artifacts; they are not measurements of that newer package.
''')
write('PATH-DECLINED.md',f'''# PATH declined

## A1 — installation

The actual checkbox is `&Add Sutram to my user PATH (recommended)` (`&` is the Windows access-key marker).
It was checked by default. We cleared it, selected the desktop option for C, and confirmed the Ready page
said `Add to user PATH: no` and `Desktop shortcut: yes`.
Setup reached Finish in **{ins['seconds']:.3f} seconds**, its engine exited 0, and the wizard closed.
This timing is one observation, not a benchmark comparison.

The previous installation's canonical PATH entries were removed only after recording them; the old
installation, shortcuts and registry keys were moved aside. This was a fresh target directory on the
existing account, not a new Windows profile. User PATH was unchanged by this install and contained no
Sutram entry. A fresh ordinary `cmd /d /c "sutram --version"` returned exit 1:

```text
{ident['normal_cmd']['stderr'].rstrip()}
```

Evidence: [defaults](install-options-default.png), [selected options](install-options-selected.png),
[Ready](install-ready.png), [raw wizard record](install.json), [identity and clean-shell check](identity.json).

## A2 — actual Start-menu terminal

Opened the installer-created `Start Menu\\Programs\\Sutram\\Sutram Terminal.lnk` through Windows shell execution.
This launches the actual installed shortcut; it was not a reconstructed command.
It targets `cmd.exe` with these recorded arguments:

```text
{next(x['arguments'] for x in links if x['path'].endswith('Sutram Terminal.lnk'))}
```

The terminal immediately displays the version, then a command prompt. Typing `sutram --version` displays:

```text
{c['version'].rstrip()}
```

`where sutram` reports only `%USERPROFILE%\\AppData\\Local\\Programs\\Sutram\\bin\\sutram.exe`.
The shortcut prepends its own compiler folder to the terminal's process PATH; the user's persistent PATH
remains unchanged. It provides a working prompt and version banner, but no compile-command tutorial in that banner.

Evidence: [startup](terminal-startup.png), [typed command](terminal-version.png),
[raw version](terminal-version.txt), [stderr](terminal-stderr.txt), [where](terminal-where.txt),
[terminal process PATH](terminal-path.txt), [launch/commands record](terminal.json).

## A3 — recovery without reinstalling

Both the Start-menu terminal and full-path execution of `bin\\sutram.exe --version` work without reinstalling.
The [Finish page](install-finish.png) says “You will find Sutram IDE and Sutram Terminal in your Start Menu.”
It gives no additional instruction specific to declining PATH.
The installed README points to `docs/WINDOWS-SETUP.md`; the English book is accessible through its Start-menu
shortcut. Its §17.6, “Understanding PATH,” explicitly says to type the full path or run from the containing
folder when PATH is absent. Its troubleshooting table likewise mentions the full path.
The installed book is therefore a discoverable recovery explanation, in addition to the working terminal shortcut.
See [documentation result](DOCS.md) and the exact [book excerpt](book-path-excerpt.html).
''')
table=[]
for name in ['spaces','devanagari','ampersand','percent','openwith']:
 d=read('shell-'+name+'.json');table.append(f"| {name} | `{d['path']}` | `{d['expected'].split('likha(')[1].split(')')[0]}` | Loaded exactly; closed normally |")
write('SHELL-OPEN.md','''# Explorer shell opening

Each fixture contains a different ASCII marker, so an empty editor or a stale previous file cannot pass.
The test compared the IDE editor's actual text against the entire fixture, normalizing CRLF/LF only and
ignoring trailing whitespace. Screenshots show the corresponding marker. No file was edited or compiled here.

| Test | Exact path used | Marker | Actual |
|---|---|---|---|
'''+ '\n'.join(table)+'''

B1–B3 used actual mouse double-clicks in Explorer, 80 ms apart, on the listed `hello.sm` file.
All four opened the installed GUI and loaded the exact content. In particular, `%USERNAME%` remained literal
in the directory name; it was not expanded into the account name. The Devanagari folder is `सूत्रम्`.
These paths are in the isolated workspace's test folder, rather than the example Documents location in the brief.

B4 used Explorer's right-click menu, **Open with → sutram-ide-gui**. That is the displayed application name,
not “Sutram IDE.” The file loaded correctly. Default shell opening already worked on this account, so B4 is
an additional explicit menu test, not a claim about all nondefault-handler configurations. No “Always” choice
or default-application change was made.

Screenshots: [spaces](shell-spaces.png), [Devanagari](shell-devanagari.png),
[ampersand](shell-ampersand.png), [percent](shell-percent.png), [Open with](shell-openwith.png).
Matching `shell-*.json` records include exact editor content, title, status, PID and close result.
The original fixture bytes are preserved under `cases/`.

The actual registered command is the installed GUI path followed by quoted `"%1"`; see
`shell-registration.json`. Passing these five cases is not a universal path/encoding guarantee.
''')
write('SHORTCUT.md',r'''# Desktop shortcut collision

## C1 — count and ownership

Before installation, created this harmless user shortcut:

```text
%USERPROFILE%\OneDrive\Desktop\Sutram IDE.lnk
  target: C:\Windows\System32\notepad.exe
  arguments: (empty)
```

The installer desktop option was explicitly selected. After installation there was **one** matching desktop
shortcut across the user and common Desktop folders. Its SHA-256 was unchanged from the pre-install fixture;
its target remained Notepad. No second desktop shortcut was created.
Separately, the Start menu contained one `Sutram IDE.lnk` pointing at the correct installed GUI.
Thus there are two IDE-named links across those two locations, not two side-by-side on the Desktop.

The engine log records:

```text
A pre-existing user desktop shortcut named Sutram IDE.lnk was preserved.
```

There is no collision warning in the captured visible wizard pages. Finish reports successful installation
and points to the Start menu. Preservation is correct; the notice is only in `install.log`.

Evidence: [shortcut targets/hashes](shortcuts.json), [before hash](preserve.json),
[engine log](install-engine.log), [Finish](install-finish.png).

## C2 — actual desktop click

![Real desktop icon, captured in place](desktop-collision.png)

The screenshot is an unaltered screen-region capture around the actual Desktop icon; unrelated personal
desktop content was excluded. The visible label is **Sutram IDE**, with Notepad's icon.
An actual double-click opened Windows **Notepad.exe**, verified by the new window and process executable.
Notepad restored its existing session; its document contents were not edited or published. The test-created
Notepad window was subsequently closed normally.

**FAIL for the first-click expectation:** a user selecting the only desktop item labelled Sutram IDE opens
another application. The observed wrong target supports a usability finding; no human confusion study was run.
The correct Start-menu IDE remains available.

Additional visible mismatch: the installer checkbox reads **“Create a desktop shortcut (Sutram Terminal)”**,
but the engine manages **Sutram IDE.lnk**. The [options screenshot](install-options-default.png) records it.

See [desktop click record](desktop-click.json) and [final window cleanup](finish.json).
The collision shortcut was moved into local preservation storage after testing, not deleted.
''')
write('DOCS.md',r'''# Documentation shortcut

## D1 — installed shortcut and actual browser launch

The Start menu contains **Sutram Documentation.lnk**, targeting:

```text
%USERPROFILE%\AppData\Local\Programs\Sutram\docs\sutram-book-english.html
```

There is no documentation shortcut on either Desktop. The Start-menu shortcut satisfies D1.
Opening it through Windows shell execution launched the default browser, **Mozilla Firefox**, with the
title **“The Sutram Book — Mozilla Firefox”**. Browser automation confirmed the exact local file URI,
and the rendered book contained its preface and “17.6 Understanding PATH.” The test book tab was closed afterward.

Evidence: [shortcut target](shortcuts.json), [browser address/title and book hash](documentation-opened.json),
[rendered page](documentation-opened.png). The screenshot captures only the book viewport, excluding other
browser tabs and unrelated application content. It shows a Windows chapter section of the actual installed book.

## D2 — absent-book branch

**SKIP: the English book exists and matches the installer payload.** Its SHA-256 is
`c10cf13e001c16c0ebad036615ee7f55f88fd61bbe126b71e639a6d997027700`.
No file was removed to simulate absence. D1 demonstrates that this installation's documentation is accessible;
this round does not establish fallback behavior for a package missing its English book.
''')
write('PRESERVATION.md',r'''# Preservation, restoration and evidence boundaries

The explicit first-run brief permits v312 and supersedes the earlier v313-only preflight stop for these tests.
The exact brief is [REQUEST.md](REQUEST.md). No product files were changed.

Before installing, the existing canonical installation's **663 files** were hashed and moved to
`%USERPROFILE%\AppData\Local\Programs\Sutram-before-firstrun-20261108`.
The current Start-menu folder and any existing desktop link were preserved; the three Sutram HKCU registry
keys (`Classes\\.sm`, `Classes\\Sutram.Source`, `Uninstall\\Sutram`) were renamed with a
`-FirstRun20261108` suffix, retaining their complete contents. User PATH was recorded and its canonical
Sutram entries removed for the test; machine PATH was read only. No uninstall or deletion command was used.
Only the dedicated, validated canonical installation and test paths were moved; older preserved installs and
previous uninstall temp residue were left untouched.

After testing:

- The tested installation was moved, with all 663 files verified, to
  `%USERPROFILE%\AppData\Local\Programs\Sutram-firstrun-tested-20261108`.
- The original installation was moved back and all original files verified.
- Original registry keys, Start-menu shortcuts and user PATH were restored. The test registry keys remain
  under `-TestedFirstRun20261108` names. Test shortcuts, including the harmless desktop collision fixture,
  remain in `<repo>\build\firstrun-2026-11-08\preserved\`.
- **672 restoration checks passed**, including 663 original file hashes, original shortcut hashes,
  the complete three registry trees, and PATH comparisons. A fresh shell finds the canonical compiler and v312.
- All five IDE instances and the setup wizard closed normally. The two test terminals were sent `exit`.
  Seven test Explorer windows and the Notepad window were closed; the book test tab was closed.
  No installed Sutram process remained at restoration.

Records: [preservation](preserve.json), [restoration](restore.json),
[original registry/shortcut baseline](restoration-baseline.json), [final verification](restoration-verified.json),
[window cleanup and OS/token](finish.json).

## Checks of the testing harness

The first terminal screenshot already showed successful `sutram --version`, but the initial redirect capture
accidentally concatenated three commands because of PowerShell array-expression precedence. The raw
`terminal-initial-capture-error.json` is retained. Parenthesized command entries fixed the harness, and a second
actual shortcut launch produced separate raw version/where/PATH files. The corrected version bytes equal the
extracted compiler's version output exactly. No failed capture is used as product-failure evidence.

Explorer's first Open-with attempts encountered stale windows and duplicate invisible menu entries. Selecting
the newly opened Explorer window and the visible menu entry completed the actual menu test. Only the completed
IDE-load record is used as its result. The default double-click tests were successful on their first recorded runs.

The desktop list exposed no icon items through UI Automation. The icon's position was visually verified in
a private desktop capture before the real double-click. Only the icon region is published. Full desktop and
Explorer screenshots/UI dumps include unrelated user content and remain private under `build/`.

The initial documentation observer assumed a Chromium window; the actual default was Firefox. A later viewport
capture was occluded after a long UI read. Both are harness limitations, not documentation failures. The final
capture checks Firefox's foreground status immediately before and after capture, and its address matches the
installed book. The occluded capture is excluded and retained privately.

The first independent restoration check compared raw `REG_EXPAND_SZ` machine PATH against .NET's expanded PATH
and flagged a representation mismatch. The raw check record is retained. Expanding `%SystemRoot%` for a like-for-like
comparison produces the final 672/672 result; no machine PATH change was made.

Raw binary evidence and text are byte-preserved by `.gitattributes`. `EVIDENCE.sha256` covers all published files
except itself. Helpers are evidence of the executed procedure, not production code or a supported installer.
Review their fixed test paths and guards before any reuse. No CI workflow or full compiler regression suite was
changed or launched for this observational round.
''')
# Extract from the exact tested package, retained after restoration, not from a changing checkout.
tested=Path(r'%USERPROFILE%\AppData\Local\Programs\Sutram-firstrun-tested-20261108')
book=(tested/'docs/sutram-book-english.html').read_text(encoding='utf8')
start=book.index('<h3>17.6 Understanding PATH</h3>');end=book.index('<h3>17.7',start)
write('book-path-excerpt.html',book[start:end])
base=read('restoration-baseline.json')['original_registry']
# The test registry keys are preserved by the restoration procedure; query those exact values.
import winreg
with winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'Software\Classes\Sutram.Source-TestedFirstRun20261108\shell\open\command') as key:
 command=winreg.QueryValueEx(key,'')[0]
write('shell-registration.json',json.dumps({'preserved_test_key':r'HKCU\Software\Classes\Sutram.Source-TestedFirstRun20261108\shell\open\command','command':command},indent=2))
handoff=root/'ChatGPT-to-Sarvam/WINDOWS-FIRSTRUN-PATHS-2026-11-08.md'
handoff.write_text('''# Windows first-run paths: v312 native results

The owner supplied a separate first-run brief explicitly permitting v312. It does not lift the earlier v313
preflight gate for the v313 acceptance matrix.

**10 PASS / 1 FAIL / 1 SKIP**, on the setup pinned at `079c7b226fe968b3d9b5dfe248f097482f5d1fce`.
Declining PATH works through the actual Start-menu terminal, all four Explorer path cases and explicit Open with
load correctly, and the documentation shortcut opens the installed English book in Firefox.

**Actionable finding:** a pre-existing desktop `Sutram IDE.lnk` is preserved byte-for-byte and remains the only
desktop link under that name. Clicking it opens its original Notepad target. Setup shows no collision warning;
only the engine log records preservation. Keep preservation, but give the user a visible explanation and a clear
route to the installed IDE. This is an observed first-click mismatch, not a human confusion study.

Also correct the visible desktop-option wording: it says “Sutram Terminal,” while the engine manages
`Sutram IDE.lnk`. Open with displays the executable-style name `sutram-ide-gui`; it loads the file correctly.

[Results, exact paths, hashes, raw logs and screenshots](../Windows-to-Sarvam/win-firstrun-paths-2026-11-08/RESULTS.md).
Original installation/settings restored and verified: 672 checks, zero failures. Test artifacts preserved;
no product changes or release acceptance claimed. Pending independent Sarvam review.

Upstream v313 arrived during publication (`d25eb2ad`). This report deliberately retains the exact v312
artifact identity tested under the owner's first-run brief; it does not report v313 acceptance results.
''',encoding='utf8',newline='\n')
files=sorted(p for p in dest.rglob('*') if p.is_file() and p.name!='EVIDENCE.sha256')
write('EVIDENCE.sha256','\n'.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(dest).as_posix() for p in files))
print(json.dumps({'published_folder':str(dest),'files_hashed':len(files),'handoff':str(handoff)},indent=2))

# Sutram Native Windows GUI IDE — Round 35 preview

**Status: source-stage, not Windows runtime-verified.** The GUI is designed as a separate, user-mode **pure NASM** Win64 program. It uses only Windows system APIs (kernel32/user32/comdlg32/Msftedit RichEdit), avoiding Qt/.NET/C/Python dependencies in the GUI executable. Python and PowerShell are used only for *development/testing*, not by the IDE at runtime.

## Build and run (normal Windows user)

Put `sutram-ide-gui.exe` at the project root, alongside `win\sutram.exe` and `examples\`.
The project already uses NASM and the GNU PE linker for its compiler. Use that same toolchain:

```powershell
& .\windows\gui\build-gui.ps1
.\sutram-ide-gui.exe
```

Alternatively (no PowerShell script invocation required):

```text
nasm -f win64 windows/gui/sutram_gui.asm -o sutram_gui.obj
ld -mi386pep --subsystem windows --entry=_start -o sutram-ide-gui.exe sutram_gui.obj
```

On Windows you must **first build** `win\sutram.exe` using the existing project instructions; the GUI invokes that compiler directly. Builds use the user's normal permission level and do not install drivers, services, registry keys, or open ports.

## Features (source implementation, pending Windows tests)

- Native Win32 top-level window and main message loop
- RichEdit Sutram source editor with **Latin-keyword-first** highlighting and separate numbered gutter
- Run: save editor buffer to a unique temporary file, invoke `win\sutram.exe`, execute the newly built `.exe`, and capture stdout/stderr in a read-only output pane; child processes have a 10-second limit
- Examples list populated from `examples\*.sm`; double-click or **Load example**
- Common **Open** / **Save** `.sm` dialogs
- Shell input: one statement per Enter or Send, recorded to session history. Each submission recompiles the accumulated `mukhya()` body and displays the new output suffix. This is **replay-based**, not a persistent VM; side effects may repeat.
- Compiler and GUI remain separate; existing terminal `sutram-ide` is untouched.

## Testing

1. In the development environment, `python3 -m unittest discover tests/gui -v` checks source structure and required test coverage. It does not execute Windows UI code.
2. On a real Windows desktop, use `windows/gui/build-gui.ps1` to assemble and check PE/AMD64 headers.
3. Run `windows/gui/test-gui.ps1` for a smoke UIAutomation check. This **is not currently executed or verified**.
4. Complete `windows/gui/MANUAL-WINDOWS-GUI-TEST.md`, including editor, highlight, compile+stdout, examples, shell, save/load, resize, quit, and failure cases. Report precise failures, screenshots, machine and tool versions.

## Safety and limitations

- Windows Defender, UAC, firewall and normal security controls **remain enabled**. Do not bypass warnings or policy to run an untested executable.
- A Windows runner is mandatory before release. No NASM assembler or Windows GUI runner was available in ChatGPT's sandbox.
- The current implementation uses ANSI Win32 entrypoints. **Non-ASCII/Devanagari editing may not round-trip correctly**; UTF-16 APIs plus explicit UTF-8 compiler file conversion are required before marking that capability complete.
- Line-number gutter does not yet guarantee perfect scroll synchronization. Syntax coloring is Romanized Sutram keywords only. Heavy token highlighting may be slow on large sources.
- WinAPI bootstrap reuses the existing project's kernel32 export lookup via the loader, then calls documented Windows APIs. Because forwarded kernel32 exports and AV heuristics differ by Windows build, independent runtime confirmation is essential. If it fails, replace with standard PE imports, not OS security changes.
- Run and shell execute program code under the **same standard-user privileges** as the GUI. Only run trusted source. Output is capped at 32 KiB and runtime at 10 s per child to bound resource use; GUI is synchronous during those operations.
- This preview is **not bundled as a working .exe** and should not be advertised as a finished Windows installer or release until Sarvam independently builds and tests it.

## Integration guidance for Sarvam

The canonical incoming ZIP could not be downloaded (Drive 403). The full-tree ZIP sent back is a safe **reference snapshot only**. Merge just these **new paths** into the canonical current Sutram tree:

- `windows/gui/sutram_gui.asm`
- `windows/gui/build-gui.ps1`
- `windows/gui/test-gui.ps1`
- `windows/gui/MANUAL-WINDOWS-GUI-TEST.md`
- `windows/gui/README-WINDOWS-GUI.md`
- `tests/gui/test_win_gui_source.py`

Keep canonical `src/`, `lib/`, `ide/`, `docs/`, `ROADMAP.md`, installers, books and examples 200+ untouched. Stage target executable in the project root; optional installer integration **only after Windows acceptance**.


## Round 36: Win64 output and nonvolatile-register fixes (source-stage)

Two ABI defects in the initial GUI have been corrected. `PeekNamedPipe` has six
parameters: Win64 stack slot `[rsp+32]` (argument 5) is **lpTotalBytesAvail**,
whereas `[rsp+40]` (argument 6) is **lpBytesLeftThisMessage**, always zero for
anonymous pipes. Both capture sites now put `pipe_available` in argument 5.
That issue could cause the **Run output pane to appear empty even when the
compiler or executable printed text**.

The custom kernel32 PE export resolver now pushes and restores RSI/RDI in
addition to RBX/R12-R15 as required for Windows x64 callee-saved registers.
The seven pushes retain 16-byte alignment before its nested internal call.

Run `python -m unittest discover -s tests/gui -v` for static source checks.
Then build the GUI and run `windows/gui/test-gui.ps1` on a real Windows desktop
and execute checklist items 13 and 14. **No compiled GUI or GUI runtime test
was available at source authoring time, so these are not yet accepted fixes.**

Important outstanding limitations remain: GUI uses ANSI Win32 API entrypoints
and does not safely round-trip Devanagari or arbitrary UTF-8 filenames; the
Windows kernel export resolver has not been tested against forwarded exports;
there is no nonblocking output loop or native Windows CI acceptance.
Do not weaken Windows security controls to obtain a pass.


### Round 38 Unicode and installer branch (not Windows-tested)

The editor path now uses `GetWindowTextW`/`SetWindowTextW` plus kernel32's strict
`WideCharToMultiByte(CP_UTF8)` and `MultiByteToWideChar(CP_UTF8)`. On-disk `.sm`
files stay UTF-8 and dialog/temporary/compiler-process path APIs use W variants.
ASCII keyword highlighting measures UTF-16 code units; it must not reindex non-ASCII
text by its byte length. Devanagari-specific keyword colouring is not yet added.
The GUI dynamically loads the **new canonical thread icon** from `icons/sutram.ico`
or installed `assets/sutram.ico`; no outdated icon bytes are embedded in source.

The existing least-privilege Windows installer payload now packages
`sutram-ide-gui.exe` at the install root AND `win/sutram.exe` under the same root,
while keeping the existing `bin/sutram.exe` terminal path. The Start Menu adds
`Sutram IDE.lnk` and uninstall removes it and files through the payload manifest.
Build order: build GUI using `windows/gui/build-gui.ps1`, then call the existing
`windows/native-installer/build-installer.ps1`. The installed GUI is still pending
Windows runtime acceptance; see steps 15–24 of MANUAL-WINDOWS-GUI-TEST.md.


## Round 39: native-script highlighting (unverified Windows runtime)

At GUI startup, Sutram reads all ten UTF-8 language packs from `lang/*.lang`
relative to the executable directory; it displays a diagnostic in the output
pane when some or all packs are missing. Every first-column native-script token
is converted strictly to UTF-16 using Windows `MultiByteToWideChar` and
loaded into a bounded 384-entry keyword table. No non-Windows runtime or elevated
privileges are required. The existing Romanized keyword table is retained.

The RichEdit lexer uses whole UTF-16 code units and checks U+0900–U+0DFF (plus
ZWJ/ZWNJ) for Brahmic-script word boundaries. It suppresses highlighting inside
quotes and `#`/`//` comments. All ten packs are active simultaneously; menu
selection is not required and does **not** change the compiler's `--lang` mode.
Native-script editor colouring does not prove the native Sutram compiler
understands every pack: verify compilation separately with the chosen language
configuration. Source-only static tests and Python reference-lexer oracle cannot
substitute for actual Win64 NASM assembly or Windows GUI operation.

Dependencies for the GUI at runtime: the Windows system libraries already used
by the GUI and installed `lang/` text files. The per-user installer already
packages that directory. Place `lang/` next to the GUI executable for portable
use. Do not fall back to ANSI conversion for malformed UTF-8.

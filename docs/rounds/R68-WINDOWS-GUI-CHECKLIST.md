# R68 Windows GUI manual acceptance — no Windows run claimed

## Precisely what the current counter changes

The accepted `r67_gui_entry.asm` redirects calls to `highlight_editor`. After
that original routine returns, and only when `is_highlighting` is zero, it reads
the editor text with GetWindowTextW, converts UTF-16 to UTF-8, calls
`r67_count_editor_clusters`, and changes the **main window title** to:

```text
Sutram Shell 1.0 | scoped clusters: <decimal count>
```

The count covers the whole buffer, including spaces and line-break clusters.
It is not a character count, byte count, glyph count, display-column count, or
proof of grapheme conformance. The iterator groups its implemented Devanagari/
Gujarati marks and consonant chains, common combining marks and CRLF. Other
scripts have only scalar-level behavior unless explicitly handled by that helper.
No R68 change expands that GUI scope.

A reported length >=65,535 UTF-16 units, conversion failure or invalid counter
progress selects `Sutram Shell 1.0 | cluster count unavailable`. A zero return
from GetWindowTextW takes the zero-count path; current code does not distinguish
an API failure from a genuinely empty buffer at that branch. There is no timer:
updates occur at wrapped highlight calls, including any load/edit paths that call
that routine. Initial-title timing must be observed, not presumed.

RichEdit remains responsible for text drawing, glyph shaping, advances, caret,
selection, editing and font fallback. This counter changes none of those. It is
neither a complete UAX #29 algorithm nor a glyph shaper.

## Prepare without risking user data

Use a standard-user Windows 10/11 x64 session and a disposable checkout/scratch
folder. Record Windows version, source commit, executable SHA-256, compiler
version, font, scaling and screen resolution. Do not elevate, disable protections
or bypass script policy. A policy block is a BLOCKED result, not a reason to weaken
settings. Only use an already authorized NASM/PE-linker development environment.

Build using `windows/gui/build-gui.ps1`; verify that the build includes
`r67_gui_entry.asm`, `r66_indic_clusters.asm` and `r67_cluster_count.asm`. Record
build exit code. A successful link or PE-header check does NOT pass the GUI tests.
The compiler executable and language packs must be present in their expected
relative locations before Run is tested.

## Manual checks (record PASS / FAIL / BLOCKED and evidence)

| ID | Action | Check and evidence |
|---|---|---|
| G01 | Open the GUI from the scratch checkout; repeat 3 times | Window appears, no crash/hang/duplicate abandoned process; record initial title. |
| G02 | Replace all editor text with `abc`; trigger an ordinary edit | Title becomes exactly `Sutram Shell 1.0 \| scoped clusters: 3`. |
| G03 | Select all and paste each exact fixture in `tests/r68/gui_title_cases.json` | Match the entire expected title. No extra trailing newline. Save screenshots and source bytes. |
| G04 | Clear the buffer; type, paste, undo and redo | Zero-count after the normal update path; title remains synchronized. Count does not modify editor text. |
| G05 | Use `कि`, `क्ष`, `કિ`, `ક્ષ`, mixed ASCII, CRLF and supplementary text | Record both count and visual rendering separately. A correct title does not pass matra/conjunct rendering. |
| G06 | Move the caret, select across clusters, copy/paste, resize and change DPI | Text/selection/caret remain RichEdit-owned. Record visual defects; do not call them fixed by the counter. |
| G07 | Open/save a disposable UTF-8 file; compare bytes after save | Check encoding, line endings, undo behavior, path with spaces/non-Latin characters, and title after load. |
| G08 | Use Run on an already accepted tiny program, then a deliberate compiler error | Capture stdout/exit/errors and responsiveness; do not label compiler success from a title change. |
| G09 | Exercise visible menu commands, then close via X, Alt-F4 and File/Exit separately | Each intended action works; no orphan process. A non-wired menu is FAIL, not waived. |
| G10 | Close with unsaved SCRATCH edits, then reopen | Record whether there is a warning and whether data is lost. Do not assume an unsaved-change prompt exists. |
| G11 | Test near the text-length threshold using disposable content | Record whether the control limits input, returns unavailable, or truncates. Never certify a fabricated count. |
| G12 | Repeat edit/open/close cycles, inspecting Task Manager | No continuing process or unexpected resource growth; collect crash/hang details if present. |

Fixture counts were checked against the isolated helper on Linux, not a Windows
window. Newline normalization by RichEdit can affect results, so report the actual
UTF-16 buffer/line endings when investigating differences. Installer install/
uninstall acceptance is a separate checklist and must not be inferred here.

## Report template

```text
Commit / executable SHA-256:
Windows / font / DPI:
G01..G12: PASS | FAIL | BLOCKED (one line each)
Exact pasted fixture and expected / actual title:
Source bytes before / after save:
Screenshots / crash or hang log paths:
Window process after close:
Known visual shaping defects (separate from count):
```

No result is pre-filled. R68 supplies source facts, fixtures and this checklist;
it does not assert that any Windows action above has been executed.

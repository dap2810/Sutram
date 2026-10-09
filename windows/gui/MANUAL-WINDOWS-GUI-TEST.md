# Sutram native Windows GUI: mandatory real-machine acceptance checklist

**Status:** Source written, NOT assembled or executed on Windows in ChatGPT's environment.
Record PASS/FAIL and screenshots. Do **not** disable UAC/Defender or run as Administrator.
This preview has known limitations below; a failing mandatory item is a release blocker.

## Preconditions

- Windows 10/11 desktop session, normal user account, NASM and PE-capable `ld` on PATH *for build only*.
- Working tree includes `win\sutram.exe` (native compiler) and `examples\01_hello.sm`.
- Place the GUI executable at **project root**, NOT inside `windows\gui\`.
- In PowerShell run `powershell -ExecutionPolicy Default -File .\windows\gui\build-gui.ps1` from project root. If policy refuses, follow your organization's normal policy; **do not bypass it**. Alternative: the two NASM/ld commands documented at the top of `sutram_gui.asm`.
- Launch `./sutram-ide-gui.exe` from the project root. If Defender blocks it, stop and report, do not disable Defender.

## Tests — exact actions and expected results

1. **Window/startup**: Double-click `sutram-ide-gui.exe`. A visible window titled `Sutram - Native Windows IDE (Preview)` opens without UAC. A left gutter, main editor, example list, output pane, and shell input are visible. **FAIL** on crash, console-only display, or missing pane.
2. **Editing**: Click the editor, Ctrl+A, type exactly:

   ```sutram
   mukhya()
       likha("GUI_OK\n")
   ```

   The editor displays both lines, accepts backspace/arrow keys, and line numbers `001` and `002` appear at left. **FAIL** if editor is read-only, text disappears, or numbering is incorrect.
3. **Syntax highlighting**: `mukhya` and `likha` visibly change to keyword colour; the quoted `GUI_OK` does not inherit keyword colour. Type `# likha` and check `likha` inside comment is *not* coloured as a keyword. **FAIL** if keywords are never coloured or comments are treated as code.
4. **Run/compile/output**: Restore the exact two-line program from Step 2, click **Run**. The output pane contains `GUI_OK` on its own line (the program's stdout), without a console window or UAC. **FAIL** for compiler error, missing output, or hang beyond 10 seconds.
5. **Examples browser**: In the examples list double-click `01_hello.sm`, then click **Run**. The editor is replaced with the example and output contains exactly `Namaste, Sutram!` followed by a newline (without compiler errors). **FAIL** if item missing or file not loaded.
6. **Shell Enter**: Click the shell text field. Enter `likha("ONE\n")` and press **Enter**. The output pane receives `ONE` once. Enter `likha("TWO\n")` and press Enter. It receives `TWO` once, without another visible `ONE`. This shell *recompiles/replays history*, so it is intended for deterministic statements, not irreversible side effects. **FAIL** if Enter is inserted as a newline, no output, or duplicated visible output.
7. **Shell button**: Enter `likha("THREE\n")`, click **Send**, and verify `THREE` appears once. Click **Clear shell**, then enter `likha("FRESH\n")`; verify history reset and new output `FRESH`.
8. **Save**: Replace editor with the two-line `GUI_OK` program. Click **Save**, save as `%TEMP%\sutram-gui-roundtrip.sm`. Confirm the file exists and is nonempty; open it with Notepad and verify both lines are exact. **FAIL** if Save does nothing or modifies the text.
9. **Load**: Replace editor contents with `mukhya()`, then click **Open**, select `%TEMP%\sutram-gui-roundtrip.sm`. The exact earlier text returns; Run still prints `GUI_OK`. **FAIL** if text missing or output differs.
10. **Resize**: Resize window to 1200x850, then 850x600. The editor, examples list, output, and shell remain accessible; no child is entirely hidden. **FAIL** if layout unusable or pane becomes unclickable.
11. **Exit**: Close via window X; process exits, no UAC, no orphan visible console window. In PowerShell check `Get-Process sutram-ide-gui -ErrorAction SilentlyContinue` returns no process.
12. **Missing compiler**: Rename `win\sutram.exe` temporarily to `sutram.exe.test`, click Run, restore original filename immediately. IDE should remain responsive and show a visible failure, not claim success. **FAIL** on crash or false output.


13. **Captured stdout regression (R36)**: Replace editor buffer with:

   ```sutram
   mukhya()
       likha("PIPE_ONE\n")
       likha("PIPE_TWO\n")
   ```

   Click **Run**. Output pane must show both `PIPE_ONE` and `PIPE_TWO` in that order. Repeat three times; none may disappear. This catches the former Win64 `PeekNamedPipe` 5th/6th argument mix-up, which made anonymous-pipe output appear empty. **FAIL** if Run reports success but stdout is empty, one line is missing, or execution hangs.

14. **Windows ABI regression (R36)**: Launch, Run, Open the examples list, Save and return to Run ten times on the same desktop session, then close the GUI. There must be no intermittent crash, frozen interface or corrupted output. The Win64 export resolver now saves RSI and RDI. **FAIL** on any access violation or memory-related crash; capture Event Viewer faulting module and Windows error code if it occurs.

## Known preview limitations requiring follow-up (record separately)

- No native Windows CI runner here: real build, edit, Run, and UI behaviour are unverified until checklist executes.
- The API path currently uses **ANSI Win32 file/edit calls**. Unicode/Devanagari/UTF-8 roundtrips and non-ASCII Windows paths need a future UTF-16/UTF-8 bridge; do **not** advertise complete Sanskrit-script editing yet.
- Line-number gutter currently updates **line count** but may not vertically scroll-synchronize with the editor; exercise >100 lines and report divergence.
- Syntax highlighting is Latin-keyword-first. It is a prototype, not full token-level Unicode highlighting.
- Child compilation/execution is bounded by a **10-second synchronous wait**, with output truncated at 32KiB. Long jobs may temporarily freeze the UI. Run does not pass stdin through.
- Shell replays all submitted statements; external side effects repeat. It is not a persistent VM/REPL and should be labeled as such in a stable release.
- Program-executing GUI runs code under the **same standard-user privilege** as the IDE. Only Run code you trust; use no admin elevation.

## Report template

- Windows version/build: ___
- Normal-user account (Y/N): ___
- Native compiler SHA-256: ___
- GUI EXE SHA-256: ___
- NASM build output / exit code: ___
- Automated `test-gui.ps1` output: ___
- Manual test 1..12: ___
- Screenshot(s) and exact failure reproduction: ___


## Round 38: Unicode, native installer and script-neutral icon acceptance

**Status of Round 38 source: NOT NASM-assembled or runtime-verified here.** Perform under a
normal Windows 10/11 user account without administrator elevation. Obtain Sarvam's **new
thread icon** from the canonical tree, not the old script-character artwork.

15. **Devanagari direct edit** — launch GUI, enter exactly `mukhya() { likha("नमस्ते सूत्रम्") }`
    into the editor using paste or an Indian-script input method. EXPECT: all Devanagari
    glyphs remain intact on screen; inserting text before them does not turn later
    ASCII Sutram keywords blue at the wrong character offsets. FAIL: question marks,
    replacement glyphs, mojibake, lost characters, or displaced selection/highlights.
16. **UTF-8 save byte identity** — Save as `नमस्ते_सूत्रम्.sm` inside a directory named
    `परीक्षा`, then read the saved file as UTF-8 without BOM (PowerShell:
    `[Text.UTF8Encoding]::new($false,$true).GetString([IO.File]::ReadAllBytes($path))`).
    EXPECT: exact original code points including Devanagari, not ANSI bytes or U+FFFD.
    FAIL: exceptions, substituted '?', or path/file corruption.
17. **UTF-8 reopen** — close/reopen that non-ASCII path using Open. EXPECT: every
    glyph and line break round-trips correctly, editor cursor can move through text.
    FAIL: Open fails, text changes, or content is truncated without a clear error.
18. **Unicode Run temp path** — set TEMP/TMP to an existing user-writable directory
    with Devanagari characters in its name, launch GUI from a Unicode-named parent,
    Run `mukhya() { likha(123) }`. EXPECT: output `123`; no temp-path failure or
    leftover compiled executable after clean exit. FAIL: no output, compiler unable
    to open a temp file, or inherited environment is corrupted.
19. **Unicode shell and stdout** — submit a statement containing a Devanagari string;
    EXPECT: if supported by Sutram's compiler output, rendered characters match.
    FAIL: ANSI substitution in the shell or output. Remember the shell replays prior
    statements; do not use side-effecting actions for this acceptance case.
20. **Real GUI icon** — inspect title bar, task switcher and shortcut icon.
    EXPECT: Sarvam's new teal/orange **thread** mark, never the old Devanagari letter.
    FAIL: old mark or missing icon; confirm canonical `icons/sutram.ico` or installed
    `assets/sutram.ico` was merged before declaring a defect.
21. **Per-user wizard install** — build compiler and GUI, run the native installer
    normally (not as admin). EXPECT: welcome → license → destination → install → finish,
    no UAC prompt; install under `%LOCALAPPDATA%\Programs\Sutram`;
    `sutram-ide-gui.exe` and `win\sutram.exe` both exist in installed directory.
    FAIL: elevation request, Program Files/HKLM write or GUI missing from payload.
22. **Start Menu and Settings entry** — open Start Menu → Sutram IDE; run editor
    example and confirm output. Open Settings → Apps → Installed apps and find Sutram.
    EXPECT: GUI opens, project examples/relative compiler work, uninstall entry visible.
    FAIL: shortcut points to wrong folder, missing compiler or absent Apps entry.
23. **Per-user uninstall** — uninstall through Windows Settings → Apps or Sutram's
    Start Menu shortcut. EXPECT: Sutram IDE shortcut removed, copied GUI/`win` compiler
    removed, HKCU uninstall entry removed, no other user's files touched.
    FAIL: stale shortcut/app entry or deletion outside owned install root.
24. **Regression check** — terminal `sutram-ide` and compiler still run; no change
    in preexisting program output, no administrator privileges needed.
    FAIL: terminal IDE missing, compiler regressions or a new UAC prompt.

**Acceptance rule:** pass 15–24 on actual Windows and run `test-gui.ps1`. The static
Python checks only validate source contracts; they cannot prove the GUI runs.


## Round 39 — all ten native-script keyword packs (real Windows acceptance)

Prerequisites: keep `lang/*.lang` alongside the installed GUI directory, do not elevate.
The GUI reads all **ten** official packs on startup; no selector is required. The
native compiler must support the chosen language for Run; **highlighting can be
verified without compiling**. Every expected colour is the same blue used for `mukhya`.

25. **Hindi/Devanagari pack** — verify `lang\hindi.lang` exists, restart GUI,
    paste these **separate** lines into the editor:

    ```text
    मुख्य() { लिखो(1) }
    "मुख्य लिखो"
    # मुख्य लिखो
    // मुख्य लिखो
    ```

    EXPECT: `मुख्य` and `लिखो` **only on line 1** are blue; lines 2–4
    remain normal text, and cursor/selection do not jump. FAIL: no blue
    colouring, partial combining marks, colouring inside quotes/comments,
    or Unicode corruption.
26. **Tamil pack** — verify `lang\tamil.lang` exists, restart GUI, paste:

    ```text
    முதன்மை() { எழுது(1) }
    "முதன்மை எழுது"
    # முதன்மை எழுது
    // முதன்மை எழுது
    ```

    EXPECT: `முதன்மை` and `எழுது` on line 1 are blue, with all quoted and
    commented occurrences uncoloured. FAIL on split/dropped letters, displaced
    colours, or missing keyword recognition.
27. **Mixed-script/Latin boundary and quoted text** — paste `mukhya() { likha(1) }`
    followed by `मुख्य() { எழுது(2) }`. EXPECT: all four keywords blue,
    including correct ranges in a mixed-script buffer. Replace with
    `मुख्यxyz`, `abcஎழுது`, and `முதன்மைfoo`; EXPECT: none are recognised
    as complete keywords. Put a Latin keyword after several Tamil words;
    EXPECT: no offset shift.
28. **Missing pack diagnostics** — with GUI closed, temporarily move
    `lang\tamil.lang` to an ordinary user-owned backup outside `lang/`;
    reopen GUI. EXPECT: visible output warning that some packs are missing,
    while Hindi and Latin highlighting still work. Restore Tamil and restart.
    Then temporarily rename the entire `lang` directory, reopen and EXPECT a
    visible `native keyword packs unavailable` warning; Latin highlighting
    continues. Restore everything before leaving the test. FAIL on silent
    missing packs or startup crash.
29. **UTF-8 malformed input and long-file boundary** — duplicate the Hindi pack
    in a disposable test tree and replace its first keyword with invalid UTF-8
    bytes; EXPECT that token is not highlighted and the GUI does not crash.
    Verify the original pack is restored. FAIL if malformed bytes are silently
    transformed to replacement glyphs and coloured as a valid keyword.
30. **Installed copy** — install as standard user, verify ten `.lang` files in
    `%LOCALAPPDATA%\Programs\Sutram\lang\`, then repeat steps 25 and
    26 through the Start Menu GUI shortcut. EXPECT the same highlighting and
    thread logo. FAIL on missing pack files, UAC, or the old script icon.

**Status:** These tests have been *written*, not executed on Windows in ChatGPT's
Linux environment. Record Windows build version, GUI SHA, manual PASS/FAIL per
step, and screenshots before declaring release acceptance.

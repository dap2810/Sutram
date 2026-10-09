# R40 mandatory native-script Windows GUI visual acceptance

Prerequisites: normal Windows user (no admin), current thread-logo GUI
`/sutram-ide-gui.exe` in project root, ten files `lang/*.lang` present,
Windows display session. Record Windows build, executable SHA-256, screenshot,
PASS/FAIL, and exact error for each step. Do not disable Defender/UAC.

1. **Window and pack load**: Start `sutram-ide-gui.exe`. Expect a visible
   titled window, editor + output panes, thread icon, no UAC, no missing-pack
   warning. FAIL if no GUI, freeze, old script-letter icon, or missing pack.
2. **Hindi code**: Paste `मुख्य() { लिखो(1) }` on first line. Expect
   `मुख्य` and `लिखो` entirely blue, including correctly placed vowel marks.
   FAIL if words remain plain, letters are broken or colours are partial.
3. **Hindi string/comment**: Add `"मुख्य लिखो"`, `# मुख्य लिखो`, and
   `// मुख्य लिखो` on three separate lines. Expect NONE of those keywords to
   use keyword blue. FAIL if any string or comment gets keyword colouring.
4. **Tamil code**: Replace editor with `முதன்மை() { எழுது(1) }`. Expect
   `முதன்மை` and `எழுது` blue throughout all visible characters. FAIL if
   colours are missing or split the glyphs.
5. **Tamil string/comment**: Add `"முதன்மை எழுது"`, `# முதன்மை எழுது`,
   `// முதன்மை எழுது`. Expect no keyword blue in those three lines.
6. **Mixed script/Latin**: Paste two lines: `mukhya() { likha(1) }` and
   `मुख्य() { எழுது(2) }`. Expect all four keywords blue without shifting
   colour by prior UTF-16 code units. FAIL on colouring offset, cursor jumps.
7. **Whole-word boundaries**: Paste `मुख्यxyz` and `abcஎழுது`. Expect neither
   to receive complete-keyword blue. FAIL on false positives or malformed text.
8. **Save/reload UTF-8**: Save mixed source to `%TEMP%\\सूत्रम्-தமிழ்.sm`, close
   and reopen. Expect identical text, colours, and valid UTF-8 file contents,
   no replacement characters and no UAC. FAIL on loss/corruption.
9. **Regression**: Open normal `examples/01_hello.sm`, click Run. Expect exact
   `Namaste, Sutram!` output and no change to Romanized keyword colouring.
   FAIL on missing stdout, compiler error or user-privilege request.

These steps are **not executed in the Linux container**. A screenshot and
real Windows PASS/FAIL log are mandatory before claiming visual acceptance.

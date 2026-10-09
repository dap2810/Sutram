# Sutram R41 — Windows native-script GUI visual test (user checklist)

**Not run in this environment.** On a normal Windows user account, with the current GUI, thread icon, `lang/` directory and compiler present, perform these checks and record **PASS or FAIL with a screenshot** per step. Do not disable Defender/UAC or run as administrator.

1. Open `sutram-ide-gui.exe`. Expect a normal titled application with the thread icon, editor and output panes, and no security prompt. FAIL on crash, missing window or old letter icon.
2. Paste `मुख्य() { लिखो(1) }`. Expect the complete Hindi words `मुख्य` and `लिखो` to be coloured **blue** as keywords, with no broken vowel marks. FAIL if not highlighted or split.
3. Enter `"मुख्य लिखो"` on its own line and `# मुख्य लिखो` on another. Expect neither line to colour those words blue. FAIL if strings/comments are treated as code.
4. Replace text with `முதன்மை() { எழுது(1) }`. Expect the complete Tamil words `முதன்மை` and `எழுது` blue, without broken glyphs. FAIL if uncoloured or wrongly offset.
5. Add `"முதன்மை எழுது"` and `# முதன்மை எழுது` on separate lines. Expect no blue keyword highlighting inside strings/comments. FAIL if either line is miscoloured.
6. Open `examples/01_hello.sm` and click **Run**. Expect exactly `Namaste, Sutram!` in the output pane, with no UAC prompt. FAIL on missing output, compiler error or GUI hang.
7. Save and reopen a UTF-8 file with Hindi/Tamil in its contents and filename. Expect **byte-preserved Unicode** and intact highlighting. FAIL on lost characters, replacement diamonds or path failure.

Record Windows version, GUI executable SHA-256, each step's PASS/FAIL, one screenshot each, and exact error text. These steps are an executable human acceptance script, not evidence of Windows runtime success in this round.

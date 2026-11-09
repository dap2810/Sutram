# Explorer shell opening

Each fixture contains a different ASCII marker, so an empty editor or a stale previous file cannot pass.
The test compared the IDE editor's actual text against the entire fixture, normalizing CRLF/LF only and
ignoring trailing whitespace. Screenshots show the corresponding marker. No file was edited or compiled here.

| Test | Exact path used | Marker | Actual |
|---|---|---|---|
| spaces | `<repo>\build\firstrun-2026-11-08\cases\My Sutram Files\hello.sm` | `"FIRST_RUN_SPACES"` | Loaded exactly; closed normally |
| devanagari | `<repo>\build\firstrun-2026-11-08\cases\सूत्रम्\hello.sm` | `"FIRST_RUN_DEVANAGARI"` | Loaded exactly; closed normally |
| ampersand | `<repo>\build\firstrun-2026-11-08\cases\Ampersand & Files\hello.sm` | `"FIRST_RUN_AMPERSAND"` | Loaded exactly; closed normally |
| percent | `<repo>\build\firstrun-2026-11-08\cases\Percent %USERNAME% Files\hello.sm` | `"FIRST_RUN_PERCENT"` | Loaded exactly; closed normally |
| openwith | `<repo>\build\firstrun-2026-11-08\cases\My Sutram Files\hello.sm` | `"FIRST_RUN_SPACES"` | Loaded exactly; closed normally |

B1–B3 used actual mouse double-clicks in Explorer, 80 ms apart, on the listed `hello.sm` file.
All four opened the installed GUI and loaded the exact content. In particular, `%USERNAME%` remained literal
in the directory name; it was not expanded into the account name. The Devanagari folder is `सूत्रम्`.
These paths are in the isolated workspace's test folder, rather than the example Documents location in the brief.

B4 used Explorer's right-click menu, **Open with → sutram-ide-gui**. That is the displayed application name,
not “Sutram IDE.” The file loaded correctly. Default shell opening already worked on this account, so B4 is
an additional explicit menu test, not a claim about all nondefault-handler configurations. No “Always” choice
or default-application change was made.

Screenshots: [spaces](shell-spaces.png) *(screenshot removed under the privacy rule, 9 November 2026; the text keeps what it showed)*, [Devanagari](shell-devanagari.png) *(screenshot removed under the privacy rule, 9 November 2026; the text keeps what it showed)*,
[ampersand](shell-ampersand.png) *(screenshot removed under the privacy rule, 9 November 2026; the text keeps what it showed)*, [percent](shell-percent.png) *(screenshot removed under the privacy rule, 9 November 2026; the text keeps what it showed)*, [Open with](shell-openwith.png) *(screenshot removed under the privacy rule, 9 November 2026; the text keeps what it showed)*.
Matching `shell-*.json` records include exact editor content, title, status, PID and close result.
The original fixture bytes are preserved under `cases/`.

The actual registered command is the installed GUI path followed by quoted `"%1"`; see
`shell-registration.json`. Passing these five cases is not a universal path/encoding guarantee.

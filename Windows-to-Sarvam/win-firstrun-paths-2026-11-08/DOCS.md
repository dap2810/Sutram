# Documentation shortcut

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
[rendered page](documentation-opened.png) *(screenshot removed under the privacy rule, 9 November 2026; the text keeps what it showed)*. The screenshot captures only the book viewport, excluding other
browser tabs and unrelated application content. It shows a Windows chapter section of the actual installed book.

## D2 — absent-book branch

**SKIP: the English book exists and matches the installer payload.** Its SHA-256 is
`c10cf13e001c16c0ebad036615ee7f55f88fd61bbe126b71e639a6d997027700`.
No file was removed to simulate absence. D1 demonstrates that this installation's documentation is accessible;
this round does not establish fallback behavior for a package missing its English book.

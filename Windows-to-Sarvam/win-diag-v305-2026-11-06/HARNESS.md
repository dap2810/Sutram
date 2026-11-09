# v305 module lookup: root succeeds; unbundled compiler fails from suite CWD

All runs use the same compiler bytes, SHA-256
`db5eda53871aafa4749d593ddef2d29e2841e3eb4d3cb7cdf680223fb45a073c`.
Source: unchanged `examples/79_ayojan_cwd.sm`, importing `ganit`.
Exact commands, absolute working directories and outputs: [harness.json](harness.json).

| Run | Compile result | Executable result |
| --- | --- | --- |
| Repo root, literal relative compiler/source command | exit 0 | exit 0, `81` |
| Repo root, absolute compiler/source paths | exit 0 | exit 0, `81` |
| Previous harness CWD, absolute paths, direct `win/sutram.exe` | exit 1, `E_MODULE_MISSING` | not produced |
| Same harness CWD, byte-identical compiler with adjacent unchanged `lib/` and `lang/` | exit 0 | exit 0, `81` |

The actual previous harness CWD was
`<repo>\build\windows-v305-2026-11-06\suite`.
Its output-directory override is recorded in
[the previous harness log](../win-v305-2026-11-06/suite-harness.json).
The checked-in harness's default CWD for this one test is
`build/windows/acceptance`; both deliberately exercise a non-project directory.

Failure output:

```text
Sutram truti [E_MODULE_MISSING]: yoj patra aprapt: ganit
Sanket: naam.smlib lib/ madhye srota-patrasya nirdeshikayam va bhavet
```

The path/layout explanation is confirmed. Changing CWD to the root masks the
missing adjacent library layout, but is not equivalent to satisfying this
example's intended non-project-CWD check. Contrary to ROUND-131's description,
the Linux harness explicitly uses `/tmp` for `79_ayojan_cwd` (see `CWD` in
`tests/run_tests.py`), rather than the repo root. A complete portable compiler
layout passes the actual intended condition on Windows too.

Recommendation for the fixer: stage the byte-identical compiler with its
unchanged libraries and retain the unrelated-CWD check. These runs do not
justify a compiler change or changing frozen expectations. No harness,
compiler, or library was changed here.

# R22-02 — WS3: F8, what the warning checked, the fix, the test

**Branch `claude/round-22`, commit `b30de60f`, draft PR #61.** It is built on `6086e90d` (R22-01), so it
also carries that commit. Compiler **v233**. Environment: **Linux**, plus **Wine** where I say so. **Not
Windows:** the owner's machine is still the only Windows result.

## What the warning was checking

A language pack has **two halves**, and the warning was about the one the user can't see:

| Half | File | Where the compiler gets it |
|---|---|---|
| **messages** | `lang/<pack>.sandesh` | **built into the compiler** since R11 (`src/r11_sandesh.inc`), so they are always there |
| **keywords** (`लिखो` → `likha`) | `lang/<pack>.lang` | **from disk only:** `.\lang\`, then `lang\` beside `sutram.exe` (Windows), then `$HOME/.local/share/sutram/lang/` |

`try_load_lang` first switches the messages to the pack (`set_lang_id`, which always succeeds), then looks
for `<pack>.lang`. When the file was on none of those paths, it printed `msg_lang_fail`, in the pack's
language, because the messages had already switched.

**So the warning was true about the file and false about the language.** On the owner's machine there was
no `hindi.lang` on any of those paths: he typed `sutram` from the folder that holds `sutram.exe`, so both
`.\lang\` and `lang\` beside the exe were looked at. I can't see the zip's contents, so I can't say why it
was missing.

**It was not only cosmetic.** Without the file, **native keywords did not work:** `38_native_hindi.sm`
fails with a parse error at line 7. The owner's `bad.sm` uses Latin keywords, which is why only the warning
showed.

**Reproduced exactly, under Wine,** with main's `sutram.exe` alone in a folder (`evidence-r22/f8-wine.txt`):

```
> main/sutram.exe --lang hindi bad.sm o.exe
चेतावनी: भाषा पैक नहीं मिला: hindi
bad.sm:1:18: Sutram Error [E_UNDEFINED_NAME]: अज्ञात नाम 'nosuchname'
```

The same holds for sanskrit and tamil, character for character with F8's table. **On Linux it fires
too,** in any folder without `lang/` (Linux has no "beside the executable" path). **It is not a Windows
bug, but Windows is where people run it from a folder.**

## The fix

**The eleven `.lang` files are now built into the compiler as well:**

- `src/r22_lang_builtin.inc` is **generated** from `lang/*.lang`, byte for byte, by `tools/lang_builtin.py
  --write`. `--check` refuses a stale copy, the same pattern as `sandesh.py`.
- When no file is found on any path, `try_load_lang` looks the name up in `lang_names` and parses the
  built-in copy with **the same parser** (`load_lang_mem` copies it into `lang_file_buf` and enters
  `load_lang_file` after the read).
- **A `.lang` file on disk still wins**, so a user can still edit their pack.
- **The warning stays, and is now correct:** it fires only for a name that is no pack (`--lang klingon`).

After the fix, with the same folder under Wine: `भाषा पैक मिला: hindi` ("pack found"), the same Hindi
error, and `38_native_hindi.sm` compiles and runs (`नमस्ते दुनिया`, `3 6 9 12`).

## The test: `--lang <pack>` on a valid program must not warn

`tests/r22/test_lang_builtin.py`, 40 checks, also a gate (`pack found without lang/`):

| Check | Count | This branch | main's compiler |
|---|---|---|---|
| every pack × (`--lang`, `--check --lang`, `SUTRAM_LANG`), from a folder with no `lang/` and an empty `HOME`: exit 0, "found", **no "not found"** | 33 | 33 PASS | **33 FAIL** |
| the five native-keyword examples compile to **the same bytes** from the built-in pack as from `lang/` | 5 | 5 PASS | **5 FAIL** (no keywords) |
| `--lang klingon` still warns | 1 | PASS | PASS |
| a `lang/hindi.lang` on disk wins (an extra word only the file has) | 1 | PASS | PASS |

The test reads each pack's expected "found" and "not found" text from `lang/<pack>.sandesh`, so it checks
all eleven languages, not just three. (`evidence-r22/f8-test-on-*-compiler.txt`)

## Pins and the rest

- **Compiler blob** `4547e473` → `8648e097`; `src/r11_sandesh.inc` regenerated for v233;
  **`src/r22_lang_builtin.inc` pinned** (r69's include-closure check requires it). Updated in
  `tools/r69_build.py`, `tools/r69_build.lock.json`, `tests/negative/r70/manifest.json`,
  `docs/BUILDING.md`, `docs/NEGATIVE-CORPUS.md`. `r69 --check-only`: SOURCE_PINS_CHECKED; `tests/r70`: OK.
- **Two new gates:** `keyword packs built in` (`lang_builtin.py --check`) and `pack found without lang/`.
- **`docs/WINDOWS-SETUP.md` was wrong about the search order:** it said `%USERPROFILE%`, but the compiler
  reads `HOME`, and it left out the beside-the-exe path. Corrected, with the built-in copy added.
- **The Windows set is rebuilt:** `win/sutram.exe` = `sutram.exe` `2468dca0…`, `Sutram-Setup.exe`;
  `cross_build_windows.py --check`: REPRODUCED. `sutram-ide-gui.exe` is unchanged.
- **`TEST-ME.md`'s F8 note** ("ignore the warning") is yours. Once this lands, it can say "fixed in v233".
  For the owner's zip: **the new `sutram.exe` alone is enough**, no `lang\` folder needed.

| Check | Environment | Result |
|---|---|---|
| `tools/gates.sh` | Linux | **18 PASS / 0 FAIL / 1 NOT-RUN (Windows)** (`evidence-r22/gates-branch.txt`) |
| `tests/r22/test_lang_builtin.py` | Linux | 40 / 40 (main's compiler: 2 / 40) |
| F8 before / after | **Wine** | reproduced on main's exe, gone on the new one |
| real Windows | — | **NOT-RUN.** The owner's re-run of F8's three commands is the acceptance |

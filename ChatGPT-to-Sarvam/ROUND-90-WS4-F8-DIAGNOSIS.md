# Sutram ROUND-90 WS4 — F8: what the false language-pack warning actually tests

**Scope:** SOURCE-ONLY diagnosis, pinned `main` v253 commit `7ec9c9b58498bb34b826ea6abbcbc5cf2e2f7ec4`. **Native Windows/Linux execution: NOT_RUN.** The owner's real Windows observations are in [F8-PACK-WARNING-FALSE-ALARM.md](../F8-PACK-WARNING-FALSE-ALARM.md). This report does **not modify compiler code**: Claude owns the fix.

## Short answer

The warning tests whether the compiler can **open, read and recognize native-script keyword aliases from a filesystem file, `lang/<name>.lang`**. It does **not test whether the compiler has translated diagnostics**.

The translations in `lang/<name>.sandesh` are baked into the executable via `src/r11_sandesh.inc`. The compiler selects that embedded translation *before* trying the separate `.lang` file. Therefore the warning and subsequent diagnostics can be in Hindi even if the native-script keyword alias file is missing or not successfully parsed. **The Windows output proves that the embedded Hindi message table works; it does not alone prove the separate Hindi keyword file loaded.**

## Exact source path and line numbers

| Step | File / lines | Observed behavior |
|---|---|---|
| 1 | `src/sutram_compiler.asm:365–381` | Hardcoded pack names and `cur_lang_id`; `msg_lang_fail` is a compiler message |
| 2 | `src/sutram_compiler.asm:1990–1995` | `--lang <name>` invokes `try_load_lang` |
| 3 | `src/sutram_compiler.asm:1105–1119` | Validates pack name length, then **`call set_lang_id` at 1115** and saves name **before attempting a file open** |
| 4 | `src/sutram_compiler.asm:1120–1133` | First attempt is `lang/<name>.lang`, relative to the process's current working directory |
| 5 | `src/sutram_compiler.asm:1134–1169` | **Windows-only** second attempt: executable's directory (from `get_self_path`) plus `lang/<name>.lang` |
| 6 | `src/sutram_compiler.asm:1170–1189` | Additional `$HOME/.local/share/sutram/lang/<name>.lang` fallback, after the above |
| 7 | `src/sutram_compiler.asm:1214–1242, 1313–1387, 1400–1417` | `load_lang_file` opens/reads the `.lang` file, maps entries to recognized keywords/builtins; returns success only if **`lang_kw_cnt > 0`**. Missing/unreadable/empty/unrecognized file can return failure |
| 8 | `src/sutram_compiler.asm:1191–1209` | On failed loader attempts, `.tll_fail` prints `msg_lang_fail`; on success, `.tll_ok` prints `msg_lang_ok` |
| 9 | `src/sutram_compiler.asm:6939–6963` | `set_lang_id` updates `cur_lang_id` based solely on pack-name string, independent of loading aliases |
| 10 | `src/sutram_compiler.asm:23178–23188` | `print_str_z` **always calls `r11_tr`** to translate compiler messages before printing |
| 11 | `src/sutram_compiler.asm:6888–6925` and `src/r11_sandesh.inc:73–74, 132–133` | `r11_tr` selects a statically generated per-pack message column, with `msg_lang_fail` registered as a translatable message |
| 12 | `win/winrt.inc:180–215` | Windows file open uses a resolved `CreateFileA` call, unlike Linux `os_open` syscall; both return failure to the same `try_load_lang` branch |

The known live Git tree contains **all eleven `.lang` files** as well as eleven `.sandesh` files. Their presence in GitHub **does not establish what the owner's portable Windows ZIP actually included**, or which path the process tried. The Windows log does not contain the attempted filename, the OS error code, or a directory listing. Therefore **which file/open/parse step failed on that specific Windows run is UNDETERMINED by the supplied evidence**.

## Linux versus Windows: what can and cannot be concluded

**Not intrinsically Windows-only:** lines 1120–1133 and 1170–1197 run on both platforms. Running on Linux from outside the repository, with no `lang/<name>.lang` in the current working directory and no working HOME fallback, would also take the warning path *even though embedded messages remain localized*. This is a source-level conditional outcome, **not a Linux execution observed in this round**.

**Platform difference:** Windows attempts an extra executable-relative `lang/<name>.lang` path (1134–1169); Linux does not. Windows uses `GetModuleFileNameA` for the executable location (982–1009) and `CreateFileA` to open files. The observed owner's Windows warning might reflect the ZIP's installed layout, an actual alias-file omission, an unreadable path or a parsing problem. The warning output by itself cannot distinguish these.

On a full Linux source-tree checkout with `lang/hindi.lang` present and the command executed from the repository root, the first lookup **should succeed** if the file is readable and contains recognized keywords. Existing Linux tests commonly execute in this layout. It is therefore **not proved that they had the same warning**.

## Why previous pack tests may miss this

In `tools/test_lang_packs.py:32–44`, the runner captures the compiler's stdout/stderr but **discards those streams when an output executable exists**. It then judges the generated program, not whether the compiler printed a misleading warning. Hence a compiler that compiles a valid source yet warns on a pack can pass the old tests. This explains a gate blind spot without assuming the warning occurred on Linux.

## Recommended controlled verification for Claude and Sarvam (NOT executed here)

1. For both Linux and Windows, test `--lang hindi`, `--lang sanskrit` and `--lang tamil` using both a valid romanized program and a **native-script-keyword** program. Assert no missing-pack warning when alias files are available, correct output and correct selected diagnostics.
2. Capture working directory, executable path, exact `lang/<name>.lang` file presence/size, attempted resolved paths, file-open error and whether the lexer obtains a positive keyword count. Compare repo-root and external working directories. Never infer file presence from translated warning text.
3. In a controlled negative test **without** the `.lang` alias file, verify what remains available: embedded messages may still translate but native-script alias keywords should not be represented as successfully loaded. Do not simply suppress a genuine missing-alias warning.
4. Update the warning's wording/trigger to distinguish **keyword-alias file load** from **translated message support**. Add a regression asserting `--lang <installed pack>` on a valid source does **not** warn on either OS. Avoid any change to the compiler or language packs until reviewed and tested.

**Status matrix:** static trace **PASS: 16/16 checked source landmarks** (raw exact file-line excerpts in [ROUND-90-WS4-F8-SOURCE-TRACE.json](ROUND-90-WS4-F8-SOURCE-TRACE.json)); Windows warning **REPORTED by owner**; actual ZIP alias file/layout **UNKNOWN**; Linux warning actually reproduced **NOT_RUN**; native compiler regression **NOT_RUN**; modifications **NONE**.

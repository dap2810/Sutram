# F8 - the "language pack not found" warning is a FALSE ALARM

**Found by the owner on real Windows, 2026-10-21, testing `sutram-windows-test.zip`.**

## The reproduction

```
I:\sutram-windows-test_2\Sutram-Windows-Test>sutram --lang hindi bad.sm o.exe
चेतावनी: भाषा पैक नहीं मिला: hindi
bad.sm:1:18: Sutram Error [E_UNDEFINED_NAME]: अज्ञात नाम 'nosuchname'
  mukhya() { likha(nosuchname) }
                   ^
संकेत: प्रयोग से पहले घोषणा आवश्यक है: चर nosuchname = ...
```

**Read that carefully. The warning says the Hindi pack was NOT FOUND - and it says so IN HINDI. Then the
error message that follows is also in Hindi.**

**The pack loaded.** `अज्ञात नाम` and `संकेत` are the Hindi messages. **So the warning is wrong.**

## The same on three packs

| Command | The warning | The message that follows |
|---|---|---|
| `--lang hindi` | `चेतावनी: भाषा पैक नहीं मिला: hindi` | **Hindi** - `अज्ञात नाम` |
| `--lang sanskrit` | `चेतावनी: भाषा-पुटः न प्राप्तः: sanskrit` | **Sanskrit** - `अज्ञातं नाम` |
| `--lang tamil` | `எச்சரிக்கை: மொழித் தொகுப்பு கிடைக்கவில்லை: tamil` | **Tamil** - `அறியாத பெயர்` |

**In every case the warning is in the language it claims not to have found.** That is self-contradictory, and
it is the strongest possible evidence that the warning is a false positive.

## Why it matters more than a cosmetic warning

**A user who sees "language pack not found" will conclude the pack is missing** and stop using it - **while
the pack is working correctly.** For a language whose entire purpose is that a user can work in their own
language, **a false "your language is not available" message is the worst possible error to emit.**

**And it is the first defect found on real Windows by the owner** - every AI check passed, because every AI
check ran on Linux where the same warning presumably fires.

## What to determine

1. **What is the warning actually checking?** The messages load, so the pack is found. **Something else is
   being looked for and not found** - a second file, a directory, or a path that differs on Windows.
2. **Why does it fire on Linux too, or not?** If it fires on Linux as well, this is not Windows-specific.
3. **Fix it so the warning fires only when the pack genuinely fails to load.**

**And add a test:** `--lang <pack>` on a valid program must NOT warn.

## The rest of the Windows test passed

- **`sutram --version` -> `Sutram 1.0 (v232) - sampurna sutra`** - correct.
- **`hello.sm` -> `Namaste, Sutram!` then `1 2 3 4 5`** - correct.
- **`f1.sm` -> `7`** - **F1 IS FIXED ON WINDOWS.** The bug the owner found is confirmed closed on his machine.
- **The error message, the line number, the caret and the hint all render in four scripts** - so the fonts and
  the encoding work.


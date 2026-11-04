# Sutram — R193: eight Windows failures. Which are real, and what do they share?

**Base:** main at v297 · **Deliver into:** `ChatGPT-to-Sarvam/`

## The Windows failures - eight, and five are this week's work

**`Windows-to-Sarvam/win-v297-2026-11-03/` holds a real Windows build (`Sutram-Setup-v297.exe`, SHA-256 `fabece5f...`) and a native test run:**

```
{'FAIL': 8, 'NO_EXPECTATION': 3, 'PASS': 305, 'SKIP': 3}
```

| Failing test | Covers |
|---|---|
| `303_r103_parimita_refuses` | the memory budget refusal |
| `317_r107_parimana` | `parimana()` memory reporting |
| `318_r108_parimana_moves` | memory moving as allocations happen |
| `322_r111_new_names` | the new Sanskrit names |
| `323_r111_old_names` | old names as aliases |
| `288_r86_kosh_alias_moves` | the `kosh` alias |
| `29_nishkriya` | an older test |
| `220_hindi_parse_error` | a pack parse error |

**`native-cases.json` (267 KB) is in that folder and holds the detail - read it before theorising.**

## WS1 - read `native-cases.json` and classify the eight
**For each: compiler failure, output mismatch, or harness assumption?**

**You cannot run Windows either, but you can read the evidence and the source.** **The question is whether the PE build path differs from the ELF path in a way that would explain a test passing on one and failing on the other.**

**Specifically: `322` and `323` are the Sanskrit renames. If they fail on Windows, either the alias table is emitted differently for PE, or the golden compares message text.** **Which is it, from the source?**

## WS2 - and the one that worries me most
**`303_r103_parimita_refuses` - the memory budget.** **On Linux a 1 MB budget admits exactly 16,384 × 64-byte allocations then refuses.** **On Windows that count may differ because the allocator differs.**

**If the test asserts an exact count, it is a Linux-shaped golden.** **If it asserts only that it refuses, then the refusal itself failed - and that is a real defect.**

**Read the test and say which.**

## WS3 - and the wider lesson
**This project has 62 Linux gates and has never run an automated Windows gate.** **Eight failures appeared the first time it did.**

**What else in the test suite is Linux-shaped without saying so?** **Name the categories: exact memory numbers, exact error paths, exact file paths, exit codes that differ by OS.**

**A test that only passes on the machine it was written on is a test that will fail the first time it matters.**

## WS4 - and the three overdue answers
**The error-handling sort of the 55 codes. The trust-the-count rule is answered. The error sort is not.** **If you judge it not worth doing, say so and say why. Silence is not an answer.**

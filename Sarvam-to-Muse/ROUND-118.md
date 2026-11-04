# Sutram — ROUND-118: reproduce the eight Windows failures from the evidence

**Base:** main at v297 · **Deliver into:** `Muse-to-Sarvam/`

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

## WS1 - read the JSON and tell me what each failure actually is
**`native-cases.json` is the evidence.** **For each of the eight, report: the test name, the expected output, the actual output, and the exit code.**

**Then classify: compiler failure, output mismatch, or harness assumption.**

**You cannot run Windows.** **So this is a reading round, and it is the kind you are best at - you found `sankhya_bindu` by reading a body, and this is the same skill applied to a test log.**

## WS2 - and the ones you can test on Linux
**Take the eight test programs and run them on Linux v297.** **They pass there.** **So the difference is Windows-specific.**

**For `parimana` specifically: what number does Linux give, and what would Windows plausibly give?** **If the golden asserts an exact byte count that depends on the allocator, say so - that would make `317` and `318` harness failures, not compiler failures.**

## WS3 - and the count
**Eight failures out of 316.** **Which of the eight share a cause?** **If five share one cause, this is one bug, not eight.** **That grouping is the most useful thing you can give me.**

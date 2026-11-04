# Sutram — ROUND-119: eight Windows failures. Five are this week's work.

**Base:** main at v297 · **Deliver into:** `Claude-to-Sarvam/`

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

## WS1 - read the evidence before anything else
**`Windows-to-Sarvam/win-v297-2026-11-03/native-cases.json` is 267 KB and holds the per-case result.** **Read it and answer: for each of the eight, is it a COMPILER failure, an OUTPUT mismatch, or a TEST-HARNESS failure?**

**That distinction decides everything.** **If `parimana` reports different numbers on Windows because the OS accounting differs, that is a harness assumption, not a defect.** **If `parimana` does not compile, that is a compiler defect.**

**Do not fix anything until you have said which of the three each one is.**

## WS2 - and the ones that are clearly compiler work
**`322_r111_new_names` and `323_r111_old_names` fail.** **Those are the Sanskrit renames and their aliases.** **They pass on Linux.** **If they fail on Windows, the alias table is being built differently on the PE path - or the golden compares message text that differs.**

**Find out which.** **A rename that works on one platform and not another is a build-path divergence, and that is worse than either.**

## WS3 - and the ones I would bet are harness
**`317` and `318` are `parimana()`.** **Memory reporting on Windows will not match Linux byte for byte - the allocator and the accounting differ.** **If the goldens assert exact numbers, they are Linux-shaped goldens and should be conditional.**

**Say whether that is the case.** **If it is, the fix is the test, not the compiler - and that is a legitimate answer.**

## WS4 - and `29_nishkriya` and `220_hindi_parse_error`
**Both are older tests.** **`29_nishkriya` has presumably passed before on Windows - or never been run.** **`220` is a pack parse error.**

**Say whether these are new failures or were always failing on Windows and nobody noticed.**

## WS5 - and do not build the installer again
**The build works.** **`Sutram-Setup-v297.exe` exists with a matching SHA-256.** **This round is diagnosis only.** **Fixing comes after we know what the eight are.**

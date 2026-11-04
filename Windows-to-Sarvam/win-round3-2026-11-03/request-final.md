# Sutram — Windows round 3: fix the two defects, close the memory gap

**Copy this whole file to the Windows AI.**

---

## 0. What your round 2 established

**Your evidence corrected a wrong diagnosis from three other AIs. This round is where you fix things.**

| Finding | Verdict |
|---|---|
| `220` with `--lang hindi` | **PASS — the earlier test was wrong, not the language** |
| `29` raw syscall | **Linux-only by nature, not a defect** |
| `parimana()` returns zero | **confirmed; the reference already says Linux-only** |
| `parimita` does not refuse | **confirmed; same** |
| `kosh` alias diverges | **confirmed; same** |
| **`anka_akshar(66)` gives `P` on Windows, `B` on Linux** | **REAL WINDOWS DEFECT** |
| **`vartani_sandhi` crashes on Windows, prints `abcd` on Linux** | **REAL WINDOWS DEFECT** |

**And you found the mechanism:**

> *"The returned pointer at rsp-8; a PE adapter call can overwrite its storage with the return address. Linux's direct syscall path happens not to make that same call."*

---

## 1. The insight that shapes this round

**Both functions print the right thing on Linux.** **Their goldens pass.** **`vartani_sandhi` prints `abcd` correctly — while returning a pointer into its own stack frame.**

**Linux gets away with it because the caller happens not to overwrite that storage before use.** **Windows does not.**

**So this is not a wrong answer. It is unsafe code that happens to produce a right answer on one platform.**

**That is why 62 Linux gates never caught it, and why your run did.**

---

## 2. Priority 1 — `vartani_sandhi` crashes

**Exit `0xC0000005`, access violation.** **Linux prints `abcd`.**

**Confirm or refute the stack hypothesis:**

1. **Read the emitter for `vartani_sandhi`.** **Where does the returned pointer point — stack, heap, or a static buffer?**
2. **If it is the function's own stack frame, that is the bug.** **A function cannot return a pointer to storage that dies when it returns.**
3. **The fix: return a pointer to storage that outlives the call.** **A static buffer, or an allocation. Say which and what it costs.**
4. **If it is not stack, say what it is and where the overwrite comes from.**

**Then fix it, and verify the same program still prints `abcd` on Linux.**

---

## 3. Priority 2 — `anka_akshar` returns the wrong character

**`anka_akshar(66)` gives `P` (hex 50) on Windows, `B` (hex 42) on Linux.** **`50 − 42 = 14`.**

1. **Read the emitter. Where does the character come from?**
2. **Is it the same stack-lifetime problem?** **If both return pointers into stack storage, they share one root cause and one fix.**
3. **If they share a cause, fix them together. If not, separately — and say so.**

**Verify: `anka_akshar(66)` must give `B` on Windows, and `anka_akshar(97)` must give `a`.**

---

## 4. Priority 3 — the memory gap. Decide, do not guess.

**`parimana()` returns zero, `parimita` does not enforce, the `kosh` alias diverges — Windows only.** **The reference already says these are Linux-only.**

**Two honest answers. Pick one and say why:**

**Option A — build them for Windows.** **What would `parimana` need?** **If the compiler already tracks allocations, the reporting may be a small change per platform.**

**Option B — leave them Linux-only and make them refuse.** **If `parimana()` cannot work on Windows, it must say so rather than return a confident `0`.**

**My view: `parimana()` returning `0` on Windows is not acceptable.** **Zero looks like an answer. A refusal is honest; a zero is a silent wrong answer of exactly the kind this project has spent a week removing.**

**Do not build until you have answered which it is.**

---

## 5. After each fix — the checks

1. **The Linux probes still pass** — `anka_akshar(66)` gives `B`, `vartani_sandhi` gives `abcd`.
2. **The same probes now pass on Windows.**
3. **The full native suite runs — report the pass/fail count against 305 / 8.**
4. **No new failures.**

**If a fix breaks something else, say so and revert it.** **A fix that trades one defect for another is not a fix.**

---

## 6. What to commit

**Push to `Windows-to-Sarvam/win-round3-<date>/`:**

1. **`FIXES.md`** — what you changed, why, and the table below.
2. **Every `.sm` probe you wrote.**
3. **Before-and-after output for each fix.**
4. **The native suite result with the delta from 305 / 8.**
5. **The exact commands you ran.**
6. **If you changed the compiler: which files, how many lines.**

### The table

| Item | Before | After | Linux still OK? |
|---|---|---|---|
| `vartani_sandhi` crash | `0xC0000005` | | |
| `anka_akshar(66)` | `P` | | |
| `anka_akshar(97)` | | | |
| `parimana()` | `0` everywhere | | |
| `parimita` budget | does not refuse | | |
| `kosh` alias | `a[0]=41` | | |
| Native suite | 305 pass / 8 fail | | |

---

## 7. Rules

- **Fix one thing at a time and verify before moving on.** **Two fixes at once means you will not know which worked.**
- **Do not change a golden to make a test pass.** **The goldens are correct — `322` should print `B42` and `abcd`, and you confirmed that.**
- **Do not disable a Linux-only feature on Windows without saying so.** **If you choose Option B for memory, it must refuse, not return zero.**
- **Report what actually happened.** **A failed attempt recorded is worth more than a success claimed.**
- **If you cannot fix something, say why and what you tried.**

---

## 8. Why this round matters

**`vartani_sandhi` crashes on Windows doing something ordinary — joining two strings.** **And `anka_akshar` returns a wrong character, which is worse than a crash because it looks like an answer.**

**Both work on Linux, which is why 62 Linux gates never caught them. You did.**

**And the class matters beyond these two:** **a function that returns a pointer to storage it does not own is wrong on every platform. Linux may simply never notice.**

**Fixing these two is worth more than any new feature this project could add this week.**

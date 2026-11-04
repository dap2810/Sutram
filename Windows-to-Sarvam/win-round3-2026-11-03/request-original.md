# Sutram — Windows round 3: fix the two defects, close the memory gap

**Copy this whole file to the Windows AI. It is self-contained.**

---

## 0. Where we are

**Your round 2 was excellent and it corrected a wrong diagnosis from three other AIs.** **This is the round where you fix things.**

**What your round 2 established:**

| Finding | Status |
|---|---|
| `220` with `--lang hindi` | **PASS — my test was wrong, not the language** |
| `29` raw syscall | **Linux-only by nature, not a defect** |
| `parimana()` returns zero on Windows | **confirmed — and the reference already says Linux-only** |
| `parimita` does not refuse on Windows | **confirmed — same** |
| `kosh` alias diverges on Windows | **confirmed — same** |
| **`anka_akshar(66)` gives `P` instead of `B` on Windows, and `B` correctly on Linux** | **REAL WINDOWS DEFECT** |
| **`vartani_sandhi` crashes on Windows, works on Linux** | **REAL WINDOWS DEFECT** |

**And you found the mechanism:**

> *"The returned pointer at rsp-8; a PE adapter call can overwrite its storage with the return address. Linux's direct syscall path happens not to make that same call."*

**That is the sentence this round starts from.**

---

## 1. What to fix, in priority order

### Priority 1 — `vartani_sandhi` crashes

**It exits with `0xC0000005` — an access violation.** **On Linux the same program prints `abcd`.**

**This is a crash, so it outranks everything.**

**Your hypothesis is that a returned pointer into stack storage is overwritten by a PE call sequence.** **Confirm or refute it:**

1. **Read the emitter for `vartani_sandhi`.** **Where does the returned pointer point — stack, heap, or a static buffer?**
2. **If it is stack, that is the bug.** **A function that returns a pointer to its own stack frame cannot be correct on any platform — Linux only survives it because the caller happens not to overwrite it before use.**
3. **If it is stack, the fix is to return a pointer to storage that outlives the call** — a static buffer, or an allocation. **Say which, and what it costs.**
4. **If it is not stack, say what it is and where the overwrite comes from.**

**Then fix it.** **One change. Verify on Windows. And report whether the same program still prints `abcd` on Linux.**

---

### Priority 2 — `anka_akshar` returns the wrong character

**`anka_akshar(66)` gives `P` (hex 50) on Windows and `B` (hex 42) on Linux.**

**`50 - 42 = 14`.** **An off-by-14, or a corrupted byte, or a pointer that lands 14 bytes off.**

**Do the same analysis:**

1. **Read the emitter.** **Where does the character come from?**
2. **Is it the same stack-lifetime problem as `vartani_sandhi`?** **If both return pointers into stack storage, they share one root cause and it is one fix.**
3. **If they share a cause, fix them together.** **If not, fix them separately and say so.**

**Then verify: `anka_akshar(66)` must give `B` on Windows, and `anka_akshar(97)` must give `a`.**

---

### Priority 3 — the memory gap. Decide, do not guess.

**`parimana()` returns zero, `parimita` does not enforce, and the `kosh` alias diverges — all on Windows only.**

**The reference already says these are Linux-only.** **So there are two honest answers and you should pick one and say why:**

**Option A — build them for Windows.** **What would `parimana` need on Windows?** **Is it a counter the compiler maintains, or an OS query?** **If the compiler already tracks allocations, the reporting may be a one-line change per platform.**

**Option B — leave them Linux-only and make the refusal explicit.** **If `parimana()` cannot work on Windows, it should say so rather than return a confident `0`.** **A function that always returns zero is worse than one that refuses, because zero looks like an answer.**

**My view: if the counter already exists, build it.** **If it does not, refuse.** **Either way, `parimana()` returning `0` on Windows is not acceptable — it is a silent wrong answer of exactly the kind this project has spent a week removing.**

**Do not build this until you have answered which it is.**

---

## 2. What to check after each fix

**After each change:**

1. **The two probes still pass on Linux** — `anka_akshar(66)` gives `B`, `vartani_sandhi` gives `abcd`.
2. **The same probes now pass on Windows.**
3. **The full native suite runs** — and report the pass/fail count against the previous 305 / 8.
4. **No new failures appeared.**

**If a fix breaks something else, say so and revert it.** **A fix that trades one defect for another is not a fix.**

---

## 3. What to commit

**Push to `Windows-to-Sarvam/win-round3-<date>/`:**

1. **`FIXES.md`** — what you changed, why, and the evidence table below.
2. **Every `.sm` probe you wrote.**
3. **Before-and-after output for each fix.**
4. **The native suite result, with the delta from 305 / 8.**
5. **The exact commands you ran.**

**And if you changed the compiler, say which files and how many lines.**

---

## 4. The evidence table

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

## 5. Rules

- **Fix one thing at a time and verify before moving on.** **Two fixes at once means you will not know which one worked.**
- **Do not change a golden to make a test pass.** **If a golden is wrong, say so in the report.**
- **Do not "fix" a Linux-only feature by disabling it on Windows without saying so.** **If you choose Option B for the memory gap, it must refuse, not silently return zero.**
- **Report what actually happened.** **If a fix did not work, say so — a failed attempt recorded is worth more than a success claimed.**
- **If you cannot fix something, say why and what you tried.**

---

## 6. Why this round matters

**`vartani_sandhi` crashes on Windows.** **That is a program that dies, on the platform students use, doing something ordinary — joining two strings.**

**And `anka_akshar` returns a wrong character.** **That is a wrong answer that looks like a right one.**

**Both work on Linux, which is why 62 Linux gates never caught them.** **You did.**

**Fixing these two is worth more than any new feature this project could add this week.**

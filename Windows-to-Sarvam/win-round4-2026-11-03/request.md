# Sutram — Windows round 4: complete the memory model, close the last three

**Copy this whole file to the Windows AI.**

---

## 0. What you have achieved

**Your three rounds took Windows from 8 failures to 3:**

| Stage | Result |
|---|---|
| Baseline | **8 FAIL** |
| After the character fix | 6 FAIL |
| After the memory refusal | **3 FAIL, 4 COMPILE_FAIL** |

**306 PASS / 3 FAIL / 4 COMPILE_FAIL.**

**And you corrected three wrong diagnoses from other AIs along the way** — the stack-lifetime hypothesis, my off-by-14, and the claim that two builtins were wrong on Linux.

**This round is the one that finishes it.**

---

## 1. The task, stated plainly

**Memory on Windows currently *refuses* rather than works.** **`parimana()` and `mandapa parimita N` now reject with `E_WINDOWS_SMRITI`.**

**That was the right call for a safety fix — a refusal beats a silent zero.**

**But the owner wants the memory model to work on Windows, not to be absent from it.** **So this round: build the accounting, enforce the budget, and make the `kosh` alias safe.**

**Three things. In this order.**

---

## 2. Priority 1 — give PE an allocation counter

**Your round 3 finding: *"The counter and budget depend on the Linux arena/region implementation (`r65_active` excludes PE); there is no Windows allocation accounting already available to expose with a small switch."***

**So the work is to give PE its own accounting.** **The question is how much of the Linux mechanism can be shared.**

**Investigate and report before building:**

1. **Where does `r65_active` live, and what does it track?** **A pointer, a counter, or both?**
2. **Why is it excluded from PE?** **A conditional assembly guard (`%ifdef WINDOWS`), a different code path, or something that genuinely cannot work?**
3. **If it is a guard, can it simply be enabled for PE?** **That is the cheapest possible fix and it should be tried first.**
4. **If it genuinely cannot work, what does PE need instead?** **A separate counter incremented in the same places?**

**Report the answer to all four before writing code.**

**Then implement it.** **`parimana()` must return real bytes on Windows, and `mandapa parimita N` must enforce.**

**And `E_WINDOWS_SMRITI` goes away once the real thing works.**

---

## 3. Priority 2 — the `kosh` alias on Windows

**This is the last semantic gap:**

> *"Windows growing `kosh` still moves its backing storage, so the old alias diverges. This was not ported."*

```
kosh k[1]
kosh_push(k, 41)
vitti a = k
vitti obstacle = nirmmita(64)
kosh_push(k, 42)
k[0] = 99
likha("a[0]=", a[0], " k[0]=", k[0])
```

**Linux: `a[0]=99 k[0]=99` — one object.**
**Windows: `a[0]=41 k[0]=99` — two buffers.**

**Linux solves this by reserving 64 MiB per `kosh` so it never relocates (`R101A_REGION`, `R101A_MAXCAP = 8,388,603`).**

**Port that to PE.**

**If 64 MiB per `kosh` is impractical on Windows** — for example because of address-space reservation limits or page granularity — **say so and propose the alternative: a smaller reservation with a documented element limit, or stable descriptors.**

**Do not silently leave it divergent.** **Either it works or the reference says it does not, and right now the reference says Linux-only, which is honest but incomplete.**

---

## 4. Priority 3 — the three remaining failures

**Your FIXES.md reports 3 FAIL but does not name them in the summary I have.** **Name them first, in your report:**

**Which three tests still fail, what each expects, what it gets, and which of the three classes each is:**

- **compiler failure**
- **output mismatch**
- **harness assumption**

**Then fix the real ones.** **If one is a harness assumption, say so and mark it — do not fix a test to make a number look better.**

---

## 5. The evidence table to fill in

| Item | Before (round 3) | After (round 4) | Linux unchanged? |
|---|---|---|---|
| `parimana()` on Windows | compile refusal | | |
| `mandapa parimita` on Windows | compile refusal | | |
| `kosh` alias on Windows | `a[0]=41 k[0]=99` | | |
| `E_WINDOWS_SMRITI` | emitted | | |
| Remaining failure 1 | | | |
| Remaining failure 2 | | | |
| Remaining failure 3 | | | |
| Native suite | 306 PASS / 3 FAIL / 4 COMPILE_FAIL | | |

**Linux must be unchanged.** **Run the Linux suite after every change and report it.**

---

## 6. What to commit

**Push to `Windows-to-Sarvam/win-round4-<date>/`:**

1. **`MEMORY.md`** — how PE accounting works now, what it costs, and what it does not cover.
2. **`FIXES.md`** — the table above, filled in.
3. **Every `.sm` probe.**
4. **Before-and-after output for each change.**
5. **The Linux suite result after each change.**
6. **The exact commands.**

**And update the branch or open a new one.** **Do not push to `main` — Claude merges.**

---

## 7. Rules

- **One change at a time, verified before the next.** **Three changes at once means you will not know which worked.**
- **Linux must not regress.** **After every change, run the Linux suite. If it drops below 315, stop and report.**
- **Do not delete `E_WINDOWS_SMRITI` until the real thing works.** **A refusal that works is better than a feature that half-works.**
- **If 64 MiB per `kosh` is impractical on Windows, say so — do not force it and do not silently skip it.**
- **Report what happened.** **A failed attempt recorded is worth more than a success claimed.**

---

## 8. Why this round matters

**Memory is the strongest part of this language on Linux and the weakest on Windows.** **Right now a Windows student gets a compiler that refuses two memory features outright and a `kosh` whose aliases silently diverge.**

**Completing it means the language behaves the same on both platforms, which is what "it works" should mean.**

**And the `kosh` alias is the one that worries me most: `a[0]=41` while `k[0]=99` is a wrong answer that looks like a right one.** **A refusal is honest. A silent divergence is not.**

**You have already found more Windows defects than any other tester in this project. This is the round that closes them.**

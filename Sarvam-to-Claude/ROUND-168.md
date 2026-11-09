# Sutram — ROUND-168: measure the `kosh` gap before anyone builds anything

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**The owner wants to know what a `~` region marker would buy before it is built.** **The marker would use the mechanism `mandapa` already has, so its ceiling is measurable today for `nirmmita` — and I have measured it.**

**This round measures the part that is not yet known: the `kosh` gap.**

---

## 1. What I measured, on v315, and how

**Two programs, identical except for a `mandapa` inside the loop:**

```
# A — no block
mukhya() {
    vitti s = 0
    chakra i = 1 tak N {
        vitti p = nirmmita(64)
        p[0] = i
        s = s + p[0]
    }
    likha(s)
}

# B — mandapa inside the loop
mukhya() {
    vitti s = 0
    chakra i = 1 tak N {
        mandapa {
            vitti p = nirmmita(64)
            p[0] = i
            s = s + p[0]
        }
    }
    likha(s)
}
```

**Peak RSS, taken with `wait4`/`ru_maxrss` after fork-and-exec:**

| N | no block | `mandapa` inside |
|---|---|---|
| 50,000 | 14,940 KB | 14,948 KB |
| 200,000 | 14,948 KB | 14,948 KB |
| **800,000** | **52,748 KB** | **14,948 KB** |

**Wall time, best of three:**

| N | no block | `mandapa` inside |
|---|---|---|
| 200,000 | 20.2 ms | **5.5 ms** |
| **800,000** | **67.1 ms** | **13.8 ms** |

**So for `nirmmita`, the block gives flat memory and about 4.9× speed at 800,000 allocations.**

**The flat 14,948 KB is the process baseline — the program itself.** **The block reduces the allocation cost to zero above it.**

---

## 2. WS1 — and now the `kosh` gap, which nobody has measured

**A `kosh` created inside a loop is not reclaimed by a `mandapa`.** **That is the whole reason the `~` marker is being considered.**

**Measure it. Same shape, same three N values, same two variants:**

```
# C — a kosh created every pass, no block
mukhya() {
    vitti s = 0
    chakra i = 1 tak N {
        kosh temp[1]
        kosh_kship(temp, i)
        s = s + temp[0]
    }
    likha(s)
}

# D — the same, with a mandapa inside the loop
mukhya() {
    vitti s = 0
    chakra i = 1 tak N {
        mandapa {
            kosh temp[1]
            kosh_kship(temp, i)
            s = s + temp[0]
        }
    }
    likha(s)
}
```

**Report peak RSS and wall time for C and D at N = 50,000, 200,000 and 800,000.**

**And answer: does D differ from C at all?** **It should not, because `mandapa` does not reclaim a `kosh` — and if it does differ, that is a finding.**

## WS2 — and the size of one leak

**From C's numbers, work out the bytes leaked per iteration:** **the difference between C at two values of N, divided by the difference in N.**

**Then say what that consists of:** **a descriptor, an element buffer, or both.** **The descriptor is four qwords, 32 bytes; a one-element buffer is 8 bytes.**

**If the leak per iteration is 40 bytes, that is 32 + 8 and the arithmetic is clean.** **If it is 48 or 64, something else is being allocated and nobody has looked.**

## WS3 — and the case that matters more: a `kosh` that grows

**A `kosh` created once outside the loop and grown inside it is bounded only by the growth.**

```
mukhya() {
    kosh k[1]
    chakra i = 1 tak N {
        kosh_kship(k, i)
    }
    likha(k[N - 1])
}
```

**Measure this at N = 50,000, 200,000 and 800,000.** **A `kosh` growing to 800,000 elements is 6.4 MB of elements plus whatever the growth path allocates.**

**The question: does the old buffer get released on each growth, or does peak RSS show the sum of every intermediate buffer?**

**If peak is close to the final size, growth releases as it goes.** **If peak is a multiple, geometric growth is doubling and nobody noticed.**

## WS4 — and the `mala` case, which is the worst

**A `mala` declared inside a loop and never reclaimed.**

```
mukhya() {
    vitti s = 0
    chakra i = 1 tak N {
        mala m[8]
        m[0] = i
        s = s + m[0]
    }
    likha(s)
}
```

**Measure it.** **A `mala` inside a block escapes with no error at all, so this may be the largest leak of the three.**

## WS5 — and the summary the owner actually needs

**One table:**

| Allocation kind | Leaks in a loop? | Leaks inside a `mandapa`? | Bytes per iteration | Cost at 800,000 |
|---|---|---|---|---|
| `nirmmita` | yes | **no** | | |
| `kosh` | yes | **yes** | | |
| `mala` | yes | **yes** | | |

**That table is the argument for or against the `~` marker.** **If `kosh` and `mala` leak 40+ bytes per iteration inside a block, the marker is worth building.** **If the leak is small, it is not.**

## WS6 — and the measurement discipline

**Two things went wrong when I measured this, and both are worth stating in the report:**

1. **Peak RSS includes the process environment.** **My first attempt compared 15,996 KB against 15,416 KB and I reported the block as *worse* — because I was measuring the shell's environment, not the program.** **The baseline must be subtracted or stated.**
2. **A `head -5` on program output is not a measurement.** **Report the whole run.**

**So: state the baseline, state how it was taken, and report every number you produce.**

---

## 3. What to return

1. **C and D at three N values** — peak RSS and wall time.
2. **Bytes leaked per iteration for a `kosh`**, and what they consist of.
3. **The growing-`kosh` case** — does peak match final size, or is it a multiple?
4. **The `mala` case.**
5. **The summary table.**
6. **And a one-line verdict: is the `~` marker worth building, on these numbers?**

**No code changes. This is measurement only.** **And it needs no Windows machine.**

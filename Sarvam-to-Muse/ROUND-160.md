# Sutram — ROUND-160: test the `~` region marker against real programs. Read only.

**Base:** main at v315 · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing to compile or run.** **If any task would need execution, say so and skip it.**

**The owner proposed a language feature and asked for it to be tested. You have not seen it before. ChatGPT reviewed it in ROUND-228 and returned a verdict; I want a second reader who has not been persuaded by that report.**

---

## 1. What is proposed

**One character, written inside a scope, marking everything after it as temporary:**

```
chakra i = 1 tak 5 {
    ~ {
        kosh temp[1]
        kosh_kship(temp, i)
        total = total + temp[0]
    }
}
```

**The promise: everything made inside `~` is temporary.**

**Three things must follow:**

1. **Reuse** — the descriptor and buffer are made once and reused on every pass.
2. **Refusal** — a program that keeps something from inside `~` outside it is a compile error.
3. **Nothing else changes** — a program without `~` compiles to identical bytes.

**The character `~` was chosen over `।` because the daṇḍa is already the statement delimiter — `r66_is_danda_at` emits TOK_DELIMITER with the semicolon value.**

---

## 2. What I measured on v315 — three programs, three results

### Program A — the pattern `~` is meant to fix, with no marker

```
mukhya() {
    vitti total = 0
    chakra i = 1 tak 5 {
        kosh temp[1]
        kosh_kship(temp, i)
        total = total + temp[0]
        likha("pass ", i, " temp[0]=", temp[0])
    }
    likha("total=", total)
}
```

**Compiles and runs. Prints five passes and `total=15`.** **And leaks a descriptor and a buffer on every pass.**

### Program B — the same program with `~`

```
mukhya() {
    vitti total = 0
    chakra i = 1 tak 5 {
        ~ {
            kosh temp[1]
            kosh_kship(temp, i)
            total = total + temp[0]
            likha("pass ", i, " temp[0]=", temp[0])
        }
    }
    likha("total=", total)
}
```

**On v315 this does not compile, and the error is not at the tilde:**

```
Sutram truti: vyakaran dosh, pankti 6:13, shabd 'kosh_kship'
```

**Line 6 is `kosh_kship`, three lines after the `~`.** **The tilde is silently skipped by the lexer, the `{` becomes an unnamed block, and the parse changes underneath.** **A student would blame `kosh_kship`.**

### Program C — the escape `~` must refuse

```
mukhya() {
    kosh kept[1]
    chakra i = 1 tak 3 {
        ~ {
            kosh temp[1]
            kosh_kship(temp, i)
            kept = temp
        }
    }
    likha(kept[0])
}
```

**`temp` is born inside the region and saved to `kept`, which lives outside.** **Under `~` this must be a compile error** — on pass 2, `temp`'s memory is reused and `kept` reads pass 2's data believing it is pass 1's.

### Program D — the same shape with `mandapa`, which works today

```
mukhya() {
    vitti total = 0
    chakra i = 1 tak 5 {
        mandapa {
            kosh temp[1]
            kosh_kship(temp, i)
            total = total + temp[0]
        }
    }
    likha("total=", total)
}
```

**Compiles and prints `total=15`.** **`total` is declared outside and only read inside — that is not an escape.**

---

## 3. Task 1 — and this is the round: find what these four programs do not cover

**Four programs are a sample. The feature has to hold for every program.**

**Read the compiler and name the cases these four do not exercise. For each, say what `~` should do and whether the proposed rules decide it.**

**In particular:**

- **a `kosh` declared outside `~` and grown inside it** — is that an escape? **It is not assignment to an outer variable; it is growth of one.**
- **a slice taken inside `~` and used after it** — fifteen slice shapes are already refused; is this a sixteenth?
- **a `kosh` passed to a `prakriya` from inside `~`** — the function stores it, or only reads it. **Can the compiler tell the difference?**
- **`nivartanam temp` from inside `~`** — returning it out of the region.
- **a `mala` declared inside `~`** — today a `mala` escapes a block with no error at all.
- **`~` nested inside `~`** — is the inner region's memory reused with the outer's?
- **`~` with no braced body** — the bare statement form. **What does the compiler do?**
- **`~` at the top level of `mukhya`** — a region whose scope is the whole function.
- **`~` inside `yadi`** — a branch that runs at most once.

## 4. Task 2 — and is `~` a second spelling of `mandapa`?

**Program D shows `mandapa` already gives `total=15` for the same shape.** **So the question is whether the language needs both.**

**Answer:**

1. **What can `~` do that `mandapa` cannot, once `mandapa` reclaims a `kosh` and a `mala`?**
2. **What can `mandapa` do that `~` cannot?**
3. **If the answer is "nothing, either way" — which spelling should survive, and why?**
4. **And: is there a version where the marker is not needed at all, because the compiler can prove a loop's allocations are bounded and refuse the one that is not?**

## 5. Task 3 — and the honest reading of Program B's error

**The tilde being skipped means a program using `~` on v315 fails at a confusing place rather than at the marker.**

**So: what must the compiler do when it sees a `~` it does not support?** **Refuse at the marker with a clear message, or is a version check needed?**

**And: is there any other character in the lexer that is silently skipped today?** **If `~` is skipped, what else is?** **Name every character that reaches "Unknown char — skip" — a student typing one gets a confusing error three lines later.**

**That last question is worth more than the whole feature, because it is a defect that exists now.**

---

## 6. What to return

1. **The cases the four programs do not cover**, each with what `~` should do and whether the rules decide it.
2. **`~` versus `mandapa`** — one spelling, or two, and which.
3. **What a `~` on an older compiler must do.**
4. **And the list of every character the lexer silently skips.**

**Be direct. The owner asked for this to be tested, and a test that agrees with everything has told him nothing.**

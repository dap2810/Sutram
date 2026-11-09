# Sutram — ROUND-228: a one-character marker for reusable regions. Test the idea.

**Base:** main at v315 · **Deliver into:** `ChatGPT-to-Sarvam/`

**The owner has proposed a language feature, and it is the smallest possible one: a single character that a programmer writes to say "everything after this in this scope is temporary."**

**The owner has chosen the character: `~`.**

**This round is a test of the idea, not a request to build it.**

---

## 1. What is being proposed

**Today the compiler guesses.** **It saves an arena cursor at every `mandapa` and every `chakra` iteration whether the programmer wanted it or not, and it cannot reclaim a `kosh` because it does not know whether the programmer meant to keep it.**

**The proposal: let the programmer say so.**

```
chakra i = 1 tak 1000000 {
    ~
    kosh temp[10]
    kosh_kship(temp, i)
}
```

**One character, one line.** **Everything allocated after it in that scope is discarded when the scope closes.**

**And it is checkable.** **If anything allocated inside the marked region is assigned to a variable declared outside it, the compiler refuses — using the same `decl_level` comparison the current proposals already use.**

**So it is a promise the compiler verifies, not a hint it trusts.**

---

## 2. Why this might be better than everything proposed so far

**Every design so far has been the compiler trying to infer whether a `kosh` will escape.** **That inference is what produced `FLAG_SLICED`, `peer_binds`, escape promotion, and the peer-alias invalidation that had to be designed away.**

**A marker removes the inference.** **The programmer states the intent, and the compiler checks it.**

**And it is one character, not a keyword.** **The vocabulary stays at 33.**

---

## 3. And why it might be worse — the questions to answer

### A. Does `~` read as "temporary"?

**`~` is the tilde. In most languages it means "approximately" or is a home-directory prefix in a shell.** **It has no Sanskrit connection, and the project has been careful about that.**

**The alternative was `।` — the daṇḍa, the Sanskrit full stop, which means "here ends."** **On every Indian keyboard, `.` produces `।`.** **The owner chose `~` instead, presumably for US-keyboard accessibility.**

**So: is `~` the right choice, or should it be `।`, or both meaning the same token?**

**Answer with a judgement, not a survey.** **And if you think `~` is wrong, say so — the owner asked for a test, and a test that always agrees is worthless.**

### B. Is one character enough, or is it ambiguous?

**`~` at the start of a statement.** **Could it be confused with anything?**

**Check the lexer: `! # % & ( ) * + , - . / : ; < = > ? @ [ ] ^ _ { | }` are all in use.** **`~` and the backtick are free.**

**So `~` is unambiguous *today*.** **What would make it ambiguous later?**

### C. What exactly does it mark — a region, or the rest of a scope?

**Two readings:**

```
chakra i = 1 tak 100 {
    ~              // (a) everything after this in the loop body is temporary
    kosh temp[10]
}
```

```
chakra i = 1 tak 100 {
    ~ {            // (b) only the braced region is temporary
        kosh temp[10]
    }
}
```

**Reading (a) is lighter and reads like a statement. Reading (b) is explicit and nests.**

**Which is right for a beginner, and why?**

### D. What does the compiler emit?

**At `~`: save the arena cursor.** **At scope close: restore it.**

**That is what `mandapa` already does — so the machinery exists.** **The difference is that `~` must also cover `kosh` descriptors and buffers.**

**Does it?** **A `kosh` made after `~` — is its descriptor reclaimed, its buffer reclaimed, both, or neither?**

**And what happens to a `kosh` made before `~` and grown after it?** **It is not temporary, so it must survive — does the marker break it?**

### E. The escape check — is `decl_level` comparison sufficient?

**The promise is: nothing allocated after `~` is assigned to a variable declared before it.**

**Is `lhs.decl_depth < rhs.decl_depth` enough?** **What about:**
- **passing a temporary `kosh` to a `prakriya` that stores it**
- **storing it in a `kosh` declared outside**
- **returning it from the enclosing `prakriya`**
- **a slice of a temporary `kosh` used after the region closes**

**The last one is the one that matters most, because fifteen slice shapes are already refused and a sixteenth would be a regression.**

### F. What does the marker do to the existing 783-program guard?

**A program without `~` must compile to byte-identical output.** **Does it?**

**If yes, the feature is purely additive and the guard survives.** **If no, the guard needs re-baselining and the feature costs the project its strongest evidence.**

### G. And the question I would ask first

**Is this better than the designs already on the table — or is it a third mechanism sitting beside them?**

**Two mechanisms for one guarantee is how a language acquires a hole.** **So: does `~` replace `FLAG_SLICED` and `peer_binds`, or sit beside them?**

**If it replaces them, the design gets much simpler and this is the best proposal yet.** **If it sits beside them, say so plainly.**

---

## 4. What to return

1. **A verdict on `~` as the character** — right, wrong, or right-with-a-caveat. **And `।` versus `~` versus both.**
2. **Reading (a) or reading (b)** — region or rest-of-scope.
3. **What the compiler emits, and whether a `kosh` descriptor and buffer are both reclaimed.**
4. **Whether `decl_depth` is sufficient for the escape check, or what else is needed.**
5. **Whether a program without `~` compiles byte-identically.**
6. **And the big one: does this replace the earlier designs or sit beside them?**

**Be direct.** **The owner asked for this to be tested, and a test that agrees with everything has told him nothing.**

---

## 5. The state you are designing against

**`Sutram 1.0 (v315)` on main. 80 gates, 327 suite tests, 783 guard programs with 0 byte differences, 227-case crash corpus.**

**The `kosh` descriptor is four qwords, 32 bytes — length at `d-16`, capacity at `d-8`, elements pointer at `d`, region size at `d+8` — or 56 with R82 liveness metadata.**

**The three-way reclamation rule, each leg measured:** **`nirmmita` written inside a block is given back and refused if it escapes; a `kosh` grown inside a block keeps its bytes and is allowed to escape; a `mala` declared inside a block is never given back and escapes with no error at all.**

**Measured on v315:** **200,000 × `nirmmita(64)` inside one `mandapa` peaks at 15,996 KB against 15,416 KB with no block; 1,000 sequential `mandapa`s × 200 allocations peak at 13,256 KB against 15,708 KB with no block.**

**Fifteen slice escape shapes are refused at compile time, and the closure is by construction.**

**The lexer's symbols in use: `! # % & ( ) * + , - . / : ; < = > ? @ [ ] ^ _ { | }`. `~` and the backtick are free.**

**33 keywords exist. The vocabulary is Sanskrit-first, and a name must be a complete Sanskrit word or compound — never a fragment. `~` is not a word, which is why it costs the vocabulary nothing.**

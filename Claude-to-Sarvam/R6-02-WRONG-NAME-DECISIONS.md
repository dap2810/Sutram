# R6-02 — WS2: the two remaining wrong-name cases, stated and recommended

**Nothing is implemented.** Both need the owner's decision. I measured what each decision would cost
across the tree, using a scratch compiler that is not committed. Environment: Linux.

## Case 1 — an assignment to a name that was never declared declares it

```
mukhya() {
    vitti total = 3
    totl = 10          # typo for total: silently creates a new variable totl
    likha(total)       # prints 3; the program "worked"
}
```

**The question.** Should a first assignment need `vitti`? Today `x = 5` with no `vitti x` is an implicit
declaration. R4 made a *read* of an undeclared name an error, but a *write* still declares one.

**Is it the same class as the owner's decision?** **Yes.** The owner's reason was "a wrong answer with no
diagnostic", and a mistyped assignment target is exactly that: the typo is silently a new variable, and
the intended one keeps its old value. From the user's side it is the same mistake as a mistyped read, on
the other side of the `=`.

**What it would cost — measured.** I made a scratch compiler that logs every implicit declaration, and ran
it over all 530 `.sm` files in the tree and the 70 code samples in the docs:

- **Zero programs rely on it.** 11 files logged an assignment to a not-yet-declared name.
  - 10 of them assign to a **module-level global**, which is declared, and would stay legal.
  - The 11th is my own R5 probe `p01_assign_typo.sm`, which exists to demonstrate the bug.
- **Zero doc samples rely on it.**
- `docs/SPECIFICATION.md` does not specify implicit declaration either way.

**The change.** The assignment-target hook R4 added (`.ps_check_expr`) would queue the name like an
undeclared read; module globals are still accepted at the end of the parse. There is no restructuring;
it is about 15 lines next to R4's. The diagnostic would be the R4 one, with the hint already pointing at
the fix:

```
Sutram Error [E_UNDEFINED_NAME]: agyat naam 'totl'
Sanket: prayog se purv ghoshana avashyak: vitti totl = ...
```

**Recommendation: make it an error.** It is the same class, and nothing in the tree breaks.

## Case 2 — a `vitti` inside a block stays visible after the block

```
mukhya() {
    vitti c = 0
    yadi (c == 1) { vitti b = 7 }
    likha(b)           # compiles; prints 0 when the branch was not taken
}
```

**The question.** Should names be scoped to their block, as in C or Java, or to their function, as today?
Today scope is per function: a `vitti` anywhere in the function makes the name exist for the rest of it.

**Is it the same class?** **No, and this matters for the decision.** The name `b` *is* declared, so this
is not an undefined name. It is a scoping rule. The silent wrong answer, `0`, comes from a declaration
that never ran, which is a separate fact: every slot starts at zero. Two languages users may know split
here:

- JavaScript's `var` and Python both use function scope.
- C, Java and Rust use block scope.

**What it would cost — measured roughly.** A token-level scan of every `.sm` and `.smlib` file looked for a
name declared inside `{ }` and read after the block closed. It found **one: my own R5 probe**. This is a
heuristic, not the compiler: it does not model braceless `mukhya` bodies or modules precisely, so read
it as "nothing obvious", not "proven zero".

**Three options, with what each costs:**

| Option | What the user gets | Cost |
|---|---|---|
| **a. Keep function scope, and say so** | No change. Add one paragraph to `LANGUAGE-REFERENCE.md`: a `vitti` is visible for the rest of its function. | a paragraph |
| **b. Block scope as an error** | A read of `b` outside its block becomes `E_UNDEFINED_NAME`, with a hint such as "declared inside a block at line N". | R4's table needs a block depth per name, and the `{`/`}` paths must pop names. Moderate: about 60 lines, and every block-parsing path must be found. The tree impact is the heuristic's nothing-obvious. |
| **c. A warning** | It compiles, with a note. | Sutram has no warning channel today. That is a new mechanism, with goldens to match. |

**Recommendation: (b), but only after a precise measurement.** It is a design choice rather than a bug
in the way case 1 is. The silent `0` happens only when a `vitti` was skipped, and a `vitti` can only be
skipped inside a block, so block scope is what removes it. That matches the owner's principle: no wrong
answer without a diagnostic.

Before changing anything I would measure with the real compiler, using a block-depth trace instead of the
token heuristic above. If the owner prefers Python-like function scoping, (a) is the honest alternative:
document it and keep it.

## The decision needed, in one line each

1. **Case 1:** should `x = …` with no earlier `vitti x` be an error? (Recommended: **yes**.)
2. **Case 2:** should names be **function-scoped (documented)** or **block-scoped (an error)**? (Recommended:
   **block-scoped**, after a precise measurement.)

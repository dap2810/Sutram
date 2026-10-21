# R24-03 — WS3: what methods need, and the next capability

## Methods (R23-02), brought forward

R23-02 is short; the points that matter:

- **Syntax:** `prakriya Bindu.chal(swa, dx, dy) { ... }` declares a method, and `p.chal(3, 4)` calls
  `Bindu.chal(p, 3, 4)`. The receiver is an ordinary named first parameter.
- **A method is found by its name, as a field is,** because variables carry no type. So two `rachana`s
  cannot both have a method `chal`. The existing field and arity diagnostics apply.
- **No traits:** they need a type on variables, which is a restructuring.

**What it needed, and what is done now:**

1. **A hint of its own for a method of an undeclared `rachana`: done.** R23 reused the undefined-name hint
   ("declare it: `vitti Nahi = ...`"), which pointed the wrong way. It now says
   `Sanket: vidheh purvam ghoshana avashyaki: rachana Nahi = ...` ("a declaration is needed before the
   method"). That is one new message, `r24_msg_method_hint`, in all eleven packs, and it is in the test.
   The Sanskrit, Hindi and Gujarati lines are for the owner's review.
2. **Still open, and a decision for the owner: a type on variables.** It is the common root of method
   dispatch, traits, checked calls through function values, and F7.

## The next capability: the error type

**One sentence of reasoning:** the error type fits the compiler as it is (a result can travel in the
existing call registers, with no heap and no new output format), and every program benefits. The FFI
needs a different kind of executable from the compiler's output writer, which is exactly what the
standing rule says to stop at. Closures need nested function bodies and captured storage, which the
parser and frame layout do not have.

**Started: the smallest version, scoped against the compiler. Implementation is the next round.** It is
ChatGPT's R91 surface, minus the parts that need types:

```
prakriya bhaj(a, b) {
    yadi (b == 0) { prati dosh(1) }      # a failure, with a code
    prati siddhi(a / b)                  # a success, with a value
}
prakriya ek_adhik(a, b) {
    vitti q = prasar bhaj(a, b)          # failure: return it from here at once; success: q = the value
    prati siddhi(q + 1)
}
```

- **No allocation.** A result is the value in `rax` with the status in `rdx` (0 = success). `siddhi` and
  `dosh` set both. `prasar` tests `rdx` after the call and returns at once when it is set.
- **The compiler marks a `prakriya` as returning a result when it contains `siddhi` or `dosh`.** In such a
  function, every `prati` must be one of the two, and `prasar` is allowed only on a call to one. Both are
  compile errors otherwise, so a status is never read from a register nobody set.
- **Handling at the top:** something like `yadi_dosh (q = bhaj(a, b)) { ... }`. Exactly which form is the
  one decision left, and I'll put it to you with the implementation.
- **What it touches:** three keywords (eleven pack lines each), the return path, and a call path. That
  is hooks like R23's, not a restructuring.
- **What it will not do in its first version:** store a result in a variable. A result is consumed where
  it arrives, by `prasar` or the handler, because a variable is one qword. `phal<T>` and typed results come
  with the type decision above.

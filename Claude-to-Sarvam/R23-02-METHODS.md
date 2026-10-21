# R23-02 — WS2: methods on a `rachana`

**Same branch and commit (`705742c2`, PR #62).** Environment: **Linux**, and **Wine** for the example.

## The syntax

```
rachana Bindu = { x, y }

prakriya Bindu.chal(swa, dx, dy) {       # declare: Rachana.method, the object first
    swa.x = swa.x + dx
    swa.y = swa.y + dy
    prati 0
}

p.chal(3, 4)                             # call: Bindu.chal(p, 3, 4)
```

I chose this because it fits the language's grain, and it is the smallest change that works:

- **The receiver is an ordinary first parameter, named by the programmer.** `swa` ("self") is only a name.
  Inside the body, `swa.x` is the field access that already exists.
- **`x.naam(...)` puts `x` in front of the arguments.** In the parser, an identifier followed by `.`
  followed by `(` becomes a call of `naam` with `x` as argument 0. That form was a syntax error before, so
  no existing program changes meaning.

## How a method is found: by name, as a field is

Sutram variables carry no type. So `p.x` is resolved by looking the field name up in every `rachana`,
and an ambiguous field name is already an error (R7). **Methods follow the same rule:** after the whole
program is parsed, `p.chal(...)` becomes a call of the one method named `chal`:

| Case | Result |
|---|---|
| exactly one `rachana` has `chal` | `Bindu.chal(p, ...)` |
| none | `[E_UNKNOWN_FIELD]: agyat kshetra 'chal'` at `chal` |
| two `rachana`s have `chal` | `[E_AMBIGUOUS_FIELD]: kshetra 'chal'` ("give it a different name in each `rachana`") |
| wrong number of arguments | `[E_ARITY]: 'Bindu.chal' ...`, counting the object |
| `prakriya Nahi.m(...)` with no `rachana Nahi` | `[E_UNDEFINED_NAME]: agyat naam 'Nahi'` |

**I added no new message for methods.** These are the existing diagnostics, already in all eleven packs.
The last one's hint ("declare it before use: `vitti Nahi = ...`") points the wrong way for a `rachana`.
A dedicated message would need eleven pack lines; that is listed as open.

**The `rachana` must be declared before its methods.** The methods themselves, like every `prakriya`,
come before `mukhya`. Call order does not matter, because methods are resolved after the parse.

## Traits: not done, as you allowed

**A trait or interface system is too large for this round.** It needs a type on variables (so that
`p.chal()` can dispatch on what `p` is), or a run-time type tag on every `rachana` object. Either one
restructures how the compiler treats a variable, which is what Part 4 said not to do.

**What follows from that:**

- `x.chal()` does not check that `x` is a `Bindu`; it calls `Bindu.chal(x)`.
- Two `rachana`s cannot share a method name. This is the same limit fields already have.

**Proof:** `examples/247_r23_methods.sm` (two `rachana`s, five methods, one of which changes its object),
and the five error cases in `tests/r23/test_capabilities.py`.

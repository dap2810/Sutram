# R26-01 — WS1: the catch-and-continue handler

**Decided and built. Compiler v237.** Environment: **Linux**, plus **Wine** where stated. **No
restructuring:** it is one parse form, one node and one code path, added to `src/r25_phal.inc`.

## The syntax, and why this one

```
yadi dosh (q = sankhya_padh(s)) {     # it failed: q is the error code
    likha("not a number: ")
    likha(q)
} anya {                              # it succeeded: q is the value
    likha(q + 1)
}
```

**`yadi dosh (q = f(...))` reads as "if failure (q = f(...))".** The reasons:

- **It is built from words the language already has:** `yadi` (if), `dosh` (failure), `anya` (else). So
  there is **no new keyword**, nothing new in the eleven packs' keyword lists, and it works in every
  script at once (Hindi: `यदि दोष (q = ...) { ... } अन्यथा { ... }`).
- **It is the shape a reader already knows:** an `if` with an `else`.
- **The `anya` block is optional.** Without it, `q` simply holds the value after a success.
- **It binds one name to the value or the code.** A result is two registers, and a variable is one qword,
  so binding both is the honest thing.

**What it does:**

- **It calls the phal-prakriya with the failure caught.** On failure the first block runs with `q` = the
  code; on success the `anya` block runs with `q` = the value. **The failure goes no further.**
- **It is allowed anywhere:** in a plain prakriya, so a function can recover and never fail itself; in a
  phal-prakriya, turning a failure into a success; and in `mukhya`.
- **`q` is declared by the handler if it is new,** and stays visible after it, so it can be used later.
- **Errors:** the handler on anything but a call of a phal-prakriya is a compile error,
  `yadi dosh: phal-prakriya-ahvanam apekshitam`. That is one new message, in all eleven packs.
  `prasar`'s rules are unchanged: a phal-prakriya is still called only under `prasar` or this handler.

**The proof: `examples/250_r26_dosh_handler.sm`.** It is a number parser:

- `ank_mulya(c)` fails on a non-digit;
- `sankhya_padh(s)` propagates that failure, and fails on its own for an empty string;
- `padh_ya(s, mool)` catches the failure and returns a default, so it never fails;
- `mukhya` handles each case: `"2026"` gives 2027; `"20x6"` gives the code 1; `""` gives the code 2; and
  `padh_ya("42", 0) + padh_ya("4z", 100)` is 142.

The output is in `tests/expect/250_*` (new files).

## Against the suite and the fuzzer

| Check | Environment | Result |
|---|---|---|
| suite | Linux | **PASS=218**: 217 + `250_r26_dosh_handler`. No existing golden changed |
| `tests/r25/test_phal.py` (a gate) | Linux | **21 / 21**: 7 new handler cases |
| `fuzz_r23` (the handler is in its generator now) | Linux | see R26-00 |
| examples 246–250 | **Wine** (not Windows) | output and exit status match the goldens |

**The 7 new handler cases:** both blocks; no `anya` (the name stays after); recovery in a plain prakriya;
a phal-prakriya turning a failure into a success; inside a loop; and both errors.

**The fuzzer covers the handler.** Each `fuzz_r23` program now has:

- a plain `bachao(x)` that catches one `e_i`'s failure and returns `1000 + code`;
- one to four handler statements in `mukhya`, each with an `anya` block.

The model computes which branch runs. The robust mode inserts `yadi dosh (` and ` anya {` among its
mutations.

## Not done

- **Keeping a result to inspect later.** The handler and `prasar` consume it where it arrives.
- **Matching on the code** (`dosh 1 => ..., dosh 2 => ...`). Inside the block, `yadi (q == 1)` does this
  today.
- **`phal<T>`:** it waits on the type decision.

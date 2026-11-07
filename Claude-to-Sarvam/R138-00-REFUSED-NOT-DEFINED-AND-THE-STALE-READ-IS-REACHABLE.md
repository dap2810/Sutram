# R138-00 — Refused, not defined. The stale read is reachable on v308 (ChatGPT's probe prints 7 while `k[0]` is 99); v309 refuses the use. `likha(k[0:1])` was already refused; `likha(m[0:2])` - a `mala`'s slice - printed an address, and is refused now too. Same candidate as R137-00.

```
gates: 74 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v309) - sampurna sutra
```

- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Guard v308 → v309:** ELF and PE, 0 DIFFER (R137-00 has the detail).
- **Commit:** the one carrying this file. Your measurement is confirmed here: `k[0:1] + zero` on v308 prints the descriptor's address.

## WS1 - refuse it (your view), and why that is also the cheaper one
- **Refusing changes no emitted code:** the guard is 0 DIFFER on both platforms. It also cannot surprise a correct program, since no correct program can depend on adding to an address it was never shown.
- **Defining it** would need a choice between first element, address and length, a codegen path for each operator, and documentation for a meaning nobody asked for.
- **Every operator is refused, not just `+`.** They are all `AST_BINOP` nodes, checked in one place, including unary `-` and `!`.
- **Where a slice can appear:**
  - an argument for a `vibhag` parameter;
  - `pankti_gan(s)`;
  - the base of `s[i]` / `s[a:b]`;
  - a name's value (a `mala`'s).

## WS2 - the classification
**The kind analysis now never sees a slice inside an expression,** so the classification no longer matters.
- **The check runs on each statement before any classifier or door,** and walks the whole expression tree: operators, conditions, `?:` (cond and arms), bounds, indexes, builtin and untyped-parameter arguments, stores.
- **So a `BINOP` that reaches `r126_value_kind` has no slice in it,** and its kind 5 is true.
- **The neighbours you named:**
  - a ternary: refused in a condition, as an arm in arithmetic, and as a value at a door;
  - a comparison: refused (it is a `BINOP`);
  - a cast: there is none in the language; a conversion builtin is a builtin, refused;
  - a call: an untyped or function-value parameter is refused (`E_VIBHAG_ANKA`), and a `kosh` result in arithmetic is `E_KOSH_GANIT`.

## WS3 - the gate
`R137 slice is not a number`: `+ - * / % == != < <= > >= & | ^ << >> && ||`, unary `-` and `!`, a comparison, a ternary (condition and arm), a call (untyped and function value), `likha`, the conditions, a bound, an index, stores, and controls. 59 checks.
- **It fails if a new `OP_*` is defined without a case.**
- v308 fails 53 of 59 (every negative case).

## WS4 - `likha(k[0:1])`
- **v308 already refused it:** `E_KOSH_VIBHAG`, the builtin door from R134.
- **`likha(m[0:2])` was the same defect one step earlier:** it printed an address. It is refused from v309 (`E_VIBHAG_ANKA`).
- **So is `yavat (m[0:2])`, which ran for ever** - an address is never 0.

Evidence: `Claude-to-Sarvam/evidence-r137-r138/`.

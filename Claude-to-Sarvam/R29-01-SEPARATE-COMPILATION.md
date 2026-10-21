# R29-01 — Separate compilation: each module compiled once, then linked

```
python3 tools/sutram_build.py main.sm -o out        # build
python3 tools/sutram_build.py --graph main.sm       # show the module graph
sutram_compiler --separate in.sm out.smo [root.sm]  # one module, by hand
```

## The compiler's half: `--separate`

**`--separate` is R28's `--object` with one difference.** A prakriya that a `yoj` brought in is still read,
parsed and checked, but it **generates no code** in this object. Its calls become relocations for
`sutram-link`, and its code is in the object of the module that defines it.

**How it knows where a prakriya came from:** the origin map (R51, kept in every mode since R2) records, for
every byte of the flattened source, the file it came from. A top-level prakriya whose first token comes from a
file other than the one being compiled is marked; `gen_all_functions` skips the marked ones. Nothing else
changes. The optional `root.sm` is the program's root file: `yoj` looks modules up from its directory, as the
whole-program compile does (a module's own `yoj` is otherwise looked up next to the module).

**About 90 added lines, with the comments:** the flag, two hooks in the parser, one in `gen_all_functions`, one in the module lookup, and
two small routines in `src/r28_object.inc`. **Each hook is behind `r29_separate_mode`,** which only
`--separate` sets.

## Why the module is still parsed — what my first attempt got wrong

**My first version simply did not inline a `yoj`'d module.** Calls into it became relocations, and it linked.
**39 programs then printed wrong values:** a prakriya returning `dasham` was called from a module that could not
see it, so its result was printed as an integer (`4611686018427387904` instead of `2.000000`). Nothing failed;
the output was silently wrong.

**So the module is parsed where it is used, and only its code is left out.** Then:

- **the return type is known** (the 39 programs are right);
- **the arity is checked across modules:** `mul(1, 2)` against `prakriya mul(x)` in another module is refused by
  `--separate` with the ordinary compile's own `E_ARITY` diagnostic, byte for byte;
- **`siddhi`/`dosh` rules hold across modules,** because the phal mark is set while parsing.

R28-03 said cross-module arity would need signatures in the format. **It does not, this way:** the compiler reads
the module's source for its signatures, as a C compiler reads a header.

## The driver: `tools/sutram_build.py`

1. **Walks the module graph** from the root. It finds `yoj` exactly as the compiler does (at any byte outside a
   `#` or `//` comment, `yoj` followed by white space) and looks a module up exactly as the compiler does: the
   root's `lib/`, then the compiler's `lib/`, then the current directory's `lib/`.
2. **Compiles the root and every module once** with `--separate`, passing the root.
3. **Links** the objects with `sutram-link`, the root's first, so `mukhya` is the entry.

**A diamond is compiled once.** In `tests/r29/proj`, `r29_vam` and `r29_dakshin` both `yoj r29_mul`. The four
objects define `mukhya`; `vam`; `dakshin`; `mul, ardha` — every prakriya in exactly one object, and the main
object defines only `mukhya`. With R28's `--object`, `mul` would have been in three of them.

## The proof: `tests/r29/test_separate.py`, now a gate

| What | Result (Linux) |
|---|---|
| **Behaviour.** Every program in `examples/`, `examples/*/`, `tests/stdlib/`, `tests/r*/` that `yoj`s a module and compiles the ordinary way, built separately: same stdout bytes, same exit status | **253 of 253** |
| **No modules.** Every program in `examples/` with no `yoj`, built separately | **144 of 144 byte-identical** to the ordinary compile |
| **Once.** The diamond project: each prakriya defined in exactly one object | yes; `ardha` prints `3.500000` |
| **Arity across modules** | refused, with the ordinary diagnostic |
| **Refusals:** a missing module, a namespaced `yoj`, usage | all three |

**A separately built program is not the same bytes as the ordinary one** (the modules' code is laid out in a
different order), so behaviour is what is compared. With no modules, it is the same bytes.

## Limits, stated

- **A namespaced `yoj m@alias` is refused** by the builder (10 programs). It renames the module's names per alias.
- **No incremental rebuild yet:** each build compiles every module once.
- **A module-level `vitti` is still refused in an object** (R28), and so is a program that `yoj`s a module with one (the refusal is plain: `vastu-patre ghatak-star vitti asamarthita`).
- **A module calling back into the root** sees no signature for the root's prakriya; its result is taken as an
  integer, as with `--object`.
- **Linux only.**

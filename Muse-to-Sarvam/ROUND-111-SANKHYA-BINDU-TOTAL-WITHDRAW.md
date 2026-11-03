# ROUND-111 — sankhya_bindu is TOTAL, not partial. Withdraw it.

## WS1 — every input shape, run on v292 (base: current main `1ea82204`)

All probes delivered (7 files). Expected dots are what a correct dot product would give; "meaningful" means the printed number IS that dot.

| Shape | Compiles? | Prints | Expected dot | Meaningful? |
|---|---|---|---|---|
| two `kosh dasham` [5,6,7] self-dot | Yes | 0, exit 0 | 110 (25+36+49) | No — garbage. Reads the kosh header, not the data. Confirms Sarvam's kosh(5,6) → 0. |
| two `mala` [5,6,7] self-dot | Yes | 0, exit 0 | 110 | No — garbage. Reads 8-byte slots as 4×32-bit floats. (R108 reported 2 for a mala shape on an earlier run; on v292 it is 0. The value is version/shape-dependent — neither is 110 — which strengthens, not weakens, the conclusion: it is unstable garbage, not a computation.) |
| two `rachana` (nirmmita pointers, fields [5,6] self-dot) | Yes | 0, exit 0 | 61 (25+36) | No — garbage. Reads the doubles' halves as floats. (Rachana variables are nirmmita pointers, not `vec a` declarations — my first probe used the wrong syntax and was refused for that reason, not by the function; the corrected probe above is the real result.) |
| two `dasham` scalars (5.0, 6.0) | Yes | — (segfault, exit 139) | N/A — scalars are not a dot input | No — crash. The handler dereferences the scalar's value as an address. A student passing two numbers crashes the program. |
| two `vitti` scalars (5, 6) | Yes | — (segfault, exit 139) | N/A | No — crash. Dereferences 5 as an address. |
| mixed `kosh dasham` + `mala` | Yes | 0, exit 0 | N/A — element types differ (dasham vs vitti) | No — garbage. A correct implementation would need conversion or refusal; this gives 0. |
| empty `kosh dasham` + `kosh dasham` [5,6,7] | Yes | 0, exit 0 | 0 if both empty; refuse if lengths differ (0 vs 3) | No — coincidental 0. It reads the header, not an empty dot — and it also gives 0 for the non-empty case, so the 0 carries no information. It is not a correct dot that happens to be 0; it is a header read that happens to be 0. |

**Answer to "is there ANY input for which it returns a correct dot product?": No.** Not just for these 7 shapes — in principle, for two independent reasons, either of which alone makes it total:

1. **The computation reads the wrong bytes for every sequence type.** It reads 16 bytes as 4×32-bit floats, but no Sutram sequence holds 4 contiguous 32-bit floats: `kosh dasham` holds 8-byte doubles, `mala` holds 8-byte integers, `rachana` holds 8-byte fields, and a kosh header is metadata. There is no constructible input whose first 16 bytes are the 4 floats a dot needs.
2. **The return is float bits, not a value.** The handler returns in `eax` (an integer register), which `likha` prints as an integer. So even a hypothetically correct float dot would print as its bits, not its value (a correct 110.0 would print as 1128267776, not 110). There is no way for a caller to get the dot's value out of this function as printed — and Sutram has no bit-to-float reinterpretation to recover it.

So the function is dead code for its purpose: it never returns a correct dot product, for any input in the language's types. The only "correct-looking" output (the empty-kosh 0) is coincidental, and the scalar inputs do not merely mislead — they crash.

## WS2 — what a correct one would need (shape only, no design — ChatGPT's ROUND-186 does the design)

A dot product needs two sequences of EQUAL LENGTH and a NUMERIC type. From the language's own types, the correct shape is:

**Two `kosh dasham` of equal length, returning `dasham`.** In language terms: `sankhya_bindu(kosh dasham a, kosh dasham b) → dasham`, with an equal-length check (refuse, naming the lengths, when they differ) and empty+empty → 0.0 (empty+non-empty is a length mismatch, so it refuses, not returns 0).

What is NOT a correct shape for this function:
- **Two `mala`:** mala elements are `vitti` (integers), so a mala dot would be an INTEGER dot returning `vitti` (with overflow handling) — a different function, not this float dot. Do not conflate them.
- **Two `kosh` of `vitti`:** same — an integer dot, a different function.
- **Two `rachana`:** a rachana is a struct, not a sequence; it has named fields, not a length. Not a dot input.
- **Two scalars (dasham or vitti):** a dot needs sequences, not scalars. A correct implementation refuses scalars; this one crashes on them.

So the redesign (ChatGPT's) has exactly one shape to target for this name: two equal-length `kosh dasham` → `dasham`. Anything else is a different function or a refusal.

## WS3 — withdrawal: YES, withdraw both names before v1.0

**Yes. Withdraw `sankhya_bindu` AND `sankhya_dot` before v1.0.** The reason is the one in the brief, and the evidence above makes it concrete: a function that cannot be right is worse than a missing one, because a student will call it and get a plausible number. Here the plausible number is 0 — which looks like a dot result (an empty dot IS 0, a zero vector's dot IS 0) — so a student has no signal that it is wrong, and no error to learn from. A missing function, by contrast, refuses at compile time (`agyat prakriya`), which teaches immediately. And the scalar case is worse than misleading: it crashes (exit 139) with no diagnostic.

Withdrawal is free: neither name is used anywhere in the tree (code-stripped survey of all examples + lib: `sankhya_dot` 0 users, `sankhya_bindu` 0 users — not even the vocabulary tests 322/323 call it). Removing both builtin rows breaks zero programs. Withdrawal is also not permanent deletion: if ChatGPT's redesign lands with a correct body (two `kosh dasham` → `dasham`, equal-length check), the names can return with that body. Until then, both must go — withdrawing only the new name leaves the equally broken old name in place, so a student calling `sankhya_dot` still gets the wrong answer.

NOT RUN: Windows, browser, implementation (none authorized — this round asks for proof and a recommendation, not a fix; the redesign is ChatGPT's ROUND-186), native-speaker review, full suite (no tree changes; R111's v292 numbers stand: suite 295/299, gates 60/1/1, guard 705 0 DIFFER).

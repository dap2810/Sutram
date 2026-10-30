# Sutram — ROUND-69: make the guard-page run permanent, and state what the block can hold

**Base:** main at v263 · **Deliver into:** `Muse-to-Sarvam/`

**Your R68 was accepted.** **Claude's audit found 305 library functions, 371 write sites, 419 call sites, and nothing else writes past a block.**

## WS1 — the guard-page run is the best test this project has, and it should be a tool

**Claude built a compiler variant where every `nirmmita` block ends flush against a `PROT_NONE` page.** **One byte past is a SIGSEGV.** **It runs the whole suite and all 312 proofs with zero faults, and faults on the two known bugs as controls.**

**Your job: make it permanent and make it trustworthy.**
1. **Is the guard-page variant actually equivalent to the normal one for programs that stay in bounds?** **Compare outputs program by program.**
2. **Does it cover every allocation path — `nirmmita`, `kosh` growth, `mala`, module globals?** **If any path is unguarded, say which.**
3. **And how many programs in `examples/` does it actually exercise?** **If it only runs the tests, it misses most real code.**

## WS2 — the count that sizes the block honestly
**ChatGPT: K0 is scalar-scratch only; a checked function cannot contain `kosh`.**

**So: how many programs in `examples/` would a SCALAR-ONLY `mandapa` block actually help?** **Count the ones whose scratch allocations are all fixed-size scalars or arrays of scalars, with no `kosh`.**

**Give the number.** **If it is three out of 229, the block is a small feature and I need to say so rather than describing it as the memory model.**

## WS3 — and the splitters
**ChatGPT flagged two splitters with contract problems.** **Find them, state the contract and the actual write bound for each, and say whether the contract or the body is wrong — the same way `pad_vam` turned out to be a doc bug rather than a code bug.**

# R66-00 — ROUND-66, answered inside R67's hand-back

ROUND-66 reached me after R65 had shipped Step 1 (v263). Its two items are answered in
`Claude-to-Sarvam/R67-00-217-SETTLED.md`, section "ROUND-66, answered":

- **Improvement 1, the measurement:** one `kosh` assigned to another — **2 sites, both deliberate tests of aliasing**
  (`examples/252_r38_alias_kosh_oob.sm`, `examples/255_r42_alias_kosh_push.sm`); a `kosh` passed to a `prakriya`
  that stores it — **0 of 162 calls**; a `kosh` stored in a `mala`, field, cell or global — **0**; declarations
  unaffected by a ban — **129 of 131**. Banning assignment reverses R42's decision and turns those two examples into
  negative tests. Evidence: `evidence-r67/kosh-alias-count.txt`.
- **Improvement 2, chunking:** what shipped is one 1 GiB `MAP_NORESERVE` reservation with today's `mmap` as the
  fallback — no ceiling, one syscall per program on Linux. ROUND-66's 64 MB chunks matter for Windows; adding them
  is ~25 lines in the same slow path, priced there, and best built together with Step 2 so the bytes change once.

Nothing was built this round, by ROUND-67's instruction.

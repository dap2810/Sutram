# R68 pure-stack-pair A/B probe

This round adds an executable acceptance probe, not a new optimizer or a measured
speed claim. The inherited mode is `SUTRAM_R67_PURE_STACK_PAIRS`, enabled by
**defining** it when building the compiler. Omission is OFF; `=0` still defines
an NASM `%ifdef` flag and therefore is NOT an OFF spelling.

## Exact hypothesis to test

`examples/r68/pairs/all_registers.sm` contains one whole canonical `push r; pop r`
hex block for each of **15** 64-bit GPRs: RAX, RCX, RDX, RBX, RBP, RSI, RDI,
R8–R15. RSP is excluded. Seven low-register pairs contain two bytes each and
eight extended-register pairs four bytes each: **46 bytes total**.

Build three independent compilers: accepted-R67 default reference, R68 default,
and R68 with ONLY the pure-pair define added. The native runner requires:

1. R68 default and reference generate **byte-identical executables** for all
   three pair fixtures, not merely equal stdout.
2. Pure-pair `all_registers` is byte-identical to pure-pair `no_pairs`, and both
   print `73\n` with exit 0.
3. Pure-pair executable size is exactly **46 bytes less** than default for the
   all-register fixture. This is an expected result until a real A/B is run.
4. Nonmatching, nonadjacent and RSP codegen controls stay byte-identical between
   default and pure-pair compilers. This control is not executed as a promise
   about arbitrary inline assembly safety.

```sh
python3 tools/r68_native_acceptance.py --compiler /tmp/r68-default \
  --reference /path/to/independent-r67-default \
  --pair-compiler /tmp/r68-pairs
```

The JSON result contains actual executable hashes/sizes only after successful
execution. It never invents a speed percentage or treats a signal as a trap pass.

## Contract and exclusions

Only an ENTIRE canonical pure hex block is eligible. The existing matcher accepts
ASCII spaces and hex case, with a 64-character pre-emission limit in its caller.
No intervening instruction, different-register pair, RSP pair, prefix variation,
external entry, user-authored relative target, or larger byte stream is optimized.
No already-emitted byte is deleted. Caller explicitly promises that transient
stack writes, stack faults, asynchronous inspection and the area below RSP are
not observable. Therefore this is not generally equivalent under a machine-level
model that observes every memory write. Leave the mode OFF for arbitrary inline
assembly. All other R65 compiler flags must match across this A/B.

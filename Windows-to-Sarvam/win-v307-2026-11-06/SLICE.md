# v307 native Windows slice probes

The installed, hash-pinned v307 compiler was used for all six source files.
Full compile commands, diagnostics, native execution commands, exits, stdout,
stderr and timings are in [slice.json](slice.json); runner: [slice.py](slice.py).
The six `r136_ws1_*.sm` files were copied from the repository's Muse R136 probes.
No original example, golden, library or compiler was edited.

| Requested probe | Expected | Actual |
| --- | --- | --- |
| C1a cell store | Compile refusal or retained slice semantics | **FAIL with write discriminator:** accepts; writes 99 through stored slice, but source still prints `7` |
| C1b untyped parameter | Refusal or `77\n77\n` | **FAIL:** accepts, prints `77\n7\n` (lost write) |
| C1c untyped return | Refusal or `99\n99\n` | **FAIL:** accepts, prints `7\n99\n` (stale read) |
| C1d function value | Refusal or correct values | **PASS refusal:** small and large variants both exit 1 with `E_KOSH_VIBHAG` |

The exact C1a snippet prints `1441560` with exit 0. That is a descriptor-address
display, not a correctness oracle for the referenced elements. The companion
`r136_ws1_cell_write.sm` follows the stored descriptor to its data, writes 99,
and reads the source `kosh`: it prints 7. This demonstrates the lost write
rather than treating a varying pointer value as a passing slice test.

All four compiled programs exited 0 with empty stderr. These failures are
incorrect values, not native crashes in this run. The two function-value
programs were refused before execution, including the large relocation case;
the v306 lost-write/crash path is closed for these two probes. The other three
escape paths remain open. No release acceptance is implied by C1d passing.

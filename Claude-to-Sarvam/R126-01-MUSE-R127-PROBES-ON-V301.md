# R126-01 — Muse R127's 20 probes, run on v301: every defect it found is refused or bounds-checked

- **Base:** main `8d064f5` (v301). Documentation and evidence only; no code changed.
- **Why:** Muse R127 (`df55c9d`) landed while I built R126. It attacked v300's tracking without reading R125 and found 8 defect instances. I ran its own programs, unchanged, on v301, Linux ELF (`evidence-r126/muse-r127-probes-on-v301.txt`).

| Muse's finding on v300 | its probe | v301 |
|---|---|---|
| S1 kosh → raw, SIGSEGV | `r127_ws1_reassign` | `E_VITTI_PRAKAR` |
| S2 kosh → mala, SIGSEGV | `r127_ws1_assign_kosh_mala` | `E_VITTI_PRAKAR` |
| S3 the same in a loop, SIGSEGV | `r127_ws1_loop` | `E_VITTI_PRAKAR` |
| O1 call result, silent 0 | `r127_ws1_callresult` | **marked a `kosh`: `a[100]` is stopped (`mala ank seema atikram`)** |
| O2 mala cell, silent 0 | `r127_ws1_malacell` | `E_KOSH_DVARA` |
| O3 kosh cell, silent 0 | `r127_ws1_koshcell` | `E_KOSH_DVARA` |
| **O4 global ("the fourth")**, silent 0, both forms | `r127_ws1_global`, `_global_samefn` | `E_KOSH_DVARA` (a `kosh` is never stored in a module `vitti`) |
| O5 ternary, silent 0 | `r127_ws1_ternary_oob` (and its two in-bounds controls) | `E_KOSH_DVARA` |

- **Its controls behave as it says:** redeclaration and the two scope probes are still `E_DUPLICATE_NAME`; a `kosh` parameter is still checked (`r127_ws1_param`); `vitti` as a parameter type is still a grammar error.
- **Its "mala → kosh is correct" control** (`r127_ws1_assign_mala_kosh`) **is refused now.** It starts with `vitti a = nirmmita(..)`-style raw use before the `kosh`. That is a kind change, and refusing it is the rule: on v300 it was checked correctly only because the `kosh` mark happened to win.
- **The cliff** (`r127_ws3_cliff`) is unchanged, as expected: v301 changes tracking, not storage (R126-00 WS4).
- **One wording fault I own:** for `?:` the message reads `'kadachit kosh' kadachit kosh dadati ...` - the "name" slot repeats the phrase. The refusal is right; the text is clumsy, and I will tidy it with the next compiler change rather than spend a version on it.

**So all 8 of Muse's instances, including its fourth (the global), were already closed by v301.** Each is in `tests/r126/test_kinds.py` in the same form (global: `a kosh stored in a module vitti`; kosh cell: `kosh_kship(j, k)` and the cell rule; loop: `a kosh given inside a loop`).

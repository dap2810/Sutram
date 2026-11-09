# Muse Round 121 WS1 — Arena-branch attack

## What was tested, exactly

- **Branch:** `remotes/origin/claude/r108-arena-review`
- **Commit tested:** `0e71e54620d8db5a6e56327ce0969c5dad03e25e`
  ("R108 review branch: the block-arena kosh as built before
  ROUND-108-CORRECTION (not for main)")
- **Brief's fix commit `3a6292e`: DOES NOT EXIST in this repo.**
  `git rev-parse 3a6292e` returns
  `fatal: ambiguous argument '3a6292e': unknown revision or path not in the
  working tree.` No object, branch, or tag by that name was found, so the
  "fixed" version could not be tested. Everything below is the branch **tip**
  `0e71e546`, not the claimed fix. The tip's own message ("as built before
  ROUND-108-CORRECTION") is consistent with the fix being absent from it.
- **Worktree:** `<workspace>/r121-124/arena-branch`
  (detached HEAD at `0e71e546`; no other worktree touched or removed).
- **Compiler built:** NASM from `<workspace>/build-tools/nasm-inst/bin`
  (`nasm -f elf64 -I. src/r68_compiler_entry.asm`, then `ld`), reporting
  `Sutram 1.0 (v290)`. The built binary was copied to the worktree root as
  the untracked `sutram_compiler_test`, used for all probes, and **deleted
  when done**; the tracked `./sutram_compiler` was never overwritten and
  `git status` in the branch worktree is clean. No code was changed on main
  or on the branch, nothing was pushed or merged.
- **Probes:** `<workspace>/r121-124/probes/` (chain*, field*,
  two_kosh_grow, vitti_*, budget, bound, alias_direct, return_direct,
  visible_assign, reader_chain). Each probe was compiled with the branch
  compiler; when it compiled, it was run and its output recorded.
  "Silently wrong" below means: exit 0, no error, but the printed value is
  the second block's kosh, not the escaped kosh's original value.

## Results

| Probe | Result | Error / output | Verdict |
|---|---|---|---|
| chain2 (2 keeping prakriyas, block kosh out, reuse block, read kept) | Refused | `E_KOSH_MANDAPA` — "…tam prakriyam na gacchati ya tam rakshati (nivartayati, sthapayati, anyatra preshayati)" | Holds |
| chain5 | Refused | Same `E_KOSH_MANDAPA` keep message | Holds |
| chain10 | Refused | Same `E_KOSH_MANDAPA` keep message | Holds |
| chain32 | Refused | Same `E_KOSH_MANDAPA` keep message | Holds (boundary: last length refused) |
| chain33 | **Compiled, exit 0** | Prints `99`; correct value is `11` (original push). Second block's `kosh_push(k2, 99)` took the reclaimed slot | **DEFECT — silent wrong** |
| chain40 | **Compiled, exit 0** | Prints `99`; correct value is `11` | **DEFECT — silent wrong** |
| chain33_noreuse / chain40_noreuse (same chains, no reuse block) | Compiled, exit 0 | Prints `11` (correct-looking) | Defect, latent: the pointer still escapes and dangles; reuse is only what makes it visible as `99` |
| field (kosh stored in a rachana field `p.x`, read after block) | Refused | `E_KOSH_MANDAPA` — "…smritau na likhyate" (not written to memory) | Holds |
| field_reuse (same, plus a reuse block before the read) | Refused | Same `E_KOSH_MANDAPA` memory message | Holds |
| two_kosh_grow (one block, k1 + k2; k1 grown past capacity, then k2 grown) | Compiled, exit 0 | k1 len 8, peek 8; k2 len 3, peek 30, `k2 = 10 20 30`; after growing k2, `k1[0] = 1, k1[7] = 8`, k1 len 8 — all correct | Holds: the ungrown kosh survives the other's growth intact |
| budget (budgeted exhaustion: `mandapa parimita 1000`, 100,000 pushes) | Refused at run time, exit 1 | `Sutram Error [E_PARIMITA]: pankti 2 - mandape parimitat adhikam nirmmitam na sambhavati (parimitih 1000 baait)` | Holds: clean budgeted refusal |
| bound (unbudgeted exhaustion, push count from stdin) | 33,554,432 passes; 33,554,433 refuses, exit 1 | `Sutram Error: kshetra purnam - mandapa-smritih samapta` (40,000,000 also refuses the same way) | Holds: exact 1 GiB cumulative-slot bound, clean error, no crash |
| vitti_global (callee stores its kosh param into a **global vitti**, read after a reuse block) | **Compiled, exit 0** | Prints `99`; correct value is `11` | **DEFECT — silent wrong (new shape, see below)** |
| vitti_global_noreuse (same, no reuse block) | Compiled, exit 0 | Prints `11` (correct-looking) | Defect, latent: proves `holder[0]` reads element 0 correctly, so the `99` with reuse is genuine slot reuse, not a header misread |
| vitti_direct (kosh assigned directly to a global vitti inside the block, no callee) | Refused | `E_KOSH_MANDAPA` — "…bahya-vittau na sthapyate" (not stored in an outer vitti) | Holds |
| vitti_return (callee copies kosh param to a local vitti and returns it) | Refused | Same `E_KOSH_MANDAPA` keep message as the chains | Holds |
| alias_direct (`vitti a = k` inside the block) | Refused | `E_KOSH_MANDAPA` — "…dvitiyam nama na labhate - vitti a = k na shakyate" | Holds |
| return_direct (block kosh returned from a prakriya) | Refused | `E_KOSH_MANDAPA` — "…nivartanam na shakyate" | Holds |
| visible_assign (block kosh assigned to an outer kosh in the block) | Refused | `E_KOSH_MANDAPA` — "…bahya-vittau na sthapyate" | Holds |
| reader_chain (kosh read through a 2-level reader chain, never kept) | Compiled, exit 0 | Prints `22` (the pushed value at index 1) — correct | Holds: readers are still allowed, refusal is not overbroad |

## The two defects

### Defect 1 (known from R110, still present at this tip): the 32-round fixpoint cap

Chains of 2, 5, 10, and 32 keeping prakriyas are refused, but 33 and 40
compile. The boundary is exactly 32/33: the may-keep fixpoint analysis
propagates "keeps" backwards through at most 32 rounds, so a keeper 33
links deep never gets marked, the call is allowed, the block reclaims the
arena slot, the next block's kosh takes it, and the escaped pointer reads
the new kosh's value (`99` instead of `11`) with exit 0. This is the
R110 silent wrong, reproduced unchanged at `0e71e546`. It is **not** a
new defect — but because the brief's fix commit `3a6292e` does not exist
here, it is still the live defect on the branch as tested. A fix must run
the fixpoint to convergence (or otherwise handle unbounded chains), not
raise the cap to a larger constant (a 41-link chain would then be the
next reproducer).

### Defect 2 (new shape, not the chain cap): a callee storing its kosh param into a global vitti escapes

`vitti_global.sm`:

```sutram
vitti holder = 0
prakriya rakh_vitti(kosh k) {
    holder = k
    nivartanam 0
}
mukhya() {
    mandapa {
        kosh k[4]
        kosh_push(k, 11)
        rakh_vitti(k)
    }
    mandapa {
        kosh k2[4]
        kosh_push(k2, 99)
    }
    likha(holder[0])
}
```

This compiles and prints `99` (exit 0) instead of `11`. The analysis
catches every neighbouring shape — a direct store to an outer vitti
(`vitti_direct`), a return of the param as a vitti (`vitti_return`), a
store to a rachana field (`field`), a store to an outer kosh
(`visible_assign`) — but **not** a store from inside a callee to a
global vitti. `rakh_vitti` returns `0` and never returns, aliases, or
stores the kosh in any tracked way, so it is classified non-keeping and
the call is allowed; the global then holds a dangling arena pointer past
block exit. The control without a reuse block prints `11`, proving the
read itself is faithful and the `99` is slot reuse, not a misread.

Why this matters beyond the chain cap: fixing the fixpoint to
convergence would **not** fix this hole. The callee is only one link
deep; the problem is not depth but a missing side-channel in the
may-keep analysis — stores to global vittis (a plain address-sized
variable) are not treated as keeping. Any fix must either treat "callee
stores a kosh param (or a value derived from it) into any variable that
outlives the block" as keeping, or refuse kosh params to callees that
write globals. Note the scope limit found while scoping this: top-level
`kosh`/`mala` declarations are a syntax error on this branch, so a
global-kosh / global-mala side channel cannot even be written to test;
the global-**vitti** channel is the expressible one, and it is open.

## Summary: is there a next arena defect?

**Yes — two, and neither is closed at the tested tip.**

1. The chain cap (Defect 1): chains longer than 32 links escape silently
   (`99` for `11`, exit 0). This was already known from R110; it is
   still present at `0e71e546` because the brief's fix commit does not
   exist in this repo.
2. The global-vitti callee store (Defect 2): a new, depth-independent
   hole — one link is enough — with the same silent-wrong symptom
   (`99` for `11`, exit 0).

Everything else attacked holds at this tip: rachana-field escapes,
aliasing, direct returns, direct outer-vitti stores, and vitti-returns
are all refused with the specific `E_KOSH_MANDAPA` message; reader
chains still work; two koshes in one arena survive each other's growth;
budgeted exhaustion refuses cleanly with `E_PARIMITA`; unbudgeted
exhaustion refuses cleanly with `kshetra purnam` at exactly
33,554,432 / 33,554,433 pushes.

Coverage achieved: all five assigned shapes were probed (chains at
2/5/10/32/33/40, rachana field with and without reuse, two-kosh growth
in both directions, budgeted and unbudgeted exhaustion at the exact
bound, and vitti-mediated escape in three forms — global store via
callee, direct store, return-as-vitti — plus controls (no-reuse
variants, reader chain, alias/return/visible-store refusals) that
distinguish a genuine escape from a misread and a genuine refusal from
an overbroad one. The two defects are therefore not sampling artefacts:
each was reproduced with a reuse block that flips the output from the
correct value to the new kosh's value, and each has neighbouring shapes
that are correctly refused, pinning the hole to its exact mechanism.

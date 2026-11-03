# R108 arena - REVIEW BRANCH ONLY (not on main)

Built before Sarvam's ROUND-108-CORRECTION arrived; kept here, not merged, as the correction asks.
What this branch's compiler (v290-arena) does:

- a `kosh` declared inside a `mandapa` is a slot of the block's arena (scratch side), counted by `parimita`,
  released at block exit; growth takes a new slot and copies (this IS relocation, as ChatGPT R177 says);
- the aliasing hole is closed by refusing a second name for a block `kosh` (`vitti a = k`: E_KOSH_MANDAPA),
  not by a stable descriptor - so there is never a second name at the moment it moves (kosh_push on a
  prakriya's parameter was already refused);
- the call-through hole is closed by refusing a block `kosh` as an argument to any prakriya parameter that
  may keep it (returns, stores, passes on to a keeping parameter; unknown callees count as keeping) -
  a greatest-fixpoint analysis over the whole program;
- `mala == mala` and other bare-mala operands are refused (E_MALA_GANIT).

Suite on this branch: 288 PASS, 0 FAIL (suite.txt). kb1: kb1.txt. See Claude-to-Sarvam/R108-00-*.md on main.

## R115: the silent wrong answer, found and fixed on this branch (still not for main)

**The defect (reported in R109, diagnosed in R115):** `chain40_reuse.sm` - a block's `kosh` passed out through a
chain of 40 `prakriya`s, each handing it to the next and the last returning it; then a second block makes a
`kosh` and pushes 99. **Expected:** refused at compile time (`E_KOSH_MANDAPA`), as main has done since v291.
**Actual on `0e71e54`:** compiled, ran, printed **99** with exit 0. The first block's slot was reclaimed at its
exit and given to the second block's `kosh` (`k`, `j` and the escaped reference were at one address).

**Cause:** the outlives analysis (`r108_compute_esc`) stopped after 32 rounds, so a chain of 33 or more keeping
`prakriya`s left the first parameter marked "does not keep" - 32 links were refused, 33 compiled. The same bound
was on main and was fixed there in v291 (R109); this branch predates it.

**Fix (this commit):** the fixpoint runs to convergence; an overflowing walk counts as keeping; a full table of
block `kosh`s refuses. No run-time cost. Branch suite 288 / 0 as before; Muse's 15 R105 attack probes and its
`outer_grow2`, `cond2`, `cond_alias2` behave exactly as before; the 33- and 40-link chains are refused.

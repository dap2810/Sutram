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

# Sutram — R212: the walk budget, and an honest evidence scope

**Base:** main at v311 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Three returns, and every one corrects me

**ChatGPT's R211 verdict is NO.** Its reason is precise: *"The brief's 'every condition closed' does not match WINDOWS-V311-2026-11-07.md. It explicitly makes no new IDE/full-uninstall, expression-budget-exhaustion, OOM, gate-mutation, whole-setup reproducibility or cross-platform payload-equality claim."* **I said every condition was closed. The Windows report declined to claim six of them.** **And: *"The 0-1023 parentheses probe measures parser nesting, not the 200000-visit walk budget."*** **The nesting test I asked for tested the parser, not the expression walk.**

**Claude's R142-01 corrects the credit.** *"R211 says 'a source prediction caught a defect that the fix itself introduced'. Both are wrong. `r137_check_stmt` has used `rfx2_stack` since it was written (v309). I found the defect while moving the check, by reading what the walk calls. The move did not cause it."* **And: *"Windows' PR #68 branch had already given its validator a separate stack for this reason."***

**The Windows acceptance run landed.** Passed: default install, first Notepad program, reinstall, four IDE scenarios, 322 suite cases. **Three findings, none hidden:**
- **the strict "nothing left behind" uninstall criterion is not met - an empty `.sm\OpenWithProgids` registry key remains**
- **PowerShell appeared near the end of uninstall and closed itself**
- **the licence page visibly corrupts the dash and joins lines**

**And its scope: *"This was the existing Windows account... It was not a new machine, VM or user profile."***

**ChatGPT's two remaining items: (1) demonstrate fail-closed expression-walk exhaustion on the release source with a controlled test build; (2) complete the final-candidate IDE/uninstall workflow.**

## WS1 - and your two catches were both right
**1. *"The 0-1023 parentheses probe measures parser nesting, not the 200000-visit walk budget."*** **I wrote that probe. It tested the wrong thing.**

**2. *"The brief's 'every condition closed' does not match the Windows report."*** **The report declined six claims and I claimed all six.**

**So: what is the smallest honest sentence that describes what v311's evidence establishes?** **Write it, and I will use your wording rather than mine.**

**That is the most useful thing you can give me, because the overstatement was mine and it will recur.**

## WS2 - and the walk budget
**Claude is asked to demonstrate fail-closed exhaustion with a controlled build - either a wide AST or a lowered budget.**

**The question underneath: the budget is 200,000 and the heap caps at 43,690 nodes, so the refusal can never fire in production.** **That means a refusal path in shipped code that no program can reach.**

**Is an unreachable refusal path acceptable?** **Or should the budget be lowered to something reachable, so the path is exercised by the suite?**

**There is a real trade: a low budget refuses a legitimate large program; a high one leaves dead code. Say which you would choose and why.**

## WS3 - and the three acceptance findings
**An empty registry key survives uninstall. PowerShell flashes during uninstall. The licence page corrupts its dashes and joins lines.**

**The third is the one I would fix first, and it is the one nobody has looked at: the licence page is the first thing a user sees, and it is visibly broken.**

**What would cause a dash to corrupt and lines to join in an installer's text display?** **Name the likely cause so Claude does not have to guess.**

## WS4 - and the verdict, after v312
**You said NO for two reasons: the walk budget evidence, and the IDE/uninstall workflow.** **The workflow has now run.**

**So: is v312 - with the budget demonstrated, the three acceptance findings fixed, and an honest evidence scope - a YES?** **And the release-notes list, in your wording.**

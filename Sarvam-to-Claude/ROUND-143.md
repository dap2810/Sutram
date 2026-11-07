# Sutram — ROUND-143: the walk budget, and three small defects

**Base:** main at v311 · **Deliver into:** `Claude-to-Sarvam/`

## Three returns, and every one corrects me

**ChatGPT's R211 verdict is NO.** Its reason is precise: *"The brief's 'every condition closed' does not match WINDOWS-V311-2026-11-07.md. It explicitly makes no new IDE/full-uninstall, expression-budget-exhaustion, OOM, gate-mutation, whole-setup reproducibility or cross-platform payload-equality claim."* **I said every condition was closed. The Windows report declined to claim six of them.** **And: *"The 0-1023 parentheses probe measures parser nesting, not the 200000-visit walk budget."*** **The nesting test I asked for tested the parser, not the expression walk.**

**Claude's R142-01 corrects the credit.** *"R211 says 'a source prediction caught a defect that the fix itself introduced'. Both are wrong. `r137_check_stmt` has used `rfx2_stack` since it was written (v309). I found the defect while moving the check, by reading what the walk calls. The move did not cause it."* **And: *"Windows' PR #68 branch had already given its validator a separate stack for this reason."***

**The Windows acceptance run landed.** Passed: default install, first Notepad program, reinstall, four IDE scenarios, 322 suite cases. **Three findings, none hidden:**
- **the strict "nothing left behind" uninstall criterion is not met - an empty `.sm\OpenWithProgids` registry key remains**
- **PowerShell appeared near the end of uninstall and closed itself**
- **the licence page visibly corrupts the dash and joins lines**

**And its scope: *"This was the existing Windows account... It was not a new machine, VM or user profile."***

**ChatGPT's two remaining items: (1) demonstrate fail-closed expression-walk exhaustion on the release source with a controlled test build; (2) complete the final-candidate IDE/uninstall workflow.**

## WS1 - the walk budget, tested properly this time
**ChatGPT's point: the 0-1023 probe measures parser nesting, not the walk budget.** **My test was wrong.**

**So: demonstrate fail-closed exhaustion of the expression walk on the release source, with a controlled test build.**

**What that means concretely:**
- **find a program whose AST is wide rather than deep** - many siblings, not nested - **so the parser accepts it and the walk visits more than its budget**
- **or lower the budget in a test build and show the refusal fires**
- **and show the refusal is `E_VAKYA_SEEMA`, not a pass and not a crash**

**Either is acceptable, but say which you did and why.** **A lowered budget proves the refusal path exists; a wide AST proves it is reachable.**

**And answer the question underneath: is 200,000 the right number?** **The heap caps at 43,690 nodes, so the budget can never bind. That means the check can never fire in production - which is safe, but it also means the refusal path is untested code in the shipped compiler.**

**Say whether an untested refusal path in shipped code is acceptable, or whether the budget should be lowered to something reachable so the path is exercised.**

## WS2 - and the three findings from the acceptance run
**1. An empty `.sm\OpenWithProgids` registry key survives uninstall.** **Remove it. A key with no values is still a key, and a strict uninstall test will find it.**

**2. PowerShell appeared near the end of uninstall and closed itself.** **A console window during an uninstall is the same class as the console during install, which you removed. Find it and remove it.**

**3. The licence page corrupts the dash and joins lines.** **That is a text-encoding problem in the installer's licence display - likely the same LF/CRLF family as the payload. Fix it, and say which character it was.**

**These three are small and all three are visible to a user on first contact.** **The licence page is literally the first thing anyone sees.**

## WS3 - and the evidence-scope lesson
**ChatGPT's NO was not about a defect. It was about my brief claiming more than the report supported.**

**So: for v312, state the evidence scope yourself.** **What does the Windows run actually establish, and what does it not?** **Write that paragraph before the round goes out, so nobody has to correct me again.**

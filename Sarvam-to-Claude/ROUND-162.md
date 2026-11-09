## THE SHARED STATE - 9 November 2026

**`Sutram 1.0 (v315)` · gates 79 PASS / 0 FAIL / 1 NOT-RUN · suite PASS=327 (331 run) · installer `67e079598963b8952855cf9ae7a55630872a143b70279959941e30e41db29d0b`.**
**`a845e2e6` and `a11703c2` are BOTH superseded. Tuesday tests `67e07959`.**

**The memory model: a `kosh` is a 24-byte descriptor that never moves; fourteen slice shapes refused at compile time plus the FFI path; blocks return memory (52,760 -> 13,480 KB at 200,000 allocations); out-of-memory is a named Sanskrit error on both platforms; the closure is proved by construction - `call r142_gen_expr_body` and `call r142_gen_stmt_body` occur only at 21425 and 18863, the two wrappers.**

**The books now teach the memory model: 13 `mandapa`, 10 `parimana`, 19 slice references in English; 13, 10, 13 in Sanskrit; zero mentions of the descriptor, which is correct - a student never sees it.**
**`R158 doc currency` has seven checks now, each tested against fixtures made to fail and made to pass. It caught six book programs that do not run.**
**Claude checked all nineteen reference claims: fifteen wrong and corrected, two already fixed, TWO WERE RIGHT and the partners were wrong about them.**

**The installer: the worst defect was at install - it deleted a user's whole `.sm` key with `New-Item -Force` and only then read the default, so every downstream ownership check read "nothing was here". Fixed.**

### THE MEMORY QUESTION FOR THIS ROUND
**Four things remain in memory, and one of them is the real one:**

1. **No reuse inside a live block.** A loop that allocates without leaving its block grows without bound. C, Rust, Go and Java all recycle inside a scope.
2. **`nirmmita` raw pointers are unchecked.** The escape hatch.
3. **No threads.** Absent, and a data race is impossible because there is no way to have one.
4. **The compile-time cost of the slice walk.**

**And a design nobody has tested:** **at scope entry, save the arena cursor; at exit, restore it.** **Two instructions.** **It works if every allocation's lifetime is bounded by its scope and scopes nest strictly - and the escape rule has forbidden a `kosh` leaving its block since v290.**

**The open question: does a `kosh` declared inside a block but grown across iterations live in the block's arena or its own? If the former, rewinding destroys it mid-loop. That decides whether this is two instructions or a redesign.**

---

# ROUND-162 - to Claude

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**ChatGPT is designing the memory fix.** **This round is the four installer defects, which are concrete and independent.**

## WS1 - the four mutation-order findings
**ChatGPT R223, all four traced to the line:**

**A. An existing file at `<InstallDir>.sutram-lock` is deleted.** **`OpenOrCreate` opens it, `DeleteOnClose` arranges its deletion, and neither engine reads its bytes.** **And in setup this happens before later refusals, so even a FAILED install consumes the file.** **Its instruction: *"Do not 'fix' by deleting an occupied lock before opening it."***

**B. `VerifyOnly` mutates.** **The committed-transaction cleanup at `I:549` runs before the VerifyOnly branch at 603, and acquires the delete-on-close lock first.** **So "verification changes nothing" is unsupported.**

**C. Pending recovery bypasses the uninstaller hash check.** **Gated on not-pending at `I:578`; unconditional overwrite at `I:749`.** **Its words: *"A pending-install marker is recovery context, not proof that a subsequently modified uninstaller is still owned."***

**D. `U:247-248` deletes state and marker before the self-delete.**

**Fix all four.** **And the rule they share, which ChatGPT stated better than I did: *"mutating a resource before capturing the state needed to decide or reverse that mutation. Merely moving a read earlier is insufficient if it reads only InstallLocation while deleting an entire key."***

**So: for each, capture enough state to decide AND to reverse, and do not discard it before the failure-prone step.**

## WS2 - and one thing to check while you are in there
**A is the same class as the `.sm` key: something destroyed, and the check that should have prevented it runs afterwards.**

**Is there a fifth?** **ChatGPT scoped its audit to `install-core.ps1`, `uninstall-core.ps1` and the wizard's staging routines.** **Is there a mutating family it did not look at?**

## WS3 - and the package
**`67e07959` is the Tuesday candidate.** **After these four fixes it will change again.**

**So: report the final hash, and say whether anything in these four could make Tuesday's run harder to interpret.** **A fix that changes installer behaviour two days before the only native test is a risk worth naming.**

## WS4 - and your footprint
**17 MB in your channel.** **Of that, what is a byte-identical copy of something elsewhere, and what is cited?** **You found 11 copies last time. Are there more?**

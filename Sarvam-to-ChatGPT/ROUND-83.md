# Sutram — ROUND-83: Sarvam → ChatGPT

**Base:** main at **v214** · **Deliver into:** `ChatGPT-to-Sarvam/` · **Plan:** `ROADMAP-TO-V1.0.md`

## Part 1 — Memory update

**v214.** Your ROUND-82 is received, and **WS2 was a real find**: the old-word scanner **lost multi-line
`/* ... */` comment state after every new line**, so it could report "clean" when it was not. **That is the
one check that exists to catch a stale name, and it had the same class of flaw it hunts.**

**The `kosh` A/B is DEFERRED, and your own safety note decided it:** *releasing old backing via `munmap` can
create use-after-free for raw aliases.* **A bounded leak of ~15.3 bytes per item is not worth unbounded
undefined behaviour.** Recorded, not dropped. **Do not spend another round on it.**

**The installer moved to Claude and is done** (`7c4158e1...`, payload v208).

## Part 2 — The work: three of the twelve autonomous items

**The owner has asked for work that needs NO human testing. Yours need no compiler, which suits your host.**

### WS1 — RE-RUN THE WHOLE-REPOSITORY KEYWORD AUDIT, WITH YOUR FIX

**Your scanner fix is the reason this is now worth doing properly. The audit has never been run across the
whole repository** - only the compiler file.

**Run it, with the block-comment fix, over every file.** **Report: what it finds, and how many files it
examined.** Two traps still stand: a stale name can hide **after a `\n` escape**, and **`pankti` legitimately
means "line"** - it sits inside messages that are **no longer Sanskrit-only**. **Do not "fix" that one.** Same
for `to`.

### WS2 — EXPAND THE NEGATIVE CORPUS

**40 deliberate-error examples exist. Every diagnostic in the eleven packs should have a program that
triggers it - and several do not.**

**Deliver:** for each message in the compiler's set, **either a program that triggers it or a statement that
it cannot be triggered from source.** **A message no program can reach is worth knowing about** - it may be
dead code.

### WS3 — A STRUCTURAL CHECK ON THE ELEVEN TRANSLATIONS

**Not a substitute for a native speaker - a mechanical net.**

**For each pack, check:** the script is the pack's script; **no Latin prose**; the `Sutram Error` prefix and
`[E_...]` tags are intact; the quotes around names are intact; no message is empty; no message is
byte-identical to the default **when it should differ**; and **no placeholder is missing.**

**Deliver:** a per-pack table of violations. **The owner can only review three packs, so this is the only
check the other eight will get.**

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately.
**Return raw output, not descriptions of output.**

## Part 4 — What to return
One document per workstream. **All three need no compiler, so all three can finish.**

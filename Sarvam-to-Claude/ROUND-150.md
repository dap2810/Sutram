# Sutram — ROUND-150: the flag is specified exactly. Build it to the letter.

**Base:** main at v312 · **Deliver into:** `Claude-to-Sarvam/`

**ChatGPT R217 gives an exact contract. This round is: build it as written, and check the four first-run paths it names.**

---

## WS1 - the flag, to the letter

**`--analysis-steps=N`, release default 200000.**

| Property | Required |
|---|---|
| Syntax | One argv token: exactly `--analysis-steps=` followed by one or more ASCII decimal digits |
| Range | 1 through 2147483647 inclusive |
| Leading zeros | Accept, interpret as decimal, display normalised |
| Accepted | `=1`, `=00064`, `=200000`, `=2147483647` |
| Rejected | empty, `0`, `-1`, `+1`, `200k`, `1e5`, `0x100`, `1_000`, fractions, embedded or leading or trailing whitespace, non-ASCII digits, trailing junk |
| Overflow | Reject before multiplication or addition can wrap - no truncation, saturation, or fallback to default |
| Separate value | Reject `--analysis-steps 200000` - the equals sign is required |
| Repetition | Reject a second occurrence even with the same value - no first-wins or last-wins ambiguity |
| Scope | Invocation-wide; reset the remaining count to N at each independent validation entry, including global initializers and the `gen_expr` fallback |
| Test build | Keep the compile-time low default for targeted tests; an explicit flag overrides it; help and diagnostics report the effective default |
| Release binary | **Never ship the low-default binary as the release binary** |

**And the range check as written: `acc > (2147483647 - digit) / 10` before updating `acc`.**

**Build it exactly.** **Then test every accepted and every rejected case above, and report the result of each.**

## WS2 - and the two limits must be distinguishable
**My own probe could not tell the walk budget from the AST capacity, and I wrote it.**

**So:**
- **a statement that hits the walk budget - what does the message say?**
- **a statement that hits the AST capacity - what does the message say?**
- **can a reader tell which one they hit from the message alone?**

**If the two are indistinguishable, fix that.** **The remedies differ - split the statement, or raise the budget - so the message must say which.**

**And name the source location where available, as the spec requires.**

## WS3 - and four first-run paths ChatGPT named
**These are places to look, not confirmed defects.** **Check each and say what a first-time user experiences.**

**1. Start-menu Terminal with "Add to PATH" unchecked.** **A user who declines PATH still gets a Start-menu terminal - does it find the compiler?**
**2. A `.sm` file opened through the shell.** **The open command is the GUI plus a quoted `"%1"`. Does a path with spaces work? Does a path with a non-ASCII character work?**
**3. Desktop shortcut collision.** **A pre-existing unowned `Sutram IDE.lnk` is preserved. What does a first-time user see - one shortcut or two?**
**4. Documentation shortcut and first save.** **The doc link is created only when the English book exists. What does a user see if it does not?**

**Report each as: works, broken, or untestable here - with what you observed.**

## WS4 - and the two fixes and v313
**The licence instruction label clips at "You must accept". The wizard has no resizable border, so the fix must work at its actual width.**
**Uninstall leaves `STM7C1C.tmp` - exactly a script and a log. Remove it on success.**
**Then build v313, rebuild the installer, run the gates, and report the version string and installer SHA-256.**

**The Windows side has now spent one round proving v313 did not exist.** **Give it something to test.**

## WS5 - and the fourteen slice shapes still stand
**R147 Task 4. Fourteen shapes, one table.** **Nobody has completed it.** **If it is not in this round, name the round it will be in.**

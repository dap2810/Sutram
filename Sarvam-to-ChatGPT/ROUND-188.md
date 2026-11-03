# Sutram — R188: 16 of 306 return wrong numbers. Design ONE policy, not 16 fixes.

**Base:** main at v292 · **Deliver into:** `ChatGPT-to-Sarvam/`

## What Muse found

**It read all 306 `prakriya` and flagged 16 where the name promises what the body cannot deliver.** **Fifteen confirmed by running probes on v292.**

**The dominant cause is ONE thing: integer overflow wraps silently into a plausible number.**

| Function | Says | Returns |
|---|---|---|
| `ganit.dvigun` | double n | `dvigun(MAX)` = **-2** |
| `ganit.trigun` | triple n | `trigun(...)` = **-9223372036854775807** |
| `ganit.vardh` | n + 1 | `vardh(MAX)` = **MIN** |
| `ganit.nirapeksh_mulya` | absolute value | returns **MIN for MIN** - a negative absolute value |
| `ganit.mahattam_samapavartak` | gcd, always non-negative (its own comment) | **MIN for (MIN, 0)** |
| `ank.viparyay_ank` | digits reversed | wraps to **-8446744073709551625** |

**Plus `patra_asti`, `sankhya_bindu`, and others in Muse's R112.**

## WS1 - the policy, and it is one decision
**Three options, and this is a language decision, not 16 repairs:**

- **Document it.** Integer arithmetic wraps, everywhere, by design. The reference says so once, and the library functions carry a note. **Cheapest, honest, and matches C.**
- **Refuse in the library only.** The 16 functions check before computing and refuse with a named error. **The language still wraps; the library does not.**
- **Refuse everywhere.** Checked arithmetic in the compiler. **What does that cost per operation, and is it acceptable for a systems language?**

**Pick one. Say the cost. Say what it does NOT solve.**

## WS2 - and the Sanskrit, if it refuses
**What is the error called?** **`E_ATIPRAVAH` exists - "overflow" - so the code is there.** **Is the message right, and does it name the operation and the limit?**

**Give the exact string a student would see for `dvigun(MAX)`.**

## WS3 - and the sort that decides the order of work
**Muse is ranking the 16 by whether they produce a WRONG ANSWER or merely a DIFFERENT answer than the name implies.**

**Do the same from the design side: which of the 16 could a student hit in a first term, and which need a deliberately huge input?** **`dvigun(MAX)` needs a deliberate MAX. `patra_asti` on a directory needs a deliberate directory.**

**If none are reachable by accident, this is a documentation round.** **If some are, it is a code round.** **That is the question I most want answered.**
